-- Roll Model: account emails (game v355): a private email for each account, the welcome email with a button that confirms it,
-- "Forgot password?" with a reset link, and a "your password was changed" notice.
--
-- Run it after 20261018000000_liveops.sql, the same way: Supabase > SQL Editor > New query, paste all of this, Run. It's safe to
-- run again (it also refreshes the email templates).
--
-- How it works:
-- - A player's email lives in account_emails, private like the rest of their account: other players never see it, and the
--   game's sign-in stays by username (the made-up u<id>@rollmodel.invalid address), so no one can look an email up from a name.
-- - The emails are sent by the database itself, through Resend (https://resend.com), with Supabase's pg_net extension. The
--   Resend key lives in Supabase's Vault, put there by you; it's never in the game, the website, or this file.
-- - The links in the emails carry a one-time token. Only a hash of it is kept here. A confirm link works for 24 hours, a reset
--   link once, for 30 minutes. Reset links only go to confirmed emails, so a mistyped address can't be used to take an account.
-- - "Forgot password?" never says whether an account exists. Each account gets at most 3 reset emails an hour.
--
-- Switching the emails on (once, after the domain and Resend are set up; see site/README.md):
--   1. Database > Extensions: turn on pg_net (this file tries to as well).
--   2. In the SQL editor, put the Resend key in the Vault (only you ever see it):
--        select vault.create_secret('re_your_key_here', 'resend_api_key');
--   3. Tell it your website and addresses:
--        update public.rm_settings set v = v || '{"site": "https://playrollmodel.com", "sender": "Roll Model <hello@mail.playrollmodel.com>",
--          "support": "support@playrollmodel.com"}' where k = 'mail';
--   Until all three are done, nothing is sent; emails are still saved, and the game says so.

do $$ begin
  create extension if not exists pg_net;
exception when others then raise notice 'pg_net is not available here, so no email will be sent: %', sqlerrm;
end $$;

-- ---------------------------------------------------------------- tables

create table if not exists public.account_emails (
  id uuid primary key references auth.users (id) on delete cascade,
  email text not null check (char_length(email) between 6 and 254 and email ~ '^[^@\s<>",;]+@[^@\s<>",;]+\.[A-Za-z]{2,}$'),
  verified_at timestamptz,
  updated_at timestamptz not null default now()
);
create unique index if not exists account_emails_email on public.account_emails (lower(email));

