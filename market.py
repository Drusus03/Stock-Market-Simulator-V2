# market.py
# ─────────────────────────────────────────────
# Stock universe, price simulation, news events,
# live tick generation, and chart functions.
# NO print() statements — all data returned as dicts.
# ─────────────────────────────────────────────

import random
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────
# STOCK UNIVERSE
# ─────────────────────────────────────────────
STOCKS = {
    "AAPL": {"price": 175.0,  "history": [175.0]},
    "TSLA": {"price": 210.0,  "history": [210.0]},
    "GOOG": {"price": 140.0,  "history": [140.0]},
    "AMZN": {"price": 185.0,  "history": [185.0]},
    "MSFT": {"price": 420.0,  "history": [420.0]},
}

current_day = 1

# ─────────────────────────────────────────────
# BASIC GETTERS
# ─────────────────────────────────────────────
def get_price(symbol):
    """Returns official closing price of a stock."""
    if symbol in STOCKS:
        return STOCKS[symbol]["price"]
    return None

def get_history(symbol):
    """Returns full price history list of a stock."""
    if symbol in STOCKS:
        return list(STOCKS[symbol]["history"])
    return []

def get_all_symbols():
    return list(STOCKS.keys())

# ─────────────────────────────────────────────
# MARKET SNAPSHOT — structured data for UI
# ─────────────────────────────────────────────
def get_market_data():
    """
    Returns list of dicts, one per stock.
    Used by UI to populate market table.
    """
    result = []
    for symbol, data in STOCKS.items():
        price   = data["price"]
        history = data["history"]
        if len(history) > 1:
            prev       = history[-2]
            change     = price - prev
            change_pct = (change / prev) * 100
        else:
            change     = 0.0
            change_pct = 0.0
        result.append({
            "symbol":     symbol,
            "price":      price,
            "change":     round(change, 2),
            "change_pct": round(change_pct, 2),
            "history":    list(history),
        })
    return result

# ─────────────────────────────────────────────
# LIVE TICK — intra-day micro-movement
# Does NOT advance day or touch official history.
# Called every ~2 seconds by the UI animation timer.
# ─────────────────────────────────────────────
def generate_tick():
    """
    Generates tiny random intra-day price movements.
    These are DISPLAY ONLY — not saved to history.
    Volatility: 0.05% per tick (realistic feel).

    Returns: {symbol: tick_price, ...}
    """
    tick_prices = {}
    for symbol, data in STOCKS.items():
        price     = data["price"]
        # Small Gaussian noise around official price
        tick_shock = random.gauss(0, 0.0005)
        tick_price = round(price * (1 + tick_shock), 2)
        tick_price = max(tick_price, 1.0)
        tick_prices[symbol] = tick_price
    return tick_prices

# ─────────────────────────────────────────────
# NEXT DAY — official price advance
# ─────────────────────────────────────────────
def next_day():
    """
    Advances market by exactly one official day.
    - Updates STOCKS[symbol]["price"]
    - Appends to STOCKS[symbol]["history"]
    - Generates news events (10% chance per stock)

    Returns dict:
        day          → new current_day
        news_events  → list of news dicts
        price_updates→ {symbol: new_price}
    """
    global current_day
    current_day += 1
    news_events   = []
    price_updates = {}

    for symbol, data in STOCKS.items():
        price     = data["price"]
        news_roll = random.random()

        if news_roll < 0.05:
            # BAD NEWS → sharp drop
            shock    = random.uniform(-0.15, -0.05)
            headline = random.choice(NEGATIVE_HEADLINES[symbol])
            news_events.append({
                "type":       "bad",
                "symbol":     symbol,
                "headline":   headline,
                "change_pct": round(abs(shock) * 100, 1),
            })
        elif news_roll < 0.10:
            # GOOD NEWS → sharp rise
            shock    = random.uniform(0.05, 0.15)
            headline = random.choice(POSITIVE_HEADLINES[symbol])
            news_events.append({
                "type":       "good",
                "symbol":     symbol,
                "headline":   headline,
                "change_pct": round(shock * 100, 1),
            })
        else:
            # Normal day: Gaussian random walk
            drift      = 0.001
            volatility = 0.02
            shock      = drift + volatility * random.gauss(0, 1)

        new_price = round(price * (1 + shock), 2)
        new_price = max(new_price, 1.0)

        STOCKS[symbol]["price"] = new_price
        STOCKS[symbol]["history"].append(new_price)
        price_updates[symbol] = new_price

    return {
        "day":           current_day,
        "news_events":   news_events,
        "price_updates": price_updates,
    }

# ─────────────────────────────────────────────
# NEWS HEADLINES
# ─────────────────────────────────────────────
POSITIVE_HEADLINES = {
    "AAPL": ["iPhone sales surge!", "Apple announces new AI chip.", "Record quarterly earnings."],
    "TSLA": ["Tesla gigafactory opens.", "Record deliveries this quarter.", "New model revealed."],
    "GOOG": ["Google wins antitrust case.", "Search revenue beats estimates.", "AI assistant launches."],
    "AMZN": ["Amazon Prime hits 300M users.", "AWS cloud revenue explodes.", "Record holiday sales."],
    "MSFT": ["Azure growth beats rivals.", "Copilot adoption soaring.", "Record cloud revenue."],
}

NEGATIVE_HEADLINES = {
    "AAPL": ["iPhone sales disappoint.", "Supply chain crisis hits.", "Regulatory probe launched."],
    "TSLA": ["Recall issued for 50K vehicles.", "Elon sells more stock.", "Delivery miss reported."],
    "GOOG": ["Antitrust fine issued.", "Ad revenue slows down.", "Data breach reported."],
    "AMZN": ["Union strike disrupts ops.", "AWS outage reported.", "Earnings miss estimates."],
    "MSFT": ["Security vulnerability found.", "Layoffs announced.", "Cloud growth slows."],
}

# ─────────────────────────────────────────────
# CHART FUNCTIONS (kept for fallback use)
# Phase 2 will embed these inside tkinter instead.
# ─────────────────────────────────────────────
def plot_stock(symbol):
    """Plots single stock price history."""
    symbol = symbol.upper()
    if symbol not in STOCKS:
        return {"success": False, "message": f"Stock '{symbol}' not found."}
    prices = STOCKS[symbol]["history"]
    days   = list(range(1, len(prices) + 1))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(days, prices, color="#00bfff", linewidth=2, marker="o", markersize=3)
    ax.fill_between(days, prices, alpha=0.1, color="#00bfff")
    ax.set_title(f"{symbol} — Price History", fontsize=14, fontweight="bold")
    ax.set_xlabel("Day")
    ax.set_ylabel("Price ($)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    return {"success": True, "message": ""}

def plot_all_stocks():
    """Plots all stocks in 2x3 grid."""
    symbols = list(STOCKS.keys())
    colors  = ["#00bfff", "#ff6b6b", "#51cf66", "#ffd43b", "#cc5de8"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle("Stock Market — All Prices", fontsize=16, fontweight="bold")
    for i, symbol in enumerate(symbols):
        row    = i // 3
        col    = i % 3
        ax     = axes[row][col]
        prices = STOCKS[symbol]["history"]
        days   = list(range(1, len(prices) + 1))
        ax.plot(days, prices, color=colors[i], linewidth=2)
        ax.fill_between(days, prices, alpha=0.15, color=colors[i])
        ax.set_title(symbol, fontweight="bold")
        ax.set_xlabel("Day")
        ax.set_ylabel("$")
        ax.grid(True, alpha=0.3)
    axes[1][2].set_visible(False)
    plt.tight_layout()
    plt.show()
    return {"success": True, "message": ""}