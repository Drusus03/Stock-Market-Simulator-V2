# bot.py
# ─────────────────────────────────────────────
# Intelligent trading bot.
#
# Strategy: Triple Confirmation System
#   Indicator 1 → MA Crossover  (trend direction)
#   Indicator 2 → RSI           (overbought/oversold)
#   Indicator 3 → MACD          (momentum confirmation)
#
# Signal scoring:
#   Each indicator contributes -1, 0, or +1
#   Total score range: -3 to +3
#
#   Score ≥ +2 → STRONG BUY  (execute trade)
#   Score == +1 → BUY         (execute trade)
#   Score == 0  → HOLD        (no trade)
#   Score == -1 → SELL        (execute trade)
#   Score ≤ -2 → STRONG SELL  (execute trade)
#
# NO print() statements — all results returned.
# ─────────────────────────────────────────────

import market
import portfolio
import trading


# ═══════════════════════════════════════════════
# TECHNICAL INDICATORS
# ═══════════════════════════════════════════════

def simple_moving_average(prices: list, window: int):
    """
    SMA: Unweighted average of last 'window' prices.
    Returns None if insufficient data.

    Example (window=3): [100, 102, 98, 105] → avg(98,105) — wait,
    avg of last 3: avg(102, 98, 105) = 101.67
    """
    if len(prices) < window:
        return None
    return round(sum(prices[-window:]) / window, 4)


def exponential_moving_average(prices: list, period: int):
    """
    EMA: Weighted average giving more weight to recent prices.

    Formula per step:
        EMA_today = price_today × k + EMA_yesterday × (1 - k)
        k = 2 / (period + 1)

    Seeded with SMA of first 'period' prices.
    Returns None if insufficient data.
    """
    if len(prices) < period:
        return None

    k   = 2.0 / (period + 1)
    ema = sum(prices[:period]) / period  # seed = SMA

    for price in prices[period:]:
        ema = price * k + ema * (1 - k)

    return round(ema, 4)


def calculate_rsi(prices: list, period: int = 14):
    """
    RSI: Relative Strength Index (0 to 100 scale).

    Formula:
        RS  = avg_gain / avg_loss  (over last 'period' moves)
        RSI = 100 - (100 / (1 + RS))

    Interpretation:
        RSI > 70 → Overbought → potential SELL signal
        RSI < 30 → Oversold   → potential BUY signal
        30–70    → Neutral

    Returns None if insufficient data (need period+1 prices).
    """
    if len(prices) < period + 1:
        return None

    # Calculate price deltas for the last 'period' moves
    recent = prices[-(period + 1):]
    gains  = []
    losses = []

    for i in range(1, len(recent)):
        delta = recent[i] - recent[i - 1]
        if delta > 0:
            gains.append(delta)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(delta))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100.0  # All gains, no losses → RSI = 100

    rs  = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return round(rsi, 2)


def calculate_macd(prices: list, fast: int = 12,
                   slow: int = 26, signal_period: int = 9):
    """
    MACD: Moving Average Convergence Divergence.

    Components:
        MACD Line   = EMA(fast) - EMA(slow)
        Signal Line = EMA(signal_period) of MACD Line history
        Histogram   = MACD Line - Signal Line

    Interpretation:
        Histogram > 0 → bullish momentum → BUY signal
        Histogram < 0 → bearish momentum → SELL signal
        Histogram crossing zero → trend reversal

    Returns dict or None if insufficient data.
    Minimum required prices: slow + signal_period
    """
    if len(prices) < slow + signal_period:
        return None

    # Build MACD line history
    macd_line_history = []
    for i in range(slow, len(prices) + 1):
        subset   = prices[:i]
        ema_fast = exponential_moving_average(subset, fast)
        ema_slow = exponential_moving_average(subset, slow)
        if ema_fast is not None and ema_slow is not None:
            macd_line_history.append(ema_fast - ema_slow)

    if len(macd_line_history) < signal_period:
        return None

    # Current MACD line value
    macd_line = macd_line_history[-1]

    # Signal line = EMA of MACD line history
    k           = 2.0 / (signal_period + 1)
    signal_line = sum(macd_line_history[:signal_period]) / signal_period
    for val in macd_line_history[signal_period:]:
        signal_line = val * k + signal_line * (1 - k)

    histogram = macd_line - signal_line

    return {
        "macd_line":   round(macd_line,   4),
        "signal_line": round(signal_line, 4),
        "histogram":   round(histogram,   4),
    }


