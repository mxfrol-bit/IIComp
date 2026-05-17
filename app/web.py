from __future__ import annotations

import html
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.config import settings
from app.db import supabase

app = FastAPI(title="AI Content Factory", version="5.0")


def _check_token(token: str | None) -> None:
    expected = settings.admin_web_token
    if not expected:
        raise HTTPException(403, "ADMIN_WEB_TOKEN is not configured in Railway")
    if token != expected:
        raise HTTPException(403, "Bad admin token")


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


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(title)}</title>
<style>
:root {{ color-scheme: dark; --bg:#080d16; --panel:#111827; --panel2:#172033; --text:#e8eefc; --muted:#91a0bb; --brand:#7c5cff; --ok:#28d17c; --warn:#ffbd4a; --line:rgba(255,255,255,.08); }}
*{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at top left,#172554 0,#080d16 38%,#050812 100%);font-family:Inter,system-ui,-apple-system,Segoe UI,Arial,sans-serif;color:var(--text)}}
a{{color:inherit}} .wrap{{max-width:1180px;margin:0 auto;padding:28px 18px 80px}} .hero{{display:flex;align-items:flex-start;justify-content:space-between;gap:18px;margin-bottom:22px}} .h1{{font-size:34px;font-weight:900;letter-spacing:-.04em;margin:0}} .sub{{color:var(--muted);margin-top:8px;line-height:1.55}} .pill{{display:inline-flex;gap:8px;align-items:center;border:1px solid var(--line);background:rgba(255,255,255,.05);padding:10px 14px;border-radius:999px;color:#c9d5ee;font-size:14px}} .grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:14px}} .card{{grid-column:span 2;background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.035));border:1px solid var(--line);border-radius:24px;padding:20px;box-shadow:0 18px 70px rgba(0,0,0,.22)}} .card.big{{grid-column:span 3}} .num{{font-size:38px;font-weight:900;letter-spacing:-.04em}} .label{{color:var(--muted);margin-top:4px}} .section{{margin-top:18px}} .section h2{{font-size:22px;margin:0 0 12px}} table{{width:100%;border-collapse:collapse;overflow:hidden;border-radius:18px;background:rgba(255,255,255,.035);border:1px solid var(--line)}} th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left;font-size:14px;vertical-align:top}} th{{color:#d8e1f7;background:rgba(255,255,255,.05)}} td{{color:#c9d5ee}} .btn{{display:inline-flex;border:0;text-decoration:none;background:linear-gradient(135deg,#7c5cff,#00d4ff);padding:12px 16px;border-radius:14px;font-weight:800;color:white}} .btn2{{background:rgba(255,255,255,.07);border:1px solid var(--line)}} .tag{{display:inline-block;padding:4px 8px;border-radius:999px;background:rgba(124,92,255,.18);color:#d8d2ff;font-size:12px}} @media(max-width:850px){{.grid{{grid-template-columns:1fr}}.card,.card.big{{grid-column:span 1}}.hero{{display:block}}}}
</style>
</head>
<body><div class="wrap">{body}</div></body></html>"""


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
            text = html.escape(str(val or ""))[:220]
            tds.append(f"<td>{text}</td>")
        out.append("<tr>" + "".join(tds) + "</tr>")
    return "".join(out)


@app.get("/health")
async def health():
    return {"ok": True, "service": "ai-content-factory", "ts": datetime.utcnow().isoformat()}


@app.get("/admin", response_class=HTMLResponse)
async def admin(token: str | None = Query(default=None)):
    _check_token(token)
    s = _stats()
    gens = _recent("content_generations", 12)
    models = _recent("ai_models", 8)
    products = _recent("products", 8)
    public = (settings.web_public_url or "").rstrip("/")
    mini_url = f"{public}/mini" if public else "/mini"
    api_url = f"/admin/api/stats?token={html.escape(token or '')}"
    body = f"""
    <div class="hero">
      <div><h1 class="h1">🏭 AI Content Factory Admin</h1><div class="sub">Панель контроля MVP: модели, товары, генерации, качество, Mini App.</div></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="{mini_url}">📲 Mini App</a><a class="btn btn2" href="{api_url}">API stats</a></div>
    </div>
    <div class="grid">
      <div class="card"><div class="num">{s['users']}</div><div class="label">Пользователи</div></div>
      <div class="card"><div class="num">{s['ai_models']}</div><div class="label">AI-модели</div></div>
      <div class="card"><div class="num">{s['products']}</div><div class="label">Товары</div></div>
      <div class="card"><div class="num">{s['content_generations']}</div><div class="label">Генерации</div></div>
      <div class="card"><div class="num">{s['content_plans']}</div><div class="label">Контент-планы</div></div>
      <div class="card"><div class="num">{s['payments']}</div><div class="label">Платежи</div></div>
    </div>
    <div class="section"><h2>🔥 Последние генерации</h2><table><tr><th>ID</th><th>Тип</th><th>Сценарий</th><th>Статус</th><th>Формат</th><th>Создано</th></tr>{_rows(gens, ['id','content_type','scenario_key','status','format','created_at'])}</table></div>
    <div class="section"><h2>👤 Последние модели</h2><table><tr><th>ID</th><th>Имя</th><th>Ниша</th><th>Hero</th><th>Создано</th></tr>{_rows(models, ['id','name','niche','hero_image_url','created_at'])}</table></div>
    <div class="section"><h2>📦 Последние товары</h2><table><tr><th>ID</th><th>Название</th><th>Категория</th><th>Описание</th><th>Создано</th></tr>{_rows(products, ['id','title','category','description','created_at'])}</table></div>
    <div class="section"><div class="card big"><b>⚙️ Quality mode:</b> <span class="tag">{html.escape(settings.photo_quality_mode)}</span><br><br>Для продажи продукта держи PHOTO_QUALITY_MODE=pro или max, PRODUCT_AWARE_MODE=true, bucket generations публичный.</div></div>
    """
    return HTMLResponse(_page("AI Content Factory Admin", body))


@app.get("/admin/api/stats")
async def admin_stats(token: str | None = Query(default=None)):
    _check_token(token)
    return JSONResponse({"stats": _stats(), "recent_generations": _recent("content_generations", 5)})


@app.get("/mini", response_class=HTMLResponse)
async def mini(request: Request):
    bot = "MYAICOM_bot"
    body = f"""
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <div class="hero"><div><h1 class="h1">AI Content Factory</h1><div class="sub">Создавай AI-модель, загружай товар и собирай рекламный контент для Instagram, Reels и Ads.</div></div></div>
    <div class="grid">
      <div class="card big"><div class="num">🧬</div><h2>AI-модель</h2><p class="sub">Hero portrait, identity pack, стабильный образ для кампаний.</p><a class="btn" href="https://t.me/{bot}?start=mini_model">Создать модель</a></div>
      <div class="card big"><div class="num">📦</div><h2>Товар</h2><p class="sub">Платье, бутылка, шоколад, косметика, аксессуар — загрузи фото и сделай рекламу.</p><a class="btn" href="https://t.me/{bot}?start=mini_product">Добавить товар</a></div>
      <div class="card big"><div class="num">📸</div><h2>Ad photos</h2><p class="sub">Lifestyle, fashion, product placement, studio, UGC, beauty.</p><a class="btn" href="https://t.me/{bot}?start=mini_ads">Генерировать</a></div>
      <div class="card big"><div class="num">🎥</div><h2>Reels</h2><p class="sub">Видео из готового кадра: 5/10/15 сек, 9:16, 4:5, 1:1.</p><a class="btn" href="https://t.me/{bot}?start=mini_reels">Сделать Reels</a></div>
    </div>
    <script>if(window.Telegram&&Telegram.WebApp){{Telegram.WebApp.ready();Telegram.WebApp.expand();}}</script>
    """
    return HTMLResponse(_page("AI Content Factory Mini App", body))
