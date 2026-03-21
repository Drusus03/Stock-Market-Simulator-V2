# test-phase1.py
# Run this to verify Phase 1 is 100% working
# before starting Phase 2.

import market
import trading
import portfolio
import history
import bot
from state import app_state

print("=" * 55)
print("  PHASE 1 — BACKEND VERIFICATION TEST")
print("=" * 55)

# ── Test 1: Market data ──
data = market.get_market_data()
assert len(data) == 5, "Should have 5 stocks"
assert all("symbol" in d and "price" in d for d in data)
print("✅ Test 1 PASS — market.get_market_data()")

# ── Test 2: Tick generation ──
tick = market.generate_tick()
assert len(tick) == 5
assert all(v > 0 for v in tick.values())
print("✅ Test 2 PASS — market.generate_tick()")

# ── Test 3: Next day ──
result = market.next_day()
assert "day" in result
assert "news_events" in result
assert "price_updates" in result
assert market.current_day == 2
print(f"✅ Test 3 PASS — market.next_day() → Day {market.current_day}")

# ── Test 4: Buy stock ──
result = trading.buy_stock("AAPL", 5)
assert result["success"], f"Buy failed: {result['message']}"
assert "AAPL" in portfolio.holdings
print(f"✅ Test 4 PASS — trading.buy_stock() → {result['message']}")

# ── Test 5: Sell stock ──
result = trading.sell_stock("AAPL", 2)
assert result["success"], f"Sell failed: {result['message']}"
assert portfolio.holdings["AAPL"]["shares"] == 3
print(f"✅ Test 5 PASS — trading.sell_stock() → {result['message']}")

# ── Test 6: Portfolio data ──
pf = portfolio.get_portfolio_data()
assert "balance" in pf
assert "holdings" in pf
assert "total_value" in pf
assert "profit_loss" in pf
print(f"✅ Test 6 PASS — portfolio.get_portfolio_data()")

# ── Test 7: Add balance ──
result = portfolio.add_balance(500)
assert result["success"]
print(f"✅ Test 7 PASS — portfolio.add_balance() → {result['message']}")

# ── Test 8: Trade history ──
trades = history.get_history_data()
assert len(trades) == 2  # 1 buy + 1 sell
assert trades[0]["action"] == "BUY"
print(f"✅ Test 8 PASS — history.get_history_data() → {len(trades)} trades")

# ── Test 9: RSI ──
# Need at least 15 prices, so advance days first
for _ in range(20):
    market.next_day()
rsi = bot.calculate_rsi(market.get_history("AAPL"), 14)
assert rsi is not None
assert 0 <= rsi <= 100
print(f"✅ Test 9 PASS — bot.calculate_rsi() → {rsi}")

# ── Test 10: EMA ──
ema = bot.exponential_moving_average(market.get_history("TSLA"), 12)
assert ema is not None and ema > 0
print(f"✅ Test 10 PASS — bot.exponential_moving_average() → {ema:.2f}")

# ── Test 11: MACD ──
# MACD needs 26 + 9 = 35 prices minimum.
# Advance extra days to guarantee enough history.
while len(market.get_history("GOOG")) < 36:
    market.next_day()
macd = bot.calculate_macd(market.get_history("GOOG"), 12, 26, 9)
assert macd is not None
assert "macd_line" in macd and "signal_line" in macd and "histogram" in macd
print(f"✅ Test 11 PASS — bot.calculate_macd() → histogram={macd['histogram']}")
assert "macd_line" in macd and "signal_line" in macd and "histogram" in macd
print(f"✅ Test 11 PASS — bot.calculate_macd() → histogram={macd['histogram']}")

# ── Test 12: Full analysis ──
analysis = bot.analyze_stock("MSFT")
assert "signal" in analysis
assert "score"  in analysis
assert "reasons" in analysis
print(f"✅ Test 12 PASS — bot.analyze_stock() → {analysis['signal']} (score={analysis['score']})")

# ── Test 13: Bot run ──
actions, analyses = bot.run_bot(shares_per_trade=1)
assert len(actions) == 5
assert len(analyses) == 5
print(f"✅ Test 13 PASS — bot.run_bot() → {len(actions)} actions")

# ── Test 14: AppState tick ──
tick = app_state.update_tick()
assert len(tick) == 5
print(f"✅ Test 14 PASS — app_state.update_tick()")

# ── Test 15: AppState advance day ──
result = app_state.advance_day()
assert "day" in result
print(f"✅ Test 15 PASS — app_state.advance_day() → Day {result['day']}")

# ── Test 16: AppState trade ──
result = app_state.execute_trade("BUY", "TSLA", 1)
assert result["success"]
print(f"✅ Test 16 PASS — app_state.execute_trade()")

# ── Test 17: AppState save ──
result = app_state.save()
assert result["success"]
print(f"✅ Test 17 PASS — app_state.save()")

# ── Test 18: Callback system ──
fired = []
app_state.subscribe("tick", lambda d: fired.append(d))
app_state.update_tick()
assert len(fired) == 1
print(f"✅ Test 18 PASS — AppState callback system")

print("\n" + "=" * 55)
print("  ALL 18 TESTS PASSED — Phase 1 complete ✅")
print("  Ready to start Phase 2 (tkinter UI)")
print("=" * 55)