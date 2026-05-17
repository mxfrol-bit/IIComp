from __future__ import annotations

import html
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.config import settings
from app.db import supabase

app = FastAPI(title="IIComp AI Content Factory", version="10.0")

BOT_USERNAME = "MYAICOM_bot"


def _check_token(token: str | None) -> None:
    expected = settings.admin_web_token
    if not expected:
        raise HTTPException(403, "ADMIN_WEB_TOKEN is not configured in Railway")
    if token != expected:
        raise HTTPException(403, "Bad admin token")


def _public_url() -> str:
    return (settings.web_public_url or "").rstrip("/")


def _bot_link(start: str = "") -> str:
    suffix = f"?start={start}" if start else ""
    return f"https://t.me/{BOT_USERNAME}{suffix}"


def _count(table: str) -> int:
    try:
        res = supabase.table(table).select("id", count="exact").limit(1).execute()
        return int(res.count or 0)
    except Exception:
        return 0


def _recent(table: str, limit: int = 10) -> list[dict[str, Any]]:
    try:
        return supabase.table(table).select("*").order("created_at", desc=True).limit(limit).execute().data or []
    except Exception:
        return []


def _stats() -> dict[str, int]:
    return {
        "users": _count("users"),
        "ai_models": _count("ai_models"),
        "products": _count("products"),
        "content_generations": _count("content_generations"),
        "content_plans": _count("content_plans"),
        "payments": _count("payments"),
    }


def _esc(value: Any) -> str:
    return html.escape(str(value or ""))


def _rows(items: list[dict[str, Any]], cols: list[str]) -> str:
    if not items:
        return "<tr><td colspan='10'>Пока пусто</td></tr>"
    out = []
    for item in items:
        tds = []
        for col in cols:
            val = item.get(col)
            if isinstance(val, dict):
                val = ", ".join([f"{k}: {v}" for k, v in list(val.items())[:4]])
            if isinstance(val, list):
                val = f"{len(val)} items"
            text = _esc(val)[:260]
            if col.endswith("_url") and val:
                text = f"<a href='{_esc(val)}' target='_blank'>открыть</a>"
            tds.append(f"<td>{text}</td>")
        out.append("<tr>" + "".join(tds) + "</tr>")
    return "".join(out)


