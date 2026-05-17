from __future__ import annotations

import io
import json
import logging
import random
import time
from typing import Optional

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, URLInputFile

from app import db
from app.config import settings
from app.content_plan_client import generate_content_plan, render_plan
from app.factory_catalog import (
    AGE_RANGES, APPEARANCE_TYPES, HAIR_COLORS, HAIR_LENGTHS, MODEL_STYLES,
    NICHES, PHOTO_SCENARIOS, PRODUCT_CATEGORIES, VIDEO_FORMATS,
    get_photo_scenario, get_video_scenario,
)
from app.factory_keyboards import (
    back_menu_kb, main_menu_kb, model_age_kb, model_appearance_kb,
    model_card_kb, model_delete_kb, model_hair_color_kb, model_hair_length_kb,
    model_niche_kb, model_style_kb, models_kb, photo_categories_kb,
    photo_scenarios_kb, product_card_kb, product_category_kb, product_upload_kb,
    products_kb, pick_model_for_product_kb, after_photo_kb, video_categories_kb,
    video_durations_kb, video_formats_kb, video_scenarios_kb,
)
from app.factory_prompts import (
    build_hero_prompt, build_identity_pack_prompt, build_photo_prompt, build_video_prompt,
    build_base_scene_for_product_prompt, build_product_integration_prompt, clothing_tryon_category,
)
from app.image_client import generate_image
from app.identity import make_identity_dna
from app.product_clients import generate_tryon, integrate_product, product_holding, embed_product_strict, product_lifestyle_shot
from app.moderation import ModerationError, check_prompt
from app.states import ModelCreation, ProductUpload
from app.video_client import generate_video_from_image

router = Router()
log = logging.getLogger(__name__)


def _has_unlimited(user: dict) -> bool:
    return bool(user.get("is_admin") or user.get("tier") == "premium")


def _credits_label(user: dict) -> str:
    return "∞" if _has_unlimited(user) else str(user.get("credits", 0))


async def _spend(user: dict, amount: int, reason: str) -> bool:
    if _has_unlimited(user):
        return True
    if int(user.get("credits") or 0) < amount:
        return False
    for _ in range(amount):
        if not db.spend_credit(user["id"], reason):
            return False
    return True


def _model_caption(model: dict) -> str:
    persona = model.get("persona_json") or {}
    fixed = "✅" if model.get("hero_image_url") else "⚠️"
    pack_count = len(model.get("identity_pack_json") or []) if isinstance(model.get("identity_pack_json"), list) else 0
    dna = persona.get("identity_dna") if isinstance(persona.get("identity_dna"), dict) else {}
    dna_line = dna.get("identity_anchor_ru") or "уникальный визуальный якорь создан"
    return (
        f"👤 {model['name']}\n\n"
        f"Ниша: {NICHES.get(model.get('niche') or '', model.get('niche') or '—')}\n"
        f"Возраст: {persona.get('age', '—')}\n"
        f"Волосы: {persona.get('hair_color', '—')}, {persona.get('hair_length', '—')}\n"
        f"Типаж: {persona.get('appearance', '—')}\n"
        f"Стиль: {persona.get('style', '—')}\n\n"
        f"Постоянное лицо: {fixed} главный портрет\n"
        f"Пакет постоянства: {pack_count} кадров\n"
        f"ДНК лица: {dna_line[:180]}...\n\n"
        "Выбери, какой контент производим."
    )


def _product_caption(product: dict) -> str:
    return (
        f"📦 {product['title']}\n\n"
        f"Категория: {PRODUCT_CATEGORIES.get(product.get('category') or '', product.get('category') or '—')}\n"
        f"Описание: {product.get('description') or '—'}\n\n"
        "Теперь можно делать нативную рекламу, UGC, Reels и контент-план."
    )


async def _send_model_card(message_or_cb, model: dict):
    caption = _model_caption(model)
    if model.get("hero_image_url"):
        await message_or_cb.answer_photo(URLInputFile(model["hero_image_url"]), caption=caption, reply_markup=model_card_kb(model["id"]))
    else:
        await message_or_cb.answer(caption, reply_markup=model_card_kb(model["id"]))


# ---------- Model creation ----------

@router.callback_query(F.data == "fm:new")
async def model_new(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ModelCreation.waiting_name)
    await cb.message.answer(
        "🧬 Создаём AI-модель для контент-завода.\n\n"
        "Напиши имя модели. Например: Mira, Lora, Sophie, Алиса."
    )
    await cb.answer()


