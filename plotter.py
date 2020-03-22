import os
import sys
import json
import pandas
import pathlib
import requests

CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
LOCAL_COUNTRY = 'peru'
LOCAL_DATAFILE_PATH = pathlib.Path(CURRENT_PATH, '{}.csv'.format(LOCAL_COUNTRY))
COUNTRIES_JSON_PATH = pathlib.Path(CURRENT_PATH, 'countries.json')
DATAFILE_PATH = pathlib.Path(CURRENT_PATH, 'history.csv')
DEFAULT_API_ENDPOINT = 'https://coronavirus-19-api.herokuapp.com/countries'
FALLBACK_API_ENDPOINT = 'https://thevirustracker.com/free-api?countryTotal={}'
BASH_COMMAND = 'bash plot.sh {} {} {}'

class Plotter:

    def __init__(self, country, days):
        self.country = country
        self.days = days

        with open(COUNTRIES_JSON_PATH, 'rb') as file:
            self.countries = json.load(file)

    def country_name(self):
        return self.countries[self.country]['name']

    def country_code(self):
        return self.countries[self.country]['code']

    def country_total_cases(self):
        try:
            r = requests.get(DEFAULT_API_ENDPOINT)
            return [entry['cases'] for entry in r.json() if entry['country'] == self.country_name()][0]
        except:
            r = requests.get(FALLBACK_API_ENDPOINT.format(self.country_code()))
            return r.json()['countrydata'][0]['total_cases']

    def cases_at_index(self, index):
        return int(self.dataframe.at[self.dataframe.shape[0]-index, "{}".format(self.country)])

    def updated_from_yesterday(self):
        today_entry = self.cases_at_index(1)
        yesterday_entry = self.cases_at_index(2)

        return not yesterday_entry == today_entry

    def calculate_days_ago(self):
        if (not self.updated_from_yesterday()):
            return 1
        return 0

    def get_dataframe(self):
        return pandas.read_csv(DATAFILE_PATH)

    def modify_cases(self):
        self.dataframe.at[self.dataframe.shape[0]-1, "{}".format(self.country)] = self.country_total_cases()

    def write_csv(self):
        self.dataframe.to_csv(DATAFILE_PATH, index=False)

    def days_ago(self):
        if self.days == 0: return self.calculate_days_ago()
        return self.days

    def modify_with_local_data(self):
        if not self.country == LOCAL_COUNTRY: return

        local_dataframe = pandas.read_csv(LOCAL_DATAFILE_PATH)
        if self.dataframe.shape[0] > local_dataframe.shape[0]: return

        self.dataframe[LOCAL_COUNTRY] = local_dataframe[LOCAL_COUNTRY]

    def update_data(self):
        self.dataframe = self.get_dataframe()

        self.modify_cases()

        # Exceptional modification (more accurate data than the API for my country) [totally optional]
        self.modify_with_local_data()

        self.write_csv()

    def plot(self):
        os.system(BASH_COMMAND.format(
                self.country_name(),
                self.days,
                self.updated_from_yesterday()
            ))
