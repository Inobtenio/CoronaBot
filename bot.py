import os
import re
import json
import logging
import pathlib
import sys
from datetime import datetime
from plotter import CommandPlotter

CURRENT_PATH = pathlib.Path(__file__).parent.parent.absolute()
COUNTRIES_JSON_PATH = pathlib.Path(CURRENT_PATH, 'countries.json')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseBot(object):
    ACCESS_TOKEN = ''
    COMMAND_FORMAT = ''

    def info(self):
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
        return text

    def country_names(self):
        with open(COUNTRIES_JSON_PATH, 'rb') as file:
            return [*json.load(file).keys()]

    def get_command_type(self, message):
        args = message[message.find(":")+1:].split(',')
        return args[0].strip().lower()

    def get_country(self, message):
        args = message[message.find(":")+1:].split(',')
        return args[1].strip().lower()

    def get_days(self, message):
        args = message[message.find(":")+1:].split(',')
        if (len(args) == 3): return abs(int(args[2].strip()))
        return 0

    def plot_request(self, options):
        plotter = CommandPlotter()
        plotter.execute(options['command_type'], options['country'], options['days_ago'])

    def plot_total_image_path(self):
        return pathlib.Path(CURRENT_PATH , 'plot', 'total', '{} {} - {}.png')

    def plot_default_image_path(self, command_type):
        return pathlib.Path(CURRENT_PATH , 'plot', command_type, '{} - {}.png')

    def get_total_photo(self, options):
        return open(str(self.plot_total_image_path()).format(options['country'], options['days_ago'], datetime.now().strftime("%m-%d-%y")), 'rb')

    def get_default_photo(self, options):
        return open(str(self.plot_default_image_path(options['command_type'])).format(options['country'], datetime.now().strftime("%m-%d-%y")), 'rb')

    def get_photo(self, options):
        if options['command_type'] == 'total':
            return self.get_total_photo(options)
        return self.get_default_photo(options)

    def plot(self):
        logger.warning('You need to implement your custom plot method')

