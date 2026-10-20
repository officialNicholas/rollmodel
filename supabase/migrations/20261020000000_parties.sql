-- Roll Model: parties (game v391; first written for v312) and notifications while the game is closed.
--
-- Run it after the others (friends, accounts, saves, liveops, email), the same way: Supabase > SQL Editor > New query,
-- paste all of this, Run. It's safe to run again.
--
-- What it changes:
-- - An invite can be to a party (mode 'party'), not only to a v306 duel room. A party's join code is 8 characters, so
--   an invite's code may now be 5 to 12 characters. Invites still need you to be friends, still respect blocks both
--   ways, still run out after 2 minutes, and still count towards the 40 an hour.
-- - rm_inbox2 is what the party game reads: everything rm_inbox has, with party invites. rm_inbox (the v306 to v390
--   games) now leaves party invites out, so an older game never shows an invite it can't open.
-- - rm_add_friend also answers with the id of the player the request went to, so the game can nudge that player's game
--   to show it at once.
-- - push_tokens: the iPhone app's address for notifications (its APNs device token), kept with the player's account.
--   Only the player can put theirs there or take it away (rm_push_token, rm_push_forget). The game server sends the
--   notification for a party invite: it asks rm_invite_push, as the player who sent the invite, for that one open
--   invite's notification (once per invite, and only between friends), and posts it to Apple. (So the sender's own game
--   could ask for it too, and see the friend's token: a token is no use to anyone without the app's APNs key.)

-- ---------------------------------------------------------------- invites to a party

do $$ declare c record; begin
  for c in select conname from pg_constraint where conrelid = 'public.invites'::regclass and contype = 'c'
      and (pg_get_constraintdef(oid) like '%room%' or pg_get_constraintdef(oid) like '%mode%') loop
    execute format('alter table public.invites drop constraint %I', c.conname);
  end loop;
end $$;
alter table public.invites add constraint invites_room_check check (room ~ '^[A-Z0-9]{5,12}$');
alter table public.invites add constraint invites_mode_check check (mode in ('duel', 'party'));

-- invite a friend: to a party (p_mode 'party', p_room its join code from the game server) or, from older games, to a
-- duel room. One open invite per friend; it lasts 2 minutes.
create or replace function public.rm_invite(p_to uuid, p_room text, p_mode text default 'duel')
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); rm text := upper(coalesce(p_room, '')); md text := coalesce(nullif(p_mode, ''), 'duel'); id uuid;
begin
  if rm !~ '^[A-Z0-9]{5,12}$' then return jsonb_build_object('ok', false, 'why', 'bad_room'); end if;
  if md not in ('duel', 'party') then return jsonb_build_object('ok', false, 'why', 'bad_mode'); end if;
  if not public._friends(u, p_to) or public._blocked(u, p_to) then return jsonb_build_object('ok', false, 'why', 'not_friends'); end if;
  if not public._rate(u, 'invite', 40) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  delete from public.invites where (from_id = u or to_id = u) and created_at < now() - interval '1 day';
  update public.invites set status = 'cancelled' where from_id = u and to_id = p_to and status = 'open';
  insert into public.invites (from_id, to_id, room, mode) values (u, p_to, rm, md) returning invites.id into id;
  return jsonb_build_object('ok', true, 'id', id);
end $$;

-- ---------------------------------------------------------------- the inbox

-- everything the Friends screen and the inbox show, in one call, with the invites of the kinds given; it also marks you
-- online ('lobby' or 'match'; 'offline' when you leave)
create or replace function public._inbox(p_status text, p_modes text[])
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
      from public.invites i join public.profiles p on p.id = i.from_id where i.to_id = u and i.status = 'open' and i.expires_at > now() and i.mode = any(p_modes)), '[]'::jsonb),
    'sent', coalesce((select jsonb_agg(jsonb_build_object('id', i.id, 'to', i.to_id, 'room', i.room, 'mode', i.mode, 'status', i.status, 'expires', i.expires_at) order by i.created_at desc)
      from public.invites i where i.from_id = u and i.created_at > now() - interval '10 minutes' and i.mode = any(p_modes)), '[]'::jsonb),
    'blocked', coalesce((select jsonb_agg(jsonb_build_object('id', p.id, 'name', p.name) order by b.created_at desc)
      from public.blocks b join public.profiles p on p.id = b.blocked where b.blocker = u), '[]'::jsonb),
    'now', now());
end $$;

-- the v306 to v311 games: duel invites only
create or replace function public.rm_inbox(p_status text default 'lobby')
returns jsonb language sql volatile security definer set search_path = '' as $$ select public._inbox(p_status, array['duel']) $$;
-- the v312 game: party invites
create or replace function public.rm_inbox2(p_status text default 'lobby')
returns jsonb language sql volatile security definer set search_path = '' as $$ select public._inbox(p_status, array['party']) $$;

-- ---------------------------------------------------------------- friend requests say who they went to

