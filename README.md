# 📈 Stock Market Simulator V2 MAX

> A professional-grade paper trading terminal built entirely in Python —
> no web framework, no database, just clean modular Python.

<br>

**Built by Parth — AI & Data Science Engineering, DMCE Mumbai**
**Datta Meghe College of Engineering**

---

## ✨ Features

### 🖥️ Professional Trading Terminal UI
- Bloomberg × Zerodha Kite inspired dark theme (deep navy, surgical accents)
- Live market price table updating every **2 seconds** with inline % change
- Smooth animated **Next Day** transitions using linear interpolation
- Scrolling news ticker at the bottom of the screen
- Real-time topbar — Day counter, Cash Balance, Total Value, live P&L
- Hover tooltips on market rows showing full MA / RSI / MACD analysis
- P&L flash animation on portfolio update (green ↑ / red ↓)

### 📊 Charts
- **Line chart** with MA5 and MA20 moving average overlays
- **Candlestick (OHLC) chart** — green/red candles with wicks
- **All Stocks grid** — 5 stocks in a 2×3 layout simultaneously
- **Portfolio value over time** — net worth tracked across every simulated day

### 💼 Portfolio Management
- Cash balance and stock holdings with live tick prices
- Weighted average buy price calculation
- Per-position P&L and return % with color-coded flash on change
- Full trade history with BUY / SELL filter
- **Best Trade** — highest profit single sell
- **Worst Trade** — highest loss single sell

### 📊 Performance Insights
- 📈 Portfolio Growth %
- 📉 Max Drawdown %
- 🏆 Best performing stock
- 📉 Worst performing stock

### 🤖 Trading Bot — Triple Confirmation System
Three independent technical indicators vote on every trade:

| Indicator | Signal |
|-----------|--------|
| **MA Crossover** (MA5 vs MA20) | Trend direction |
| **RSI** (14-period) | Overbought / Oversold zones |
| **MACD** (12/26/9) | Momentum confirmation |

**Combined score −3 to +3:**

| Score | Signal |
|-------|--------|
| ≥ +2 | **STRONG BUY** |
| +1 | **BUY** |
| 0 | **HOLD** |
| −1 | **SELL** |
| ≤ −2 | **STRONG SELL** |

**Bot modes:**
- **Manual** — shows full trade proposal with confirmation dialog before executing
- **Auto** — trades silently every N days (configurable interval in sidebar)
- Auto-bot flashes green on the sidebar button when it fires

### 📰 Market News Events
- 10% daily probability of a major news event per stock
- Bad news: −5% to −15% price shock
- Good news: +5% to +15% price shock
- Full news feed saved and restored on reload
- Scrolling news ticker shows latest events at the bottom

### ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1` – `6` | Navigate panels |
| `N` | Next Day |
| `B` | Buy dialog |
| `S` | Sell dialog |
| `A` | Toggle Auto-Bot |
| `Ctrl+S` | Save portfolio |

> Shortcuts are suppressed when typing in input fields.

### 💾 Persistent Save / Load
Saves the **complete simulator state** to `portfolio.json`:
- Cash balance and holdings
- Full market price history for all 5 stocks
- Current day counter
- Portfolio value history
- Market news feed history
- Trade history exported to `history.csv`

---

## 🗂️ Project Structure

```
Stock-Market-Simulator-V2/
│
├── main.py           ← UI — tkinter trading terminal (2,174 lines)
├── market.py         ← Stock universe, price simulation, news events
├── trading.py        ← Buy / sell logic with validation
├── portfolio.py      ← Portfolio state, save/load, P&L calculations
├── history.py        ← Trade log, CSV export
├── bot.py            ← SMA, EMA, RSI, MACD, scoring engine
├── state.py          ← Central AppState singleton + callback system
│
├── run.bat           ← One-click launcher (Windows)
├── portfolio.json    ← Save file (auto-generated)
├── history.csv       ← Trade history (auto-generated)
└── test-phase1.py    ← Backend verification — 18 automated tests
```