@router.message(ModelCreation.waiting_name)
async def model_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()[:40]
    if len(name) < 2:
        await message.answer("Имя слишком короткое. Напиши имя модели.")
        return
    await state.update_data(name=name)
    await state.set_state(ModelCreation.waiting_age)
    await message.answer("Выбери возрастной диапазон:", reply_markup=model_age_kb())


@router.callback_query(ModelCreation.waiting_age, F.data.startswith("fmage:"))
async def model_age(cb: CallbackQuery, state: FSMContext):
    key = cb.data.split(":", 1)[1]
    await state.update_data(age=AGE_RANGES.get(key, key))
    await state.set_state(ModelCreation.waiting_hair_color)
    await cb.message.edit_text("Цвет волос:", reply_markup=model_hair_color_kb())
    await cb.answer()


@router.callback_query(ModelCreation.waiting_hair_color, F.data.startswith("fmhair:"))
async def model_hair(cb: CallbackQuery, state: FSMContext):
    key = cb.data.split(":", 1)[1]
    await state.update_data(hair_color=HAIR_COLORS.get(key, key))
    await state.set_state(ModelCreation.waiting_hair_length)
    await cb.message.edit_text("Длина волос:", reply_markup=model_hair_length_kb())
    await cb.answer()


@router.callback_query(ModelCreation.waiting_hair_length, F.data.startswith("fmlen:"))
async def model_hair_len(cb: CallbackQuery, state: FSMContext):
    key = cb.data.split(":", 1)[1]
    await state.update_data(hair_length=HAIR_LENGTHS.get(key, key))
    await state.set_state(ModelCreation.waiting_appearance)
    await cb.message.edit_text("Типаж внешности:", reply_markup=model_appearance_kb())
    await cb.answer()


@router.callback_query(ModelCreation.waiting_appearance, F.data.startswith("fmap:"))
async def model_appearance(cb: CallbackQuery, state: FSMContext):
    key = cb.data.split(":", 1)[1]
    await state.update_data(appearance=APPEARANCE_TYPES.get(key, key))
    await state.set_state(ModelCreation.waiting_style)
    await cb.message.edit_text("Стиль модели:", reply_markup=model_style_kb())
    await cb.answer()


@router.callback_query(ModelCreation.waiting_style, F.data.startswith("fmstyle:"))
async def model_style(cb: CallbackQuery, state: FSMContext):
    key = cb.data.split(":", 1)[1]
    await state.update_data(style=MODEL_STYLES.get(key, key))
    await state.set_state(ModelCreation.waiting_niche)
    await cb.message.edit_text("Ниша / роль модели:", reply_markup=model_niche_kb())
    await cb.answer()


@router.callback_query(ModelCreation.waiting_niche, F.data.startswith("fmniche:"))
async def model_niche(cb: CallbackQuery, state: FSMContext):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    key = cb.data.split(":", 1)[1]
    data = await state.get_data()
    seed = random.randint(1, 2_000_000_000)
    identity_dna = make_identity_dna(data["name"], seed)
    persona = {
        "age": data.get("age"),
        "hair_color": data.get("hair_color"),
        "hair_length": data.get("hair_length"),
        "appearance": data.get("appearance"),
        "style": data.get("style"),
        "niche": NICHES.get(key, key),
        "identity_dna": identity_dna,
        "identity_note": identity_dna.get("identity_anchor_en"),
    }
    model = db.create_ai_model(user["id"], data["name"], persona, key, seed)
    await state.clear()

    placeholder = await cb.message.edit_text(
        f"✅ Модель {model['name']} создана.\n\n"
        "Сейчас создаю главный портрет — он станет лицом модели для будущего контента."
    )
    await cb.answer()

    prompt = build_hero_prompt(model)
    try:
        check_prompt(prompt)
        image_url = await generate_image(prompt=prompt, seed=seed, aspect_ratio="4:5")
        stored_url = await db.upload_image_from_url(image_url, f"factory/u{user['id']}/models/m{model['id']}/hero_{int(time.time())}.jpg")
        db.update_ai_model(model["id"], hero_image_url=stored_url, identity_pack_json=[stored_url])
        fresh = db.get_ai_model(model["id"], user_id=user["id"])
        try:
            await placeholder.delete()
        except Exception:
            pass
        await cb.message.answer_photo(URLInputFile(stored_url), caption=_model_caption(fresh), reply_markup=model_card_kb(model["id"]))
    except Exception as e:
        log.exception("Hero model generation failed")
        await placeholder.edit_text(
            f"Модель {model['name']} создана, но первый портрет не получился.\n"
            "Можно открыть карточку и закрепить лицо позже.",
            reply_markup=model_card_kb(model["id"]),
        )


