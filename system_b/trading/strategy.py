class Strategy:
    def __init__(self, config):
        self.config = config

    def check_entry_condition(self, prediction, has_position):
        # Enter if bullish signal and no open position
        return prediction == 1 and not has_position

    def check_trade_exit(self, entry_price, current_price, current_stop, current_target, current_prediction):
        """
        Implements revised logic:
          - If current price <= current_stop: SELL (stop-loss hit)
          - If current price >= current_target:
               * Re-run prediction (current_prediction provided)
               * If still bullish (==1), adjust:
                    new_stop = current_price
                    new_target = current_price * (1 + self.config.ADJUSTMENT_TARGET_PCT)
                    Action = "ADJUST"
               * Else, SELL (take-profit)
          - Else: HOLD
        """
        if current_price <= current_stop:
            return "SELL_STOPLOSS", current_stop, current_target
        if current_price >= current_target:
            if current_prediction == 1:
                new_stop = current_price   # lock in current price as stop-loss
                new_target = current_price * (1 + self.config.ADJUSTMENT_TARGET_PCT)
                return "ADJUST", new_stop, new_target
            else:
                return "SELL_TAKEPROFIT", current_stop, current_target
        return "HOLD", current_stop, current_target
