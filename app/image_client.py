"""Image generation client (fal.ai).

Provider-agnostic name — if we ever swap fal for something else, we change
this file only. Public API is `generate_image(prompt, seed, ...)`.
"""
import logging
import os
from typing import Optional

import fal_client

from app.config import settings

log = logging.getLogger(__name__)

# fal_client reads FAL_KEY from env
os.environ["FAL_KEY"] = settings.fal_key


def _lora_url() -> str:
    """Returns the LoRA URL from settings. URL must be a publicly accessible
    .safetensors file (Hugging Face works; raw Civitai download links don't —
    fal's servers can't fetch them)."""
    return settings.lora_url


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