@router.callback_query(F.data == "fm:list")
async def model_list(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    models = db.get_user_ai_models(user["id"])
    text = "👤 Твои AI-модели" if models else "Пока нет AI-моделей. Создай первую."
    try:
        await cb.message.edit_text(text, reply_markup=models_kb(models))
    except Exception:
        await cb.message.answer(text, reply_markup=models_kb(models))
    await cb.answer()


@router.callback_query(F.data.startswith("fm:open:"))
async def model_open(cb: CallbackQuery):
    model_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    model = db.get_ai_model(model_id, user_id=user["id"])
    if not model:
        await cb.answer("Модель не найдена", show_alert=True)
        return
    try:
        await cb.message.delete()
    except Exception:
        pass
    await _send_model_card(cb.message, model)
    await cb.answer()


@router.callback_query(F.data.startswith("fm:delq:"))
async def model_delete_question(cb: CallbackQuery):
    model_id = int(cb.data.split(":")[-1])
    await cb.message.answer("Удалить AI-модель? Контент и товары не удалятся, но связь с моделью потеряется.", reply_markup=model_delete_kb(model_id))
    await cb.answer()


@router.callback_query(F.data.startswith("fm:del:"))
async def model_delete(cb: CallbackQuery):
    model_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    ok = db.delete_ai_model(model_id, user["id"])
    models = db.get_user_ai_models(user["id"])
    await cb.message.answer("Удалено." if ok else "Не удалось удалить.", reply_markup=models_kb(models))
    await cb.answer()


@router.callback_query(F.data.startswith("fm:identity:"))
async def model_identity_pack(cb: CallbackQuery):
    model_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    user = db.refresh_daily_credits(user)
    model = db.get_ai_model(model_id, user_id=user["id"])
    if not model:
        await cb.answer("Модель не найдена", show_alert=True)
        return

    views = [
        "front face portrait with the same unique facial DNA",
        "three quarter face portrait with the same unique facial DNA",
        "profile portrait with the same unique facial DNA",
        "full body neutral model digitals with the same face and proportions",
    ]
    cost = len(views)
    if not await _spend(user, cost, "identity_pack"):
        await cb.answer(f"Нужно {cost} кредитов для identity pack", show_alert=True)
        return

    await cb.answer("Создаю identity pack…")
    status = await cb.message.answer("🧬 Генерирую 4 референса лица/фигуры. Это может занять пару минут.")
    urls = list(model.get("identity_pack_json") or [])
    for i, view in enumerate(views, 1):
        try:
            prompt = build_identity_pack_prompt(model, view)
            image_url = await generate_image(prompt=prompt, seed=int(model.get("seed") or random.randint(1, 999999)) + i, aspect_ratio="4:5")
            stored = await db.upload_image_from_url(image_url, f"factory/u{user['id']}/models/m{model_id}/identity_{i}_{int(time.time())}.jpg")
            urls.append(stored)
            await cb.message.answer_photo(URLInputFile(stored), caption=f"Референс лица {i}/4")
        except Exception as e:
            log.warning("Identity ref failed: %s", e)
    db.update_ai_model(model_id, identity_pack_json=urls)
    await status.edit_text("✅ Пакет постоянства обновлён. Теперь модель будет отличаться от других и держать один образ заметно лучше.", reply_markup=model_card_kb(model_id))


@router.callback_query(F.data.startswith("fc:video_model:"))
async def video_model_home(cb: CallbackQuery):
    model_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    model = db.get_ai_model(model_id, user_id=user["id"])
    if not model:
        await cb.answer("Модель не найдена", show_alert=True)
        return
    gens = [g for g in db.get_recent_content_generations(user["id"], limit=12) if g.get("model_id") == model_id and g.get("image_url")]
    if not gens:
        await cb.message.answer(
            "🎥 Видео делается из готового кадра. Сначала сделай фото или рекламный кадр, потом под ним нажми «Сделать Reels/видео».",
            reply_markup=model_card_kb(model_id),
        )
    else:
        await cb.message.answer("Выбери кадр для видео. Под каждым кадром есть кнопка Reels/видео.")
        for g in gens[:5]:
            await cb.message.answer_photo(
                URLInputFile(g["image_url"]),
                caption=f"Кадр #{g['id']} · {g.get('scenario_key')}",
                reply_markup=after_photo_kb(model_id, g.get("product_id") or 0, g.get("scenario_key") or "ig_cafe", g["id"]),
            )
    await cb.answer()


# ---------- Product upload ----------

@router.callback_query(F.data == "fp:new")
async def product_new(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ProductUpload.waiting_title)
    await cb.message.answer("📦 Добавляем товар.\n\nНапиши название товара: например, шоколадка ChocoPro, платье Aurora, бутылка воды Aqua.")
    await cb.answer()


@router.message(ProductUpload.waiting_title)
async def product_title(message: Message, state: FSMContext):
    title = (message.text or "").strip()[:80]
    if len(title) < 2:
        await message.answer("Слишком короткое название. Напиши название товара.")
        return
    await state.update_data(title=title)
    await state.set_state(ProductUpload.waiting_category)
    await message.answer("Выбери категорию товара:", reply_markup=product_category_kb())


@router.callback_query(ProductUpload.waiting_category, F.data.startswith("fpcat:"))
async def product_category(cb: CallbackQuery, state: FSMContext):
    key = cb.data.split(":", 1)[1]
    await state.update_data(category=key)
    await state.set_state(ProductUpload.waiting_description)
    await cb.message.edit_text(
        "Коротко опиши товар: цвет, форма, упаковка, этикетка, важные детали.\n\n"
        "Пример: тёмная плитка шоколада в матовой чёрной упаковке с золотой надписью."
    )
    await cb.answer()


@router.message(ProductUpload.waiting_description)
async def product_description(message: Message, state: FSMContext):
    desc = (message.text or "").strip()[:1000]
    await state.update_data(description=desc, photos=[])
    await state.set_state(ProductUpload.waiting_photos)
    await message.answer(
        "Теперь загрузи 1–5 фото товара. Лучше: чистый фон, видно упаковку, без бликов.\n\n"
        "После загрузки нажми «Готово».",
        reply_markup=product_upload_kb(False),
    )


@router.message(ProductUpload.waiting_photos, F.photo)
async def product_photo(message: Message, state: FSMContext, bot: Bot):
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    data = await state.get_data()
    photos = list(data.get("photos") or [])
    if len(photos) >= 5:
        await message.answer("Максимум 5 фото. Нажми «Готово».", reply_markup=product_upload_kb(True))
        return
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    bio = io.BytesIO()
    await bot.download_file(file.file_path, destination=bio)
    raw = bio.getvalue()
    path = f"factory/u{user['id']}/products/tmp_{int(time.time())}_{len(photos)+1}.jpg"
    url = await db.upload_bytes(raw, path, content_type="image/jpeg")
    photos.append(url)
    await state.update_data(photos=photos)
    await message.answer(f"Фото принято: {len(photos)}/5. Можно загрузить ещё или нажать «Готово».", reply_markup=product_upload_kb(True))


@router.callback_query(ProductUpload.waiting_photos, F.data == "fp:done")
async def product_done(cb: CallbackQuery, state: FSMContext):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    data = await state.get_data()
    photos = list(data.get("photos") or [])
    if not photos:
        await cb.answer("Сначала загрузи хотя бы одно фото товара", show_alert=True)
        return
    product = db.create_product(
        user_id=user["id"],
        title=data.get("title", "Товар"),
        category=data.get("category", "other"),
        description=data.get("description", ""),
        primary_image_url=photos[0],
        extra_images=photos[1:],
    )
    await state.clear()
    try:
        await cb.message.delete()
    except Exception:
        pass
    await cb.message.answer_photo(URLInputFile(product["primary_image_url"]), caption=_product_caption(product), reply_markup=product_card_kb(product["id"]))
    await cb.answer("Товар сохранён")


@router.callback_query(F.data == "fp:list")
async def product_list(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    products = db.get_user_products(user["id"])
    text = "📦 Твои товары" if products else "Пока нет товаров. Добавь бутылку, шоколадку, платье, косметику или другой продукт."
    try:
        await cb.message.edit_text(text, reply_markup=products_kb(products))
    except Exception:
        await cb.message.answer(text, reply_markup=products_kb(products))
    await cb.answer()


@router.callback_query(F.data.startswith("fp:open:"))
async def product_open(cb: CallbackQuery):
    product_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    product = db.get_product(product_id, user_id=user["id"])
    if not product:
        await cb.answer("Товар не найден", show_alert=True)
        return
    try:
        await cb.message.delete()
    except Exception:
        pass
    await cb.message.answer_photo(URLInputFile(product["primary_image_url"]), caption=_product_caption(product), reply_markup=product_card_kb(product_id))
    await cb.answer()


@router.callback_query(F.data.startswith("fp:pick_model_"))
async def product_pick_model(cb: CallbackQuery):
    parts = cb.data.split(":")
    mode = parts[1].replace("pick_model_", "")
    product_id = int(parts[2])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    models = db.get_user_ai_models(user["id"])
    if not models:
        await cb.message.answer("Сначала создай AI-модель.", reply_markup=main_menu_kb())
    else:
        await cb.message.answer("Выбери модель для этого товара:", reply_markup=pick_model_for_product_kb(models, product_id, mode))
    await cb.answer()


@router.callback_query(F.data.startswith("fp:delq:"))
async def product_delete_question(cb: CallbackQuery):
    product_id = int(cb.data.split(":")[-1])
    await cb.message.answer(
        "Удалить товар?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Да, удалить", callback_data=f"fp:del:{product_id}")],
            [InlineKeyboardButton(text="Отмена", callback_data=f"fp:open:{product_id}")],
        ]),
    )
    await cb.answer()

