-- (v428) The Time trial's one leaderboard: everyone's best on a canvas this week (the top 25), your friends marked, and where you
-- stand if you're further down. Reads the same runs the Friends board did (public.trial_scores, written by rm_trial).
create or replace function public.rm_global_board(p_stage text, p_week date default null)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare u uuid := public._me(); wk date := coalesce(p_week, (date_trunc('week', now() at time zone 'utc'))::date); mine jsonb; n int;
begin
  if p_stage !~ '^[a-z0-9_-]{1,24}$' then return jsonb_build_object('week', wk, 'rows', '[]'::jsonb, 'total', 0); end if;
  select count(*) into n from public.trial_scores t where t.week = wk and t.stage = p_stage;
  -- where you stand (a tie goes to whoever set it first)
  select jsonb_build_object('rank', r.rk, 'best', r.best) into mine from (
    select t.user_id, t.best, rank() over (order by t.best desc, t.updated_at) as rk
    from public.trial_scores t where t.week = wk and t.stage = p_stage) r where r.user_id = u;
  return jsonb_build_object('week', wk, 'total', n, 'me', mine, 'rows', coalesce((
    select jsonb_agg(jsonb_build_object('id', x.id, 'name', x.name, 'look', x.look, 'best', x.best, 'runs', x.runs, 'rank', x.rk,
      'me', x.id = u, 'friend', x.id <> u and public._friends(u, x.id)) order by x.rk)
    from (select p.id, p.name, p.look, t.best, t.runs, rank() over (order by t.best desc, t.updated_at) as rk
          from public.trial_scores t join public.profiles p on p.id = t.user_id
          where t.week = wk and t.stage = p_stage
          order by t.best desc, t.updated_at limit 25) x), '[]'::jsonb));
end $$;

revoke all on function public.rm_global_board(text, date) from public, anon;
grant execute on function public.rm_global_board(text, date) to authenticated;
