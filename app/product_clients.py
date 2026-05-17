"""Product-aware generation clients for AI Content Factory.

Important production rule:
- Qwen/fusion endpoints are good for *creative blending*, but they may redraw a product.
- For real advertising/product catalog tasks we must preserve the uploaded product.

Therefore non-clothes product flow defaults to BRIA strict placement:
1) product_holding: exact product placed naturally in a person's hands
2) embed_product: exact product embedded into the already generated scene by coordinates
3) product_shot: exact product placed into a product-photo scene when model integration fails
"""
from __future__ import annotations

import logging
import os
from typing import Any

import fal_client

from app.config import settings

log = logging.getLogger(__name__)
os.environ["FAL_KEY"] = settings.fal_key


def _first_image_url(result: dict[str, Any]) -> str:
    images = result.get("images") or result.get("image") or []
    if isinstance(images, dict):
        url = images.get("url")
        if url:
            return url
    if isinstance(images, list) and images:
        first = images[0]
        if isinstance(first, dict) and first.get("url"):
            return first["url"]
        if isinstance(first, str):
            return first
    for key in ("output", "result", "url"):
        value = result.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and value.get("url"):
            return value["url"]
    raise RuntimeError(f"No image URL in fal result: {str(result)[:500]}")


async def generate_tryon(
    *,
    model_image_url: str,
    garment_image_url: str,
    category: str = "one-pieces",
    quality: str = "balanced",
) -> str:
    """Generate virtual try-on image with FASHN.

    This is only for clothes / dresses. It uses the uploaded garment reference.
    """
    arguments: dict[str, Any] = {
        "model_image": model_image_url,
        "garment_image": garment_image_url,
    }
    log.info("fal.ai try-on: model=%s category=%s", settings.tryon_model, category)
    try:
        result = await fal_client.subscribe_async(
            settings.tryon_model,
            arguments=arguments,
            with_logs=False,
        )
    except Exception as e:
        log.exception("fal.ai try-on failed")
        raise RuntimeError(f"try-on error: {str(e)[:300]}") from e
    return _first_image_url(result)


async def product_holding(
    *,
    person_image_url: str,
    product_image_url: str,
) -> str:
    """Place the exact uploaded product naturally in a person's hands.

    Good for bottles, cosmetics, food, boxes, toothpaste, chocolate, small objects.
    """
    arguments: dict[str, Any] = {
        "person_image_url": person_image_url,
        "product_image_url": product_image_url,
    }
    log.info("fal.ai product holding: model=%s", settings.product_holding_model)
    try:
        result = await fal_client.subscribe_async(
            settings.product_holding_model,
            arguments=arguments,
            with_logs=False,
        )
    except Exception as e:
        log.exception("fal.ai product holding failed")
        raise RuntimeError(f"product holding error: {str(e)[:300]}") from e
    return _first_image_url(result)


def _scene_size(aspect_ratio: str) -> tuple[int, int]:
    """Approximate output size used for BRIA embed coordinates.

    BRIA Embed Product needs coordinates in the scene image. Flux output size may vary,
    but these presets work well enough for our common Instagram formats.
    """
    if aspect_ratio == "9:16":
        return 768, 1365
    if aspect_ratio == "4:5":
        return 1024, 1280
    return 1024, 1024


def _embed_coordinates(aspect_ratio: str, scenario_key: str = "") -> dict[str, int]:
    w, h = _scene_size(aspect_ratio)

    # Product close-up / packshot: larger and centered.
    if scenario_key in {"pr_pack", "pr_hero", "be_perfume", "be_skin"}:
        width = int(w * 0.42)
        height = int(width * 0.55)
        x = int((w - width) / 2)
        y = int(h * 0.62)
        return {"x": x, "y": y, "width": width, "height": height}

    # Cafe/table/lifestyle: place exact product on lower third, as if on table.
    if scenario_key in {"ig_cafe", "ig_morning", "pr_table", "fo_breakfast", "fo_rest"}:
        width = int(w * 0.38)
        height = int(width * 0.55)
        x = int(w * 0.31)
        y = int(h * 0.72)
        return {"x": x, "y": y, "width": width, "height": height}

    # Vertical story/reels: product lower center.
    if aspect_ratio == "9:16":
        width = int(w * 0.48)
        height = int(width * 0.55)
        x = int((w - width) / 2)
        y = int(h * 0.70)
        return {"x": x, "y": y, "width": width, "height": height}

    width = int(w * 0.36)
    height = int(width * 0.55)
    x = int((w - width) / 2)
    y = int(h * 0.68)
    return {"x": x, "y": y, "width": width, "height": height}


async def embed_product_strict(
    *,
    scene_image_url: str,
    product_image_url: str,
    aspect_ratio: str = "4:5",
    scenario_key: str = "",
    seed: int | None = None,
) -> str:
    """Strict product embedding with coordinates.

    This preserves the uploaded product much better than prompt-only/fusion editing.
    """
    coords = _embed_coordinates(aspect_ratio, scenario_key)
    arguments: dict[str, Any] = {
        "image_source": scene_image_url,
        "products": [{
            "image_source": product_image_url,
            "coordinates": coords,
        }],
        "sync_mode": False,
    }
    if seed is not None:
        arguments["seed"] = seed

    log.info("fal.ai BRIA embed product: model=%s coords=%s", settings.product_embed_model, coords)
    try:
        result = await fal_client.subscribe_async(
            settings.product_embed_model,
            arguments=arguments,
            with_logs=False,
        )
    except Exception as e:
        log.exception("fal.ai product embed failed")
        raise RuntimeError(f"product embed error: {str(e)[:300]}") from e
    return _first_image_url(result)


async def integrate_product(
    *,
    scene_image_url: str,
    product_image_url: str,
    prompt: str,
) -> str:
    """Creative fusion product integration.

    Use only as optional/fallback because it can redraw packaging and change labels.
    """
    arguments: dict[str, Any] = {
        "image_urls": [scene_image_url, product_image_url],
        "prompt": prompt,
        "num_images": 1,
        "lora_scale": 1,
    }
    log.info("fal.ai product integrate/fusion: model=%s", settings.product_integration_model)
    try:
        result = await fal_client.subscribe_async(
            settings.product_integration_model,
            arguments=arguments,
            with_logs=False,
        )
    except Exception as e:
        log.exception("fal.ai product integration failed")
        raise RuntimeError(f"product integration error: {str(e)[:300]}") from e
    return _first_image_url(result)


async def product_lifestyle_shot(
    *,
    product_image_url: str,
    scene_description: str,
    placement: str = "bottom_center",
) -> str:
    """Exact product-first lifestyle shot via BRIA Product Shot.

    Fallback when model + product composition fails. This prioritizes preserving the real product.
    """
    arguments: dict[str, Any] = {
        "image_url": product_image_url,
        "scene_description": scene_description,
        "placement_type": "manual_placement",
        "manual_placement_selection": placement,
        "num_results": 1,
        "fast": True,
    }
    log.info("fal.ai Bria product shot: model=%s", settings.product_shot_model)
    try:
        result = await fal_client.subscribe_async(
            settings.product_shot_model,
            arguments=arguments,
            with_logs=False,
        )
    except Exception as e:
        log.exception("fal.ai product shot failed")
        raise RuntimeError(f"product shot error: {str(e)[:300]}") from e
    return _first_image_url(result)
