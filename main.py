# main.py
# ═══════════════════════════════════════════════════════════════════
# Stock Market Simulator V2 MAX
# Professional Trading Terminal  ─  Phase 4 (Final)
#
# Phase 4 additions:
#   Step 10 → Keyboard shortcuts (N/B/S/1-6/Ctrl+S)
#   Step 11 → Candlestick chart with OHLC bars
#   Step 12 → Hover tooltips, P&L flash, N-day bot interval
# ═══════════════════════════════════════════════════════════════════

import random
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from collections import deque
from datetime import datetime

import market
import portfolio
import history
import bot
from state import app_state

# ═══════════════════════════════════════════════════════════════════
# THEME — Professional Dark Trading Terminal
# Deep navy base, surgical accent colors, zero visual noise
# ═══════════════════════════════════════════════════════════════════

BG      = "#0b0f1a"
SURF    = "#111827"
SURF2   = "#1a2235"
SURF3   = "#1e2d40"
BORDER  = "#1f2d3d"
ACCENT  = "#3b82f6"
GREEN   = "#10b981"
RED     = "#ef4444"
YELLOW  = "#f59e0b"
PURPLE  = "#8b5cf6"
CYAN    = "#06b6d4"
ORANGE  = "#f97316"
TEXT    = "#e2e8f0"
MUTED   = "#94a3b8"
DIM     = "#475569"

STOCK_COLORS = {
    "AAPL": "#3b82f6",
    "TSLA": "#ef4444",
    "GOOG": "#10b981",
    "AMZN": "#f59e0b",
    "MSFT": "#8b5cf6",
}

F_SM   = ("Consolas", 9)
F_MONO = ("Consolas", 10)
F_BOLD = ("Consolas", 11, "bold")
F_LG   = ("Consolas", 12)
F_TITL = ("Consolas", 13, "bold")
F_HUGE = ("Consolas", 20, "bold")
F_MID  = ("Consolas", 11)

TICK_HIST = {
    s: deque([market.get_price(s)] * 60, maxlen=80)
    for s in market.STOCKS
}

# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def pl_color(v):   return GREEN if v >= 0 else RED
def fmt_p(v):      return f"${v:,.2f}"
def fmt_pct(v):    return f"+{v:.2f}%" if v >= 0 else f"{v:.2f}%"
def fmt_pl(v):     return f"+${v:,.2f}" if v >= 0 else f"-${abs(v):,.2f}"
def now_str():     return datetime.now().strftime("%H:%M:%S")

def mpl_ax_style(ax, facecolor=SURF):
    """Apply dark theme to a matplotlib Axes object."""
    ax.set_facecolor(facecolor)
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(BORDER)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(TEXT)

# ═══════════════════════════════════════════════════════════════════
# TTK STYLE
# ═══════════════════════════════════════════════════════════════════

def setup_style():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("T.Treeview",
                 background=SURF, foreground=TEXT,
                 fieldbackground=SURF, borderwidth=0,
                 rowheight=30, font=F_MONO)
    s.configure("T.Treeview.Heading",
                 background=SURF2, foreground=MUTED,
                 font=F_BOLD, borderwidth=0, relief="flat")
    s.map("T.Treeview",
          background=[("selected", SURF3)],
          foreground=[("selected", ACCENT)])
    s.map("T.Treeview.Heading",
          background=[("active", BORDER)])
    s.configure("Dark.Vertical.TScrollbar",
                 background=SURF2, troughcolor=SURF,
                 borderwidth=0, arrowsize=12, arrowcolor=MUTED)
    s.map("Dark.Vertical.TScrollbar",
          background=[("active", SURF3)])

# ═══════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════

class SidebarButton(tk.Frame):
    def __init__(self, parent, icon, label, command, **kwargs):
        super().__init__(parent, bg=BG, cursor="hand2", **kwargs)
        self._active = False
        self._cmd    = command

        self._bar = tk.Frame(self, bg=BG, width=3)
        self._bar.pack(side="left", fill="y")

        self._inner = tk.Frame(self, bg=BG)
        self._inner.pack(side="left", fill="both", expand=True,
                         padx=(8, 12), pady=10)

        self._ic_lbl = tk.Label(self._inner, text=icon, bg=BG,
                                 fg=MUTED, font=("Consolas", 14))
        self._ic_lbl.pack(side="left", padx=(0, 8))

        self._tx_lbl = tk.Label(self._inner, text=label, bg=BG,
                                 fg=MUTED, font=F_BOLD, anchor="w")
        self._tx_lbl.pack(side="left", fill="x")

        for w in [self, self._inner, self._ic_lbl, self._tx_lbl, self._bar]:
            w.bind("<Button-1>", lambda e: self._cmd())
            w.bind("<Enter>",    lambda e: self._on_hover(True))
            w.bind("<Leave>",    lambda e: self._on_hover(False))

    def set_active(self, active: bool):
        self._active = active
        self._bar.config(bg=ACCENT if active else BG)
        self._tx_lbl.config(fg=TEXT if active else MUTED,
                             font=(F_BOLD[0], F_BOLD[1], "bold"))
        self._bg_refresh(SURF2 if active else BG)

    def _on_hover(self, entering):
        if not self._active:
            col = SURF if entering else BG
            self._bg_refresh(col)
            self._tx_lbl.config(fg=TEXT if entering else MUTED)

    def _bg_refresh(self, col):
        self.config(bg=col)
        self._inner.config(bg=col)
        self._ic_lbl.config(bg=col)
        self._tx_lbl.config(bg=col)


class StatCard(tk.Frame):
    def __init__(self, parent, label, value="—", color=TEXT, **kw):
        super().__init__(parent, bg=SURF2,
                         highlightthickness=1,
                         highlightbackground=BORDER, **kw)
        tk.Label(self, text=label, bg=SURF2, fg=MUTED,
                 font=F_SM).pack(anchor="w", padx=12, pady=(10, 0))
        self._val = tk.Label(self, text=value, bg=SURF2,
                              fg=color, font=F_TITL)
        self._val.pack(anchor="w", padx=12, pady=(2, 10))
        self._prev_val = value

    def update(self, value, color=None):
        self._val.config(text=value)
        if color:
            self._val.config(fg=color)

    def flash(self, up: bool):
        """
        Brief border + label flash when value changes direction.
        up=True → green flash (profit increased)
        up=False → red flash (profit decreased)
        Called by PortfolioPanel on P&L updates.
        """
        flash_col = GREEN if up else RED
        orig_fg   = self._val.cget("fg")
        self._val.config(fg=flash_col)
        self.config(highlightbackground=flash_col, highlightthickness=2)
        def _restore():
            try:
                self._val.config(fg=orig_fg)
                self.config(highlightbackground=BORDER,
                             highlightthickness=1)
            except Exception:
                pass
        self.after(400, _restore)


# ═══════════════════════════════════════════════════════════════════
# TOOLTIP  — floating hover info box
# ═══════════════════════════════════════════════════════════════════

class Tooltip:
    """
    Floating dark tooltip that appears near the cursor.
    Used by MarketPanel to show full bot analysis on row hover.

    Usage:
        tip = Tooltip(widget)
        tip.show("text", x, y)   # show at screen coords
        tip.hide()               # destroy window
    """
    def __init__(self, widget):
        self._widget = widget
        self._win    = None
        self._job    = None

    def schedule(self, text: str, x: int, y: int, delay: int = 500):
        """Show tooltip after 'delay' ms — cancels any pending show."""
        self.cancel()
        self._job = self._widget.after(
            delay, lambda: self.show(text, x, y))

    def cancel(self):
        if self._job:
            self._widget.after_cancel(self._job)
            self._job = None

    def show(self, text: str, x: int, y: int):
        """Immediately show tooltip at screen position (x, y)."""
        self.hide()
        self._win = tk.Toplevel(self._widget)
        self._win.wm_overrideredirect(True)
        self._win.wm_geometry(f"+{x + 18}+{y + 12}")
        self._win.configure(bg=SURF2)

        frame = tk.Frame(self._win, bg=SURF2,
                         highlightthickness=1,
                         highlightbackground=ACCENT)
        frame.pack()
        tk.Label(frame, text=text, bg=SURF2, fg=TEXT,
                 font=F_SM, justify="left",
                 padx=12, pady=8).pack()

    def hide(self, _=None):
        self.cancel()
        if self._win:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None

# ═══════════════════════════════════════════════════════════════════
# DIALOGS
# ═══════════════════════════════════════════════════════════════════

