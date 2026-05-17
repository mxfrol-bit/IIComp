from __future__ import annotations

import json
import logging
from typing import Optional

import httpx

from app.config import settings
from app.factory_catalog import PRODUCT_CATEGORIES

log = logging.getLogger(__name__)


def _fallback_plan(model: dict, product: Optional[dict]) -> dict:
    product_name = product.get("title") if product else None
    niche = model.get("niche") or "lifestyle"
    model_name = model.get("name") or "AI-модель"

    if product_name:
        return {
            "summary": f"Контент-серия для AI-модели {model_name} в нише {niche}. Товар: {product_name}.",
            "posts": [
                {
                    "title": "Нативный пост-знакомство с товаром",
                    "idea": f"Модель держит {product_name} в естественной сцене: кафе, дом, прогулка или рабочий день.",
                    "next_action": "Сгенерировать рекламный кадр с товаром в руке или рядом с моделью.",
                    "format": "Instagram 4:5",
                },
                {
                    "title": "UGC-кадр как будто снято на телефон",
                    "idea": "Лёгкий домашний/уличный кадр без ощущения студийной рекламы.",
                    "next_action": "Сделать 2–3 варианта UGC, выбрать самый живой.",
                    "format": "Story/Reels 9:16",
                },
                {
                    "title": "Крупный акцент на упаковке",
                    "idea": "Товар крупно в кадре, лицо модели мягко на фоне, упаковка читается.",
                    "next_action": "Выбрать режим точного сохранения товара / strict.",
                    "format": "Post/Ads 4:5",
                },
                {
                    "title": "Problem → solution",
                    "idea": "Сцена показывает ситуацию, где продукт органично решает маленькую повседневную задачу.",
                    "next_action": "Сгенерировать кадр и затем короткий Reels на 5–10 сек.",
                    "format": "Reels 9:16",
                },
                {
                    "title": "Premium placement",
                    "idea": "Более дорогая визуальная подача: чистый фон, мягкий свет, ощущение бренда.",
                    "next_action": "Сгенерировать hero-ad кадр для рекламы.",
                    "format": "Ads 4:5 / 1:1",
                },
            ],
            "reels": [
                {
                    "title": "Product reveal",
                    "idea": "Модель поднимает товар ближе к камере, лёгкий поворот, улыбка.",
                    "next_action": "Сначала сделать ключевой кадр, затем видео 5 сек.",
                    "duration": "5 сек",
                },
                {
                    "title": "UGC: проблема → продукт → реакция",
                    "idea": "Короткий ролик: ситуация, продукт появляется, финальная эмоция.",
                    "next_action": "Сгенерировать вертикальный кадр 9:16 и запустить Wan/Kling I2V.",
                    "duration": "10 сек",
                },
                {
                    "title": "Lifestyle walk",
                    "idea": "Модель идёт по улице/коридору/отелю, товар в руке или сумке.",
                    "next_action": "Выбрать fashion/lifestyle видео-сценарий.",
                    "duration": "5–10 сек",
                },
                {
                    "title": "Routine / tasting / unboxing",
                    "idea": "В зависимости от категории: пробует, распаковывает, наносит, показывает упаковку.",
                    "next_action": "Выбрать product/beauty/food сценарий видео.",
                    "duration": "10 сек",
                },
                {
                    "title": "Cinematic hero-shot",
                    "idea": "Медленный зум, красивый свет, товар в центре композиции.",
                    "next_action": "Делать только после выбора лучшего фото.",
                    "duration": "5 сек",
                },
            ],
            "ads": [
                {
                    "title": "Нативный отзыв",
                    "idea": "Текст от лица инфлюенсера: почему продукт попал в её день.",
                    "next_action": "Сделать UGC-фото + подпись с хук-фразой.",
                },
                {
                    "title": "Premium product placement",
                    "idea": "Чистый рекламный кадр для таргета и сайта.",
                    "next_action": "Сделать hero-ad фото, потом квадрат 1:1 для рекламы.",
                },
                {
                    "title": "Story/Reels hook",
                    "idea": "Быстрый первый кадр с интригой и читаемым товаром.",
                    "next_action": "Сгенерировать вертикальный keyframe 9:16.",
                },
            ],
            "hooks": [
                f"Я не ожидала, что {product_name} так легко впишется в мой день",
                "Сохрани, если любишь красивые вещи без лишнего шума",
                "Тот самый случай, когда упаковка выглядит дороже, чем стоит",
                "Маленький ритуал, который делает день приятнее",
                "Показываю без фильтров — как это выглядит в жизни",
                "Если бы мне надо было выбрать один кадр для рекламы, я бы выбрала этот",
            ],
            "next_steps": [
                "Нажми «📸 Сгенерировать 3 поста» и выбери лучший кадр.",
                "После лучшего кадра нажми «🎥 Сделать Reels». Во вкладке видео выбери формат 9:16 и длину 5–10 сек.",
                "Если товар плохо читается — используй режим «🎯 Точно сохранить товар». Для одежды — «👗 Примерка». ",
                "Сохрани 3 лучших результата в галерею и используй их как мини-кампанию.",
            ],
        }

    return {
        "summary": f"Контент-серия для AI-модели {model_name} в нише {niche}. Товар пока не выбран — серия строится вокруг образа модели и прогрева аудитории.",
        "posts": [
            {
                "title": "Пост-знакомство с образом",
                "idea": "Портрет модели, визуальное позиционирование и короткая подпись: кто она и какой у неё стиль.",
                "next_action": "Сгенерировать Instagram/lifestyle портрет 4:5.",
                "format": "Instagram 4:5",
            },
            {
                "title": "День из жизни",
                "idea": "Кафе, прогулка, рабочий день, отель или домашний кадр — чтобы модель стала живой.",
                "next_action": "Сделать 2–3 lifestyle кадра в разных локациях.",
                "format": "Post/Story",
            },
            {
                "title": "Стиль недели",
                "idea": "Fashion/outfit кадр, который можно потом использовать для рекламы одежды или аксессуаров.",
                "next_action": "Сгенерировать full-body fashion кадр.",
                "format": "4:5 / 9:16",
            },
            {
                "title": "UGC как будто с телефона",
                "idea": "Немного неидеальный, живой кадр: зеркало, лифт, кафе, улица.",
                "next_action": "Сгенерировать вертикальный UGC keyframe.",
                "format": "9:16",
            },
            {
                "title": "Кадр под будущую рекламу",
                "idea": "Нейтральная сцена с местом для товара/текста, чтобы потом встроить продукт.",
                "next_action": "Загрузить товар и повторить генерацию как рекламную.",
                "format": "Ads 4:5",
            },
        ],
        "reels": [
            {
                "title": "5 сек: живой портрет",
                "idea": "Мягкое движение камеры, модель смотрит в кадр, лёгкая улыбка.",
                "next_action": "Сгенерировать портретный keyframe и сделать видео 5 сек.",
                "duration": "5 сек",
            },
            {
                "title": "10 сек: прогулка / fashion walk",
                "idea": "Модель идёт, камера двигается за ней, ощущение Reels.",
                "next_action": "Выбрать видео-сценарий lifestyle/fashion.",
                "duration": "10 сек",
            },
            {
                "title": "UGC-вступление",
                "idea": "Как будто модель сама записала короткий ролик для сторис.",
                "next_action": "Сделать вертикальный кадр 9:16 и I2V.",
                "duration": "5 сек",
            },
            {
                "title": "Mood reel",
                "idea": "Красивый атмосферный ролик без товара: отель, город, кафе, вечерний свет.",
                "next_action": "Выбрать cinematic/video стиль.",
                "duration": "5–10 сек",
            },
            {
                "title": "Teaser для будущей рекламы",
                "idea": "Кадр-заготовка, куда позже можно встроить продукт.",
                "next_action": "Загрузить товар и использовать product-aware режим.",
                "duration": "5 сек",
            },
        ],
        "ads": [
            {
                "title": "Прогрев образа",
                "idea": "Серия кадров, чтобы аудитория привыкла к модели до рекламы.",
                "next_action": "Сделать 3 lifestyle поста.",
            },
            {
                "title": "Брендовый стиль",
                "idea": "Проверить, как модель смотрится в premium / UGC / fashion эстетике.",
                "next_action": "Сгенерировать по 1 кадру в каждом стиле.",
            },
            {
                "title": "Подготовка к product placement",
                "idea": "Создать кадры с пустым местом для будущего товара.",
                "next_action": "Добавить товар и перейти к рекламной съёмке.",
            },
        ],
        "hooks": [
            "Новый визуальный образ для контента на каждый день",
            "Сохрани, если нравится чистый lifestyle без перегруза",
            "Мини-серия, с которой можно начать вести AI-инфлюенсера",
            "Кадр, который выглядит как настоящая Instagram-съёмка",
            "Сначала стиль — потом реклама",
            "Этот образ легко адаптировать под продукт",
        ],
        "next_steps": [
            "Нажми «📸 Сгенерировать 3 поста» и выбери лучший стиль модели.",
            "Нажми «🎥 Сделать Reels» после лучшего кадра, чтобы оживить его.",
            "Загрузи товар, когда стиль модели утверждён — так реклама будет выглядеть цельно.",
            "Для коммерческого теста сделай 3 фото + 1 видео и отправь клиенту как мини-пакет.",
        ],
    }


