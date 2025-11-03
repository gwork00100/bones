#!/usr/bin/env python3
"""
bones/main.py
Autonomous Data Collector for the "bones → nerves → blood" architecture.

Continuously fetches new data (trends, tweets, coins, search results),
logs operational heartbeats, and seeds content automatically if needed.
"""

import os
import time
import random
import traceback
from datetime import datetime, timezone
from dotenv import load_dotenv
import pandas as pd

# ------------------------------
# Load environment and config
# ------------------------------
load_dotenv()
TREND_KEYWORDS = os.getenv("TREND_KEYWORDS", "python,ai").split(",")
FETCH_INTERVAL = int(os.getenv("BONES_FETCH_INTERVAL", 600))  # seconds (default 10 min)

# ------------------------------
# Imports (internal modules)
# ------------------------------
from heartbeat_logger import log_heartbeat, supabase
from trends_fetcher import fetch_google_trends, save_to_supabase, fetch_ollama_trends
from twitter_helper import search_tweets, save_tweets_to_supabase
from coingecko_helper import get_trending_coins
from your_google_script import fetch_search_results, save_results_to_supabase
from generate_content import generate_content

# ============================================================
# Retry wrapper with persistent heartbeat logging
# ============================================================
def retry(func, max_attempts=3, delay=5, *args, **kwargs):
    """
    Retry a function up to max_attempts with a delay between attempts.
    Logs each attempt to Supabase heartbeat table.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            log_heartbeat("success", f"{func.__name__} succeeded on attempt {attempt}", retries=attempt-1)
            return result
        except Exception as e:
            log_heartbeat("error", f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}", retries=attempt)
            if attempt < max_attempts:
                time.sleep(delay)
            else:
                log_heartbeat("failure", f"{func.__name__} permanently failed after {max_attempts} attempts: {e}", retries=max_attempts)
                raise e

# ============================================================
# Seed content if empty
# ============================================================
def seed_content_if_empty():
    """Seed initial content in Supabase if table is empty."""
    try:
        resp = supabase.table("content_performance").select("*").limit(1).execute()
        if not resp.data:
            log_heartbeat("info", "Seeding initial content...")
            initial_keywords = ["bitcoin", "ethereum", "zk rollup", "AI", "python"]
            for kw in initial_keywords:
                prompt = f"Generate content about '{kw}' prioritizing Google trends."
                try:
                    retry(generate_content, 3, 5, prompt)
                    log_heartbeat("success", f"Seeded content for '{kw}'")
                except Exception as e:
                    log_heartbeat("error", f"Seeding failed for '{kw}': {e}")
    except Exception as e:
        log_heartbeat("error", f"Seed check failed: {e}")

# ============================================================
# Dynamic prompt builder
# ============================================================
def build_prompt(keyword, source, weights):
    """Construct a context-aware generation prompt."""
    weight = weights.get(source, 1.0)
    return f"Generate content about '{keyword}'. Prioritize insights from {source} with weight {weight:.2f}."

# ============================================================
# Main processing cycle
# ============================================================
def run_cycle():
    """Run a full autonomous data fetch + generation cycle."""
    try:
        # --- Seed content if first run ---
        seed_content_if_empty()

        # --- Get trending keywords ---
        keywords = get_trending_coins()[:3] + ["bitcoin", "zk rollup"]

        # --- Load adaptive weights ---
        weights_resp = supabase.table("prompt_weights").select("*").execute()
        weights_dict = {item["source"]: item["weight"] for item in (weights_resp.data or [])}
        sources = ["Twitter", "Google", "Reddit", "Medium"]

        # --- Fetch and save Google Trends ---
        try:
            google_trends = retry(fetch_google_trends, 3, 5, TREND_KEYWORDS)
            if not google_trends.empty:
                save_to_supabase(google_trends, table_name="google_trends")
                log_heartbeat("success", f"Fetched and saved {len(google_trends)} Google Trends.")
        except Exception as e:
            log_heartbeat("error", f"Failed Google Trends after retries: {e}")

        # --- Fetch and save Ollama Trends ---
        try:
            ollama_trends = retry(fetch_ollama_trends, 3, 5)
            if not ollama_trends.empty:
                save_to_supabase(ollama_trends, table_name="ollama_trends")
                log_heartbeat("success", f"Fetched and saved {len(ollama_trends)} Ollama Trends.")
        except Exception as e:
            log_heartbeat("error", f"Failed Ollama Trends after retries: {e}")

        # --- Main keyword loop ---
        for kw in keywords:
            # Twitter
            try:
                tweets = retry(search_tweets, 3, 5, kw)
                save_tweets_to_supabase(tweets)
            except Exception as e:
                log_heartbeat("error", f"Twitter fetch/save failed for '{kw}' after retries: {e}")

            # Google Search
            try:
                results = retry(fetch_search_results, 3, 5, kw)
                save_results_to_supabase(results, kw)
            except Exception as e:
                log_heartbeat("error", f"Google search fetch/save failed for '{kw}' after retries: {e}")

            # Adaptive prompt
            source_weights = [weights_dict.get(src, 1.0) for src in sources]
            selected_source = random.choices(sources, weights=source_weights, k=1)[0]
            prompt = build_prompt(kw, selected_source, weights_dict)
            print(f"📝 Generated prompt: {prompt}")

            # Content Generation
            try:
                retry(generate_content, 3, 5, prompt)
            except Exception as e:
                log_heartbeat("error", f"LLM content generation failed for '{kw}' after retries: {e}")

        log_heartbeat("success", "Cycle completed successfully.")

    except Exception as e:
        tb = traceback.format_exc()
        log_heartbeat("error", f"Main cycle crashed: {e}\n{tb}")

# ============================================================
# Continuous autonomous loop
# ============================================================
def main_loop():
    print(f"🦴 bones autonomous collector started (interval: {FETCH_INTERVAL}s)")
    while True:
        start_time = datetime.now(timezone.utc).isoformat()
        log_heartbeat("info", f"Starting cycle at {start_time}")
        run_cycle()
        log_heartbeat("info", f"Cycle completed. Sleeping for {FETCH_INTERVAL} seconds.")
        time.sleep(FETCH_INTERVAL)

# ============================================================
# Entrypoint
# ============================================================
if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        log_heartbeat("info", "bones manually stopped via KeyboardInterrupt.")
    except Exception as e:
        tb = traceback.format_exc()
        log_heartbeat("fatal", f"bones crashed unexpectedly: {e}\n{tb}")
        raise
