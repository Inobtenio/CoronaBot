import os
import inspect
import logging
import requests
from utils import url

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

API_HOST = os.environ['API_HOST']

class BaseBot(object):
    def __init__(self):
        self.info_text_base = None

    def start_text_modifier(self):
        return ''

    def start_text(self):
        text =  """Hi, I'm the CoronaBot. You can ask for current info about the novel coronavirus in your area.
                {}"""

        return inspect.cleandoc(text.format(self.start_text_modifier()))

    def info_text_modifier(self):
        return ''

    def info_text(self):
        if not self.info_text_base:
            self.info_text_base = self.call('info').json()['message']

        return inspect.cleandoc(self.info_text_base.format(self.info_text_modifier()))

    def get_plot_file_url(self, options, **kwargs):
            r = self.call('plot', **options)
            if not r.status_code == requests.codes.ok: return self.handle_plot_error(**r.json()['errors'], **kwargs)
            return r.json()['message']

    def call(self, endpoint, **kwargs):
        api_url = url(API_HOST, endpoint)
        return requests.get(api_url, params=kwargs)

    def handle_plot_error(self, **kwargs):
        return kwargs['error']

    def log_error(self, message):
        logger.error(message)
