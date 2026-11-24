-- Execute in your own Supabase project's SQL editor. No public/anonymous data access.
create table if not exists public.career_hub_backups (
  user_id uuid primary key references auth.users(id) on delete cascade,
  payload jsonb not null,
  updated_at timestamptz not null default now()
);
alter table public.career_hub_backups enable row level security;
revoke all on public.career_hub_backups from anon;
grant select, insert, update, delete on public.career_hub_backups to authenticated;
drop policy if exists "read own backup" on public.career_hub_backups;
drop policy if exists "insert own backup" on public.career_hub_backups;
drop policy if exists "update own backup" on public.career_hub_backups;
drop policy if exists "delete own backup" on public.career_hub_backups;
create policy "read own backup" on public.career_hub_backups for select to authenticated using ((select auth.uid()) = user_id);
create policy "insert own backup" on public.career_hub_backups for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "update own backup" on public.career_hub_backups for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "delete own backup" on public.career_hub_backups for delete to authenticated using ((select auth.uid()) = user_id);
