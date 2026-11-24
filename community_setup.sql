-- Run after account_setup.sql in your Supabase project's SQL Editor.
-- Public readers can only see approved, anonymous posts via restricted RPCs.
-- The moderator list is not accessible to visitors. No DMs or public profiles.
create table if not exists public.career_moderators (user_id uuid primary key references auth.users(id) on delete cascade);
create table if not exists public.career_community (
 id uuid primary key default gen_random_uuid(), author uuid references auth.users(id) on delete cascade not null,
 kind text not null check (kind in ('Recruitment experience','Employer review','Recruitment timeline','Apprentice question','General preparation tip','Apprentice answer','Vacancy report')),
 employer text not null check (char_length(employer) between 1 and 100), stage text not null default '' check (char_length(stage)<=100),
 body text not null check (char_length(body) between 1 and 600), wait_days int check(wait_days between 0 and 365), rating int check(rating between 1 and 5),
 target uuid references public.career_community(id) on delete set null,
 status text not null default 'pending' check(status in ('pending','approved','rejected')), created_at timestamptz not null default now()
);
create table if not exists public.career_content_reports (
 id uuid primary key default gen_random_uuid(), reporter uuid not null references auth.users(id) on delete cascade,
 post_id uuid not null references public.career_community(id) on delete cascade, created_at timestamptz not null default now(), unique(reporter,post_id)
);
alter table public.career_moderators enable row level security;
alter table public.career_community enable row level security;
alter table public.career_content_reports enable row level security;
revoke all on public.career_moderators,public.career_community,public.career_content_reports from public,anon,authenticated;
create or replace function public.career_is_moderator() returns boolean language sql stable security definer set search_path = '' as $$ select exists(select 1 from public.career_moderators where user_id=auth.uid()); $$;
create or replace function public.career_public_community() returns table(id uuid,kind text,employer text,stage text,body text,wait_days int,rating int) language sql stable security definer set search_path='' as $$
 select c.id,c.kind,c.employer,c.stage,c.body,c.wait_days,c.rating from public.career_community c where c.status='approved' and c.kind<>'Vacancy report' order by c.created_at desc limit 500;
$$;
create or replace function public.career_submit_community(p_kind text,p_employer text,p_stage text,p_body text,p_wait int,p_rating int,p_target uuid) returns uuid language plpgsql security definer set search_path='' as $$
declare new_id uuid; u uuid:=auth.uid(); begin
 if u is null then raise exception 'Sign-in required'; end if;
 if p_body is null or p_employer is null or trim(p_body)='' or trim(p_employer)='' then raise exception 'Empty contribution'; end if;
 if concat_ws(' ',p_employer,p_stage,p_body) ~* '(https?:|www\.|@|[0-9]{7,})' then raise exception 'Remove links and contact information'; end if;
 perform pg_advisory_xact_lock(hashtextextended(u::text,0));
 if (select count(*) from public.career_community where author=u and created_at>now()-interval '1 day')>=5 then raise exception 'Daily contribution limit'; end if;
 insert into public.career_community(author,kind,employer,stage,body,wait_days,rating,target) values(u,p_kind,trim(p_employer),coalesce(p_stage,''),trim(p_body),p_wait,p_rating,null) returning id into new_id;
 return new_id;
end; $$;
create or replace function public.career_moderation_queue() returns table(id uuid,kind text,employer text,stage text,body text,wait_days int,rating int) language plpgsql stable security definer set search_path='' as $$ begin
 if not public.career_is_moderator() then raise exception 'Moderator required'; end if;
 return query select c.id,c.kind,c.employer,c.stage,c.body,c.wait_days,c.rating from public.career_community c where c.status='pending' or (c.status='approved' and exists(select 1 from public.career_content_reports r where r.post_id=c.id)) order by c.created_at limit 500;
end; $$;
create or replace function public.career_moderate(p_id uuid,p_approve boolean) returns void language plpgsql security definer set search_path='' as $$ begin
 if not public.career_is_moderator() then raise exception 'Moderator required'; end if;
 update public.career_community set status=case when p_approve and kind<>'Vacancy report' then 'approved' else 'rejected' end where id=p_id;
 delete from public.career_content_reports where post_id=p_id;
