"""Prompt engine for AI Content Factory.

v8 adds xAI/Grok as an optional prompt brain. It improves prompts for:
- more natural, less plastic faces;
- product-aware advertising composition;
- Wan I2V motion prompts;
- captions/CTA snippets.

The module is fail-safe: if Grok is not configured or returns invalid JSON, we keep
using the original deterministic prompt builders.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

import httpx

from app.config import settings
from app.factory_catalog import PRODUCT_CATEGORIES

log = logging.getLogger(__name__)


BAD_WORDS = (
    "plastic skin", "doll face", "wax skin", "generic stock woman", "ai render",
    "overperfect", "fake label", "wrong packaging", "product redesign",
)


def _compact(obj: Any, max_len: int = 6000) -> str:
    try:
        text = json.dumps(obj, ensure_ascii=False, default=str)
    except Exception:
        text = str(obj)
    return text[:max_len]


def _extract_json(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {}
    # remove markdown fences if any
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I).strip()
    text = re.sub(r"\s*```$", "", text).strip()
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except Exception:
        pass
    # best-effort extraction
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return {}
    try:
        data = json.loads(m.group(0))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _product_payload(product: Optional[dict]) -> Optional[dict]:
    if not product:
        return None
    return {
        "title": product.get("title"),
        "category": PRODUCT_CATEGORIES.get(product.get("category") or "", product.get("category") or "product"),
        "description": product.get("description"),
        "has_uploaded_reference_image": bool(product.get("primary_image_url")),
    }


def _persona_payload(model: dict) -> dict[str, Any]:
    persona = model.get("persona_json") or model.get("persona") or {}
    if not isinstance(persona, dict):
        persona = {}
    return {
        "name": model.get("name"),
        "niche": model.get("niche"),
        "seed": model.get("seed"),
        "persona": persona,
        "hero_image_exists": bool(model.get("hero_image_url")),
        "identity_pack_count": len(model.get("identity_pack_json") or []) if isinstance(model.get("identity_pack_json"), list) else 0,
    }


async def _xai_json(system: str, user_payload: dict[str, Any], *, strategy: bool = False, timeout: int = 35) -> dict[str, Any]:
    if not settings.xai_api_key:
        return {}
    model = settings.prompt_strategy_model if strategy else settings.prompt_model
    url = f"{settings.xai_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.xai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "temperature": 0.55 if strategy else 0.35,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": _compact(user_payload)},
        ],
        "response_format": {"type": "json_object"},
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return _extract_json(content)
    except Exception as e:
        log.warning("xAI prompt engine failed, fallback to deterministic prompt: %s", str(e)[:300])
        return {}


def _clean_prompt(text: str) -> str:
    text = " ".join((text or "").split())
    return text[:5000]


async def improve_photo_prompt(
    *,
    model: dict,
    product: Optional[dict],
    scenario: dict,
    draft_prompt: str,
    purpose: str = "photo",
) -> str:
    """Use Grok/xAI to rewrite a production prompt, fallback to draft."""
    if (settings.prompt_provider or "").lower() != "xai" or not settings.xai_api_key:
        return draft_prompt

    system = (
        "You are a senior AI advertising prompt engineer for photorealistic Instagram/Reels/Ads content. "
        "Return only valid JSON. Your job: rewrite the provided draft prompt into a production-ready English prompt. "
        "Priorities: natural realistic face, non-plastic skin, unique identity per model, commercial lighting, product accuracy, "
        "real uploaded product must not be redesigned, no fake labels, no unreadable brand text, no explicit content. "
        "Do not mention tools, AI, prompts, Grok, fal, Midjourney, or model names in the result. "
        "JSON schema: {\"photo_prompt_en\": string, \"negative_prompt\": string, \"caption_ru\": string, \"cta_ru\": string}."
    )
    payload = {
        "purpose": purpose,
        "draft_prompt": draft_prompt,
        "model": _persona_payload(model),
        "product": _product_payload(product),
        "scenario": scenario,
        "anti_plastic_requirements": settings.realism_negative_prompt,
    }
    data = await _xai_json(system, payload, strategy=False)
    prompt = _clean_prompt(data.get("photo_prompt_en") or "")
    negative = _clean_prompt(data.get("negative_prompt") or settings.realism_negative_prompt)
    if not prompt:
        return draft_prompt
    return f"{prompt}. Negative requirements: {negative}."


async def improve_video_prompt(
    *,
    content_gen: dict,
    product: Optional[dict],
    scenario: dict,
    draft_prompt: str,
    duration: int,
    aspect_ratio: str,
) -> str:
    """Use Grok/xAI to write a Wan/Kling motion prompt, fallback to draft."""
    if (settings.prompt_provider or "").lower() != "xai" or not settings.xai_api_key:
        return draft_prompt

    system = (
        "You are a director creating concise prompts for image-to-video advertising models such as Wan/Kling. "
        "Return only JSON. Write a motion prompt that preserves the starting image identity and product exactly. "
        "The video must be realistic, smooth, commercial, no face morphing, no product deformation, no fake label changes. "
        "JSON schema: {\"video_motion_prompt_en\": string, \"negative_prompt\": string}."
    )
    payload = {
        "draft_prompt": draft_prompt,
        "scenario": scenario,
        "product": _product_payload(product),
        "duration_sec": duration,
        "aspect_ratio": aspect_ratio,
        "content_generation": {
            "id": content_gen.get("id"),
            "scenario_key": content_gen.get("scenario_key"),
            "format": content_gen.get("format"),
        },
    }
    data = await _xai_json(system, payload, strategy=False)
    prompt = _clean_prompt(data.get("video_motion_prompt_en") or "")
    negative = _clean_prompt(data.get("negative_prompt") or settings.realism_negative_prompt)
    if not prompt:
        return draft_prompt
    return f"{prompt}. Negative requirements: {negative}."


async def build_strategy_card(*, model: dict, product: Optional[dict], task: str) -> dict[str, Any]:
    """Optional Grok strategy helper for future admin/Mini App use."""
    if (settings.prompt_provider or "").lower() != "xai" or not settings.xai_api_key:
        return {}
    system = (
        "You are a creative director for an AI content factory. Return JSON with creative_strategy, risks, prompt_notes, "
        "recommended_scenarios[5], reels_hooks[5]. Write in Russian for the operator."
    )
    return await _xai_json(system, {"task": task, "model": _persona_payload(model), "product": _product_payload(product)}, strategy=True)
