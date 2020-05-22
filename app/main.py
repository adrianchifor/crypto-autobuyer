import os
import sys
import logging
import ccxt

from flask import Flask

EXCHANGE = os.getenv("EXCHANGE", None)
API_KEY = os.getenv("API_KEY", None)
API_SECRET = os.getenv("API_SECRET", None)
PAIR = os.getenv("PAIR", None)
AMOUNT = os.getenv("AMOUNT", None)
TAKE_PROFIT = os.getenv("TAKE_PROFIT", None)

if not EXCHANGE or not API_KEY or not API_SECRET or not PAIR or not AMOUNT:
    print("Error: EXCHANGE, API_KEY, API_SECRET, PAIR AND AMOUNT env vars are required")
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
    print(f"Error: Incorrect formatting of pair {PAIR}, needs to be <BASE>/<QUOTE>")
    sys.exit(1)

app = Flask(__name__)


@app.before_first_request
def setup_logging():
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route("/", methods=["POST"])
def main():
    try:
        ticker = exchange.fetch_ticker(PAIR)
        price = float(ticker["last"])
        amount_in_base_currency = round(float(AMOUNT) / price, 8)

        exchange.create_market_buy_order(PAIR, amount_in_base_currency)
        app.logger.info((f"Bought {amount_in_base_currency} {BASE_PAIR} at "
                         f"{price} {QUOTE_PAIR} ({AMOUNT} {QUOTE_PAIR})"))

        if TAKE_PROFIT:
            tp_price = round(price + (price * (int(TAKE_PROFIT) / 100)), 1)
            tp_amount = int(amount_in_base_currency * tp_price)
            exchange.create_limit_sell_order(PAIR, amount_in_base_currency, tp_price)
            app.logger.info((f"Limit sell set for {amount_in_base_currency} {BASE_PAIR} at "
                             f"{tp_price} {QUOTE_PAIR} ({tp_amount} {QUOTE_PAIR})"))

        return "OK", 200
    except Exception as e:
        app.logger.error(e)
        return f"Error: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)
