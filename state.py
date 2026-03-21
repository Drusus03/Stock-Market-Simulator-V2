# state.py
# ─────────────────────────────────────────────
# Central AppState — single source of truth.
#
# Every piece of live data flows through here.
# UI widgets subscribe to events via callbacks.
# ─────────────────────────────────────────────

import market
import portfolio
import history


class AppState:
    """
    Singleton shared state for the entire app.

    Callback events:
        "tick"       → intra-day price tick (every ~2s)
        "day_change" → official new day advanced
        "trade"      → buy or sell executed
        "news"       → news event(s) arrived
        "portfolio"  → portfolio data changed
        "bot"        → bot analysis completed
        "save"       → save completed
    """

    def __init__(self):
        # ── Live tick prices (display only — not in official history) ──
        self.tick_prices = {
            s: market.STOCKS[s]["price"] for s in market.STOCKS
        }

        # ── News feed — each event is a dict with a "day" stamp ──
        self.news_feed  = []
        self.max_news   = 200

        # ── Bot analysis results ──
        self.bot_analyses     = {}
        self.bot_last_run_day = -1

        # ── Animation state ──
        # is_animating: True while Next Day animation is running.
        # animation_ticks: counts how many ticks shown this day cycle.
        # Used by UI to block double-clicks and show PROCESSING state.
        self.is_animating    = False
        self.animation_ticks = 0

        # ── Callback registry ──
        self._callbacks = {
            "tick":       [],
            "day_change": [],
            "trade":      [],
            "news":       [],
            "portfolio":  [],
            "bot":        [],
            "save":       [],
        }

    # ─────────────────────────────────────────────
    # CALLBACK SYSTEM
    # ─────────────────────────────────────────────

    def subscribe(self, event: str, callback):
        """
        Register a UI callback for a data event.

        Example:
            app_state.subscribe("tick", update_price_table)

        The callback receives one argument: the event data dict.
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def unsubscribe(self, event: str, callback):
        """Remove a previously registered callback."""
        if event in self._callbacks:
            try:
                self._callbacks[event].remove(callback)
            except ValueError:
                pass

    def _fire(self, event: str, data=None):
        """
        Trigger all callbacks registered for an event.
        Errors in individual callbacks are caught to prevent
        one broken widget from crashing the whole app.
        """
        for cb in self._callbacks.get(event, []):
            try:
                cb(data)
            except Exception:
                pass

    # ─────────────────────────────────────────────
    # LIVE TICK
    # ─────────────────────────────────────────────

    def update_tick(self):
        """
        Generates one intra-day price tick.
        Does NOT change official prices or history.
        Fires "tick" callbacks with latest tick prices.

        Called by the UI timer every ~2 seconds.
        Returns: {symbol: tick_price, ...}
        """
        tick_prices = market.generate_tick()
        self.tick_prices.update(tick_prices)
        self._fire("tick", dict(self.tick_prices))
        return dict(self.tick_prices)

    # ─────────────────────────────────────────────
    # ADVANCE DAY
    # ─────────────────────────────────────────────

    def advance_day(self):
        """
        Advances one full official market day.

        NEWS FIX: Each event is stamped with result["day"]
        before insertion into news_feed. This allows the
        news feed to be saved and restored correctly with
        day groupings intact.
        """
        result = market.next_day()
        portfolio.snapshot_value()

        # Sync live ticks to new official close prices
        self.tick_prices = {
            s: market.STOCKS[s]["price"] for s in market.STOCKS
        }

        # Stamp each event with the current day then add to feed
        for event in result["news_events"]:
            event["day"] = result["day"]       # ← day stamp
            self.news_feed.insert(0, event)

        if len(self.news_feed) > self.max_news:
            self.news_feed = self.news_feed[:self.max_news]

        self._fire("day_change", result)
        if result["news_events"]:
            self._fire("news", result["news_events"])
        self._fire("portfolio", portfolio.get_portfolio_data())

        return result

    # ─────────────────────────────────────────────
    # MARKET DATA
    # ─────────────────────────────────────────────

    def get_market_snapshot(self):
        """
        Returns market data combining official prices
        with latest live tick prices for the UI table.

        Day change % is vs official yesterday close,
        but displayed price is the live tick price.
        """
        result = []
        for symbol, data in market.STOCKS.items():
            official_price = data["price"]
            tick_price     = self.tick_prices.get(symbol, official_price)
            price_history  = data["history"]

            if len(price_history) > 1:
                prev_close  = price_history[-2]
                day_change  = tick_price - prev_close
                day_chg_pct = (day_change / prev_close) * 100
            else:
                day_change  = 0.0
                day_chg_pct = 0.0

            result.append({
                "symbol":         symbol,
                "price":          tick_price,
                "official_price": official_price,
                "day_change":     round(day_change,  2),
                "day_change_pct": round(day_chg_pct, 2),
                "history":        list(price_history),
            })
        return result

    # ─────────────────────────────────────────────
    # PORTFOLIO
    # ─────────────────────────────────────────────

    def get_portfolio_snapshot(self):
        return portfolio.get_portfolio_data()

    # ─────────────────────────────────────────────
    # TRADE EXECUTION
    # ─────────────────────────────────────────────

    def execute_trade(self, action: str, symbol: str, quantity: int):
        """
        Executes a BUY or SELL trade.
        Fires "trade" and "portfolio" callbacks on success.

        action   → "BUY" or "SELL"
        symbol   → e.g. "AAPL"
        quantity → number of shares

        Returns result dict from trading module.
        """
        import trading
        if action == "BUY":
            result = trading.buy_stock(symbol, quantity)
        elif action == "SELL":
            result = trading.sell_stock(symbol, quantity)
        else:
            return {"success": False, "message": f"Unknown action: {action}"}

        if result["success"]:
            self._fire("trade",     result)
            self._fire("portfolio", portfolio.get_portfolio_data())

        return result

    # ─────────────────────────────────────────────
    # ADD BALANCE
    # ─────────────────────────────────────────────

    def add_balance(self, amount: float):
        result = portfolio.add_balance(amount)
        if result["success"]:
            self._fire("portfolio", portfolio.get_portfolio_data())
        return result

    # ─────────────────────────────────────────────
    # NEWS
    # ─────────────────────────────────────────────

    def get_news_feed(self):
        """Returns news feed list (newest first)."""
        return list(self.news_feed)

    # ─────────────────────────────────────────────
    # BOT
    # ─────────────────────────────────────────────

    def run_bot(self, shares_per_trade=2):
        """
        Runs the intelligent trading bot.
        Fires "bot" and "portfolio" callbacks.
        Returns (actions, analyses) tuple.
        """
        import bot
        actions, analyses = bot.run_bot(shares_per_trade)
        self.bot_analyses     = analyses
        self.bot_last_run_day = market.current_day
        self._fire("bot",       {"actions": actions, "analyses": analyses})
        self._fire("portfolio", portfolio.get_portfolio_data())
        return actions, analyses

    def get_bot_analyses(self):
        """Returns latest bot analyses dict for all stocks."""
        import bot
        self.bot_analyses = bot.get_all_analyses()
        return self.bot_analyses

    # ─────────────────────────────────────────────
    # SAVE / LOAD
    # ─────────────────────────────────────────────

    def save(self):
        result = portfolio.save_portfolio()
        self._fire("save", result)
        return result

    def load(self):
        """
        Loads portfolio + history on startup.
        Syncs tick prices to loaded official prices.
        """
        port_result = portfolio.load_portfolio()
        hist_result = portfolio.load_history()

        # Sync tick prices to loaded official prices
        self.tick_prices = {
            s: market.STOCKS[s]["price"] for s in market.STOCKS
        }
        return port_result, hist_result


# ─────────────────────────────────────────────
# GLOBAL SINGLETON
# Import everywhere as: from state import app_state
# ─────────────────────────────────────────────
app_state = AppState()