def _base(title: str, body: str, *, compact: bool = False) -> str:
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="theme-color" content="#0d0c0a" />
<title>{_esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Spectral:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
:root {{
  --ink:#15130f; --paper:#f4f1ea; --paper2:#ece7da; --card:#fffdf7;
  --line:#d8d2c2; --line2:#c2bba6; --muted:#736b58; --soft:#3f3a30;
  --accent:#e0431f; --accent2:#1a1714; --gold:#b8893b; --green:#3f6f43;
  --shadow:0 1px 0 #fff inset, 0 18px 50px -28px rgba(20,16,10,.45);
  --r:6px; --disp:'Space Grotesk',ui-sans-serif,system-ui,sans-serif;
  --serif:'Spectral',Georgia,serif; --mono:'JetBrains Mono',ui-monospace,monospace;
}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}}
body{{margin:0;font-family:var(--disp);color:var(--ink);background:var(--paper);
  background-image:
    linear-gradient(rgba(20,16,10,.022) 1px,transparent 1px),
    linear-gradient(90deg,rgba(20,16,10,.022) 1px,transparent 1px);
  background-size:34px 34px;font-feature-settings:"ss01","cv01";-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}
.wrap{{max-width:1240px;margin:0 auto;padding:{'14px' if compact else '20px'} 22px 90px}}
.nav{{position:sticky;top:0;z-index:50;background:rgba(244,241,234,.86);backdrop-filter:blur(10px);border-bottom:1px solid var(--line2)}}
.nav-inner{{max-width:1240px;margin:0 auto;padding:13px 22px;display:flex;align-items:center;justify-content:space-between;gap:14px}}
.logo{{display:flex;align-items:center;gap:11px;font-weight:700;letter-spacing:-.02em;font-size:18px;text-transform:uppercase}}
.logo-badge{{width:34px;height:34px;border-radius:3px;background:var(--accent2);color:var(--paper);display:grid;place-items:center;font-size:15px;border:1px solid var(--ink)}}
.nav-links{{display:flex;gap:2px;flex-wrap:wrap;align-items:center}}
.nav-links a{{padding:8px 13px;color:var(--soft);font-size:13px;font-weight:500;text-transform:uppercase;letter-spacing:.04em;border-bottom:2px solid transparent}}
.nav-links a:hover{{color:var(--accent);border-bottom-color:var(--accent)}}
.hero{{display:grid;grid-template-columns:1.15fr .85fr;gap:30px;align-items:center;padding:54px 0 30px;border-bottom:1px solid var(--line2)}}
.kicker{{display:inline-flex;gap:8px;align-items:center;padding:6px 11px;border:1px solid var(--ink);border-radius:2px;background:var(--ink);color:var(--paper);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.13em}}
h1{{font-family:var(--disp);font-size:clamp(38px,6.6vw,74px);line-height:.96;letter-spacing:-.045em;margin:20px 0 18px;font-weight:700}}
.lead{{font-family:var(--serif);font-size:20px;line-height:1.62;color:var(--soft);max-width:660px}}
.muted{{color:var(--muted);font-family:var(--serif);line-height:1.6}}
.actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:26px}}
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:1px solid var(--ink);border-radius:3px;padding:13px 20px;font-family:var(--disp);font-weight:700;font-size:14px;background:var(--accent);color:#fff;cursor:pointer;text-transform:uppercase;letter-spacing:.03em;transition:transform .12s,box-shadow .12s;box-shadow:3px 3px 0 var(--ink)}}
.btn:hover{{transform:translate(-1px,-1px);box-shadow:5px 5px 0 var(--ink)}}
.btn.alt{{background:var(--card);color:var(--ink)}} .btn.dark{{background:var(--accent2);color:var(--paper)}}
.panel{{background:var(--card);border:1px solid var(--line2);border-radius:var(--r);box-shadow:var(--shadow);padding:24px}}
.glass{{background:var(--paper2);border:1px solid var(--line);border-radius:var(--r);padding:18px}}
.grid{{display:grid;grid-template-columns:repeat(12,1fr);gap:14px}}
.card{{grid-column:span 4;background:var(--card);border:1px solid var(--line2);border-radius:var(--r);padding:22px;box-shadow:var(--shadow)}}
.card.span6{{grid-column:span 6}} .card.span8{{grid-column:span 8}} .card.span12{{grid-column:span 12}} .card.span3{{grid-column:span 3}} .card.span4{{grid-column:span 4}}
.num{{font-family:var(--mono);font-size:40px;font-weight:700;letter-spacing:-.04em;font-variant-numeric:tabular-nums}}
.label{{color:var(--muted);margin-top:6px;font-size:12px;text-transform:uppercase;letter-spacing:.1em;font-weight:500}}
.h2{{font-family:var(--disp);font-size:27px;letter-spacing:-.035em;margin:0 0 14px;font-weight:700}}
.h3{{font-family:var(--disp);font-size:18px;letter-spacing:-.02em;margin:0 0 9px;font-weight:700;text-transform:uppercase}}
.small{{font-size:13px;color:var(--muted);line-height:1.6;font-family:var(--mono)}}
.tag{{display:inline-flex;align-items:center;gap:6px;background:var(--paper2);border:1px solid var(--line2);padding:5px 10px;border-radius:2px;color:var(--soft);font-size:12px;font-weight:500;font-family:var(--mono)}}
.tag.green{{background:#e7efe2;border-color:#b9cdb0;color:var(--green)}} .tag.yellow{{background:#f3ead2;border-color:#d8c189;color:var(--gold)}}
.section{{padding:34px 0}}
.flow{{display:grid;grid-template-columns:repeat(5,1fr);gap:0;border:1px solid var(--line2);border-radius:var(--r);overflow:hidden}}
.step{{background:var(--card);padding:18px;min-height:128px;border-right:1px solid var(--line2);position:relative}} .step:last-child{{border-right:0}}
.step b{{display:block;margin-bottom:9px;font-family:var(--disp);text-transform:uppercase;font-size:14px;letter-spacing:-.01em}}
.step::before{{content:counter(s,decimal-leading-zero);counter-increment:s;font-family:var(--mono);font-size:11px;color:var(--accent);position:absolute;top:14px;right:14px;font-weight:700}}
.flow{{counter-reset:s}}
.tabs{{display:flex;gap:0;flex-wrap:wrap;margin:20px 0;border-bottom:1px solid var(--line2)}}
.tab{{padding:11px 16px;border:0;border-bottom:2px solid transparent;background:none;cursor:pointer;color:var(--muted);font-family:var(--disp);font-weight:700;font-size:13px;text-transform:uppercase;letter-spacing:.03em}}
.tab.active{{color:var(--accent);border-bottom-color:var(--accent)}} .tabpage{{display:none}} .tabpage.active{{display:block}}
table{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line2);border-radius:var(--r);overflow:hidden}}
th,td{{padding:12px 13px;border-bottom:1px solid var(--line);text-align:left;font-size:13px;vertical-align:top;font-family:var(--mono)}}
th{{color:var(--ink);background:var(--paper2);text-transform:uppercase;font-size:11px;letter-spacing:.08em;font-weight:700}} td{{color:var(--soft)}} tr:last-child td{{border-bottom:0}} td a{{color:var(--accent);font-weight:700}}
.mock-phone{{max-width:380px;margin:0 auto;background:var(--accent2);border:1px solid var(--ink);border-radius:32px;padding:13px;box-shadow:8px 8px 0 var(--ink)}}
.screen{{border-radius:22px;background:var(--paper);min-height:540px;overflow:hidden;border:1px solid var(--line2)}}
.screen-head{{padding:18px;background:var(--ink);color:var(--paper);border-bottom:1px solid var(--ink)}}
.tile{{padding:14px;margin:12px;border-radius:4px;background:var(--card);border:1px solid var(--line2)}}
.thumbs{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}
.thumb{{aspect-ratio:4/5;border-radius:3px;background:var(--accent2);border:1px solid var(--ink);display:grid;place-items:center;color:var(--paper);font-family:var(--disp);font-weight:700}}
.check{{display:grid;gap:11px}} .check div{{display:flex;gap:10px;align-items:flex-start;color:var(--soft);font-family:var(--serif);font-size:15px}}
.dot{{width:7px;height:7px;border-radius:0;background:var(--accent);margin-top:8px;flex:0 0 auto;transform:rotate(45deg)}}
.footer{{border-top:1px solid var(--line2);margin-top:40px;padding-top:24px;color:var(--muted);font-size:12px;font-family:var(--mono);text-transform:uppercase;letter-spacing:.06em}}
@media(max-width:900px){{.hero{{grid-template-columns:1fr;padding:34px 0 22px}}.grid{{grid-template-columns:1fr}}.card,.card.span3,.card.span4,.card.span6,.card.span8,.card.span12{{grid-column:span 1}}.flow{{grid-template-columns:1fr}}.step{{border-right:0;border-bottom:1px solid var(--line2)}}.nav-links{{display:none}}}}
</style>
</head>
<body>
<div class="nav"><div class="nav-inner"><a class="logo" href="/"><span class="logo-badge">◢</span><span>IIComp&nbsp;Factory</span></a><div class="nav-links"><a href="/studio">Studio</a><a href="/pitch">Investors</a><a href="/mini">Mini&nbsp;App</a><a href="/health">Status</a></div></div></div>
<div class="wrap">{body}<div class="footer">IIComp AI Content Factory — Telegram · Web · Mini App — Railway / Supabase / fal.ai / Grok</div></div>
<script>
function showTab(name){{document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x.dataset.tab===name));document.querySelectorAll('.tabpage').forEach(x=>x.classList.toggle('active',x.id===name));}}
async function loadStudio(){{try{{const r=await fetch('/studio/api/overview');const d=await r.json();document.querySelectorAll('[data-stat]').forEach(el=>{{el.textContent=d.stats[el.dataset.stat]??'0'}});}}catch(e){{console.log(e)}}}}
if(location.pathname.includes('studio')) loadStudio();
</script>
</body></html>"""


def _kpi_cards(s: dict[str, int]) -> str:
    labels = [
        ("users", "Пользователи", "👥"),
        ("ai_models", "AI-модели", "🧬"),
        ("products", "Товары", "📦"),
        ("content_generations", "Генерации", "📸"),
        ("content_plans", "Контент-планы", "🧾"),
        ("payments", "Платежи", "💎"),
    ]
    return "".join([f"<div class='card span3'><div class='num'><span>{icon}</span> <span data-stat='{key}'>{s.get(key,0)}</span></div><div class='label'>{label}</div></div>" for key, label, icon in labels])


def _scenario_grid() -> str:
    groups = {
        "Instagram / lifestyle": ["утро в кафе", "городская прогулка", "зеркальное селфи", "hotel room", "street style", "UGC на телефон"],
        "Реклама товара": ["товар в руке", "товар на столе", "упаковка крупно", "до/после", "premium placement", "hero ad"],
        "Fashion": ["full body", "примерочная", "walking shot", "editorial pose", "outfit details", "luxury corridor"],
        "Beauty": ["крупный портрет", "skincare routine", "ванная", "нанесение крема", "perfume close-up", "glow skin"],
        "Видео / Reels": ["slow zoom", "product reveal", "UGC hook", "outfit spin", "unboxing", "cinematic push-in"],
        "Маркетплейсы": ["белый фон", "инфографика", "карточка 1:1", "до/после", "комплект кадров", "баннер"],
    }
    html_blocks = []
    for title, items in groups.items():
        chips = "".join([f"<span class='tag'>{_esc(i)}</span> " for i in items])
        html_blocks.append(f"<div class='card span6'><h3 class='h3'>{_esc(title)}</h3><div style='display:flex;gap:8px;flex-wrap:wrap'>{chips}</div></div>")
    return "".join(html_blocks)


@app.get("/health")
async def health():
    return {"ok": True, "service": "iicomp-ai-content-factory", "version": "10.0", "ts": datetime.utcnow().isoformat()}


@app.get("/", response_class=HTMLResponse)
async def landing():
    public = _public_url()
    admin_url = f"{public}/admin?token=YOUR_TOKEN" if public else "/admin?token=YOUR_TOKEN"
    body = f"""
    <section class='hero'>
      <div>
        <span class='kicker'>🚀 Investor demo ready · AI Content Factory</span>
        <h1>Контент-завод для AI-моделей, товаров и Reels</h1>
        <p class='lead'>IIComp создаёт виртуальную модель, загружает товар, генерирует рекламные фото, UGC, Reels и контент-планы. Один интерфейс для Instagram, маркетплейсов и performance-креативов.</p>
        <div class='actions'>
          <a class='btn' href='/studio'>Открыть Web App</a>
          <a class='btn alt' href='/pitch'>Показать инвесторам</a>
          <a class='btn alt' href='{_bot_link()}'>Открыть Telegram</a>
        </div>
      </div>
      <div class='mock-phone'><div class='screen'><div class='screen-head'><b>AI Campaign Builder</b><div class='small'>Модель + товар → фото → Reels → контент-план</div></div><div class='tile'><b>🧬 mira</b><div class='small'>Beauty / skincare · identity pack · hero face</div></div><div class='tile'><b>📦 ChocoPro</b><div class='small'>product-aware mode · strict/fast/try-on</div></div><div class='tile'><b>🎬 Reels 9:16</b><div class='small'>Wan I2V · 5/10/15 сек · motion prompt</div></div><div class='tile thumbs'><div class='thumb'>AI</div><div class='thumb'>AD</div><div class='thumb'>UGC</div></div></div></div>
    </section>
    <section class='grid'>{_kpi_cards(_stats())}</section>
    <section class='section'><h2 class='h2'>Как работает продукт</h2><div class='flow'>
      <div class='step'><b>1. AI-модель</b><span class='small'>Ниша, типаж, стиль, face DNA, hero portrait, identity pack.</span></div>
      <div class='step'><b>2. Товар</b><span class='small'>Фото упаковки, одежды, косметики, еды, аксессуара.</span></div>
      <div class='step'><b>3. Ad photo</b><span class='small'>Product-aware генерация: try-on, product shot, strict placement.</span></div>
      <div class='step'><b>4. Reels</b><span class='small'>Wan/Kling image-to-video, формат 9:16, motion сценарии.</span></div>
      <div class='step'><b>5. Campaign</b><span class='small'>Grok/Claude собирают план постов, хуки и CTA.</span></div>
    </div></section>
    <section class='section grid'>{_scenario_grid()}</section>
    """
    return HTMLResponse(_base("IIComp AI Content Factory", body))


@app.get("/pitch", response_class=HTMLResponse)
async def pitch():
    s = _stats()
    body = f"""
    <section class='hero'>
      <div><span class='kicker'>◢ Investor Brief</span><h1>Студия рекламного контента без съёмок</h1><p class='lead'>AI-модель, товар и сценарий превращаются в фото, Reels и UGC для брендов и маркетплейсов. Один пайплайн вместо студии, моделей и продакшена.</p><div class='actions'><a class='btn' href='/studio'>Живая демонстрация</a><a class='btn alt' href='{_bot_link()}'>Открыть в Telegram</a></div></div>
      <div class='panel'><h3 class='h3'>Сценарий показа · 5 минут</h3><div class='check'>
        <div><span class='dot'></span><span>Создать AI-модель под нишу бренда (30 сек).</span></div>
        <div><span class='dot'></span><span>Загрузить товар: тюбик, платье, бутылку.</span></div>
        <div><span class='dot'></span><span>Получить 3 рекламных кадра в разных стилях.</span></div>
        <div><span class='dot'></span><span>Собрать Reels 9:16 из лучшего кадра.</span></div>
        <div><span class='dot'></span><span>Открыть админку — всё сохранено в системе.</span></div>
      </div></div>
    </section>
    <section class='section'><h2 class='h2'>Трекшен на платформе</h2><div class='grid'>{_kpi_cards(s)}</div><p class='small' style='margin-top:14px'>Данные читаются вживую из Supabase в момент открытия страницы — это не мокап.</p></section>
    <section class='section grid'>
      <div class='card span6'><h3 class='h3'>Проблема</h3><p class='muted'>Перформанс-маркетингу нужны десятки креативов в неделю. Классическая съёмка — это модель, локация, фотограф, логистика и 1–3 недели на цикл. Не масштабируется и дорого на тест гипотез.</p></div>
      <div class='card span6'><h3 class='h3'>Решение</h3><p class='muted'>Контент-завод: виртуальная модель с постоянным лицом + фото товара + сценарий → готовый рекламный кадр, Reels и контент-план за минуты, без студии.</p></div>
      <div class='card span4'><h3 class='h3'>Кому продаём</h3><p class='muted'>Селлеры WB/Ozon, D2C-бренды, SMM-агентства, инфлюенс-команды. Боль и бюджет на контент уже есть.</p></div>
      <div class='card span4'><h3 class='h3'>Монетизация</h3><p class='muted'>Кредиты за генерацию, подписки Pro/Premium, пакеты кампаний, B2B-доступ для агентств и брендов.</p></div>
      <div class='card span4'><h3 class='h3'>Технологический ров</h3><p class='muted'>Product-aware пайплайн (товар не перерисовывается), стабильное лицо модели через identity DNA, Grok prompt engine, Wan I2V, try-on.</p></div>
      <div class='card span6'><h3 class='h3'>Стек</h3><p><span class='tag green'>fal.ai</span> <span class='tag'>FLUX LoRA</span> <span class='tag'>Wan I2V</span> <span class='tag'>FASHN try-on</span> <span class='tag'>Grok</span> <span class='tag'>Supabase</span> <span class='tag'>Railway</span> <span class='tag'>aiogram</span></p><p class='small' style='margin-top:10px'>Telegram-бот + Web Studio + Mini App на одной кодовой базе.</p></div>
      <div class='card span6'><h3 class='h3'>Roadmap</h3><div class='check'><div><span class='dot'></span><span>Сейчас: demo web, product-aware, Reels.</span></div><div><span class='dot'></span><span>Next: батч-кампании (серия креативов в один клик).</span></div><div><span class='dot'></span><span>Затем: персональная LoRA на модель бренда.</span></div><div><span class='dot'></span><span>B2B-кабинет команды и API для агентств.</span></div></div></div>
    </section>
    """
    return HTMLResponse(_base("IIComp · Investor Brief", body))


@app.get("/studio", response_class=HTMLResponse)
async def studio():
    s = _stats()
    models = _recent("ai_models", 6)
    products = _recent("products", 6)
    gens = _recent("content_generations", 8)
    body = f"""
    <section class='hero'>
      <div><span class='kicker'>🧠 Web Studio · demo для инвесторов</span><h1>Управляй контент-заводом из браузера</h1><p class='lead'>Веб-приложение показывает продукт как полноценную платформу: модели, товары, кампании, видео, качество и админ-аналитика.</p><div class='actions'><a class='btn' href='{_bot_link('mini_model')}'>Создать модель в Telegram</a><a class='btn alt' href='/pitch'>Investor Story</a></div></div>
      <div class='panel'><h2 class='h2'>Quick actions</h2><div class='actions'><a class='btn' href='{_bot_link('mini_model')}'>🧬 AI-модель</a><a class='btn alt' href='{_bot_link('mini_product')}'>📦 Товар</a><a class='btn alt' href='{_bot_link('mini_ads')}'>📸 Реклама</a><a class='btn alt' href='{_bot_link('mini_reels')}'>🎥 Reels</a></div></div>
    </section>
    <section class='grid'>{_kpi_cards(s)}</section>
    <div class='tabs'>
      <button class='tab active' data-tab='dash' onclick="showTab('dash')">🏠 Дашборд</button>
      <button class='tab' data-tab='models' onclick="showTab('models')">🧬 Модели</button>
      <button class='tab' data-tab='products' onclick="showTab('products')">📦 Товары</button>
      <button class='tab' data-tab='campaign' onclick="showTab('campaign')">📢 Кампания</button>
      <button class='tab' data-tab='video' onclick="showTab('video')">🎥 Видео Lab</button>
      <button class='tab' data-tab='quality' onclick="showTab('quality')">✨ Качество</button>
      <button class='tab' data-tab='admin' onclick="showTab('admin')">🛠 Admin</button>
    </div>
    <section id='dash' class='tabpage active section grid'>
      <div class='card span8'><h2 class='h2'>Pipeline</h2><div class='flow'><div class='step'><b>AI-модель</b><span class='small'>face DNA, identity pack</span></div><div class='step'><b>Товар</b><span class='small'>фото и категория</span></div><div class='step'><b>Фото</b><span class='small'>ad/lifestyle/UGC</span></div><div class='step'><b>Видео</b><span class='small'>Wan I2V</span></div><div class='step'><b>План</b><span class='small'>хуки, CTA, серия</span></div></div></div>
      <div class='card span4'><h2 class='h2'>Стек</h2><p><span class='tag green'>fal.ai</span> <span class='tag'>Wan I2V</span> <span class='tag'>Grok prompts</span> <span class='tag'>Supabase</span></p><p class='small'>Фото: { _esc(settings.fal_model) }<br>Видео: { _esc(settings.video_model_i2v) }<br>Качество: { _esc(settings.photo_quality_mode) }</p></div>
      <div class='card span12'><h2 class='h2'>Сценарии</h2><div class='grid'>{_scenario_grid()}</div></div>
    </section>
    <section id='models' class='tabpage section'><h2 class='h2'>AI-модели</h2><table><tr><th>ID</th><th>Имя</th><th>Ниша</th><th>Hero</th><th>Identity</th><th>Создано</th></tr>{_rows(models, ['id','name','niche','hero_image_url','identity_pack_json','created_at'])}</table></section>
    <section id='products' class='tabpage section'><h2 class='h2'>Товары</h2><table><tr><th>ID</th><th>Название</th><th>Категория</th><th>Фото</th><th>Описание</th><th>Создано</th></tr>{_rows(products, ['id','title','category','primary_image_url','description','created_at'])}</table></section>
    <section id='campaign' class='tabpage section grid'>
      <div class='card span6'><h2 class='h2'>Campaign Builder</h2><p class='muted'>Собери серию: 3 поста + 2 Reels + 3 hooks + CTA. Для инвестора это выглядит как полноценный B2B-инструмент.</p><div class='actions'><a class='btn' href='{_bot_link('mini_plan')}'>🧾 Сгенерировать план</a><a class='btn alt' href='{_bot_link('mini_ads')}'>📸 Сделать кадры</a></div></div>
      <div class='card span6'><h2 class='h2'>Готовые пакеты</h2><div class='check'><div><span class='dot'></span><span>Launch Pack: 5 кадров + 2 Reels</span></div><div><span class='dot'></span><span>UGC Pack: 10 коротких hooks</span></div><div><span class='dot'></span><span>Marketplace Pack: 6 карточек товара</span></div></div></div>
    </section>
    <section id='video' class='tabpage section grid'>
      <div class='card span4'><h2 class='h2'>Движение</h2><p><span class='tag'>slow zoom</span> <span class='tag'>product reveal</span> <span class='tag'>walk forward</span> <span class='tag'>outfit spin</span> <span class='tag'>UGC hook</span></p></div>
      <div class='card span4'><h2 class='h2'>Форматы</h2><p><span class='tag green'>9:16 Reels</span> <span class='tag'>4:5 feed</span> <span class='tag'>1:1 ads</span></p></div>
      <div class='card span4'><h2 class='h2'>Длина</h2><p><span class='tag'>5 сек</span> <span class='tag'>10 сек</span> <span class='tag'>15 сек</span></p></div>
    </section>
    <section id='quality' class='tabpage section grid'>
      <div class='card span6'><h2 class='h2'>Контроль качества</h2><div class='check'><div><span class='dot'></span><span>Натуральная кожа, не пластик</span></div><div><span class='dot'></span><span>Товар не перерисован</span></div><div><span class='dot'></span><span>Лицо модели не одинаковое у всех</span></div><div><span class='dot'></span><span>Руки, упаковка, композиция проходят QA</span></div></div></div>
      <div class='card span6'><h2 class='h2'>Настройки</h2><p class='small'>LORA_SCALE={settings.lora_scale}<br>INFERENCE_STEPS={settings.inference_steps}<br>GUIDANCE_SCALE={settings.guidance_scale}<br>PRODUCT_MODE={_esc(settings.product_composition_mode)}<br>TIMEOUT={settings.product_pipeline_timeout_sec}s</p></div>
    </section>
    <section id='admin' class='tabpage section'><h2 class='h2'>Последние генерации</h2><table><tr><th>ID</th><th>Тип</th><th>Сценарий</th><th>Статус</th><th>Формат</th><th>Фото</th><th>Видео</th><th>Создано</th></tr>{_rows(gens, ['id','content_type','scenario_key','status','format','image_url','video_url','created_at'])}</table></section>
    """
    return HTMLResponse(_base("IIComp Studio", body))


@app.get("/studio/api/overview")
async def studio_api_overview():
    return JSONResponse({
        "stats": _stats(),
        "models": _recent("ai_models", 8),
        "products": _recent("products", 8),
        "generations": _recent("content_generations", 8),
        "settings": {
            "image_model": settings.fal_model,
            "video_model": settings.video_model_i2v,
            "quality": settings.photo_quality_mode,
            "product_mode": settings.product_composition_mode,
        },
    })


@app.get("/admin", response_class=HTMLResponse)
async def admin(token: str | None = Query(default=None)):
    _check_token(token)
    s = _stats()
    gens = _recent("content_generations", 20)
    models = _recent("ai_models", 10)
    products = _recent("products", 10)
    public = _public_url()
    mini_url = f"{public}/mini" if public else "/mini"
    studio_url = f"{public}/studio" if public else "/studio"
    pitch_url = f"{public}/pitch" if public else "/pitch"
    api_url = f"/admin/api/stats?token={_esc(token or '')}"
    body = f"""
    <section class='hero'><div><span class='kicker'>🛠 Live admin</span><h1>Панель управления IIComp</h1><p class='lead'>Статистика, последние модели/товары/генерации, ссылки на web app, mini app и investor pitch.</p><div class='actions'><a class='btn' href='{studio_url}'>Studio</a><a class='btn alt' href='{mini_url}'>Mini App</a><a class='btn alt' href='{pitch_url}'>Investor</a><a class='btn alt' href='{api_url}'>API</a></div></div><div class='panel'><h2 class='h2'>Status</h2><p><span class='tag green'>online</span> <span class='tag'>Railway</span> <span class='tag'>Supabase</span></p><p class='small'>Image: {_esc(settings.fal_model)}<br>Video: {_esc(settings.video_model_i2v)}<br>Prompt: {_esc(settings.prompt_provider)}</p></div></section>
    <section class='grid'>{_kpi_cards(s)}</section>
    <section class='section'><h2 class='h2'>🔥 Последние генерации</h2><table><tr><th>ID</th><th>Тип</th><th>Сценарий</th><th>Статус</th><th>Формат</th><th>Фото</th><th>Видео</th><th>Создано</th></tr>{_rows(gens, ['id','content_type','scenario_key','status','format','image_url','video_url','created_at'])}</table></section>
    <section class='section grid'><div class='card span6'><h2 class='h2'>👤 Модели</h2><table><tr><th>ID</th><th>Имя</th><th>Ниша</th><th>Hero</th></tr>{_rows(models, ['id','name','niche','hero_image_url'])}</table></div><div class='card span6'><h2 class='h2'>📦 Товары</h2><table><tr><th>ID</th><th>Название</th><th>Категория</th><th>Фото</th></tr>{_rows(products, ['id','title','category','primary_image_url'])}</table></div></section>
    """
    return HTMLResponse(_base("IIComp Admin", body))


@app.get("/admin/api/stats")
async def admin_stats(token: str | None = Query(default=None)):
    _check_token(token)
    return JSONResponse({"stats": _stats(), "recent_generations": _recent("content_generations", 10), "models": _recent("ai_models", 8), "products": _recent("products", 8)})


@app.get("/mini", response_class=HTMLResponse)
async def mini(request: Request):
    body = f"""
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <section class='hero' style='padding-top:14px'><div><span class='kicker'>📲 Telegram Mini App</span><h1>AI Content Factory</h1><p class='lead'>Быстрые действия для создания модели, товара, рекламы и Reels.</p></div></section>
    <section class='grid'>
      <div class='card span6'><div class='num'>🧬</div><h2>AI-модель</h2><p class='muted'>Создать образ, hero face и identity pack.</p><a class='btn' href='{_bot_link('mini_model')}'>Создать</a></div>
      <div class='card span6'><div class='num'>📦</div><h2>Товар</h2><p class='muted'>Загрузить фото товара для рекламы.</p><a class='btn' href='{_bot_link('mini_product')}'>Загрузить</a></div>
      <div class='card span6'><div class='num'>📸</div><h2>Реклама</h2><p class='muted'>Product placement, UGC, lifestyle, marketplace.</p><a class='btn' href='{_bot_link('mini_ads')}'>Сделать кадр</a></div>
      <div class='card span6'><div class='num'>🎥</div><h2>Reels</h2><p class='muted'>Видео из готового кадра: 5/10/15 сек.</p><a class='btn' href='{_bot_link('mini_reels')}'>Сделать Reels</a></div>
      <div class='card span12'><div class='num'>🧾</div><h2>Контент-план</h2><p class='muted'>Идеи постов, хуки, CTA и серия под запуск.</p><a class='btn alt' href='{_bot_link('mini_plan')}'>Получить план</a></div>
    </section>
    <script>if(window.Telegram&&Telegram.WebApp){{Telegram.WebApp.ready();Telegram.WebApp.expand();Telegram.WebApp.MainButton.setText('Открыть бота');}}</script>
    """
    return HTMLResponse(_base("IIComp Mini App", body, compact=True))
