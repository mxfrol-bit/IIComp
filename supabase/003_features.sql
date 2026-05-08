-- ===========================================================================
-- Migration 003: referrals + UX features
-- Run AFTER 002_story_engine.sql
-- ===========================================================================

-- Add avatar field to characters (first generated photo)
alter table characters add column if not exists avatar_url text;

-- Referrals: who referred whom
create table if not exists referrals (
    id              bigserial primary key,
    referrer_id     bigint references users(id) on delete cascade,
    referred_id     bigint references users(id) on delete cascade unique,  -- one referral per user
    bonus_granted   boolean default false,
    created_at      timestamptz default now()
);

create index if not exists idx_referrals_referrer on referrals(referrer_id);

-- Admin flag for users
alter table users add column if not exists is_admin boolean default false;
