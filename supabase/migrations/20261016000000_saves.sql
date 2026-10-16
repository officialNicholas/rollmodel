-- Roll Model: progress saved with your account (game v312).
--
-- Run it after 20261015010000_accounts.sql, the same way: Supabase > SQL Editor > New query, paste all of this, Run.
-- It's safe to run again.
--
-- What it adds:
-- - A copy of a player's progress (rank, drops, everything they've bought, crafted and unlocked, the lessons done) kept
--   with their account, so logging in on another phone brings it back. Only players with a real account have one, and
--   only they can read or write it, through rm_save_put() and rm_save_get().
-- - A guard for two phones on one account: a copy with less rank (xp) than the one kept is refused, so a phone that was
--   left behind can't wipe out progress made on the other.
-- - Deleting the account (rm_delete_me) deletes its saved progress with it.

-- ---------------------------------------------------------------- the saves

create table if not exists public.saves (
  id uuid primary key references auth.users (id) on delete cascade,
  data jsonb not null check (jsonb_typeof(data) = 'object'),
  xp bigint not null default 0 check (xp >= 0),
  updated_at timestamptz not null default now()
);
alter table public.saves enable row level security;
revoke all on public.saves from anon, authenticated;

-- ---------------------------------------------------------------- the app's functions

-- keep this copy of your progress. Answers { ok: true, at } (at: when it was kept, in ms since 1970), or { ok: false, why }:
-- no_account (only real accounts keep progress), bad (not an object), too_big (over 200 kB), slow_down (more than 240 an
-- hour), or behind (the copy kept has more rank: then also its xp and at, and nothing is changed).
create or replace function public.rm_save_put(p_data jsonb)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); x bigint; r public.saves;
begin
  if not exists (select 1 from public.accounts where id = u) then return jsonb_build_object('ok', false, 'why', 'no_account'); end if;
  if p_data is null or jsonb_typeof(p_data) <> 'object' then return jsonb_build_object('ok', false, 'why', 'bad'); end if;
  if octet_length(p_data::text) > 200000 then return jsonb_build_object('ok', false, 'why', 'too_big'); end if;
  x := case when jsonb_typeof(p_data -> 'xp') = 'number' then least(greatest(floor((p_data ->> 'xp')::numeric), 0), 1e15)::bigint else 0 end;
  select * into r from public.saves where id = u for update;
  if r.id is not null and r.xp > x then
    return jsonb_build_object('ok', false, 'why', 'behind', 'xp', r.xp, 'at', floor(extract(epoch from r.updated_at) * 1000));
  end if;
  if not public._rate(u, 'save', 240) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  insert into public.saves (id, data, xp, updated_at) values (u, p_data, x, now())
    on conflict (id) do update set data = excluded.data, xp = excluded.xp, updated_at = excluded.updated_at
    returning * into r;
  return jsonb_build_object('ok', true, 'at', floor(extract(epoch from r.updated_at) * 1000));
end $$;

-- your progress as kept: { ok: true, data, xp, at }, or { ok: true, data: null } when nothing's kept yet
create or replace function public.rm_save_get()
returns jsonb language sql stable security definer set search_path = '' as $$
  select coalesce(
    (select jsonb_build_object('ok', true, 'data', s.data, 'xp', s.xp, 'at', floor(extract(epoch from s.updated_at) * 1000))
       from public.saves s where s.id = public._me()),
    jsonb_build_object('ok', true, 'data', null))
$$;

-- ---------------------------------------------------------------- who may call what

revoke all on function public.rm_save_put(jsonb), public.rm_save_get() from public, anon;
grant execute on function public.rm_save_put(jsonb), public.rm_save_get() to authenticated;
