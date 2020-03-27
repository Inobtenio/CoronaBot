import os
import re
import json
import logging
import pathlib
from plotter import CommandPlotter
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

ACCESS_TOKEN = os.environ['TELEGRAM_BOT_ACCESS_TOKEN']
COMMAND_FORMAT = "([c,C])oronabot\s*:\s*\w*\s*,\s*\w*\s*(,\s*-?\d+)?"
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
COUNTRIES_JSON_PATH = pathlib.Path(CURRENT_PATH, 'countries.json')
COMMAND_TYPES = ['total', 'new', 'deaths', 'recovered']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO);
logger = logging.getLogger(__name__)

def info(update, context):
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

def country_names():
    with open(COUNTRIES_JSON_PATH, 'rb') as file:
        return [*json.load(file).keys()]

def get_command_type(message):
    args = message[message.index(":")+1:].split(',')
    return args[0].strip().lower()

def get_country(message):
    args = message[message.index(":")+1:].split(',')
    return args[1].strip().lower()

def get_days(message):
    args = message[message.index(":")+1:].split(',')
    if (len(args) == 3): return abs(int(args[2].strip()))
    return 0

def plot(update, context):
    message = update.message.text
    match = re.search(COMMAND_FORMAT, message)

    if not match: return

    command_type = get_command_type(message)

    if not command_type in COMMAND_TYPES:
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm afraid I can't help you with that.");
        return

    country = get_country(message)

    if not country in country_names():
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, that's not a place I know about.");
        return

    days_ago = get_days(message)

    if not days_ago in range(0,8):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Hmmm, I don't think I can go back that far.")
        return

    send_text(update, context, "Plotting... Please wait for me :)")
    plotting_options = {'command_type': command_type, 'country': country, 'days_ago': days_ago}
    plot_request(plotting_options)
    send_photo(update, context, get_photo(plotting_options))

def plot_request(options):
    plotter = CommandPlotter()
    plotter.execute(options['command_type'], options['country'], options['days_ago'])

def plot_total_image_path():
    return pathlib.Path(CURRENT_PATH , 'plot', 'total', '{} {} - {}.png')

def plot_default_image_path(command_type):
    return pathlib.Path(CURRENT_PATH , 'plot', command_type, '{} - {}.png')

def get_total_photo(options):
    return open(str(plot_total_image_path()).format(options['country'], options['days_ago'], datetime.now().strftime("%m-%d-%y")), 'rb')

def get_default_photo(options):
    return open(str(plot_default_image_path(options['command_type'])).format(options['country'], datetime.now().strftime("%m-%d-%y")), 'rb')

def get_photo(options):
    if options['command_type'] == 'total':
        return get_total_photo(options)
    return get_default_photo(options)

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
