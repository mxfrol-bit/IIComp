-- ============================================================
-- Migration 007: AI Content Factory v3 full schema
-- Safe to run multiple times on an old seeyou project.
-- ============================================================

-- Users compatibility / required fields
create table if not exists public.users (
    id bigserial primary key,
    tg_id bigint unique,
    tg_username text,
    credits int default 3,
    credits_reset_at timestamptz default (now() + interval '1 day'),
    tier text default 'free',
    tier_until timestamptz,
    is_admin boolean default false,
    created_at timestamptz default now()
);

alter table public.users add column if not exists tg_id bigint;
alter table public.users add column if not exists tg_username text;
alter table public.users add column if not exists credits int default 3;
alter table public.users add column if not exists credits_reset_at timestamptz default (now() + interval '1 day');
alter table public.users add column if not exists tier text default 'free';
alter table public.users add column if not exists tier_until timestamptz;
alter table public.users add column if not exists is_admin boolean default false;
alter table public.users add column if not exists age_confirmed boolean default false;
alter table public.users add column if not exists age_confirmed_at timestamptz;
alter table public.users add column if not exists content_mode text default 'safe';
alter table public.users add column if not exists active_character_id bigint;
alter table public.users add column if not exists chat_enabled boolean default false;
alter table public.users add column if not exists relationship_score int default 0;

do $$
declare
  has_telegram_id boolean;
  has_username boolean;
  has_first_name boolean;
  has_updated_at boolean;
begin
  select exists(select 1 from information_schema.columns where table_schema='public' and table_name='users' and column_name='telegram_id') into has_telegram_id;
  select exists(select 1 from information_schema.columns where table_schema='public' and table_name='users' and column_name='username') into has_username;
  select exists(select 1 from information_schema.columns where table_schema='public' and table_name='users' and column_name='first_name') into has_first_name;
  select exists(select 1 from information_schema.columns where table_schema='public' and table_name='users' and column_name='updated_at') into has_updated_at;

  if has_telegram_id then
    execute 'alter table public.users alter column telegram_id drop not null';
    execute 'update public.users set tg_id = telegram_id where tg_id is null and telegram_id is not null';
  end if;
  if has_username then
    execute 'alter table public.users alter column username drop not null';
    execute 'update public.users set tg_username = username where tg_username is null and username is not null';
  end if;
  if has_first_name then
    execute 'alter table public.users alter column first_name drop not null';
  end if;
  if has_updated_at then
    execute 'alter table public.users alter column updated_at set default now()';
  end if;
end $$;

create index if not exists idx_users_tg on public.users(tg_id);

-- Ledger / payments / referrals used by billing and promo links
create table if not exists public.credits_ledger (
    id bigserial primary key,
    user_id bigint references public.users(id) on delete cascade,
    delta int not null,
    reason text not null,
    meta jsonb,
    created_at timestamptz default now()
);
create index if not exists idx_ledger_user on public.credits_ledger(user_id, created_at desc);

create table if not exists public.payments (
    id bigserial primary key,
    user_id bigint references public.users(id) on delete cascade,
    telegram_payment_id text unique,
    provider_payment_id text,
    amount_stars int not null,
    tier text not null,
    status text default 'pending',
    created_at timestamptz default now()
);

create table if not exists public.referrals (
    id bigserial primary key,
    referrer_id bigint references public.users(id) on delete cascade,
    referred_id bigint references public.users(id) on delete cascade unique,
    bonus_granted boolean default false,
    created_at timestamptz default now()
);
create index if not exists idx_referrals_referrer on public.referrals(referrer_id);

create table if not exists public.promo_claims (
    id bigserial primary key,
    user_id bigint references public.users(id) on delete cascade,
    code text not null,
    credits int not null default 0,
    created_at timestamptz default now(),
    unique(user_id, code)
);
create index if not exists idx_promo_claims_user on public.promo_claims(user_id, created_at desc);
create index if not exists idx_promo_claims_code on public.promo_claims(code, created_at desc);

-- Legacy compatibility tables so old admin stats do not fail
create table if not exists public.characters (
    id bigserial primary key,
    user_id bigint references public.users(id) on delete cascade,
    name text not null default 'legacy',
    persona jsonb not null default '{}'::jsonb,
    seed bigint not null default 1,
    reference_url text,
    avatar_url text,
    created_at timestamptz default now()
);

create table if not exists public.generations (
    id bigserial primary key,
    user_id bigint references public.users(id) on delete cascade,
    character_id bigint references public.characters(id) on delete cascade,
    preset_key text,
    prompt text,
    replicate_id text,
    image_url text,
    video_url text,
    video_status text,
    video_prompt text,
    status text default 'pending',
    error text,
    created_at timestamptz default now()
);

-- New AI Content Factory entities
create table if not exists public.ai_models (
    id bigserial primary key,
    user_id bigint references public.users(id) on delete cascade,
    name text not null,
    age_range text,
    persona_json jsonb not null default '{}'::jsonb,
    niche text,
    hero_image_url text,
    identity_pack_json jsonb not null default '[]'::jsonb,
    seed bigint not null,
    custom_lora_url text,
    created_at timestamptz default now()
);
create index if not exists idx_ai_models_user on public.ai_models(user_id, created_at desc);

create table if not exists public.products (
    id bigserial primary key,
    user_id bigint references public.users(id) on delete cascade,
    title text not null,
    category text,
    description text,
    primary_image_url text,
    extra_images_json jsonb not null default '[]'::jsonb,
    extracted_object_url text,
    brand_style_json jsonb not null default '{}'::jsonb,
    created_at timestamptz default now()
);
create index if not exists idx_products_user on public.products(user_id, created_at desc);

create table if not exists public.content_generations (
    id bigserial primary key,
    user_id bigint references public.users(id) on delete cascade,
    model_id bigint references public.ai_models(id) on delete set null,
    product_id bigint references public.products(id) on delete set null,
    content_type text not null,
    scenario_key text,
    format text,
    duration_sec int,
    prompt text,
    image_url text,
    video_url text,
    video_prompt text,
    status text default 'pending',
    video_status text,
    error text,
    meta_json jsonb not null default '{}'::jsonb,
    created_at timestamptz default now()
);
create index if not exists idx_content_generations_user on public.content_generations(user_id, created_at desc);
create index if not exists idx_content_generations_model on public.content_generations(model_id, created_at desc);
create index if not exists idx_content_generations_product on public.content_generations(product_id, created_at desc);

create table if not exists public.content_plans (
    id bigserial primary key,
    user_id bigint references public.users(id) on delete cascade,
    model_id bigint references public.ai_models(id) on delete set null,
    product_id bigint references public.products(id) on delete set null,
    niche text,
    result_json jsonb not null default '{}'::jsonb,
    created_at timestamptz default now()
);
create index if not exists idx_content_plans_user on public.content_plans(user_id, created_at desc);
