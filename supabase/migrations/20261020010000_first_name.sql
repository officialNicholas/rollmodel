-- v391: an account asks for a first name only. The last name is no longer asked for or kept: the ones kept so far are cleared,
-- and none is saved from now on. An earlier version of the game that still sends one keeps working (it's taken and not kept).
-- Safe to run again.

alter table public.accounts alter column last_name drop not null;
-- and the last names kept so far go too (the privacy policy from v391 says an account keeps a first name only)
update public.accounts set last_name = null where last_name is not null;

-- your account details, saved once your player has been made into a real account (an email and password set on it).
-- Answers { ok: true } or { ok: false, why: not_signed_up | first | birthday | age | terms }. p_last is only there for older
-- versions of the game, which still send one: it isn't kept.
create or replace function public.rm_account_save(p_first text, p_last text, p_birthday date, p_terms text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare u uuid := public._me(); anon boolean;
  f text := btrim(regexp_replace(coalesce(p_first, ''), '\s+', ' ', 'g'));
begin
  select is_anonymous into anon from auth.users where id = u;
  if anon is distinct from false then return jsonb_build_object('ok', false, 'why', 'not_signed_up'); end if;
  if f !~ '^[[:alpha:]][[:alpha:] .''-]{0,39}$' then return jsonb_build_object('ok', false, 'why', 'first'); end if;
  if p_birthday is null or p_birthday < date '1900-01-01' or p_birthday > current_date then return jsonb_build_object('ok', false, 'why', 'birthday'); end if;
  if p_birthday > (current_date - interval '13 years')::date then return jsonb_build_object('ok', false, 'why', 'age'); end if;
  if coalesce(p_terms, '') !~ '^[a-z0-9.-]{1,32}$' then return jsonb_build_object('ok', false, 'why', 'terms'); end if;
  insert into public.accounts (id, first_name, last_name, birthday, terms) values (u, f, null, p_birthday, p_terms)
    on conflict (id) do update set first_name = excluded.first_name, last_name = excluded.last_name, birthday = excluded.birthday,
      terms = excluded.terms, agreed_at = case when public.accounts.terms = excluded.terms then public.accounts.agreed_at else now() end, updated_at = now();
  return jsonb_build_object('ok', true);
end $$;