-- the links' one-time tokens: only their hash, who they're for, what they do, and until when
create table if not exists public.mail_tokens (
  hash bytea primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  kind text not null check (kind in ('verify', 'reset')),
  email text,
  expires_at timestamptz not null,
  used_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists mail_tokens_user on public.mail_tokens (user_id, kind);

-- what was sent, for checking delivery (no addresses; gone with the account)
create table if not exists public.mail_log (
  id bigint generated always as identity primary key,
  at timestamptz not null default now(),
  user_id uuid references auth.users (id) on delete cascade,
  kind text not null,
  req bigint,
  note text
);
create index if not exists mail_log_at on public.mail_log (at desc);

create table if not exists public.mail_templates (
  kind text primary key check (kind in ('welcome', 'reset', 'changed')),
  subject text not null,
  html text not null,
  text text not null
);

insert into public.rm_settings (k, v) values ('mail', '{"paused": false, "site": "", "sender": "", "support": ""}') on conflict (k) do nothing;

alter table public.account_emails enable row level security;
alter table public.mail_tokens enable row level security;
alter table public.mail_log enable row level security;
alter table public.mail_templates enable row level security;
revoke all on public.account_emails, public.mail_tokens, public.mail_log, public.mail_templates from anon, authenticated;
revoke all on sequence public.mail_log_id_seq from public, anon, authenticated;

-- ---------------------------------------------------------------- helpers (not callable from the app)

-- a new one-time token: token (goes in the link) and hash (kept here)
create or replace function public._mail_token(out token text, out hash bytea) language plpgsql volatile set search_path = '' as $$
begin
  token := rtrim(translate(encode(extensions.gen_random_bytes(32), 'base64'), '+/', '-_'), '=');
  hash := extensions.digest(convert_to(token, 'UTF8'), 'sha256');
end $$;

create or replace function public._esc(p text) returns text language sql immutable set search_path = '' as $$
  select replace(replace(replace(replace(replace(coalesce(p, ''), '&', '&amp;'), '<', '&lt;'), '>', '&gt;'), '"', '&quot;'), '''', '&#39;')
$$;

-- fill a template's {{...}} values (escaped for HTML when p_html)
create or replace function public._fill(p_t text, p_vars jsonb, p_html boolean) returns text language plpgsql immutable set search_path = '' as $$
declare k text; v text; t text := p_t;
begin
  for k, v in select key, value from jsonb_each_text(p_vars) loop
    t := replace(t, '{{' || k || '}}', case when p_html then public._esc(v) else coalesce(v, '') end);
  end loop;
  return t;
end $$;

-- the mail settings, and whether sending is possible at all (pg_net there, the key in the Vault, the website and sender set)
create or replace function public._mail_cfg() returns jsonb language sql stable set search_path = '' as $$
  select coalesce((select v from public.rm_settings where k = 'mail'), '{}'::jsonb)
$$;
create or replace function public._mail_key() returns text language plpgsql stable set search_path = '' as $$
declare k text;
begin
  if to_regclass('vault.decrypted_secrets') is null then return null; end if;
  execute 'select decrypted_secret from vault.decrypted_secrets where name = $1 order by created_at desc limit 1' into k using 'resend_api_key';
  return nullif(btrim(coalesce(k, '')), '');
exception when others then return null;
end $$;
create or replace function public._mail_on() returns boolean language sql stable set search_path = '' as $$
  select to_regprocedure('net.http_post(text,jsonb,jsonb,jsonb,integer)') is not null and public._mail_key() is not null
     and coalesce(public._mail_cfg() ->> 'site', '') ~ '^https://' and coalesce(public._mail_cfg() ->> 'sender', '') like '%@%'
     and coalesce(public._mail_cfg() ->> 'support', '') like '%@%'
     and coalesce(public._mail_cfg() ->> 'paused', 'false') <> 'true'
$$;

-- send one of the templates to p_to, through Resend. Returns whether it went (it's sent after this transaction commits)
create or replace function public._mail(p_kind text, p_user uuid, p_to text, p_vars jsonb) returns boolean language plpgsql volatile set search_path = '' as $$
declare cfg jsonb := public._mail_cfg(); t public.mail_templates; v jsonb; req bigint;
begin
  select * into t from public.mail_templates where kind = p_kind;
  if t.kind is null or not public._mail_on() then
    insert into public.mail_log (user_id, kind, note) values (p_user, p_kind, case when t.kind is null then 'no template' else 'mail off' end);
    return false;
  end if;
  v := jsonb_build_object('site', rtrim(cfg ->> 'site', '/'), 'support', cfg ->> 'support',
         'year', to_char(now() at time zone 'utc', 'YYYY')) || coalesce(p_vars, '{}'::jsonb);
  execute 'select net.http_post(url := $1, body := $2, headers := $3, timeout_milliseconds := 10000)' into req using
    'https://api.resend.com/emails',
    jsonb_build_object('from', cfg ->> 'sender', 'to', jsonb_build_array(p_to), 'subject', public._fill(t.subject, v, false),
      'html', public._fill(t.html, v, true), 'text', public._fill(t.text, v, false),
      'reply_to', cfg ->> 'support', 'tags', jsonb_build_array(jsonb_build_object('name', 'kind', 'value', p_kind))),
    jsonb_build_object('Authorization', 'Bearer ' || public._mail_key(), 'Content-Type', 'application/json');
  insert into public.mail_log (user_id, kind, req) values (p_user, p_kind, req);
  return true;
end $$;

-- a token's row, by the token in a link (null when there's none)
create or replace function public._mail_find(p_token text, p_kind text) returns public.mail_tokens language sql stable set search_path = '' as $$
  select * from public.mail_tokens where kind = p_kind and p_token ~ '^[A-Za-z0-9_-]{20,100}$' and hash = extensions.digest(convert_to(p_token, 'UTF8'), 'sha256')
$$;

-- the welcome email (also sent again on request): their username and a button that confirms the email, for 24 hours
create or replace function public._mail_welcome(p_user uuid, p_email text) returns boolean language plpgsql volatile set search_path = '' as $$
declare tk record; nm text;
begin
  delete from public.mail_tokens where user_id = p_user and kind = 'verify';
  select * into tk from public._mail_token();
  insert into public.mail_tokens (hash, user_id, kind, email, expires_at) values (tk.hash, p_user, 'verify', p_email, now() + interval '24 hours');
  select name into nm from public.profiles where id = p_user;
  return public._mail('welcome', p_user, p_email, jsonb_build_object('username', coalesce(nm, 'Player'),
    'link', rtrim(public._mail_cfg() ->> 'site', '/') || '/confirm#t=' || tk.token));
end $$;

-- a reset email to a player's confirmed email: a link that works once, for 30 minutes (any earlier one stops working)
create or replace function public._mail_reset(p_user uuid) returns boolean language plpgsql volatile set search_path = '' as $$
declare tk record; nm text; em text;
begin
  select email into em from public.account_emails where id = p_user and verified_at is not null;
  if em is null then return false; end if;
  delete from public.mail_tokens where user_id = p_user and kind = 'reset';
  select * into tk from public._mail_token();
  insert into public.mail_tokens (hash, user_id, kind, expires_at) values (tk.hash, p_user, 'reset', now() + interval '30 minutes');
  select name into nm from public.profiles where id = p_user;
  return public._mail('reset', p_user, em, jsonb_build_object('username', coalesce(nm, 'Player'),
    'link', rtrim(public._mail_cfg() ->> 'site', '/') || '/reset#t=' || tk.token));
end $$;

-- ---------------------------------------------------------------- what the game calls (signed in)

-- your email, and whether it's confirmed: { email, verified } ({ email: null } when there's none)
create or replace function public.rm_email_get()
returns jsonb language sql stable security definer set search_path = '' as $$
  select coalesce((select jsonb_build_object('email', email, 'verified', verified_at is not null, 'mail', public._mail_on())
                     from public.account_emails where id = public._me()),
                  jsonb_build_object('email', null, 'verified', false, 'mail', public._mail_on()))
$$;

-- your email: saved (accounts only), and the welcome email sent to it with a button to confirm it. The same confirmed email again
-- changes nothing. Answers { ok: true, sent } (sent: false while emails aren't switched on), or { ok: false, why: no_account |
-- bad | taken | slow_down }
create or replace function public.rm_email_set(p_email text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); em text := btrim(coalesce(p_email, '')); cur public.account_emails;
begin
  if not exists (select 1 from public.accounts where id = u) then return jsonb_build_object('ok', false, 'why', 'no_account'); end if;
  if char_length(em) not between 6 and 254 or em !~ '^[^@\s<>",;]+@[^@\s<>",;]+\.[A-Za-z]{2,}$' then return jsonb_build_object('ok', false, 'why', 'bad'); end if;
  select * into cur from public.account_emails where id = u;
  if cur.id is not null and lower(cur.email) = lower(em) and cur.verified_at is not null then return jsonb_build_object('ok', true, 'sent', false, 'verified', true); end if;
  if exists (select 1 from public.account_emails where lower(email) = lower(em) and id <> u) then return jsonb_build_object('ok', false, 'why', 'taken'); end if;
  if not public._rate(u, 'email_set', 5) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  begin
    insert into public.account_emails (id, email) values (u, em)
      on conflict (id) do update set email = excluded.email, verified_at = case when lower(public.account_emails.email) = lower(excluded.email) then public.account_emails.verified_at end, updated_at = now();
  exception when unique_violation then return jsonb_build_object('ok', false, 'why', 'taken'); -- (someone else took it just now)
  end;
  return jsonb_build_object('ok', true, 'sent', public._mail_welcome(u, em), 'verified', false);
end $$;

-- the welcome email again (for an email not confirmed yet). { ok: true, sent } or { ok: false, why: none | verified | slow_down }
create or replace function public.rm_email_resend()
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); cur public.account_emails;
begin
  select * into cur from public.account_emails where id = u;
  if cur.id is null then return jsonb_build_object('ok', false, 'why', 'none'); end if;
  if cur.verified_at is not null then return jsonb_build_object('ok', false, 'why', 'verified'); end if;
  if not public._rate(u, 'email_set', 5) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  return jsonb_build_object('ok', true, 'sent', public._mail_welcome(u, cur.email));
end $$;

-- ---------------------------------------------------------------- what the website calls (anyone)

-- the confirm button: { ok: true, username } or { ok: false, why: expired | used | bad }
create or replace function public.rm_email_verify(p_token text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare t public.mail_tokens := public._mail_find(p_token, 'verify'); nm text;
begin
  if t.hash is null then return jsonb_build_object('ok', false, 'why', 'bad'); end if;
  if t.used_at is not null then return jsonb_build_object('ok', false, 'why', 'used'); end if;
  if t.expires_at < now() then return jsonb_build_object('ok', false, 'why', 'expired'); end if;
  -- (the email was changed since: this link was for the old one)
  if not exists (select 1 from public.account_emails where id = t.user_id and lower(email) = lower(t.email)) then return jsonb_build_object('ok', false, 'why', 'bad'); end if;
  update public.mail_tokens set used_at = now() where hash = t.hash;
  update public.account_emails set verified_at = coalesce(verified_at, now()) where id = t.user_id;
  select name into nm from public.profiles where id = t.user_id;
  return jsonb_build_object('ok', true, 'username', nm);
end $$;

-- "Forgot password?": a username or an email. If it's an account with a confirmed email, a reset link goes to that email. It
-- always answers { ok: true }, so it never tells whether an account exists. At most 3 an hour for an account, 500 an hour in all
create or replace function public.rm_reset_request(p_who text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare w text := btrim(coalesce(p_who, '')); u uuid;
begin
  if char_length(w) between 3 and 254 then
    if position('@' in w) > 0 then
      select id into u from public.account_emails where lower(email) = lower(w) and verified_at is not null;
    else
      select p.id into u from public.profiles p join public.account_emails e on e.id = p.id and e.verified_at is not null where lower(p.name) = lower(w);
    end if;
  end if;
  if u is not null and public._rate(u, 'reset_mail', 3) and public._rate('00000000-0000-0000-0000-000000000000'::uuid, 'reset_mail_all', 500) then
    perform public._mail_reset(u);
  end if;
  return jsonb_build_object('ok', true);
end $$;

-- the reset page: a new password (8 to 72 characters, a letter and a digit), then signed out everywhere and a "changed" email.
-- { ok: true, username } or { ok: false, why: expired | used | bad | weak }. A weak password doesn't use the link up
create or replace function public.rm_reset_password(p_token text, p_password text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare t public.mail_tokens := public._mail_find(p_token, 'reset'); nm text;
begin
  if t.hash is null then return jsonb_build_object('ok', false, 'why', 'bad'); end if;
  if t.used_at is not null then return jsonb_build_object('ok', false, 'why', 'used'); end if;
  if t.expires_at < now() then return jsonb_build_object('ok', false, 'why', 'expired'); end if;
  if p_password is null or char_length(p_password) < 8 or octet_length(p_password) > 72 or p_password !~ '[A-Za-z]' or p_password !~ '[0-9]' then
    return jsonb_build_object('ok', false, 'why', 'weak');
  end if;
  if not exists (select 1 from auth.users where id = t.user_id and not is_anonymous) then return jsonb_build_object('ok', false, 'why', 'bad'); end if;
  update public.mail_tokens set used_at = now() where hash = t.hash;
  delete from public.mail_tokens where user_id = t.user_id and kind = 'reset' and hash <> t.hash;
  update auth.users set encrypted_password = extensions.crypt(p_password, extensions.gen_salt('bf', 10)), updated_at = now() where id = t.user_id;
  perform public._end_sessions(t.user_id);
  select name into nm from public.profiles where id = t.user_id;
  return jsonb_build_object('ok', true, 'username', nm);
end $$;

-- ---------------------------------------------------------------- the "password changed" notice, however it changed

-- the game setting a new password, a reset link, or support: the player gets a "your password was changed" email (when they have a
-- confirmed email). Never in the way of the change itself: anything that goes wrong here is skipped
create or replace function public._mail_changed() returns trigger language plpgsql security definer set search_path = '' as $$
declare em text; nm text;
begin
  if old.encrypted_password is null or old.encrypted_password = '' or new.encrypted_password is not distinct from old.encrypted_password then return new; end if;
  begin
    select email into em from public.account_emails where id = new.id and verified_at is not null;
    if em is not null then
      select name into nm from public.profiles where id = new.id;
      perform public._mail('changed', new.id, em, jsonb_build_object('username', coalesce(nm, 'Player'),
        'when', to_char(now() at time zone 'utc', 'FMMonth FMDD, YYYY "at" FMHH12:MI AM "UTC"'),
        'link', rtrim(public._mail_cfg() ->> 'site', '/') || '/forgot'));
    end if;
  exception when others then null;
  end;
  return new;
end $$;
drop trigger if exists rm_mail_changed on auth.users;
create trigger rm_mail_changed after update of encrypted_password on auth.users for each row execute function public._mail_changed();

-- ---------------------------------------------------------------- the dashboard

-- a player's email and whether it's confirmed (null when there's none)
create or replace function public.adm_player_email(p_id uuid)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  perform public._adm();
  return (select jsonb_build_object('email', email, 'verified', verified_at is not null, 'verified_at', verified_at, 'updated_at', updated_at)
            from public.account_emails where id = p_id);
end $$;

-- players with exactly this email (any case): the same rows as adm_find
create or replace function public.adm_find_email(p_q text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  perform public._adm();
  return (select coalesce(jsonb_agg(jsonb_build_object('id', p.id, 'name', p.name, 'code', p.friend_code, 'rank', p.rank,
            'account', exists (select 1 from public.accounts a where a.id = p.id), 'created_at', p.created_at, 'last_seen', p.last_seen)), '[]'::jsonb)
            from public.account_emails e join public.profiles p on p.id = e.id where lower(e.email) = lower(btrim(coalesce(p_q, ''))));
end $$;

-- send a player a reset link (better than making up a password for them). { ok: true, sent } or { ok: false, why: missing | admin |
-- no_email | slow_down }
create or replace function public.adm_email_reset(p_id uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare a uuid := public._adm(); sent boolean;
begin
  if not exists (select 1 from auth.users where id = p_id) then return jsonb_build_object('ok', false, 'why', 'missing'); end if;
  if exists (select 1 from public.rm_admins where id = p_id) then return jsonb_build_object('ok', false, 'why', 'admin'); end if;
  if not exists (select 1 from public.account_emails where id = p_id and verified_at is not null) then return jsonb_build_object('ok', false, 'why', 'no_email'); end if;
  if not public._rate(a, 'adm_password', 60) then return jsonb_build_object('ok', false, 'why', 'slow_down'); end if;
  sent := public._mail_reset(p_id);
  perform public._audit(a, 'email_reset', p_id::text, jsonb_build_object('name', (select name from public.profiles where id = p_id), 'sent', sent));
  return jsonb_build_object('ok', true, 'sent', sent);
end $$;

-- ---------------------------------------------------------------- the templates (built from email/ by tools/email_build.py)

-- TEMPLATES (tools/email_sql.py writes what's between these lines)
insert into public.mail_templates (kind, subject, html, text) values ('welcome',
  $s$Welcome to Roll Model, {{username}}!$s$,
  $h$<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>Welcome to Roll Model, {{username}}!</title>
<link href="https://fonts.googleapis.com/css2?family=Bowlby+One&amp;display=swap" rel="stylesheet">
<style>
  body{margin:0;padding:0;-webkit-text-size-adjust:100%;text-size-adjust:100%}
  a{text-decoration:none}
  @media (max-width:620px){
    .wrap{padding:12px 10px 28px!important}
    .card{border-radius:22px!important}
    .pad{padding-left:22px!important;padding-right:22px!important}
    .h1{font-size:28px!important;line-height:32px!important}
    .name{font-size:26px!important}
  }
  @media (prefers-color-scheme:dark){
    .bg{background:#110E18!important}
    .card{background:#1E1928!important;border-color:#342C42!important}
    .ink{color:#F4EEE3!important}
    .soft{color:#B9AFC6!important}
    .namebox{background:#2A2336!important;border-color:#CBE45A!important}
    .namebox .name{color:#CBE45A!important}
    .rule{border-color:#342C42!important}
    .warn{background:#2A2336!important;border-color:#4A3F5C!important}
  }
</style>
</head>
<body class="bg" style="margin:0;padding:0;background:#F4EEE3">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;mso-hide:all">Your username is {{username}}. Confirm your email so you can always get back in.&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
<table role="presentation" class="bg" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#F4EEE3">
<tr><td class="wrap" align="center" style="padding:28px 16px 40px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:560px">
    <tr><td align="center" style="padding:0 0 6px">
      <a href="{{site}}" style="text-decoration:none"><img src="{{site}}/email/logo.png" width="230" height="161" alt="Roll Model" style="display:block;width:230px;max-width:62%;height:auto;border:0"></a>
    </td></tr>
    <tr><td>
      <table role="presentation" class="card" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#FFFCF6;border:1px solid #E6DCCB;border-radius:28px;border-collapse:separate">
        <tr><td class="pad" style="padding:34px 40px 36px">
          <h1 class="h1 ink" style="margin:0 0 14px;font-family:'Bowlby One','Arial Black','Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif;font-weight:900;font-synthesis:none;font-size:32px;line-height:36px;color:#171320;text-align:center;letter-spacing:.2px">Welcome to Roll&nbsp;Model!</h1>
          <p class="ink" style="margin:0 0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:25px;color:#171320;text-align:center">Your account is ready. This is the name the canvas will know you by:</p>
          <table role="presentation" class="namebox" align="center" cellpadding="0" cellspacing="0" border="0" style="margin:6px auto 22px;background:#CBE45A;border:2px solid #171320;border-radius:18px;border-collapse:separate">
            <tr><td align="center" style="padding:12px 30px 14px">
              <p class="soft" style="margin:0 0 2px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:11px;line-height:14px;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:#171320;opacity:.7">Your username</p>
              <p class="name" style="margin:0;font-family:'Bowlby One','Arial Black','Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif;font-weight:900;font-synthesis:none;font-size:30px;line-height:36px;color:#171320;word-break:break-all">{{username}}</p>
            </td></tr>
          </table>
          <p class="ink" style="margin:0 0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:25px;color:#171320;text-align:center">Log in with it and your password on any phone, and your progress comes with you.</p>
          <p class="ink" style="margin:0 0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:25px;color:#171320;text-align:center">One last thing: confirm your email, so we can get you back in if you ever forget your password.</p>
          <table role="presentation" align="center" cellpadding="0" cellspacing="0" border="0" style="margin:8px auto 22px">
            <tr><td align="center" bgcolor="#E3122F" style="border-radius:999px;background:#E3122F;border-bottom:4px solid #99091F">
              <a href="{{link}}" style="display:inline-block;padding:16px 34px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:17px;line-height:20px;font-weight:800;color:#FFFFFF;text-decoration:none;border-radius:999px">Confirm my email</a>
            </td></tr>
          </table>
          <p class="soft" style="margin:0 0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:13px;line-height:20px;color:#6E6577;text-align:center">The button works for 24 hours.</p>
          <hr class="rule" style="border:0;border-top:1px solid #E6DCCB;margin:22px 0 20px">
          <p class="ink" style="margin:0 0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:25px;color:#171320;text-align:center">See you on the canvas!<br><b>Ol&#8217; Bloop</b>, your coach</p>

        </td></tr>
      </table>
    </td></tr>
    <tr><td class="pad" style="padding:22px 30px 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:12px;line-height:18px;color:#6E6577;text-align:center">
      <p class="soft" style="margin:0 0 8px;color:#6E6577">You got this email because a Roll Model account was made with this address. If that wasn&#8217;t you, ignore it.</p>
      <p class="soft" style="margin:0 0 8px;color:#6E6577">Questions? Write to <a href="mailto:{{support}}" style="color:#6E6577;text-decoration:underline">{{support}}</a></p>
      <p class="soft" style="margin:0;color:#6E6577"><a href="{{site}}/privacy" style="color:#6E6577;text-decoration:underline">Privacy Policy</a> &nbsp;&middot;&nbsp; <a href="{{site}}/terms" style="color:#6E6577;text-decoration:underline">Terms of Service</a> &nbsp;&middot;&nbsp; <a href="{{site}}/support" style="color:#6E6577;text-decoration:underline">Support</a></p>
      <p class="soft" style="margin:10px 0 0;color:#6E6577">Roll Model &middot; A Marcelin Game &middot; &copy; {{year}}</p>
    </td></tr>
  </table>
</td></tr>
</table>
</body>
</html>
$h$,
  $t$Welcome to Roll Model!

Your account is ready. Your username is:

    {{username}}

Log in with it and your password on any phone, and your progress comes with you.

One last thing: confirm your email, so we can get you back in if you ever forget your password:
{{link}}
(The link works for 24 hours.)

See you on the canvas!
Ol' Bloop, your coach

--
You got this email because a Roll Model account was made with this address. If that wasn't you, ignore it.
Questions? Write to {{support}}
Privacy Policy: {{site}}/privacy  Terms: {{site}}/terms  Support: {{site}}/support
Roll Model, A Marcelin Game
$t$)
  on conflict (kind) do update set subject = excluded.subject, html = excluded.html, text = excluded.text;
insert into public.mail_templates (kind, subject, html, text) values ('reset',
  $s$Reset your Roll Model password$s$,
  $h$<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>Reset your Roll Model password</title>
<link href="https://fonts.googleapis.com/css2?family=Bowlby+One&amp;display=swap" rel="stylesheet">
<style>
  body{margin:0;padding:0;-webkit-text-size-adjust:100%;text-size-adjust:100%}
  a{text-decoration:none}
  @media (max-width:620px){
    .wrap{padding:12px 10px 28px!important}
    .card{border-radius:22px!important}
    .pad{padding-left:22px!important;padding-right:22px!important}
    .h1{font-size:28px!important;line-height:32px!important}
    .name{font-size:26px!important}
  }
  @media (prefers-color-scheme:dark){
    .bg{background:#110E18!important}
    .card{background:#1E1928!important;border-color:#342C42!important}
    .ink{color:#F4EEE3!important}
    .soft{color:#B9AFC6!important}
    .namebox{background:#2A2336!important;border-color:#CBE45A!important}
    .namebox .name{color:#CBE45A!important}
    .rule{border-color:#342C42!important}
    .warn{background:#2A2336!important;border-color:#4A3F5C!important}
  }
</style>
</head>
<body class="bg" style="margin:0;padding:0;background:#F4EEE3">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;mso-hide:all">Choose a new password for {{username}}. The link works for 30 minutes.&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
<table role="presentation" class="bg" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#F4EEE3">
<tr><td class="wrap" align="center" style="padding:28px 16px 40px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:560px">
    <tr><td align="center" style="padding:0 0 6px">
      <a href="{{site}}" style="text-decoration:none"><img src="{{site}}/email/logo.png" width="230" height="161" alt="Roll Model" style="display:block;width:230px;max-width:62%;height:auto;border:0"></a>
    </td></tr>
    <tr><td>
      <table role="presentation" class="card" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#FFFCF6;border:1px solid #E6DCCB;border-radius:28px;border-collapse:separate">
        <tr><td class="pad" style="padding:34px 40px 36px">
          <h1 class="h1 ink" style="margin:0 0 14px;font-family:'Bowlby One','Arial Black','Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif;font-weight:900;font-synthesis:none;font-size:32px;line-height:36px;color:#171320;text-align:center;letter-spacing:.2px">Forgot your password?</h1>
          <p class="ink" style="margin:0 0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:25px;color:#171320;text-align:center">No problem, <b>{{username}}</b>. Tap the button and choose a new one.</p>
          <table role="presentation" align="center" cellpadding="0" cellspacing="0" border="0" style="margin:8px auto 22px">
            <tr><td align="center" bgcolor="#E3122F" style="border-radius:999px;background:#E3122F;border-bottom:4px solid #99091F">
              <a href="{{link}}" style="display:inline-block;padding:16px 34px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:17px;line-height:20px;font-weight:800;color:#FFFFFF;text-decoration:none;border-radius:999px">Choose a new password</a>
            </td></tr>
          </table>
          <p class="soft" style="margin:0 0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:13px;line-height:20px;color:#6E6577;text-align:center">The button works once, for 30 minutes.</p>
          <hr class="rule" style="border:0;border-top:1px solid #E6DCCB;margin:22px 0 20px">
          <p class="soft" style="margin:0 0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:13px;line-height:20px;color:#6E6577;text-align:center">Didn&#8217;t ask for this? Ignore this email. Your password stays the same and your account is safe.</p>
          <p class="soft" style="margin:0 0 4px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:13px;line-height:20px;color:#6E6577;text-align:center">Button not working? Copy this link into your browser:</p>
          <p style="margin:0 0 4px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:12px;line-height:18px;text-align:center;word-break:break-all"><a href="{{link}}" style="color:#E3122F;text-decoration:underline">{{link}}</a></p>

        </td></tr>
      </table>
    </td></tr>
    <tr><td class="pad" style="padding:22px 30px 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:12px;line-height:18px;color:#6E6577;text-align:center">
      <p class="soft" style="margin:0 0 8px;color:#6E6577">You got this email because someone asked to reset the password of the Roll Model account with this address.</p>
      <p class="soft" style="margin:0 0 8px;color:#6E6577">Questions? Write to <a href="mailto:{{support}}" style="color:#6E6577;text-decoration:underline">{{support}}</a></p>
      <p class="soft" style="margin:0;color:#6E6577"><a href="{{site}}/privacy" style="color:#6E6577;text-decoration:underline">Privacy Policy</a> &nbsp;&middot;&nbsp; <a href="{{site}}/terms" style="color:#6E6577;text-decoration:underline">Terms of Service</a> &nbsp;&middot;&nbsp; <a href="{{site}}/support" style="color:#6E6577;text-decoration:underline">Support</a></p>
      <p class="soft" style="margin:10px 0 0;color:#6E6577">Roll Model &middot; A Marcelin Game &middot; &copy; {{year}}</p>
    </td></tr>
  </table>
</td></tr>
</table>
</body>
</html>
$h$,
  $t$Forgot your password?

No problem, {{username}}. Open this link and choose a new one:
{{link}}

The link works once, for 30 minutes.

Didn't ask for this? Ignore this email. Your password stays the same and your account is safe.

--
You got this email because someone asked to reset the password of the Roll Model account with this address.
Questions? Write to {{support}}
Privacy Policy: {{site}}/privacy  Terms: {{site}}/terms  Support: {{site}}/support
Roll Model, A Marcelin Game
$t$)
  on conflict (kind) do update set subject = excluded.subject, html = excluded.html, text = excluded.text;
insert into public.mail_templates (kind, subject, html, text) values ('changed',
  $s$Your Roll Model password was changed$s$,
  $h$<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>Your Roll Model password was changed</title>
<link href="https://fonts.googleapis.com/css2?family=Bowlby+One&amp;display=swap" rel="stylesheet">
<style>
  body{margin:0;padding:0;-webkit-text-size-adjust:100%;text-size-adjust:100%}
  a{text-decoration:none}
  @media (max-width:620px){
    .wrap{padding:12px 10px 28px!important}
    .card{border-radius:22px!important}
    .pad{padding-left:22px!important;padding-right:22px!important}
    .h1{font-size:28px!important;line-height:32px!important}
    .name{font-size:26px!important}
  }
  @media (prefers-color-scheme:dark){
    .bg{background:#110E18!important}
    .card{background:#1E1928!important;border-color:#342C42!important}
    .ink{color:#F4EEE3!important}
    .soft{color:#B9AFC6!important}
    .namebox{background:#2A2336!important;border-color:#CBE45A!important}
    .namebox .name{color:#CBE45A!important}
    .rule{border-color:#342C42!important}
    .warn{background:#2A2336!important;border-color:#4A3F5C!important}
  }
</style>
</head>
<body class="bg" style="margin:0;padding:0;background:#F4EEE3">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;mso-hide:all">If this was you, you&#8217;re all set.&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
<table role="presentation" class="bg" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#F4EEE3">
<tr><td class="wrap" align="center" style="padding:28px 16px 40px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:560px">
    <tr><td align="center" style="padding:0 0 6px">
      <a href="{{site}}" style="text-decoration:none"><img src="{{site}}/email/logo.png" width="230" height="161" alt="Roll Model" style="display:block;width:230px;max-width:62%;height:auto;border:0"></a>
    </td></tr>
    <tr><td>
      <table role="presentation" class="card" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#FFFCF6;border:1px solid #E6DCCB;border-radius:28px;border-collapse:separate">
        <tr><td class="pad" style="padding:34px 40px 36px">
          <h1 class="h1 ink" style="margin:0 0 14px;font-family:'Bowlby One','Arial Black','Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif;font-weight:900;font-synthesis:none;font-size:32px;line-height:36px;color:#171320;text-align:center;letter-spacing:.2px">Your password was changed</h1>
          <p class="ink" style="margin:0 0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:25px;color:#171320;text-align:center"><b>{{username}}</b>, the password for your Roll Model account was changed on {{when}}. You&#8217;ve been signed out on your other devices.</p>
          <p class="ink" style="margin:0 0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:25px;color:#171320;text-align:center">If this was you, you&#8217;re all set.</p>
          <table role="presentation" class="warn" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 18px;background:#F4EEE3;border:1px solid #E6DCCB;border-radius:16px;border-collapse:separate">
            <tr><td style="padding:16px 18px 2px">
              <p class="ink" style="margin:0 0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:25px;color:#171320;text-align:center"><b>Wasn&#8217;t you?</b> Choose a new password right away, then write to us at {{support}}.</p>
              <table role="presentation" align="center" cellpadding="0" cellspacing="0" border="0" style="margin:8px auto 22px">
                <tr><td align="center" bgcolor="#E3122F" style="border-radius:999px;background:#E3122F;border-bottom:4px solid #99091F">
                  <a href="{{link}}" style="display:inline-block;padding:16px 34px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:17px;line-height:20px;font-weight:800;color:#FFFFFF;text-decoration:none;border-radius:999px">Reset my password</a>
                </td></tr>
              </table>
            </td></tr>
          </table>

        </td></tr>
      </table>
    </td></tr>
    <tr><td class="pad" style="padding:22px 30px 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:12px;line-height:18px;color:#6E6577;text-align:center">
      <p class="soft" style="margin:0 0 8px;color:#6E6577">You got this email because the password of the Roll Model account with this address was changed.</p>
      <p class="soft" style="margin:0 0 8px;color:#6E6577">Questions? Write to <a href="mailto:{{support}}" style="color:#6E6577;text-decoration:underline">{{support}}</a></p>
      <p class="soft" style="margin:0;color:#6E6577"><a href="{{site}}/privacy" style="color:#6E6577;text-decoration:underline">Privacy Policy</a> &nbsp;&middot;&nbsp; <a href="{{site}}/terms" style="color:#6E6577;text-decoration:underline">Terms of Service</a> &nbsp;&middot;&nbsp; <a href="{{site}}/support" style="color:#6E6577;text-decoration:underline">Support</a></p>
      <p class="soft" style="margin:10px 0 0;color:#6E6577">Roll Model &middot; A Marcelin Game &middot; &copy; {{year}}</p>
    </td></tr>
  </table>
</td></tr>
</table>
</body>
</html>
$h$,
  $t$Your password was changed

{{username}}, the password for your Roll Model account was changed on {{when}}. You've been signed out on your other devices.

If this was you, you're all set.

Wasn't you? Choose a new password right away:
{{link}}
then write to us at {{support}}.

--
You got this email because the password of the Roll Model account with this address was changed.
Questions? Write to {{support}}
Privacy Policy: {{site}}/privacy  Terms: {{site}}/terms  Support: {{site}}/support
Roll Model, A Marcelin Game
$t$)
  on conflict (kind) do update set subject = excluded.subject, html = excluded.html, text = excluded.text;
-- END TEMPLATES

-- ---------------------------------------------------------------- who may call what

revoke all on function public._mail_token(), public._esc(text), public._fill(text, jsonb, boolean), public._mail_cfg(), public._mail_key(), public._mail_on(),
  public._mail(text, uuid, text, jsonb), public._mail_find(text, text), public._mail_welcome(uuid, text), public._mail_reset(uuid), public._mail_changed()
  from public, anon, authenticated;
revoke all on function public.rm_email_get(), public.rm_email_set(text), public.rm_email_resend() from public, anon;
grant execute on function public.rm_email_get(), public.rm_email_set(text), public.rm_email_resend() to authenticated;
revoke all on function public.rm_email_verify(text), public.rm_reset_request(text), public.rm_reset_password(text, text) from public;
grant execute on function public.rm_email_verify(text), public.rm_reset_request(text), public.rm_reset_password(text, text) to anon, authenticated;
revoke all on function public.adm_player_email(uuid), public.adm_find_email(text), public.adm_email_reset(uuid) from public, anon;
grant execute on function public.adm_player_email(uuid), public.adm_find_email(text), public.adm_email_reset(uuid) to authenticated;
