# IIComp / AI Content Factory v3

Telegram-бот для производства контента с AI-моделями: Instagram-фото, рекламные кадры с товаром, Reels/video из кадра, контент-планы.

Основная концепция больше не «чат-компаньон», а **профессиональный контент-завод для AI-моделей и товаров**.

## Что умеет v3

- 🧬 Создание AI-модели: имя, возраст, волосы, типаж, стиль, ниша.
- 👤 Hero face: после создания генерируется главный портрет модели.
- 🧬 Identity pack: 4 референса лица/фигуры для стабильного образа.
- 📦 Загрузка товара: 1–5 фото, категория, описание.
- 📸 Фото-контент: Instagram, fashion, beauty, product placement, food/drinks, travel/hotel.
- 📢 Реклама с товаром: товар в руке, на столе, product reveal, unboxing, hero ad.
- 🎥 Видео/Reels: выбор категории, сценария движения, формата 9:16/4:5/1:1 и длины 5/10/15 сек.
- 🧾 Контент-план через Claude или fallback без Claude.
- 💎 Telegram Stars: Pro/Premium.
- 🔒 Private-раздел оставлен как отдельный модуль, но не участвует в основном профессиональном флоу.

## Важное про постоянное лицо

В v3 заложен базовый слой постоянства:

1. `hero_image_url` — главный портрет модели;
2. `identity_pack_json` — набор референсов;
3. фиксированный `seed`;
4. единое описание лица в каждом промпте.

Это улучшает консистентность, но **идеальная стабильность лица появится после обучения personal LoRA** под конкретную AI-модель. Поле `custom_lora_url` уже есть в базе под следующий этап.

## Важное про товар

Сейчас товар сохраняется как фото + описание и участвует в промптах. Это работает для нативных рекламных образов, но точное сохранение реального лейбла/упаковки потребует следующего этапа: image-reference / image-to-image / inpaint pipeline. База уже хранит product photos для этого.

## Быстрый запуск

### 1. Supabase

В SQL Editor запусти:

```sql
supabase/007_content_factory.sql
```

Если база новая или непонятно, что уже накатано — можно безопасно запустить:

```sql
supabase/seeyou_full_setup.sql
```

Storage bucket:

```text
generations — public read
```

### 2. Railway Variables

```env
TELEGRAM_BOT_TOKEN=...
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
FAL_KEY=...

FAL_MODEL=fal-ai/flux-lora
LORA_URL=https://huggingface.co/strangerzonehf/Flux-Super-Realism-LoRA/resolve/main/super-realism.safetensors
LORA_SCALE=0.9
CIVITAI_API_TOKEN=
ENABLE_SAFETY_CHECKER=true

FAL_VIDEO_MODEL=fal-ai/kling-video/v2.1/standard/image-to-video
VIDEO_COST_CREDITS=3
VIDEO_DEFAULT_DURATION=5
VIDEO_ALLOWED_DURATIONS=5,10,15

ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-3-5-haiku-latest

PRO_PRICE_STARS=399
PREMIUM_PRICE_STARS=1490
FREE_DAILY_CREDITS=3
PRO_DAILY_CREDITS=100

PROMO_REF_CODE=beta2000
PROMO_REF_BONUS_CREDITS=2000
```

### 3. Деплой

```bash
git add .
git commit -m "Rebuild as AI Content Factory v3"
git push
```

Railway сам сделает redeploy.

## Проверка после деплоя

1. `/start`
2. `🧬 Создать AI-модель`
3. Дождаться hero portrait.
4. `📦 Мои товары` → `➕ Добавить товар` → загрузить фото товара.
5. Открыть модель → `📢 Реклама с товаром`.
6. Выбрать товар → категорию → сценарий.
7. Под готовым кадром нажать `🎥 Сделать Reels/видео`.
8. Выбрать сценарий видео, формат и длину.
9. Проверить `🧾 Контент-план`.

## Основные файлы

```text
app/handlers/factory.py       главный хендлер v3
app/factory_catalog.py        огромный каталог сценариев фото/видео
app/factory_keyboards.py      новая навигация
app/factory_prompts.py        сборка промптов для моделей/товаров/рекламы
app/content_plan_client.py    генерация контент-плана
app/image_client.py           fal.ai image generation
app/video_client.py           fal.ai image-to-video
supabase/007_content_factory.sql
```

## Команды

```text
/start
/menu
/help
/balance
/admin stats
/admin grant username 1000
/admin tier username premium
```

Чтобы снять лимиты себе:

```sql
update public.users
set is_admin = true,
    tier = 'premium',
    tier_until = now() + interval '365 days',
    credits = 999999
where tg_id = ТВОЙ_TELEGRAM_ID;
```
