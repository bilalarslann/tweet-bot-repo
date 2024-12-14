import tweepy
from datetime import datetime, timedelta
import schedule
import time
import os

# Load your Twitter API keys directly in the code (no need for dotenv)
TWITTER_API_KEY = "KkwS4DUd7KJmsbw5zjyGPVVng"
TWITTER_API_SECRET = "zYyWGHDntj6sSwIhoS9hb1xxAmqlxceYjjL8Zqo5GTHNUDaXI8"
TWITTER_ACCESS_TOKEN = "1236314898059182080-Pr1eOuI6MV1SUsh1WBT7IB6On0yhN5"
TWITTER_ACCESS_TOKEN_SECRET = "ylmERYrKELFjq9vIKhSQHmJxSln2M0rsbTiCrOxjS097n"
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABIcxgEAAAAA%2BnljJHjFkmmWFscZBs17hrLWxpk%3D0EU5oKtaytQEfRitwBmbbbqU0NYfxZbvZRKmdk5gTmAVy7XOA8"

# TwitterBot class to help us organize our code and manage shared state
class TwitterBot:
    def __init__(self):
        self.twitter_api = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN,
                                         consumer_key=TWITTER_API_KEY,
                                         consumer_secret=TWITTER_API_SECRET,
                                         access_token=TWITTER_ACCESS_TOKEN,
                                         access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
                                         wait_on_rate_limit=True)

        self.twitter_me_id = self.get_me_id()
        self.tweet_response_limit = 35 # How many tweets to respond to each time the program wakes up

        # For statics tracking for each run. This is not persisted anywhere, just logging
        self.mentions_found = 0
        self.mentions_replied = 0
        self.mentions_replied_errors = 0

    # Generate a simple response ("Hello")
    def generate_response(self, mentioned_conversation_tweet_text):
        return "Hello"

    def respond_to_mention(self, mention, mentioned_conversation_tweet):
        response_text = self.generate_response(mentioned_conversation_tweet.text)
        
        # Try and create the response to the tweet. If it fails, log it and move on
        try:
            response_tweet = self.twitter_api.create_tweet(text=response_text, in_reply_to_tweet_id=mention.id)
            self.mentions_replied += 1
        except Exception as e:
            print (e)
            self.mentions_replied_errors += 1
            return
        
        return True

    # Returns the ID of the authenticated user for tweet creation purposes
    def get_me_id(self):
        return self.twitter_api.get_me()[0].id
    
    # Returns the parent tweet text of a mention if it exists. Otherwise returns None
    # We use this to since we want to respond to the parent tweet, not the mention itself
    def get_mention_conversation_tweet(self, mention):
        if mention.conversation_id is not None:
            conversation_tweet = self.twitter_api.get_tweet(mention.conversation_id).data
            return conversation_tweet
        return None

    # Get mentioned to the user thats authenticated and running the bot.
    # Using a lookback window of 2 hours to avoid parsing over too many tweets
    def get_mentions(self):
        now = datetime.utcnow()

        start_time = now - timedelta(minutes=20)

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
            mentioned_conversation_tweet = self.get_mention_conversation_tweet(mention)
            
            if mentioned_conversation_tweet.id != mention.id:
                self.respond_to_mention(mention, mentioned_conversation_tweet)
        return True

    def execute_replies(self):
        print (f"Starting Job: {datetime.utcnow().isoformat()}")
        self.respond_to_mentions()
        print (f"Finished Job: {datetime.utcnow().isoformat()}, Found: {self.mentions_found}, Replied: {self.mentions_replied}, Errors: {self.mentions_replied_errors}")

# The job that we'll schedule to run every X minutes
def job():
    print(f"Job executed at {datetime.utcnow().isoformat()}")
    bot = TwitterBot()
    bot.execute_replies()

if __name__ == "__main__":
    # Schedule the job to run every 6 minutes
    schedule.every(1).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