@router.callback_query(F.data.startswith("fp:del:"))
async def product_delete(cb: CallbackQuery):
    product_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    ok = db.delete_product(product_id, user["id"])
    products = db.get_user_products(user["id"])
    await cb.message.answer("Товар удалён." if ok else "Не удалось удалить.", reply_markup=products_kb(products))
    await cb.answer()


# ---------- Photo/content generation ----------

@router.callback_query(F.data == "fc:photo_home")
async def photo_home(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    models = db.get_user_ai_models(user["id"])
    if not models:
        await cb.message.answer("Сначала создай AI-модель.", reply_markup=main_menu_kb())
    else:
        await cb.message.answer("Выбери модель для Instagram/рекламной съёмки:", reply_markup=models_kb(models))
    await cb.answer()


@router.callback_query(F.data == "fc:video_home")
async def video_home(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    gens = db.get_recent_content_generations(user["id"], limit=5)
    if not gens:
        await cb.message.answer(
            "🎥 Видео делается из готового кадра.\n\n"
            "Сначала сгенерируй фото-контент, потом под кадром нажми «Сделать Reels/видео».",
            reply_markup=main_menu_kb(),
        )
    else:
        await cb.message.answer("Выбери последний кадр и нажми под ним «Сделать Reels/видео». Показываю последние:")
        for g in gens:
            if g.get("image_url"):
                await cb.message.answer_photo(URLInputFile(g["image_url"]), caption=f"Кадр #{g['id']}: {g.get('scenario_key')}", reply_markup=after_photo_kb(g["model_id"], g.get("product_id") or 0, g.get("scenario_key") or "ig_cafe", g["id"]))
    await cb.answer()


@router.callback_query(F.data == "fc:plan_home")
async def plan_home(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    models = db.get_user_ai_models(user["id"])
    if not models:
        await cb.message.answer("Сначала создай AI-модель.", reply_markup=main_menu_kb())
    else:
        await cb.message.answer("Выбери модель для контент-плана:", reply_markup=models_kb(models))
    await cb.answer()


@router.callback_query(F.data.startswith("fc:ad_products:"))
async def ad_products(cb: CallbackQuery):
    model_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    products = db.get_user_products(user["id"])
    if not products:
        await cb.message.answer("Сначала добавь товар: бутылку, шоколадку, платье, косметику или аксессуар.", reply_markup=products_kb(products))
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"📦 {p['title']}", callback_data=f"fc:photo:{model_id}:{p['id']}")]
            for p in products
        ] + [[InlineKeyboardButton(text="➕ Добавить товар", callback_data="fp:new")]])
        await cb.message.answer("Выбери товар для рекламной съёмки:", reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("fc:photo:"))
