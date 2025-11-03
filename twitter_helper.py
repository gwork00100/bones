import tweepy
import time
import os
from supabase import create_client

# ---------------------------
# Twitter API setup
# ---------------------------
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")  # Set in environment
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

# Keywords to rotate
KEYWORDS = [
    "bitcoin",
    "ETH sale",
    "Solana mint",
    "airdrop",
]

# ---------------------------
# Supabase setup
# ---------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------
# Functions
# ---------------------------
def search_tweets(keyword, max_results=50):
    """
    Search recent tweets for a keyword, normalize engagement by followers.
    Returns list of tweet dicts.
    """
    tweets_data = []
    try:
        response = client.search_recent_tweets(
            query=keyword + " -is:retweet -is:reply lang:en",
            max_results=max_results,
            tweet_fields=["public_metrics", "created_at", "author_id"],
            expansions=["author_id"],
        )
        if not response.data:
            return []

        users = {u.id: u for u in response.includes['users']}

        for tweet in response.data:
            user = users.get(tweet.author_id)
            if not user:
                continue

            metrics = tweet.public_metrics
            follower_count = user.public_metrics.get("followers_count", 1) or 1
            engagement = (metrics['like_count'] + metrics['retweet_count'] + metrics['reply_count']) / follower_count

            tweets_data.append({
                "tweet_id": tweet.id,
                "text": tweet.text,
                "author_id": tweet.author_id,
                "created_at": tweet.created_at.isoformat(),
                "like_count": metrics['like_count'],
                "retweet_count": metrics['retweet_count'],
                "reply_count": metrics['reply_count'],
                "followers_count": follower_count,
                "engagement_norm": engagement,
                "keyword": keyword,
            })
    except Exception as e:
        print(f"[Twitter Error] {e}")

    return tweets_data

def save_tweets_to_supabase(tweets, table_name="tweets"):
    """
    Save a list of tweet dicts to Supabase table.
    """
    if not tweets:
        return 0
    try:
        response = supabase.table(table_name).insert(tweets).execute()
        if response.error:
            print(f"[Supabase Error] {response.error}")
            return 0
        return len(tweets)
    except Exception as e:
        print(f"[Supabase Exception] {e}")
        return 0

def rotate_keywords(keywords=KEYWORDS, index=0):
    """
    Rotate through keywords cyclically.
    """
    return keywords[index % len(keywords)]

def run_three_times_daily():
    """
    Run the search and save process 3 times daily (every 8 hours).
    """
    import schedule

    last_index = 0

    def job():
        nonlocal last_index
        keyword = rotate_keywords(index=last_index)
        print(f"Searching Twitter for keyword: {keyword}")
        tweets = search_tweets(keyword)
        saved_count = save_tweets_to_supabase(tweets)
        print(f"Fetched {len(tweets)} tweets, saved {saved_count} to Supabase")
        last_index += 1

    schedule.every(8).hours.do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)
