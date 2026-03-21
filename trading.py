# trading.py
# ─────────────────────────────────────────────
# Buy and sell logic.
# All functions return structured result dicts.
# NO print() statements.
# ─────────────────────────────────────────────

import market
import portfolio
import history

def buy_stock(symbol, quantity):
    """
    Buys 'quantity' shares of 'symbol'.

    Returns dict:
        success  → bool
        message  → human-readable result string
        data     → trade details (only on success)
    """
    symbol = symbol.upper()

    # ── Validate stock exists ──
    price = market.get_price(symbol)
    if price is None:
        return {
            "success": False,
            "message": f"Stock '{symbol}' not found in market."
        }

    # ── Validate quantity ──
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        return {
            "success": False,
            "message": "Quantity must be a positive number."
        }
    quantity = int(quantity)

    # ── Check funds ──
    total_cost = round(price * quantity, 2)
    if total_cost > portfolio.balance:
        return {
            "success": False,
            "message": (
                f"Insufficient funds. "
                f"Need: ${total_cost:,.2f} | "
                f"Available: ${portfolio.balance:,.2f}"
            )
        }

    # ── Deduct balance ──
    portfolio.balance = round(portfolio.balance - total_cost, 2)

    # ── Update holdings with weighted average buy price ──
    # Formula: new_avg = (old_shares * old_avg + qty * price) / new_shares
    if symbol in portfolio.holdings:
        existing   = portfolio.holdings[symbol]
        old_shares = existing["shares"]
        old_avg    = existing["avg_buy"]
        new_shares = old_shares + quantity
        new_avg    = ((old_shares * old_avg) + (quantity * price)) / new_shares
        portfolio.holdings[symbol]["shares"]  = new_shares
        portfolio.holdings[symbol]["avg_buy"] = round(new_avg, 4)
    else:
        portfolio.holdings[symbol] = {
            "shares":  quantity,
            "avg_buy": price,
        }

    # ── Log trade ──
    history.record_trade("BUY", symbol, quantity, price, market.current_day)

    return {
        "success": True,
        "message": (
            f"Bought {quantity} share(s) of {symbol} at ${price:.2f} | "
            f"Total: ${total_cost:,.2f}"
        ),
        "data": {
            "symbol":            symbol,
            "quantity":          quantity,
            "price":             price,
            "total_cost":        total_cost,
            "remaining_balance": portfolio.balance,
        }
    }


def sell_stock(symbol, quantity):
    """
    Sells 'quantity' shares of 'symbol'.

    Returns dict:
        success  → bool
        message  → human-readable result string
        data     → trade details (only on success)
    """
    symbol = symbol.upper()

    # ── Check ownership ──
    if symbol not in portfolio.holdings:
        return {
            "success": False,
            "message": f"You don't own any shares of {symbol}."
        }

    owned = portfolio.holdings[symbol]["shares"]

    # ── Validate quantity ──
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        return {
            "success": False,
            "message": "Quantity must be a positive number."
        }
    quantity = int(quantity)

    if quantity > owned:
        return {
            "success": False,
            "message": f"You only own {owned} share(s) of {symbol}."
        }

    # ── Get current price ──
    price    = market.get_price(symbol)
    proceeds = round(price * quantity, 2)

    # ── Update balance ──
    portfolio.balance = round(portfolio.balance + proceeds, 2)

    # ── Update holdings ──
    portfolio.holdings[symbol]["shares"] -= quantity
    if portfolio.holdings[symbol]["shares"] == 0:
        del portfolio.holdings[symbol]

    # ── Log trade ──
    history.record_trade("SELL", symbol, quantity, price, market.current_day)

    return {
        "success": True,
        "message": (
            f"Sold {quantity} share(s) of {symbol} at ${price:.2f} | "
            f"Received: ${proceeds:,.2f}"
        ),
        "data": {
            "symbol":      symbol,
            "quantity":    quantity,
            "price":       price,
            "proceeds":    proceeds,
            "new_balance": portfolio.balance,
        }
    }