async def photo_categories(cb: CallbackQuery):
    _, _, model_id_str, product_id_str = cb.data.split(":")
    model_id = int(model_id_str)
    product_id = int(product_id_str)
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    model = db.get_ai_model(model_id, user_id=user["id"])
    if not model:
        await cb.answer("Модель не найдена", show_alert=True)
        return
    product = db.get_product(product_id, user_id=user["id"]) if product_id else None
    title = f"📸 Сценарии для {model['name']}"
    if product:
        title += f" + {product['title']}"
    await cb.message.answer(title, reply_markup=photo_categories_kb(model_id, product_id))
    await cb.answer()


@router.callback_query(F.data.startswith("fc:pcat:"))
async def photo_scenarios(cb: CallbackQuery):
    _, _, model_id_str, product_id_str, cat_key = cb.data.split(":")
    model_id = int(model_id_str)
    product_id = int(product_id_str)
    if cat_key not in PHOTO_SCENARIOS:
        await cb.answer("Категория не найдена", show_alert=True)
        return
    await cb.message.answer(
        f"📸 Выбери конкретную сцену: {PHOTO_SCENARIOS[cat_key]['title']}",
        reply_markup=photo_scenarios_kb(model_id, product_id, cat_key),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("fc:pgen:"))
async def photo_generate(cb: CallbackQuery):
    _, _, model_id_str, product_id_str, scenario_key = cb.data.split(":")
    model_id = int(model_id_str)
    product_id = int(product_id_str)
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    user = db.refresh_daily_credits(user)

    model = db.get_ai_model(model_id, user_id=user["id"])
    product = db.get_product(product_id, user_id=user["id"]) if product_id else None
    scenario = get_photo_scenario(scenario_key)
    if not model or not scenario:
        await cb.answer("Данные не найдены", show_alert=True)
        return
    if product_id and not product:
        await cb.answer("Товар не найден", show_alert=True)
        return
    if not await _spend(user, 1, "content_photo"):
        await cb.answer("Не хватает кредитов", show_alert=True)
        return

    # Important: if product is uploaded, we should actually use its image.
    # Old v3 only put product name into text prompt, so the uploaded dress/bottle never reached the model.
    prompt = build_photo_prompt(model, product, scenario)
    try:
        check_prompt(prompt)
    except ModerationError as e:
        await cb.answer(e.reason, show_alert=True)
        return

    gen = db.create_content_generation(user["id"], model_id, product_id or None, "photo", scenario_key, prompt, fmt=scenario["aspect"])
    await cb.answer("Готовлю кадр…")

    product_mode = bool(product and settings.product_aware_mode)
    if product and product.get("category") == "clothes":
        wait_text = "👗 Сначала делаю базовый кадр модели, потом надеваю загруженную вещь через virtual try-on."
    elif product_mode:
        wait_text = "📦 Собираю рекламный кадр с учётом фото товара. Стараюсь сохранить форму, цвет и упаковку."
    else:
        wait_text = "📸 Генерирую рекламный кадр. Обычно 10–30 секунд."
    placeholder = await cb.message.answer(wait_text)

    try:
        seed = int(model.get("seed") or random.randint(1, 999999999)) + random.randint(1, 999999)

        if product_mode:
            # Step 1: generate a clean base image with the same AI model.
            base_prompt = build_base_scene_for_product_prompt(model, product, scenario)
            base_url = await generate_image(prompt=base_prompt, seed=seed, aspect_ratio=scenario["aspect"])

            if product.get("category") == "clothes":
                # Step 2a: virtual try-on, so the uploaded dress/clothes are actually worn.
                garment_url = product.get("primary_image_url")
                try:
                    provider_url = await generate_tryon(
                        model_image_url=base_url,
                        garment_image_url=garment_url,
                        category=clothing_tryon_category(product),
                    )
                except Exception as e:
                    log.warning("Try-on failed; falling back to prompt-only generation: %s", e)
                    provider_url = await generate_image(prompt=prompt, seed=seed + 17, aspect_ratio=scenario["aspect"])
            else:
                # Step 2b: non-clothing product. Use strict product-preserving tools first.
                # Qwen/fusion can look pretty, but often redraws the product (wrong logo/label).
                # For real ad content the uploaded product must stay the same.
                product_ref = product.get("primary_image_url")
                holding_scenarios = {
                    "pr_hand", "pr_reveal", "pr_use", "pr_story",
                    "fo_sip", "fo_choco", "be_skin", "be_perfume", "v_pr_hand"
                }
                try:
                    mode = (settings.product_composition_mode or "fast").lower()
                    if mode == "holding" and settings.product_holding_enabled and scenario_key in holding_scenarios:
                        provider_url = await product_holding(
                            person_image_url=base_url,
                            product_image_url=product_ref,
                        )
                    elif mode == "fusion":
                        integration_prompt = build_product_integration_prompt(product, scenario)
                        provider_url = await integrate_product(
                            scene_image_url=base_url,
                            product_image_url=product_ref,
                            prompt=integration_prompt,
                        )
                    elif mode == "strict" and settings.product_embed_enabled:
                        provider_url = await embed_product_strict(
                            scene_image_url=base_url,
                            product_image_url=product_ref,
                            aspect_ratio=scenario["aspect"],
                            scenario_key=scenario_key,
                            seed=seed,
                        )
                    else:
                        # Fast MVP mode: product-first lifestyle shot. It is faster and usually preserves packaging better.
                        provider_url = await product_lifestyle_shot(
                            product_image_url=product_ref,
                            scene_description=(
                                f"premium Instagram advertising scene inspired by: {scenario['prompt']}; "
                                f"AI model style nearby or implied: {model['name']}; "
                                "clean commercial lighting, realistic shadows, high-end product photography, preserve original packaging"
                            ),
                            placement="bottom_center",
                        )
                except Exception as e:
                    log.warning("Product-aware placement failed; trying product-shot fallback: %s", e)
                    try:
                        provider_url = await product_lifestyle_shot(
                            product_image_url=product_ref,
                            scene_description=(
                                f"premium Instagram advertising scene inspired by: {scenario['prompt']}; "
                                "clean commercial lighting, realistic shadows, high-end product photography, preserve original packaging"
                            ),
                            placement="bottom_center",
                        )
                    except Exception as e2:
                        log.warning("Product shot fallback failed; falling back to prompt-only generation: %s", e2)
                        provider_url = await generate_image(prompt=prompt, seed=seed + 17, aspect_ratio=scenario["aspect"])
        else:
            provider_url = await generate_image(prompt=prompt, seed=seed, aspect_ratio=scenario["aspect"])

        stored = await db.upload_image_from_url(provider_url, f"factory/u{user['id']}/content/g{gen['id']}_{int(time.time())}.jpg")
        db.update_content_generation(gen["id"], status="done", image_url=stored)
        try:
            await placeholder.delete()
        except Exception:
            pass
        fresh = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
        product_note = (
            f"товар использован по фото · режим {settings.product_composition_mode}"
            if product_mode else "без товара"
        )
        await cb.message.answer_photo(
            URLInputFile(stored),
            caption=(
                f"📸 {scenario['label']}\n"
                f"Модель: {model['name']}\n"
                f"Товар: {product['title'] if product else 'без товара'}\n"
                f"Режим: {product_note}\n"
                f"Кредиты: {_credits_label(fresh)}"
            ),
            reply_markup=after_photo_kb(model_id, product_id, scenario_key, gen["id"]),
        )
    except Exception as e:
        log.exception("Factory photo generation failed")
        db.update_content_generation(gen["id"], status="failed", error=str(e)[:500])
        if not _has_unlimited(user):
            db.grant_credits(user["id"], 1, "refund_failed_content_photo", {"gen_id": gen["id"]})
        await placeholder.edit_text("Не получилось сделать кадр. Кредит вернул, попробуй другой сценарий.")


