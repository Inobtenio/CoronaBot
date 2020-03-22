import json
import pandas
import pathlib
import requests

CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
CSV_FILE_PATH = pathlib.Path(CURRENT_PATH, 'history.csv')
API_ENDPOINT = 'https://thevirustracker.com/timeline/map-data.json'
UNREASONABLE_FAR_DATE = '12/12/40'

def total_cases_for(country):
    if country['totalcases'] == '': return 0
    return country['totalcases']

def get_index(arr):
    try:
        return next(x for x, val in enumerate(arr) if val > 0)
    except:
        return len(arr)-1

def get_country_names(dataframe):
    return list(map(lambda x: x['countrylabel'].lower(), dataframe.at[0, 'data']))

def restructure(dataframe):
    dataframe['data'] = dataframe['data'].apply(lambda x: list(map(total_cases_for, x)))

    # Due to some inconsistency in the data coming from the server
    dataframe['date'] = dataframe['date'].apply(lambda x: x.replace('\r', ''))

def construct_dataframe_from(dataframe):
    country_names = get_country_names(dataframe)

    restructure(dataframe)

    new_dataframe = pandas.DataFrame(dataframe.data.to_list(), columns=country_names)
    new_dataframe['date'] = dataframe['date']
    return new_dataframe

def row_to_append(dataframe):
    row = []

    for (columnName, columnData) in dataframe.iteritems():
        if not (columnName == "date"): row.append(list(dataframe['date'].values)[get_index(columnData.values)])

    row.append(UNREASONABLE_FAR_DATE)
    return row

def insert_dates_row_to(dataframe):
    dataframe.loc[-1] = row_to_append(dataframe)
    dataframe.index += 1
    dataframe.sort_index(inplace=True)

def get_dataframe():
    r = requests.get(API_ENDPOINT)
    return pandas.DataFrame(r.json())

def write_csv(dataframe):
    dataframe.to_csv(CSV_FILE_PATH, index=False)

def main():
    dataframe = get_dataframe()

    new_dataframe = construct_dataframe_from(dataframe)

    # For data parsing purposes. Blame my reduced knowledge of gnuplot.
    insert_dates_row_to(new_dataframe)

    write_csv(new_dataframe)


if __name__ == '__main__':
    main()
