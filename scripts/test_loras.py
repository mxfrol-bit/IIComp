"""Compare 3 LoRA candidates on the same prompts.

Usage:
    python -m scripts.test_loras

Outputs to: ./lora_comparison/<lora_name>/<scene>.jpg
After it finishes — open the folder and visually compare.
"""
import asyncio
import os
import time
from pathlib import Path

import fal_client
import httpx

from app.config import settings

# Set fal key
os.environ["FAL_KEY"] = settings.fal_key

OUTPUT_DIR = Path("lora_comparison")

# Three candidates
CANDIDATES = [
    {
        "name": "1_super_realism",
        "model": "fal-ai/flux-lora",
        "lora_url": "https://huggingface.co/strangerzonehf/Flux-Super-Realism-LoRA/resolve/main/super-realism.safetensors",
        "lora_scale": 0.9,
    },
    {
        "name": "2_xlabs_realism",
        "model": "fal-ai/flux-lora",
        "lora_url": "https://huggingface.co/XLabs-AI/flux-RealismLora/resolve/main/lora.safetensors",
        "lora_scale": 0.9,
    },
    {
        "name": "3_no_lora_flux_realism",
        "model": "fal-ai/flux/dev",  # base Flux without LoRA — for baseline comparison
        "lora_url": None,
        "lora_scale": 0,
    },
]

# Anna persona (matches content/season_anna_pilot.json)
PERSONA = (
    "26 years old, long brown hair with soft waves, "
    "warm brown eyes, light freckles, gentle smile, "
    "slim build, beige sweater, vintage jeans, minimalist style"
)

# Triggers + tail (same as in app/presets.py)
BASE_TRIGGERS = "amateurish photo, low lighting, shot on iPhone, slightly noisy"
QUALITY_TAIL = "natural skin texture, candid moment, soft daylight, depth of field"

# 5 reference scenes that cover episode 1 + extra stress-tests
SCENES = [
    ("01_cafe", "in a cozy cafe by the window, holding a coffee mug, looking out at the rain, soft afternoon light"),
    ("02_evening_walk", "walking on a wet city street at evening, autumn coat, leaves on pavement, golden hour light, candid"),
    ("03_morning_bed", "selfie lying in bed in the morning, messy hair, white sheets, sleepy smile, soft window light"),
    ("04_gym_mirror", "mirror selfie in a gym, sportswear, post-workout glow, casual"),
    ("05_park_bench", "sitting on a bench in a park, holding a book, dappled sunlight"),
]

# Fixed seed across all models — so we compare LoRA effect, not seed variance
FIXED_SEED = 1714283


async def generate_one(candidate: dict, scene_key: str, scene_text: str) -> str:
    prompt = f"{BASE_TRIGGERS}, {PERSONA}, {scene_text}, {QUALITY_TAIL}"

    arguments = {
        "prompt": prompt,
        "image_size": "portrait_4_3",
        "num_inference_steps": 40,
        "guidance_scale": 2.5,
        "seed": FIXED_SEED,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "jpeg",
    }
    if candidate["lora_url"]:
        arguments["loras"] = [{
            "path": candidate["lora_url"],
            "scale": candidate["lora_scale"],
        }]

    print(f"  [{candidate['name']}] {scene_key}: generating...")
    result = await fal_client.subscribe_async(
        candidate["model"],
        arguments=arguments,
        with_logs=False,
    )

    images = result.get("images") or []
    if not images:
        raise RuntimeError(f"No images: {result}")
    return images[0]["url"]


async def download(url: str, dest: Path) -> None:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(url)
        r.raise_for_status()
        dest.write_bytes(r.content)


async def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Output: {OUTPUT_DIR.resolve()}\n")

    total = len(CANDIDATES) * len(SCENES)
    done = 0

    for cand in CANDIDATES:
        cand_dir = OUTPUT_DIR / cand["name"]
        cand_dir.mkdir(exist_ok=True)
        print(f"\n=== {cand['name']} ===")

        for scene_key, scene_text in SCENES:
            done += 1
            try:
                url = await generate_one(cand, scene_key, scene_text)
                dest = cand_dir / f"{scene_key}.jpg"
                await download(url, dest)
                print(f"  ✅ ({done}/{total}) {dest}")
            except Exception as e:
                print(f"  ❌ ({done}/{total}) {cand['name']}/{scene_key}: {e}")
            # small breather between requests
            await asyncio.sleep(1)

    print(f"\n✨ Done. Open {OUTPUT_DIR.resolve()} and compare side-by-side.")
    print("\nFolders:")
    for cand in CANDIDATES:
        print(f"  {OUTPUT_DIR / cand['name']}")


if __name__ == "__main__":
    asyncio.run(main())
