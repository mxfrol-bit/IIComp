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
