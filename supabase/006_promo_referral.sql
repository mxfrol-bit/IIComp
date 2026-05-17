-- Migration 006: one-time promo/test referral links

create table if not exists public.promo_claims (
    id          bigserial primary key,
    user_id     bigint references public.users(id) on delete cascade,
    code        text not null,
    credits     int not null default 0,
    created_at  timestamptz default now(),
    unique(user_id, code)
);

create index if not exists idx_promo_claims_user on public.promo_claims(user_id, created_at desc);
create index if not exists idx_promo_claims_code on public.promo_claims(code, created_at desc);
