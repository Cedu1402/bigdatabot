import os

from flask import Flask, render_template

from database.token_trade_history_table import get_trade_stats
from database.token_watch_table import get_current_token_watch_stats

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))


# Route for the homepage
@app.route('/')
def home():
    try:
        token_watch_stats = get_current_token_watch_stats()
        trade_stats = get_trade_stats()

        combined_data = {**token_watch_stats, **trade_stats}

        # Pass data to template
        return render_template('index.html', data=combined_data)

    except Exception as e:
        return f"Error: {e}"


if __name__ == '__main__':
    app.run(debug=False, port=4359)
