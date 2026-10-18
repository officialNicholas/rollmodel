-- Roll Model: live ops (game v354 and the admin dashboard in admin/).
--
-- Run it after 20261016000000_saves.sql, the same way: Supabase > SQL Editor > New query, paste all of this, Run.
-- It's safe to run again.
--
-- What it adds:
-- - Anonymous play stats from the game (rm_track): installs, sessions, matches by mode, the tutorial steps reached, Paint Shop
--   views and buys, dabs earned and spent, rewarded ads, ranks. One row per install plus small daily counters, so the
--   database stays small however many people play.
-- - Live prices (rm_config): the dashboard sets a price for an item and the game picks it up within about a minute.
-- - The admin dashboard's functions (adm_*): analytics, the price editor, and customer support (find a player, reset their
--   password, sign them out everywhere, delete their account), every action written to an audit log.
--
-- How the admin side is locked down:
-- - There's no secret key anywhere. The dashboard signs in with Supabase Auth like any app, and every adm_* function checks
--   who's calling before it does anything.
-- - An admin is someone whose user id is in rm_admins (only the owner can add one, here in the SQL editor) AND who signed in
--   with their password and an authenticator-app code (the token's assurance level is aal2), with that code entered in the
--   last 12 hours. Anyone else gets "not an admin".
-- - The admin functions can't touch an admin's own account (no password reset, sign-out or delete of anyone in rm_admins).
-- - As with the rest of the database, the tables have row level security on with no policies and are closed to the app's
--   roles; everything goes through the functions.
--
-- Making yourself an admin (once): Authentication > Users > Add user > Create new user, with your real email and a long
-- password (tick "Auto Confirm User"). Then here in the SQL editor:
--   insert into public.rm_admins (id, note) select id, 'owner' from auth.users where email = 'you@example.com';
-- The dashboard asks you to set up the authenticator app the first time you sign in. See admin/README.md.

create schema if not exists extensions;
create extension if not exists pgcrypto with schema extensions;

-- ---------------------------------------------------------------- admins and the audit log

create table if not exists public.rm_admins (
  id uuid primary key references auth.users (id) on delete cascade,
  note text check (char_length(note) <= 80),
  added_at timestamptz not null default now()
);

-- what every admin did, kept even when the admin or the player is gone (no foreign keys)
create table if not exists public.rm_audit (
  id bigint generated always as identity primary key,
  at timestamptz not null default now(),
  admin_id uuid,
  admin_email text,
  action text not null,
  target text,
  detail jsonb not null default '{}'::jsonb
);
create index if not exists rm_audit_at on public.rm_audit (at desc);
create index if not exists rm_audit_target on public.rm_audit (target, at desc);
create index if not exists rm_audit_action on public.rm_audit (action, at desc);

-- ---------------------------------------------------------------- live prices

-- only the overrides: every other item costs what the game says (admin/catalog.json)
create table if not exists public.rm_prices (
  item text primary key check (item ~ '^[a-z0-9_]{1,32}$'),
  price int not null check (price between 0 and 100000),
  updated_at timestamptz not null default now(),
  updated_by text
);

-- ---------------------------------------------------------------- play stats

-- one row per install: where it's at now, and what it's done in all
create table if not exists public.rm_installs (
  iid uuid primary key,
  user_id uuid references auth.users (id) on delete set null,   -- the player, when signed in (unlinked when they delete their account)
  platform text,
  app_ver text,
  game_ver int,
  first_at timestamptz not null default now(),
  last_at timestamptz not null default now(),
  days bigint not null default 0,                               -- bit k: seen on the k-th day after the first (k up to 62), for retention
  rank int,
  xp bigint,
  dabs bigint,
  tut text,                                                     -- the tutorial phase the game reports now
  tut_steps text[] not null default '{}',                       -- every tutorial step reached
  modes text[] not null default '{}',                           -- every mode played
  sessions int not null default 0,
  matches int not null default 0,
  play_secs bigint not null default 0,
  view_day date,                                                -- the items looked at today (a view counts once a day)
  viewed text[] not null default '{}',
  win_at timestamptz,                                           -- the rate limit's hour, and the calls in it
  win_n int not null default 0
);
create index if not exists rm_installs_last on public.rm_installs (last_at);
create index if not exists rm_installs_first on public.rm_installs (first_at);
create index if not exists rm_installs_user on public.rm_installs (user_id);

-- counters per UTC day. k is a key like 'dau', 'matches', 'm:duel:1:plays' (mode, online, what), 'v:tophat' (views of an item);
-- see rm_track for them all
create table if not exists public.rm_daily (
  day date not null,
  k text not null,
  n bigint not null default 0,
  primary key (day, k)
);

-- every Paint Shop buy (an item is bought once per install, so this stays small)
create table if not exists public.rm_buys (
  id bigint generated always as identity primary key,
  at timestamptz not null default now(),
  iid uuid not null,
  item text not null,
  price int not null
);
create index if not exists rm_buys_item on public.rm_buys (item, at);
create index if not exists rm_buys_at on public.rm_buys (at);

alter table public.rm_admins enable row level security;
alter table public.rm_audit enable row level security;
alter table public.rm_prices enable row level security;
alter table public.rm_installs enable row level security;
alter table public.rm_daily enable row level security;
alter table public.rm_buys enable row level security;
revoke all on public.rm_admins, public.rm_audit, public.rm_prices, public.rm_installs, public.rm_daily, public.rm_buys from anon, authenticated;

-- ---------------------------------------------------------------- helpers (not callable from the app)

-- when the authenticator code was entered, from the token's amr claim (null when it wasn't)
create or replace function public._code_at(p_jwt jsonb) returns timestamptz language sql immutable set search_path = '' as $$
  select to_timestamp(max((e ->> 'timestamp')::double precision))
    from jsonb_array_elements(case when jsonb_typeof(p_jwt -> 'amr') = 'array' then p_jwt -> 'amr' else '[]'::jsonb end) e
   where jsonb_typeof(e) = 'object' and e ->> 'method' = 'totp' and jsonb_typeof(e -> 'timestamp') = 'number'
