# YouTube Metadata Analyzer

This repository houses the core data aggregation service for my final-year Computer Science qualification work. I'm a university student based in Ukraine. Given the ongoing war, continuing my education and completing my diploma project requires operating under unpredictable infrastructural constraints. 

To account for this, I built a headless Python service designed to systematically sample and track historical YouTube metadata to build longitudinal datasets for academic trend analysis. It monitors shifts in upload frequencies, tag clustering, and viewer engagement across a defined cohort of channels over time, requiring zero manual oversight.

## Technical Architecture

This service runs on the backend to pull daily metrics automatically. I built it to respect network resources and API rate limits, strictly adhering to Google's quota optimization guidelines.

* **Asynchronous I/O:** Uses `asyncio` and `aiohttp` for non-blocking concurrent requests.
* **Strict Batching:** Groups targets and maxes out the `videos.list` endpoint at exactly 50 IDs per call. I never request single videos.
* **Payload Minimization:** Restricts API responses via the `part` parameter. The script requests only `id` and `statistics` to minimize byte payloads over the wire.
* **ETag Caching:** Implements local SQLite caching to store `ETag` headers for every endpoint URL. The service passes `If-None-Match` on subsequent runs and accepts `304 Not Modified` responses to prevent redundant data transfer.

## Quota Requirements

The default 10,000 unit daily limit breaks the data collection. 

Discovering new uploads across an academic cohort requires paginating through the `search.list` endpoint, which costs 100 units per page. Analyzing a control group of just 5 channels drains the default limit within the first execution cycle. This project requires an extended quota of 250,000 units to process its daily target queues without hitting a 403 ceiling and halting my thesis research.

## Installation & Execution

Clone the repository and install the standard dependencies.

    git clone https://github.com/SviatoslavShafulin/yt-metadata-analyzer.git
    cd yt-metadata-analyzer
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

You must supply your own Google Cloud credentials. Set the environment variable before execution.

    export YOUTUBE_API_KEY="your_api_key_here"
    python3 main.py

## Privacy

This script uses YouTube API Services. By running this software, you agree to the Google Privacy Policy at http://www.google.com/policies/privacy. We store no user data.