class TradeDialog(tk.Toplevel):
    """
    Modal BUY / SELL order dialog.
    Shows live price preview and estimated cost/proceeds.
    """
    def __init__(self, parent, action: str, symbol: str = ""):
        super().__init__(parent)
        self.action = action
        self.result = None
        color       = GREEN if action == "BUY" else RED

        self.title(f"{'Buy' if action == 'BUY' else 'Sell'} Order")
        self.configure(bg=SURF)
        self.resizable(False, False)
        self.grab_set()
        self.geometry("380x300")
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - 380) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 300) // 2
        self.geometry(f"+{px}+{py}")

        tk.Frame(self, bg=color, height=4).pack(fill="x")
        icon = "🟢" if action == "BUY" else "🔴"
        tk.Label(self, text=f"{icon}  {action} ORDER",
                 bg=SURF, fg=color, font=F_TITL).pack(pady=(16, 2))
        tk.Label(self, text=f"Available Cash: {fmt_p(portfolio.balance)}",
                 bg=SURF, fg=MUTED, font=F_SM).pack()

        form = tk.Frame(self, bg=SURF)
        form.pack(fill="x", padx=28, pady=14)

        def row(label, var):
            r = tk.Frame(form, bg=SURF)
            r.pack(fill="x", pady=5)
            tk.Label(r, text=label, bg=SURF, fg=MUTED,
                     font=F_MONO, width=11, anchor="w").pack(side="left")
            e = tk.Entry(r, textvariable=var, bg=SURF2, fg=TEXT,
                         font=F_LG, insertbackground=TEXT, bd=0,
                         highlightthickness=1, highlightcolor=color,
                         highlightbackground=BORDER, width=14)
            e.pack(side="left", ipady=7)
            e.bind("<KeyRelease>", self._preview)
            return e

        self.sym_var = tk.StringVar(value=symbol.upper())
        self.qty_var = tk.StringVar(value="1")
        row("  Symbol  :", self.sym_var)
        row("  Quantity:", self.qty_var)

        self.prev_var = tk.StringVar(value="Estimated Cost: —")
        tk.Label(self, textvariable=self.prev_var,
                 bg=SURF, fg=YELLOW, font=F_SM).pack(pady=4)

        bf = tk.Frame(self, bg=SURF)
        bf.pack(pady=14)
        tk.Button(bf, text="  CANCEL  ", bg=BG, fg=MUTED, font=F_BOLD,
                  bd=0, padx=12, pady=9, cursor="hand2",
                  relief="flat", command=self.destroy).pack(side="left", padx=8)
        lbl = "  CONFIRM BUY  " if action == "BUY" else "  CONFIRM SELL  "
        tk.Button(bf, text=lbl, bg=color, fg=TEXT, font=F_BOLD,
                  bd=0, padx=12, pady=9, cursor="hand2",
                  relief="flat", command=self._confirm).pack(side="left", padx=8)

        self._preview()
        self.wait_window()

    def _preview(self, _=None):
        try:
            sym   = self.sym_var.get().strip().upper()
            qty   = int(self.qty_var.get())
            price = market.get_price(sym)
            if price and qty > 0:
                total = price * qty
                word  = "Cost" if self.action == "BUY" else "Proceeds"
                self.prev_var.set(
                    f"Est. {word}: {fmt_p(total)}  ({qty} x {fmt_p(price)})"
                )
        except (ValueError, TypeError):
            self.prev_var.set("Estimated Cost: —")

    def _confirm(self):
        try:
            sym = self.sym_var.get().strip().upper()
            qty = int(self.qty_var.get())
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be > 0", parent=self)
                return
            self.result = (sym, qty)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Enter a valid quantity.", parent=self)


class AddBalanceDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.title("Add Funds")
        self.configure(bg=SURF)
        self.resizable(False, False)
        self.grab_set()
        self.geometry("340x230")
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - 340) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 230) // 2
        self.geometry(f"+{px}+{py}")

        tk.Frame(self, bg=CYAN, height=4).pack(fill="x")
        tk.Label(self, text="💰  ADD FUNDS", bg=SURF,
                 fg=CYAN, font=F_TITL).pack(pady=(16, 2))
        tk.Label(self, text=f"Current Balance: {fmt_p(portfolio.balance)}",
                 bg=SURF, fg=MUTED, font=F_SM).pack()

        frame = tk.Frame(self, bg=SURF)
        frame.pack(fill="x", padx=30, pady=14)
        tk.Label(frame, text="Amount ($):", bg=SURF,
                 fg=MUTED, font=F_MONO).pack(anchor="w", pady=(0, 4))
        self.amt_var = tk.StringVar(value="5000")
        tk.Entry(frame, textvariable=self.amt_var,
                 bg=SURF2, fg=TEXT, font=F_LG,
                 insertbackground=TEXT, bd=0,
                 highlightthickness=1, highlightcolor=CYAN,
                 highlightbackground=BORDER).pack(fill="x", ipady=9)

        bf = tk.Frame(self, bg=SURF)
        bf.pack(pady=12)
        tk.Button(bf, text=" CANCEL ", bg=BG, fg=MUTED, font=F_BOLD,
                  bd=0, padx=10, pady=8, cursor="hand2",
                  relief="flat", command=self.destroy).pack(side="left", padx=8)
        tk.Button(bf, text=" ADD FUNDS ", bg=CYAN, fg=BG, font=F_BOLD,
                  bd=0, padx=10, pady=8, cursor="hand2",
                  relief="flat", command=self._confirm).pack(side="left", padx=8)
        self.wait_window()

    def _confirm(self):
        try:
            amt = float(self.amt_var.get().replace(",", "").replace("$", ""))
            if amt <= 0:
                messagebox.showerror("Error", "Amount must be > 0", parent=self)
                return
            self.result = amt
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number.", parent=self)

# ═══════════════════════════════════════════════════════════════════
# PANEL: MARKET
# ═══════════════════════════════════════════════════════════════════

class MarketPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app             = app
        self.selected_symbol = "AAPL"
        self._tooltip        = None
        self._build()
        self._refresh_table()
        self._refresh_chart()

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 8))
        tk.Label(hdr, text="LIVE MARKET", bg=BG,
                 fg=TEXT, font=F_TITL).pack(side="left")
        self._day_lbl = tk.Label(hdr, text=f"Day {market.current_day}",
                                  bg=BG, fg=MUTED, font=F_MONO)
        self._day_lbl.pack(side="right")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # LEFT — table
        left = tk.Frame(body, bg=SURF,
                        highlightthickness=1, highlightbackground=BORDER)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cols = ("symbol", "price", "change", "chg_pct", "signal")
        self._tree = ttk.Treeview(left, columns=cols,
                                   show="headings", style="T.Treeview",
                                   selectmode="browse")
        heads = {
            "symbol":  ("SYMBOL",  70,  "center"),
            "price":   ("PRICE",   170, "e"),
            "change":  ("CHANGE",  90,  "e"),
            "chg_pct": ("CHG %",   80,  "e"),
            "signal":  ("SIGNAL",  90,  "center"),
        }
        for col, (label, width, anchor) in heads.items():
            self._tree.heading(col, text=label)
            self._tree.column(col, width=width, anchor=anchor, stretch=True)

        self._tree.tag_configure("up",   foreground=GREEN)
        self._tree.tag_configure("down", foreground=RED)
        self._tree.tag_configure("flat", foreground=MUTED)

        vsb = ttk.Scrollbar(left, orient="vertical",
                             style="Dark.Vertical.TScrollbar",
                             command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── Hover tooltip bindings ──
        self._tooltip = Tooltip(self._tree)
        self._tree.bind("<Motion>",    self._on_hover)
        self._tree.bind("<Leave>",     self._on_leave)
        self._tree.bind("<FocusOut>",  self._on_leave)

        # RIGHT — sparkline
        right = tk.Frame(body, bg=SURF,
                         highlightthickness=1, highlightbackground=BORDER,
                         width=380)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        chart_hdr = tk.Frame(right, bg=SURF)
        chart_hdr.pack(fill="x", padx=14, pady=(12, 4))
        self._chart_title = tk.Label(chart_hdr, text="AAPL — Live",
                                      bg=SURF, fg=TEXT, font=F_BOLD)
        self._chart_title.pack(side="left")
        self._chart_price = tk.Label(chart_hdr, text="—",
                                      bg=SURF, fg=ACCENT, font=F_TITL)
        self._chart_price.pack(side="right")

        self._fig = Figure(figsize=(4.5, 3.8), dpi=88, facecolor=SURF)
        self._ax  = self._fig.add_subplot(111, facecolor=SURF)
        mpl_ax_style(self._ax, SURF)
        self._fig.subplots_adjust(left=0.12, right=0.97,
                                   top=0.92, bottom=0.15)
        self._line, = self._ax.plot([], [], color=ACCENT,
                                     linewidth=1.8, alpha=0.95)
        self._fill  = None
        self._canvas = FigureCanvasTkAgg(self._fig, master=right)
        self._canvas.get_tk_widget().pack(fill="both", expand=True,
                                           padx=6, pady=6)

    def _on_select(self, _=None):
        sel = self._tree.selection()
        if sel:
            vals = self._tree.item(sel[0], "values")
            if vals:
                self.selected_symbol = vals[0]
                self._chart_title.config(text=f"{vals[0]} — Live")
                self._refresh_chart()

    def _on_hover(self, event):
        """Build and show tooltip with full bot analysis for hovered row."""
        item = self._tree.identify_row(event.y)
        if not item:
            self._tooltip.hide()
            return
        sym = item  # iid == symbol
        analyses = app_state.get_bot_analyses()
        a = analyses.get(sym, {})
        if not a:
            return

        if not a.get("data_ready", False):
            reasons = a.get("reasons", [])
            text = f"{sym}\n{reasons[0] if reasons else 'Insufficient data'}"
        else:
            ma5   = a.get("ma5")
            ma20  = a.get("ma20")
            rsi   = a.get("rsi")
            macd  = a.get("macd")
            score = a.get("score", 0)
            sig   = a.get("signal", "—")
            lines = [
                f"  {sym}  —  {sig}  (score: {'+' if score>0 else ''}{score})",
                f"  ─────────────────────────────",
            ]
            if ma5  is not None: lines.append(f"  MA5   : {ma5:.2f}")
            if ma20 is not None: lines.append(f"  MA20  : {ma20:.2f}")
            if rsi  is not None: lines.append(f"  RSI   : {rsi:.1f}{'  ← Oversold' if rsi<30 else '  ← Overbought' if rsi>70 else ''}")
            if macd is not None:
                h = macd.get("histogram", 0)
                lines.append(f"  MACD H: {h:+.4f}  ({'Bull' if h>0 else 'Bear'})")
            text = "\n".join(lines)

        x = event.x_root
        y = event.y_root
        self._tooltip.schedule(text, x, y, delay=300)

    def _on_leave(self, _=None):
        self._tooltip.hide()

    def update_tick(self, tick_prices: dict):
        # TICK_HIST is written by TradingApp only — no append here.
        # This method only refreshes the display.
        self._refresh_table()
        self._refresh_chart()
        self._day_lbl.config(text=f"Day {market.current_day}")

    def _refresh_table(self):
        selected     = self.selected_symbol
        bot_analyses = app_state.get_bot_analyses()
        self._tree.delete(*self._tree.get_children())

        for row in app_state.get_market_snapshot():
            sym     = row["symbol"]
            price   = row["price"]
            change  = row["day_change"]
            chg_pct = row["day_change_pct"]
            signal  = bot_analyses.get(sym, {}).get("signal", "—")
            tag     = "up" if change >= 0 else "down"

            # Price column: "$150.00 (+2.3%)" — inline % change
            pct_str   = f"+{chg_pct:.2f}%" if chg_pct >= 0 else f"{chg_pct:.2f}%"
            price_col = f"${price:.2f}  ({pct_str})"

            self._tree.insert("", "end", iid=sym, values=(
                sym,
                price_col,
                f"+{change:.2f}" if change >= 0 else f"{change:.2f}",
                fmt_pct(chg_pct),
                signal,
            ), tags=(tag,))

        if selected and self._tree.exists(selected):
            self._tree.selection_set(selected)

    def _refresh_chart(self):
        sym    = self.selected_symbol
        prices = list(TICK_HIST[sym])
        xs     = list(range(len(prices)))
        color  = STOCK_COLORS.get(sym, ACCENT)

        self._line.set_data(xs, prices)
        self._line.set_color(color)

        if self._fill:
            self._fill.remove()
        baseline   = min(prices) * 0.999
        self._fill = self._ax.fill_between(xs, prices, baseline,
                                            alpha=0.15, color=color)
        self._ax.set_xlim(0, len(prices) - 1)
        if len(prices) > 1:
            ypad = (max(prices) - min(prices)) * 0.1 or 0.5
            self._ax.set_ylim(min(prices) - ypad, max(prices) + ypad)

        self._ax.set_xlabel("Ticks", color=MUTED, fontsize=8)
        self._ax.set_ylabel("Price ($)", color=MUTED, fontsize=8)
        self._ax.grid(True, color=BORDER, alpha=0.5, linewidth=0.6)

        if prices:
            self._chart_price.config(text=f"${prices[-1]:.2f}", fg=color)

        self._canvas.draw_idle()

    def on_day_changed(self):
        self._day_lbl.config(text=f"Day {market.current_day}")
        self._refresh_table()
        self._refresh_chart()

# ═══════════════════════════════════════════════════════════════════
# PANEL: PORTFOLIO
# ═══════════════════════════════════════════════════════════════════

class PortfolioPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app      = app
        self._prev_pl = None   # tracks last P&L for flash direction
        self._build()
        self.refresh()

    def _build(self):
        tk.Label(self, text="PORTFOLIO", bg=BG,
                 fg=TEXT, font=F_TITL).pack(anchor="w", padx=20, pady=(18, 10))

        # Stat cards
        cards_frame = tk.Frame(self, bg=BG)
        cards_frame.pack(fill="x", padx=20, pady=(0, 14))
        self._c_balance = StatCard(cards_frame, "CASH BALANCE", color=CYAN)
        self._c_total   = StatCard(cards_frame, "TOTAL VALUE",  color=TEXT)
        self._c_pl      = StatCard(cards_frame, "TOTAL P&L",    color=MUTED)
        self._c_plpct   = StatCard(cards_frame, "RETURN %",     color=MUTED)
        for card in [self._c_balance, self._c_total,
                     self._c_pl, self._c_plpct]:
            card.pack(side="left", expand=True, fill="x",
                      padx=(0, 10), ipady=4)

        # Holdings table
        tbl_frame = tk.Frame(self, bg=SURF,
                              highlightthickness=1, highlightbackground=BORDER)
        tbl_frame.pack(fill="x", padx=20, pady=(0, 14))
        tk.Label(tbl_frame, text=" HOLDINGS", bg=SURF,
                 fg=MUTED, font=F_SM).pack(anchor="w", padx=8, pady=(8, 2))

        cols = ("symbol", "shares", "avg_buy", "price", "value", "pl", "pl_pct")
        self._tree = ttk.Treeview(tbl_frame, columns=cols,
                                   show="headings", style="T.Treeview",
                                   height=5)
        heads = {
            "symbol":  ("SYMBOL",  70,  "center"),
            "shares":  ("SHARES",  70,  "e"),
            "avg_buy": ("AVG BUY", 95,  "e"),
            "price":   ("CURRENT", 95,  "e"),
            "value":   ("VALUE",   100, "e"),
            "pl":      ("P&L",     100, "e"),
            "pl_pct":  ("P&L %",   80,  "e"),
        }
        for col, (label, width, anchor) in heads.items():
            self._tree.heading(col, text=label)
            self._tree.column(col, width=width, anchor=anchor, stretch=True)
        self._tree.tag_configure("profit", foreground=GREEN)
        self._tree.tag_configure("loss",   foreground=RED)
        self._tree.pack(fill="x", padx=4, pady=(0, 8))

        # Value chart
        chart_frame = tk.Frame(self, bg=SURF,
                                highlightthickness=1, highlightbackground=BORDER)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        tk.Label(chart_frame, text=" PORTFOLIO VALUE OVER TIME",
                 bg=SURF, fg=MUTED, font=F_SM).pack(
                     anchor="w", padx=10, pady=(8, 2))

        self._pfig = Figure(figsize=(8, 2.4), dpi=90, facecolor=SURF)
        self._pax  = self._pfig.add_subplot(111, facecolor=SURF)
        mpl_ax_style(self._pax, SURF)
        self._pfig.subplots_adjust(left=0.08, right=0.98,
                                    top=0.88, bottom=0.2)
        self._pline, = self._pax.plot([], [], color=ACCENT,
                                       linewidth=2, alpha=0.95)
        self._pfill   = None
        self._pcanvas = FigureCanvasTkAgg(self._pfig, master=chart_frame)
        self._pcanvas.get_tk_widget().pack(fill="both", expand=True,
                                            padx=6, pady=6)

        # ── Feature 3: Best / Worst Trade ──
        trade_row = tk.Frame(self, bg=BG)
        trade_row.pack(fill="x", padx=20, pady=(6, 0))
        self._c_best  = StatCard(trade_row, "BEST TRADE",  color=GREEN)
        self._c_worst = StatCard(trade_row, "WORST TRADE", color=RED)
        self._c_best.pack(side="left",  expand=True, fill="x", padx=(0, 10))
        self._c_worst.pack(side="left", expand=True, fill="x", padx=(0, 10))

        # ── Feature 4: Performance Insights ──
        insights_frame = tk.Frame(self, bg=SURF,
                                   highlightthickness=1,
                                   highlightbackground=BORDER)
        insights_frame.pack(fill="x", padx=20, pady=(8, 16))
        tk.Label(insights_frame, text=" PERFORMANCE INSIGHTS",
                 bg=SURF, fg=MUTED, font=F_SM).pack(
                     anchor="w", padx=10, pady=(8, 4))
        self._lbl_insights = tk.Label(
            insights_frame, text="—", bg=SURF,
            fg=TEXT, font=F_MONO, justify="left", anchor="w")
        self._lbl_insights.pack(fill="x", padx=16, pady=(0, 10))

    def refresh(self):
        """Full refresh using official prices — called on day change."""
        data = app_state.get_portfolio_snapshot()

        self._c_balance.update(fmt_p(data["balance"]), CYAN)
        self._c_total.update(fmt_p(data["total_value"]), TEXT)
        pl    = data["profit_loss"]
        plpct = data["profit_loss_pct"]
        self._c_pl.update(fmt_pl(pl),        pl_color(pl))
        self._c_plpct.update(fmt_pct(plpct),  pl_color(pl))

        # ── Flash P&L card when value changes direction ──
        if self._prev_pl is not None and pl != self._prev_pl:
            up = pl > self._prev_pl
            self._c_pl.flash(up)
            self._c_plpct.flash(up)
        self._prev_pl = pl

        self._tree.delete(*self._tree.get_children())
        for h in data["holdings"]:
            tag = "profit" if h["pl"] >= 0 else "loss"
            self._tree.insert("", "end", values=(
                h["symbol"], h["shares"],
                fmt_p(h["avg_buy"]),
                fmt_p(h["current_price"]),
                fmt_p(h["position_value"]),
                fmt_pl(h["pl"]),
                fmt_pct(h["pl_pct"]),
            ), tags=(tag,))

        vals = data["value_history"]
        if len(vals) < 2:
            return
        xs    = list(range(1, len(vals) + 1))
        start = vals[0]
        color = GREEN if vals[-1] >= start else RED

        self._pline.set_data(xs, vals)
        self._pline.set_color(color)
        if self._pfill:
            self._pfill.remove()
        self._pfill = self._pax.fill_between(
            xs, vals, start, alpha=0.12, color=color)
        self._pax.axhline(y=start, color=DIM, linestyle="--",
                           linewidth=0.8, alpha=0.7)
        self._pax.set_xlim(1, max(len(vals), 2))
        ypad = (max(vals) - min(vals)) * 0.1 or 100
        self._pax.set_ylim(min(vals) - ypad, max(vals) + ypad)
        self._pax.set_xlabel("Day", color=MUTED, fontsize=8)
        self._pax.set_ylabel("Value ($)", color=MUTED, fontsize=8)
        self._pax.grid(True, color=BORDER, alpha=0.4, linewidth=0.6)
        self._pcanvas.draw_idle()

        # ── Feature 3: Best / Worst Trade ──
        trades = history.get_history_data()
        if trades:
            # Walk trades chronologically to track avg buy price per symbol.
            # This correctly handles fully-sold positions where the symbol
            # no longer exists in portfolio.holdings (which caused $0 P&L).
            running_shares  = {}   # sym → shares held
            running_cost    = {}   # sym → total cost basis
            trade_pnl       = []   # list of (pnl, trade_dict)

            for t in trades:
                sym = t["symbol"]
                qty = t["quantity"]
                p   = t["price"]

                if t["action"] == "BUY":
                    # Accumulate cost basis
                    running_shares[sym] = running_shares.get(sym, 0) + qty
                    running_cost[sym]   = running_cost.get(sym, 0) + qty * p

                elif t["action"] == "SELL":
                    # Avg buy price from cost basis tracked so far
                    held = running_shares.get(sym, 0)
                    cost = running_cost.get(sym, 0)
                    avg_buy = (cost / held) if held > 0 else p
                    pnl     = round((p - avg_buy) * qty, 2)
                    trade_pnl.append((pnl, t))

                    # Reduce cost basis proportionally
                    if held > 0:
                        running_shares[sym] = max(0, held - qty)
                        running_cost[sym]   = max(0.0, cost - avg_buy * qty)

            if trade_pnl:
                best_pnl,  best_t  = max(trade_pnl, key=lambda x: x[0])
                worst_pnl, worst_t = min(trade_pnl, key=lambda x: x[0])
                self._c_best.update(
                    f"{best_t['symbol']}  {fmt_pl(best_pnl)}", GREEN)
                self._c_worst.update(
                    f"{worst_t['symbol']}  {fmt_pl(worst_pnl)}", RED)
            else:
                self._c_best.update("No sells yet", MUTED)
                self._c_worst.update("No sells yet", MUTED)
        else:
            self._c_best.update("No trades yet", MUTED)
            self._c_worst.update("No trades yet", MUTED)

        # ── Feature 4: Performance Insights ──
        growth_pct = data["profit_loss_pct"]
        max_loss   = min(0.0,
                         min((v - start for v in vals), default=0.0))
        max_loss_pct = round((max_loss / start) * 100, 2) if start else 0.0

        # Best and worst stock by P&L
        holdings_list = data["holdings"]
        if holdings_list:
            best_s  = max(holdings_list, key=lambda h: h["pl"])
            worst_s = min(holdings_list, key=lambda h: h["pl"])
            best_str  = (f"🏆 Best Stock  : "
                         f"{best_s['symbol']}  {fmt_pl(best_s['pl'])}"
                         f"  ({fmt_pct(best_s['pl_pct'])})")
            worst_str = (f"📉 Worst Stock : "
                         f"{worst_s['symbol']}  {fmt_pl(worst_s['pl'])}"
                         f"  ({fmt_pct(worst_s['pl_pct'])})")
        else:
            best_str  = "🏆 Best Stock  : —  (no holdings)"
            worst_str = "📉 Worst Stock : —  (no holdings)"

        insight_text = (
            f"📈 Portfolio Growth : {fmt_pct(growth_pct)}\n"
            f"📉 Max Drawdown     : {max_loss_pct:.2f}%\n"
            f"{best_str}\n"
            f"{worst_str}"
        )
        self._lbl_insights.config(text=insight_text)

    def live_update(self, tick_prices: dict):
        """
        Live refresh every 2 seconds using tick prices.
        Updates stat cards + holdings table only (not value chart).
        FIXED: Now correctly indented INSIDE PortfolioPanel class.
        """
        stock_value = 0.0
        for symbol, data in portfolio.holdings.items():
            price = tick_prices.get(symbol, market.get_price(symbol))
            stock_value += data["shares"] * price

        live_total = round(portfolio.balance + stock_value, 2)
        live_pl    = live_total - portfolio.STARTING_BALANCE
        live_plpct = round((live_pl / portfolio.STARTING_BALANCE) * 100, 2)

        self._c_balance.update(fmt_p(portfolio.balance), CYAN)
        self._c_total.update(fmt_p(live_total), TEXT)
        self._c_pl.update(fmt_pl(live_pl),        pl_color(live_pl))
        self._c_plpct.update(fmt_pct(live_plpct),  pl_color(live_pl))

        # Flash on direction change
        if self._prev_pl is not None and live_pl != self._prev_pl:
            up = live_pl > self._prev_pl
            self._c_pl.flash(up)
            self._c_plpct.flash(up)
        self._prev_pl = live_pl

        self._tree.delete(*self._tree.get_children())
        for symbol, data in portfolio.holdings.items():
            shares  = data["shares"]
            avg_buy = data["avg_buy"]
            now     = tick_prices.get(symbol, market.get_price(symbol))
            pl      = round((now - avg_buy) * shares, 2)
            pl_pct  = round(((now - avg_buy) / avg_buy) * 100, 2) \
                      if avg_buy > 0 else 0.0
            tag = "profit" if pl >= 0 else "loss"
            self._tree.insert("", "end", values=(
                symbol, shares,
                fmt_p(avg_buy), fmt_p(now),
                fmt_p(now * shares),
                fmt_pl(pl), fmt_pct(pl_pct),
            ), tags=(tag,))

# ═══════════════════════════════════════════════════════════════════
# PANEL: HISTORY
# ═══════════════════════════════════════════════════════════════════

class HistoryPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app     = app
        self._filter = "ALL"
        self._build()
        self.refresh()

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(hdr, text="TRADE HISTORY", bg=BG,
                 fg=TEXT, font=F_TITL).pack(side="left")

        btn_frame = tk.Frame(hdr, bg=BG)
        btn_frame.pack(side="right")
        self._filter_btns = {}
        for label, key in [("ALL", "ALL"), ("BUY", "BUY"), ("SELL", "SELL")]:
            btn = tk.Button(btn_frame, text=f" {label} ", font=F_SM,
                            bd=0, padx=8, pady=4, cursor="hand2",
                            relief="flat",
                            command=lambda k=key: self._set_filter(k))
            btn.pack(side="left", padx=3)
            self._filter_btns[key] = btn
        self._update_filter_style()

        tbl = tk.Frame(self, bg=SURF,
                        highlightthickness=1, highlightbackground=BORDER)
        tbl.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        cols = ("time", "day", "action", "symbol",
                "quantity", "price", "total")
        self._tree = ttk.Treeview(tbl, columns=cols,
                                   show="headings", style="T.Treeview")
        heads = {
            "time":     ("TIME",    80,  "center"),
            "day":      ("DAY",     50,  "center"),
            "action":   ("ACTION",  70,  "center"),
            "symbol":   ("SYMBOL",  75,  "center"),
            "quantity": ("QTY",     60,  "e"),
            "price":    ("PRICE",   100, "e"),
            "total":    ("TOTAL",   110, "e"),
        }
        for col, (label, width, anchor) in heads.items():
            self._tree.heading(col, text=label)
            self._tree.column(col, width=width, anchor=anchor, stretch=True)

        self._tree.tag_configure("buy",  foreground=GREEN)
        self._tree.tag_configure("sell", foreground=RED)

        vsb = ttk.Scrollbar(tbl, orient="vertical",
                             style="Dark.Vertical.TScrollbar",
                             command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._summary = tk.Label(self, text="", bg=BG,
                                  fg=MUTED, font=F_SM)
        self._summary.pack(anchor="e", padx=24, pady=(0, 8))

    def _set_filter(self, key):
        self._filter = key
        self._update_filter_style()
        self.refresh()

    def _update_filter_style(self):
        for key, btn in self._filter_btns.items():
            if key == self._filter:
                btn.config(bg=ACCENT, fg=TEXT)
            else:
                btn.config(bg=SURF2, fg=MUTED)

    def refresh(self):
        self._tree.delete(*self._tree.get_children())
        trades = history.get_history_data()
        if self._filter != "ALL":
            trades = [t for t in trades if t["action"] == self._filter]

        buys = sells = 0
        for t in reversed(trades):
            tag = "buy" if t["action"] == "BUY" else "sell"
            self._tree.insert("", "end", values=(
                t["time"], f"D{t['day']}", t["action"],
                t["symbol"], t["quantity"],
                fmt_p(t["price"]), fmt_p(t["total"]),
            ), tags=(tag,))
            if t["action"] == "BUY": buys  += 1
            else:                    sells += 1

        self._summary.config(
            text=f"Total: {len(trades)} trades  |  "
                 f"Buys: {buys}  |  Sells: {sells}"
        )

# ═══════════════════════════════════════════════════════════════════
# PANEL: CHARTS
# ═══════════════════════════════════════════════════════════════════

class ChartPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app                = app
        self.selected           = "AAPL"
        self._current_view      = "single"   # "single" | "all" | "candle"
        self._build()
        self._draw_single()

    def _build(self):
        ctrl = tk.Frame(self, bg=BG)
        ctrl.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(ctrl, text="CHARTS", bg=BG,
                 fg=TEXT, font=F_TITL).pack(side="left")

        right_ctrl = tk.Frame(ctrl, bg=BG)
        right_ctrl.pack(side="right")
        self._btn_single = tk.Button(right_ctrl, text=" Individual ",
                                      bg=ACCENT, fg=TEXT, font=F_SM,
                                      bd=0, padx=8, pady=5, cursor="hand2",
                                      relief="flat", command=self._show_single)
        self._btn_single.pack(side="left", padx=3)
        self._btn_candle = tk.Button(right_ctrl, text=" Candlestick ",
                                      bg=SURF2, fg=MUTED, font=F_SM,
                                      bd=0, padx=8, pady=5, cursor="hand2",
                                      relief="flat", command=self._show_candlestick)
        self._btn_candle.pack(side="left", padx=3)
        self._btn_all = tk.Button(right_ctrl, text=" All Stocks ",
                                   bg=SURF2, fg=MUTED, font=F_SM,
                                   bd=0, padx=8, pady=5, cursor="hand2",
                                   relief="flat", command=self._show_all)
        self._btn_all.pack(side="left", padx=3)

        sym_frame = tk.Frame(ctrl, bg=BG)
        sym_frame.pack(side="right", padx=(0, 20))
        tk.Label(sym_frame, text="Stock:", bg=BG,
                 fg=MUTED, font=F_SM).pack(side="left", padx=(0, 4))
        self._sym_var = tk.StringVar(value="AAPL")
        sym_menu = ttk.Combobox(sym_frame, textvariable=self._sym_var,
                                 values=list(market.STOCKS.keys()),
                                 width=8, state="readonly", font=F_MONO)
        sym_menu.pack(side="left")
        sym_menu.bind("<<ComboboxSelected>>", self._on_sym_change)

        self._chart_frame = tk.Frame(self, bg=BG)
        self._chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self._fig    = Figure(facecolor=BG)
        self._canvas = FigureCanvasTkAgg(self._fig, master=self._chart_frame)
        self._canvas.get_tk_widget().pack(fill="both", expand=True)

    def _on_sym_change(self, _=None):
        self.selected = self._sym_var.get()
        if self._current_view == "single":
            self._draw_single()
        elif self._current_view == "candle":
            self._draw_candlestick()

    def _show_single(self):
        self._current_view = "single"
        self._btn_single.config(bg=ACCENT, fg=TEXT)
        self._btn_candle.config(bg=SURF2,  fg=MUTED)
        self._btn_all.config(   bg=SURF2,  fg=MUTED)
        self._draw_single()

    def _show_candlestick(self):
        self._current_view = "candle"
        self._btn_candle.config(bg=ORANGE, fg=TEXT)
        self._btn_single.config(bg=SURF2,  fg=MUTED)
        self._btn_all.config(   bg=SURF2,  fg=MUTED)
        self._draw_candlestick()

    def _show_all(self):
        self._current_view = "all"
        self._btn_all.config(   bg=ACCENT, fg=TEXT)
        self._btn_single.config(bg=SURF2,  fg=MUTED)
        self._btn_candle.config(bg=SURF2,  fg=MUTED)
        self._draw_all()

    def _draw_candlestick(self):
        """
        Candlestick (OHLC) chart.

        Since we only store daily close prices, OHLC is derived:
            Open  = previous day's close
            Close = this day's close
            High  = max(O,C) + spread  (seeded random per candle)
            Low   = min(O,C) - spread  (seeded random per candle)

        Seeded with hash(symbol + day_index) so candles are
        deterministic — same symbol always shows same candles.

        Green candle = close > open (bullish day)
        Red   candle = close < open (bearish day)
        """
        sym    = self.selected
        prices = market.get_history(sym)

        if len(prices) < 2:
            self._draw_single()
            return

        self._fig.clear()
        ax = self._fig.add_subplot(111, facecolor=SURF)
        mpl_ax_style(ax, SURF)
        self._fig.patch.set_facecolor(BG)
        self._fig.subplots_adjust(left=0.08, right=0.97,
                                   top=0.90, bottom=0.12)

        all_highs = []
        all_lows  = []

        for i, close in enumerate(prices):
            open_p = prices[i - 1] if i > 0 else close

            # Deterministic OHLC spread using seeded RNG
            rng    = random.Random(hash(sym) + i * 1337)
            spread = abs(close - open_p) * 0.4 + close * 0.003
            high   = max(open_p, close) + abs(rng.gauss(0, spread))
            low    = min(open_p, close) - abs(rng.gauss(0, spread))
            all_highs.append(high)
            all_lows.append(low)

            bullish    = close >= open_p
            body_color = GREEN if bullish else RED
            x_pos      = i + 1

            # ── Wick (high-low line) ──
            ax.plot([x_pos, x_pos], [low, high],
                    color=body_color, linewidth=0.9,
                    alpha=0.75, zorder=2)

            # ── Candle body (open → close rectangle) ──
            body_y = min(open_p, close)
            body_h = abs(close - open_p) or close * 0.002
            rect   = mpatches.Rectangle(
                (x_pos - 0.3, body_y), 0.6, body_h,
                facecolor=body_color,
                edgecolor=body_color,
                alpha=0.88, zorder=3)
            ax.add_patch(rect)

        # Axis limits with padding
        ax.set_xlim(0.5, len(prices) + 0.5)
        y_lo  = min(all_lows)
        y_hi  = max(all_highs)
        y_pad = (y_hi - y_lo) * 0.06 or 2.0
        ax.set_ylim(y_lo - y_pad, y_hi + y_pad)

        ax.set_title(f"{sym} — Candlestick  (Day 1 → {len(prices)})",
                     color=TEXT, fontsize=11, fontweight="bold", pad=10)
        ax.set_xlabel("Day", color=MUTED, fontsize=9)
        ax.set_ylabel("Price ($)", color=MUTED, fontsize=9)
        ax.grid(True, color=BORDER, alpha=0.3, linewidth=0.5, zorder=0)
        self._canvas.draw_idle()

    def _draw_single(self):
        sym    = self.selected
        prices = market.get_history(sym)
        days   = list(range(1, len(prices) + 1))
        color  = STOCK_COLORS.get(sym, ACCENT)

        self._fig.clear()
        ax = self._fig.add_subplot(111, facecolor=SURF)
        mpl_ax_style(ax, SURF)
        self._fig.patch.set_facecolor(BG)
        self._fig.subplots_adjust(left=0.08, right=0.97,
                                   top=0.90, bottom=0.12)

        ax.plot(days, prices, color=color, linewidth=2.2,
                label=sym, zorder=3)
        ax.fill_between(days, prices, min(prices) * 0.998,
                         alpha=0.12, color=color)

        if len(prices) >= 5:
            ma5 = [sum(prices[max(0, i-4):i+1]) /
                   min(i+1, 5) for i in range(len(prices))]
            ax.plot(days, ma5, color=YELLOW, linewidth=1.2,
                    linestyle="--", alpha=0.8, label="MA5")

        if len(prices) >= 20:
            ma20 = [sum(prices[max(0, i-19):i+1]) /
                    min(i+1, 20) for i in range(len(prices))]
            ax.plot(days, ma20, color=PURPLE, linewidth=1.2,
                    linestyle="--", alpha=0.8, label="MA20")

        ax.set_title(f"{sym} — Price History  (Day 1 → {len(days)})",
                     color=TEXT, fontsize=11, fontweight="bold", pad=10)
        ax.set_xlabel("Day", color=MUTED, fontsize=9)
        ax.set_ylabel("Price ($)", color=MUTED, fontsize=9)
        ax.grid(True, color=BORDER, alpha=0.5, linewidth=0.7)
        ax.legend(facecolor=SURF2, edgecolor=BORDER,
                  labelcolor=TEXT, fontsize=8, framealpha=0.9)
        self._canvas.draw_idle()

    def _draw_all(self):
        symbols = list(market.STOCKS.keys())
        colors  = [STOCK_COLORS[s] for s in symbols]

        self._fig.clear()
        self._fig.patch.set_facecolor(BG)
        self._fig.suptitle("All Stocks — Price History",
                            color=TEXT, fontsize=12,
                            fontweight="bold", y=0.98)

        for i, (sym, color) in enumerate(zip(symbols, colors)):
            ax     = self._fig.add_subplot(2, 3, i + 1, facecolor=SURF)
            prices = market.get_history(sym)
            days   = list(range(1, len(prices) + 1))
            mpl_ax_style(ax, SURF)
            ax.plot(days, prices, color=color, linewidth=1.8)
            ax.fill_between(days, prices,
                             min(prices) * 0.998, alpha=0.12, color=color)
            ax.set_title(sym, color=TEXT, fontsize=10,
                         fontweight="bold", pad=4)
            ax.set_xlabel("Day", color=MUTED, fontsize=7)
            ax.grid(True, color=BORDER, alpha=0.4, linewidth=0.5)

        self._fig.subplots_adjust(hspace=0.45, wspace=0.35,
                                   left=0.07, right=0.97,
                                   top=0.91, bottom=0.10)
        self._canvas.draw_idle()

    def refresh(self):
        if self._current_view == "single":
            self._draw_single()
        elif self._current_view == "candle":
            self._draw_candlestick()
        else:
            self._draw_all()

# ═══════════════════════════════════════════════════════════════════
# PANEL: BOT
# ═══════════════════════════════════════════════════════════════════

class BotPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app        = app
        self._log_lines = []
        self._build()
        self._refresh_analyses()

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(hdr, text="TRADING BOT", bg=BG,
                 fg=TEXT, font=F_TITL).pack(side="left")
        tk.Label(hdr, text="Triple Confirmation: MA × RSI × MACD",
                 bg=BG, fg=MUTED, font=F_SM).pack(side="left", padx=16)
        tk.Button(hdr, text=" ▶  RUN BOT ", bg=PURPLE, fg=TEXT,
                  font=F_BOLD, bd=0, padx=14, pady=7,
                  cursor="hand2", relief="flat",
                  command=self._run_bot).pack(side="right")

        grid_outer = tk.Frame(self, bg=BG)
        grid_outer.pack(fill="x", padx=20, pady=(0, 12))
        self._cards_frame  = grid_outer
        self._signal_cards = {}
        self._build_cards()

        log_frame = tk.Frame(self, bg=SURF,
                              highlightthickness=1, highlightbackground=BORDER)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        tk.Label(log_frame, text=" BOT ACTION LOG",
                 bg=SURF, fg=MUTED, font=F_SM).pack(
                     anchor="w", padx=8, pady=(8, 2))

        self._log_text = tk.Text(log_frame, bg=SURF, fg=TEXT, font=F_SM,
                                  bd=0, state="disabled",
                                  highlightthickness=0, wrap="word", height=8)
        vsb = ttk.Scrollbar(log_frame, orient="vertical",
                             style="Dark.Vertical.TScrollbar",
                             command=self._log_text.yview)
        self._log_text.configure(yscrollcommand=vsb.set)
        self._log_text.pack(side="left", fill="both",
                             expand=True, padx=(8, 0), pady=(0, 8))
        vsb.pack(side="right", fill="y", pady=(0, 8), padx=(0, 4))

    def _build_cards(self):
        for widget in self._cards_frame.winfo_children():
            widget.destroy()
        self._signal_cards = {}

        for i, sym in enumerate(market.STOCKS):
            col  = i % 5
            card = tk.Frame(self._cards_frame, bg=SURF2,
                             highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=0, column=col, padx=5, pady=4, sticky="ew")
            self._cards_frame.columnconfigure(col, weight=1)

            color = STOCK_COLORS.get(sym, ACCENT)
            tk.Frame(card, bg=color, height=3).pack(fill="x")
            tk.Label(card, text=sym, bg=SURF2,
                     fg=color, font=F_BOLD).pack(pady=(8, 2))

            sig_lbl   = tk.Label(card, text="—", bg=SURF2,
                                  fg=MUTED, font=F_BOLD)
            sig_lbl.pack()
            score_lbl = tk.Label(card, text="Score: —", bg=SURF2,
                                  fg=MUTED, font=F_SM)
            score_lbl.pack(pady=(0, 2))
            details   = tk.Label(card, text="", bg=SURF2,
                                  fg=MUTED, font=F_SM,
                                  justify="left", wraplength=130)
            details.pack(padx=8, pady=(0, 8))

            self._signal_cards[sym] = {
                "signal":  sig_lbl,
                "score":   score_lbl,
                "details": details,
            }

    def _refresh_analyses(self):
        analyses = bot.get_all_analyses()
        for sym, a in analyses.items():
            if sym not in self._signal_cards:
                continue
            card   = self._signal_cards[sym]
            signal = a.get("signal", "—")
            score  = a.get("score",  0)
            ready  = a.get("data_ready", False)

            sig_color = {
                "STRONG BUY":  GREEN,
                "BUY":         GREEN,
                "HOLD":        YELLOW,
                "SELL":        RED,
                "STRONG SELL": RED,
                "WAIT":        MUTED,
            }.get(signal, MUTED)

            card["signal"].config(text=signal, fg=sig_color)
            card["score"].config(
                text=f"Score: {'+' if score > 0 else ''}{score}"
                if ready else "—"
            )
            if ready:
                parts = []
                if a.get("ma5")  is not None: parts.append(f"MA5:  {a['ma5']:.1f}")
                if a.get("ma20") is not None: parts.append(f"MA20: {a['ma20']:.1f}")
                if a.get("rsi")  is not None: parts.append(f"RSI:  {a['rsi']:.1f}")
                card["details"].config(text="\n".join(parts), fg=MUTED)
            else:
                reasons = a.get("reasons", [])
                card["details"].config(
                    text=reasons[0] if reasons else "—", fg=DIM)

    def _run_bot(self):
        """
        Manual RUN BOT button handler.
        Step 1 → Analyse all stocks (NO trades yet)
        Step 2 → Show proposed trades to user
        Step 3 → Ask for confirmation
        Step 4 → Only execute if user confirms YES
        """
        # ── Step 1: Analyse without trading ──
        analyses = bot.get_all_analyses()
        self._refresh_analyses()

        # ── Step 2: Build proposal summary ──
        proposals    = []
        has_actions  = False   # True only if at least one BUY or SELL exists

        for sym, a in analyses.items():
            signal = a.get("signal", "WAIT")
            if not a.get("data_ready", False):
                proposals.append(f"  WAIT  {sym:5}  — {a['reasons'][0]}")
                continue
            if signal in ("STRONG BUY", "BUY"):
                cost = round(a["price"] * 2, 2)
                can  = "✓" if portfolio.balance >= cost else "✗ insufficient funds"
                proposals.append(
                    f"  BUY   {sym:5}  {signal:12}  2 shares @ ${a['price']:.2f}  {can}")
                if portfolio.balance >= cost:
                    has_actions = True
            elif signal in ("STRONG SELL", "SELL"):
                owned = portfolio.holdings.get(sym, {}).get("shares", 0)
                qty   = min(owned, 2)
                can   = f"✓ own {owned}" if qty > 0 else "✗ no shares owned"
                proposals.append(
                    f"  SELL  {sym:5}  {signal:12}  {qty} shares @ ${a['price']:.2f}  {can}")
                if qty > 0:
                    has_actions = True
            else:
                proposals.append(f"  HOLD  {sym:5}  {signal}")

        summary = "\n".join(proposals)

        # ── Step 3: Only ask if there's something actionable ──
        if not has_actions:
            # Nothing to trade — just show the analysis log, no dialog
            lines = [
                f"─── Day {market.current_day}  {now_str()} ───",
                "  Analysis complete — no actionable signals.",
            ] + [f"  {p.strip()}" for p in proposals]
            self._log(lines)
            return

        confirmed = messagebox.askyesno(
            "Bot Trade Proposals",
            f"Day {market.current_day} — Bot Analysis\n"
            f"{'─' * 52}\n"
            f"{summary}\n\n"
            f"Execute these trades?",
            parent=self.winfo_toplevel()
        )

        # ── Step 4: Execute only if confirmed ──
        if not confirmed:
            lines = [f"─── Day {market.current_day}  {now_str()} ───",
                     "  User declined — no trades executed."]
            self._log(lines)
            return

        actions, _ = app_state.run_bot(shares_per_trade=2)
        self._refresh_analyses()

        lines = [f"─── Day {market.current_day}  {now_str()} ───"]
        for a in actions:
            sym    = a["symbol"]
            action = a["action"]
            signal = a["signal"]
            if action in ("BUY", "SELL"):
                res  = a.get("result", {})
                verb = "BUY " if action == "BUY" else "SELL"
                if res.get("success"):
                    lines.append(f"  {verb} {sym:5}  {signal}  → {res['message']}")
                else:
                    lines.append(f"  SKIP {sym:5}  {signal}  → {res.get('message','')}")
            elif action == "HOLD":
                lines.append(f"  HOLD {sym:5}  {signal}")
            elif action == "WAIT":
                lines.append(f"  WAIT {sym:5}  {a.get('message','')}")
            elif action == "SKIP":
                lines.append(f"  SKIP {sym:5}  {signal}  {a.get('message','')}")

        self._log(lines)
        self.app.refresh_all_panels()

    def _log(self, lines):
        self._log_text.config(state="normal")
        self._log_text.insert("1.0", "\n".join(lines) + "\n\n")
        self._log_text.config(state="disabled")

    def refresh(self):
        self._refresh_analyses()

# ═══════════════════════════════════════════════════════════════════
# PANEL: NEWS
# ═══════════════════════════════════════════════════════════════════

class NewsPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="MARKET NEWS", bg=BG,
                 fg=TEXT, font=F_TITL).pack(
                     anchor="w", padx=20, pady=(18, 10))

        feed_frame = tk.Frame(self, bg=SURF,
                               highlightthickness=1, highlightbackground=BORDER)
        feed_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self._feed_text = tk.Text(feed_frame, bg=SURF, fg=TEXT,
                                   font=F_MONO, bd=0, state="disabled",
                                   highlightthickness=0, wrap="word",
                                   padx=12, pady=8)
        vsb = ttk.Scrollbar(feed_frame, orient="vertical",
                             style="Dark.Vertical.TScrollbar",
                             command=self._feed_text.yview)
        self._feed_text.configure(yscrollcommand=vsb.set)
        self._feed_text.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._feed_text.tag_configure("good",    foreground=GREEN)
        self._feed_text.tag_configure("bad",     foreground=RED)
        self._feed_text.tag_configure("day_hdr", foreground=ACCENT,
                                       font=F_BOLD)
        self._feed_text.tag_configure("muted",   foreground=DIM)

    def add_news(self, events: list, day: int):
        self._feed_text.config(state="normal")
        self._feed_text.insert("1.0", "\n")
        for ev in reversed(events):
            kind     = ev.get("type", "good")
            symbol   = ev["symbol"]
            headline = ev["headline"]
            chg      = ev["change_pct"]
            icon     = "▲" if kind == "good" else "▼"
            line = (f"  {icon} {symbol}  {headline}"
                    f"  ({'+' if kind == 'good' else '-'}{chg}%)\n")
            self._feed_text.insert("1.0", line, kind)
        self._feed_text.insert("1.0",
            f"  Day {day}  ─────────────────────────────\n", "day_hdr")
        self._feed_text.config(state="disabled")

    def load_feed(self):
        """
        Repopulates the news feed from app_state.news_feed.
        Called once after data is loaded on startup so previous
        news events appear in the NEWS panel correctly.
        """
        feed = app_state.get_news_feed()  # newest first
        if not feed:
            return

        # Group events by day and render oldest→newest (bottom→top)
        # so newest events always appear at the top of the widget
        from itertools import groupby
        # Sort oldest first for insertion (we prepend each group)
        sorted_feed = sorted(feed, key=lambda e: e.get("day", 0))
        grouped = {}
        for ev in sorted_feed:
            d = ev.get("day", 0)
            grouped.setdefault(d, []).append(ev)

        self._feed_text.config(state="normal")
        self._feed_text.delete("1.0", "end")

        # Insert oldest day first so newest ends up on top
        for day_num in sorted(grouped.keys()):
            events = grouped[day_num]
            self._feed_text.insert("1.0", "\n")
            for ev in reversed(events):
                kind     = ev.get("type", "good")
                symbol   = ev.get("symbol", "")
                headline = ev.get("headline", "")
                chg      = ev.get("change_pct", 0)
                icon     = "▲" if kind == "good" else "▼"
                line = (f"  {icon} {symbol}  {headline}"
                        f"  ({'+' if kind == 'good' else '-'}{chg}%)\n")
                self._feed_text.insert("1.0", line, kind)
            self._feed_text.insert(
                "1.0",
                f"  Day {day_num}  ─────────────────────────────\n",
                "day_hdr")

        self._feed_text.config(state="disabled")

    def refresh(self):
        self.load_feed()

# ═══════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════

class TradingApp:
    """
    Main trading terminal window.

    Layout:
    ┌─────────────────────────────────────────────────────────┐
    │  TOP BAR  ─  Day, Balance, Total Value, P&L, Clock       │
    ├──────────┬──────────────────────────────────────────────┤
    │          │                                              │
    │ SIDEBAR  │      ACTIVE PANEL                           │
    │          │                                              │
    │ Nav      │                                              │
    │ Actions  │                                              │
    │          │                                              │
    ├──────────┴──────────────────────────────────────────────┤
    │  NEWS TICKER  ─  scrolling recent events                │
    └─────────────────────────────────────────────────────────┘
    """
    def __init__(self, root: tk.Tk):
        self.root          = root
        self._panels       = {}
        self._active_panel = None
        self._active_btn   = None
        self._tick_job     = None
        self._ticker_job   = None
        self._ticker_pos   = 0
        self._ticker_text  = "  —  Welcome to Stock Market Simulator V2 MAX  —  "
        self._animating    = False
        self._auto_bot     = False
        self._bot_interval = 1      # run auto-bot every N days (1 = every day)
        self._bot_day_ctr  = 0      # counts days since last auto-bot run

        self._setup_window()
        self._load_data()
        setup_style()
        self._build_layout()
        self._setup_keyboard_shortcuts()
        self._start_tick_loop()
        self._start_ticker()
        # Populate news panel from saved feed
        news_panel = self._panels.get("news")
        if news_panel:
            news_panel.load_feed()
        self._navigate("market")

    def _setup_window(self):
        self.root.title("Stock Market Simulator V2 MAX")
        self.root.configure(bg=BG)
        self.root.geometry("1420x860")
        self.root.minsize(1100, 700)
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw - 1420) // 2
        y  = (sh - 860)  // 2
        self.root.geometry(f"1420x860+{x}+{y}")

    def _load_data(self):
        app_state.load()
        # Reinitialize tick buffers from loaded prices
        for sym in market.STOCKS:
            price = market.get_price(sym)
            TICK_HIST[sym] = deque([price] * 60, maxlen=80)

    def _build_layout(self):
        self._topbar = tk.Frame(self.root, bg=SURF, height=58,
                                 highlightthickness=1,
                                 highlightbackground=BORDER)
        self._topbar.pack(fill="x")
        self._topbar.pack_propagate(False)
        self._build_topbar()

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        self._sidebar = tk.Frame(body, bg=BG, width=200,
                                  highlightthickness=1,
                                  highlightbackground=BORDER)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._build_sidebar()

        self._content = tk.Frame(body, bg=BG)
        self._content.pack(side="left", fill="both", expand=True)
        self._build_panels()

        self._ticker_bar = tk.Frame(self.root, bg=SURF2, height=28,
                                     highlightthickness=1,
                                     highlightbackground=BORDER)
        self._ticker_bar.pack(fill="x", side="bottom")
        self._ticker_bar.pack_propagate(False)
        self._build_ticker()

    def _build_topbar(self):
        left = tk.Frame(self._topbar, bg=SURF)
        left.pack(side="left", fill="y", padx=(16, 0))
        tk.Label(left, text="▣ SIMTRADE", bg=SURF,
                 fg=ACCENT, font=("Consolas", 15, "bold")).pack(
                     side="left", padx=(0, 20))

        tk.Frame(self._topbar, bg=BORDER, width=1).pack(
            side="left", fill="y", pady=10)

        stats = tk.Frame(self._topbar, bg=SURF)
        stats.pack(side="left", fill="both", expand=True, padx=20)

        def stat_col(label, fg=TEXT):
            col = tk.Frame(stats, bg=SURF)
            col.pack(side="left", padx=24)
            tk.Label(col, text=label, bg=SURF, fg=MUTED, font=F_SM).pack(anchor="w")
            lbl = tk.Label(col, text="—", bg=SURF, fg=fg, font=F_BOLD)
            lbl.pack(anchor="w")
            return lbl

        self._lbl_day     = stat_col("DAY",          ACCENT)
        self._lbl_balance = stat_col("CASH BALANCE", CYAN)
        self._lbl_total   = stat_col("TOTAL VALUE",  TEXT)
        self._lbl_pl      = stat_col("P&L",          MUTED)

        self._lbl_clock = tk.Label(self._topbar, bg=SURF, fg=DIM, font=F_SM)
        self._lbl_clock.pack(side="right", padx=20)
        self._update_clock()
        self._update_topbar()

    def _build_sidebar(self):
        tk.Label(self._sidebar, text="TERMINAL",
                 bg=BG, fg=DIM, font=F_SM).pack(
                     anchor="w", padx=16, pady=(16, 8))

        nav_items = [
            ("📈", "MARKET",    "market"),
            ("💼", "PORTFOLIO", "portfolio"),
            ("📋", "HISTORY",   "history"),
            ("📊", "CHARTS",    "charts"),
            ("🤖", "BOT",       "bot"),
            ("📰", "NEWS",      "news"),
        ]
        self._nav_buttons = {}
        for icon, label, key in nav_items:
            btn = SidebarButton(self._sidebar, icon, label,
                                command=lambda k=key: self._navigate(k))
            btn.pack(fill="x")
            self._nav_buttons[key] = btn

        tk.Frame(self._sidebar, bg=BORDER, height=1).pack(
            fill="x", padx=16, pady=12)
        tk.Label(self._sidebar, text="ACTIONS",
                 bg=BG, fg=DIM, font=F_SM).pack(
                     anchor="w", padx=16, pady=(0, 6))

        def action_btn(text, color, cmd):
            btn = tk.Button(self._sidebar, text=text, bg=color, fg=TEXT,
                             font=F_SM, bd=0, pady=9, cursor="hand2",
                             relief="flat", command=cmd)
            btn.pack(fill="x", padx=14, pady=3)
            return btn

        self._btn_nextday = action_btn(" ⏭  NEXT DAY",  ACCENT, self._do_next_day)
        action_btn(" 💾  SAVE",       SURF2, self._do_save)
        action_btn(" 💰  ADD FUNDS",  CYAN,  self._do_add_balance)
        action_btn(" 🛒  BUY",        GREEN, self._do_buy)
        action_btn(" 📤  SELL",       RED,   self._do_sell)

        # Auto-bot toggle
        tk.Frame(self._sidebar, bg=BORDER, height=1).pack(
            fill="x", padx=16, pady=8)
        self._btn_autobot = tk.Button(
            self._sidebar,
            text=" 🤖  AUTO BOT: OFF",
            bg=SURF2, fg=MUTED, font=F_SM,
            bd=0, pady=9, cursor="hand2", relief="flat",
            command=self._toggle_auto_bot)
        self._btn_autobot.pack(fill="x", padx=14, pady=3)

        # ── N-day bot interval ──
        interval_frame = tk.Frame(self._sidebar, bg=BG)
        interval_frame.pack(fill="x", padx=14, pady=(4, 0))
        tk.Label(interval_frame, text="Bot every:", bg=BG,
                 fg=DIM, font=F_SM).pack(side="left")
        self._interval_var = tk.IntVar(value=1)
        vcmd = (self.root.register(
            lambda v: v.isdigit() and 1 <= int(v) <= 99), "%P")
        self._interval_spin = tk.Spinbox(
            interval_frame,
            from_=1, to=99,
            textvariable=self._interval_var,
            width=3, font=F_SM,
            bg=SURF2, fg=TEXT, bd=0,
            buttonbackground=SURF3,
            insertbackground=TEXT,
            highlightthickness=1,
            highlightbackground=BORDER,
            command=self._on_interval_change)
        self._interval_spin.pack(side="left", padx=(6, 4))
        tk.Label(interval_frame, text="days", bg=BG,
                 fg=DIM, font=F_SM).pack(side="left")
        self._interval_spin.bind("<FocusOut>", self._on_interval_change)

    def _build_panels(self):
        self._panels["market"]    = MarketPanel(self._content,    self)
        self._panels["portfolio"] = PortfolioPanel(self._content, self)
        self._panels["history"]   = HistoryPanel(self._content,   self)
        self._panels["charts"]    = ChartPanel(self._content,     self)
        self._panels["bot"]       = BotPanel(self._content,       self)
        self._panels["news"]      = NewsPanel(self._content,      self)

        for panel in self._panels.values():
            panel.place(relwidth=1, relheight=1)
            panel.place_forget()

    def _build_ticker(self):
        tk.Label(self._ticker_bar, text=" NEWS",
                 bg=ACCENT, fg=TEXT, font=F_SM,
                 padx=8).pack(side="left", fill="y")
        self._ticker_lbl = tk.Label(self._ticker_bar,
                                     text=self._ticker_text,
                                     bg=SURF2, fg=MUTED, font=F_SM,
                                     anchor="w")
        self._ticker_lbl.pack(side="left", fill="both", expand=True, padx=8)

    # ─────────────────────────────────────────────────────────
    # NAVIGATION
    # ─────────────────────────────────────────────────────────

    def _navigate(self, key: str):
        if self._active_btn:
            self._active_btn.set_active(False)
        if self._active_panel:
            self._active_panel.place_forget()

        panel = self._panels[key]
        panel.place(relwidth=1, relheight=1)
        self._active_panel = panel

        btn = self._nav_buttons.get(key)
        if btn:
            btn.set_active(True)
            self._active_btn = btn

        if key in ("portfolio", "history", "charts", "bot", "news"):
            panel.refresh()

    # ─────────────────────────────────────────────────────────
    # TOPBAR
    # ─────────────────────────────────────────────────────────

    def _update_topbar(self):
        """Full refresh using official prices."""
        data = app_state.get_portfolio_snapshot()
        pl   = data["profit_loss"]
        self._lbl_day.config(text=f"Day {market.current_day}")
        self._lbl_balance.config(text=fmt_p(data["balance"]))
        self._lbl_total.config(text=fmt_p(data["total_value"]))
        self._lbl_pl.config(text=fmt_pl(pl), fg=pl_color(pl))

    def _update_topbar_live(self, tick_prices: dict):
        """
        Live topbar using tick prices every 2 seconds.
        FIXED: Correctly indented as method of TradingApp.
        """
        stock_value = 0.0
        for symbol, data in portfolio.holdings.items():
            price = tick_prices.get(symbol, market.get_price(symbol))
            stock_value += data["shares"] * price
        live_total = round(portfolio.balance + stock_value, 2)
        live_pl    = live_total - portfolio.STARTING_BALANCE
        self._lbl_day.config(text=f"Day {market.current_day}")
        self._lbl_balance.config(text=fmt_p(portfolio.balance))
        self._lbl_total.config(text=fmt_p(live_total))
        self._lbl_pl.config(text=fmt_pl(live_pl), fg=pl_color(live_pl))

    def _update_clock(self):
        self._lbl_clock.config(text=now_str())
        self.root.after(1000, self._update_clock)

    # ─────────────────────────────────────────────────────────
    # KEYBOARD SHORTCUTS  (Step 10)
    # ─────────────────────────────────────────────────────────

    def _setup_keyboard_shortcuts(self):
        """
        Bind global keyboard shortcuts to the root window.

        Navigation:
            1  → Market panel
            2  → Portfolio panel
            3  → History panel
            4  → Charts panel
            5  → Bot panel
            6  → News panel

        Actions:
            N  → Next Day
            B  → Buy dialog
            S  → Sell dialog
            A  → Toggle Auto-Bot
            Ctrl+S → Save portfolio

        All bindings are case-insensitive (both <n> and <N> work).
        Bindings are suppressed when a dialog/entry has focus so
        typing in quantity fields doesn't accidentally trigger them.
        """
        r = self.root

        def guard(fn):
            """Only fire shortcut if no Entry/Spinbox has focus."""
            def _inner(event):
                focused = r.focus_get()
                if isinstance(focused, (tk.Entry, tk.Spinbox)):
                    return
                fn()
            return _inner

        # ── Navigation ──
        r.bind("<Key-1>", guard(lambda: self._navigate("market")))
        r.bind("<Key-2>", guard(lambda: self._navigate("portfolio")))
        r.bind("<Key-3>", guard(lambda: self._navigate("history")))
        r.bind("<Key-4>", guard(lambda: self._navigate("charts")))
        r.bind("<Key-5>", guard(lambda: self._navigate("bot")))
        r.bind("<Key-6>", guard(lambda: self._navigate("news")))

        # ── Actions (case-insensitive) ──
        for key in ("<n>", "<N>"):
            r.bind(key, guard(self._do_next_day))
        for key in ("<b>", "<B>"):
            r.bind(key, guard(self._do_buy))
        for key in ("<s>", "<S>"):
            r.bind(key, guard(self._do_sell))
        for key in ("<a>", "<A>"):
            r.bind(key, guard(self._toggle_auto_bot))

        # ── Ctrl+S → Save ──
        r.bind("<Control-s>", lambda e: self._do_save())
        r.bind("<Control-S>", lambda e: self._do_save())

    # ─────────────────────────────────────────────────────────
    # TICK LOOP
    # ─────────────────────────────────────────────────────────

    def _start_tick_loop(self):
        self._tick_loop()

    def _tick_loop(self):
        """
        Live tick every 2 seconds.
        FIXED: Body correctly indented inside method.
        """
        tick = app_state.update_tick()
        for sym, price in tick.items():
            TICK_HIST[sym].append(price)

        mp = self._panels.get("market")
        if mp and self._active_panel is mp:
            mp.update_tick(tick)

        self._update_topbar_live(tick)

        pp = self._panels.get("portfolio")
        if pp and self._active_panel is pp:
            pp.live_update(tick)

        self._tick_job = self.root.after(2000, self._tick_loop)

    # ─────────────────────────────────────────────────────────
    # NEXT DAY
    # ─────────────────────────────────────────────────────────

    def _do_next_day(self):
        """
        CHART FIX: Advance day FIRST to know new prices,
        then animate from old price TO new price using linear
        interpolation + small noise. This eliminates the cliff
        caused by news events because the animation always
        lands exactly on the new official price.
        """
        if self._animating:
            return
        self._animating = True
        self._btn_nextday.config(state="disabled", text=" ⏳ PROCESSING")

        if self._tick_job:
            self.root.after_cancel(self._tick_job)
            self._tick_job = None

        # ── Step 1: Capture old prices before advancing ──
        old_prices = {s: market.get_price(s) for s in market.STOCKS}

        # ── Step 2: Advance day NOW so we know the new prices ──
        result = app_state.advance_day()

        # ── Step 3: Capture new official prices ──
        new_prices = {s: market.get_price(s) for s in market.STOCKS}

        # ── Step 4: Animate from old → new using lerp + tiny noise ──
        step        = [0]
        total_steps = 24

        def animate():
            if step[0] < total_steps:
                t    = step[0] / total_steps  # 0.0 → 1.0 (progress)
                tick = {}
                for sym in market.STOCKS:
                    # Linear interpolation from old to new price
                    lerp  = old_prices[sym] + t * (new_prices[sym] - old_prices[sym])
                    # Add tiny organic noise (0.05% std — barely visible)
                    noise = random.gauss(0, 0.0005) * old_prices[sym]
                    tick[sym] = round(max(lerp + noise, 1.0), 2)

                for sym, price in tick.items():
                    TICK_HIST[sym].append(price)

                mp = self._panels.get("market")
                if mp and self._active_panel is mp:
                    mp.update_tick(tick)

                self._update_topbar_live(tick)
                step[0] += 1
                self.root.after(90, animate)
            else:
                # Final step: append exact official close price
                for sym in market.STOCKS:
                    TICK_HIST[sym].append(market.get_price(sym))

                self._on_day_changed(result)
                self._btn_nextday.config(state="normal",
                                          text=" ⏭  NEXT DAY")
                self._animating = False
                self._tick_job  = self.root.after(2000, self._tick_loop)

        animate()

    def _on_day_changed(self, result: dict):
        self._update_topbar()

        # ── AUTO BOT: runs every N days when enabled ──
        if self._auto_bot:
            self._bot_day_ctr += 1
            if self._bot_day_ctr >= self._bot_interval:
                self._bot_day_ctr = 0
                actions, _ = app_state.run_bot(shares_per_trade=2)

                # Log results into the Bot panel
                bot_panel = self._panels.get("bot")
                if bot_panel:
                    lines = [f"🤖 AUTO  Day {market.current_day}  {now_str()}  "
                             f"(every {self._bot_interval}d)"]
                    for a in actions:
                        sym    = a["symbol"]
                        action = a["action"]
                        signal = a["signal"]
                        if action in ("BUY", "SELL"):
                            res  = a.get("result", {})
                            verb = "BUY " if action == "BUY" else "SELL"
                            if res.get("success"):
                                lines.append(
                                    f"  {verb} {sym:5} {signal} → {res['message']}")
                            else:
                                lines.append(
                                    f"  SKIP {sym:5} {signal} → {res.get('message','')}")
                        elif action == "HOLD":
                            lines.append(f"  HOLD {sym:5} {signal}")
                        elif action in ("WAIT", "SKIP"):
                            lines.append(f"  {action} {sym:5} {a.get('message', signal)}")
                    bot_panel._log(lines)
                    bot_panel._refresh_analyses()

                # Flash the AUTO BOT button green to confirm it fired
                self._btn_autobot.config(bg=GREEN)
                self.root.after(600, lambda: self._btn_autobot.config(
                    bg=PURPLE if self._auto_bot else SURF2))

        events = result.get("news_events", [])
        if events:
            self._panels["news"].add_news(events, result["day"])
            parts = []
            for e in events:
                icon = "▲" if e["type"] == "good" else "▼"
                parts.append(
                    f"  {icon} {e['symbol']}: {e['headline']}"
                    f" ({'+' if e['type'] == 'good' else '-'}"
                    f"{e['change_pct']}%)  |"
                )
            if parts:
                self._ticker_text = "  " + "  ".join(parts) + "  "

        self.refresh_all_panels()
        mp = self._panels.get("market")
        if mp:
            mp.on_day_changed()

    def refresh_all_panels(self):
        self._panels["portfolio"].refresh()
        self._panels["history"].refresh()
        self._panels["charts"].refresh()
        self._panels["bot"].refresh()
        self._update_topbar()

    # ─────────────────────────────────────────────────────────
    # TICKER
    # ─────────────────────────────────────────────────────────

    def _start_ticker(self):
        self._scroll_ticker()

    def _scroll_ticker(self):
        text = self._ticker_text
        if len(text) > 0:
            display = text[self._ticker_pos:] + text[:self._ticker_pos]
            self._ticker_lbl.config(text=display[:140])
            self._ticker_pos = (self._ticker_pos + 1) % len(text)
        self._ticker_job = self.root.after(120, self._scroll_ticker)

    # ─────────────────────────────────────────────────────────
    # ACTION HANDLERS
    # ─────────────────────────────────────────────────────────

    def _do_buy(self):
        dlg = TradeDialog(self.root, "BUY")
        if dlg.result:
            sym, qty = dlg.result
            result = app_state.execute_trade("BUY", sym, qty)
            if result["success"]:
                messagebox.showinfo("Order Executed",
                                    result["message"], parent=self.root)
                self.refresh_all_panels()
            else:
                messagebox.showerror("Order Rejected",
                                     result["message"], parent=self.root)

    def _do_sell(self):
        dlg = TradeDialog(self.root, "SELL")
        if dlg.result:
            sym, qty = dlg.result
            result = app_state.execute_trade("SELL", sym, qty)
            if result["success"]:
                messagebox.showinfo("Order Executed",
                                    result["message"], parent=self.root)
                self.refresh_all_panels()
            else:
                messagebox.showerror("Order Rejected",
                                     result["message"], parent=self.root)

    def _toggle_auto_bot(self):
        """
        Toggle autonomous bot on/off.
        ON  → bot silently trades every N days (no dialogs)
        OFF → bot only runs when manually triggered from Bot panel
        """
        self._auto_bot    = not self._auto_bot
        self._bot_day_ctr = 0   # reset counter on toggle
        if self._auto_bot:
            self._btn_autobot.config(
                text=" 🤖  AUTO BOT: ON",
                bg=PURPLE, fg=TEXT)
        else:
            self._btn_autobot.config(
                text=" 🤖  AUTO BOT: OFF",
                bg=SURF2, fg=MUTED)

    def _on_interval_change(self, _=None):
        """Update bot interval from spinner value."""
        try:
            v = int(self._interval_var.get())
            if v < 1:  v = 1
            if v > 99: v = 99
            self._bot_interval = v
            self._bot_day_ctr  = 0
        except (ValueError, tk.TclError):
            self._interval_var.set(self._bot_interval)

    def _do_add_balance(self):
        dlg = AddBalanceDialog(self.root)
        if dlg.result:
            result = app_state.add_balance(dlg.result)
            if result["success"]:
                self._update_topbar()
                self._panels["portfolio"].refresh()
                messagebox.showinfo("Funds Added",
                                    result["message"], parent=self.root)

    def _do_save(self):
        result = app_state.save()
        if result["success"]:
            messagebox.showinfo("Saved",
                                "Portfolio and history saved.",
                                parent=self.root)
        else:
            messagebox.showerror("Save Failed",
                                 result["message"], parent=self.root)

# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app  = TradingApp(root)

    def on_close():
        if messagebox.askyesno(
            "Exit",
            f"Save portfolio before exiting?\n\n"
            f"Final Value: {fmt_p(portfolio.get_total_value())}",
            parent=root
        ):
            app_state.save()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()