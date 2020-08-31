import os
import sys
import time
import logging
import ccxt

from flask import Flask
from ccxt.base.errors import NetworkError

logger = logging.getLogger('werkzeug')
if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
    logger = logging.getLogger("gunicorn.error")

EXCHANGE = os.getenv("EXCHANGE", None)
API_KEY = os.getenv("API_KEY", None)
API_SECRET = os.getenv("API_SECRET", None)
PAIR = os.getenv("PAIR", None)
AMOUNT = os.getenv("AMOUNT", None)
TAKE_PROFIT = os.getenv("TAKE_PROFIT", None)

if not EXCHANGE or not API_KEY or not API_SECRET or not PAIR or not AMOUNT:
    logger.error(
        "Error: EXCHANGE, API_KEY, API_SECRET, PAIR AND AMOUNT env vars are required")
    sys.exit(1)

exchange_config = {
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "enableRateLimit": True,
}
if "PASSWORD" in os.environ:
    exchange_config["password"] = os.environ["PASSWORD"]

exchange = getattr(ccxt, EXCHANGE)(exchange_config)

if "/" in PAIR:
    BASE_PAIR, QUOTE_PAIR = PAIR.split("/")
else:
    logger.error(f"Error: Incorrect formatting of pair {PAIR}, needs to be <BASE>/<QUOTE>")
    sys.exit(1)

app = Flask(__name__)


@app.route("/", methods=["POST"])
def main():
    try:
        price = get_price()
        base_balance = get_base_balance()
        amount_in_base_currency = round(float(AMOUNT) / price, 8)
        market_buy(amount_in_base_currency, base_balance)
        logger.info((f"Bought {amount_in_base_currency} {BASE_PAIR} at "
                     f"{price} {QUOTE_PAIR} ({AMOUNT} {QUOTE_PAIR})"))

        if TAKE_PROFIT:
            tp_price = round(price + (price * (int(TAKE_PROFIT) / 100)), 1)
            tp_amount = int(amount_in_base_currency * tp_price)
            limit_sell(amount_in_base_currency, tp_price)
            logger.info((f"Limit sell set for {amount_in_base_currency} {BASE_PAIR} at "
                         f"{tp_price} {QUOTE_PAIR} ({tp_amount} {QUOTE_PAIR})"))

        return "OK", 200
    except Exception as e:
        logger.error(e)
        return f"Error: {e}", 500


def get_price(retries: int = 3) -> float:
    try:
        ticker = exchange.fetch_ticker(PAIR)
        return float(ticker["last"])
    except NetworkError as e:
        if retries <= 0:
            raise
        logger.error(f"get_price failed: {e}, retrying...")
        time.sleep(1)
        return get_price(retries-1)


def get_base_balance(retries: int = 3) -> float:
    try:
        balance = exchange.fetch_balance()
        return balance["free"][BASE_PAIR]
    except NetworkError as e:
        if retries <= 0:
            raise
        logger.error(f"get_base_balance failed: {e}, retrying...")
        time.sleep(1)
        return get_base_balance(retries-1)


def market_buy(amount: float, base_balance: float, retries: int = 3):
    try:
        exchange.create_market_buy_order(PAIR, amount)
    except NetworkError as e:
        if retries <= 0:
            raise
        logger.error(f"market_buy failed: {e}, checking balance...")
        time.sleep(1)
        new_base_balance = get_base_balance()
        if new_base_balance > base_balance:
            logger.error(f"market_buy: balance increased, marking as successful")
            return
        logger.error(f"market_buy: balance did not increase, retrying...")
        market_buy(amount, base_balance, retries-1)


def limit_sell(amount: float, price: float, retries: int = 3):
    try:
        exchange.create_limit_sell_order(PAIR, amount, price)
    except NetworkError as e:
        if retries <= 0:
            raise
        logger.error(f"limit_sell failed: {e}, retrying...")
        time.sleep(1)
        limit_sell(amount, price, retries-1)


if __name__ == "__main__":
    app.run(debug=True)
