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
    lora_scale: float = 0.9

    # Optional Civitai/Civitai.red API token.
    # Keep it ONLY in Railway/Shell env; never commit it to GitHub.
    # If LORA_URL points to civitai.com or civitai.red, image_client.py appends ?token=... automatically.
    civitai_api_token: str | None = None
    inference_steps: int = 40
    guidance_scale: float = 2.5
    enable_safety_checker: bool = True

    # Companion chat (optional). If empty, bot uses built-in fallback replies.
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-haiku-latest"

    # Video generation via fal.ai image-to-video endpoint.
    fal_video_model: str = "fal-ai/kling-video/v2.1/standard/image-to-video"
    video_cost_credits: int = 3
    video_default_duration: int = 5
    video_allowed_durations: str = "5,10,15"

    # Test/promo referral link. Example: https://t.me/BOT?start=beta2000
    promo_ref_code: str = "beta2000"
    promo_ref_bonus_credits: int = 2000


settings = Settings()
