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

    # Optional Civitai token (only if LoRA download becomes gated)
    civitai_api_token: str = ""

    # Tiers
    free_daily_credits: int = 3
    pro_daily_credits: int = 100

    # Stars pricing
    pro_price_stars: int = 399
    premium_price_stars: int = 1490

    # Image model & LoRA
    fal_model: str = "fal-ai/flux-lora"
    lora_url: str = "https://civitai.com/api/download/models/1026423"
    lora_scale: float = 0.9
    inference_steps: int = 40
    guidance_scale: float = 2.5


settings = Settings()
