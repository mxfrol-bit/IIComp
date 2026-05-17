# AI Content Factory Pro v5

Профессиональный Telegram-бот + Web Admin + Telegram Mini App для создания AI-моделей, загрузки товаров и генерации рекламного контента для Instagram/Reels/Ads.

## Что нового в v5

- новая «бомбическая» навигация: быстрый старт, модели, товары, реклама, Reels, контент-план;
- Web Admin на том же Railway-сервисе: `/admin?token=...`;
- Telegram Mini App: `/mini`;
- улучшенный quality pipeline: `PHOTO_QUALITY_MODE=pro/max`, pro prompt tail, усиленные рекламные промпты;
- product-aware генерация: одежда через virtual try-on, товары через product integration;
- кнопка `/admin web` выдаёт ссылку на админку и Mini App;
- быстрый путь: модель → товар → рекламный кадр.

## Деплой

```bash
unzip -o ai-content-factory-pro-v5.zip
cd IIComp-pro-v5

git add .
git commit -m "AI Content Factory Pro v5: admin web, mini app, quality upgrade"
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
LORA_SCALE=0.68
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
# strict mode preserves the uploaded product better than creative fusion
PRODUCT_COMPOSITION_MODE=strict
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
For bottles, toothpaste, cosmetics, chocolate and other physical goods the bot now uses strict product-preserving placement first:

1. `fal-ai/image-apps-v2/product-holding` — exact product in hands.
2. `bria/embed-product` — exact product embedded into a generated scene by coordinates.
3. `fal-ai/bria/product-shot` — product-first commercial fallback.

`PRODUCT_COMPOSITION_MODE=fusion` can be used for more creative images, but it may redraw labels or change packaging. For real advertising keep `strict`.
