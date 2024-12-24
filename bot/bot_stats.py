import logging
import os

from dotenv import load_dotenv
from flask import Flask, render_template

from database.token_trade_history_table import get_trade_stats, get_open_trades
from database.token_watch_table import get_current_token_watch_stats
from structure_log.logger_setup import setup_logger

setup_logger("bot_stats")
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))


# Route for the homepage
@app.route('/')
def home():
    try:
        load_dotenv()
        token_watch_stats = get_current_token_watch_stats()
        trade_stats = get_trade_stats()
        open_trades = get_open_trades()

        combined_data = {**token_watch_stats, **trade_stats, **{'open_trades': open_trades}}

        # Pass data to template
        return render_template('index.html', data=combined_data)

    except Exception as e:
        return f"Error: {e}"


if __name__ == '__main__':
    load_dotenv()
    app.run(debug=False, port=4359)