# ---------- Video generation ----------

@router.callback_query(F.data.startswith("fv:cat:"))
async def video_cat(cb: CallbackQuery):
    gen_id = int(cb.data.split(":")[-1])
    await cb.message.answer("🎬 Собираем Reels/видео. Выбери стиль ролика:", reply_markup=video_categories_kb(gen_id))
    await cb.answer()


@router.callback_query(F.data.startswith("fv:sc:"))
async def video_scene(cb: CallbackQuery):
    _, _, gen_id_str, cat_key = cb.data.split(":")
    gen_id = int(gen_id_str)
    await cb.message.answer("🎥 Выбери движение камеры / действие в кадре:", reply_markup=video_scenarios_kb(gen_id, cat_key))
    await cb.answer()


@router.callback_query(F.data.startswith("fv:fmt:"))
async def video_format(cb: CallbackQuery):
    _, _, gen_id_str, scenario_key = cb.data.split(":")
    await cb.message.answer("📐 Куда публикуем? Выбери формат:", reply_markup=video_formats_kb(int(gen_id_str), scenario_key))
    await cb.answer()


@router.callback_query(F.data.startswith("fv:dur:"))
async def video_duration(cb: CallbackQuery):
    _, _, gen_id_str, scenario_key, fmt_key = cb.data.split(":")
    await cb.message.answer("⏱ Выбери длину видео:", reply_markup=video_durations_kb(int(gen_id_str), scenario_key, fmt_key))
    await cb.answer()


