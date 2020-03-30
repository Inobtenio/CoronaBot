import os
import re
import logging

from bot import BaseBot

# Slack dependencies
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
import ssl as ssl_lib
import certifi

SLACK_ACCESS_TOKEN = os.environ['SLACK_BOT_ACCESS_TOKEN']
SLACK_SIGNING_SECRET = os.environ['SLACK_BOT_SIGNING_SECRET']
COMMAND_TYPES = ['total', 'new', 'deaths', 'recovered']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Slack
flask_app = Flask('Coronabot')
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", flask_app)

class SlackBot(BaseBot):
    ACCESS_TOKEN = SLACK_ACCESS_TOKEN
    COMMAND_FORMAT = r"\s*\w*\s*,\s*\w*\s*(,\s*-?\d+)?"

    def __init__(self):
        self.slack_web_client = WebClient(token=self.ACCESS_TOKEN)

    def start_listening(self):
        # ssl_context = ssl_lib.create_default_context(cafile=certifi.where())

        slack_events_adapter.on("message", self.message)
        slack_events_adapter.on("app_mention", self.message)

        logger.info("Start listening for Slack events")

        flask_app.run(port=3000)

    def send_text(self, channel_id, message):
        slack_message = {
            "channel": channel_id,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                }
            ]
        }

        self.slack_web_client.chat_postMessage(**slack_message)

    def send_photo(self, channel_id, photo):
        slack_message = {
            "channel": channel_id,
            "blocks": [
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": "Example Image",
                        "emoji": True
                    },
                    "image_url": "https://api.slack.com/img/blocks/bkb_template_images/goldengate.png",
                    "alt_text": "Plot image"
                }
            ]
        }
        self.slack_web_client.chat_postMessage(**slack_message)

    def error(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def plot(self, channel_id, message):
        match = re.search(self.COMMAND_FORMAT, message)

        logger.info(match)

        if not match: return

        command_type = self.get_command_type(message)

        if not command_type in COMMAND_TYPES:
            self.send_text(channel_id, "I'm afraid I can't help you with that.")
            return

        country = self.get_country(message)

        if not country in self.country_names():
            self.send_text(channel_id, "Sorry, that's not a place I know about.")
            return

        days_ago = self.get_days(message)

        if not days_ago in range(0,8):
            self.send_text(channel_id, "Hmmm, I don't think I can go back that far.")
            return

        self.send_text(channel_id, "Plotting... Please wait for me :)")
        plotting_options = {'command_type': command_type, 'country': country, 'days_ago': days_ago}
        self.plot_request(plotting_options)
        self.send_photo(channel_id, self.get_photo(plotting_options))

    # @slack_events_adapter.on("app_mention")
    def message(self, payload):
        event = payload.get("event", {})
        channel_id = event.get("channel")
        message = event.get("text")

        self.plot(channel_id, message)

def main():
    slack_bot = SlackBot()

    slack_bot.start_listening()

if __name__ == '__main__':
    main()
