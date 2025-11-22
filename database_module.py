import datetime
import sqlite3


# These functions open a connection to the local SQLite database, execute the input query, and then close the
# connection to conserve memory. get_request is used to get data and thus returns a value. set_request is used to
# insert or update data and therefore has no return value.
def get_request(query, params=()):
    connection = sqlite3.connect('macrodb.db')
    sql_cursor = connection.cursor()
    sql_cursor.execute(query, params)
    result = sql_cursor.fetchall()
    sql_cursor.close()
    connection.close()
    return result


def set_request(query, params=()):
    connection = sqlite3.connect('macrodb.db')
    sql_cursor = connection.cursor()
    sql_cursor.execute(query, params)
    connection.commit()
    sql_cursor.close()
    connection.close()


# updates all daily data such as spot/forward rates
def update_daily_data(data):
    for row in data['rates']:
        query = f"insert into rates (current_rate, forecast_rate, bank_id, timestamp) values (?, ?, ?, ?)"
        params = (row['spot'], row['forward'], row['bank_id'], datetime.date.today().strftime('%Y-%m-%d'))
        set_request(query, params)
    for row in data['yields']:
        query = f"insert into yields (bank_id, onemo, threemo, sixmo, oney, twoy, threey, fivey, teny, twentyy, thirtyy, timestamp) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        params = (row['bank_id'], row['1MO'], row['3MO'], row['6MO'], row['1'], row['2'], row['3'], row['5'],row['10'], row['20'], row['30'], datetime.date.today().strftime('%Y-%m-%d'))
        set_request(query, params)


# returns spot and forward rate for a given central bank
def get_rates(bank_id):
    query = f"select rates.current_rate, rates.forecast_rate from rates where rates.bank_id = ? order by id desc limit 1"
    params = (bank_id,)
    return get_request(query, params)


# returns next CB decision date for a given central bank
def get_next_date(bank_id):
    today = datetime.date.today().strftime('%Y-%m-%d')
    query = f"select policydates.date from policydates where policydates.bank_id = ? and policydates.date > ? order by policydates.date asc limit 1"
    params = (bank_id, today)
    return get_request(query, params)


def get_yields(bank_id):
    query = f"select yields.onemo, yields.threemo, yields.sixmo, yields.oney, yields.twoy, yields.threey, yields.fivey, yields.teny, yields.twentyy, yields.thirtyy from yields where yields.bank_id = ? order by id desc limit 1"
    params = (bank_id,)
    return get_request(query, params)


def get_macro_data(bank_id):
    query = f"select macros.date from macros where macros.bank_id = ? order by macros.date desc limit 30"
    params = (bank_id,)
    return get_request(query, params)
