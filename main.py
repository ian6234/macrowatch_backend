from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import yfinance as yf

# Internal Imports
import calculations
import data_fetcher
import database_module

app = FastAPI()
scheduler = BackgroundScheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def upload_daily_data():
    data = data_fetcher.fetch_daily_data()
    database_module.update_daily_data(data)


def upload_spy_data():
    data = data_fetcher.fetch_spy_greeks()
    # database_module.update_spy_data(data)


@app.on_event("startup")
def startup_event():
    upload_daily_data()
    scheduler.add_job(upload_daily_data, 'interval', days=1)
    # scheduler.add_job(upload_spy_data, 'interval', hours=1)
    scheduler.start()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_json({"message": "Hello World"})


@app.get("/homepage-data")
async def homepage_data():

    current_rate_us, forward_rate_us = database_module.get_rates(1)[0]
    current_rate_uk, forward_rate_uk = database_module.get_rates(2)[0]

    us_policy_date = database_module.get_next_date(1)[0]
    uk_policy_date = database_module.get_next_date(2)[0]

    us_yields = database_module.get_yields(1)[0]
    us_yield_data = [{"name": '1-month', "yield": us_yields[0]}, {"name": '3-month', "yield": us_yields[1]},
                 {"name": '6-month', "yield": us_yields[2]}, {"name": '1-year', "yield": us_yields[3]},
                 {"name": '2-year', "yield": us_yields[4]}, {"name": '3-year', "yield": us_yields[5]},
                 {"name": '5-year', "yield": us_yields[6]}, {"name": '10-year', "yield": us_yields[7]},
                 {"name": '20-year', "yield": us_yields[8]}, {"name": '30-year', "yield": us_yields[9]}]

    spy_data = data_fetcher.fetch_spy_greeks()

    labels, matrix = data_fetcher.fetch_vol_correlation()

    return {"rate_forecasts": {
                "us_forecast": {
                    "id": "Federal Reserve",
                    "current_rate": current_rate_us,
                    "forecast": calculations.fed_rate_odds(current_rate_us, forward_rate_us),
                    "next_decision_date": us_policy_date},
                "uk_forecast": {
                    "id": "Bank of England",
                    "current_rate": current_rate_uk,
                    "forecast": calculations.fed_rate_odds(current_rate_uk, forward_rate_uk),
                    "next_decision_date": uk_policy_date}
                },
            "yield_curves":
            {
                "us_yield_curve": {
                    "id": "US Yield Curve",
                    "yields": us_yield_data,
                    "domain": [min(us_yields)-0.25, max(us_yields)+0.25]
                }
            },
            "macro_data":
            {
                "us_macro": {
                    "id": "US Macro Data",
                    "macro_data": 0,
                    "domain": [min(us_yields) - 0.25, max(us_yields) + 0.25]
                }
            },
            "options_data":
            {
                "SPY": {
                    "id": "S&P 500 Options (SPY ETF)",
                    "strikes": 0,
                    "expiries": 0,
                    "iv_surface": 0,
                    "greeks": 0
                },
                "SPY_ATM": {
                    "id": "S&P 500 Options (SPY ATM)",
                    "strike": spy_data['SPY_ATM']['STRIKE'],
                    "underlying": spy_data['SPY_ATM']['UNDERLYING'],
                    "expiry": spy_data['SPY_ATM']['EXPIRY'],
                    "implied_vol": spy_data['SPY_ATM']['IV'],
                    "greeks": spy_data['SPY_ATM']['GREEKS']
                }
            },
            "correlation_data":
            {
                "labels": labels,
                "matrix": matrix
            }

            }