end; $$;
create or replace function public.career_report_content(p_id uuid) returns void language plpgsql security definer set search_path='' as $$ declare u uuid:=auth.uid(); begin
 if u is null then raise exception 'Sign-in required'; end if;
 if not exists(select 1 from public.career_community where id=p_id and status='approved' and kind<>'Vacancy report') then raise exception 'Contribution not found'; end if;
 perform pg_advisory_xact_lock(hashtextextended(u::text,0));
 if (select count(*) from public.career_content_reports where reporter=u and created_at>now()-interval '1 day')>=10 then raise exception 'Daily report limit'; end if;
 insert into public.career_content_reports(reporter,post_id) values(u,p_id) on conflict do nothing;
end; $$;
revoke all on function public.career_is_moderator(),public.career_public_community(),public.career_submit_community(text,text,text,text,int,int,uuid),public.career_moderation_queue(),public.career_moderate(uuid,boolean),public.career_report_content(uuid) from public,anon,authenticated;
grant execute on function public.career_public_community() to anon,authenticated;
grant execute on function public.career_is_moderator(),public.career_submit_community(text,text,text,text,int,int,uuid),public.career_moderation_queue(),public.career_moderate(uuid,boolean),public.career_report_content(uuid) to authenticated;
-- Authorise yourself only after you create your account. Copy the UUID from Authentication > Users.
-- insert into public.career_moderators(user_id) values ('YOUR-USER-UUID');
-- Optional push subscriptions; private per-user and not included in published vacancies.
create table if not exists public.career_push_subscriptions (
 user_id uuid not null references auth.users(id) on delete cascade,
 endpoint text not null check(char_length(endpoint)<=2048), subscription jsonb not null check(octet_length(subscription::text)<=8192),
 created_at timestamptz default now(), primary key(user_id,endpoint)
);
alter table public.career_push_subscriptions enable row level security;
revoke all on public.career_push_subscriptions from anon,public;
grant select,insert,update,delete on public.career_push_subscriptions to authenticated;
drop policy if exists career_push_own on public.career_push_subscriptions;
create policy career_push_own on public.career_push_subscriptions for all to authenticated using (auth.uid()=user_id) with check (auth.uid()=user_id and endpoint ~ '^https://(fcm\.googleapis\.com|updates\.push\.services\.mozilla\.com|web\.push\.apple\.com|[a-z0-9-]+\.notify\.windows\.com)/' and subscription->>'endpoint'=endpoint);
grant select,delete on public.career_push_subscriptions to service_role;
-- Moderator-controlled public vacancy warnings. They never delete personal saved applications.
create table if not exists public.career_vacancy_flags (
 vacancy_key text primary key check(char_length(vacancy_key) between 1 and 500),
 updated_at timestamptz not null default now()
);
alter table public.career_vacancy_flags enable row level security;
revoke all on public.career_vacancy_flags from public,anon,authenticated;
create or replace function public.career_public_vacancy_flags() returns table(vacancy_key text) language sql stable security definer set search_path='' as $$ select f.vacancy_key from public.career_vacancy_flags f limit 5000; $$;
create or replace function public.career_flag_vacancy(p_key text,p_hidden boolean) returns void language plpgsql security definer set search_path='' as $$ begin
 if not public.career_is_moderator() then raise exception 'Moderator required'; end if;
 if p_hidden then insert into public.career_vacancy_flags(vacancy_key) values(p_key) on conflict(vacancy_key) do update set updated_at=now(); else delete from public.career_vacancy_flags where vacancy_key=p_key; end if;
end; $$;
revoke all on function public.career_public_vacancy_flags(),public.career_flag_vacancy(text,boolean) from public,anon,authenticated;
grant execute on function public.career_public_vacancy_flags() to anon,authenticated;
grant execute on function public.career_flag_vacancy(text,boolean) to authenticated;