def _normalize_items(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _item_to_text(item, i: int) -> list[str]:
    if isinstance(item, dict):
        title = item.get("title") or item.get("name") or f"Идея {i}"
        idea = item.get("idea") or item.get("description") or ""
        action = item.get("next_action") or item.get("action") or ""
        fmt = item.get("format") or item.get("duration") or ""
        lines = [f"{i}. {title}"]
        if idea:
            lines.append(f"   — {idea}")
        if fmt:
            lines.append(f"   Формат: {fmt}")
        if action:
            lines.append(f"   Дальше: {action}")
        return lines
    return [f"{i}. {item}"]


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
            "has_product_image": bool(product.get("primary_image_url")),
        }

    system = (
        "Ты — продюсер Instagram/Reels контента и рекламных креативов для AI-инфлюенсеров. "
        "Задача: не просто дать идеи, а дать понятную карту действий для клиента, что нажать и что получить дальше. "
        "Верни строго JSON без Markdown. Структура: "
        "summary:string, posts[5], reels[5], ads[3], hooks[6], next_steps[4]. "
        "Каждый posts/reels/ads элемент должен быть объектом: "
        "{title, idea, format или duration, next_action}. "
        "Если product=null, не пиши product reveal, product detail, product placement как будто товар есть. "
        "Тогда цель — прогрев образа AI-модели и подготовка к будущей рекламе. "
        "Если товар есть — делай акцент на точном сохранении товара, упаковки, логотипа и понятном следующем действии. "
        "Пиши по-русски, конкретно, коротко, для продающего визуального контента. Без adult/explicit."
    )
    user = {
        "model_name": model.get("name"),
        "niche": model.get("niche"),
        "persona": persona,
        "product": product_payload,
        "available_buttons": [
            "📸 Сгенерировать 3 поста",
            "🎥 Сделать Reels после лучшего кадра",
            "📢 Рекламный кадр с товаром",
            "📦 Загрузить товар",
            "👤 Вернуться к модели",
        ],
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
                    "max_tokens": 2200,
                    "temperature": 0.65,
                    "system": system,
                    "messages": [{"role": "user", "content": json.dumps(user, ensure_ascii=False)}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text").strip()
            plan = json.loads(text)
            if not plan.get("next_steps"):
                plan["next_steps"] = _fallback_plan(model, product).get("next_steps", [])
            return plan
    except Exception as e:
        log.warning("Content plan via Claude failed: %s", e)
        return _fallback_plan(model, product)


def render_plan(plan: dict) -> str:
    lines = ["🧾 Контент-план", ""]
    if plan.get("summary"):
        lines += [str(plan["summary"]), ""]

    for title, key in (("📸 Посты", "posts"), ("🎥 Reels", "reels"), ("📢 Реклама", "ads"), ("🪝 Хуки", "hooks")):
        items = _normalize_items(plan.get(key))
        if items:
            lines.append(title)
            for i, item in enumerate(items, 1):
                lines.extend(_item_to_text(item, i))
            lines.append("")

    steps = _normalize_items(plan.get("next_steps"))
    if steps:
        lines.append("✅ Что делать дальше")
        for i, step in enumerate(steps, 1):
            if isinstance(step, dict):
                step = step.get("text") or step.get("action") or str(step)
            lines.append(f"{i}. {step}")
        lines.append("")

    lines.append("👇 Выбери действие кнопкой ниже: сгенерировать посты, перейти к Reels или загрузить товар.")
    return "\n".join(lines).strip()
