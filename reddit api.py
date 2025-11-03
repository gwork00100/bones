import praw

# Reddit app credentials
reddit = praw.Reddit(
    client_id="uxWOlBAmDgP7T9WP1EIyPw",
    client_secret="uVHZRXjnGrNR45I4HGMpEqxoDEexSw",
    username="letsgo_look",
    password="YOUR_REDDIT_PASSWORD",
    user_agent="trend-agent-script by /u/letsgo_look"
)

# Fetch top 5 posts from /r/popular
subreddit = reddit.subreddit("popular")

print("\n🔝 Top Reddit Posts Today:\n")
for post in subreddit.top(limit=5, time_filter="day"):
    print(f"📌 {post.title}")
    print(f"   🧠 Subreddit: {post.subreddit}")
    print(f"   🔗 URL: {post.url}\n")