# ═══════════════════════════════════════════════
# SIGNAL SCORING ENGINE
# ═══════════════════════════════════════════════

def _score_ma(ma5, ma20):
    """
    MA Crossover score.
    +1 if ma5 > ma20 (short above long → uptrend)
    -1 if ma5 < ma20 (short below long → downtrend)
     0 if equal or unavailable
    """
    if ma5 is None or ma20 is None:
        return 0, "MA: Insufficient data"
    if ma5 > ma20:
        diff_pct = ((ma5 - ma20) / ma20) * 100
        return +1, f"MA Cross: Bullish (+{diff_pct:.2f}% spread)"
    elif ma5 < ma20:
        diff_pct = ((ma20 - ma5) / ma20) * 100
        return -1, f"MA Cross: Bearish (-{diff_pct:.2f}% spread)"
    return 0, "MA Cross: Neutral (equal)"


def _score_rsi(rsi):
    """
    RSI score.
    +1 if rsi < 30 (oversold → buy opportunity)
    -1 if rsi > 70 (overbought → sell opportunity)
     0 if neutral or unavailable
    """
    if rsi is None:
        return 0, "RSI: Insufficient data"
    if rsi < 30:
        return +1, f"RSI {rsi:.1f}: Oversold — BUY zone"
    elif rsi > 70:
        return -1, f"RSI {rsi:.1f}: Overbought — SELL zone"
    return 0, f"RSI {rsi:.1f}: Neutral zone (30–70)"


def _score_macd(macd):
    """
    MACD Histogram score.
    +1 if histogram > 0 (bullish momentum)
    -1 if histogram < 0 (bearish momentum)
     0 if zero or unavailable
    """
    if macd is None:
        return 0, "MACD: Insufficient data"
    h = macd["histogram"]
    if h > 0:
        return +1, f"MACD Histogram: +{h:.4f} (Bullish)"
    elif h < 0:
        return -1, f"MACD Histogram: {h:.4f} (Bearish)"
    return 0, f"MACD Histogram: 0 (Neutral)"


def _score_to_signal(score):
    """Converts numeric score to signal label."""
    if   score >=  2: return "STRONG BUY"
    elif score ==  1: return "BUY"
    elif score == -1: return "SELL"
    elif score <= -2: return "STRONG SELL"
    return "HOLD"


# ═══════════════════════════════════════════════
# FULL STOCK ANALYSIS
# ═══════════════════════════════════════════════

