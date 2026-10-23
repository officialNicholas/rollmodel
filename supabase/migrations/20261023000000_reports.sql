-- Roll Model: reporting a player (game v436).
--
-- Run it after the other migrations, the same way: Supabase > SQL Editor > New query, paste all of this, Run.
-- It's safe to run again.
--
-- What it adds:
-- - Report: from the Friends page (a friend, someone asking to be your friend, or someone you played online with), a player
--   can report another for an offensive username, cheating, bullying or something else, with an optional line of their own.
--   Reporting can also block them in the same step. The reported player is never told who reported them.
-- - For you, in the admin dashboard (admin/): the open reports, newest first, with how many different players have reported
--   the same person; close a report (with what you did), or reset an offensive username (they're asked for a new one the
--   next time they open the game). Apple expects reports to be looked at promptly: aim for within 24 hours.
-- - A reported player whose name three or more different players have reported is given a neutral name straight away
--   (player_xxxxxxxx) and asked for a new one, until you've looked at it.

-- ---------------------------------------------------------------- the reports

create table if not exists public.reports (
  id bigint generated always as identity primary key,
  reporter uuid references public.profiles (id) on delete set null,
  reported uuid not null references public.profiles (id) on delete cascade,
  reported_name text not null check (char_length(reported_name) between 1 and 16),
  reason text not null check (reason in ('name', 'cheating', 'bullying', 'other')),
  place text not null check (place in ('friends', 'request', 'recent', 'match', 'party')),
  note text check (char_length(note) <= 200),
  status text not null default 'open' check (status in ('open', 'closed')),
  outcome text check (outcome in ('no_action', 'warned', 'renamed', 'deleted')),
  created_at timestamptz not null default now(),
  closed_at timestamptz,
  closed_by uuid
);
create index if not exists reports_open on public.reports (status, created_at desc);
create index if not exists reports_reported on public.reports (reported, status);
alter table public.reports enable row level security;
revoke all on public.reports from anon, authenticated;

-- ---------------------------------------------------------------- the app's function

-- report a player (by their id, as the game has it from the friends list, a request or an online match's roster). Answers
-- { ok: true, blocked } or { ok: false, why: not_found | self | reason | slow_down }. The same player reported again by the same
-- person while their first report is still open updates that report rather than adding another.
create or replace function public.rm_report(p_other uuid, p_reason text, p_place text default 'friends', p_note text default null, p_block boolean default false)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); nm text; n int; why text := lower(btrim(coalesce(p_reason, ''))); pl text := lower(btrim(coalesce(p_place, 'friends')));
  v_note text := nullif(left(btrim(regexp_replace(coalesce(p_note, ''), '[[:cntrl:]]', ' ', 'g')), 200), '');
begin
  if p_other is null then return jsonb_build_object('ok', false, 'why', 'not_found'); end if;
  if p_other = u then return jsonb_build_object('ok', false, 'why', 'self'); end if;
  select name into nm from public.profiles where id = p_other;
  if nm is null then return jsonb_build_object('ok', false, 'why', 'not_found'); end if;
  if why not in ('name', 'cheating', 'bullying', 'other') then return jsonb_build_object('ok', false, 'why', 'reason'); end if;
  if pl not in ('friends', 'request', 'recent', 'match', 'party') then pl := 'friends'; end if;
  if not public._rate(u, 'report', 20) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  update public.reports set reason = why, place = pl, note = coalesce(v_note, public.reports.note), reported_name = nm, created_at = now()
    where reporter = u and reported = p_other and status = 'open';
  if not found then
    insert into public.reports (reporter, reported, reported_name, reason, place, note) values (u, p_other, nm, why, pl, v_note);
  end if;
  -- three or more different players reporting the same name: it's swapped for a neutral one until it's been looked at
  if why = 'name' then
    select count(distinct reporter) into n from public.reports where reported = p_other and reason = 'name' and status = 'open';
    if n >= 3 then
      update public.profiles set name = 'player_' || substr(replace(id::text, '-', ''), 1, 8), needs_name = true where id = p_other and not needs_name;
    end if;
  end if;
  if coalesce(p_block, false) then perform public.rm_block(p_other); end if;
  return jsonb_build_object('ok', true, 'blocked', coalesce(p_block, false));
