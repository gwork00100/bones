import tweepy
import time
from datetime import datetime

# Twitter API Bearer Token (set yours here or via env variable)
BEARER_TOKEN = "YOUR_BEARER_TOKEN"

# Initialize client
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

# Keywords to rotate across
KEYWORDS = [
    "bitcoin",
    "ETH sale",
    "Solana mint",
    "airdrop",
]

def search_tweets(keyword, max_results=50):
    """
    Search recent tweets for a keyword, get relevant engagement metrics,
    normalize by followers, and return list of dicts with tweet data.
    """
    tweets_data = []
    try:
        # Search recent tweets matching keyword (last 7 days)
        # You can add filters: lang, tweet fields, expansions, etc.
        response = client.search_recent_tweets(
            query=keyword + " -is:retweet -is:reply lang:en",  # filter retweets, replies, only English
            max_results=max_results,
            tweet_fields=["public_metrics", "created_at", "author_id"],
            expansions=["author_id"],
        )
        if not response.data:
            return []

        # Build map of user id to followers count
        users = {u.id: u for u in response.includes['users']}

        for tweet in response.data:
            user = users.get(tweet.author_id)
            if not user:
                continue

            metrics = tweet.public_metrics
            follower_count = user.public_metrics.get("followers_count", 1) or 1  # avoid div zero

            # Normalize engagement score
            engagement = (metrics['like_count'] + metrics['retweet_count'] + metrics['reply_count']) / follower_count

            tweets_data.append({
                "tweet_id": tweet.id,
                "text": tweet.text,
                "author_id": tweet.author_id,
                "created_at": tweet.created_at,
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

def rotate_keywords(keywords=KEYWORDS, index=0):
    """
    Rotate through keywords cyclically
    """
    return keywords[index % len(keywords)]

def run_three_times_daily():
    """
    Example runner: search 3x per day at fixed intervals.
    You'd want to run this as a cron job or background scheduler.
    """
    import schedule

    def job():
        # Rotate keywords each time job runs
        # Save last index somewhere persistent or pass externally
        global last_index
        keyword = rotate_keywords(index=last_index)
        print(f"Searching Twitter for keyword: {keyword}")
        tweets = search_tweets(keyword)
        # TODO: Save tweets to DB or process further here
        print(f"Fetched {len(tweets)} tweets for {keyword}")
        last_index += 1

    last_index = 0
    schedule.every(8).hours.do(job)  # every 8 hours = 3 times a day

    while True:
        schedule.run_pending()
        time.sleep(60)
