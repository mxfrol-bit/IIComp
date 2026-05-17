"""Image generation client (fal.ai).

Provider-agnostic name — if we ever swap fal for something else, we change
this file only. Public API is `generate_image(prompt, seed, ...)`.
"""
import logging
import os
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import fal_client

from app.config import settings

log = logging.getLogger(__name__)

# fal_client reads FAL_KEY from env
os.environ["FAL_KEY"] = settings.fal_key


def _append_civitai_token(url: str) -> str:
    """Append CIVITAI_API_TOKEN to Civitai/Civitai.red download URLs.

    The token is kept in Railway env only. We do not log it and do not store it
    in DB. If fal.ai still cannot fetch the file from Civitai, switch LORA_URL
    back to a Hugging Face/Supabase public URL.
    """
    token = settings.civitai_api_token
    if not token:
        return url

    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if "civitai." not in host:
        return url

    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() != "token"]
    query.append(("token", token))
    return urlunparse(parsed._replace(query=urlencode(query)))


def _lora_url() -> str:
    """Returns the LoRA URL for fal.ai.

    Supported production options:
    - Hugging Face direct .safetensors URL
    - Supabase Storage public .safetensors URL
    - Civitai/Civitai.red download URL + CIVITAI_API_TOKEN
    """
    return _append_civitai_token(settings.lora_url)


# Map our aspect ratios to fal.ai image_size enum
_ASPECT_TO_SIZE = {
    "3:4": "portrait_4_3",     # 768 x 1024
    "9:16": "portrait_16_9",   # 720 x 1280
    "1:1": "square_hd",        # 1024 x 1024
    "4:3": "landscape_4_3",
    "16:9": "landscape_16_9",
}


async def generate_image(
    prompt: str,
    seed: int,
    aspect_ratio: str = "3:4",
    lora_scale: Optional[float] = None,
) -> str:
    """
    Run Flux + LoRA generation on fal.ai. Returns image URL.
    Typical latency: 8–15 seconds (faster than Replicate).
    """
    image_size = _ASPECT_TO_SIZE.get(aspect_ratio, "portrait_4_3")

    arguments = {
        "prompt": prompt,
        "loras": [{
            "path": _lora_url(),
            "scale": lora_scale or settings.lora_scale,
        }],
        "image_size": image_size,
        "num_inference_steps": settings.inference_steps,
        "guidance_scale": settings.guidance_scale,
        "seed": seed,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "jpeg",
    }

    log.info("fal.ai run: model=%s prompt=%s seed=%s",
             settings.fal_model, prompt[:80], seed)

    result = await fal_client.subscribe_async(
        settings.fal_model,
        arguments=arguments,
        with_logs=False,
    )

    images = result.get("images") or []
    if not images:
        raise RuntimeError(f"fal.ai returned no images: {result}")

    return images[0]["url"]