end $$;

-- ---------------------------------------------------------------- the dashboard's functions (admins only, as in liveops)

-- the reports: open ones (or p_status 'closed', or 'all'), newest first, each with the names on both sides and how many
-- different players have an open report on the same person
create or replace function public.adm_reports(p_status text default 'open', p_limit int default 100)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare st text := lower(coalesce(p_status, 'open'));
begin
  perform public._adm();
  return (select coalesce(jsonb_agg(jsonb_build_object(
      'id', r.id, 'at', r.created_at, 'reason', r.reason, 'place', r.place, 'note', r.note, 'status', r.status, 'outcome', r.outcome, 'closed_at', r.closed_at,
      'reported', r.reported, 'reported_name', coalesce(pd.name, r.reported_name), 'name_when_reported', r.reported_name,
      'reporter', r.reporter, 'reporter_name', pr.name,
      'open_on_them', (select count(distinct x.reporter) from public.reports x where x.reported = r.reported and x.status = 'open')
    ) order by r.created_at desc, r.id desc), '[]'::jsonb)
    from (select * from public.reports where st = 'all' or status = st order by created_at desc, id desc limit least(greatest(coalesce(p_limit, 100), 1), 500)) r
    left join public.profiles pd on pd.id = r.reported left join public.profiles pr on pr.id = r.reporter);
end $$;

-- close a report, saying what was done: { ok: true } or { ok: false, why: missing | outcome }. p_all: every open report on the
-- same player closes with it.
create or replace function public.adm_report_close(p_id bigint, p_outcome text, p_all boolean default false)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare a uuid := public._adm(); r public.reports; o text := lower(coalesce(p_outcome, '')); n int;
begin
  if o not in ('no_action', 'warned', 'renamed', 'deleted') then return jsonb_build_object('ok', false, 'why', 'outcome'); end if;
  select * into r from public.reports where id = p_id;
  if r.id is null then return jsonb_build_object('ok', false, 'why', 'missing'); end if;
  update public.reports set status = 'closed', outcome = o, closed_at = now(), closed_by = a
    where status = 'open' and (id = p_id or (coalesce(p_all, false) and reported = r.reported));
  get diagnostics n = row_count;
  perform public._audit(a, 'report_close', r.reported::text, jsonb_build_object('report', p_id, 'outcome', o, 'closed', n));
  return jsonb_build_object('ok', true, 'closed', n);
end $$;

-- an offensive username taken away: the player gets a neutral name (player_xxxxxxxx) and is asked for a new one when they next
-- open the game. { ok: true, name } or { ok: false, why: missing | admin | slow_down }
create or replace function public.adm_reset_name(p_id uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare a uuid := public._adm(); old text; nm text;
begin
  select name into old from public.profiles where id = p_id for update;
  if old is null then return jsonb_build_object('ok', false, 'why', 'missing'); end if;
  if exists (select 1 from public.rm_admins where id = p_id) then return jsonb_build_object('ok', false, 'why', 'admin'); end if;
  if not public._rate(a, 'adm_rename', 120) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  nm := 'player_' || substr(replace(p_id::text, '-', ''), 1, 8);
  update public.profiles set name = nm, needs_name = true where id = p_id;
  perform public._audit(a, 'reset_name', p_id::text, jsonb_build_object('name', old));
  return jsonb_build_object('ok', true, 'name', nm);
end $$;

-- ---------------------------------------------------------------- who may call what

revoke all on function public.rm_report(uuid, text, text, text, boolean) from public, anon;
grant execute on function public.rm_report(uuid, text, text, text, boolean) to authenticated;
revoke all on function public.adm_reports(text, int), public.adm_report_close(bigint, text, boolean), public.adm_reset_name(uuid) from public, anon;
grant execute on function public.adm_reports(text, int), public.adm_report_close(bigint, text, boolean), public.adm_reset_name(uuid) to authenticated;