$$;

-- the calling admin's id, or "not an admin": listed in rm_admins, signed in with an authenticator code (aal2), entered in the last 12 hours
create or replace function public._adm() returns uuid language plpgsql stable set search_path = '' as $$
declare u uuid := auth.uid(); j jsonb := coalesce(auth.jwt(), '{}'::jsonb); c timestamptz;
begin
  c := public._code_at(j);
  if u is null or coalesce(j ->> 'aal', '') <> 'aal2' or c is null or c < now() - interval '12 hours' or c > now() + interval '5 minutes'
     or not exists (select 1 from public.rm_admins where id = u) then
    raise exception 'not an admin' using errcode = '42501';
  end if;
  return u;
end $$;

create or replace function public._audit(p_admin uuid, p_action text, p_target text, p_detail jsonb) returns void language sql volatile set search_path = '' as $$
  insert into public.rm_audit (admin_id, admin_email, action, target, detail)
  values (p_admin, (select email from auth.users where id = p_admin), p_action, p_target, coalesce(p_detail, '{}'::jsonb))
$$;

-- when the live prices last changed, in ms since 1970 (0 when they never have)
create or replace function public._prices_v() returns bigint language sql stable set search_path = '' as $$
  select coalesce(floor(extract(epoch from max(at)) * 1000)::bigint, 0) from public.rm_audit where action = 'set_price'
$$;

