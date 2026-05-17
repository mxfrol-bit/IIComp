# AI Content Factory Pro v7

Профессиональный Telegram-бот + Web Admin + Telegram Mini App для создания AI-моделей, загрузки товаров и генерации рекламного контента для Instagram/Reels/Ads.

## Что нового в v7

- весь пользовательский интерфейс и сценарии переведены на русский;
- расширены каталоги: больше фото-сцен, видео-сцен, ниш, типажей и категорий товаров;
- у каждой AI-модели теперь создаётся уникальная «ДНК лица» — лицо меньше повторяется между моделями;
- LoRA scale по умолчанию снижен до 0.62, чтобы модели не становились одинаковыми;
- product pipeline стал стабильнее: `fast` по умолчанию, `strict/holding/fusion` включаются отдельно;
- добавлен таймаут product-aware шагов, чтобы бот не висел на тяжёлых endpoints;
- качество усилено под продающий Instagram / Reels / Ads контент.

## Деплой

```bash
unzip -o ai-content-factory-pro-v7-ru-accuracy.zip
cd IIComp-pro-v5

git add .
git commit -m "AI Content Factory Pro v7: RU scenes, identity DNA and stable product pipeline"
git push
```

Railway сам сделает redeploy.

## Railway Variables

Минимум:

```env
TELEGRAM_BOT_TOKEN=...
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
FAL_KEY=...
ANTHROPIC_API_KEY=...
```

Фото/LoRA:

```env
FAL_MODEL=fal-ai/flux-lora
LORA_URL=https://huggingface.co/strangerzonehf/Flux-Super-Realism-LoRA/resolve/main/super-realism.safetensors
LORA_SCALE=0.62
ENABLE_SAFETY_CHECKER=true
```

Качество:

```env
PHOTO_QUALITY_MODE=pro
INFERENCE_STEPS=45
GUIDANCE_SCALE=2.5
```

Для максимального качества тестируй:

```env
PHOTO_QUALITY_MODE=max
INFERENCE_STEPS=55
```

Product-aware:

```env
PRODUCT_AWARE_MODE=true
TRYON_MODEL=fal-ai/fashn/tryon/v1.5
# fast — быстрее и стабильнее для MVP; strict — точнее, но дольше; holding — товар в руке; fusion — красиво, но может менять упаковку
PRODUCT_COMPOSITION_MODE=fast
PRODUCT_HOLDING_ENABLED=false
PRODUCT_EMBED_ENABLED=true
PRODUCT_PIPELINE_TIMEOUT_SEC=90
PRODUCT_EMBED_MODEL=bria/embed-product
PRODUCT_HOLDING_MODEL=fal-ai/image-apps-v2/product-holding
PRODUCT_INTEGRATION_MODEL=fal-ai/qwen-image-edit-plus-lora-gallery/integrate-product
PRODUCT_SHOT_MODEL=fal-ai/bria/product-shot
TRYON_EXTRA_CREDITS=2
PRODUCT_INTEGRATION_EXTRA_CREDITS=2
```

Видео:

```env
FAL_VIDEO_MODEL=fal-ai/kling-video/v2.1/standard/image-to-video
VIDEO_COST_CREDITS=3
VIDEO_DEFAULT_DURATION=5
VIDEO_ALLOWED_DURATIONS=5,10,15
```

Web Admin / Mini App:

```env
WEB_ENABLED=true
WEB_PUBLIC_URL=https://your-railway-domain.up.railway.app
ADMIN_WEB_TOKEN=long_random_secret
```

После деплоя в Telegram:

```text
/admin web
```

Бот пришлёт ссылку на админку и Mini App.

## Supabase

Нужны таблицы из `supabase/seeyou_full_setup.sql` или миграция `007_content_factory.sql` поверх старой базы.

Storage bucket:

```text
Name: generations
Public: ON
File size: 100 MB
```

## Как тестировать

1. `/start`
2. `🚀 Быстрый старт`
3. создать AI-модель
4. загрузить товар
5. сделать рекламный кадр
6. сделать Reels/видео
7. `/admin web` — открыть web admin
8. Mini App — открыть через кнопку в боте или `/mini` на Railway URL

## Коммерческое качество

Для одежды:
- загружай фото платья/одежды на чистом фоне;
- выбирай fashion full body / walking / studio сценарии;
- избегай кафе/крупных портретов, если нужно показать платье целиком.

Для товаров:
- чистое фото товара спереди;
- описание цвета, упаковки, материала;
- выбирай product placement / hero ad / UGC сценарии.

Для стабильного лица:
- после создания модели нажми `🧬 Улучшить постоянство лица`;
- в будущем лучший путь — personal LoRA на каждую модель.


## Product accuracy notes

For clothes/dresses the bot uses virtual try-on.
For bottles, toothpaste, cosmetics, chocolate and other physical goods the bot now supports multiple product-preserving modes:

- `PRODUCT_COMPOSITION_MODE=fast` — быстрый product-shot, лучший старт для MVP.
- `PRODUCT_COMPOSITION_MODE=strict` — вставка товара в сцену через координаты.
- `PRODUCT_COMPOSITION_MODE=holding` + `PRODUCT_HOLDING_ENABLED=true` — товар в руках модели.
- `PRODUCT_COMPOSITION_MODE=fusion` — креативная интеграция, но может менять упаковку.

Для продажи сначала держи `fast`, для точных тестов упаковки — `strict`, для товара в руках — `holding`.
