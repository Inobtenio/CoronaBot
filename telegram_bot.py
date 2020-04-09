import os
import re
from base_bot import BaseBot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

ACCESS_TOKEN = os.environ['TELEGRAM_BOT_ACCESS_TOKEN']
COMMAND_FORMAT = '([c,C])oronabot\s*:\s*\w*\s*,\s*\w*\s*(,\s*-?\d+)?'

class TelegramBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.updater = Updater(ACCESS_TOKEN, use_context=True)
        dispatcher = self.updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('info', self.info))
        dispatcher.add_handler(MessageHandler(Filters.update.message, self.plot))
        dispatcher.add_error_handler(self.error)

    def start_text_modifier(self):
        text =  """
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
                Coronabot: deaths, United Kingdom

            Safe plotting ;)
            """

        return text

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text=self.start_text());

    def info_text_modifier(self):
        text =  """
            Telegram Bot created by:
            Kevin Martin

            Open source code at:
            https://github.com/Inobtenio/CoronaBot
            """

        return text

    def info_text(self):
        return super().info_text().format('')

    def info(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text=self.info_text());

    def split_args(self, message):
        return message[message.index(':')+1:].split(',')

    def get_command(self, message):
        args = self.split_args(message)
        return args[0].strip().lower()

    def get_country(self, message):
        args = self.split_args(message)
        return args[1].strip().lower()

    def get_days(self, message):
        args = self.split_args(message)
        if (len(args) == 3): return args[2].strip()

    def get_bot_info(self, update, context):
        return {'bot': context.bot, 'chat_id': update.effective_chat.id}

    def plot(self, update, context):
        request_text = update.message.text
        if not isinstance(request_text, str): return

        match = re.search(COMMAND_FORMAT, request_text)
        if not match: return

        bot_info = self.get_bot_info(update, context)
        self.send_text(bot_info, 'Got it... Please wait for me :)')

        plotting_options = {
                    'command': self.get_command(request_text),
                    'country': self.get_country(request_text),
                    'days': self.get_days(request_text)
                }

        plot_file_url = self.get_plot_file_url(plotting_options, bot_info=bot_info)
        if plot_file_url: self.send_photo(bot_info, plot_file_url)

    def handle_plot_error(self, **kwargs):
        self.send_error(kwargs['bot_info'], kwargs['error'])

    def send_error(self, bot_info, message):
        error_message = 'Oops, an error ocurred: ' + message
        bot_info['bot'].send_message(chat_id=bot_info['chat_id'], text=error_message)

    def send_text(self, bot_info, message):
        bot_info['bot'].send_message(chat_id=bot_info['chat_id'], text=message)

    def send_photo(self, bot_info, photo):
        bot_info['bot'].send_photo(chat_id=bot_info['chat_id'], photo=photo)

    def error(self, update, context):
        self.log_error(f'Update ---- {update} ---- caused error ---- {context.error} ----')
        self.send_error(self.get_bot_info(update, context), 'I don\'t know what but something went wrong :(.')

    def listen(self):
        self.updater.start_polling()

        self.updater.idle()


if __name__ == '__main__':
    TelegramBot().listen()
