-- Roll Model: the two demo accounts for App Review (game v436 and later).
--
-- Paste all of this into Supabase > SQL Editor > New query and press Run. It's safe to run again: it finds the two demo accounts it
-- made before and resets them (password, progress, friendship), and it never touches an account it didn't make.
--
-- It makes:
-- - @rollreview (password CHANGE-ME-1): the account for App Review to sign in with. Rank 13, so every mode, Stroke, skill and item is
--   unlocked; 25,000 dabs to spend in the Paint Shop; the lessons marked done so the reviewer lands straight in the lobby.
-- - @rollreviewpal (password CHANGE-ME-2): a second account, already on the first one's friends list, so the Friends page has someone on
--   it and the reviewer can invite them, start a party or remove and re-add them with their friend code. Same unlocks.
-- - A Time trial score for each on three canvases this week, so the leaderboard isn't empty.
-- Both sign in like any player: on the loading screen, "I already have an account", then the username and password.
--
-- Requires the earlier migrations (friends, accounts, saves) to have been run. Supabase already has the pgcrypto extension.

create or replace function pg_temp.rm_demo_user(p_name text, p_pass text, p_save jsonb, p_rank int)
returns uuid language plpgsql as $$
declare u uuid; mail text; c text; has_provider_id boolean;
begin
  -- the account this script made before under that name, if any; a real player's account with that name stops everything
  select p.id into u from public.profiles p where lower(p.name) = lower(p_name);
  if u is not null and not exists (select 1 from auth.users x where x.id = u and coalesce(x.raw_app_meta_data ->> 'rm_demo', '') = 'app_review') then
    raise exception 'The username @% belongs to a real player. Change the name at the bottom of this script and run it again.', p_name;
  end if;
  if u is null then
    u := gen_random_uuid(); mail := 'u' || replace(u::text, '-', '') || '@rollmodel.invalid';
    insert into auth.users (instance_id, id, aud, role, email, encrypted_password, email_confirmed_at, raw_app_meta_data, raw_user_meta_data, created_at, updated_at, is_anonymous)
      values ('00000000-0000-0000-0000-000000000000', u, 'authenticated', 'authenticated', mail, extensions.crypt(p_pass, extensions.gen_salt('bf', 10)), now(),
        '{"provider":"email","providers":["email"],"rm_demo":"app_review"}'::jsonb, '{}'::jsonb, now(), now(), false);
    -- Supabase's sign-in reads these as text: they must be empty, not missing (whichever of them this project's auth has)
    foreach c in array array['confirmation_token', 'recovery_token', 'email_change_token_new', 'email_change', 'email_change_token_current', 'phone_change', 'phone_change_token', 'reauthentication_token'] loop
      if exists (select 1 from information_schema.columns where table_schema = 'auth' and table_name = 'users' and column_name = c) then
        execute format('update auth.users set %I = coalesce(%I, '''') where id = $1', c, c) using u;
      end if;
    end loop;
    select exists (select 1 from information_schema.columns where table_schema = 'auth' and table_name = 'identities' and column_name = 'provider_id') into has_provider_id;
    if has_provider_id then
      execute 'insert into auth.identities (id, provider_id, user_id, identity_data, provider, last_sign_in_at, created_at, updated_at) values (gen_random_uuid(), $1::text, $1, $2, ''email'', now(), now(), now())'
        using u, jsonb_build_object('sub', u::text, 'email', mail, 'email_verified', true, 'phone_verified', false);
    else
      execute 'insert into auth.identities (id, user_id, identity_data, provider, last_sign_in_at, created_at, updated_at) values ($1::text, $1, $2, ''email'', now(), now(), now())'
        using u, jsonb_build_object('sub', u::text, 'email', mail, 'email_verified', true);
    end if;
    insert into public.profiles (id, name, friend_code, look, rank) values (u, p_name, public._new_friend_code(), jsonb_build_object('c', p_save ->> 'color', 'eyes', p_save #>> '{look,eyes}'), p_rank);
  else
    update auth.users set encrypted_password = extensions.crypt(p_pass, extensions.gen_salt('bf', 10)), banned_until = null, updated_at = now() where id = u;
    update public.profiles set name = p_name, needs_name = false, rank = p_rank where id = u;
  end if;
  insert into public.accounts (id, first_name, last_name, birthday, terms) values (u, 'App', 'Review', date '1990-01-01', 'tos-2026-10-18')
    on conflict (id) do update set first_name = 'App', last_name = 'Review', birthday = date '1990-01-01', terms = 'tos-2026-10-18', updated_at = now();
  insert into public.saves (id, data, xp, updated_at) values (u, p_save, coalesce((p_save ->> 'xp')::bigint, 0), now())
    on conflict (id) do update set data = excluded.data, xp = excluded.xp, updated_at = now();
  return u;
end $$;

do $$
declare
  main_name text := 'rollreview'; main_pass text := 'CHANGE-ME-1';
  pal_name text := 'rollreviewpal'; pal_pass text := 'CHANGE-ME-2';
  m uuid; p uuid; wk date := (date_trunc('week', now() at time zone 'utc'))::date;
begin
  m := pg_temp.rm_demo_user(main_name, main_pass, '{"level":0,"sel":0,"best":{},"stars":{},"seen":{"steer":1,"startitem":1,"jump":1,"hold":1,"roll":1,"missile":1,"pound":1,"burst":1,"dry":1,"item":1,"orb":1,"items":1,"look":1,"rroll":1},"runs":60,"name":"rollreview","color":"red","introDone":1,"tut":{"ph":"done","strokes":1,"comms":1,"modes":1,"trySd":1},"xp":4200,"drops":25000,"abilSeen":1,"look":{"eyes":"round"},"mode":"duel","diff":"medium","unlocked":1,"strokes":{"special":"rocket","skill":"pockets","item":"roller","own":["rocket","giant","freeze","storm","bomb","swim","pockets","boost","jackpot","shock","roller","trap","turret","whirl","boom"],"sk257":1,"b370":1,"it286":1},"bought":[],"itemIn":8}'::jsonb, 13);
  p := pg_temp.rm_demo_user(pal_name, pal_pass, '{"level":0,"sel":0,"best":{},"stars":{},"seen":{"steer":1,"startitem":1,"jump":1,"hold":1,"roll":1,"missile":1,"pound":1,"burst":1,"dry":1,"item":1,"orb":1,"items":1,"look":1,"rroll":1},"runs":60,"name":"rollreviewpal","color":"purple","introDone":1,"tut":{"ph":"done","strokes":1,"comms":1,"modes":1,"trySd":1},"xp":4200,"drops":25000,"abilSeen":1,"look":{"eyes":"sly"},"mode":"duel","diff":"medium","unlocked":1,"strokes":{"special":"rocket","skill":"pockets","item":"roller","own":["rocket","giant","freeze","storm","bomb","swim","pockets","boost","jackpot","shock","roller","trap","turret","whirl","boom"],"sk257":1,"b370":1,"it286":1},"bought":[],"itemIn":8}'::jsonb, 13);
  -- friends with each other, nothing blocked or pending between them
  delete from public.blocks where (blocker = m and blocked = p) or (blocker = p and blocked = m);
  delete from public.friend_requests where (from_id = m and to_id = p) or (from_id = p and to_id = m);
  insert into public.friendships (a, b) values (least(m, p), greatest(m, p)) on conflict do nothing;
  -- a few Time trial scores this week
  insert into public.trial_scores (user_id, week, stage, best) values (m, wk, 'island', 64), (m, wk, 'blank', 58), (m, wk, 'raft', 61),
    (p, wk, 'island', 71), (p, wk, 'blank', 49), (p, wk, 'raft', 55)
    on conflict (user_id, week, stage) do update set best = excluded.best, updated_at = now();
  raise notice 'App Review accounts ready: @% and @% (friends).', main_name, pal_name;
end $$;

select p.name as username, p.friend_code, s.xp, (select count(*) from public.friendships f where f.a = p.id or f.b = p.id) as friends
from public.profiles p join public.saves s on s.id = p.id join auth.users u on u.id = p.id
where coalesce(u.raw_app_meta_data ->> 'rm_demo', '') = 'app_review' order by p.name;
