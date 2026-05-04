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
