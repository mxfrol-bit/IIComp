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
