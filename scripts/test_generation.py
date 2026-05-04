"""Smoke test: run a single generation against Replicate and save locally.

Usage:
    python -m scripts.test_generation
"""
import asyncio
from pathlib import Path

import httpx

from app.image_client import generate_image


async def main() -> None:
    prompt = (
        "amateurish photo, low lighting, shot on iPhone, slightly noisy, "
        "23-26 years old, long brown hair, athletic build, casual student style, "
        "sitting in a cafe by the window, laptop on table, warm afternoon light, "
        "natural skin texture, candid moment, soft daylight, depth of field"
    )
    print("Generating…")
    url = await generate_image(prompt=prompt, seed=42)
    print(f"Got URL: {url}")

    out = Path("test_output.jpg")
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        out.write_bytes(resp.content)
    print(f"Saved to: {out.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
