import io
import os
import sys
import zipfile

from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import DataFrame


def get_download_url(url: str):
    res = requests.get(f'{url}/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html')
    soup = BeautifulSoup(res.text, 'html.parser')

    urls_to_download = soup.findAll('a', class_='download')

    for url in urls_to_download:
        if 'hist' in url['href']:
            url_with_hist_data = url['href']

    return url_with_hist_data


def download_zip_csv(url: str, url_to_download: str, path: str) -> str:
    res = requests.get(f'{url}{url_to_download}')
    files = zipfile.ZipFile(io.BytesIO(res.content))
    files.extractall(path)

    filenames = []
    for file in files.filelist:
        filenames.append(file.filename)

        if len(filenames) > 1:
            sys.stdout.write("Got two filenames. Don't know which to use. Stopping....\n")
            sys.exit(0)

    return filenames[0]


def _filter_helper(file: str, columns_to_filter: list) -> list:
    data = pd.read_csv(file)

    filtered_columns = DataFrame(data, columns=columns_to_filter)

    date_cond = pd.to_datetime(data['Date']) > pd.Timestamp(2018, 12, 31)
    filtered_data = filtered_columns.loc[date_cond]

    return filtered_data


def csv_by_dates(path: str, csv_file: str, columns_to_filter: list) -> str:
    data = _filter_helper(f'{path}/{csv_file}', columns_to_filter)
    clean_data = pd.DataFrame(columns=['Date', 'DKK', 'CAD'])

    for index, row in data.iterrows():
        clean_data = clean_data.append({'Date': row['Date'].replace('-', ''),
                                        'DKK': row['DKK'], 'CAD': row['CAD']}, ignore_index=True)

    filename = f'{path}/rates_by_dates.csv'
    clean_data.to_csv(filename, index=False)

    return filename


def csv_by_months(path: str, csv_file: str, columns_to_filter: list) -> str:
    dirty_data = _filter_helper(f'{path}/{csv_file}', columns_to_filter)
    dirty_data['Date'] = pd.to_datetime(dirty_data['Date'])

    clean_data = dirty_data.set_index('Date').resample('M')['DKK', 'CAD'].mean()[::-1]
    clean_data = clean_data.reset_index()
    clean_data = clean_data.round(decimals=4)

    clean_data['Date'] = clean_data.Date.dt.strftime('%Y%m')
    clean_data = clean_data.rename(columns={'Date': 'Month'})

    filename = f'{path}/rates_by_months.csv'
    clean_data.to_csv(filename, index=False)

    return filename


if __name__ == '__main__':
    root_url = 'https://www.ecb.europa.eu'
    current_folder = os.path.dirname(os.path.realpath(__file__))
    columns_filter = ['Date', 'DKK', 'CAD']

    download_url = get_download_url(root_url)
    raw_file = download_zip_csv(root_url, download_url, current_folder)
    csv_by_dates_name = csv_by_dates(current_folder, raw_file, columns_filter)
    csv_by_months_name = csv_by_months(current_folder, raw_file, columns_filter)

    result = f""" ============= Results =============
    Current folder: {current_folder}
    Root url: {root_url}
    Raw file: {current_folder}/{raw_file}
    Rates by Date CSV: {current_folder}/{csv_by_dates_name}
    Rates by Month CSV:{current_folder}/{csv_by_months_name}
    """
    sys.stdout.write(result)