@router.callback_query(F.data.startswith("fv:gen:"))
async def video_generate(cb: CallbackQuery):
    _, _, gen_id_str, scenario_key, fmt_key, dur_key = cb.data.split(":")
    gen_id = int(gen_id_str)
    duration = int(dur_key)
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    user = db.refresh_daily_credits(user)
    gen = db.get_content_generation(gen_id, user_id=user["id"])
    if not gen or not gen.get("image_url"):
        await cb.answer("Кадр не найден", show_alert=True)
        return
    scenario = get_video_scenario(scenario_key)
    if not scenario:
        await cb.answer("Сценарий не найден", show_alert=True)
        return
    fmt = VIDEO_FORMATS.get(fmt_key, VIDEO_FORMATS["916"])[1]
    cost = max(1, int(duration / 5)) * int(settings.video_cost_credits)
    if not await _spend(user, cost, "content_video"):
        await cb.answer(f"Для видео нужно {cost} кредитов", show_alert=True)
        return

    model = db.get_ai_model(gen["model_id"], user_id=user["id"])
    product = db.get_product(gen.get("product_id"), user_id=user["id"]) if gen.get("product_id") else None
    prompt = build_video_prompt(gen, product, scenario)
    await cb.answer("Генерирую видео…")
    placeholder = await cb.message.answer(f"🎥 Делаю видео {duration} сек в формате {fmt}. Обычно 1–3 минуты.")
    try:
        provider_url = await generate_video_from_image(gen["image_url"], prompt=prompt, duration=duration, aspect_ratio=fmt)
        stored = await db.upload_file_from_url(provider_url, f"factory/u{user['id']}/videos/g{gen_id}_{duration}_{int(time.time())}.mp4", content_type="video/mp4")
        db.update_content_generation(gen_id, video_url=stored, video_status="done", video_prompt=prompt, duration_sec=duration, format=fmt)
        try:
            await placeholder.delete()
        except Exception:
            pass
        await cb.message.answer_video(URLInputFile(stored), caption=f"🎥 Готово: {scenario['label']} · {duration} сек · {fmt}", reply_markup=main_menu_kb())
    except Exception as e:
        log.exception("Factory video failed")
        db.update_content_generation(gen_id, video_status="failed", error=str(e)[:500])
        if not _has_unlimited(user):
            db.grant_credits(user["id"], cost, "refund_failed_content_video", {"gen_id": gen_id})
        await placeholder.edit_text("Не получилось сделать видео. Кредиты вернул, попробуй другой сценарий.")


