import os
import re
import logging
from plotter import CommandPlotter, CommandError, CountryError, DaysError, PlottingError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

ACCESS_TOKEN = os.environ['TELEGRAM_BOT_ACCESS_TOKEN']
COMMAND_FORMAT = "([c,C])oronabot\s*:\s*\w*\s*,\s*\w*\s*(,\s*-?\d+)?"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO);
logger = logging.getLogger(__name__)

def start(update, context):
    text = """Hi, I'm the CoronaBot. You can ask for current info about the novel coronavirus in your area.

Just type: Coronabot: <command>, <country>, <days_back>

Where
<command> is one of:
    'total' for total cases over time
    'new' for new cases over time
    'deaths' for deaths over time
    'recovered' for recovered numbers over time

<country> is the name of the country you want to ask for

<days_back> (works with 'total' only) reflects the reality from as many days ago (max. 7) as you specify

For example:
    Coronabot: total, Brazil, 3
    Coronabot: recovered, japan

Happy plotting."""
    context.bot.send_message(chat_id=update.effective_chat.id, text=text);

def info(update, context):
    text = """Created by: Kevin Martin
knmartinm@gmail.com
@Inobtenio
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=text);

def split_args(message):
    return message[message.index(":")+1:].split(',')

def get_command(message):
    args = split_args(message)
    return args[0].strip().lower()

def get_country(message):
    args = split_args(message)
    return args[1].strip().lower()

def get_days(message):
    args = split_args(message)
    if (len(args) == 3): return abs(int(args[2].strip()))
    return 0

def plot(update, context):
    request_text = update.message.text
    match = re.search(COMMAND_FORMAT, request_text)

    if not match: return

    send_text(update, context, "Got it... Please wait for me :)")

    try:
        plot_file_url = plot_request(get_command(request_text), get_country(request_text), get_days(request_text))
        send_photo(update, context, plot_file_url)
    except (CommandError, CountryError, DaysError, PlottingError) as e:
        send_error(update, context, str(e))

def plot_request(command, country, days):
    return CommandPlotter().execute(command, country, days)

def send_error(update, context, message):
    error_message = "Oops, an error ocurred: " + message
    context.bot.send_message(chat_id=update.effective_chat.id, text=error_message);

def send_text(update, context, message):
    context.bot.send_message(chat_id=update.effective_chat.id, text=message);

def send_photo(update, context, photo):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(ACCESS_TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(MessageHandler(Filters.text, plot))

    dispatcher.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
