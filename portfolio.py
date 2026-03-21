# portfolio.py
# ─────────────────────────────────────────────
# Portfolio state, calculations, save/load.
# NO print() statements — all results returned.
# ─────────────────────────────────────────────

import json
import csv
import market
import history
from state import app_state

# ─────────────────────────────────────────────
# PORTFOLIO STATE
# ─────────────────────────────────────────────
balance          = 10000.0
holdings         = {}
value_history    = [10000.0]
SAVE_FILE        = "portfolio.json"
STARTING_BALANCE = 10000.0   # Reference for P&L calculation

# ─────────────────────────────────────────────
# CALCULATIONS
# ─────────────────────────────────────────────
def get_total_value():
    """Returns total portfolio worth = cash + all stock positions."""
    stock_value = 0.0
    for symbol, data in holdings.items():
        price = market.get_price(symbol)
        if price is not None:
            stock_value += data["shares"] * price
    return round(balance + stock_value, 2)

def snapshot_value():
    """
    Records current total portfolio value into value_history.
    Called every time a new day advances.
    """
    value_history.append(get_total_value())

def get_portfolio_data():
    """
    Returns complete portfolio snapshot as a structured dict.
    Used by UI to populate portfolio panel.
    """
    total       = get_total_value()
    profit_loss = total - STARTING_BALANCE

    holdings_data = []
    for symbol, data in holdings.items():
        shares  = data["shares"]
        avg_buy = data["avg_buy"]
        now     = market.get_price(symbol)
        if now is None:
            continue
        pl     = round((now - avg_buy) * shares, 2)
        pl_pct = round(((now - avg_buy) / avg_buy) * 100, 2) if avg_buy > 0 else 0.0
        holdings_data.append({
            "symbol":         symbol,
            "shares":         shares,
            "avg_buy":        avg_buy,
            "current_price":  now,
            "position_value": round(now * shares, 2),
            "pl":             pl,
            "pl_pct":         pl_pct,
        })

    return {
        "balance":         balance,
        "total_value":     total,
        "profit_loss":     round(profit_loss, 2),
        "profit_loss_pct": round((profit_loss / STARTING_BALANCE) * 100, 2),
        "holdings":        holdings_data,
        "value_history":   list(value_history),
    }

# ─────────────────────────────────────────────
# ADD BALANCE
# ─────────────────────────────────────────────
def add_balance(amount):
    global balance
    if not isinstance(amount, (int, float)) or amount <= 0:
        return {"success": False, "message": "Amount must be greater than 0."}
    balance = round(balance + amount, 2)
    return {
        "success":     True,
        "message":     f"Added ${amount:,.2f} to account.",
        "new_balance": balance,
    }

# ─────────────────────────────────────────────
# SAVE
# Saves: balance, holdings, value_history,
#        current_day, full market state
# ─────────────────────────────────────────────
def save_portfolio():
    """
    Saves complete simulator state to portfolio.json.

    BUG 2 FIX: Now saves current_day and full market state
    (stock prices + complete price history per stock) so that
    on next load, the day counter and all charts restore
    correctly to where you left off.
    """
    try:
        # Capture full market state per stock
        market_state = {}
        for sym, data in market.STOCKS.items():
            market_state[sym] = {
                "price":   data["price"],
                "history": list(data["history"]),
            }

        save_data = {
            "balance":       balance,
            "holdings":      holdings,
            "value_history": value_history,
            "current_day":   market.current_day,
            "market_state":  market_state,
            "news_feed":     app_state.news_feed,   # save full news history
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(save_data, f, indent=4)

        history.save_history()
        return {"success": True, "message": "Portfolio saved successfully."}
    except Exception as e:
        return {"success": False, "message": f"Save failed: {str(e)}"}

# ─────────────────────────────────────────────
# LOAD PORTFOLIO
# Restores: balance, holdings, value_history,
#           current_day, full market state
# ─────────────────────────────────────────────
def load_portfolio():
    """
    Loads complete simulator state from portfolio.json.

    BUG 2 FIX: Now restores current_day (so day counter
    doesn't reset to 1) and full market state (so all stock
    prices and chart histories restore to saved values,
    not Day-1 opening prices).
    """
    global balance, holdings, value_history
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        # Restore portfolio state
        balance       = data.get("balance",       10000.0)
        holdings      = data.get("holdings",      {})
        value_history = data.get("value_history", [balance])

        # Restore market day counter
        market.current_day = data.get("current_day", 1)

        # Restore full market prices and history per stock
        market_state = data.get("market_state", {})
        for sym, mdata in market_state.items():
            if sym in market.STOCKS:
                market.STOCKS[sym]["price"]   = mdata.get(
                    "price", market.STOCKS[sym]["price"])
                market.STOCKS[sym]["history"] = mdata.get(
                    "history", market.STOCKS[sym]["history"])

        # Restore news feed so NEWS panel shows previous events
        saved_news = data.get("news_feed", [])
        if saved_news:
            app_state.news_feed = saved_news

        return {
            "success": True,
            "message": f"Portfolio loaded. Balance: ${balance:,.2f}"
        }
    except FileNotFoundError:
        return {"success": False, "message": "No save file found. Starting fresh."}
    except json.JSONDecodeError:
        return {"success": False, "message": "Save file corrupted. Starting fresh."}
    except Exception as e:
        return {"success": False, "message": f"Load failed: {str(e)}"}

# ─────────────────────────────────────────────
# LOAD HISTORY
# ─────────────────────────────────────────────
def load_history():
    """Loads trade history from history.csv into history.trade_log."""
    try:
        with open("history.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                history.trade_log.append({
                    "time":     row["time"],
                    "day":      int(row["day"]),
                    "action":   row["action"],
                    "symbol":   row["symbol"],
                    "quantity": int(row["quantity"]),
                    "price":    float(row["price"]),
                    "total":    float(row["total"]),
                })
        return {"success": True, "message": "Trade history loaded."}
    except FileNotFoundError:
        return {"success": False, "message": "No history file found. Starting fresh."}
    except Exception as e:
        return {"success": False, "message": f"History load failed: {str(e)}"}

# ─────────────────────────────────────────────
# PORTFOLIO VALUE CHART (standalone fallback)
# ─────────────────────────────────────────────
def plot_portfolio_value():
    """Plots portfolio value over time using matplotlib."""
    import matplotlib.pyplot as plt
    if len(value_history) < 2:
        return {"success": False, "message": "Need at least 2 days of data to plot."}

    days        = list(range(1, len(value_history) + 1))
    values      = value_history
    start       = values[0]
    final_color = "#51cf66" if values[-1] >= start else "#ff6b6b"

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(days, values, color=final_color, linewidth=2.5,
            marker="o", markersize=4)
    ax.fill_between(days, values, start, alpha=0.15, color=final_color)
    ax.axhline(y=start, color="gray", linestyle="--", alpha=0.7,
               label=f"Start: ${start:,.0f}")
    ax.set_title("Portfolio Value Over Time", fontsize=14, fontweight="bold")
    ax.set_xlabel("Day")
    ax.set_ylabel("Total Value ($)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    return {"success": True, "message": ""}