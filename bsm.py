import numpy as np
import scipy


def d1(S, strike, time, r, sigma):
    return (np.log(S/strike) + (r + (sigma**2)/2)*time) / (sigma * np.sqrt(time))


def d2(S, strike, time, r, sigma):
    return d1(S, strike, time, r, sigma) - (sigma * np.sqrt(time))


def call_vega(S, strike, time, r, sigma):
    return S * np.sqrt(time) * scipy.stats.norm.pdf(d1(S, strike, time, r, sigma), 0.0, 1.0)


def put_vega(S, strike, time, r, sigma):
    return S * np.sqrt(time) * scipy.stats.norm.pdf(d1(S, strike, time, r, sigma), 0.0, 1.0)


def call_delta(S, strike, time, r, sigma):
    return scipy.stats.norm.cdf(d1(S, strike, time, r, sigma), 0.0, 1.0)


def put_delta(S, strike, time, r, sigma):
    return -scipy.stats.norm.cdf(-d1(S, strike, time, r, sigma), 0.0, 1.0)


def call_gamma(S, strike, time, r, sigma):
    return scipy.stats.norm.pdf(d1(S, strike, time, r, sigma), 0.0, 1.0) / (S*(sigma * np.sqrt(time)))


def put_gamma(S, strike, time, r, sigma):
    return scipy.stats.norm.pdf(d1(S, strike, time, r, sigma), 0.0, 1.0) / (S*(sigma * np.sqrt(time)))


def call_theta(S, strike, time, r, sigma):
    return (-S * scipy.stats.norm.pdf(d1(S, strike, time, r, sigma), 0.0, 1.0) * sigma/(2 * np.sqrt(time)) - r * strike * np.exp(-r*time) * scipy.stats.norm.cdf(d2(S, strike, time, r, sigma), 0.0, 1.0)) / 365


def put_theta(S, strike, time, r, sigma):
    return (-S * scipy.stats.norm.pdf(d1(S, strike, time, r, sigma), 0.0, 1.0) * sigma/(2 * np.sqrt(time)) + r * strike * np.exp(-r*time) * scipy.stats.norm.cdf(-d2(S, strike, time, r, sigma), 0.0, 1.0)) / 365


def call_rho(S, strike, time, r, sigma):
    return strike * time * np.exp(-r*time) * scipy.stats.norm.cdf(d2(S, strike, time, r, sigma), 0.0, 1.0) / 100


def put_rho(S, strike, time, r, sigma):
    return -strike * time * np.exp(-r * time) * scipy.stats.norm.cdf(-d2(S, strike, time, r, sigma), 0.0, 1.0) / 100


def call_greeks(S, strike, time, r, sigma):
    return call_delta(S, strike, time, r, sigma), call_gamma(S, strike, time, r, sigma), call_vega(S, strike, time, r, sigma), call_theta(S, strike, time, r, sigma), call_rho(S, strike, time, r, sigma)


def put_greeks(S, strike, time, r, sigma):
    return put_delta(S, strike, time, r, sigma), put_gamma(S, strike, time, r, sigma), put_vega(S, strike, time, r, sigma), put_theta(S, strike, time, r, sigma), put_rho(S, strike, time, r, sigma)


def call_price(S, strike, time, r, sigma):
    return S * scipy.stats.norm.cdf(d1(S, strike, time, r, sigma), 0.0, 1.0) - strike * np.exp(-r*time) * scipy.stats.norm.cdf(d2(S, strike, time, r, sigma), 0.0, 1.0)


# Calculates Implied Volatility of the Option Contract using the Newton-Raphson Method.
def call_implied_vol(S, strike, time, r, opt_price, sigma_est, iterations):

    for i in range(iterations):
        diff = call_price(S, strike, time, r, sigma_est)-opt_price
        sigma_est -= diff / call_vega(S, strike, time, r, sigma_est)
        if np.abs(diff) < 0.001:
            break
        else:
            continue
    return sigma_est