import os
import sys
import json
import pandas
import pathlib
import requests
import subprocess
import urllib.parse

HOST = os.environ['HOST']
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
LOCAL_COUNTRY = 'peru'
LOCAL_DATAFILE_PATH = pathlib.Path(CURRENT_PATH, '{}.csv'.format(LOCAL_COUNTRY))
COUNTRIES_JSON_PATH = pathlib.Path(CURRENT_PATH, 'countries.json')
DEFAULT_API_ENDPOINT = 'https://coronavirus-19-api.herokuapp.com/countries'
FALLBACK_API_ENDPOINT = 'https://thevirustracker.com/free-api?countryTotal={}'
ENDPOINT_HEADERS = {'User-Agent': 'CoronaBot'}

def decode(bytes):
    return bytes.decode().strip()

class Plotter(object):

    def __init__(self, country):
        with open(COUNTRIES_JSON_PATH, 'rb') as file:
            self.countries = json.load(file)

        self.country = country

    def get_data_for(self, default_api_key, fallback_api_key):
        try:
            r = requests.get(DEFAULT_API_ENDPOINT, headers=ENDPOINT_HEADERS)
            return [entry[default_api_key] for entry in r.json() if entry['country'] == self.country_name()][0]
        except:
            r = requests.get(FALLBACK_API_ENDPOINT.format(self.country_code()), headers=ENDPOINT_HEADERS)
            return r.json()['countrydata'][0][fallback_api_key]

    def country_name(self):
        return self.countries[self.country]['name']

    def country_code(self):
        return self.countries[self.country]['code']

    def get_dataframe(self):
        return pandas.read_csv(self.DATAFILE_PATH)

    def modify_data(self):
        raise NotImplementedError

    def write_csv(self):
        self.dataframe.to_csv(self.DATAFILE_PATH, index=False)

    def update_data(self):
        self.dataframe = self.get_dataframe()
        self.modify_data()
        self.write_csv()

    def run_command(self):
        return subprocess.run(['bash', self.BASH_COMMAND, self.country_name()], stdout=subprocess.PIPE)

    def plot(self):
        result = self.run_command()
        if result.returncode == 1: raise PlottingError('Unknown')
        return HOST + urllib.parse.quote(decode(result.stdout))


class TotalPlotter(Plotter):
    BASH_COMMAND = 'plot_total.sh'
    DATAFILE_PATH = pathlib.Path(CURRENT_PATH, 'total_history.csv')

    def __init__(self, country, days):
        self.days = str(days)
        super().__init__(country)

    def country_total_cases(self):
        return self.get_data_for('cases', 'total_cases')

    def modify_data(self):
        self.dataframe.at[self.dataframe.shape[0]-1, '{}'.format(self.country)] = self.country_total_cases()

    def modify_with_local_data(self):
        if not self.country == LOCAL_COUNTRY: return

        local_dataframe = pandas.read_csv(LOCAL_DATAFILE_PATH)
        if self.dataframe.shape[0] > local_dataframe.shape[0]: return

        self.dataframe[LOCAL_COUNTRY] = local_dataframe[LOCAL_COUNTRY]

    def update_data(self):
        self.dataframe = self.get_dataframe()

        self.modify_data()

        # Exceptional modification (more accurate data than the API for my country) [totally optional]
        self.modify_with_local_data()

        self.write_csv()

    def run_command(self):
        return subprocess.run(['bash', self.BASH_COMMAND, self.country_name(), self.days], stdout=subprocess.PIPE)


class NewCasesPlotter(TotalPlotter):
    BASH_COMMAND = 'plot_new.sh'

    def __init__(self, country):
        super().__init__(country, 0)

    def run_command(self):
        return subprocess.run(['bash', self.BASH_COMMAND, self.country_name()], stdout=subprocess.PIPE)


class DeathsPlotter(Plotter):
    BASH_COMMAND = 'plot_deaths.sh'
    DATAFILE_PATH = pathlib.Path(CURRENT_PATH, 'deaths_history.csv')

    def country_total_deaths(self):
        return self.get_data_for('deaths', 'total_deaths')

    def modify_data(self):
        self.dataframe.at[self.dataframe.shape[0]-1, '{}'.format(self.country)] = self.country_total_deaths()


class RecoveredPlotter(Plotter):
    BASH_COMMAND = 'plot_recovered.sh'
    DATAFILE_PATH = pathlib.Path(CURRENT_PATH, 'recovered_history.csv')

    def country_total_recovered(self):
        return self.get_data_for('recovered', 'total_recovered')

    def modify_data(self):
        self.dataframe.at[self.dataframe.shape[0]-1, '{}'.format(self.country)] = self.country_total_recovered()


class PlottingError(Exception):
    pass

class CommandError(Exception):
    pass

class CountryError(Exception):
    pass

class DaysError(Exception):
    pass


class CommandValidator(object):
    VALID_COMMANDS = ['total', 'new', 'deaths', 'recovered']
    with open(COUNTRIES_JSON_PATH, 'rb') as file:
        COUNTRY_NAMES = [*json.load(file).keys()]

    def valid_number(self, target):
        try:
            number = int(target)
            return number in range(0,8)
        except ValueError:
            return False

    def validate(self, command, country, days):
        if not command in self.VALID_COMMANDS: raise CommandError(f'I don\'t recognize that command. Accepted ones are {self.VALID_COMMANDS}.')
        if not country in self.COUNTRY_NAMES: raise CountryError('That\'s a country I have no data for.')
        if not self.valid_number(days): raise DaysError('Not a valid value for <days_back>. Use a number between 0 and 7 instead.')


class CommandPlotter:
    def execute(self, command, country, days):
        plotter = factory.get_command_plotter(command, country, days)
        plotter.update_data()
        return plotter.plot()


class CommandPlotterFactory:
    def get_command_plotter(self, command, country, days):
        if not days: days = 0
        CommandValidator().validate(command, country, days)
        if command == 'total':
            return TotalPlotter(country, days)
        if command == 'new':
            return NewCasesPlotter(country)
        if command == 'deaths':
            return DeathsPlotter(country)
        if command == 'recovered':
            return RecoveredPlotter(country)

factory = CommandPlotterFactory()
