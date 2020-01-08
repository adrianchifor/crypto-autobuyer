import os
import sys
import logging
import ccxt

from ccxt.base.errors import ExchangeError
from flask import Flask

EXCHANGE = os.getenv("EXCHANGE", None)
API_KEY = os.getenv("API_KEY", None)
API_SECRET = os.getenv("API_SECRET", None)
PAIR = os.getenv("PAIR", None)
AMOUNT = os.getenv("AMOUNT", None)
TYPE = os.getenv("TYPE", "BUY")

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

try:
    ticker = exchange.fetch_ticker(PAIR)
except ExchangeError:
    print(f"Error: Couldn't find {PAIR} pair on {EXCHANGE} exchange")
    sys.exit(1)

TYPE = TYPE.upper()
if TYPE != "BUY" and TYPE != "SELL":
    print(f"Error: TYPE can only be 'BUY' or 'SELL'")
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
        amount_in_base_currency = round(float(AMOUNT) / float(ticker["last"]), 8)
        msg = f"{amount_in_base_currency} {BASE_PAIR} ({AMOUNT} {QUOTE_PAIR})"
        if TYPE == "BUY":
            exchange.create_market_buy_order(PAIR, amount_in_base_currency)
            msg = f"Bought {msg}"
        elif TYPE == "SELL":
            exchange.create_market_sell_order(PAIR, amount_in_base_currency)
            msg = f"Sold {msg}"

        app.logger.info(msg)
        return msg, 200
    except Exception as e:
        app.logger.error(e)
        return f"Error: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)
