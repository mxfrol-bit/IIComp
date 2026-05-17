# AI Companion Bot — MVP

Telegram bot that delivers an interactive story serial — episode by episode, with pre-generated photos of the heroine, paid early-unlocks via Telegram Stars, and a free per-character generation mode.

**Stack:** aiogram 3 · fal.ai (Flux + UltraRealistic LoRA) · Supabase · Railway

## Что внутри

Два продуктовых режима coexist:

1. **📺 Story (primary)** — interactive serial. One main heroine, episodes of 6–8 beats each, choices on later episodes, 24-hour cooldowns between episodes, paid early-unlock via Stars. All beat images are **pre-generated** by the operator before release — zero generation cost in runtime.
2. **✨ Free-form character (secondary)** — user creates their own character, picks scene presets, generates on demand. Burns generation credits per request. Daily limits + Pro/Premium tiers.

## User-facing features

- **18+ age gate** на /start + timestamp подтверждения в БД
- **Создание персонажа** (FSM: имя → возраст → волосы → телосложение → стиль)
- **Карточка персонажа** с аватаркой (первое фото) и инфо
- **Удаление персонажа** с подтверждением
- **46+ пресетов сцен**: обычные, романтика и soft 18+ без explicit
- **🔄 Рерол сцены** — кнопка под фото для перегенерации с новым seed
- **🎁 Что нового** — последние 5 фото юзера в одном экране
- **🤝 Реферальная программа** — t.me/<bot>?start=ref_<id>, +5 фото за каждого приглашённого
- **💎 Тарифы Pro/Premium** через Telegram Stars (399⭐ / 1490⭐); Pro открывает soft 18+, Premium работает без дневного лимита
- **📺 Story-режим** с эпизодами, битами, выборами, платными анлоками
- **❓ /help** с описанием всего функционала
- **ℹ️ /balance** — быстрый баланс одной командой
- **🛠 Admin-команды** для управления тестерами и тарифами

## Admin commands

Чтобы стать админом — выполни в Supabase SQL Editor:
```sql
update users set is_admin = true where tg_username = 'твой_username';
```

После этого доступны:
- `/admin grant <username> <credits>` — выдать кредиты вручную
- `/admin tier <username> <free|pro|premium>` — сменить тариф на 30 дней
- `/admin stats` — общая статистика по юзерам и генерациям
- `/admin makeadmin <username>` — назначить ещё одного админа

## Quick start

