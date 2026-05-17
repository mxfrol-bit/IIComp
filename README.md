# AI Content Factory Pro v8

Telegram-бот + Web Admin + Mini App для создания AI-моделей, загрузки товаров и генерации рекламного контента для Instagram/Reels/Ads.

## Что нового в v8

- подключён **Grok/xAI как prompt engine**: бот может улучшать промпты для фото и видео перед отправкой в fal.ai;
- подключён **Wan 2.2 I2V** как основной видео-движок: `wan/v2.2-a14b/image-to-video/lora`;
- оставлен альтернативный видео-движок: `wan/v2.7/image-to-video`;
- добавлен анти-пластиковый realism layer: меньше кукольной кожи, generic stock лица и одинаковых девушек;
- identity pack расширен до 8 кадров через `IDENTITY_PACK_SIZE=8`;
- LORA_SCALE понижен до `0.45`, чтобы снизить одинаковость лиц;
- product-aware pipeline остался: try-on для одежды, product-shot/embed/holding для товаров;
- весь пользовательский интерфейс остаётся на русском.

## Деплой

```bash
unzip -o ai-content-factory-pro-v8-grok-wan.zip
cd IIComp-pro-v5

git add .
git commit -m "AI Content Factory Pro v8: Grok prompt engine and Wan I2V"
git push
```

Railway сам сделает redeploy.

## Railway Variables

Без кавычек.

```env
TELEGRAM_BOT_TOKEN=...
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
FAL_KEY=...

# xAI / Grok prompt engine
XAI_API_KEY=...
XAI_BASE_URL=https://api.x.ai/v1
PROMPT_PROVIDER=xai
PROMPT_MODEL=grok-4.20-non-reasoning
PROMPT_STRATEGY_MODEL=grok-4.20-reasoning

# Фото / реализм
FAL_MODEL=fal-ai/flux-lora
LORA_URL=https://huggingface.co/strangerzonehf/Flux-Super-Realism-LoRA/resolve/main/super-realism.safetensors
LORA_SCALE=0.45
ENABLE_SAFETY_CHECKER=true
PHOTO_QUALITY_MODE=pro
INFERENCE_STEPS=40
GUIDANCE_SCALE=2.3
IDENTITY_PACK_SIZE=8
ENABLE_IDENTITY_DNA=true
ENABLE_HERO_FACE=true

# Product-aware
PRODUCT_AWARE_MODE=true
PRODUCT_COMPOSITION_MODE=fast
PRODUCT_HOLDING_ENABLED=false
PRODUCT_EMBED_ENABLED=true
PRODUCT_PIPELINE_TIMEOUT_SEC=90
TRYON_MODEL=fal-ai/fashn/tryon/v1.5
PRODUCT_SHOT_MODEL=fal-ai/bria/product-shot
PRODUCT_EMBED_MODEL=bria/embed-product
PRODUCT_HOLDING_MODEL=fal-ai/image-apps-v2/product-holding
PRODUCT_INTEGRATION_MODEL=fal-ai/qwen-image-edit-plus-lora-gallery/integrate-product
TRYON_EXTRA_CREDITS=2
PRODUCT_INTEGRATION_EXTRA_CREDITS=2

# Видео / Wan I2V
VIDEO_PROVIDER=fal
FAL_VIDEO_MODEL=wan/v2.2-a14b/image-to-video/lora
VIDEO_MODEL_I2V=wan/v2.2-a14b/image-to-video/lora
VIDEO_MODEL_I2V_ALT=wan/v2.7/image-to-video
VIDEO_COST_CREDITS=3
VIDEO_DEFAULT_DURATION=5
VIDEO_DEFAULT_ASPECT=9:16
VIDEO_ALLOWED_DURATIONS=5,10,15

# Claude / content plans fallback
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-3-5-haiku-latest

# Web admin + Mini App
WEB_ENABLED=true
WEB_PUBLIC_URL=https://iicomp-production.up.railway.app
ADMIN_WEB_TOKEN=...

# Tariffs / promo
FREE_DAILY_CREDITS=50
PRO_DAILY_CREDITS=500
PRO_PRICE_STARS=399
PREMIUM_PRICE_STARS=1490
PROMO_REF_CODE=beta2000
PROMO_REF_BONUS_CREDITS=2000
```

## Важное по Wan 2.2

Wan 2.2 принимает `image_url`, `prompt`, `num_frames`, `frames_per_second`, `aspect_ratio`, `resolution` и другие параметры. В коде v8 эти параметры подставляются автоматически.

Для 5 секунд используется примерно 81 кадр, для 10 секунд — 161 кадр. Если выбрать 15 секунд, endpoint всё равно ограничен максимумом 161 кадр, поэтому для длинных роликов дальше нужно делать stitching/склейку нескольких клипов.

## Что тестировать

1. `/start`
2. создать новую AI-модель;
3. сделать identity pack;
4. загрузить товар;
5. сделать рекламный кадр;
6. сделать видео/Reels;
7. проверить, что в логах есть `prompt provider: xai` и `video model: wan/v2.2-a14b/image-to-video/lora`.

## Если Grok не подключён

Если `XAI_API_KEY` пустой или API недоступен, бот не падает. Он использует старые deterministic prompts.

## Если видео через Wan долго считается

Это нормально для видео. Для быстрых тестов можно временно вернуть Kling:

```env
VIDEO_MODEL_I2V=fal-ai/kling-video/v2.1/standard/image-to-video
FAL_VIDEO_MODEL=fal-ai/kling-video/v2.1/standard/image-to-video
```

Но для качества дальше тестируем Wan.
