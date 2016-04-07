from config import ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET


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