### Prereqs
- Python 3.11+
- [@BotFather](https://t.me/BotFather) bot token
- [fal.ai](https://fal.ai/dashboard/keys) API key (paid account; ~$0.025/image on `fal-ai/flux-lora`)
- [Supabase](https://supabase.com) project

### Setup
```bash
# 1. Database
# In Supabase SQL Editor, run in order:
#    supabase/schema.sql
#    supabase/002_story_engine.sql
#    supabase/003_features.sql
#    supabase/004_content_modes.sql
# Create Storage bucket "generations" — public read access

# 2. Env
cp .env.example .env  # fill in tokens

# 3. Install
pip install -r requirements.txt

# 4. Smoke-test fal.ai (generates one test image to disk)
python -m scripts.test_generation

# 5. Seed your first season
python -m scripts.seed_season content/season_anna_pilot.json

# 6. Pre-generate images for episode 1 (this hits fal.ai ~8 times)
python -m scripts.pregenerate_episode anna_s1 1

# 7. Run the bot locally
python -m app.main
```

### Deploy to Railway
```bash
railway login && railway init
railway variables set TELEGRAM_BOT_TOKEN=... FAL_KEY=... \
                     SUPABASE_URL=... SUPABASE_SERVICE_KEY=...
railway up
```
Long-polling, no webhooks. Single process.

## Content modes

The bot has three content levels:

- **safe** — обычные фото: кафе, прогулки, спорт, путешествия, дом.
- **romantic** — свидания, поцелуи, объятия, утренние сообщения. Доступно после 18+ gate.
- **soft18** — купальники, бельё, халат, утро под пледом. Только Pro/Premium. Встроенный prompt-filter блокирует explicit terms, несовершеннолетних, насилие и публичных персон.

The project intentionally does not include explicit-generation flows.

## Why fal.ai

- Latency 8–15s vs Replicate's 25–40s — same Flux-style workflow, different infra
- `fal-ai/flux-lora` accepts public LoRA URLs. Hugging Face is the safest default; Civitai/Civitai.red can be used with `CIVITAI_API_TOKEN`, but server-side downloads may depend on Civitai access rules
- Pricing per megapixel (~$0.025 for portrait_4_3); comparable to Replicate per-image
- `enable_safety_checker: True` is on by default — leave it on

If you ever want to swap providers again, only `app/image_client.py` needs changes — the rest of the code talks to it through `generate_image(prompt, seed, ...)`.

## Story production workflow

The story engine separates **content** (JSON) from **runtime** (bot). Operators write episodes as JSON, seed them, then pre-generate images. End users only consume.

### Writing an episode

Edit `content/season_anna_pilot.json` (or duplicate it for new seasons). Each episode has:

```json
{
  "number": 1,
  "title": "Cafe corner",
  "hook_text": "One-line teaser shown in the season list",
  "is_premium": false,
  "unlock_after_hours": 24,
  "beats_json": {
    "start_beat": "b1",
    "end_beats": ["b8"],
    "beats": {
      "b1": {
        "image_prompt_hint": "what the image should show — appended to character persona + base triggers",
        "image_url": "",
        "text": "narrative text the user reads",
        "next": "b2"
      }
    }
  }
}
```

For **branching beats** (later episodes), replace `next` with `choices`:
```json
"choices": [
  {"id": "approach", "label": "Подойти", "next": "b3a"},
  {"id": "wait", "label": "Подождать", "next": "b3b", "premium": true}
]
```
Premium choices are gated to Pro/Premium subscribers.

### Re-running pre-generation

If you want to regenerate one beat, blank out its `image_url` in the DB (or in the JSON and re-seed) and re-run `pregenerate_episode`. The script skips beats that already have a URL.

If you want to swap the heroine's look entirely — change `master_seed` in the season JSON, re-seed, blank all `image_url`s in DB, re-run pre-generation.

### Cost discipline

- Per beat: ~$0.025 on fal.ai
- Per 8-beat episode: ~$0.20 in pre-generation cost (one time, regardless of viewer count)
- Per viewer at runtime: $0 (everything is pre-generated)

This is the model that makes the serial economy work. Don't move beats to runtime generation unless you're sure the personalisation justifies the cost.

## Architecture

```
User ⇄ Telegram ⇄ aiogram (polling)
                    ↓
              Supabase (Postgres + Storage)
                    ↑
   ┌───── Operator runs scripts/pregenerate_episode.py
   ↓
fal.ai (Flux + UltraRealistic LoRA)
```

At runtime, the bot reads from Supabase only. No external generation calls during a viewer's session.

## File map

```
app/
  main.py              entry — aiogram dispatcher
  config.py            pydantic-settings
  db.py                Supabase client + helpers
  story.py             story engine (episodes, beats, unlocks)
  image_client.py      fal.ai generation (used by pre-gen script)
  moderation.py        prompt safety
  presets.py           free-form character scene presets
  persona.py           free-form character options
  keyboards.py         all inline keyboards
  states.py            FSM states for character creation
  handlers/
    start.py           /start, age gate, main menu
    story.py           seasons, episodes, beats, unlocks
    character.py       free-form character creation FSM
    generate.py        free-form on-demand generation
    billing.py         Telegram Stars
content/
  season_anna_pilot.json   pilot season template (edit me)
supabase/
  schema.sql               base schema (users, characters, generations)
  002_story_engine.sql     story tables (seasons, episodes, progress, events)
scripts/
  test_generation.py       smoke test for fal.ai
  seed_season.py           load JSON season into Supabase
  pregenerate_episode.py   generate beat images and store URLs
```

## Tariffs

Configurable in `.env`:
- **Free**: 3 free-form generations/day · 1 episode/day from active series · no premium choices
- **Pro** (399⭐/month): 100 free-form/day · all premium choices · early-unlock discount
- **Premium** (1490⭐/month): unlimited free-form · all content, all access

**Stars costs:**
- Pro/Premium subs charged on `billing:buy:*`
- Per-episode early-unlock: 50⭐ (configurable in `app/handlers/story.py`)

## Analytics

`story_events` table logs: `episode_started`, `beat_viewed`, `episode_completed`, `unlock_purchased`. Run funnel queries directly in Supabase. Until you have >100 DAU, you don't need PostHog/Amplitude.

Suggested first-week SQL:
```sql
-- Episode 1 completion rate
select
  count(distinct user_id) filter (where event = 'episode_started') as started,
  count(distinct user_id) filter (where event = 'episode_completed') as completed
from story_events
where episode_id = (select id from episodes where number = 1 limit 1);
```

## What's deliberately NOT in MVP

- **Face consistency across episodes (production-grade)**. Currently uses fixed `master_seed` — gives ~70% consistency. v2: pre-generate one canonical reference portrait, then use PuLID for all subsequent beats.
- **Branching engine UI**. The schema supports `choices` blocks but the pilot is linear. Branching kicks in from episode 2+.
- **Per-user personalization** (their name, their photo as "you" in scenes). v3 premium feature.
- **Web admin** to write episodes. Currently you edit JSON files. Build a Next.js admin only when episode count >5 and you're tired of editing JSON.

## Operational checklist before public launch

- [ ] Age gate confirmed (already in code) — verify `age_confirmed_at` is timestamped
- [ ] Terms of Service & Privacy policy linked from `/start`
- [ ] Brand/legal entity decided — DO NOT run on a personal account that's tied to other businesses
- [ ] fal.ai has billing set up (free credits run out fast during pre-generation)
- [ ] Supabase Storage bucket is public-read but write-restricted to service role
- [ ] At least 5 episodes pre-generated and tested before opening to public
- [ ] One backup heroine ready (in case the first doesn't resonate)


## Civitai / Civitai.red LoRA через Railway

Можно использовать Civitai/Civitai.red download URL без коммита токена в код.

Railway → Service → Variables:

```env
LORA_URL=https://civitai.red/api/download/models/YOUR_MODEL_VERSION_ID
CIVITAI_API_TOKEN=YOUR_TOKEN_FROM_CIVITAI_ACCOUNT
```

Код автоматически добавит `?token=...` к URL перед отправкой в fal.ai. Токен не логируется и не пишется в Supabase.

Важно: если fal.ai не сможет скачать файл с Civitai/Civitai.red даже с токеном, переключи только переменную `LORA_URL` на Hugging Face или Supabase Storage URL. Код менять не нужно.
