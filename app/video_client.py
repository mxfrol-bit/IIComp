"""Video generation client via fal.ai image-to-video."""
import logging
import os

import fal_client

from app.config import settings

log = logging.getLogger(__name__)
os.environ["FAL_KEY"] = settings.fal_key


async def generate_video_from_image(image_url: str, prompt: str | None = None) -> str:
    """Generate a short video from a still image. Returns provider video URL."""
    video_prompt = prompt or (
        "subtle cinematic movement, natural blinking, slight camera push-in, "
        "soft hair movement, realistic phone video, tasteful romantic mood"
    )
    arguments = {
        "image_url": image_url,
        "prompt": video_prompt,
        "duration": "5",
        "aspect_ratio": "9:16",
    }
    log.info("fal.ai video run: model=%s image=%s", settings.fal_video_model, image_url[:80])
    result = await fal_client.subscribe_async(
        settings.fal_video_model,
        arguments=arguments,
        with_logs=False,
    )
    video = result.get("video") or {}
    if video.get("url"):
        return video["url"]
    videos = result.get("videos") or []
    if videos and videos[0].get("url"):
        return videos[0]["url"]
    raise RuntimeError(f"fal.ai returned no video: {result}")
