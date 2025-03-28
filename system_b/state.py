class Position:
    def __init__(self, symbol, entry_price, quantity, stop_loss, take_profit):
        self.symbol = symbol
        self.entry_price = entry_price
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.take_profit = take_profit

class BotState:
    def __init__(self):
        self.positions = {}  # symbol -> Position

    def has_position(self, symbol):
        return symbol in self.positions

    def open_position(self, symbol, entry_price, quantity, stop_loss, take_profit):
        self.positions[symbol] = Position(symbol, entry_price, quantity, stop_loss, take_profit)

    def close_position(self, symbol):
        if symbol in self.positions:
            del self.positions[symbol]

    def get_position(self, symbol):
        return self.positions.get(symbol)
