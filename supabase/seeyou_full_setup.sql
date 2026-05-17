-- ===========================================================================
-- AI Companion Bot — Supabase schema
-- Run in Supabase SQL Editor.
-- ===========================================================================

-- Users (mirror of Telegram users)
create table if not exists users (
    id              bigserial primary key,
    tg_id           bigint unique not null,
    tg_username     text,
    age_confirmed   boolean default false,
    tier            text default 'free' check (tier in ('free','pro','premium')),
    tier_until      timestamptz,
    credits         int default 3,
    credits_reset_at timestamptz default (now() + interval '1 day'),
    created_at      timestamptz default now()
);

create index if not exists idx_users_tg on users(tg_id);

-- Characters (each user can have multiple)
create table if not exists characters (
    id              bigserial primary key,
    user_id         bigint references users(id) on delete cascade,
    name            text not null,
    persona         jsonb not null,           -- age range, hair, body, style
    seed            bigint not null,          -- locked for consistency
    reference_url   text,                     -- first generated portrait
    created_at      timestamptz default now()
);

create index if not exists idx_characters_user on characters(user_id);

-- Generations
create table if not exists generations (
    id              bigserial primary key,
    user_id         bigint references users(id) on delete cascade,
    character_id    bigint references characters(id) on delete cascade,
    preset_key      text,
    prompt          text not null,
    replicate_id    text,
    image_url       text,
    status          text default 'pending' check (status in ('pending','done','failed','blocked')),
    error           text,
    created_at      timestamptz default now()
);

create index if not exists idx_generations_user on generations(user_id, created_at desc);

-- Credits ledger (audit trail for Stars purchases / generations / refunds)
create table if not exists credits_ledger (
    id              bigserial primary key,
    user_id         bigint references users(id) on delete cascade,
    delta           int not null,
    reason          text not null,           -- 'daily_grant', 'generation', 'purchase_pro', 'refund'
    meta            jsonb,
    created_at      timestamptz default now()
);

create index if not exists idx_ledger_user on credits_ledger(user_id, created_at desc);

-- Telegram Stars payments
create table if not exists payments (
    id                  bigserial primary key,
    user_id             bigint references users(id) on delete cascade,
    telegram_payment_id text unique,
    provider_payment_id text,
    amount_stars        int not null,
    tier                text not null,
    status              text default 'pending',
    created_at          timestamptz default now()
);
-- ===========================================================================
-- AI Companion Bot — Migration 002: story engine
-- Run AFTER schema.sql in Supabase SQL Editor.
-- ===========================================================================

-- Story characters (heroines of seasons — shared across all viewers)
create table if not exists story_characters (
    id              bigserial primary key,
    slug            text unique not null,
    name            text not null,
    bio             text,
    persona         jsonb not null,
    master_seed     bigint not null,
    reference_url   text,
    created_at      timestamptz default now()
);

-- Seasons
create table if not exists seasons (
    id              bigserial primary key,
    slug            text unique not null,
    title           text not null,
    description     text,
    cover_url       text,
    character_id    bigint references story_characters(id) on delete restrict,
    is_active       boolean default false,
    created_at      timestamptz default now()
);

-- Episodes
-- beats_json structure:
-- {
--   "start_beat": "b1",
--   "beats": {
--     "b1": {
--       "image_url": "https://...",     -- pre-generated, lives in Storage
--       "text": "Анна замечает...",
--       "next": "b2",                    -- linear pilot; later: "choices": [...]
--       "is_premium": false
--     },
--     ...
--   },
--   "end_beats": ["b8"]
-- }
create table if not exists episodes (
    id              bigserial primary key,
    season_id       bigint references seasons(id) on delete cascade,
    number          int not null,
    title           text not null,
    hook_text       text,
    is_premium      boolean default false,
    beats_json      jsonb not null,
    unlock_after_hours int default 24,
    created_at      timestamptz default now(),
    unique(season_id, number)
);

create index if not exists idx_episodes_season on episodes(season_id, number);

-- User progress through a season
create table if not exists user_progress (
    id              bigserial primary key,
    user_id         bigint references users(id) on delete cascade,
    season_id       bigint references seasons(id) on delete cascade,
    episode_id      bigint references episodes(id) on delete cascade,
    current_beat    text not null,
    completed_beats jsonb default '[]'::jsonb,
    choices_made    jsonb default '{}'::jsonb,
    started_at      timestamptz default now(),
    last_beat_at    timestamptz default now(),
    completed_at    timestamptz,
    unique(user_id, episode_id)
);

create index if not exists idx_progress_user on user_progress(user_id, season_id);

-- Episode unlock state per user (when next episode becomes available)
create table if not exists episode_unlocks (
    id              bigserial primary key,
    user_id         bigint references users(id) on delete cascade,
    episode_id      bigint references episodes(id) on delete cascade,
    unlocked_at     timestamptz default now(),
    unlock_reason   text,                  -- 'completed_previous', 'paid_skip', 'free_grant'
    unique(user_id, episode_id)
);

-- Analytics events (lightweight; for funnel)
create table if not exists story_events (
    id              bigserial primary key,
    user_id         bigint references users(id) on delete cascade,
    event           text not null,         -- 'episode_started', 'beat_viewed', 'episode_completed', 'unlock_purchased'
    episode_id      bigint references episodes(id) on delete set null,
    beat_key        text,
    meta            jsonb,
    created_at      timestamptz default now()
);

create index if not exists idx_events_user on story_events(user_id, created_at desc);
create index if not exists idx_events_event on story_events(event, created_at desc);
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
-- Migration 004: content modes and soft-18 controls

alter table users add column if not exists age_confirmed_at timestamptz;
alter table users add column if not exists content_mode text default 'safe'
    check (content_mode in ('safe', 'romantic', 'soft18'));

-- Backfill timestamp for already confirmed users.
update users
set age_confirmed_at = coalesce(age_confirmed_at, created_at, now())
where age_confirmed = true;


-- ===========================================================================
-- Migration 005: companion game layer
-- ===========================================================================
-- ===========================================================================
-- Migration 005: companion chat, relationship score, video generation
-- ===========================================================================

alter table public.users add column if not exists active_character_id bigint;
alter table public.users add column if not exists chat_enabled boolean default false;
alter table public.users add column if not exists relationship_score int default 0;
alter table public.users add column if not exists last_good_morning_at timestamptz;

-- FK is optional because older DBs may have partial migrations; add only if possible.
do $$
begin
  if exists (select 1 from information_schema.tables where table_schema='public' and table_name='characters') then
    if not exists (
      select 1 from information_schema.table_constraints
      where table_schema='public' and constraint_name='users_active_character_fk'
    ) then
      alter table public.users
        add constraint users_active_character_fk
        foreign key (active_character_id) references public.characters(id) on delete set null;
    end if;
  end if;
exception when duplicate_object then null;
end $$;

create table if not exists public.chat_messages (
    id              bigserial primary key,
    user_id         bigint references public.users(id) on delete cascade,
    character_id    bigint references public.characters(id) on delete cascade,
    role            text not null check (role in ('user','assistant','system')),
    content         text not null,
    event_type      text default 'chat',
    meta            jsonb default '{}'::jsonb,
    created_at      timestamptz default now()
);

create index if not exists idx_chat_messages_user_char on public.chat_messages(user_id, character_id, created_at desc);

alter table public.generations add column if not exists video_url text;
alter table public.generations add column if not exists video_status text default 'none';
alter table public.generations add column if not exists video_prompt text;

create index if not exists idx_generations_video on public.generations(user_id, video_status, created_at desc);
