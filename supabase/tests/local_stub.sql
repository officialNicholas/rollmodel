-- ONLY for testing the migration on a plain local Postgres. Never run this on the real Supabase project: it stands in for
-- what Supabase already has (its roles, the auth schema with auth.users and auth.uid(), and the realtime publication).
do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'anon') then create role anon nologin; end if;
  if not exists (select 1 from pg_roles where rolname = 'authenticated') then create role authenticated nologin; end if;
  if not exists (select 1 from pg_roles where rolname = 'service_role') then create role service_role nologin bypassrls; end if;
end $$;
create schema if not exists auth;
create table if not exists auth.users (id uuid primary key, is_anonymous boolean not null default true, created_at timestamptz not null default now());
alter table auth.users add column if not exists email text;
-- (liveops) what the admin functions read and write: the password hash, sign-in times, and the sessions and refresh tokens
-- Supabase keeps (theirs have more columns; these are the ones used)
alter table auth.users add column if not exists encrypted_password text;
alter table auth.users add column if not exists last_sign_in_at timestamptz;
alter table auth.users add column if not exists updated_at timestamptz;
create table if not exists auth.sessions (id uuid primary key, user_id uuid not null references auth.users (id) on delete cascade, created_at timestamptz not null default now());
create table if not exists auth.refresh_tokens (id bigserial primary key, token text, user_id varchar(255), session_id uuid references auth.sessions (id) on delete cascade, revoked boolean default false);
-- as Supabase does it: the caller's id from the request's JWT claims
create or replace function auth.uid() returns uuid language sql stable as $$
  select nullif(coalesce(current_setting('request.jwt.claim.sub', true), (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub')), '')::uuid
$$;
-- the request's JWT claims, as Supabase has it
create or replace function auth.jwt() returns jsonb language sql stable as $$
  select coalesce(nullif(current_setting('request.jwt.claim', true), ''), nullif(current_setting('request.jwt.claims', true), ''))::jsonb
$$;
grant usage on schema auth to anon, authenticated, service_role;
grant execute on function auth.uid(), auth.jwt() to anon, authenticated, service_role;
grant usage on schema public to anon, authenticated, service_role;
-- Supabase's default privileges hand new tables and functions in public to these roles; the migration has to take them back
alter default privileges in schema public grant all on tables to anon, authenticated, service_role;
alter default privileges in schema public grant all on functions to anon, authenticated, service_role;
