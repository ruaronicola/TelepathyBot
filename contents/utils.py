import re

from pymongo import MongoClient

from config import (ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET,
                    MONGOLAB_URI, MONGOLAB_PORT, MONGOLAB_USER, MONGOLAB_PASS)


# Connect to mongolab, where tweets are stored and classified
def connect():
    connection = MongoClient(MONGOLAB_URI, MONGOLAB_PORT)
    handle = connection["pymongo-db"]
    handle.authenticate(MONGOLAB_USER, MONGOLAB_PASS)
    return handle


# Manage Python Twitter tools
# Source at https://pypi.python.org/pypi/twitter
class Twitter:
    # Create a new Twitter connection
    @staticmethod
    def create():
        # Locally import in order to avoid conflicts on the class name
        from twitter import Twitter, OAuth
        # Set tokens/keys from Twitter App
        oauth = OAuth(
                ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
        # Initiate the connection to Twitter API
        twitter = Twitter(auth=oauth)
        return twitter

    # Query Twitter for hashtags
    @staticmethod
    def query(hashtags, c):
        # Request to filter retweets
        query = "%s %s" % (hashtags, "-filter:retweets")
        print "New twitter query: "+query
        result = Twitter.create().search.tweets(
                q=query, result_type='recent', lang='en', count=c)
        return result

    # Processing ----------
    @staticmethod
    def process_tweet(tweet):
        # Convert to lower case
        tweet = tweet.lower()
        # Convert www.* or https?://* to URL
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
        # Convert @username to AT_USER
        tweet = re.sub('@[^\s]+', 'AT_USER', tweet)
        # Remove additional white spaces
        tweet = re.sub('[\s]+', ' ', tweet)
        # Replace #word with word
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        # Trim
        tweet = tweet.strip('\'"')
        # Stretch repetitions: "hellooooo"->"helloo"
        pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
        tweet = pattern.sub(r"\1\1", tweet)

        return tweet