-- an id the stats keep (items, modes, canvases...): lowercase letters, digits, _ . - (no ':', the counters' separator)
create or replace function public._sid(p text) returns text language sql immutable set search_path = '' as $$
  select case when p ~ '^[a-z0-9_.-]{1,32}$' then p end
$$;

-- a whole number from a json value, clamped; null when it isn't a number
create or replace function public._snum(p jsonb, p_lo numeric, p_hi numeric) returns bigint language sql immutable set search_path = '' as $$
  select case when jsonb_typeof(p) = 'number' then least(greatest(floor((p #>> '{}')::numeric), p_lo), p_hi)::bigint end
$$;

-- add n to counter k in a running tally
create or replace function public._tally(p_acc jsonb, p_k text, p_n bigint) returns jsonb language sql immutable set search_path = '' as $$
  select case when p_k is null or p_n is null or p_n = 0 then p_acc else p_acc || jsonb_build_object(p_k, coalesce((p_acc ->> p_k)::bigint, 0) + p_n) end
$$;

-- the tutorial in the order a new player meets it (the same as admin/catalog.json's "tutorial")
create or replace function public._tut_steps() returns text[] language sql immutable set search_path = '' as $$
  select array['intro', 'match', 'l:move', 'l:free0', 'l:sling', 'l:free1', 'l:basin', 'l:pound', 'l:dodge', 'l:item', 'l:rollover', 'l:orb',
    'l:free3', 'l:rocketdodge', 'l:flower', 'l:rest', 'shop', 'locker', 'vote', 'match2', 'done', 'rank2', 'strokes', 'strokes_done']
$$;

-- rank from xp, as the game works it out (repOf: rank n needs 100 + 45 (n - 1) more xp, up to 99)
create or replace function public._rank_of(p_xp bigint) returns int language plpgsql immutable set search_path = '' as $$
declare lv int := 1; x bigint := greatest(coalesce(p_xp, 0), 0);
begin
  while lv < 99 and x >= 100 + 45 * (lv - 1) loop x := x - (100 + 45 * (lv - 1)); lv := lv + 1; end loop;
  return lv;
end $$;

-- the days of a report: the last p_days UTC days, oldest first
create or replace function public._days(p_days int) returns setof date language sql stable set search_path = '' as $$
  select d::date from generate_series(((now() at time zone 'utc')::date - (least(greatest(coalesce(p_days, 30), 1), 180) - 1))::timestamp,
    (now() at time zone 'utc')::date::timestamp, interval '1 day') d
$$;

-- ---------------------------------------------------------------- what the game calls

-- the game's stats, in batches (about once a minute, and when the app is put away). Anyone may call it; a signed-in player's
-- install is linked to them by their token, never by anything in the body. Answers { ok: true, v } (v: the live prices'
-- version, so the game knows when to ask rm_config again), or { ok: false, why: rate | bad }.
create or replace function public.rm_track(p_iid uuid, p_meta jsonb default '{}'::jsonb, p_ev jsonb default '[]'::jsonb)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  u uuid := auth.uid();
  today date := (now() at time zone 'utc')::date;
  m jsonb := case when jsonb_typeof(p_meta) = 'object' then p_meta else '{}'::jsonb end;
  evs jsonb := coalesce(p_ev, '[]'::jsonb);
  r public.rm_installs;
  acc jsonb := '{}'::jsonb;   -- what this call adds to the day's counters
  fresh uuid; e jsonb; v_k text; v_s text; v_t text; v_i text; v_m text; v_on text; v_r text; v_n bigint; v_bit int;
  v_steps text[]; v_modes text[]; v_viewed text[]; v_vday date; v_sessions int := 0; v_matches int := 0; v_secs bigint;
begin
  if p_iid is null or jsonb_typeof(evs) <> 'array' then return jsonb_build_object('ok', false, 'why', 'bad'); end if;
  if jsonb_array_length(evs) > 60 then return jsonb_build_object('ok', false, 'why', 'bad'); end if;
  select * into r from public.rm_installs where iid = p_iid for update;
  if r.iid is null then
    -- a flood of new installs (someone faking them) is turned away: far more than the game could get
    if (select count(*) from public.rm_installs where first_at > now() - interval '1 minute') >= 600 then
      return jsonb_build_object('ok', false, 'why', 'rate');
    end if;
    insert into public.rm_installs (iid) values (p_iid) on conflict (iid) do nothing returning iid into fresh;
    select * into r from public.rm_installs where iid = p_iid for update;
    if fresh is not null then acc := public._tally(acc, 'new', 1); end if;
  end if;
  -- 120 calls an hour from one install
  if r.win_at is not null and r.win_at > now() - interval '1 hour' then
    if r.win_n >= 120 then return jsonb_build_object('ok', false, 'why', 'rate'); end if;
    r.win_n := r.win_n + 1;
  else
    r.win_at := now(); r.win_n := 1;
  end if;
  -- its first call today: a daily active install, and a mark on its days since the first (for retention)
  if r.days = 0 or (r.last_at at time zone 'utc')::date <> today then
    acc := public._tally(acc, 'dau', 1);
    v_bit := today - (r.first_at at time zone 'utc')::date;
    if v_bit between 0 and 62 then r.days := r.days | (1::bigint << v_bit); end if;
  end if;
  v_steps := r.tut_steps; v_modes := r.modes; v_viewed := r.viewed; v_vday := r.view_day;
  if v_vday is distinct from today then v_viewed := '{}'; v_vday := today; end if;

  for e in select x from jsonb_array_elements(evs) x loop
    continue when jsonb_typeof(e) <> 'object';
    v_k := e ->> 'k';
    if v_k = 'open' then
      v_sessions := v_sessions + 1; acc := public._tally(acc, 'sessions', 1);
    elsif v_k = 'tut' then
      v_s := e ->> 's';
      if v_s ~ '^[a-z0-9_:]{1,32}$' and not (v_s = any (v_steps)) and cardinality(v_steps) < 64 then v_steps := v_steps || v_s; end if;
    elsif v_k = 'match' then
      v_m := public._sid(e ->> 'm');
      continue when v_m is null;
      v_on := 'm:' || v_m || ':' || case when e -> 'on' = 'true'::jsonb then '1' else '0' end || ':';
      v_r := case when e ->> 'r' in ('win', 'loss', 'draw') then e ->> 'r' end;
      v_matches := v_matches + 1;
      acc := public._tally(acc, 'matches', 1);
      acc := public._tally(acc, v_on || 'plays', 1);
      acc := public._tally(acc, v_on || v_r, 1);
      acc := public._tally(acc, v_on || 'secs', public._snum(e -> 's', 0, 600));
      acc := public._tally(acc, v_on || 'cov', public._snum(e -> 'cov', 0, 100));
      acc := public._tally(acc, v_on || 'ko', public._snum(e -> 'ko', 0, 99));
      acc := public._tally(acc, 'st:' || public._sid(e ->> 'st'), 1);
      acc := public._tally(acc, 'd:' || public._sid(e ->> 'd'), 1);
      if not (v_m = any (v_modes)) and cardinality(v_modes) < 32 then v_modes := v_modes || v_m; end if;
    elsif v_k = 'earn' then
      v_n := public._snum(e -> 'n', 0, 100000);
      acc := public._tally(acc, 'dabs_earned', v_n);
      acc := public._tally(acc, 'earn:' || coalesce(public._sid(e ->> 'src'), 'other'), v_n);
    elsif v_k = 'view' then
      v_i := public._sid(e ->> 'i');
      if v_i is not null and not (v_i = any (v_viewed)) and cardinality(v_viewed) < 200 then
        v_viewed := v_viewed || v_i;
        acc := public._tally(acc, 'v:' || v_i, 1);
        if e -> 'a' = 'true'::jsonb then acc := public._tally(acc, 'va:' || v_i, 1); end if;
      end if;
    elsif v_k = 'buy' then
      v_i := public._sid(e ->> 'i'); v_n := coalesce(public._snum(e -> 'p', 0, 100000), 0);
      continue when v_i is null;
      acc := public._tally(acc, 'buys', 1);
      acc := public._tally(acc, 'dabs_spent', v_n);
      acc := public._tally(acc, 'b:' || v_i, 1);
      acc := public._tally(acc, 'bd:' || v_i, v_n);
      insert into public.rm_buys (iid, item, price) values (p_iid, v_i, v_n);
    elsif v_k = 'craft' then
      acc := public._tally(acc, 'craft:' || public._sid(e ->> 'i'), 1);
    elsif v_k = 'skip' then
      acc := public._tally(acc, 'skip:' || public._sid(e ->> 'i'), 1);
    elsif v_k = 'ad' then
      v_t := case when e ->> 'r' in ('ask', 'shown', 'reward', 'fail') then e ->> 'r' end; v_i := public._sid(e ->> 'pl');
      continue when v_t is null or v_i is null;
      acc := public._tally(acc, 'ad:' || v_i || ':' || v_t, 1);
      if v_t = 'reward' then acc := public._tally(acc, 'ads', 1); end if;
    elsif v_k = 'rank' then
      v_n := public._snum(e -> 'n', 1, 999);
      if v_n is not null then acc := public._tally(acc, 'rank:' || v_n, 1); end if;
    elsif v_k = 'iap' then
      v_i := public._sid(e ->> 'pr'); v_n := coalesce(public._snum(e -> 'c', 0, 100000), 0);
      continue when v_i is null;
      acc := public._tally(acc, 'iap', 1);
      acc := public._tally(acc, 'iap_cents', v_n);
      acc := public._tally(acc, 'iap:' || v_i, 1);
      acc := public._tally(acc, 'iapc:' || v_i, v_n);
    end if;
  end loop;

  v_secs := coalesce(public._snum(m -> 'secs', 0, 3600), 0);
  acc := public._tally(acc, 'play_secs', v_secs);
  update public.rm_installs set
    user_id = coalesce(u, user_id),
    platform = coalesce(case when m ->> 'plat' ~ '^[a-z]{1,10}$' then m ->> 'plat' end, platform),
    app_ver = coalesce(case when m ->> 'av' ~ '^[0-9A-Za-z._-]{1,16}$' then m ->> 'av' end, app_ver),
    game_ver = coalesce(public._snum(m -> 'gv', 0, 1000000)::int, game_ver),
    rank = coalesce(public._snum(m -> 'rank', 1, 999)::int, rank),
    xp = coalesce(public._snum(m -> 'xp', 0, 1000000000000), xp),
    dabs = coalesce(public._snum(m -> 'dabs', 0, 1000000000), dabs),
    tut = coalesce(case when m ->> 'tut' ~ '^[a-z0-9_:]{1,32}$' then m ->> 'tut' end, tut),
    last_at = now(), days = r.days, tut_steps = v_steps, modes = v_modes, viewed = v_viewed, view_day = v_vday,
    sessions = sessions + v_sessions, matches = matches + v_matches, play_secs = play_secs + v_secs,
    win_at = r.win_at, win_n = r.win_n
  where iid = p_iid;
  -- the day's counters, in one statement with the keys in order, so two calls at once can't deadlock on them. A day already holding
  -- 3000 kinds of counter (the game makes a few hundred) only adds to those, so made-up ids can't grow the table without end
  if (select count(*) from public.rm_daily where day = today) < 3000 then
    insert into public.rm_daily (day, k, n)
      select today, x.key, x.value::bigint from jsonb_each_text(acc) x order by x.key
    on conflict (day, k) do update set n = public.rm_daily.n + excluded.n;
  else
    update public.rm_daily d set n = d.n + x.value::bigint from jsonb_each_text(acc) x where d.day = today and d.k = x.key;
  end if;
  return jsonb_build_object('ok', true, 'v', public._prices_v());
end $$;

-- the live prices: { v (when they last changed, ms since 1970; 0 when never), prices: { item: dabs } }. Anyone may ask
create or replace function public.rm_config()
returns jsonb language sql stable security definer set search_path = '' as $$
  select jsonb_build_object('v', public._prices_v(),
    'prices', coalesce((select jsonb_object_agg(item, price order by item) from public.rm_prices), '{}'::jsonb))
$$;

-- ---------------------------------------------------------------- the dashboard: who's asking

-- about yourself: are you an admin, and if not, what's missing. Any signed-in user may ask
create or replace function public.adm_whoami()
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare u uuid := public._me(); j jsonb := coalesce(auth.jwt(), '{}'::jsonb); listed boolean; aal text := j ->> 'aal'; c timestamptz := public._code_at(j);
begin
  listed := exists (select 1 from public.rm_admins where id = u);
  return jsonb_build_object('id', u, 'email', (select email from auth.users where id = u), 'aal', aal, 'listed', listed, 'code_at', c,
    'admin', listed and aal = 'aal2' and c is not null and c >= now() - interval '12 hours' and c <= now() + interval '5 minutes',
    'why', case when not listed then 'not_listed' when aal is distinct from 'aal2' or c is null then 'needs_code'
                when c < now() - interval '12 hours' or c > now() + interval '5 minutes' then 'stale' end);
end $$;

-- ---------------------------------------------------------------- the dashboard: analytics

create or replace function public.adm_overview(p_days int default 30)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare today date := (now() at time zone 'utc')::date; o jsonb; ret jsonb := '{}'::jsonb; nd int; coh int; back int; sess bigint; secs bigint;
begin
  perform public._adm();
  -- day-N retention: of the installs that started in the 7 days ending N + 1 days ago, the share seen again exactly N days after their first
  foreach nd in array array[1, 7, 30] loop
    select count(*), count(*) filter (where (days >> nd) & 1 = 1) into coh, back from public.rm_installs
     where (first_at at time zone 'utc')::date between today - nd - 7 and today - nd - 1;
    ret := ret || jsonb_build_object('d' || nd, case when coh > 0 then round(back::numeric / coh, 4) end, 'cohort_d' || nd, coh);
  end loop;
  select coalesce(sum(n) filter (where k = 'sessions'), 0), coalesce(sum(n) filter (where k = 'play_secs'), 0) into sess, secs
    from public.rm_daily where day > today - 7 and k in ('sessions', 'play_secs');
  select jsonb_build_object(
    'now', now(),
    'online', count(*) filter (where last_at > now() - interval '5 minutes'),
    'dau', count(*) filter (where last_at > now() - interval '1 day'),
    'wau', count(*) filter (where last_at > now() - interval '7 days'),
    'mau', count(*) filter (where last_at > now() - interval '30 days'),
    'installs', count(*),
    'new_today', count(*) filter (where first_at >= today::timestamp at time zone 'utc'),
    'new_7d', count(*) filter (where first_at > now() - interval '7 days'))
    into o from public.rm_installs;
  return o || jsonb_build_object(
    'accounts', (select count(*) from public.accounts),
    'sessions_today', (select coalesce(sum(n), 0) from public.rm_daily where day = today and k = 'sessions'),
    'avg_session_secs', case when sess > 0 then round(secs::numeric / sess) else 0 end,
    'retention', ret,
    'days', (select coalesce(jsonb_agg(jsonb_build_object('day', d.day,
        'dau', coalesce(c.dau, 0), 'new', coalesce(c.new, 0), 'sessions', coalesce(c.sessions, 0), 'matches', coalesce(c.matches, 0),
        'ads', coalesce(c.ads, 0), 'buys', coalesce(c.buys, 0), 'dabs_spent', coalesce(c.dabs_spent, 0), 'dabs_earned', coalesce(c.dabs_earned, 0),
        'play_secs', coalesce(c.play_secs, 0)) order by d.day), '[]'::jsonb)
      from public._days(p_days) d(day)
      left join (select day, sum(n) filter (where k = 'dau') dau, sum(n) filter (where k = 'new') new, sum(n) filter (where k = 'sessions') sessions,
                        sum(n) filter (where k = 'matches') matches, sum(n) filter (where k = 'ads') ads, sum(n) filter (where k = 'buys') buys,
                        sum(n) filter (where k = 'dabs_spent') dabs_spent, sum(n) filter (where k = 'dabs_earned') dabs_earned,
                        sum(n) filter (where k = 'play_secs') play_secs
                   from public.rm_daily where day > today - 180 and k in ('dau', 'new', 'sessions', 'matches', 'ads', 'buys', 'dabs_spent', 'dabs_earned', 'play_secs')
                  group by day) c on c.day = d.day));
end $$;

create or replace function public.adm_modes(p_days int default 30)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare since date;
begin
  perform public._adm();
  select min(d) into since from public._days(p_days) d;
  return jsonb_build_object(
    'modes', (select coalesce(jsonb_agg(jsonb_build_object('mode', x.mode, 'plays', x.plays, 'wins', x.wins, 'losses', x.losses, 'draws', x.draws,
                'players', coalesce((select count(*) from public.rm_installs where x.mode = any (modes)), 0),
                'avg_secs', case when x.plays > 0 then round(x.secs::numeric / x.plays) else 0 end,
                'avg_cov', case when x.plays > 0 then round(x.cov::numeric / x.plays, 1) else 0 end,
                'online', x.online) order by x.plays desc, x.mode), '[]'::jsonb)
      from (select split_part(k, ':', 2) mode,
                   coalesce(sum(n) filter (where split_part(k, ':', 4) = 'plays'), 0) plays,
                   coalesce(sum(n) filter (where split_part(k, ':', 4) = 'win'), 0) wins,
                   coalesce(sum(n) filter (where split_part(k, ':', 4) = 'loss'), 0) losses,
                   coalesce(sum(n) filter (where split_part(k, ':', 4) = 'draw'), 0) draws,
                   coalesce(sum(n) filter (where split_part(k, ':', 4) = 'secs'), 0) secs,
                   coalesce(sum(n) filter (where split_part(k, ':', 4) = 'cov'), 0) cov,
                   coalesce(sum(n) filter (where split_part(k, ':', 4) = 'plays' and split_part(k, ':', 3) = '1'), 0) online
              from public.rm_daily where day >= since and k like 'm:%' group by 1) x),
    'days', (select coalesce(jsonb_agg((jsonb_build_object('day', d.day, 'solo', 0, 'duel', 0, 'trio', 0, 'ffa', 0, 'duo', 0, 'online', 0)
                || coalesce(c.by_mode, '{}'::jsonb) || jsonb_build_object('online', coalesce(c.online, 0))) order by d.day), '[]'::jsonb)
      from public._days(p_days) d(day)
      left join (select day, jsonb_object_agg(mode, plays) by_mode, sum(online) online
                   from (select day, split_part(k, ':', 2) mode, sum(n) plays, sum(n) filter (where split_part(k, ':', 3) = '1') online
                           from public.rm_daily where day >= since and k like 'm:%:plays' group by day, 2) z
                  group by day) c on c.day = d.day),
    'stages', (select coalesce(jsonb_agg(jsonb_build_object('stage', substr(k, 4), 'plays', n) order by n desc, k), '[]'::jsonb)
      from (select k, sum(n) n from public.rm_daily where day >= since and k like 'st:%' group by k) s),
    'diffs', (select coalesce(jsonb_agg(jsonb_build_object('diff', substr(k, 3), 'plays', n) order by n desc, k), '[]'::jsonb)
      from (select k, sum(n) n from public.rm_daily where day >= since and k like 'd:%' group by k) s));
end $$;

create or replace function public.adm_progress(p_steps text[] default null)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare st text[] := coalesce(p_steps, public._tut_steps());
begin
  perform public._adm();
  if cardinality(st) > 100 then st := st[1:100]; end if;
  return jsonb_build_object(
    'ranks', (select coalesce(jsonb_agg(jsonb_build_object('rank', rk, 'players', players, 'active', active) order by rk), '[]'::jsonb)
      from (select least(rank, 50) rk, count(*) players, count(*) filter (where last_at > now() - interval '30 days') active
              from public.rm_installs where rank is not null group by 1) x),
    'tutorial', (
      with fur as (   -- each install's furthest step in the order, and whether it's stuck there
        select i.tut_steps, (select max(array_position(st, x)) from unnest(i.tut_steps) x) far,
               i.last_at < now() - interval '3 days' and not ('done' = any (i.tut_steps)) gone
          from public.rm_installs i),
      reached as (select x step, count(*) n from fur, unnest(fur.tut_steps) x group by x),
      stuck as (select far, count(*) n from fur where gone and far is not null group by far),
      steps as (select x step, o from unnest(st) with ordinality u(x, o)
                union all   -- steps seen that aren't in the list, after it
                select step, 1000 + row_number() over (order by step) from reached where not (step = any (st)))
      select coalesce(jsonb_agg(jsonb_build_object('step', steps.step, 'reached', coalesce(reached.n, 0),
               'stuck', case when steps.o < 1000 then coalesce(stuck.n, 0) else 0 end) order by steps.o), '[]'::jsonb)
        from steps left join reached on reached.step = steps.step left join stuck on stuck.far = steps.o),
    'active_7d', (select count(*) from public.rm_installs where last_at > now() - interval '7 days'),
    'median_rank', (select percentile_disc(0.5) within group (order by rank) from public.rm_installs where rank is not null and last_at > now() - interval '30 days'),
    'done_pct', (select case when count(*) > 0 then round((count(*) filter (where 'done' = any (tut_steps)))::numeric / count(*), 4) else 0 end from public.rm_installs));
end $$;

create or replace function public.adm_economy(p_days int default 30)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare since date;
begin
  perform public._adm();
  select min(d) into since from public._days(p_days) d;
  return jsonb_build_object(
    'items', (
      with c as (select split_part(k, ':', 1) w, split_part(k, ':', 2) item, sum(n) n
                   from public.rm_daily where day >= since and (k like 'v:%' or k like 'va:%' or k like 'b:%' or k like 'bd:%') group by 1, 2),
      ids as (select item from c union select item from public.rm_prices)
      select coalesce(jsonb_agg(jsonb_build_object('item', ids.item,
               'views', coalesce((select n from c where c.item = ids.item and w = 'v'), 0),
               'afford_views', coalesce((select n from c where c.item = ids.item and w = 'va'), 0),
               'buys', coalesce((select n from c where c.item = ids.item and w = 'b'), 0),
               'dabs', coalesce((select n from c where c.item = ids.item and w = 'bd'), 0),
               'buyers_7d', (select count(distinct iid) from public.rm_buys b where b.item = ids.item and b.at > now() - interval '7 days'),
               'price', (select price from public.rm_prices p where p.item = ids.item),
               'last_buy', (select max(at) from public.rm_buys b where b.item = ids.item)) order by ids.item), '[]'::jsonb)
        from ids),
    'totals', (select jsonb_build_object(
               'dabs_earned', coalesce(sum(n) filter (where k = 'dabs_earned'), 0),
               'dabs_spent', coalesce(sum(n) filter (where k = 'dabs_spent'), 0),
               'buys', coalesce(sum(n) filter (where k = 'buys'), 0),
               'median_balance', (select coalesce(percentile_disc(0.5) within group (order by dabs), 0) from public.rm_installs
                                   where dabs is not null and last_at > now() - interval '7 days'))
      from public.rm_daily where day >= since and k in ('dabs_earned', 'dabs_spent', 'buys')),
    'days', (select coalesce(jsonb_agg(jsonb_build_object('day', d.day, 'buys', coalesce(c.buys, 0), 'dabs_spent', coalesce(c.spent, 0),
                'dabs_earned', coalesce(c.earned, 0)) order by d.day), '[]'::jsonb)
      from public._days(p_days) d(day)
      left join (select day, sum(n) filter (where k = 'buys') buys, sum(n) filter (where k = 'dabs_spent') spent, sum(n) filter (where k = 'dabs_earned') earned
                   from public.rm_daily where day >= since and k in ('buys', 'dabs_spent', 'dabs_earned') group by day) c on c.day = d.day),
    'strokes', (select coalesce(jsonb_agg(jsonb_build_object('stroke', id, 'crafts', crafts, 'skips', skips) order by crafts desc, id), '[]'::jsonb)
      from (select split_part(k, ':', 2) id, coalesce(sum(n) filter (where k like 'craft:%'), 0) crafts, coalesce(sum(n) filter (where k like 'skip:%'), 0) skips
              from public.rm_daily where day >= since and (k like 'craft:%' or k like 'skip:%') group by 1) x),
    'earn', (select coalesce(jsonb_agg(jsonb_build_object('src', substr(k, 6), 'dabs', n) order by n desc, k), '[]'::jsonb)
      from (select k, sum(n) n from public.rm_daily where day >= since and k like 'earn:%' group by k) x));
end $$;

create or replace function public.adm_ads(p_days int default 30)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare since date;
begin
  perform public._adm();
  select min(d) into since from public._days(p_days) d;
  return jsonb_build_object(
    'placements', (select coalesce(jsonb_agg(jsonb_build_object('placement', pl, 'asked', a, 'shown', s, 'rewarded', r, 'failed', f) order by a desc, pl), '[]'::jsonb)
      from (select split_part(k, ':', 2) pl, coalesce(sum(n) filter (where k like '%:ask'), 0) a, coalesce(sum(n) filter (where k like '%:shown'), 0) s,
                   coalesce(sum(n) filter (where k like '%:reward'), 0) r, coalesce(sum(n) filter (where k like '%:fail'), 0) f
              from public.rm_daily where day >= since and k like 'ad:%' group by 1) x),
    'days', (select coalesce(jsonb_agg(jsonb_build_object('day', d.day, 'asked', coalesce(c.a, 0), 'shown', coalesce(c.s, 0),
                'rewarded', coalesce(c.r, 0), 'failed', coalesce(c.f, 0)) order by d.day), '[]'::jsonb)
      from public._days(p_days) d(day)
      left join (select day, sum(n) filter (where k like '%:ask') a, sum(n) filter (where k like '%:shown') s, sum(n) filter (where k like '%:reward') r,
                        sum(n) filter (where k like '%:fail') f
                   from public.rm_daily where day >= since and k like 'ad:%' group by day) c on c.day = d.day));
end $$;

create or replace function public.adm_iap(p_days int default 30)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare since date;
begin
  perform public._adm();
  select min(d) into since from public._days(p_days) d;
  return jsonb_build_object(
    'products', (select coalesce(jsonb_agg(jsonb_build_object('product', pr, 'buys', b, 'revenue_cents', c) order by c desc, pr), '[]'::jsonb)
      from (select split_part(k, ':', 2) pr, coalesce(sum(n) filter (where k like 'iap:%'), 0) b, coalesce(sum(n) filter (where k like 'iapc:%'), 0) c
              from public.rm_daily where day >= since and (k like 'iap:%' or k like 'iapc:%') group by 1) x),
    'days', (select coalesce(jsonb_agg(jsonb_build_object('day', d.day, 'buys', coalesce(c.b, 0), 'revenue_cents', coalesce(c.c, 0)) order by d.day), '[]'::jsonb)
      from public._days(p_days) d(day)
      left join (select day, sum(n) filter (where k = 'iap') b, sum(n) filter (where k = 'iap_cents') c
                   from public.rm_daily where day >= since and k in ('iap', 'iap_cents') group by day) c on c.day = d.day));
end $$;

-- ---------------------------------------------------------------- the dashboard: prices

create or replace function public.adm_prices()
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  perform public._adm();
  return (select coalesce(jsonb_agg(jsonb_build_object('item', item, 'price', price, 'updated_at', updated_at, 'updated_by', updated_by) order by item), '[]'::jsonb)
            from public.rm_prices);
end $$;

-- a live price for one item, or back to the game's own (p_price null). Answers { ok: true } or { ok: false, why: item | range }
create or replace function public.adm_set_price(p_item text, p_price int)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare a uuid := public._adm(); was int;
begin
  if p_item is null or p_item !~ '^[a-z0-9_]{1,32}$' then return jsonb_build_object('ok', false, 'why', 'item'); end if;
  if p_price is not null and (p_price < 0 or p_price > 100000) then return jsonb_build_object('ok', false, 'why', 'range'); end if;
  select price into was from public.rm_prices where item = p_item for update;
  if p_price is null then
    delete from public.rm_prices where item = p_item;
  else
    insert into public.rm_prices (item, price, updated_at, updated_by) values (p_item, p_price, now(), (select email from auth.users where id = a))
      on conflict (item) do update set price = excluded.price, updated_at = excluded.updated_at, updated_by = excluded.updated_by;
  end if;
  perform public._audit(a, 'set_price', p_item, jsonb_build_object('from', was, 'to', p_price));
  return jsonb_build_object('ok', true);
end $$;

-- ---------------------------------------------------------------- the dashboard: support

-- players by username (starting with), friend code or user id; at most 25, exact matches first
create or replace function public.adm_find(p_q text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare v_q text := btrim(coalesce(p_q, '')); v_code text := upper(replace(btrim(coalesce(p_q, '')), ' ', '')); v_id uuid;
begin
  perform public._adm();
  if char_length(v_q) < 2 or char_length(v_q) > 40 then return '[]'::jsonb; end if;
  if v_q ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' then v_id := v_q::uuid; end if;
  return (select coalesce(jsonb_agg(jsonb_build_object('id', f.id, 'name', f.name, 'code', f.friend_code, 'rank', f.rank,
            'account', exists (select 1 from public.accounts a where a.id = f.id), 'created_at', f.created_at, 'last_seen', f.last_seen)
            order by f.exact desc, char_length(f.name), f.last_seen desc), '[]'::jsonb)
    from (select p.id, p.name, p.friend_code, p.rank, p.created_at, p.last_seen,
                 (p.id is not distinct from v_id or p.friend_code = v_code or lower(p.name) = lower(v_q)) exact
            from public.profiles p
           where p.id = v_id or p.friend_code = v_code or starts_with(lower(p.name), lower(v_q))
           order by exact desc, char_length(p.name), p.last_seen desc
           limit 25) f);
end $$;

create or replace function public.adm_player(p_id uuid)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare pr public.profiles; u record; ac public.accounts; sv public.saves;
begin
  perform public._adm();
  select * into pr from public.profiles where id = p_id;
  select id, email, is_anonymous, created_at, last_sign_in_at into u from auth.users where id = p_id;
  if pr.id is null and u.id is null then return null; end if;
  select * into ac from public.accounts where id = p_id;
  select * into sv from public.saves where id = p_id;
  return jsonb_build_object(
    'id', p_id, 'name', pr.name, 'code', pr.friend_code, 'rank', pr.rank, 'look', pr.look,
    'account', ac.id is not null, 'anonymous', coalesce(u.is_anonymous, true),
    'created_at', coalesce(u.created_at, pr.created_at), 'last_sign_in_at', u.last_sign_in_at, 'last_seen', pr.last_seen, 'status', pr.status,
    'admin', exists (select 1 from public.rm_admins where id = p_id),
    'friends', (select count(*) from public.friendships where a = p_id or b = p_id),
    'blocked_by_them', (select count(*) from public.blocks where blocked = p_id),
    'details', case when ac.id is not null then jsonb_build_object('first_name', ac.first_name, 'last_name', ac.last_name,
                 'birth_year', extract(year from ac.birthday)::int, 'terms', ac.terms, 'agreed_at', ac.agreed_at) end,
    'save', case when sv.id is not null then jsonb_build_object('rank', public._rank_of(sv.xp), 'xp', sv.xp,
              'drops', case when jsonb_typeof(sv.data -> 'drops') = 'number' then (sv.data ->> 'drops')::numeric end,
              'items', case when jsonb_typeof(sv.data -> 'owned') = 'array' then jsonb_array_length(sv.data -> 'owned') else 0 end,
              'at', sv.updated_at) end,
    'installs', (select coalesce(jsonb_agg(jsonb_build_object('iid', iid, 'platform', platform, 'app_ver', app_ver, 'game_ver', game_ver,
                   'first_at', first_at, 'last_at', last_at, 'sessions', sessions, 'matches', matches, 'tut', tut) order by last_at desc), '[]'::jsonb)
                 from public.rm_installs where user_id = p_id),
    'audit', (select coalesce(jsonb_agg(jsonb_build_object('at', at, 'admin', admin_email, 'action', action, 'detail', detail) order by at desc), '[]'::jsonb)
              from (select * from public.rm_audit where target = p_id::text order by at desc limit 50) x));
end $$;

-- end every session of a user (their devices can't refresh; a device already in keeps working until its token expires, within the hour)
create or replace function public._end_sessions(p_id uuid) returns int language plpgsql volatile set search_path = '' as $$
declare n int := 0;
begin
  if to_regclass('auth.refresh_tokens') is not null then
    execute 'delete from auth.refresh_tokens where user_id = $1' using p_id::text;
  end if;
  if to_regclass('auth.sessions') is not null then
    execute 'with d as (delete from auth.sessions where user_id = $1 returning 1) select count(*) from d' into n using p_id;
  end if;
  return n;
end $$;

-- a new password for a player (8 to 72 characters, a letter and a digit), then signed out everywhere.
-- Answers { ok: true } or { ok: false, why: weak | missing | anonymous | admin }. The password is never kept or logged
create or replace function public.adm_set_password(p_id uuid, p_password text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare a uuid := public._adm(); u record; nm text;
begin
  select id, email, is_anonymous into u from auth.users where id = p_id for update;
  if u.id is null then return jsonb_build_object('ok', false, 'why', 'missing'); end if;
  if exists (select 1 from public.rm_admins where id = p_id) then return jsonb_build_object('ok', false, 'why', 'admin'); end if;
  if u.is_anonymous or u.email is null then return jsonb_build_object('ok', false, 'why', 'anonymous'); end if;
  if p_password is null or char_length(p_password) < 8 or octet_length(p_password) > 72 or p_password !~ '[A-Za-z]' or p_password !~ '[0-9]' then
    return jsonb_build_object('ok', false, 'why', 'weak');
  end if;
  update auth.users set encrypted_password = extensions.crypt(p_password, extensions.gen_salt('bf', 10)), updated_at = now() where id = p_id;
  select name into nm from public.profiles where id = p_id;
  perform public._audit(a, 'set_password', p_id::text, jsonb_build_object('name', nm, 'sessions', public._end_sessions(p_id)));
  return jsonb_build_object('ok', true);
end $$;

-- sign a player out on every device: { ok: true, sessions } or { ok: false, why: missing | admin }
create or replace function public.adm_signout(p_id uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare a uuid := public._adm(); n int;
begin
  if not exists (select 1 from auth.users where id = p_id) then return jsonb_build_object('ok', false, 'why', 'missing'); end if;
  if exists (select 1 from public.rm_admins where id = p_id) then return jsonb_build_object('ok', false, 'why', 'admin'); end if;
  n := public._end_sessions(p_id);
  perform public._audit(a, 'signout', p_id::text, jsonb_build_object('name', (select name from public.profiles where id = p_id), 'sessions', n));
  return jsonb_build_object('ok', true, 'sessions', n);
end $$;

-- delete a player and everything of theirs, as the in-game Delete account does (rm_delete_me). p_confirm: their username (any
-- case), or their user id when they have none. Their install stats stay, no longer linked to them.
-- Answers { ok: true } or { ok: false, why: confirm | missing | admin }
create or replace function public.adm_delete_player(p_id uuid, p_confirm text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare a uuid := public._adm(); nm text;
begin
  if not exists (select 1 from auth.users where id = p_id) then return jsonb_build_object('ok', false, 'why', 'missing'); end if;
  if exists (select 1 from public.rm_admins where id = p_id) then return jsonb_build_object('ok', false, 'why', 'admin'); end if;
  select name into nm from public.profiles where id = p_id;
  if lower(btrim(coalesce(p_confirm, ''))) is distinct from lower(coalesce(nm, p_id::text)) then return jsonb_build_object('ok', false, 'why', 'confirm'); end if;
  delete from public.rate_events where user_id = p_id;
  delete from auth.users where id = p_id;
  perform public._audit(a, 'delete_player', p_id::text, jsonb_build_object('name', nm));
  return jsonb_build_object('ok', true);
end $$;

create or replace function public.adm_audit(p_limit int default 100)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  perform public._adm();
  return (select coalesce(jsonb_agg(jsonb_build_object('at', at, 'admin', admin_email, 'action', action, 'target', target, 'detail', detail) order by at desc, id desc), '[]'::jsonb)
            from (select * from public.rm_audit order by at desc, id desc limit least(greatest(coalesce(p_limit, 100), 1), 500)) x);
end $$;

-- ---------------------------------------------------------------- who may call what

revoke all on function public._code_at(jsonb), public._adm(), public._audit(uuid, text, text, jsonb), public._prices_v(), public._sid(text),
  public._snum(jsonb, numeric, numeric), public._tally(jsonb, text, bigint), public._tut_steps(), public._rank_of(bigint), public._days(int),
  public._end_sessions(uuid) from public, anon, authenticated;
revoke all on function public.rm_track(uuid, jsonb, jsonb), public.rm_config() from public;
grant execute on function public.rm_track(uuid, jsonb, jsonb), public.rm_config() to anon, authenticated;
revoke all on function public.adm_whoami(), public.adm_overview(int), public.adm_modes(int), public.adm_progress(text[]), public.adm_economy(int),
  public.adm_ads(int), public.adm_iap(int), public.adm_prices(), public.adm_set_price(text, int), public.adm_find(text), public.adm_player(uuid),
  public.adm_set_password(uuid, text), public.adm_signout(uuid), public.adm_delete_player(uuid, text), public.adm_audit(int) from public, anon;
grant execute on function public.adm_whoami(), public.adm_overview(int), public.adm_modes(int), public.adm_progress(text[]), public.adm_economy(int),
  public.adm_ads(int), public.adm_iap(int), public.adm_prices(), public.adm_set_price(text, int), public.adm_find(text), public.adm_player(uuid),
  public.adm_set_password(uuid, text), public.adm_signout(uuid), public.adm_delete_player(uuid, text), public.adm_audit(int) to authenticated;
