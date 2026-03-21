# ─────────────────────────────────────────────
# Project  : Stock Market Simulator — GUI Edition
# Author   : Parth
# College  : DMCE — AI-DS, Sem 2
# Year     : 2025
# File     : main_gui.py
# Version  : 2.0 — Professional Trading Terminal
# ─────────────────────────────────────────────

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

import market
import trading
import portfolio
import history
import bot

# ══════════════════════════════════════════════
#  COLOR PALETTE — Professional Dark Terminal
# ══════════════════════════════════════════════
C = {
    'bg':      '#0D1117',   # main background
    'panel':   '#161B22',   # sidebar / panels
    'card':    '#21262D',   # cards / inputs
    'border':  '#30363D',   # borders / dividers
    'text':    '#E6EDF3',   # primary text
    'muted':   '#8B949E',   # secondary text
    'accent':  '#58A6FF',   # blue accent (links, highlights)
    'green':   '#3FB950',   # buy / profit
    'red':     '#F85149',   # sell / loss
    'gold':    '#D29922',   # day counter / warnings
    'purple':  '#A371F7',   # bot / special
    'teal':    '#39D353',   # live indicator
}

STOCK_COLORS = {
    'AAPL': '#58A6FF',
    'TSLA': '#F85149',
    'GOOG': '#3FB950',
    'AMZN': '#D29922',
    'MSFT': '#A371F7',
}


