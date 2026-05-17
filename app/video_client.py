"""Video generation client via fal.ai image-to-video.

v8 supports both old Kling-style endpoints and Wan I2V endpoints.
Wan 2.2 uses num_frames/fps/resolution parameters instead of simple duration.
"""
from __future__ import annotations

import logging
import os

import fal_client

from app.config import settings

log = logging.getLogger(__name__)
os.environ["FAL_KEY"] = settings.fal_key

VIDEO_NEGATIVE = (
    "face morphing, product deformation, label changes, unreadable logo, warped hands, "
    "flicker, unstable identity, melting objects, plastic skin, explicit content, low quality"
)


def _normalize_model(model: str) -> str:
    """fal endpoint IDs for Wan are namespaced under `fal-ai/`. The env/config
    often holds the short form (`wan/v2.2-a14b/image-to-video/lora`), which
    404s on fal. Normalize to the full endpoint ID. Kling/other endpoints that
    already carry their own prefix are left untouched."""
    m = (model or "").strip().strip("/")
    if m.startswith("wan/"):
        m = "fal-ai/" + m
    return m


def _video_model() -> str:
    # VIDEO_MODEL_I2V has priority, fallback to legacy FAL_VIDEO_MODEL.
    return _normalize_model(
        settings.video_model_i2v or settings.fal_video_model or "wan/v2.2-a14b/image-to-video/lora"
    )


def _alt_video_model() -> str:
    return _normalize_model(settings.video_model_i2v_alt or "")


def _wan_aspect(aspect_ratio: str) -> str:
    if aspect_ratio in {"9:16", "16:9", "1:1"}:
        return aspect_ratio
    # Wan doesn't support 4:5 directly. Vertical ad/Reels is the closest production output.
    if aspect_ratio == "4:5":
        return "9:16"
    return "auto"


def _wan_frames(duration: int) -> int:
    # Wan 2.2 accepts 17..161 frames. 16fps: 81 ~= 5s, 161 ~= 10s.
    # For 15s requests we cap at 161 for endpoint compatibility.
    duration = max(5, int(duration or 5))
    if duration <= 5:
        return 81
    if duration <= 10:
        return 161
    return 161


def _first_video_url(result: dict) -> str:
    video = result.get("video") or {}
    if isinstance(video, dict) and video.get("url"):
        return video["url"]
    videos = result.get("videos") or []
    if videos and isinstance(videos[0], dict) and videos[0].get("url"):
        return videos[0]["url"]
    for key in ("output", "result", "url"):
        value = result.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and value.get("url"):
            return value["url"]
    raise RuntimeError(f"fal.ai returned no video: {str(result)[:500]}")


async def generate_video_from_image(
    image_url: str,
    prompt: str | None = None,
    *,
    duration: int = 5,
    aspect_ratio: str = "9:16",
) -> str:
    """Generate a short video from a still image. Returns provider video URL."""
    video_prompt = prompt or (
        "subtle commercial motion, natural blinking, slight camera push-in, "
        "realistic social media video, brand-safe premium ad"
    )
    primary = _video_model()
    alt = _alt_video_model()
    # Try primary, then alt (if configured and different). This is what makes
    # video resilient: if Wan LoRA is overloaded/unavailable, we still ship a clip.
    candidates = [m for m in (primary, alt) if m]
    seen: set[str] = set()
    candidates = [m for m in candidates if not (m in seen or seen.add(m))]

    last_err: Exception | None = None
    for idx, model in enumerate(candidates):
        arguments = _build_args(model, image_url, video_prompt, duration, aspect_ratio)
        log.info(
            "fal.ai video run [%d/%d]: model=%s image=%s duration=%s aspect=%s",
            idx + 1, len(candidates), model, image_url[:80], duration, aspect_ratio,
        )
        try:
            result = await fal_client.subscribe_async(model, arguments=arguments, with_logs=False)
            return _first_video_url(result)
        except Exception as e:
            last_err = e
            log.warning("video model %s failed (%s); trying next", model, str(e)[:200])

    raise RuntimeError(f"all video models failed: {str(last_err)[:300]}")


def _build_args(model: str, image_url: str, video_prompt: str, duration: int, aspect_ratio: str) -> dict:
    model_l = model.lower()
    if "wan/" in model_l:
        return {
            "image_url": image_url,
            "prompt": video_prompt,
            "negative_prompt": VIDEO_NEGATIVE,
            "num_frames": _wan_frames(duration),
            "frames_per_second": 16,
            "resolution": "720p",
            "aspect_ratio": _wan_aspect(aspect_ratio),
            "num_inference_steps": 27,
            "enable_safety_checker": settings.enable_safety_checker,
            "enable_output_safety_checker": True,
            "enable_prompt_expansion": False,
            "acceleration": "regular",
            "guidance_scale": 3.3,
            "guidance_scale_2": 3.5,
            "video_quality": "high",
            "video_write_mode": "balanced",
        }
    # Kling / Seedance / other simple I2V endpoints usually accept duration/aspect_ratio.
    return {
        "image_url": image_url,
        "prompt": video_prompt,
        "duration": str(duration),
        "aspect_ratio": aspect_ratio,
    }
