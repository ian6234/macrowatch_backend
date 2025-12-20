import asyncio
from datetime import datetime, timedelta

import requests
import scipy
import yfinance as yf
import pandas as pd
import math
import bsm
import numpy as np
import calculations

import database_module

# I should put this in an env file but I was in a hurry to upload please dont steal

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

    uk_spot = 0.04041
    yield_1m = 0.04041
    yield_3m = 0.03943
    uk_forward = calculations.calc_forward_rate(yield_1m, yield_3m, 1/12, 3/12)
    data['rates'].append({'bank_id': 2, 'spot': uk_spot*100, 'forward': uk_forward*100})

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


def fetch_spy_greeks():

    data = {}
    data['SPY_ATM'] = {}

    # SPY IV/Greeks data
    spy_ticker = yf.Ticker('SPY')
    expiries = spy_ticker.options
    # Target: 30 day expiry ATM call option
    target_date = datetime.today() + timedelta(days=30)
    # gets the time distance from target for each expiry in absolute number of seconds
    time_deltas = list(map(lambda x: abs((target_date - datetime.strptime(x, '%Y-%m-%d')).total_seconds()), expiries))
    # get the index for the closest expiry to target
    closest_expiry = expiries[np.argmin(time_deltas)]

    spy_chain = spy_ticker.option_chain(closest_expiry).calls

    # Next get closest to ATM call contract

    target_strike = spy_ticker.history(period='1d', interval='5m')['Close'][-1]

    strike_index = np.argmin(np.abs(spy_chain['strike'] - target_strike))
    closest_strike = spy_chain.iloc[strike_index]

    # Calculate time to expiry in years
    t = (datetime.strptime(expiries[np.argmin(time_deltas)], '%Y-%m-%d') - datetime.today()).total_seconds()/(60*60*24*365)

    # Grab r from our database
    r, forward_rate_us = database_module.get_rates(1)[0]
    r = r/100
    # Calculate iv (data provided by yahoo finance is inaccurate)

    implied_vol = bsm.call_implied_vol(target_strike, closest_strike['strike'], t, r, closest_strike['lastPrice'], 0.15, 50)
    greeks = bsm.call_greeks(target_strike, closest_strike['strike'], t, r, implied_vol)

    data['SPY_ATM']['STRIKE'] = closest_strike['strike']
    data['SPY_ATM']['UNDERLYING'] = target_strike
    data['SPY_ATM']['EXPIRY'] = closest_expiry
    data['SPY_ATM']['IV'] = implied_vol
    data['SPY_ATM']['GREEKS'] = greeks

    return data


# fetches prices on several asset classes, calculates 30-day vol and then constructs a correlation matrix
def fetch_vol_correlation():

    labels = ['SPY', '^FTSE', 'MNQ=F', 'GLD', 'SLV', '^TYX']
    price_data = yf.download(labels, period='1y', interval='1d')['Close']
    price_data = price_data.pct_change().dropna()
    vol_data = price_data.dropna(axis=0, how='any').rolling(window=30, min_periods=1).std().dropna(axis=0)

    matrix = np.corrcoef(vol_data, rowvar=False)

    return labels, matrix.tolist()
