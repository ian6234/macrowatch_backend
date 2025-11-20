import datetime

import requests
import scipy
import yfinance as yf
import pandas as pd
import math
import bsm

# API-KEY: 823ad1c875548ff1111d0343ffa23ab0

api_key = '823ad1c875548ff1111d0343ffa23ab0'


def fetch_daily_data():

    data = {}
    data['rates'] = []
    data['yields'] = []

    # us rates data (spot + forward)
    url = f'https://api.stlouisfed.org/fred/series/observations?series_id=EFFR&api_key={api_key}&file_type=json'

    response = requests.get(url)
    spot = response.json()['observations'][-1]['value']

    df = yf.download("ZQ=F", period="1d", interval="30m", progress=False, threads=False)
    latest = float(df["Close"].iloc[-1]) if not df.empty else None
    forward = 100-latest
    data['rates'].append({'bank_id': 1, 'spot': spot, 'forward': forward})

    # uk rates data (spot+forward)

    data['rates'].append({'bank_id': 2, 'spot': 4.00, 'forward': 3.94})

    # US yields data
    yield_data = {'bank_id': 1}
    series_ids = ['1MO', '3MO', '6MO', '1', '2', '3', '5', '10', '20', '30']
    for series_id in series_ids:
        url = f'https://api.stlouisfed.org/fred/series/observations?series_id=DGS{series_id}&api_key={api_key}&file_type=json'
        response = requests.get(url)
        yields = response.json()['observations'][-1]['value']
        yield_data[series_id] = yields
    data['yields'].append(yield_data)



    return data


def fetch_spy_iv():
    # SPY IV/Greeks data
    spy_ticker = yf.Ticker('SPY')
    expiries = spy_ticker.options
    print(expiries)
    for exp in expiries[:5]:
        spy_options = spy_ticker.option_chain(exp)
        print(spy_options.calls['impliedVolatility'])

