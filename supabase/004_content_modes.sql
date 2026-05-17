-- Migration 004: content modes and soft-18 controls

alter table users add column if not exists age_confirmed_at timestamptz;
alter table users add column if not exists content_mode text default 'safe'
    check (content_mode in ('safe', 'romantic', 'soft18'));

-- Backfill timestamp for already confirmed users.
update users
set age_confirmed_at = coalesce(age_confirmed_at, created_at, now())
where age_confirmed = true;
