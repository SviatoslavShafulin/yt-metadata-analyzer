import asyncio
import os
import logging
from database import LocalCacheDB
from youtube_client import AsyncYouTubeClient

# Restrict verbose logging to errors only
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Academic test channels (e.g., tech, science, news)
TARGET_CHANNELS = [
    "UCXuqSBlHAE6Xw-yeJA0Tunw",  # Linus Tech Tips
    "UCsooa4yRKGN_zEE8iknghZA",  # TED-Ed
    "UCsXVk37bltHxD1rDPwtNM8Q"   # Kurzgesagt
]

async def process_channel(client: AsyncYouTubeClient, db: LocalCacheDB, channel_id: str) -> None:
    video_ids = await client.extract_channel_uploads(channel_id, max_results=50)
    
    if not video_ids:
        return

    raw_stats = await client.fetch_videos_batched(video_ids)
    
    # If None, it means 304 Not Modified caught by ETags
    if not raw_stats:
        return

    for item in raw_stats.get('items', []):
        vid_id = item.get('id')
        stats = item.get('statistics', {})
        if vid_id and stats:
            db.save_video_metrics(vid_id, stats)

async def main() -> None:
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logging.error("YOUTUBE_API_KEY environment variable is missing. Halting execution.")
        return

    db = LocalCacheDB()
    client = AsyncYouTubeClient(api_key=api_key, db=db)

    tasks = [process_channel(client, db, channel) for channel in TARGET_CHANNELS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
