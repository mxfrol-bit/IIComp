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
    """Append CIVITAI_API_TOKEN to Civitai download URLs."""
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


def _lora_url() -> str | None:
    """Returns LoRA URL or None if not configured."""
    url = (settings.lora_url or "").strip()
    if not url:
        return None
    return _append_civitai_token(url)


async def generate_image(
    prompt: str,
    seed: int,
    aspect_ratio: str = "3:4",
    lora_scale: Optional[float] = None,
) -> str:
    """
    Run Flux + optional LoRA on fal.ai.
    Returns image URL.
    """
    image_size = {
        "3:4": "portrait_4_3",
        "9:16": "portrait_16_9",
        "1:1": "square_hd",
        "4:3": "landscape_4_3",
        "16:9": "landscape_16_9",
    }.get(aspect_ratio, "portrait_4_3")

    lora_url = _lora_url()
    scale = lora_scale if lora_scale is not None else settings.lora_scale

    arguments: dict = {
        "prompt": prompt,
        "image_size": image_size,
        "num_inference_steps": settings.inference_steps,
        "guidance_scale": settings.guidance_scale,
        "seed": seed,
        "num_images": 1,
        "enable_safety_checker": settings.enable_safety_checker,
        "output_format": "jpeg",
    }

    # Добавляем LoRA только если она указана
    if lora_url:
        arguments["loras"] = [{
            "path": lora_url,
            "scale": scale,
        }]
        log.info("Using LoRA: %s (scale=%.2f)", lora_url[:80], scale)
    else:
        log.info("Generating without LoRA")

    log.info("fal.ai run: model=%s seed=%s", settings.fal_model, seed)

    try:
        result = await fal_client.subscribe_async(
            settings.fal_model,
            arguments=arguments,
            with_logs=False,
        )
    except Exception as e:
        log.exception("fal.ai generation failed")
        raise RuntimeError(f"fal.ai error: {str(e)[:300]}") from e

    images = result.get("images") or []
    if not images:
        raise RuntimeError(f"fal.ai returned no images. Full response: {result}")

    return images[0]["url"]
