from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Telegram
    telegram_bot_token: str

    # fal.ai
    fal_key: str

    # Supabase
    supabase_url: str
    supabase_service_key: str

    # Tiers
    free_daily_credits: int = 3
    pro_daily_credits: int = 100

    # Stars pricing
    pro_price_stars: int = 399
    premium_price_stars: int = 1490

    # Image model & LoRA — overridable via env (LORA_URL, FAL_MODEL, etc.)
    fal_model: str = "fal-ai/flux-lora"
    lora_url: str = "https://huggingface.co/strangerzonehf/Flux-Super-Realism-LoRA/resolve/main/super-realism.safetensors"
    # 0.55–0.70 usually gives more diverse faces. 0.9 can make all models too similar.
    lora_scale: float = 0.45

    # Optional Civitai/Civitai.red API token.
    # Keep it ONLY in Railway/Shell env; never commit it to GitHub.
    # If LORA_URL points to civitai.com or civitai.red, image_client.py appends ?token=... automatically.
    civitai_api_token: str | None = None
    inference_steps: int = 40
    guidance_scale: float = 2.5
    enable_safety_checker: bool = True


    # xAI / Grok prompt engine
    xai_api_key: str | None = None
    xai_base_url: str = "https://api.x.ai/v1"
    prompt_provider: str = "xai"  # anthropic | xai | fallback
    prompt_model: str = "grok-4.20-non-reasoning"
    prompt_strategy_model: str = "grok-4.20-reasoning"

    # Identity / realism controls
    identity_pack_size: int = 8
    enable_identity_dna: bool = True
    enable_hero_face: bool = True
    realism_negative_prompt: str = (
        "plastic skin, over-smoothed face, doll face, wax skin, generic stock woman, "
        "same default influencer face, uncanny valley, ai render look, fake glossy skin, "
        "overperfect beauty, deformed hands, unreadable product label, product redesign"
    )

    # Product-aware generation
    product_aware_mode: bool = True
    tryon_model: str = "fal-ai/fashn/tryon/v1.5"
    # Product composition. For non-clothes we default to strict BRIA placement,
    # because Qwen-style fusion can redraw/reinvent packaging.
    product_integration_model: str = "fal-ai/qwen-image-edit-plus-lora-gallery/integrate-product"
    product_shot_model: str = "fal-ai/bria/product-shot"
    product_embed_model: str = "bria/embed-product"
    product_holding_model: str = "fal-ai/image-apps-v2/product-holding"
    product_composition_mode: str = "fast"  # fast | strict | fusion | holding
    product_holding_enabled: bool = False
    product_embed_enabled: bool = True
    product_pipeline_timeout_sec: int = 90
    tryon_extra_credits: int = 2
    product_integration_extra_credits: int = 2

    # Companion chat (optional). If empty, bot uses built-in fallback replies.
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-haiku-latest"

    # Video generation via fal.ai image-to-video endpoint.
    video_provider: str = "fal"
    fal_video_model: str = "wan/v2.2-a14b/image-to-video/lora"
    video_model_i2v: str = "wan/v2.2-a14b/image-to-video/lora"
    video_model_i2v_alt: str = "wan/v2.7/image-to-video"
    video_cost_credits: int = 3
    video_default_duration: int = 5
    video_default_aspect: str = "9:16"
    video_allowed_durations: str = "5,10,15"

    # Test/promo referral link. Example: https://t.me/BOT?start=beta2000
    promo_ref_code: str = "beta2000"
    promo_ref_bonus_credits: int = 2000

    # Web admin / Telegram Mini App
    web_enabled: bool = True
    web_public_url: str | None = None  # e.g. https://your-app.up.railway.app
    admin_web_token: str | None = None  # set in Railway, never commit

    # Pro quality controls
    photo_quality_mode: str = "pro"  # fast | pro | max
    prompt_quality_tail: str = (
        "natural photorealistic premium commercial campaign, high-end editorial lighting, "
        "visible real skin texture, authentic human asymmetry, accurate hands, clean composition, realistic product scale, "
        "ready for Instagram ads, 4k detail, no artifacts"
    )
    hero_identity_refs: int = 4


settings = Settings()
