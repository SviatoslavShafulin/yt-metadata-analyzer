import sqlite3
import logging
import json
from typing import Dict, Optional, Any

class LocalCacheDB:
    def __init__(self, db_path: str = "yt_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS etag_cache (
                endpoint_url TEXT PRIMARY KEY,
                etag_value TEXT,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_stats (
                video_id TEXT PRIMARY KEY,
                metrics JSON,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def get_etag(self, endpoint_url: str) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT etag_value FROM etag_cache WHERE endpoint_url = ?', (endpoint_url,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def save_etag(self, endpoint_url: str, etag_value: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO etag_cache (endpoint_url, etag_value) 
            VALUES (?, ?)
            ON CONFLICT(endpoint_url) DO UPDATE SET 
                etag_value = excluded.etag_value,
                last_checked = CURRENT_TIMESTAMP
        ''', (endpoint_url, etag_value))
        conn.commit()
        conn.close()

    def save_video_metrics(self, video_id: str, metrics: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        metrics_json = json.dumps(metrics)
        cursor.execute('''
            INSERT INTO video_stats (video_id, metrics) 
            VALUES (?, ?)
            ON CONFLICT(video_id) DO UPDATE SET 
                metrics = excluded.metrics,
                updated_at = CURRENT_TIMESTAMP
        ''', (video_id, metrics_json))
        conn.commit()
        conn.close()
