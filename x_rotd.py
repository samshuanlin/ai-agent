import requests
from requests_oauthlib import OAuth1

class X_ROTD:
    def __init__(self):
        # Your X API credentials
        API_KEY = 'O78JwY04tkOxMTIrFfZK7RDng'
        API_SECRET_KEY = '8zIfia7OyEFEKfaTCITubfj8jZECjTaTdfQz1OAMbS4CblgLdE'
        ACCESS_TOKEN = '1718452380000563200-ayhh1esHaT9vZS9mj3ZJi8EKDVYGJK'
        ACCESS_TOKEN_SECRET = 'u6wE2XZDWlbG8oFUmkWOwjmEFmtQRTStt40XkoYu0LdJ6'
        # Set up OAuth1 authentication
        self.auth = OAuth1(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        # Function to get the trending topics for today
    def get_trending_topics(self):
        url = 'https://api.x.com/2.0/trends/place.json?id=1'
        response = requests.get(url, auth=self.auth)
        
        if response.status_code == 200:
            trends = response.json()
            return [trend['name'] for trend in trends[0]['trends']]
        else:
            print(f"Failed to fetch trends. Status code: {response.status_code}")
            return []

    # Function to search for flirtatious tweets
    def search_flirtatious_tweets(self, trend):
        url = f'https://api.x.com/2.0/search/tweets.json?q=rizz&count=100'
        response = requests.get(url, auth=self.auth)
        
        if response.status_code == 200:
            tweets = response.json()['statuses']
            flirtatious_tweets = []
            
            flirt_keywords = ['flirt', 'date', 'love', 'heart', 'crush', 'wink', 'kiss', 'romantic']
            
            # Filter tweets based on flirtatious keywords
            for tweet in tweets:
                tweet_text = tweet['text'].lower()
                if any(keyword in tweet_text for keyword in flirt_keywords):
                    flirtatious_tweets.append(tweet)
            
            return flirtatious_tweets
        else:
            print(f"Failed to fetch tweets. Status code: {response.status_code}")
            return []

    # Function to rank the tweets based on engagement (likes and retweets)
    def rank_tweets(self, tweets):
        ranked_tweets = sorted(tweets, key=lambda x: (x['favorite_count'] + x['retweet_count']), reverse=True)
        return ranked_tweets

    # Main function to get the most flirtatious tweet
    def get_most_flirtatious_tweet(self):
        # Step 1: Get trending topics
        trends = self.get_trending_topics()
        if not trends:
            return "No trending topics available."
        
        flirtatious_tweets = []
        
        # Step 2: Search for flirtatious tweets for each trending topic
        for trend in trends:
            flirtatious_tweets += self.search_flirtatious_tweets(trend)
        
        if not flirtatious_tweets:
            return "No flirtatious tweets found."
        
        # Step 3: Rank the tweets based on engagement (likes + retweets)
        ranked_tweets = self.rank_tweets(flirtatious_tweets)
        
        # Step 4: Get the most flirtatious tweet (highest engagement)
        most_flirtatious_tweet = ranked_tweets[0]

        return {
            'tweet': most_flirtatious_tweet['text'],
            'likes': most_flirtatious_tweet['favorite_count'],
            'retweets': most_flirtatious_tweet['retweet_count'],
            'author': most_flirtatious_tweet['user']['name'],
            'author_handle': most_flirtatious_tweet['user']['screen_name']
        }