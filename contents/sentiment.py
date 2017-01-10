import re

from nltk.classify import NaiveBayesClassifier
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist

from utils import Twitter, connect

# Define global variable _bestwords, used during feature extraction
_bestwords = None

# connect to mongo db
handle = connect()


# Set global variable _bestwords, used during feature extraction
def init_bestwords():
    print "Defining _bestwords.."
    global _bestwords
    _bestwords = get_best_words()


def get_best_words():
    tokenizer = TweetTokenizer()
    # Analyze frequencies
    word_fd = FreqDist()
    label_word_fd = ConditionalFreqDist()

    negstr = [obj["text"] for obj in handle.negative_tweets.find()]
    posstr = [obj["text"] for obj in handle.positive_tweets.find()]
    negwords = []
    poswords = []
    for i in range(0, len(negstr)-1):
        for w in tokenizer.tokenize(Twitter.process_tweet(negstr[i])):
            if w not in stopwords.words("english"):
                negwords.append(w)
    for i in range(0, len(posstr)-1):
        for w in tokenizer.tokenize(Twitter.process_tweet(posstr[i])):
            if w not in stopwords.words("english"):
                poswords.append(w)

    for word in poswords:
        word_fd[word] += 1
        label_word_fd['pos'][word] += 1
    for word in negwords:
        word_fd[word] += 1
        label_word_fd['neg'][word] += 1
    pos_word_count = label_word_fd['pos'].N()
    neg_word_count = label_word_fd['neg'].N()
    total_word_count = pos_word_count + neg_word_count

    # Score words
    word_scores = {}
    for word, freq in word_fd.iteritems():
        pos_score = BigramAssocMeasures.chi_sq(
                            label_word_fd['pos'][word], (freq, pos_word_count),
                            total_word_count)
        neg_score = BigramAssocMeasures.chi_sq(
                            label_word_fd['neg'][word], (freq, neg_word_count),
                            total_word_count)
        word_scores[word] = pos_score + neg_score

    # Keep best 10000 words
    best = sorted(
        word_scores.iteritems(), key=lambda (w, s): s, reverse=True)[:10000]
    bestwords = set([w for w, s in best])

    return bestwords


# Feature Extractors ----------
def word_feats(words):
    return dict([(word, True) for word in words])


def best_word_feats(words):
    return dict([(word, True) for word in words if word in _bestwords])


def best_bigram_word_feats(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    d = dict([(bigram, True) for bigram in bigrams])
    d.update(best_word_feats(words))
    return d


# Classification ----------
def get_classifier(featx):
    tokenizer = TweetTokenizer()
    print "Training Classifier..."
    negstr = [obj["text"] for obj in handle.negative_tweets.find()]
    posstr = [obj["text"] for obj in handle.positive_tweets.find()]
    negfeats = [(featx(tokenizer.tokenize(Twitter.process_tweet(negstr[i]))), 'neg')
                for i in range(0, len(negstr)-1)]
    posfeats = [(featx(tokenizer.tokenize(Twitter.process_tweet(posstr[i]))), 'pos')
                for i in range(0, len(posstr)-1)]
    trainfeats = negfeats + posfeats

    classifier = NaiveBayesClassifier.train(trainfeats)

    return classifier


# PROS: really fast processing (after one-time training), not so terrible
# CONS: no neutral labels, no probabilities
def classify(classifier, featx, strings):
    print "Classify request"
    tokenizer = TweetTokenizer()
    mood = []
    for string in strings:
        string = Twitter.process_tweet(string)
        tokenized_text = [word.lower() for word in tokenizer.tokenize(string)]
        mood.append(classifier.classify(featx(tokenized_text)))
    return mood

# TODO: Create a Twitter-specialized feature-xtractor
#       Personalized train-set