# ---------- Content plan ----------

@router.callback_query(F.data.startswith("fc:plan_model:"))
async def content_plan(cb: CallbackQuery):
    _, _, model_id_str, product_id_str = cb.data.split(":")
    model_id = int(model_id_str)
    product_id = int(product_id_str)
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    model = db.get_ai_model(model_id, user_id=user["id"])
    product = db.get_product(product_id, user_id=user["id"]) if product_id else None
    if not model:
        await cb.answer("Модель не найдена", show_alert=True)
        return
    await cb.answer("Готовлю контент-план…")
    placeholder = await cb.message.answer("🧾 Собираю идеи постов, Reels и рекламы…")
    plan = await generate_content_plan(model, product)
    db.save_content_plan(user["id"], model_id, product_id or None, model.get("niche") or "", plan)
    text = render_plan(plan)
    if len(text) > 3800:
        text = text[:3800] + "\n\n…"
    await placeholder.edit_text(text, reply_markup=main_menu_kb())


@router.callback_query(F.data == "private:home")
async def private_home(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    if not (user.get("is_admin") or user.get("tier") in ("pro", "premium")):
        await cb.message.answer(
            "🔒 Private — отдельный платный модуль.\n\n"
            "Основной сервис — профессиональный контент-завод для AI-моделей и рекламы. "
            "Private-раздел не участвует в основном флоу и открывается только платным пользователям.",
            reply_markup=main_menu_kb(),
        )
    else:
        await cb.message.answer(
            "🔒 Private-раздел зарезервирован как отдельный модуль.\n"
            "Сейчас он отключён от основной логики, чтобы не мешать профессиональному продукту.",
            reply_markup=main_menu_kb(),
        )
    await cb.answer()

@router.callback_query(F.data == "quick:start")
async def quick_start(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    models = db.get_user_ai_models(user["id"])
    products = db.get_user_products(user["id"])
    if not models:
        await cb.message.answer(
            "🚀 Быстрый старт\n\nШаг 1/3 — сначала создай AI-модель. После этого загрузишь товар и сразу соберём рекламный кадр.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🧬 Создать AI-модель", callback_data="fm:new")],
                [InlineKeyboardButton(text="◀ В меню", callback_data="menu")],
            ]),
        )
    elif not products:
        await cb.message.answer(
            "🚀 Быстрый старт\n\nШаг 2/3 — модель уже есть. Теперь загрузи товар: платье, бутылку, шоколадку, косметику или аксессуар.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📦 Загрузить товар", callback_data="fp:new")],
                [InlineKeyboardButton(text="👤 Открыть модель", callback_data=f"fm:open:{models[0]['id']}")],
                [InlineKeyboardButton(text="◀ В меню", callback_data="menu")],
            ]),
        )
    else:
        await cb.message.answer(
            "🚀 Быстрый старт\n\nШаг 3/3 — выбери модель, затем товар и сценарий рекламы.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"📢 Реклама: {models[0]['name']} + {products[0]['title']}", callback_data=f"fc:photo:{models[0]['id']}:{products[0]['id']}")],
                [InlineKeyboardButton(text="👤 Мои модели", callback_data="fm:list"), InlineKeyboardButton(text="📦 Мои товары", callback_data="fp:list")],
                [InlineKeyboardButton(text="◀ В меню", callback_data="menu")],
            ]),
        )
    await cb.answer()
