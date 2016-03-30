import os

from flask import Flask, session, render_template, request, redirect

from twitter_module import Twitter
from sentiment import best_bigram_word_feats, get_classifier, classify
from config import SECRET_KEY

app = Flask(__name__)

# Set _featx and _classifier global variables
_featx = best_bigram_word_feats
_classifier = get_classifier(_featx)


# In index() we read the name of the current request stored in session,
# if not None.. then query for tweets and classify them, finally the current
# request is cleared
@app.route("/index", methods=["GET"])
@app.route("/", methods=["GET"])
def index():
    request = session.get("request", None)
    tweets = []
    mood = []
    query_mood = ""
    if (request is not None):
        for tweet in Twitter.query(request, 40)["statuses"]:
            tweets.append(tweet["text"])
        mood = classify(_classifier, _featx, tweets)
        # Then evaluate the "global mood"
        if mood.count("pos") > mood.count("neg"):
            query_mood = "pos"
        elif mood.count("pos") < mood.count("neg"):
            query_mood = "neg"
        else:
            query_mood = "neu"
        # Clear session after processing
        session["request"] = None
    return render_template(
            "index.html", entries=tweets, mood=mood, query_mood=query_mood,
            keywords=request)


# When a query is submitted, a new request is created and its name is
# saved in "session", then the query is evaluated through
# python-twitter-tools and the sentiment.py module
@app.route("/search", methods=["POST"])
def search():
    # Get userinput from the form submitted, them store it in session
    session["request"] = request.form.get("userinput")
    return redirect("/")


# Just render the about.html template when /about is navigated to
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


if __name__ == "__main__":
    # Set secret key in order to use session
    app.config["SECRET_KEY"] = SECRET_KEY

    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


# TODO: Decently handle 404
#       Stream/update content with jquery