def analyze_stock(symbol: str):
    """
    Runs complete technical analysis on one stock.
    Computes MA, RSI, MACD and combines into a score.

    Returns a complete analysis dict:
        symbol        → stock symbol
        price         → current price
        signal        → STRONG BUY / BUY / HOLD / SELL / STRONG SELL / WAIT
        score         → -3 to +3
        reasons       → list of explanation strings
        ma5, ma20     → moving averages
        rsi           → RSI value
        macd          → MACD dict
        data_ready    → False if not enough history yet
    """
    prices = market.get_history(symbol)
    price  = market.get_price(symbol)

    # ── Compute all indicators ──
    ma5  = simple_moving_average(prices, 5)
    ma20 = simple_moving_average(prices, 20)
    rsi  = calculate_rsi(prices, 14)
    macd = calculate_macd(prices, 12, 26, 9)

    # Minimum data check (need 20 days for MA20)
    if ma20 is None:
        days_needed = max(0, 20 - len(prices))
        return {
            "symbol":      symbol,
            "price":       price,
            "signal":      "WAIT",
            "score":       0,
            "reasons":     [f"Need {days_needed} more day(s) for full analysis."],
            "ma5":         ma5,
            "ma20":        ma20,
            "rsi":         rsi,
            "macd":        macd,
            "data_ready":  False,
        }

    # ── Score each indicator ──
    ma_score,   ma_reason   = _score_ma(ma5, ma20)
    rsi_score,  rsi_reason  = _score_rsi(rsi)
    macd_score, macd_reason = _score_macd(macd)

    total_score = ma_score + rsi_score + macd_score
    signal      = _score_to_signal(total_score)
    reasons     = [ma_reason, rsi_reason, macd_reason]

    return {
        "symbol":      symbol,
        "price":       price,
        "signal":      signal,
        "score":       total_score,
        "reasons":     reasons,
        "ma5":         round(ma5, 2)  if ma5  else None,
        "ma20":        round(ma20, 2) if ma20 else None,
        "rsi":         rsi,
        "macd":        macd,
        "data_ready":  True,
    }


def get_all_analyses():
    """
    Returns technical analysis for ALL stocks without trading.
    Used by the UI signal dashboard to display live bot readings.
    """
    return {symbol: analyze_stock(symbol) for symbol in market.STOCKS}


# ═══════════════════════════════════════════════
# BOT EXECUTION
# ═══════════════════════════════════════════════

def run_bot(shares_per_trade: int = 2):
    """
    Runs the trading bot across all stocks.

    Trading rules:
        STRONG BUY / BUY  → buy if funds available
        STRONG SELL / SELL → sell if shares owned
        HOLD / WAIT        → no action

    Returns:
        actions  → list of action dicts (what the bot did)
        analyses → dict of full analysis per symbol
    """
    actions  = []
    analyses = {}

    for symbol in market.STOCKS:
        analysis         = analyze_stock(symbol)
        analyses[symbol] = analysis
        signal           = analysis["signal"]

        # ── Not enough data yet ──
        if not analysis["data_ready"]:
            actions.append({
                "symbol":   symbol,
                "action":   "WAIT",
                "signal":   "WAIT",
                "message":  analysis["reasons"][0],
                "analysis": analysis,
            })
            continue

        # ── BUY signal ──
        if signal in ("STRONG BUY", "BUY"):
            cost = analysis["price"] * shares_per_trade
            if portfolio.balance >= cost:
                result = trading.buy_stock(symbol, shares_per_trade)
                actions.append({
                    "symbol":   symbol,
                    "action":   "BUY",
                    "signal":   signal,
                    "result":   result,
                    "analysis": analysis,
                })
            else:
                actions.append({
                    "symbol":   symbol,
                    "action":   "SKIP",
                    "signal":   signal,
                    "message":  f"Insufficient funds (need ${cost:,.2f}).",
                    "analysis": analysis,
                })

        # ── SELL signal ──
        elif signal in ("STRONG SELL", "SELL"):
            owned = portfolio.holdings.get(symbol, {}).get("shares", 0)
            qty   = min(owned, shares_per_trade)
            if qty > 0:
                result = trading.sell_stock(symbol, qty)
                actions.append({
                    "symbol":   symbol,
                    "action":   "SELL",
                    "signal":   signal,
                    "result":   result,
                    "analysis": analysis,
                })
            else:
                actions.append({
                    "symbol":   symbol,
                    "action":   "SKIP",
                    "signal":   signal,
                    "message":  "No shares to sell.",
                    "analysis": analysis,
                })

        # ── HOLD ──
        else:
            actions.append({
                "symbol":   symbol,
                "action":   "HOLD",
                "signal":   signal,
                "analysis": analysis,
            })

    return actions, analyses