#!/usr/bin/env python3
"""
bones/main.py
Autonomous Data Collector with Redis queue integration, heartbeat logging, and retries.
"""

import os
import time
import random
import traceback
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests

# ------------------------------
# Load environment and config
# ------------------------------
load_dotenv()
TREND_KEYWORDS = os.getenv("TREND_KEYWORDS", "python,ai").split(",")
FETCH_INTERVAL = int(os.getenv("BONES_FETCH_INTERVAL", 600))  # default 10 min

BLOOD_URLS = {
    "google_trends": os.getenv("BLOOD_GOOGLE_ENDPOINT", "http://blood:8000/save_trends"),
    "ollama_trends": os.getenv("BLOOD_OLLAMA_ENDPOINT", "http://blood:8000/save_ollama"),
    "twitter": os.getenv("BLOOD_TWITTER_ENDPOINT", "http://blood:8000/save_tweets"),
    "search_results": os.getenv("BLOOD_SEARCH_ENDPOINT", "http://blood:8000/save_search")
}

# ------------------------------
# Internal modules
# ------------------------------
from heartbeat_logger import log_heartbeat, supabase
from trends_fetcher import fetch_google_trends, save_to_supabase, fetch_ollama_trends
from twitter_helper import search_tweets, save_tweets_to_supabase
from coingecko_helper import get_trending_coins
from your_google_script import fetch_search_results, save_results_to_supabase
from generate_content import generate_content
from redis_manager import add_to_queue, pop_from_queue, cleanup

# ------------------------------
# Retry wrapper
# ------------------------------
def retry(func, max_attempts=3, delay=5, *args, **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            log_heartbeat("success", f"{func.__name__} succeeded on attempt {attempt}", retries=attempt-1)
            return result
        except Exception as e:
            log_heartbeat("error", f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}", retries=attempt)
            if attempt < max_attempts:
                time.sleep(delay + random.uniform(0, 2))
            else:
                log_heartbeat("failure", f"{func.__name__} permanently failed: {e}", retries=max_attempts)
                raise e

# ------------------------------
# Push to Blood with retry
# ------------------------------
def push_to_blood(data, endpoint):
    def _push():
        requests.post(endpoint, json={"data": data})
    retry(_push, max_attempts=3, delay=5)

# ------------------------------
# Seed content if empty
# ------------------------------
def seed_content_if_empty():
    try:
        resp = supabase.table("content_performance").select("*").limit(1).execute()
        if not resp.data:
            log_heartbeat("info", "Seeding initial content...")
            for kw in ["bitcoin", "ethereum", "zk rollup", "AI", "python"]:
                prompt = f"Generate content about '{kw}' prioritizing Google trends."
                try:
                    retry(generate_content, 3, 5, prompt)
                    log_heartbeat("success", f"Seeded content for '{kw}'")
                except Exception as e:
                    log_heartbeat("error", f"Seeding failed for '{kw}': {e}")
    except Exception as e:
        log_heartbeat("error", f"Seed check failed: {e}")

# ------------------------------
# Build adaptive prompts
# ------------------------------
def build_prompt(keyword, source, weights):
    weight = weights.get(source, 1.0)
    return f"Generate content about '{keyword}'. Prioritize insights from {source} with weight {weight:.2f}."

# ------------------------------
# Retry queued content
# ------------------------------
def retry_queued_content():
    while True:
        item = pop_from_queue("content_queue")
        if not item:
            break
        try:
            retry(generate_content, 3, 5, item["prompt"])
            log_heartbeat("success", f"Processed queued content for '{item['keyword']}'")
        except Exception as e:
            add_to_queue("content_queue", item)
            log_heartbeat("error", f"Retry failed for queued content '{item['keyword']}': {e}")

# ------------------------------
# Main fetch & push cycle
# ------------------------------
def run_cycle():
    try:
        seed_content_if_empty()
        cleanup()

        # Fetch trending keywords
        keywords = get_trending_coins()[:3] + ["bitcoin", "zk rollup"]
        weights_resp = supabase.table("prompt_weights").select("*").execute()
        weights_dict = {item["source"]: item["weight"] for item in (weights_resp.data or [])}
        sources = ["Twitter", "Google", "Reddit", "Medium"]

        # --- Google Trends ---
        try:
            google_trends = retry(fetch_google_trends, 3, 5, TREND_KEYWORDS)
            if not google_trends.empty:
                save_to_supabase(google_trends, table_name="google_trends")
                push_to_blood(google_trends.to_dict(orient="records"), BLOOD_URLS["google_trends"])
                log_heartbeat("success", f"Fetched and pushed {len(google_trends)} Google Trends")
        except Exception as e:
            log_heartbeat("error", f"Google Trends cycle failed: {e}")

        # --- Ollama Trends ---
        try:
            ollama_trends = retry(fetch_ollama_trends, 3, 5)
            if not ollama_trends.empty:
                save_to_supabase(ollama_trends, table_name="ollama_trends")
                push_to_blood(ollama_trends.to_dict(orient="records"), BLOOD_URLS["ollama_trends"])
                log_heartbeat("success", f"Fetched and pushed {len(ollama_trends)} Ollama Trends")
        except Exception as e:
            log_heartbeat("error", f"Ollama Trends cycle failed: {e}")

        # --- Keyword loop ---
        for kw in keywords:
            # Twitter
            try:
                tweets = retry(search_tweets, 3, 5, kw)
                save_tweets_to_supabase(tweets)
                push_to_blood([t.to_dict() for t in tweets], BLOOD_URLS["twitter"])
            except Exception as e:
                log_heartbeat("error", f"Twitter fetch/save failed for '{kw}': {e}")

            # Google search
            try:
                results = retry(fetch_search_results, 3, 5, kw)
                save_results_to_supabase(results, kw)
                push_to_blood(results, BLOOD_URLS["search_results"])
            except Exception as e:
                log_heartbeat("error", f"Google search fetch/save failed for '{kw}': {e}")

            # Adaptive prompt & queue
            selected_source = random.choices(sources, weights=[weights_dict.get(s, 1.0) for s in sources], k=1)[0]
            prompt = build_prompt(kw, selected_source, weights_dict)
            add_to_queue("content_queue", {"keyword": kw, "prompt": prompt})
            log_heartbeat("info", f"Queued content prompt for '{kw}'")

        # Retry queued content
        retry_queued_content()

        log_heartbeat("success", "Cycle completed successfully.")
    except Exception as e:
        tb = traceback.format_exc()
        log_heartbeat("fatal", f"Main cycle crashed: {e}\n{tb}")

# ------------------------------
# Continuous loop
# ------------------------------
def main_loop():
    print(f"🦴 bones autonomous collector started (interval: {FETCH_INTERVAL}s)")
    while True:
        start_time = datetime.now(timezone.utc).isoformat()
        log_heartbeat("info", f"Starting cycle at {start_time}")
        run_cycle()
        log_heartbeat("info", f"Cycle completed. Sleeping for {FETCH_INTERVAL} seconds.")
        time.sleep(FETCH_INTERVAL)

# ------------------------------
# Entrypoint
# ------------------------------
if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        log_heartbeat("info", "bones manually stopped via KeyboardInterrupt.")
    except Exception as e:
        tb = traceback.format_exc()
        log_heartbeat("fatal", f"bones crashed unexpectedly: {e}\n{tb}")
        raise
