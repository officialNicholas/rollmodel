-- Roll Model: friends (game v305).
--
-- Run once in the Supabase SQL editor (or `supabase db push`). It's safe to run again: everything is "if not exists" or
-- "create or replace".
--
-- What it adds:
-- - a profile per player (name, look, rank, an 8-character friend code, and when they were last online);
-- - friend requests, friendships and blocks;
-- - invites to a private duel (the room code comes from the game server);
-- - this week's Time trial bests, for the Friends leaderboard.
--
-- How it's locked down:
-- - The app never reads or writes these tables directly. Row level security is on, with no policies, and the tables
--   are closed to the anon and authenticated roles.
-- - Everything goes through the functions at the bottom. They check who's calling (auth.uid()), and they only return
--   what that player may see: your own profile, your friends, and the people with a request or invite to or from you.
--   Profiles aren't searchable. The only way to reach a stranger is their friend code, and wrong codes are rate limited.
-- - Players sign in anonymously first (Authentication > Sign In / Providers > "Allow anonymous sign-ins"), so they need
--   no email. Linking Sign in with Apple later keeps the same user id, and so the same friends.

create schema if not exists extensions;
create extension if not exists pgcrypto with schema extensions;

-- ---------------------------------------------------------------- tables

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  name text not null default 'Rookie' check (char_length(name) between 1 and 16),
  friend_code text not null unique check (friend_code ~ '^[2-9A-HJKMNP-Z]{8}$'),
  look jsonb not null default '{}'::jsonb check (jsonb_typeof(look) = 'object' and pg_column_size(look) < 2048),
  rank int not null default 1 check (rank between 1 and 999),
  status text not null default 'offline' check (status in ('lobby', 'match', 'offline')),
  last_seen timestamptz not null default now(),
  created_at timestamptz not null default now()
);