-- add a friend by their code. If they'd already asked you, you're friends straight away.
-- Answers: sent, friends_now, already_friends, already_sent (each with the player's name and id), not_found, self, limit, slow_down
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
  if public._friends(u, t.id) then return jsonb_build_object('ok', true, 'state', 'already_friends', 'name', t.name, 'id', t.id); end if;
  if public._blocked(u, t.id) then return jsonb_build_object('ok', true, 'state', 'sent', 'name', t.name, 'id', t.id); end if; -- (a block isn't announced)
  if exists (select 1 from public.friend_requests where from_id = t.id and to_id = u) then
    delete from public.friend_requests where (from_id = t.id and to_id = u) or (from_id = u and to_id = t.id);
    insert into public.friendships (a, b) values (least(u, t.id), greatest(u, t.id)) on conflict do nothing;
    return jsonb_build_object('ok', true, 'state', 'friends_now', 'name', t.name, 'id', t.id);
  end if;
  if exists (select 1 from public.friend_requests where from_id = u and to_id = t.id) then return jsonb_build_object('ok', true, 'state', 'already_sent', 'name', t.name, 'id', t.id); end if;
  if (select count(*) from public.friendships where a = u or b = u) >= 200
    or (select count(*) from public.friend_requests where from_id = u) >= 50 then return jsonb_build_object('ok', false, 'why', 'limit'); end if;
  if (select count(*) from public.friend_requests where to_id = t.id) >= 100 then return jsonb_build_object('ok', true, 'state', 'sent', 'name', t.name, 'id', t.id); end if;
  insert into public.friend_requests (from_id, to_id) values (u, t.id);
  return jsonb_build_object('ok', true, 'state', 'sent', 'name', t.name, 'id', t.id);
end $$;

-- ---------------------------------------------------------------- who may call what

revoke all on function public._inbox(text, text[]) from public, anon, authenticated;
revoke all on function public.rm_invite(uuid, text, text), public.rm_inbox(text), public.rm_inbox2(text), public.rm_add_friend(text) from public, anon;
grant execute on function public.rm_invite(uuid, text, text), public.rm_inbox(text), public.rm_inbox2(text), public.rm_add_friend(text) to authenticated;

-- ---------------------------------------------------------------- notifications while the game is closed

-- one row per iPhone that said yes to notifications, with the account signed in on it now. A token belongs to one
-- account at a time: signing in to another account on the same phone moves it there
create table if not exists public.push_tokens (
  token text primary key check (token ~ '^[0-9a-f]{64,200}$'),
  user_id uuid not null references public.profiles (id) on delete cascade,
  env text not null default 'production' check (env in ('development', 'production')),
  updated_at timestamptz not null default now()
);
create index if not exists push_tokens_user on public.push_tokens (user_id, updated_at desc);
alter table public.push_tokens enable row level security;
revoke all on table public.push_tokens from public, anon, authenticated;

-- an invite is sent as a notification at most once
alter table public.invites add column if not exists pushed_at timestamptz;

-- this phone's token, for the player signed in (env: 'development' for an app run from Xcode, 'production' otherwise).
-- A player keeps at most 5 (their newest phones); 30 calls an hour
create or replace function public.rm_push_token(p_token text, p_env text default 'production')
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); t text := lower(coalesce(p_token, '')); e text := case when p_env = 'development' then 'development' else 'production' end;
begin
  if not exists (select 1 from public.profiles where id = u) then raise exception 'no profile yet: call rm_me first' using errcode = 'P0002'; end if;
  if t !~ '^[0-9a-f]{64,200}$' then return jsonb_build_object('ok', false, 'why', 'bad_token'); end if;
  if not public._rate(u, 'push', 30) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  insert into public.push_tokens (token, user_id, env) values (t, u, e)
    on conflict (token) do update set user_id = excluded.user_id, env = excluded.env, updated_at = now();
  delete from public.push_tokens where user_id = u and token not in
    (select token from public.push_tokens where user_id = u order by updated_at desc limit 5);
  return jsonb_build_object('ok', true);
end $$;

-- this phone's token taken away from the player signed in (logging out, or notifications turned off)
create or replace function public.rm_push_forget(p_token text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me();
begin
  delete from public.push_tokens where token = lower(coalesce(p_token, '')) and user_id = u;
  return jsonb_build_object('ok', true);
end $$;

-- (the game server, with the token of the player who sent the invite) the notification for one open party invite: who
-- it's to, the sender's username, when it runs out, and the friend's phones. Once per invite; only while the two are
-- still friends with no block between them
create or replace function public.rm_invite_push(p_id uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); i public.invites; nm text;
begin
  select * into i from public.invites where id = p_id and from_id = u for update;
  if i.id is null or i.status <> 'open' or i.expires_at <= now() or i.mode <> 'party' then return jsonb_build_object('ok', false, 'why', 'not_open'); end if;
  if i.pushed_at is not null then return jsonb_build_object('ok', false, 'why', 'sent'); end if;
  if not public._friends(u, i.to_id) or public._blocked(u, i.to_id) then return jsonb_build_object('ok', false, 'why', 'not_friends'); end if;
  update public.invites set pushed_at = now() where id = i.id;
  select name into nm from public.profiles where id = u;
  return jsonb_build_object('ok', true, 'id', i.id, 'to', i.to_id, 'from', nm, 'expires', i.expires_at,
    'tokens', coalesce((select jsonb_agg(jsonb_build_object('t', x.token, 'env', x.env) order by x.updated_at desc)
      from (select token, env, updated_at from public.push_tokens where user_id = i.to_id order by updated_at desc limit 5) x), '[]'::jsonb));
end $$;

revoke all on function public.rm_push_token(text, text), public.rm_push_forget(text), public.rm_invite_push(uuid) from public, anon;
grant execute on function public.rm_push_token(text, text), public.rm_push_forget(text), public.rm_invite_push(uuid) to authenticated;
