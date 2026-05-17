# AI Content Factory v4

Telegram bot for generating AI influencer content, product ads, product-aware images and Reels.

## Main change in v4

v3 only described the uploaded product in the text prompt. That means a dress/bottle/chocolate image was stored, but the image generator did not actually receive it as a visual reference.

v4 adds product-aware generation:

- **Clothes / dress** → `fal-ai/fashn/tryon/v1.5` virtual try-on. The uploaded garment image is actually applied to the AI model.
- **Bottle / chocolate / cosmetics / accessories** → `fal-ai/qwen-image-edit-plus-lora-gallery/integrate-product`. The uploaded product image is composited into the generated scene with perspective/light correction.
- If product-aware generation fails, the bot falls back to the old prompt-only mode and refunds only when the whole generation fails.

## Railway variables

```env
TELEGRAM_BOT_TOKEN=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
FAL_KEY=

FAL_MODEL=fal-ai/flux-lora
LORA_URL=https://huggingface.co/strangerzonehf/Flux-Super-Realism-LoRA/resolve/main/super-realism.safetensors
LORA_SCALE=0.68
CIVITAI_API_TOKEN=
ENABLE_SAFETY_CHECKER=true

FAL_VIDEO_MODEL=fal-ai/kling-video/v2.1/standard/image-to-video
VIDEO_COST_CREDITS=3
VIDEO_DEFAULT_DURATION=5
VIDEO_ALLOWED_DURATIONS=5,10,15

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-haiku-latest

PRODUCT_AWARE_MODE=true
TRYON_MODEL=fal-ai/fashn/tryon/v1.5
PRODUCT_INTEGRATION_MODEL=fal-ai/qwen-image-edit-plus-lora-gallery/integrate-product
PRODUCT_SHOT_MODEL=fal-ai/bria/product-shot
TRYON_EXTRA_CREDITS=2
PRODUCT_INTEGRATION_EXTRA_CREDITS=2

PRO_PRICE_STARS=399
PREMIUM_PRICE_STARS=1490
FREE_DAILY_CREDITS=3
PRO_DAILY_CREDITS=100

PROMO_REF_CODE=beta2000
PROMO_REF_BONUS_CREDITS=2000
```

## Supabase

Create public Storage bucket:

```text
generations
```

Run migrations:

```text
supabase/007_content_factory.sql
```

or safely run:

```text
supabase/seeyou_full_setup.sql
```

## Important for clothing

Virtual try-on works best when the base model image is full body / 3/4 body. For dresses, use fashion/product scenarios such as:

- Студийный full body
- Walking shot
- Luxury corridor
- Product reveal
- Hero ad

Cafe close-up scenes may show only the upper body, so the dress will not be fully visible.

## Deploy

```bash
unzip -o ai-content-factory-v4-product-aware.zip
cd IIComp-main

git add .
git commit -m "Add product-aware generation and virtual try-on"
git push
```
