import os
import re
import json
import parse
import logging
import pathlib
from plotter import Plotter
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

ACCESS_TOKEN = os.environ['TELEGRAM_BOT_ACCESS_TOKEN']
COMMAND_FORMAT = "([c,C])oronabot:\s*\w*(,\s*-\d+)?"
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
COUNTRIES_JSON_PATH = pathlib.Path(CURRENT_PATH, 'countries.json')
PLOT_IMAGE_PATH = pathlib.Path(CURRENT_PATH , 'plot', 'plot {} {} - {}.png')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO);
logger = logging.getLogger(__name__)

def info(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm the CoronaBot, please ask me something!");

def parse(message):
    match = re.search(COMMAND_FORMAT, message)
    if match: return get_args(match)

def country_names():
    with open(COUNTRIES_JSON_PATH, 'rb') as file:
        return [*json.load(file).keys()]

def get_country(message):
    args = message[10:].split(',')
    return args[0].strip()

def get_days(message):
    args = message[10:].split(',')
    if (len(args) == 2): return abs(int(args[1].strip()))
    return 0

def plot(update, context):
    message = update.message.text
    match = re.search(COMMAND_FORMAT, message)

    if not match: return

    country = get_country(message)

    if not country in country_names():
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, that's not a place I know about.");
        return

    days_ago = get_days(message)

    if not days_ago in range(0,7):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Hmmm, I don't think I can go back that far.")
        return

    send_text(update, context, "Plotting... Please wait for me :)")
    plot_request(country, days_ago)
    send_photo(update, context, get_photo(country, days_ago))

def plot_request(country, days_ago):
    plotter = Plotter(country, days_ago)
    plotter.update_data()
    plotter.plot()

def get_photo(country, days_ago):
    return open(str(PLOT_IMAGE_PATH).format(country, days_ago, datetime.now().strftime("%m-%d-%y")), 'rb')

def send_text(update, context, message):
    context.bot.send_message(chat_id=update.effective_chat.id, text=message);

def send_photo(update, context, photo):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(ACCESS_TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(MessageHandler(Filters.text, plot))

    dispatcher.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
