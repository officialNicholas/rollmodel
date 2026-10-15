-- Roll Model: usernames and accounts (game v306).
--
-- Run it after 20261015000000_friends.sql, the same way: Supabase > SQL Editor > New query, paste all of this, Run.
-- It's safe to run again.
--
-- What it adds:
-- - Usernames. A player's name is now their username: 3 to 16 letters, numbers or underscores, with at least one
--   letter, unique (ignoring capitals), and checked against a list of bad words and reserved names. The game runs the
--   same check as you type; this is the one that counts.
-- - Accounts. When a player makes a real account (the game asks when they first go online), their first name, last
--   name and birthday are kept here, with which terms and privacy policy they agreed to, and when. Only they can read
--   it, through rm_account(). An account needs a birthday at least 13 years ago.
-- - Logging in by username and password. Supabase signs in with an email, so each account gets a made-up one built from
--   its id (players never see it, and it never receives mail). rm_login_email() finds it from the username.
-- - Deleting an account from inside the game, which the App Store requires: rm_delete_me().
--
-- One setting in the dashboard goes with it: Authentication > Sign In / Providers > Email > turn OFF "Confirm email"
-- (the made-up emails can't receive a confirmation, and the game never asks for a real one).

-- ---------------------------------------------------------------- the username rules

-- why a username can't be used (null when it can). Mirrors unWhy() in the game (tools/v306_accounts.py).
create or replace function public._uname_bad(p text) returns boolean language plpgsql immutable set search_path = '' as $$
declare
  -- bad anywhere in the name (after capitals are split into words, leetspeak is undone, and the ok words below are taken out)
  sub text[] := array['fuck', 'fcuk', 'phuk', 'phuck', 'shit', 'cunt', 'nigg', 'fagg', 'bitch', 'whore', 'slut', 'twat', 'pussy', 'asshole',
    'hitler', 'porn', 'penis', 'vagina', 'dildo', 'boob', 'jizz', 'nazi', 'kkk', 'retard', 'wank', 'cock', 'dick', 'sex', 'rape', 'rapist',
    'piss', 'bastard', 'douche', 'bollock', 'tranny', 'molest', 'pedo', 'orgasm', 'horny', 'boner', 'blowjob', 'handjob', 'nipple', 'testic',
    'scrot', 'anal', 'cumshot', 'milf', 'hentai', 'xxx', 'killyou', 'suicide'];
  -- ordinary words that contain one of those
  allow text[] := array['scunthorpe', 'niggle', 'niggling', 'swank', 'peacock', 'cockatoo', 'cockatiel', 'cockpit', 'cockroach', 'woodcock',
    'hancock', 'hitchcock', 'shuttlecock', 'cockle', 'gamecock', 'babcock', 'cocker', 'cockney', 'dickens', 'dickinson', 'benedick', 'dickson',
    'sussex', 'essex', 'sextant', 'sexton', 'grape', 'drape', 'scrape', 'trapez', 'rapeseed', 'parapet', 'therape', 'therapist', 'serape', 'crape',
    'torpedo', 'pedometer', 'analy', 'analog', 'canal', 'kanal', 'banal', 'thorny', 'trombone'];
  -- bad as a word of its own (they hide inside ordinary words: class, cucumber, title, raccoon, hello...)
  whole text[] := array['ass', 'arse', 'cum', 'fag', 'fuk', 'spic', 'kike', 'chink', 'coon', 'tit', 'tits', 'anus', 'homo', 'damn', 'hell',
    'crap', 'prick', 'slag', 'twit', 'turd', 'nude', 'naked', 'kys'];
  camel text; raw text; sk text; w text; letters text; runs text := ''; run text := '';
begin
  camel := lower(regexp_replace(coalesce(p, ''), '([a-z])([A-Z])', '\1 \2', 'g'));
  raw := camel;                                                     -- as written: digits and _ split words ("Dick99")
  sk := translate(camel, '0123456789@$!|+', 'oizeasgtbgasiit');       -- leetspeak undone ("d1ck", "4ss")
  foreach w in array allow loop sk := replace(sk, w, ' '); end loop;
  letters := regexp_replace(sk, '[^a-z]', '', 'g');
  foreach w in array sub loop if position(w in letters) > 0 then return true; end if; end loop;
  -- word by word; letters spelled out one at a time ("d_i_c_k") count as a word too
  foreach w in array regexp_split_to_array(raw, '[^a-z]+') || regexp_split_to_array(sk, '[^a-z]+') loop
    if w = any(whole) then return true; end if;
  end loop;
  foreach w in array regexp_split_to_array(raw, '[^a-z]+') loop
    if char_length(w) = 1 then run := run || w; else if char_length(run) > 1 then runs := runs || ' ' || run; end if; run := ''; end if;
  end loop;
  if char_length(run) > 1 then runs := runs || ' ' || run; end if;
  foreach w in array regexp_split_to_array(btrim(runs), ' ') loop
    if w = any(whole) then return true; end if;
    foreach run in array sub loop if position(run in w) > 0 then return true; end if; end loop;
  end loop;
  return false;
end $$;

create or replace function public._uname_why(p text) returns text language plpgsql immutable set search_path = '' as $$
declare n text := coalesce(p, ''); l text := lower(coalesce(p, ''));
begin
  if char_length(n) < 3 then return 'short'; end if;
  if char_length(n) > 16 then return 'long'; end if;
  if n !~ '^[A-Za-z0-9_]+$' or n !~ '[A-Za-z]' then return 'chars'; end if;
  if l ~ '^(admin|administrator|mod|mods|moderator|staff|support|help|helpdesk|official|system|server|root|null|undefined|guest|you|cpu|bot|rollmodel|roll_model|bloop|olbloop|ol_bloop|marcelin|anthropic|claude|player[0-9_]*)$'
    or l ~ '^_*(admin|moderator|official)' or l ~ '(admin|moderator|official)_*[0-9]*$' then return 'reserved'; end if;
  if public._uname_bad(n) then return 'bad'; end if;
  return null;
end $$;

-- ---------------------------------------------------------------- usernames on the profiles

alter table public.profiles add column if not exists needs_name boolean not null default false;
-- names from before usernames that don't fit the rules, or that someone else already has, get a stand-in the player is asked to replace
update public.profiles p set name = 'player_' || substr(replace(p.id::text, '-', ''), 1, 8), needs_name = true
  where public._uname_why(p.name) is not null
     or exists (select 1 from public.profiles o where lower(o.name) = lower(p.name) and o.id < p.id);
create unique index if not exists profiles_name_lower on public.profiles (lower(name));

-- ---------------------------------------------------------------- accounts

create table if not exists public.accounts (
  id uuid primary key references auth.users (id) on delete cascade,
  first_name text not null check (char_length(first_name) between 1 and 40),
  last_name text not null check (char_length(last_name) between 1 and 40),
  birthday date not null,
  terms text not null check (terms ~ '^[a-z0-9.-]{1,32}$'),
  agreed_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.accounts enable row level security;
revoke all on public.accounts from anon, authenticated;

-- ---------------------------------------------------------------- the app's functions

-- is this username free? Anyone may ask (the game checks while you type, before you have an account). Answers
-- { ok: true } or { ok: false, why: short | long | chars | reserved | bad | taken }.
create or replace function public.rm_name_check(p_name text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare nm text := btrim(coalesce(p_name, '')); why text := public._uname_why(nm); u uuid := auth.uid();
begin
  if why is null and exists (select 1 from public.profiles where lower(name) = lower(nm) and id is distinct from u) then why := 'taken'; end if;
  return case when why is null then jsonb_build_object('ok', true, 'name', nm) else jsonb_build_object('ok', false, 'why', why) end;
end $$;

-- your profile. The first call makes it, with the username you give (it has to be free); after that it keeps your look
-- and rank up to date (change your username with rm_rename). Also says whether you have a real account yet.
create or replace function public.rm_me(p_name text default null, p_look jsonb default null, p_rank int default null)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); nm text := btrim(coalesce(p_name, '')); r public.profiles; why text; anon boolean;
begin
  if p_look is not null and (jsonb_typeof(p_look) <> 'object' or pg_column_size(p_look) >= 2048) then p_look := null; end if;
  select * into r from public.profiles where id = u;
  if r.id is null then
    why := public._uname_why(nm);
    if why is null and exists (select 1 from public.profiles where lower(name) = lower(nm)) then why := 'taken'; end if;
    if why is not null then return jsonb_build_object('ok', false, 'why', why); end if;
    begin
      insert into public.profiles (id, name, friend_code, look, rank)
        values (u, nm, public._new_friend_code(), coalesce(p_look, '{}'::jsonb), least(greatest(coalesce(p_rank, 1), 1), 999)) returning * into r;
    exception when unique_violation then return jsonb_build_object('ok', false, 'why', 'taken');
    end;
  else
    update public.profiles set look = coalesce(p_look, look), rank = coalesce(least(greatest(p_rank, 1), 999), rank) where id = u returning * into r;
  end if;
  select is_anonymous into anon from auth.users where id = u;
  return jsonb_build_object('ok', true, 'id', r.id, 'name', r.name, 'code', r.friend_code, 'rank', r.rank, 'needs_name', r.needs_name,
    'account', exists (select 1 from public.accounts where id = u), 'anon', coalesce(anon, true));
end $$;

-- a new username (or the first one, if you have no profile yet)
create or replace function public.rm_rename(p_name text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); nm text := btrim(coalesce(p_name, '')); why text := public._uname_why(nm);
begin
  if not exists (select 1 from public.profiles where id = u) then return public.rm_me(nm, null, null); end if;
  if why is null and exists (select 1 from public.profiles where lower(name) = lower(nm) and id <> u) then why := 'taken'; end if;
  if why is not null then return jsonb_build_object('ok', false, 'why', why); end if;
  if not public._rate(u, 'rename', 10) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  update public.profiles set name = nm, needs_name = false where id = u;
  return jsonb_build_object('ok', true, 'name', nm);
exception when unique_violation then return jsonb_build_object('ok', false, 'why', 'taken');
end $$;

-- the sign-in email of the account with this username (null if there's no such account, or it was never made into a
-- real one). Anyone may ask: it's how the game logs you in by username.
create or replace function public.rm_login_email(p_name text)
returns text language sql stable security definer set search_path = '' as $$
  select u.email from public.profiles p join auth.users u on u.id = p.id
  where lower(p.name) = lower(btrim(coalesce(p_name, ''))) and u.email is not null and not coalesce(u.is_anonymous, false)
  limit 1
$$;

-- your account details, saved once your player has been made into a real account (an email and password set on it).
-- Answers { ok: true } or { ok: false, why: not_signed_up | first | last | birthday | age | terms }.
create or replace function public.rm_account_save(p_first text, p_last text, p_birthday date, p_terms text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); anon boolean;
  f text := btrim(regexp_replace(coalesce(p_first, ''), '\s+', ' ', 'g')); l text := btrim(regexp_replace(coalesce(p_last, ''), '\s+', ' ', 'g'));
begin
  select is_anonymous into anon from auth.users where id = u;
  if anon is distinct from false then return jsonb_build_object('ok', false, 'why', 'not_signed_up'); end if;
  if f !~ '^[[:alpha:]][[:alpha:] .''-]{0,39}$' then return jsonb_build_object('ok', false, 'why', 'first'); end if;
  if l !~ '^[[:alpha:]][[:alpha:] .''-]{0,39}$' then return jsonb_build_object('ok', false, 'why', 'last'); end if;
  if p_birthday is null or p_birthday < date '1900-01-01' or p_birthday > current_date then return jsonb_build_object('ok', false, 'why', 'birthday'); end if;
  if p_birthday > (current_date - interval '13 years')::date then return jsonb_build_object('ok', false, 'why', 'age'); end if;
  if coalesce(p_terms, '') !~ '^[a-z0-9.-]{1,32}$' then return jsonb_build_object('ok', false, 'why', 'terms'); end if;
  insert into public.accounts (id, first_name, last_name, birthday, terms) values (u, f, l, p_birthday, p_terms)
    on conflict (id) do update set first_name = excluded.first_name, last_name = excluded.last_name, birthday = excluded.birthday,
      terms = excluded.terms, agreed_at = case when public.accounts.terms = excluded.terms then public.accounts.agreed_at else now() end, updated_at = now();
  return jsonb_build_object('ok', true);
end $$;

-- what your account holds (for Settings), or null
create or replace function public.rm_account()
returns jsonb language sql stable security definer set search_path = '' as $$
  select jsonb_build_object('username', p.name, 'first_name', a.first_name, 'last_name', a.last_name, 'birthday', a.birthday, 'terms', a.terms, 'agreed_at', a.agreed_at)
  from public.accounts a left join public.profiles p on p.id = a.id where a.id = public._me()
$$;

-- delete your account and everything that hangs off it: profile, friends, requests, invites, scores, account details
create or replace function public.rm_delete_me()
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me();
begin
  delete from public.rate_events where user_id = u;
  delete from auth.users where id = u;
  return jsonb_build_object('ok', true);
end $$;

-- ---------------------------------------------------------------- who may call what

revoke all on function public._uname_bad(text), public._uname_why(text) from public, anon, authenticated;
revoke all on function public.rm_name_check(text), public.rm_login_email(text) from public;
grant execute on function public.rm_name_check(text), public.rm_login_email(text) to anon, authenticated;
revoke all on function public.rm_rename(text), public.rm_account_save(text, text, date, text), public.rm_account(), public.rm_delete_me() from public, anon;
grant execute on function public.rm_rename(text), public.rm_account_save(text, text, date, text), public.rm_account(), public.rm_delete_me() to authenticated;
