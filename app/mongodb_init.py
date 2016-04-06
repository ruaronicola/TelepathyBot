from pymongo import MongoClient
from nltk.corpus import twitter_samples
from config import MONGOLAB_PASS, MONGOLAB_PORT, MONGOLAB_URI, MONGOLAB_USER


def connect():
    connection = MongoClient(MONGOLAB_URI, MONGOLAB_PORT)
    handle = connection["pymongo-db"]
    handle.authenticate(MONGOLAB_USER, MONGOLAB_PASS)
    return handle


def insert_samples():
    negstr = twitter_samples.strings("negative_tweets.json")
    posstr = twitter_samples.strings("positive_tweets.json")
    for i in range(0, len(negstr)-1):
        handle.negative_tweets.insert({"text": negstr[i]})
    for i in range(0, len(posstr)-1):
        handle.positive_tweets.insert({"text": posstr[i]})


handle = connect()
# uncomment to initialize db
# insert_samples()
