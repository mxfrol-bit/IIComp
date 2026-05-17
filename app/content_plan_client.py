from __future__ import annotations

import json
import logging
from typing import Optional

import httpx

from app.config import settings
from app.factory_catalog import PRODUCT_CATEGORIES

log = logging.getLogger(__name__)


def _fallback_plan(model: dict, product: Optional[dict]) -> dict:
    product_name = product.get("title") if product else "без товара"
    niche = model.get("niche") or "lifestyle"
    return {
        "summary": f"Контент-серия для AI-модели {model.get('name')} в нише {niche}, продукт: {product_name}.",
        "posts": [
            "Портрет модели + короткое позиционирование образа",
            "Lifestyle-кадр с нативным упоминанием продукта",
            "До/после или problem-solution под продукт",
            "Behind the scenes / UGC-кадр как будто снято на телефон",
            "Крупный product detail + лицо модели на фоне",
        ],
        "reels": [
            "5-сек product reveal: модель показывает товар в камеру",
            "10-сек UGC: проблема → продукт → улыбка",
            "Fashion/lifestyle walk с товаром в руке",
            "Beauty routine / unboxing / tasting в зависимости от категории",
            "Cinematic hero-shot для рекламы",
        ],
        "ads": [
            "Креатив 1: нативный отзыв от лица инфлюенсера",
            "Креатив 2: premium product placement",
            "Креатив 3: story/reels с быстрым хук-текстом",
        ],
        "hooks": [
            "Я не ожидала, что это станет моей новой привычкой",
            "Тот самый продукт, который выглядит дороже, чем стоит",
            "Сохрани, если любишь красивые вещи без лишнего шума",
            "Мой маленький ритуал на каждый день",
        ],
    }


async def generate_content_plan(model: dict, product: Optional[dict]) -> dict:
    if not settings.anthropic_api_key:
        return _fallback_plan(model, product)

    persona = model.get("persona_json") or {}
    product_payload = None
    if product:
        product_payload = {
            "title": product.get("title"),
            "category": PRODUCT_CATEGORIES.get(product.get("category") or "", product.get("category")),
            "description": product.get("description"),
        }

    system = (
        "Ты — продюсер Instagram/Reels контента и рекламных креативов для AI-инфлюенсеров. "
        "Верни строго JSON без Markdown. Структура: summary, posts[5], reels[5], ads[3], hooks[6]. "
        "Пиши по-русски, конкретно, для продающего визуального контента. Без adult/explicit."
    )
    user = {
        "model_name": model.get("name"),
        "niche": model.get("niche"),
        "persona": persona,
        "product": product_payload,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.anthropic_model,
                    "max_tokens": 1200,
                    "temperature": 0.7,
                    "system": system,
                    "messages": [{"role": "user", "content": json.dumps(user, ensure_ascii=False)}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text").strip()
            return json.loads(text)
    except Exception as e:
        log.warning("Content plan via Claude failed: %s", e)
        return _fallback_plan(model, product)


def render_plan(plan: dict) -> str:
    lines = ["🧾 Контент-план", ""]
    if plan.get("summary"):
        lines += [str(plan["summary"]), ""]
    for title, key in (("📸 Посты", "posts"), ("🎥 Reels", "reels"), ("📢 Реклама", "ads"), ("🪝 Хуки", "hooks")):
        items = plan.get(key) or []
        if items:
            lines.append(title)
            for i, item in enumerate(items, 1):
                lines.append(f"{i}. {item}")
            lines.append("")
    return "\n".join(lines).strip()
