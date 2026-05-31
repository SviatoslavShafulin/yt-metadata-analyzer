import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from database import LocalCacheDB

class AsyncYouTubeClient:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str, db: LocalCacheDB):
        self.api_key = api_key
        self.db = db

    async def fetch_videos_batched(self, video_ids: List[str]) -> Optional[Dict[str, Any]]:
        if not video_ids:
            return None

        # Google optimization: Max 50 IDs per batch
        if len(video_ids) > 50:
            logging.error("Batch size exceeds YouTube API limit of 50. Truncating.")
            video_ids = video_ids[:50]

        joined_ids = ",".join(video_ids)
        endpoint = f"{self.BASE_URL}/videos"
        params = {
            "part": "id,statistics",
            "id": joined_ids,
            "key": self.api_key
        }

        # ETag Cache validation
        request_url = f"{endpoint}?id={joined_ids}"
        cached_etag = self.db.get_etag(request_url)
        headers = {"If-None-Match": cached_etag} if cached_etag else {}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(endpoint, params=params, headers=headers) as response:
                    if response.status == 304:
                        return None  # Not modified, save quota

                    if response.status != 200:
                        error_text = await response.text()
                        logging.error(f"API Request Failed [{response.status}]: {error_text}")
                        return None

                    data = await response.json()
                    
                    if 'etag' in data:
                        self.db.save_etag(request_url, data['etag'])

                    return data
            except aiohttp.ClientError as e:
                logging.error(f"Network error during API call: {str(e)}")
                return None

    async def extract_channel_uploads(self, channel_id: str, max_results: int = 50) -> List[str]:
        endpoint = f"{self.BASE_URL}/search"
        params = {
            "part": "id",
            "channelId": channel_id,
            "maxResults": max_results,
            "order": "date",
            "type": "video",
            "key": self.api_key
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(endpoint, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logging.error(f"Search API Failed [{response.status}]: {error_text}")
                        return []

                    data = await response.json()
                    return [item['id']['videoId'] for item in data.get('items', []) if 'videoId' in item['id']]
            except aiohttp.ClientError as e:
                logging.error(f"Network error during Search API call: {str(e)}")
                return []
