import feedparser
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import emoji
import hashlib
import spacy

from coingecko_helper import get_trending_coins  # <-- import CoinGecko helper

# Load SpaCy model for entity recognition
nlp = spacy.load("en_core_web_sm")

# List of RSS feeds
FEED_URLS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://cryptoslate.com/feed/",
    "https://www.investing.com/rss/news_25.rss",
    "https://finance.yahoo.com/news/rssindex",
    "https://www.reutersagency.com/feed/?best-sectors=business"
]

def clean_html(text):
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text()
    text = emoji.replace_emoji(text, "")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_keywords(text):
    doc = nlp(text)
    keywords = list({ent.text.lower() for ent in doc.ents if ent.label_ in ["ORG", "PERSON", "GPE", "PRODUCT", "EVENT"]})
    # Add regex-based crypto ticker extraction
    tickers = re.findall(r"\b[A-Z]{2,5}\b", text)
    return list(set(keywords + tickers))

def compute_score(entry, keywords, trending_coins):
    score = 0

    # Keyword based scoring
    if "bitcoin" in keywords:
        score += 30
    if "ethereum" in keywords:
        score += 20

    # Boost for trending coins mention
    title = entry.get("title", "").lower()
    clean_text = clean_html(entry.get("summary", "") or title).lower()
    for coin in trending_coins:
        if coin in title or coin in clean_text:
            score += 25
            break  # Only boost once

    # Freshness (within 24h = 50 points)
    published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - published_time).total_seconds() / 3600
    if age_hours < 24:
        score += 50 - int(age_hours * 2)  # decay score over time

    return min(score, 100)

def process_feed(url, trending_coins):
    feed = feedparser.parse(url)
    source_name = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
    articles = []

    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        link = entry.get("link", "")
        published = entry.get("published", "")
        published_parsed = entry.get("published_parsed", None)

        if not published_parsed:
            continue

        # Clean
        clean_summary = clean_html(summary or title)
        keywords = extract_keywords(clean_summary)
        score = compute_score(entry, keywords, trending_coins)

        article = {
            "id": hashlib.md5(link.encode()).hexdigest(),
            "source": source_name,
            "title": title,
            "url": link,
            "summary": clean_summary[:300],
            "publish_date": datetime(*published_parsed[:6]).isoformat(),
            "keywords": keywords,
            "score": score,
            "clean_text": clean_summary
        }

        articles.append(article)
    
    return articles

def ingest_all_feeds():
    all_articles = []

    trending_coins = get_trending_coins()  # <-- fetch once here
    print(f"Trending coins: {trending_coins}")

    for url in FEED_URLS:
        try:
            articles = process_feed(url, trending_coins)
            all_articles.extend(articles)
        except Exception as e:
            print(f"Error processing {url}: {e}")
    return all_articles

if __name__ == "__main__":
    articles = ingest_all_feeds()
    
    with open("cleaned_rss_output.json", "w") as f:
        json.dump(articles, f, indent=2)

    print(f"Ingested and cleaned {len(articles)} articles.")
