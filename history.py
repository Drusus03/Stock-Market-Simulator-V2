# history.py
# ─────────────────────────────────────────────
# Trade log — record, retrieve, save, load.
# NO print() statements — all results returned.
# ─────────────────────────────────────────────

import csv
from datetime import datetime

# In-memory trade log
trade_log = []

def record_trade(action, symbol, quantity, price, day):
    """
    Appends a trade to the in-memory log.

    Returns the trade dict that was recorded.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    trade = {
        "time":     timestamp,
        "day":      day,
        "action":   action,
        "symbol":   symbol,
        "quantity": quantity,
        "price":    price,
        "total":    round(quantity * price, 2),
    }
    trade_log.append(trade)
    return trade

def get_history_data():
    """
    Returns full trade log as a list of dicts.
    Used by UI to populate trade history table.
    """
    return list(trade_log)

def get_recent_trades(n=10):
    """Returns last n trades, most recent first."""
    return list(reversed(trade_log[-n:]))

def save_history(filename="history.csv"):
    """
    Saves all trades to a CSV file.

    Returns dict:
        success → bool
        message → result string
    """
    if not trade_log:
        return {"success": False, "message": "No trades to save."}
    try:
        with open(filename, "w", newline="") as f:
            fieldnames = ["time", "day", "action", "symbol",
                          "quantity", "price", "total"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(trade_log)
        return {"success": True, "message": f"Saved {len(trade_log)} trade(s)."}
    except Exception as e:
        return {"success": False, "message": f"Save failed: {str(e)}"}	