import tweepy
from datetime import datetime, timedelta
import schedule
import time
import os
from dotenv import load_dotenv

# Helpful when testing locally
load_dotenv()

# Load your Twitter API keys
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

class TwitterBot:
    def __init__(self):
        self.twitter_api = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN,
                                         consumer_key=TWITTER_API_KEY,
                                         consumer_secret=TWITTER_API_SECRET,
                                         access_token=TWITTER_ACCESS_TOKEN,
                                         access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
                                         wait_on_rate_limit=True)

        self.twitter_me_id = self.get_me_id()
        self.tweet_response_limit = 35

        self.mentions_found = 0
        self.mentions_replied = 0
        self.mentions_replied_errors = 0

    def respond_to_mention(self, mention):
        response_text = "Hello"
        
        try:
            response_tweet = self.twitter_api.create_tweet(text=response_text, in_reply_to_tweet_id=mention.id)
            self.mentions_replied += 1
        except Exception as e:
            print(e)
            self.mentions_replied_errors += 1
            return

        return True

    def get_me_id(self):
        return self.twitter_api.get_me().data.id
    
    def get_mentions(self):
        now = datetime.utcnow()
        start_time = now - timedelta(minutes=1)
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        return self.twitter_api.get_users_mentions(id=self.twitter_me_id,
                                                   start_time=start_time_str,
                                                   expansions=['referenced_tweets.id'],
                                                   tweet_fields=['created_at', 'conversation_id']).data

    def respond_to_mentions(self):
        mentions = self.get_mentions()

        if not mentions:
            print("No mentions found")
            return
        
        self.mentions_found = len(mentions)

        for mention in mentions[:self.tweet_response_limit]:
            self.respond_to_mention(mention)
        return True

    def execute_replies(self):
        print(f"Starting Job: {datetime.utcnow().isoformat()}")
        self.respond_to_mentions()
        print(f"Finished Job: {datetime.utcnow().isoformat()}, Found: {self.mentions_found}, Replied: {self.mentions_replied}, Errors: {self.mentions_replied_errors}")

def job():
    print(f"Job executed at {datetime.utcnow().isoformat()}")
    bot = TwitterBot()
    bot.execute_replies()

if __name__ == "__main__":
    schedule.every(1).minute.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