# ══════════════════════════════════════════════
#  MAIN APPLICATION CLASS
# ══════════════════════════════════════════════
class TradingApp:

    def __init__(self):
        # ── Load saved data ──────────────────
        portfolio.load_portfolio()
        portfolio.load_history()

        # ── Root window ──────────────────────
        self.root = tk.Tk()
        self.root.title('TradeDESK  —  Stock Market Simulator')
        self.root.geometry('1280x820')
        self.root.minsize(1100, 720)
        self.root.configure(bg=C['bg'])
        try:
            self.root.state('zoomed')  # Start maximized on Windows
        except Exception:
            pass

        # ── State ────────────────────────────
        self.selected_stock = tk.StringVar(value='AAPL')
        self.live_mode      = tk.BooleanVar(value=False)
        self.status_msg     = tk.StringVar(value='  Ready — Welcome to TradeDESK')
        self.current_tab    = 'market'
        self.prev_prices    = {s: market.get_price(s) for s in market.STOCKS}
        self.price_labels   = {}
        self.change_labels  = {}
        self.qty_var        = tk.StringVar(value='1')

        # ── Build UI ─────────────────────────
        self._setup_styles()
        self._build_topbar()
        self._build_body()
        self._build_statusbar()

        # ── Start loops ──────────────────────
        self._update_clock()
        self._auto_refresh()

        # ── Show default tab ─────────────────
        self._switch_tab('market')

        self.root.protocol('WM_DELETE_WINDOW', self._on_close)
        self.root.mainloop()

    # ══════════════════════════════════════════
    #  STYLES
    # ══════════════════════════════════════════
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Dark.Treeview',
            background=C['panel'],
            foreground=C['text'],
            fieldbackground=C['panel'],
            borderwidth=0,
            rowheight=34,
            font=('Consolas', 10),
        )
        style.configure('Dark.Treeview.Heading',
            background=C['card'],
            foreground=C['muted'],
            relief='flat',
            font=('Segoe UI', 9, 'bold'),
            padding=(8, 6),
        )
        style.map('Dark.Treeview',
            background=[('selected', '#1F3A5F')],
            foreground=[('selected', C['accent'])],
        )
        style.configure('Dark.Vertical.TScrollbar',
            background=C['card'],
            troughcolor=C['panel'],
            borderwidth=0,
            arrowcolor=C['muted'],
            width=8,
        )

    # ══════════════════════════════════════════
    #  TOP BAR
    # ══════════════════════════════════════════
    def _build_topbar(self):
        bar = tk.Frame(self.root, bg=C['panel'], height=60)
        bar.pack(fill='x', side='top')
        bar.pack_propagate(False)

        # ── Accent line at very top
        tk.Frame(bar, bg=C['accent'], height=2).place(x=0, y=0, relwidth=1)

        # ── Left: Logo
        logo = tk.Frame(bar, bg=C['panel'])
        logo.pack(side='left', padx=(18, 0))
        tk.Label(logo, text='TRADE', font=('Segoe UI', 17, 'bold'),
                 bg=C['panel'], fg=C['accent']).pack(side='left')
        tk.Label(logo, text='DESK', font=('Segoe UI', 17, 'bold'),
                 bg=C['panel'], fg=C['text']).pack(side='left')
        tk.Label(logo, text='  ·  Stock Market Simulator',
                 font=('Segoe UI', 9),
                 bg=C['panel'], fg=C['muted']).pack(side='left', pady=6)

        # ── Right: Stats
        right = tk.Frame(bar, bg=C['panel'])
        right.pack(side='right', padx=18)

        # Clock
        self.clock_lbl = tk.Label(right, text='', font=('Consolas', 10),
                                   bg=C['panel'], fg=C['muted'])
        self.clock_lbl.pack(side='right', padx=(10, 0))

        self._top_divider(right)

        # Day counter
        self.day_lbl = tk.Label(right,
            text=f'DAY {market.current_day}',
            font=('Consolas', 11, 'bold'),
            bg=C['panel'], fg=C['gold'])
        self.day_lbl.pack(side='right', padx=(0, 4))

        self._top_divider(right)

        # P&L
        pl = portfolio.get_total_value() - 10000
        self.pl_lbl = tk.Label(right,
            text=('+' if pl >= 0 else '') + f'${pl:,.2f}',
            font=('Consolas', 11, 'bold'),
            bg=C['panel'], fg=C['green'] if pl >= 0 else C['red'])
        self.pl_lbl.pack(side='right', padx=(0, 2))
        tk.Label(right, text='P&L', font=('Segoe UI', 8),
                 bg=C['panel'], fg=C['muted']).pack(side='right', padx=(0, 4))

        self._top_divider(right)

        # Portfolio value
        self.portfolio_val_lbl = tk.Label(right,
            text=f'${portfolio.get_total_value():,.2f}',
            font=('Consolas', 14, 'bold'),
            bg=C['panel'], fg=C['green'])
        self.portfolio_val_lbl.pack(side='right', padx=(0, 4))
        tk.Label(right, text='PORTFOLIO', font=('Segoe UI', 8),
                 bg=C['panel'], fg=C['muted']).pack(side='right')

        self._top_divider(right)

        # Live toggle
        self.live_dot = tk.Label(right, text='●',
                                  font=('Segoe UI', 10),
                                  bg=C['panel'], fg=C['muted'],
                                  cursor='hand2')
        self.live_dot.pack(side='right', padx=(0, 2))
        self.live_label = tk.Label(right, text='LIVE',
                                    font=('Segoe UI', 8, 'bold'),
                                    bg=C['panel'], fg=C['muted'],
                                    cursor='hand2')
        self.live_label.pack(side='right')
        self.live_dot.bind('<Button-1>',   self._toggle_live)
        self.live_label.bind('<Button-1>', self._toggle_live)

    def _top_divider(self, parent):
        tk.Label(parent, text='│', font=('Segoe UI', 14),
                 bg=C['panel'], fg=C['border']).pack(side='right', padx=6)

    # ══════════════════════════════════════════
    #  BODY (sidebar + main)
    # ══════════════════════════════════════════
    def _build_body(self):
        body = tk.Frame(self.root, bg=C['bg'])
        body.pack(fill='both', expand=True)
        self._build_sidebar(body)
        self.main_frame = tk.Frame(body, bg=C['bg'])
        self.main_frame.pack(side='left', fill='both', expand=True,
                              padx=(0, 10), pady=(10, 0))

    # ══════════════════════════════════════════
    #  SIDEBAR
    # ══════════════════════════════════════════
    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=C['panel'], width=220)
        sb.pack(side='left', fill='y', padx=(10, 0), pady=(10, 0))
        sb.pack_propagate(False)

        # Nav label
        self._sb_section(sb, 'NAVIGATION')

        nav_items = [
            ('market',    '◈', 'Market'),
            ('portfolio', '◉', 'Portfolio'),
            ('history',   '≡', 'History'),
            ('bot',       '⚡', 'Auto Bot'),
            ('charts',    '▲', 'Charts'),
        ]
        self.nav_btns = {}
        for key, icon, label in nav_items:
            btn = tk.Button(sb,
                text=f'  {icon}  {label}',
                font=('Segoe UI', 11),
                bg=C['panel'], fg=C['muted'],
                relief='flat', anchor='w',
                padx=10, pady=9,
                cursor='hand2',
                command=lambda k=key: self._switch_tab(k))
            btn.pack(fill='x', padx=8, pady=1)
            self._hover(btn, C['panel'], C['card'])
            self.nav_btns[key] = btn

        self._sb_divider(sb)
        self._sb_section(sb, 'ACCOUNT SUMMARY')

        self.sb_balance = self._sb_kv(sb, 'Cash Balance',
                                       f'${portfolio.balance:,.2f}')
        self.sb_value   = self._sb_kv(sb, 'Total Value',
                                       f'${portfolio.get_total_value():,.2f}')
        pl = portfolio.get_total_value() - 10000
        self.sb_pl = self._sb_kv(sb, 'Total P&L',
                                  ('+' if pl >= 0 else '') + f'${abs(pl):,.2f}',
                                  C['green'] if pl >= 0 else C['red'])

        self._sb_divider(sb)

        # ── Action buttons
        self._sb_btn(sb, '⏭   NEXT DAY',
                     C['accent'], '#0D1117',
                     self._advance_day, bold=True)
        self._sb_btn(sb, '+  Add Balance',
                     C['card'], C['text'],
                     self._add_balance_dialog)
        self._sb_btn(sb, '  Save Portfolio',
                     C['card'], C['muted'],
                     self._save)

        # Author tag
        tk.Label(sb, text='Parth  ·  DMCE AI-DS  ·  2025',
                 font=('Segoe UI', 8),
                 bg=C['panel'], fg=C['border']).pack(side='bottom', pady=12)

    def _sb_section(self, parent, text):
        tk.Label(parent, text=text, font=('Segoe UI', 7, 'bold'),
                 bg=C['panel'], fg=C['muted']).pack(
                     anchor='w', padx=16, pady=(14, 4))

    def _sb_divider(self, parent):
        tk.Frame(parent, bg=C['border'], height=1).pack(
            fill='x', padx=16, pady=8)

    def _sb_kv(self, parent, label, value, color=None):
        card = tk.Frame(parent, bg=C['card'])
        card.pack(fill='x', padx=14, pady=2)
        tk.Label(card, text=label, font=('Segoe UI', 8),
                 bg=C['card'], fg=C['muted']).pack(
                     anchor='w', padx=10, pady=(7, 0))
        lbl = tk.Label(card, text=value,
                        font=('Consolas', 12, 'bold'),
                        bg=C['card'], fg=color or C['text'])
        lbl.pack(anchor='w', padx=10, pady=(0, 7))
        return lbl

    def _sb_btn(self, parent, text, bg, fg, cmd, bold=False):
        btn = tk.Button(parent, text=text,
                        font=('Segoe UI', 10, 'bold' if bold else 'normal'),
                        bg=bg, fg=fg,
                        relief='flat', cursor='hand2',
                        pady=9, command=cmd)
        btn.pack(fill='x', padx=14, pady=(0, 4))
        # Lighten on hover
        import colorsys
        try:
            hover_bg = self._lighten(bg, 0.08) if bg != C['card'] else C['border']
        except Exception:
            hover_bg = bg
        self._hover(btn, bg, hover_bg)
        return btn

    # ══════════════════════════════════════════
    #  STATUS BAR
    # ══════════════════════════════════════════
    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=C['panel'], height=30)
        bar.pack(fill='x', side='bottom')
        bar.pack_propagate(False)

        tk.Frame(bar, bg=C['border'], height=1).place(
            x=0, y=0, relwidth=1)

        self.status_lbl = tk.Label(bar,
            textvariable=self.status_msg,
            font=('Segoe UI', 9),
            bg=C['panel'], fg=C['muted'])
        self.status_lbl.pack(side='left', padx=16)

        self.news_lbl = tk.Label(bar, text='',
                                  font=('Segoe UI', 9, 'italic'),
                                  bg=C['panel'], fg=C['gold'])
        self.news_lbl.pack(side='right', padx=16)

        tk.Label(bar, text='v2.0 GUI Edition  ·  Python + Tkinter',
                 font=('Segoe UI', 8),
                 bg=C['panel'], fg=C['border']).pack(side='right', padx=16)

    # ══════════════════════════════════════════
    #  TAB SWITCHING
    # ══════════════════════════════════════════
    def _switch_tab(self, key):
        self.current_tab = key

        for k, btn in self.nav_btns.items():
            if k == key:
                btn.config(bg=C['card'], fg=C['accent'],
                           font=('Segoe UI', 11, 'bold'))
            else:
                btn.config(bg=C['panel'], fg=C['muted'],
                           font=('Segoe UI', 11))

        for w in self.main_frame.winfo_children():
            w.destroy()

        {
            'market':    self._show_market,
            'portfolio': self._show_portfolio,
            'history':   self._show_history,
            'bot':       self._show_bot,
            'charts':    self._show_charts,
        }[key]()

    # ══════════════════════════════════════════
    #  TAB: MARKET
    # ══════════════════════════════════════════
    def _show_market(self):
        # ── Header row
        hdr = tk.Frame(self.main_frame, bg=C['bg'])
        hdr.pack(fill='x', pady=(2, 6))
        tk.Label(hdr, text='Live Market',
                 font=('Segoe UI', 15, 'bold'),
                 bg=C['bg'], fg=C['text']).pack(side='left')
        tk.Label(hdr, text='  ·  auto-refreshing every 2s',
                 font=('Segoe UI', 9),
                 bg=C['bg'], fg=C['muted']).pack(side='left', pady=4)

        # ── Stock cards row
        self.cards_frame = tk.Frame(self.main_frame, bg=C['bg'])
        self.cards_frame.pack(fill='x', pady=(0, 8))
        self._build_stock_cards()

        # ── Middle: chart (left) + trade panel (right)
        mid = tk.Frame(self.main_frame, bg=C['bg'])
        mid.pack(fill='both', expand=True)

        # Chart panel
        chart_panel = tk.Frame(mid, bg=C['panel'])
        chart_panel.pack(side='left', fill='both', expand=True, padx=(0, 8))

        chart_hdr = tk.Frame(chart_panel, bg=C['panel'])
        chart_hdr.pack(fill='x', padx=12, pady=(10, 0))

        tk.Label(chart_hdr, text='Price Chart',
                 font=('Segoe UI', 11, 'bold'),
                 bg=C['panel'], fg=C['text']).pack(side='left')

        sel = tk.Frame(chart_hdr, bg=C['panel'])
        sel.pack(side='right')
        for sym in market.STOCKS:
            col = STOCK_COLORS.get(sym, C['accent'])
            b = tk.Button(sel, text=sym,
                          font=('Consolas', 9, 'bold'),
                          bg=C['card'], fg=col,
                          relief='flat', padx=10, pady=4,
                          cursor='hand2',
                          command=lambda s=sym: self._select_stock_chart(s))
            b.pack(side='left', padx=2)
            self._hover(b, C['card'], C['border'])

        self.market_chart_frame = tk.Frame(chart_panel, bg=C['panel'])
        self.market_chart_frame.pack(fill='both', expand=True, padx=8, pady=8)
        self._draw_mini_chart(self.market_chart_frame, self.selected_stock.get())

        # Trade panel (right side)
        trade_panel = tk.Frame(mid, bg=C['panel'], width=270)
        trade_panel.pack(side='right', fill='y')
        trade_panel.pack_propagate(False)
        self._build_trade_panel(trade_panel)

    def _build_stock_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        self.price_labels  = {}
        self.change_labels = {}

        for i, (sym, data) in enumerate(market.STOCKS.items()):
            price = data['price']
            hist  = data['history']
            col   = STOCK_COLORS.get(sym, C['accent'])

            card = tk.Frame(self.cards_frame, bg=C['card'], cursor='hand2')
            card.pack(side='left', fill='x', expand=True, padx=3)
            card.bind('<Button-1>', lambda e, s=sym: self._select_stock_chart(s))

            tk.Frame(card, bg=col, height=3).pack(fill='x')

            inner = tk.Frame(card, bg=C['card'])
            inner.pack(padx=12, pady=8)
            inner.bind('<Button-1>', lambda e, s=sym: self._select_stock_chart(s))

            tk.Label(inner, text=sym, font=('Segoe UI', 10, 'bold'),
                     bg=C['card'], fg=col).pack(anchor='w')

            price_lbl = tk.Label(inner,
                text=f'${price:,.2f}',
                font=('Consolas', 14, 'bold'),
                bg=C['card'], fg=C['text'])
            price_lbl.pack(anchor='w')
            price_lbl.bind('<Button-1>', lambda e, s=sym: self._select_stock_chart(s))
            self.price_labels[sym] = price_lbl

            if len(hist) > 1:
                chg = ((price - hist[-2]) / hist[-2]) * 100
                chg_col  = C['green'] if chg >= 0 else C['red']
                chg_text = ('▲' if chg >= 0 else '▼') + f' {chg:+.2f}%'
            else:
                chg_col, chg_text = C['muted'], '— —'

            chg_lbl = tk.Label(inner, text=chg_text,
                                font=('Segoe UI', 9, 'bold'),
                                bg=C['card'], fg=chg_col)
            chg_lbl.pack(anchor='w')
            self.change_labels[sym] = chg_lbl

    def _select_stock_chart(self, sym):
        self.selected_stock.set(sym)
        # Redraw chart only
        for w in self.market_chart_frame.winfo_children():
            w.destroy()
        self._draw_mini_chart(self.market_chart_frame, sym)
        # Update trade panel stock info if visible
        if hasattr(self, 'trade_sym_lbl'):
            self.trade_sym_lbl.config(text=sym,
                fg=STOCK_COLORS.get(sym, C['accent']))
            price = market.get_price(sym)
            self.trade_price_lbl.config(text=f'${price:,.2f}')
            self._update_cost_display()

    def _build_trade_panel(self, parent):
        tk.Label(parent, text='Quick Trade',
                 font=('Segoe UI', 12, 'bold'),
                 bg=C['panel'], fg=C['text']).pack(
                     anchor='w', padx=14, pady=(14, 6))

        sym = self.selected_stock.get()
        col = STOCK_COLORS.get(sym, C['accent'])

        self.trade_sym_lbl = tk.Label(parent, text=sym,
            font=('Consolas', 24, 'bold'),
            bg=C['panel'], fg=col)
        self.trade_sym_lbl.pack(anchor='w', padx=14)

        price = market.get_price(sym)
        self.trade_price_lbl = tk.Label(parent, text=f'${price:,.2f}',
            font=('Consolas', 14),
            bg=C['panel'], fg=C['text'])
        self.trade_price_lbl.pack(anchor='w', padx=14, pady=(0, 14))

        # Quantity row
        tk.Label(parent, text='QUANTITY',
                 font=('Segoe UI', 8, 'bold'),
                 bg=C['panel'], fg=C['muted']).pack(anchor='w', padx=14)

        qty_row = tk.Frame(parent, bg=C['panel'])
        qty_row.pack(fill='x', padx=14, pady=(4, 10))

        qty_entry = tk.Entry(qty_row, textvariable=self.qty_var,
                             font=('Consolas', 15, 'bold'),
                             bg=C['card'], fg=C['text'],
                             insertbackground=C['text'],
                             relief='flat', width=7,
                             justify='center')
        qty_entry.pack(side='left', ipady=9, padx=(0, 6))
        qty_entry.bind('<KeyRelease>', lambda e: self._update_cost_display())

        btn_col = tk.Frame(qty_row, bg=C['panel'])
        btn_col.pack(side='left')
        for sign, delta in [('+', 1), ('−', -1)]:
            tk.Button(btn_col, text=sign,
                      font=('Segoe UI', 9, 'bold'),
                      bg=C['card'], fg=C['text'],
                      relief='flat', width=3, pady=4,
                      command=lambda d=delta: self._adjust_qty(d)
                      ).pack(pady=1)

        # Cost preview
        self.cost_lbl = tk.Label(parent, text='',
                                  font=('Segoe UI', 8),
                                  bg=C['panel'], fg=C['muted'])
        self.cost_lbl.pack(anchor='w', padx=14, pady=(0, 10))
        self._update_cost_display()

        # BUY / SELL
        for text, bg, cmd in [
            ('  BUY',  C['green'], self._do_buy),
            ('  SELL', C['red'],   self._do_sell),
        ]:
            btn = tk.Button(parent, text=text,
                            font=('Segoe UI', 12, 'bold'),
                            bg=bg, fg='#0D1117' if bg == C['green'] else '#FFFFFF',
                            relief='flat', cursor='hand2', pady=11,
                            command=cmd)
            btn.pack(fill='x', padx=14, pady=(0, 6))
            lighter = self._lighten(bg, 0.1)
            self._hover(btn, bg, lighter)

        tk.Frame(parent, bg=C['border'], height=1).pack(
            fill='x', padx=14, pady=8)

        # Current position
        tk.Label(parent, text='YOUR POSITION',
                 font=('Segoe UI', 8, 'bold'),
                 bg=C['panel'], fg=C['muted']).pack(anchor='w', padx=14, pady=(0, 6))

        if sym in portfolio.holdings:
            h   = portfolio.holdings[sym]
            now = market.get_price(sym)
            pl  = (now - h['avg_buy']) * h['shares']
            pl_col = C['green'] if pl >= 0 else C['red']
            pl_txt = ('+' if pl >= 0 else '') + f'${pl:.2f}'

            for lbl, val, vc in [
                ('Shares owned',   str(h['shares']),          None),
                ('Avg buy price',  f"${h['avg_buy']:.2f}",    None),
                ('Unrealised P&L', pl_txt,                    pl_col),
                ('Position value', f"${now*h['shares']:.2f}", None),
            ]:
                self._trade_row(parent, lbl, val, vc)
        else:
            tk.Label(parent, text='No position in this stock',
                     font=('Segoe UI', 9),
                     bg=C['panel'], fg=C['muted']).pack(anchor='w', padx=14)

    def _trade_row(self, parent, label, value, vc=None):
        row = tk.Frame(parent, bg=C['panel'])
        row.pack(fill='x', padx=14, pady=1)
        tk.Label(row, text=label, font=('Segoe UI', 9),
                 bg=C['panel'], fg=C['muted']).pack(side='left')
        tk.Label(row, text=value, font=('Consolas', 9, 'bold'),
                 bg=C['panel'], fg=vc or C['text']).pack(side='right')

    def _adjust_qty(self, delta):
        try:
            v = int(self.qty_var.get()) + delta
            self.qty_var.set(str(max(1, v)))
        except Exception:
            self.qty_var.set('1')
        self._update_cost_display()

    def _update_cost_display(self):
        try:
            qty   = int(self.qty_var.get())
            price = market.get_price(self.selected_stock.get())
            total = qty * price
            bal   = portfolio.balance
            color = C['muted'] if total <= bal else C['red']
            self.cost_lbl.config(
                text=f'Cost: ${total:,.2f}   Balance: ${bal:,.2f}',
                fg=color)
        except Exception:
            pass

    def _draw_mini_chart(self, parent, symbol):
        for w in parent.winfo_children():
            w.destroy()

        prices = market.get_history(symbol)
        days   = list(range(1, len(prices) + 1))
        color  = STOCK_COLORS.get(symbol, C['accent'])

        fig = Figure(figsize=(5, 2.8), dpi=100, facecolor=C['panel'])
        ax  = fig.add_subplot(111)
        ax.set_facecolor(C['panel'])

        ax.plot(days, prices, color=color, linewidth=2.2, zorder=3)
        ax.fill_between(days, prices, min(prices) * 0.997,
                        alpha=0.15, color=color)

        if len(prices) >= 5:
            ma5 = [sum(prices[max(0, i-4):i+1]) / min(i+1, 5)
                   for i in range(len(prices))]
            ax.plot(days, ma5, color=C['muted'],
                    linewidth=1.2, linestyle='--', alpha=0.6, label='MA5')

        ax.set_title(f'{symbol}  —  Price History',
                     color=C['text'], fontsize=10, pad=6)
        ax.tick_params(colors=C['muted'], labelsize=8)
        ax.spines[:].set_color(C['border'])
        ax.set_xlabel('Day', color=C['muted'], fontsize=8)
        ax.set_ylabel('Price ($)', color=C['muted'], fontsize=8)
        ax.grid(True, alpha=0.12, color=C['border'])
        if len(prices) >= 5:
            ax.legend(facecolor=C['card'], labelcolor=C['text'],
                      framealpha=0.8, fontsize=8)
        fig.tight_layout(pad=1.5)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    # ══════════════════════════════════════════
    #  TAB: PORTFOLIO
    # ══════════════════════════════════════════
    def _show_portfolio(self):
        total = portfolio.get_total_value()
        pl    = total - 10000.0

        # ── Stat cards
        cards_row = tk.Frame(self.main_frame, bg=C['bg'])
        cards_row.pack(fill='x', pady=(4, 8))

        stats = [
            ('Total Value',   f'${total:,.2f}',                          C['accent']),
            ('Cash Balance',  f'${portfolio.balance:,.2f}',              C['text']),
            ('Total P&L',     ('+' if pl >= 0 else '') + f'${pl:,.2f}',
                              C['green'] if pl >= 0 else C['red']),
            ('Open Positions', f'{len(portfolio.holdings)} stocks',      C['gold']),
        ]
        for label, value, color in stats:
            card = tk.Frame(cards_row, bg=C['panel'])
            card.pack(side='left', fill='x', expand=True, padx=4)
            tk.Frame(card, bg=color, height=3).pack(fill='x')
            tk.Label(card, text=label, font=('Segoe UI', 8, 'bold'),
                     bg=C['panel'], fg=C['muted']).pack(
                         anchor='w', padx=14, pady=(8, 0))
            tk.Label(card, text=value,
                     font=('Consolas', 16, 'bold'),
                     bg=C['panel'], fg=color).pack(
                         anchor='w', padx=14, pady=(0, 10))

        # ── Holdings table
        tbl_panel = tk.Frame(self.main_frame, bg=C['panel'])
        tbl_panel.pack(fill='both', expand=True)

        tk.Label(tbl_panel, text='Holdings',
                 font=('Segoe UI', 11, 'bold'),
                 bg=C['panel'], fg=C['text']).pack(
                     anchor='w', padx=14, pady=(10, 4))

        cols = ('Symbol', 'Shares', 'Avg Buy', 'Current', 'P&L', 'Value', 'Weight %')
        tree = ttk.Treeview(tbl_panel, columns=cols, show='headings',
                            style='Dark.Treeview', height=7)

        widths = [80, 70, 100, 100, 110, 110, 90]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center')

        tree.tag_configure('pos', foreground=C['green'])
        tree.tag_configure('neg', foreground=C['red'])
        tree.tag_configure('empty', foreground=C['muted'])

        stock_total = sum(
            market.get_price(s) * d['shares']
            for s, d in portfolio.holdings.items()
        ) if portfolio.holdings else 0

        if portfolio.holdings:
            for sym, data in portfolio.holdings.items():
                now     = market.get_price(sym)
                pl_v    = (now - data['avg_buy']) * data['shares']
                val     = now * data['shares']
                weight  = (val / total * 100) if total > 0 else 0
                pl_txt  = ('+' if pl_v >= 0 else '') + f'${pl_v:.2f}'
                tree.insert('', 'end', values=(
                    sym,
                    data['shares'],
                    f"${data['avg_buy']:.2f}",
                    f'${now:.2f}',
                    pl_txt,
                    f'${val:.2f}',
                    f'{weight:.1f}%',
                ), tags=('pos' if pl_v >= 0 else 'neg',))
        else:
            tree.insert('', 'end', values=(
                '—', '—', '—', '—', 'No holdings yet', '—', '—'
            ), tags=('empty',))

        sb = ttk.Scrollbar(tbl_panel, orient='vertical', command=tree.yview,
                           style='Dark.Vertical.TScrollbar')
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side='left', fill='both', expand=True, padx=(14, 0), pady=(0, 14))
        sb.pack(side='right', fill='y', pady=(0, 14), padx=(0, 8))

        # ── Portfolio value chart
        chart_f = tk.Frame(self.main_frame, bg=C['panel'])
        chart_f.pack(fill='both', expand=True, pady=(0, 0))
        self._draw_portfolio_chart(chart_f)

    def _draw_portfolio_chart(self, parent):
        vals = portfolio.value_history
        if len(vals) < 2:
            tk.Label(parent,
                     text='Advance at least 1 day to see the portfolio chart',
                     font=('Segoe UI', 10),
                     bg=C['panel'], fg=C['muted']).pack(pady=20)
            return

        days  = list(range(1, len(vals) + 1))
        start = vals[0]
        color = C['green'] if vals[-1] >= start else C['red']

        fig = Figure(figsize=(8, 2.3), dpi=96, facecolor=C['panel'])
        ax  = fig.add_subplot(111)
        ax.set_facecolor(C['panel'])

        ax.plot(days, vals, color=color, linewidth=2)
        ax.fill_between(days, vals, start, alpha=0.12, color=color)
        ax.axhline(y=start, color=C['muted'], linestyle='--',
                   alpha=0.4, label=f'Start  ${start:,.0f}')

        ax.set_title('Portfolio Value Over Time',
                     color=C['text'], fontsize=10, pad=6)
        ax.tick_params(colors=C['muted'], labelsize=8)
        ax.spines[:].set_color(C['border'])
        ax.grid(True, alpha=0.1, color=C['border'])
        ax.legend(facecolor=C['card'], labelcolor=C['text'],
                  framealpha=0.8, fontsize=8)
        fig.tight_layout(pad=1)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=14, pady=(0, 12))

    # ══════════════════════════════════════════
    #  TAB: HISTORY
    # ══════════════════════════════════════════
    def _show_history(self):
        # Header
        hdr = tk.Frame(self.main_frame, bg=C['bg'])
        hdr.pack(fill='x', pady=(4, 8))
        tk.Label(hdr, text='Trade History',
                 font=('Segoe UI', 15, 'bold'),
                 bg=C['bg'], fg=C['text']).pack(side='left')
        total_trades = len(history.trade_log)
        buys  = sum(1 for t in history.trade_log if t['action'] == 'BUY')
        sells = total_trades - buys
        tk.Label(hdr,
                 text=f'  ·  {total_trades} trades  ({buys} buys / {sells} sells)',
                 font=('Segoe UI', 9),
                 bg=C['bg'], fg=C['muted']).pack(side='left', pady=4)

        # Table
        panel = tk.Frame(self.main_frame, bg=C['panel'])
        panel.pack(fill='both', expand=True)

        cols = ('Time', 'Day', 'Action', 'Symbol', 'Qty', 'Price', 'Total')
        tree = ttk.Treeview(panel, columns=cols, show='headings',
                            style='Dark.Treeview')

        widths = [90, 55, 80, 85, 60, 110, 120]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center')

        tree.tag_configure('BUY',   foreground=C['green'])
        tree.tag_configure('SELL',  foreground=C['red'])
        tree.tag_configure('empty', foreground=C['muted'])

        for t in reversed(history.trade_log):
            tree.insert('', 'end', values=(
                t['time'], f"D{t['day']}", t['action'],
                t['symbol'], t['quantity'],
                f"${t['price']:.2f}", f"${t['total']:.2f}",
            ), tags=(t['action'],))

        if not history.trade_log:
            tree.insert('', 'end', values=(
                '—', '—', 'No trades yet', '—', '—', '—', '—',
            ), tags=('empty',))

        sb = ttk.Scrollbar(panel, orient='vertical', command=tree.yview,
                           style='Dark.Vertical.TScrollbar')
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side='left', fill='both', expand=True, padx=(14, 0), pady=14)
        sb.pack(side='right', fill='y', pady=14, padx=(0, 8))

    # ══════════════════════════════════════════
    #  TAB: BOT
    # ══════════════════════════════════════════
    def _show_bot(self):
        # Header
        tk.Label(self.main_frame, text='Auto Trading Bot',
                 font=('Segoe UI', 15, 'bold'),
                 bg=C['bg'], fg=C['text']).pack(anchor='w', pady=(4, 0))
        tk.Label(self.main_frame,
                 text='Moving Average Crossover  ·  MA5 vs MA20  ·  Needs 20+ days',
                 font=('Segoe UI', 9),
                 bg=C['bg'], fg=C['muted']).pack(anchor='w', pady=(0, 8))

        # Strategy card
        info = tk.Frame(self.main_frame, bg=C['panel'])
        info.pack(fill='x', pady=(0, 10))
        tk.Frame(info, bg=C['gold'], height=3).pack(fill='x')
        tk.Label(info,
                 text='  BUY when MA5 > MA20  (short-term uptrend)'
                      '        SELL when MA5 < MA20  (short-term downtrend)',
                 font=('Segoe UI', 10),
                 bg=C['panel'], fg=C['gold']).pack(padx=14, pady=10, anchor='w')

        # Run button
        run_btn = tk.Button(self.main_frame,
            text='  ⚡  RUN BOT NOW',
            font=('Segoe UI', 12, 'bold'),
            bg=C['purple'], fg='#FFFFFF',
            relief='flat', cursor='hand2', pady=12,
            command=self._run_bot_gui)
        run_btn.pack(fill='x', pady=(0, 10))
        self._hover(run_btn, C['purple'], self._lighten(C['purple'], 0.1))

        # Log area
        log_panel = tk.Frame(self.main_frame, bg=C['panel'])
        log_panel.pack(fill='both', expand=True)

        tk.Label(log_panel, text='Bot Log',
                 font=('Segoe UI', 10, 'bold'),
                 bg=C['panel'], fg=C['muted']).pack(
                     anchor='w', padx=14, pady=(10, 4))

        self.bot_text = tk.Text(log_panel,
            bg=C['card'], fg=C['text'],
            font=('Consolas', 10),
            relief='flat',
            insertbackground=C['text'],
            state='disabled',
            padx=14, pady=12)
        self.bot_text.pack(fill='both', expand=True, padx=14, pady=(0, 14))

        self.bot_text.tag_configure('buy',    foreground=C['green'])
        self.bot_text.tag_configure('sell',   foreground=C['red'])
        self.bot_text.tag_configure('header', foreground=C['accent'],
                                    font=('Consolas', 11, 'bold'))
        self.bot_text.tag_configure('gold',   foreground=C['gold'])
        self.bot_text.tag_configure('muted',  foreground=C['muted'])
        self.bot_text.tag_configure('purple', foreground=C['purple'])

        self._bot_append(
            f'  Ready.  Day {market.current_day} of data available.\n'
            f'  Need {max(0, 20 - market.current_day)} more day(s) for MA signals.\n',
            'muted')

    def _run_bot_gui(self):
        self.bot_text.config(state='normal')
        self.bot_text.delete('1.0', 'end')

        self._bot_append('═' * 52 + '\n', 'muted')
        self._bot_append('  TRADING BOT  —  MOVING AVERAGE CROSSOVER\n', 'header')
        self._bot_append(f'  Day {market.current_day}  ·  '
                         f'Balance: ${portfolio.balance:,.2f}\n', 'muted')
        self._bot_append('═' * 52 + '\n\n', 'muted')

        any_action = False

        for symbol in market.STOCKS:
            prices   = market.get_history(symbol)
            price    = market.get_price(symbol)
            ma_short = bot.moving_average(prices, 5)
            ma_long  = bot.moving_average(prices, 20)

            self._bot_append(f'  {symbol}   ${price:.2f}\n', 'gold')

            if ma_short is None or ma_long is None:
                need = 20 - len(prices)
                self._bot_append(
                    f'    ⏳  Need {need} more days of data\n\n', 'muted')
                continue

            self._bot_append(
                f'    MA5  =  ${ma_short:.2f}   '
                f'MA20 =  ${ma_long:.2f}\n', 'muted')

            if ma_short > ma_long:
                self._bot_append(
                    '    ▲  BUY signal — short-term uptrend\n', 'buy')
                if portfolio.balance >= price * 2:
                    old_bal = portfolio.balance
                    trading.buy_stock(symbol, 2)
                    if portfolio.balance < old_bal:
                        self._bot_append(
                            f'    ✔  Bought 2 shares @ ${price:.2f}\n', 'buy')
                        any_action = True
                else:
                    self._bot_append('    ✘  Insufficient balance\n', 'muted')

            elif ma_short < ma_long:
                self._bot_append(
                    '    ▼  SELL signal — short-term downtrend\n', 'sell')
                owned = portfolio.holdings.get(symbol, {}).get('shares', 0)
                to_sell = min(owned, 2)
                if to_sell > 0:
                    old_bal = portfolio.balance
                    trading.sell_stock(symbol, to_sell)
                    if portfolio.balance > old_bal:
                        self._bot_append(
                            f'    ✔  Sold {to_sell} shares @ ${price:.2f}\n', 'sell')
                        any_action = True
                else:
                    self._bot_append('    ✘  No shares to sell\n', 'muted')
            else:
                self._bot_append('    —  HOLD\n', 'muted')

            self._bot_append('\n', '')

        self._bot_append('═' * 52 + '\n', 'muted')
        msg = '  ✔  Bot completed trades successfully.\n' \
              if any_action else \
              '  —  Bot found no trade opportunities.\n'
        self._bot_append(msg, 'buy' if any_action else 'muted')

        self.bot_text.config(state='disabled')
        self._refresh_topbar()
        self._set_status('Bot analysis complete')

    def _bot_append(self, text, tag=''):
        self.bot_text.config(state='normal')
        self.bot_text.insert('end', text, tag)
        self.bot_text.config(state='disabled')
        self.bot_text.see('end')

    # ══════════════════════════════════════════
    #  TAB: CHARTS
    # ══════════════════════════════════════════
    def _show_charts(self):
        tk.Label(self.main_frame, text='Charts',
                 font=('Segoe UI', 15, 'bold'),
                 bg=C['bg'], fg=C['text']).pack(anchor='w', pady=(4, 8))

        btn_row = tk.Frame(self.main_frame, bg=C['bg'])
        btn_row.pack(fill='x', pady=(0, 8))

        for sym in market.STOCKS:
            col = STOCK_COLORS.get(sym, C['accent'])
            b = tk.Button(btn_row, text=sym,
                          font=('Consolas', 10, 'bold'),
                          bg=C['card'], fg=col,
                          relief='flat', padx=14, pady=8,
                          cursor='hand2',
                          command=lambda s=sym: self._chart_single(s))
            b.pack(side='left', padx=3)
            self._hover(b, C['card'], C['panel'])

        for text, bg, cmd in [
            ('All Stocks',      C['accent'], self._chart_all),
            ('Portfolio Value', C['gold'],   self._chart_portfolio),
        ]:
            b = tk.Button(btn_row, text=text,
                          font=('Segoe UI', 10, 'bold'),
                          bg=bg, fg='#0D1117',
                          relief='flat', padx=14, pady=8,
                          cursor='hand2', command=cmd)
            b.pack(side='left', padx=3)

        self.chart_area = tk.Frame(self.main_frame, bg=C['panel'])
        self.chart_area.pack(fill='both', expand=True)

        # Default
        self._chart_single('AAPL')

    def _chart_single(self, symbol):
        for w in self.chart_area.winfo_children():
            w.destroy()

        prices = market.get_history(symbol)
        days   = list(range(1, len(prices) + 1))
        color  = STOCK_COLORS.get(symbol, C['accent'])

        fig = Figure(figsize=(9, 4.6), dpi=96, facecolor=C['panel'])
        ax  = fig.add_subplot(111)
        ax.set_facecolor(C['panel'])

        ax.plot(days, prices, color=color, linewidth=2.5, zorder=3)
        ax.fill_between(days, prices, min(prices) * 0.997,
                        alpha=0.15, color=color)

        if len(prices) >= 20:
            ma20 = [sum(prices[max(0, i-19):i+1]) / min(i+1, 20)
                    for i in range(len(prices))]
            ax.plot(days, ma20, color=C['gold'],
                    linewidth=1.8, linestyle='--', alpha=0.8, label='MA20')
        if len(prices) >= 5:
            ma5 = [sum(prices[max(0, i-4):i+1]) / min(i+1, 5)
                   for i in range(len(prices))]
            ax.plot(days, ma5, color=C['muted'],
                    linewidth=1.3, linestyle='--', alpha=0.7, label='MA5')

        current = prices[-1]
        ax.axhline(y=current, color=color, linewidth=0.6,
                   linestyle=':', alpha=0.5)

        ax.set_title(f'{symbol}  —  Price Chart with Moving Averages',
                     color=C['text'], fontsize=12, pad=10, fontweight='bold')
        ax.tick_params(colors=C['muted'], labelsize=9)
        ax.spines[:].set_color(C['border'])
        ax.set_xlabel('Day', color=C['muted'])
        ax.set_ylabel('Price ($)', color=C['muted'])
        ax.grid(True, alpha=0.1, color=C['border'])
        if len(prices) >= 5:
            ax.legend(facecolor=C['card'], labelcolor=C['text'],
                      framealpha=0.9, fontsize=9,
                      edgecolor=C['border'])
        fig.tight_layout(pad=1.5)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=14, pady=14)

    def _chart_all(self):
        for w in self.chart_area.winfo_children():
            w.destroy()

        symbols = list(market.STOCKS.keys())
        fig = Figure(figsize=(9, 4.6), dpi=96, facecolor=C['panel'])
        fig.suptitle('All Stocks — Price History',
                     color=C['text'], fontsize=11, fontweight='bold')

        for i, sym in enumerate(symbols):
            ax  = fig.add_subplot(2, 3, i + 1)
            col = STOCK_COLORS.get(sym, C['accent'])
            ax.set_facecolor(C['panel'])
            prices = market.get_history(sym)
            days   = list(range(1, len(prices) + 1))
            ax.plot(days, prices, color=col, linewidth=1.8)
            ax.fill_between(days, prices, min(prices) * 0.997,
                            alpha=0.12, color=col)
            ax.set_title(sym, color=col, fontsize=9, fontweight='bold')
            ax.tick_params(colors=C['muted'], labelsize=7)
            ax.spines[:].set_color(C['border'])
            ax.grid(True, alpha=0.08, color=C['border'])

        fig.tight_layout(pad=1)
        canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=14, pady=14)

    def _chart_portfolio(self):
        for w in self.chart_area.winfo_children():
            w.destroy()
        self._draw_portfolio_chart(self.chart_area)

    # ══════════════════════════════════════════
    #  ACTIONS
    # ══════════════════════════════════════════
    def _do_buy(self):
        sym = self.selected_stock.get()
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError
        except (ValueError, Exception):
            self._set_status('Invalid quantity')
            return

        old_bal = portfolio.balance
        trading.buy_stock(sym, qty)

        if portfolio.balance < old_bal:
            price = market.get_price(sym)
            msg   = f'Bought {qty}x {sym} @ ${price:.2f}'
            self._set_status(msg)
            self.news_lbl.config(text=f'BUY  {qty} {sym}', fg=C['green'])
        else:
            self._set_status('Buy failed — insufficient funds or invalid symbol')

        self._refresh_topbar()
        self._switch_tab('market')

    def _do_sell(self):
        sym = self.selected_stock.get()
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError
        except (ValueError, Exception):
            self._set_status('Invalid quantity')
            return

        if sym not in portfolio.holdings:
            self._set_status(f'No position in {sym}')
            return

        old_bal = portfolio.balance
        trading.sell_stock(sym, qty)

        if portfolio.balance > old_bal:
            price = market.get_price(sym)
            self._set_status(f'Sold {qty}x {sym} @ ${price:.2f}')
            self.news_lbl.config(text=f'SELL  {qty} {sym}', fg=C['red'])
        else:
            self._set_status('Sell failed — check quantity')

        self._refresh_topbar()
        self._switch_tab('market')

    def _advance_day(self):
        news = market.next_day()
        portfolio.snapshot_value()
        self._refresh_topbar()

        if news:
            short = news[0][:80]
            self.news_lbl.config(text=short, fg=C['gold'])
            self._set_status(
                f'Day {market.current_day} — {len(news)} news event(s)')
        else:
            self.news_lbl.config(text='No major news today', fg=C['muted'])
            self._set_status(f'Day {market.current_day} — Market updated')

        self._switch_tab(self.current_tab)

    def _add_balance_dialog(self):
        amount = simpledialog.askfloat(
            'Add Balance',
            'Enter amount to deposit ($):',
            parent=self.root,
            minvalue=1.0,
        )
        if amount:
            portfolio.add_balance(amount)
            self._refresh_topbar()
            self._set_status(f'Deposited ${amount:,.2f}')
            self._switch_tab(self.current_tab)

    def _save(self):
        portfolio.save_portfolio()
        self._set_status('Portfolio and trade history saved')

    def _toggle_live(self, event=None):
        self.live_mode.set(not self.live_mode.get())
        if self.live_mode.get():
            self.live_dot.config(fg=C['teal'])
            self.live_label.config(fg=C['teal'])
            self._set_status('Live mode ON — market advances every 5 seconds')
        else:
            self.live_dot.config(fg=C['muted'])
            self.live_label.config(fg=C['muted'])
            self._set_status('Live mode OFF')

    def _on_close(self):
        if messagebox.askyesno('Exit', 'Save portfolio before exiting?'):
            portfolio.save_portfolio()
        self.root.destroy()

    # ══════════════════════════════════════════
    #  AUTO REFRESH LOOP  (every 2 seconds)
    # ══════════════════════════════════════════
    def _auto_refresh(self):
        self._refresh_topbar()

        # Update price cards if market tab is active
        if self.current_tab == 'market' and self.price_labels:
            for sym in market.STOCKS:
                price = market.get_price(sym)
                prev  = self.prev_prices.get(sym, price)

                if sym in self.price_labels:
                    lbl = self.price_labels[sym]
                    lbl.config(text=f'${price:,.2f}')

                    if price > prev:
                        lbl.config(fg=C['green'])
                        self.root.after(
                            700, lambda l=lbl: l.config(fg=C['text']))
                    elif price < prev:
                        lbl.config(fg=C['red'])
                        self.root.after(
                            700, lambda l=lbl: l.config(fg=C['text']))

                if sym in self.change_labels:
                    hist = market.get_history(sym)
                    if len(hist) > 1:
                        chg  = ((price - hist[-2]) / hist[-2]) * 100
                        arr  = '▲' if chg >= 0 else '▼'
                        self.change_labels[sym].config(
                            text=f'{arr} {chg:+.2f}%',
                            fg=C['green'] if chg >= 0 else C['red'])

                self.prev_prices[sym] = price

        # Live mode: auto-advance every 5 seconds
        if self.live_mode.get():
            self._advance_day()
            self.root.after(5000, self._auto_refresh)
        else:
            self.root.after(2000, self._auto_refresh)

    def _refresh_topbar(self):
        total = portfolio.get_total_value()
        pl    = total - 10000.0
        c_pl  = C['green'] if pl >= 0 else C['red']

        self.portfolio_val_lbl.config(
            text=f'${total:,.2f}', fg=c_pl)
        self.pl_lbl.config(
            text=('+' if pl >= 0 else '') + f'${pl:,.2f}',
            fg=c_pl)
        self.day_lbl.config(text=f'DAY {market.current_day}')

        if hasattr(self, 'sb_balance'):
            self.sb_balance.config(text=f'${portfolio.balance:,.2f}')
            self.sb_value.config(text=f'${total:,.2f}')
            self.sb_pl.config(
                text=('+' if pl >= 0 else '') + f'${abs(pl):,.2f}',
                fg=c_pl)

    def _update_clock(self):
        self.clock_lbl.config(text=datetime.now().strftime('%H:%M:%S'))
        self.root.after(1000, self._update_clock)

    def _set_status(self, msg):
        self.status_msg.set(f'  {msg}')

    # ══════════════════════════════════════════
    #  UTILITIES
    # ══════════════════════════════════════════
    def _hover(self, widget, normal, hover):
        widget.bind('<Enter>', lambda e: widget.config(bg=hover))
        widget.bind('<Leave>', lambda e: widget.config(bg=normal))

    @staticmethod
    def _lighten(hex_color, factor=0.1):
        """Lighten a hex color by a factor."""
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f'#{r:02x}{g:02x}{b:02x}'


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == '__main__':
    app = TradingApp()
