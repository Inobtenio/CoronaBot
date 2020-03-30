import os
import re
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from bot import BaseBot

TELEGRAM_ACCESS_TOKEN = os.environ['TELEGRAM_BOT_ACCESS_TOKEN']
COMMAND_TYPES = ['total', 'new', 'deaths', 'recovered']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot(BaseBot):
    ACCESS_TOKEN = TELEGRAM_ACCESS_TOKEN
    COMMAND_FORMAT = r"([c,C])oronabot\s*:\s*\w*\s*,\s*\w*\s*(,\s*-?\d+)?"

    def __init__(self):
        self.updater = Updater(self.ACCESS_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def start_listening(self):
        send_info = lambda update, context: self.send_text(update, context, self.info())

        self.dispatcher.add_handler(CommandHandler("info", send_info))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.plot))

        self.dispatcher.add_error_handler(self.error)

        logger.info('Start polling Telegram messages')

        self.updater.start_polling()

        self.updater.idle()

    def send_text(self, update, context, message):
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    def send_photo(self, update, context, photo):
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)

    def error(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def plot(self, update, context):
        message = update.message.text
        match = re.search(self.COMMAND_FORMAT, message)

        if not match: return

        command_type = self.get_command_type(message)

        if not command_type in COMMAND_TYPES:
            self.send_text(update, context, "I'm afraid I can't help you with that.")
            return

        country = self.get_country(message)

        if not country in self.country_names():
            self.send_text(update, context, "Sorry, that's not a place I know about.")
            return

        days_ago = self.get_days(message)

        if not days_ago in range(0,8):
            self.send_text(update, context, "Hmmm, I don't think I can go back that far.")
            return

        self.send_text(update, context, "Plotting... Please wait for me :)")
        plotting_options = {'command_type': command_type, 'country': country, 'days_ago': days_ago}
        self.plot_request(plotting_options)
        self.send_photo(update, context, self.get_photo(plotting_options))


def main():
    telegram_bot = TelegramBot()

    telegram_bot.start_listening()


if __name__ == '__main__':
    main()
