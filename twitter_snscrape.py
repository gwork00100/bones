import snscrape.modules.twitter as sntwitter

query = "bitcoin"
max_tweets = 10

for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
    if i >= max_tweets:
        break
    print(f"{tweet.date} - @{tweet.user.username}: {tweet.content}\n")
