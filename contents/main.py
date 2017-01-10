import logging

from telegram import ChatAction, Emoji
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)
from twitter_module import Twitter
from sentiment import best_bigram_word_feats, get_classifier, classify, init_bestwords

from config import BOT_TOKEN


# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize bestwords variable
init_bestwords()

# Set _featx and _classifier global variables
_featx = best_bigram_word_feats
_classifier = get_classifier(_featx)


# Process /start update
def start(bot, update):
    logger.info("/start request from %s" % update.message.chat_id)
    start_message = """Bot started! Type /help if you need help!"""
    bot.sendMessage(chat_id=update.message.chat_id, text=start_message)


# Process /help update
def help(bot, update):
    help_message = """
                    I can help you analysing recent tweets regarding any kind of topic.
                    It's not complicated, there's basically one command:
                    you can type /mood followed by the tags you want to search for and I will 
                    provide a real-time analysis.  Something like..
                    /mood #football
                    /mood #summer and so on..

                    Try me out!
                    For more informations you can visit https://github.com/ruaronicola/TelepathyBot.
                   """
    logger.info("/help request from %s" % update.message.chat_id)
    bot.sendMessage(update.message.chat_id, text=help_message)


# process /mood update
def mood(bot, update, args):
    # Abort if args is empty
    if args == []:
        return None
    logger.info(
            "/mood request from %s, query: %s" %
            (update.message.chat_id, args))

    # Let the user know that the bot is "typing.."
    bot.sendChatAction(
        chat_id=update.message.chat_id, action=ChatAction.TYPING)

    # Read query and submit it via python-twitter-tools, then store tweets
    query = " ".join(tag for tag in args)
    tweets = []
    mood = []
    query_mood = ""
    EMOJI = None
    for tweet in Twitter.query(query, 40)["statuses"]:
        tweets.append(tweet["text"])

    # Request a classification
    mood = classify(_classifier, _featx, tweets)
    # Then evaluate the "global mood"
    if mood.count("pos") > mood.count("neg"):
        query_mood = "positive"
        EMOJI = Emoji.SMILING_FACE_WITH_OPEN_MOUTH.decode("utf-8")
    elif mood.count("pos") < mood.count("neg"):
        query_mood = "negative"
        EMOJI = Emoji.PENSIVE_FACE.decode("utf-8")
    else:
        query_mood = "neutral"
        EMOJI = Emoji.RELIEVED_FACE.decode("utf-8")
    bot.sendMessage(
            chat_id=update.message.chat_id,
            text="%s  People is now feeling %s about %s" %
            (EMOJI, query_mood, query))


# Handle unknown commands
def unknown(bot, update):
    logger.info("Unknown request from %s" % update.message.chat_id)
    bot.sendMessage(
        update.message.chat_id, "Sorry, I can't figure out your request!")


# Handle errors
def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        logger.warn("Update '%s' caused Unauthorized error" % (update))
    except BadRequest:
        logger.warn("Update '%s' caused BadRequest error" % (update))
    except TimedOut:
        logger.warn("Update '%s' caused TimedOut error" % (update))
    except NetworkError:
        logger.warn("Update '%s' caused NetworkError error" % (update))
    except ChatMigrated as e:
        logger.warn("Update '%s' caused ChatMigrated error" % (update))
    except TelegramError:
        logger.warn("Update '%s' caused TelegramError error" % (update))


# Handle received messages
def message(bot, update):
    logger.info("New message from %s" % update.message.chat_id)


def main():
    # Updater obj -- create telegram Bot: get new notifications from telegram
    # and forward them to the Dispatcher
    # To generate an ACCESS TOKEN: we have to talk to BotFather
    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Create handlers
    start_handler = CommandHandler('start', start)
    mood_handler = CommandHandler('mood', mood, pass_args=True)
    help_handler = CommandHandler('help', help)
    unknown_handler = MessageHandler(Filters.command, unknown)
    message_handler = MessageHandler(Filters.text, message)

    # Add handlers
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(mood_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(unknown_handler)
    dispatcher.add_error_handler(error_callback)
    dispatcher.add_handler(message_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until Ctrl-C is pressed
    updater.idle()


# Main
if __name__ == "__main__":
    main()
