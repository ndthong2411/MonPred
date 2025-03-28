from flask import Flask, jsonify, render_template
from state import BotState

app = Flask(__name__)
# For simplicity, using an in-memory state; in production, share state between bot and UI.
state = BotState()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/state")
def get_state():
    positions = [{"symbol": pos.symbol, "entry_price": pos.entry_price,
                  "quantity": pos.quantity, "stop_loss": pos.stop_loss,
                  "take_profit": pos.take_profit}
                 for pos in state.positions.values()]
    return jsonify(positions)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