-- a request lives only while it's pending: accepting, declining or cancelling deletes it
create table if not exists public.friend_requests (
  from_id uuid not null references public.profiles (id) on delete cascade,
  to_id uuid not null references public.profiles (id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (from_id, to_id),
  check (from_id <> to_id)
);
create index if not exists friend_requests_to on public.friend_requests (to_id);

-- one row per pair, the smaller id first
create table if not exists public.friendships (
  a uuid not null references public.profiles (id) on delete cascade,
  b uuid not null references public.profiles (id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (a, b),
  check (a < b)
);
create index if not exists friendships_b on public.friendships (b);

create table if not exists public.blocks (
  blocker uuid not null references public.profiles (id) on delete cascade,
  blocked uuid not null references public.profiles (id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (blocker, blocked),
  check (blocker <> blocked)
);
create index if not exists blocks_blocked on public.blocks (blocked);

create table if not exists public.invites (
  id uuid primary key default gen_random_uuid(),
  from_id uuid not null references public.profiles (id) on delete cascade,
  to_id uuid not null references public.profiles (id) on delete cascade,
  room text not null check (room ~ '^[A-Z0-9]{5}$'),
  mode text not null default 'duel' check (mode in ('duel')),
  status text not null default 'open' check (status in ('open', 'accepted', 'declined', 'cancelled')),
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default now() + interval '2 minutes',
  check (from_id <> to_id)
);
create index if not exists invites_to on public.invites (to_id, created_at desc);
create index if not exists invites_from on public.invites (from_id, created_at desc);

-- the week starts Monday 00:00 UTC, the same moment the game's own boards turn
create table if not exists public.trial_scores (
  user_id uuid not null references public.profiles (id) on delete cascade,
  week date not null,
  stage text not null check (stage ~ '^[a-z0-9_-]{1,24}$'),
  best smallint not null check (best between 0 and 100),
  runs int not null default 1 check (runs >= 1),
  updated_at timestamptz not null default now(),
  primary key (user_id, week, stage)
);
create index if not exists trial_scores_week on public.trial_scores (week, stage);

-- what a player has done lately, for the rate limits
create table if not exists public.rate_events (
  user_id uuid not null,
  kind text not null,
  at timestamptz not null default now()
);
create index if not exists rate_events_idx on public.rate_events (user_id, kind, at);

alter table public.profiles enable row level security;
alter table public.friend_requests enable row level security;
alter table public.friendships enable row level security;
alter table public.blocks enable row level security;
alter table public.invites enable row level security;
alter table public.trial_scores enable row level security;
alter table public.rate_events enable row level security;
revoke all on public.profiles, public.friend_requests, public.friendships, public.blocks, public.invites, public.trial_scores, public.rate_events
  from anon, authenticated;

-- ---------------------------------------------------------------- helpers (not callable from the app)

create or replace function public._me() returns uuid language plpgsql stable set search_path = '' as $$
declare u uuid := auth.uid();
begin
  if u is null then raise exception 'sign in first' using errcode = '28000'; end if;
  return u;
end $$;

create or replace function public._new_friend_code() returns text language plpgsql volatile set search_path = '' as $$
declare
  alphabet constant text := '23456789ABCDEFGHJKMNPQRSTUVWXYZ'; -- no 0/O, 1/I/L
  b bytea; c text;
begin
  loop
    b := extensions.gen_random_bytes(8); c := '';
    for i in 0..7 loop c := c || substr(alphabet, 1 + get_byte(b, i) % 31, 1); end loop;
    exit when not exists (select 1 from public.profiles where friend_code = c);
  end loop;
  return c;
end $$;

-- true, and counted, if the player is still under the limit for this kind of action in the last hour
create or replace function public._rate(p_user uuid, p_kind text, p_per_hour int) returns boolean language plpgsql volatile set search_path = '' as $$
declare n int;
begin
  delete from public.rate_events where user_id = p_user and at < now() - interval '1 day';
  select count(*) into n from public.rate_events where user_id = p_user and kind = p_kind and at > now() - interval '1 hour';
  if n >= p_per_hour then return false; end if;
  insert into public.rate_events (user_id, kind) values (p_user, p_kind);
  return true;
end $$;

create or replace function public._friends(p_x uuid, p_y uuid) returns boolean language sql stable set search_path = '' as $$
  select exists (select 1 from public.friendships where a = least(p_x, p_y) and b = greatest(p_x, p_y))
$$;

create or replace function public._blocked(p_x uuid, p_y uuid) returns boolean language sql stable set search_path = '' as $$
  select exists (select 1 from public.blocks where (blocker = p_x and blocked = p_y) or (blocker = p_y and blocked = p_x))
$$;

-- what a friend (or someone with a request or invite) sees of a player
create or replace function public._card(p public.profiles) returns jsonb language sql stable set search_path = '' as $$
  select jsonb_build_object('id', p.id, 'name', p.name, 'look', p.look, 'rank', p.rank,
    'online', p.status <> 'offline' and p.last_seen > now() - interval '90 seconds',
    'status', case when p.status <> 'offline' and p.last_seen > now() - interval '90 seconds' then p.status else 'offline' end,
    'last_seen', p.last_seen)
$$;

create or replace function public._clean_name(p text) returns text language sql immutable set search_path = '' as $$
  select nullif(btrim(left(btrim(regexp_replace(regexp_replace(coalesce(p, ''), '[[:cntrl:]]', '', 'g'), '\s+', ' ', 'g')), 16)), '')
$$;

-- ---------------------------------------------------------------- the app's functions

-- your profile, made the first time you call it. Name, look and rank are what the game shows your friends.
create or replace function public.rm_me(p_name text default null, p_look jsonb default null, p_rank int default null)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); nm text := public._clean_name(p_name); r public.profiles;
begin
  if p_look is not null and (jsonb_typeof(p_look) <> 'object' or pg_column_size(p_look) >= 2048) then p_look := null; end if;
  insert into public.profiles (id, name, friend_code, look, rank)
    values (u, coalesce(nm, 'Rookie'), public._new_friend_code(), coalesce(p_look, '{}'::jsonb), least(greatest(coalesce(p_rank, 1), 1), 999))
    on conflict (id) do update set
      name = coalesce(nm, public.profiles.name),
      look = coalesce(p_look, public.profiles.look),
      rank = coalesce(least(greatest(p_rank, 1), 999), public.profiles.rank)
    returning * into r;
  return jsonb_build_object('id', r.id, 'name', r.name, 'code', r.friend_code, 'rank', r.rank);
end $$;

-- everything the Friends screen shows, in one call; it also marks you online ('lobby' or 'match'; 'offline' when you leave)
create or replace function public.rm_inbox(p_status text default 'lobby')
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); me public.profiles;
begin
  update public.profiles set last_seen = now(), status = case when p_status in ('lobby', 'match', 'offline') then p_status else 'lobby' end
    where id = u returning * into me;
  if me.id is null then raise exception 'no profile yet: call rm_me first' using errcode = 'P0002'; end if;
  return jsonb_build_object(
    'me', jsonb_build_object('id', me.id, 'name', me.name, 'code', me.friend_code, 'rank', me.rank),
    'friends', coalesce((select jsonb_agg(public._card(p) order by (p.status <> 'offline' and p.last_seen > now() - interval '90 seconds') desc, p.last_seen desc)
      from public.friendships f join public.profiles p on p.id = case when f.a = u then f.b else f.a end where f.a = u or f.b = u), '[]'::jsonb),
    'incoming', coalesce((select jsonb_agg(public._card(p) || jsonb_build_object('at', q.created_at) order by q.created_at desc)
      from public.friend_requests q join public.profiles p on p.id = q.from_id where q.to_id = u), '[]'::jsonb),
    'outgoing', coalesce((select jsonb_agg(jsonb_build_object('id', p.id, 'name', p.name, 'look', p.look, 'at', q.created_at) order by q.created_at desc)
      from public.friend_requests q join public.profiles p on p.id = q.to_id where q.from_id = u), '[]'::jsonb),
    'invites', coalesce((select jsonb_agg(jsonb_build_object('id', i.id, 'from', public._card(p), 'room', i.room, 'mode', i.mode, 'at', i.created_at, 'expires', i.expires_at) order by i.created_at desc)
      from public.invites i join public.profiles p on p.id = i.from_id where i.to_id = u and i.status = 'open' and i.expires_at > now()), '[]'::jsonb),
    'sent', coalesce((select jsonb_agg(jsonb_build_object('id', i.id, 'to', i.to_id, 'room', i.room, 'status', i.status, 'expires', i.expires_at) order by i.created_at desc)
      from public.invites i where i.from_id = u and i.created_at > now() - interval '10 minutes'), '[]'::jsonb),
    'blocked', coalesce((select jsonb_agg(jsonb_build_object('id', p.id, 'name', p.name) order by b.created_at desc)
      from public.blocks b join public.profiles p on p.id = b.blocked where b.blocker = u), '[]'::jsonb),
    'now', now());
end $$;

-- add a friend by their code. If they'd already asked you, you're friends straight away.
-- Answers: sent, friends_now, already_friends, already_sent, not_found, self, limit, slow_down
create or replace function public.rm_add_friend(p_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); c text := upper(regexp_replace(coalesce(p_code, ''), '[^A-Za-z0-9]', '', 'g')); t public.profiles;
begin
  if not exists (select 1 from public.profiles where id = u) then raise exception 'no profile yet: call rm_me first' using errcode = 'P0002'; end if;
  if not public._rate(u, 'add', 30) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  c := translate(c, 'O01IL', 'OOOOO'); -- (letters the codes never use; they won't match)
  select * into t from public.profiles where friend_code = c;
  if t.id is null then return jsonb_build_object('ok', false, 'why', 'not_found'); end if;
  if t.id = u then return jsonb_build_object('ok', false, 'why', 'self'); end if;
  if public._friends(u, t.id) then return jsonb_build_object('ok', true, 'state', 'already_friends', 'name', t.name); end if;
  if public._blocked(u, t.id) then return jsonb_build_object('ok', true, 'state', 'sent', 'name', t.name); end if; -- (a block isn't announced)
  if exists (select 1 from public.friend_requests where from_id = t.id and to_id = u) then
    delete from public.friend_requests where (from_id = t.id and to_id = u) or (from_id = u and to_id = t.id);
    insert into public.friendships (a, b) values (least(u, t.id), greatest(u, t.id)) on conflict do nothing;
    return jsonb_build_object('ok', true, 'state', 'friends_now', 'name', t.name);
  end if;
  if exists (select 1 from public.friend_requests where from_id = u and to_id = t.id) then return jsonb_build_object('ok', true, 'state', 'already_sent', 'name', t.name); end if;
  if (select count(*) from public.friendships where a = u or b = u) >= 200
    or (select count(*) from public.friend_requests where from_id = u) >= 50 then return jsonb_build_object('ok', false, 'why', 'limit'); end if;
  if (select count(*) from public.friend_requests where to_id = t.id) >= 100 then return jsonb_build_object('ok', true, 'state', 'sent', 'name', t.name); end if;
  insert into public.friend_requests (from_id, to_id) values (u, t.id);
  return jsonb_build_object('ok', true, 'state', 'sent', 'name', t.name);
end $$;

create or replace function public.rm_answer_request(p_from uuid, p_accept boolean)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me();
begin
  if not exists (select 1 from public.friend_requests where from_id = p_from and to_id = u) then return jsonb_build_object('ok', false, 'why', 'gone'); end if;
  delete from public.friend_requests where (from_id = p_from and to_id = u) or (from_id = u and to_id = p_from);
  if p_accept then
    if (select count(*) from public.friendships where a = u or b = u) >= 200 then return jsonb_build_object('ok', false, 'why', 'limit'); end if;
    insert into public.friendships (a, b) values (least(u, p_from), greatest(u, p_from)) on conflict do nothing;
  end if;
  return jsonb_build_object('ok', true, 'state', case when p_accept then 'friends_now' else 'declined' end);
end $$;

create or replace function public.rm_cancel_request(p_to uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me();
begin
  delete from public.friend_requests where from_id = u and to_id = p_to;
  return jsonb_build_object('ok', true);
end $$;

create or replace function public.rm_remove_friend(p_other uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me();
begin
  delete from public.friendships where a = least(u, p_other) and b = greatest(u, p_other);
  update public.invites set status = 'cancelled' where status = 'open' and ((from_id = u and to_id = p_other) or (from_id = p_other and to_id = u));
  return jsonb_build_object('ok', true);
end $$;

-- block: no longer friends, requests and invites both ways gone, and they can't reach you again
create or replace function public.rm_block(p_other uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me();
begin
  if p_other = u or not exists (select 1 from public.profiles where id = p_other) then return jsonb_build_object('ok', false, 'why', 'not_found'); end if;
  insert into public.blocks (blocker, blocked) values (u, p_other) on conflict do nothing;
  delete from public.friendships where a = least(u, p_other) and b = greatest(u, p_other);
  delete from public.friend_requests where (from_id = u and to_id = p_other) or (from_id = p_other and to_id = u);
  update public.invites set status = 'cancelled' where status = 'open' and ((from_id = u and to_id = p_other) or (from_id = p_other and to_id = u));
  return jsonb_build_object('ok', true);
end $$;

create or replace function public.rm_unblock(p_other uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me();
begin
  delete from public.blocks where blocker = u and blocked = p_other;
  return jsonb_build_object('ok', true);
end $$;

-- invite a friend to the private room you made on the game server. One open invite per friend; it lasts 2 minutes.
create or replace function public.rm_invite(p_to uuid, p_room text, p_mode text default 'duel')
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); rm text := upper(coalesce(p_room, '')); id uuid;
begin
  if rm !~ '^[A-Z0-9]{5}$' then return jsonb_build_object('ok', false, 'why', 'bad_room'); end if;
  if not public._friends(u, p_to) or public._blocked(u, p_to) then return jsonb_build_object('ok', false, 'why', 'not_friends'); end if;
  if not public._rate(u, 'invite', 40) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  delete from public.invites where (from_id = u or to_id = u) and created_at < now() - interval '1 day';
  update public.invites set status = 'cancelled' where from_id = u and to_id = p_to and status = 'open';
  insert into public.invites (from_id, to_id, room, mode) values (u, p_to, rm, coalesce(nullif(p_mode, ''), 'duel')) returning invites.id into id;
  return jsonb_build_object('ok', true, 'id', id);
end $$;

create or replace function public.rm_answer_invite(p_id uuid, p_accept boolean)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); i public.invites;
begin
  select * into i from public.invites where id = p_id and to_id = u for update;
  if i.id is null or i.status <> 'open' or i.expires_at <= now() then return jsonb_build_object('ok', false, 'why', 'gone'); end if;
  update public.invites set status = case when p_accept then 'accepted' else 'declined' end where id = p_id;
  return jsonb_build_object('ok', true, 'room', case when p_accept then i.room end, 'mode', i.mode);
end $$;

create or replace function public.rm_cancel_invite(p_id uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me();
begin
  update public.invites set status = 'cancelled' where id = p_id and from_id = u and status = 'open';
  return jsonb_build_object('ok', true);
end $$;

-- a Time trial run: keeps your best of the week on that canvas (until the game server checks runs, this is on trust,
-- which is fine between friends)
create or replace function public.rm_trial(p_stage text, p_pct int)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); wk date := (date_trunc('week', now() at time zone 'utc'))::date; b smallint;
begin
  if p_stage !~ '^[a-z0-9_-]{1,24}$' or p_pct is null or p_pct < 0 or p_pct > 100 then return jsonb_build_object('ok', false, 'why', 'bad_run'); end if;
  if not exists (select 1 from public.profiles where id = u) then raise exception 'no profile yet: call rm_me first' using errcode = 'P0002'; end if;
  if not public._rate(u, 'trial', 120) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  insert into public.trial_scores (user_id, week, stage, best) values (u, wk, p_stage, p_pct)
    on conflict (user_id, week, stage) do update set
      runs = public.trial_scores.runs + 1,
      updated_at = case when excluded.best > public.trial_scores.best then now() else public.trial_scores.updated_at end,
      best = greatest(public.trial_scores.best, excluded.best)
    returning best into b;
  return jsonb_build_object('ok', true, 'best', b, 'week', wk);
end $$;

-- this week's board on a canvas: you and your friends, best first (a tie goes to whoever set it first)
create or replace function public.rm_friends_board(p_stage text, p_week date default null)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare u uuid := public._me(); wk date := coalesce(p_week, (date_trunc('week', now() at time zone 'utc'))::date);
begin
  return jsonb_build_object('week', wk, 'rows', coalesce((
    select jsonb_agg(jsonb_build_object('id', p.id, 'name', p.name, 'look', p.look, 'best', t.best, 'runs', t.runs, 'me', p.id = u) order by t.best desc, t.updated_at)
    from public.trial_scores t join public.profiles p on p.id = t.user_id
    where t.week = wk and t.stage = p_stage and (t.user_id = u or public._friends(u, t.user_id))), '[]'::jsonb));
end $$;

-- ---------------------------------------------------------------- who may call what

revoke all on function public._me(), public._new_friend_code(), public._rate(uuid, text, int), public._friends(uuid, uuid), public._blocked(uuid, uuid),
  public._card(public.profiles), public._clean_name(text) from public, anon, authenticated;
revoke all on function public.rm_me(text, jsonb, int), public.rm_inbox(text), public.rm_add_friend(text), public.rm_answer_request(uuid, boolean),
  public.rm_cancel_request(uuid), public.rm_remove_friend(uuid), public.rm_block(uuid), public.rm_unblock(uuid), public.rm_invite(uuid, text, text),
  public.rm_answer_invite(uuid, boolean), public.rm_cancel_invite(uuid), public.rm_trial(text, int), public.rm_friends_board(text, date) from public, anon;
grant execute on function public.rm_me(text, jsonb, int), public.rm_inbox(text), public.rm_add_friend(text), public.rm_answer_request(uuid, boolean),
  public.rm_cancel_request(uuid), public.rm_remove_friend(uuid), public.rm_block(uuid), public.rm_unblock(uuid), public.rm_invite(uuid, text, text),
  public.rm_answer_invite(uuid, boolean), public.rm_cancel_invite(uuid), public.rm_trial(text, int), public.rm_friends_board(text, date) to authenticated;