---

## 🚀 Getting Started

### Prerequisites
```bash
python3 --version   # Requires Python 3.10+
```

### Install dependencies
```bash
python3 -m pip install matplotlib
```
> `tkinter` is built into Python — no separate install needed.

### Run (recommended)
```bash
cd Stock-Market-Simulator-V2
python3 main.py
```

### One-click launcher (Windows)
Double-click `run.bat` in the project folder.
> Never double-click `main.py` directly — it changes the working directory and save files won't work.

### Verify backend (optional)
```bash
python3 test-phase1.py   # All 18 tests should pass
```

---

## 🧠 Technical Concepts Demonstrated

| Concept | Where |
|---------|-------|
| **Modular programming** | 6 independent backend modules |
| **Stochastic simulation** | Gaussian random walk: `P_new = P_old × (1 + μ + σε)` |
| **Algorithmic trading** | MA crossover, RSI, MACD triple confirmation |
| **Data visualization** | matplotlib embedded in tkinter (line, candlestick, grid) |
| **Event-driven UI** | Callback/subscription system in `state.py` |
| **File I/O** | JSON save/load, CSV trade history |
| **OOP design** | Panel classes, AppState singleton, custom widgets |
| **Statistics** | Weighted average buy price, moving averages, EMA formula |
| **Animation** | Linear interpolation for smooth Next Day transitions |
| **Real-time updates** | `root.after()` tick loop — no threading needed |

### Key Formulas

**EMA (Exponential Moving Average)**
```
k   = 2 / (period + 1)
EMA = price × k + EMA_prev × (1 − k)
```

**RSI (Relative Strength Index)**
```
RS  = avg_gain / avg_loss
RSI = 100 − (100 / (1 + RS))
```

**MACD**
```
MACD Line   = EMA(12) − EMA(26)
Signal Line = EMA(9) of MACD Line history
Histogram   = MACD Line − Signal Line
```

**Weighted Average Buy Price**
```
new_avg = (old_shares × old_avg + qty × price) / new_shares
```

**Gaussian Price Simulation**
```
P_new = P_old × (1 + drift + volatility × ε)
where ε ~ N(0, 1),  drift = 0.001,  volatility = 0.02
```

---

## 📦 Stocks Included

| Symbol | Company | Starting Price |
|--------|---------|---------------|
| AAPL | Apple Inc. | $175.00 |
| TSLA | Tesla Inc. | $210.00 |
| GOOG | Alphabet Inc. | $140.00 |
| AMZN | Amazon.com Inc. | $185.00 |
| MSFT | Microsoft Corp. | $420.00 |

---

## 🛠️ Built With

- **Python 3.10+** — core language
- **tkinter** — desktop UI framework (built-in, zero install)
- **matplotlib** — charts, candlestick visualization, embedded figures
- **json** — complete simulator state save/load
- **csv** — trade history export
- **random** — Gaussian price simulation and news events

---

## 📁 Save Files

| File | Contents |
|------|----------|
| `portfolio.json` | Balance, holdings, market price history, day counter, news feed |
| `history.csv` | All trades — time, day, action, symbol, quantity, price, total |

> To start a completely fresh simulation, delete both files before running.

---

## 🔭 Future Ideas

- [ ] RSI divergence detection
- [ ] Multiple portfolios / accounts
- [ ] Export charts as PNG
- [ ] Custom stock list and starting prices
- [ ] Dark/light theme toggle
- [ ] Backtesting mode on historical data

---

## 👨‍💻 Author

**Parth**
AI & Data Science Engineering — Semester 2
Datta College of Engineering (DMCE), Mumbai

> *"Built from scratch as a personal project, grown into a full trading terminal."*

---

## 📄 License

**All Rights Reserved.**
This project is protected under a custom restrictive license.

✅ You may read and study this code for personal learning.
❌ You may NOT copy, submit, present, or use this in any hackathon,
competition, or academic submission without explicit permission.

See [LICENSE](./LICENSE) for full terms.
