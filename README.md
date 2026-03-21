# 📈 Stock Market Simulator V2 MAX

> A professional-grade paper trading terminal built entirely in Python.
> Features a live dark-themed desktop UI, intelligent trading bot, real technical indicators, and persistent save/load — all without any web framework or database.

<br>

**Built by Parth Mahadeo Korgaonkar — AI \& Data Science Engineering, DMCE Mumbai**

\---

## ✨ Features

### 🖥️ Professional Trading Terminal UI

* Bloomberg × Zerodha Kite inspired dark theme
* Live market price table updating every 2 seconds
* Smooth animated Next Day transitions (linear interpolation, no cliffs)
* Scrolling news ticker at the bottom of the screen
* Real-time topbar showing Day, Cash Balance, Total Value, and live P\&L

### 📊 Charts

* **Line chart** with MA5 and MA20 overlays
* **Candlestick (OHLC) chart** with green/red candles and wicks
* **All Stocks grid** — 5 stocks in a 2×3 layout
* **Portfolio value over time** — tracks net worth across every day

### 💼 Portfolio Management

* Cash balance and stock holdings with live tick prices
* Weighted average buy price calculation
* Per-position P\&L and return % with color-coded flash on change
* Full trade history with BUY/SELL filter

### 🤖 Trading Bot — Triple Confirmation System

Three independent technical indicators vote on every trade:

|Indicator|Signal|
|-|-|
|**MA Crossover** (MA5 vs MA20)|Trend direction|
|**RSI** (14-period)|Overbought / Oversold zones|
|**MACD** (12/26/9)|Momentum confirmation|

Combined score −3 to +3:

* `≥ +2` → **STRONG BUY**
* `+1`   → **BUY**
* `0`    → **HOLD**
* `−1`   → **SELL**
* `≤ −2` → **STRONG SELL**

Bot modes:

* **Manual** — shows trade proposals, asks for confirmation before executing
* **Auto** — trades silently after every N days (configurable interval)

### 📰 Market News Events

* 10% daily probability of a major news event per stock
* Bad news: −5% to −15% price shock
* Good news: +5% to +15% price shock
* Full news feed saved and restored on reload

### ⌨️ Keyboard Shortcuts

|Key|Action|
|-|-|
|`1` – `6`|Navigate panels|
|`N`|Next Day|
|`B`|Buy dialog|
|`S`|Sell dialog|
|`A`|Toggle Auto-Bot|
|`Ctrl+S`|Save portfolio|

### 💾 Persistent Save / Load

Saves the **complete simulator state** to `portfolio.json`:

* Cash balance and holdings
* Full market price history for all 5 stocks
* Current day counter
* Portfolio value history
* Market news feed history
* Trade history to `history.csv`

\---

## 🗂️ Project Structure

```
stock\_market\_simulator/
│
├── main.py          ← UI — tkinter trading terminal (Phase 4)
├── market.py        ← Stock universe, price simulation, news events
├── trading.py       ← Buy / sell logic with validation
├── portfolio.py     ← Portfolio state, save/load, P\&L calculations
├── history.py       ← Trade log, CSV export
├── bot.py           ← SMA, EMA, RSI, MACD, scoring engine
├── state.py         ← Central AppState singleton + callback system
│
├── portfolio.json   ← Save file (auto-generated)
├── history.csv      ← Trade history (auto-generated)
└── test-phase1.py   ← Backend verification tests (18 tests)
```

\---

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

### Run

```bash
cd stock\_market\_simulator
python3 main.py
```

### Verify backend (optional)

```bash
python3 test-phase1.py   # All 18 tests should pass
```

\---

## 🧠 Technical Concepts Demonstrated

|Concept|Where|
|-|-|
|**Modular programming**|6 independent backend modules|
|**Stochastic simulation**|Gaussian random walk: `P\_new = P\_old × (1 + μ + σε)`|
|**Algorithmic trading**|MA crossover, RSI, MACD triple confirmation|
|**Data visualization**|matplotlib embedded in tkinter (line, candlestick, grid)|
|**Event-driven UI**|Callback/subscription system in `state.py`|
|**File I/O**|JSON save/load, CSV trade history|
|**OOP design**|Panel classes, AppState singleton, custom widgets|
|**Statistics**|Weighted average buy price, moving averages, EMA formula|
|**Animation**|Linear interpolation for smooth Next Day transitions|
|**Real-time updates**|`root.after()` tick loop — no threading needed|

### Key Formulas

**EMA (Exponential Moving Average)**

```
k   = 2 / (period + 1)
EMA = price × k + EMA\_prev × (1 − k)
```

**RSI (Relative Strength Index)**

```
RS  = avg\_gain / avg\_loss
RSI = 100 − (100 / (1 + RS))
```

**MACD**

```
MACD Line   = EMA(12) − EMA(26)
Signal Line = EMA(9) of MACD Line
Histogram   = MACD Line − Signal Line
```

**Weighted Average Buy Price**

```
new\_avg = (old\_shares × old\_avg + qty × price) / new\_shares
```

\---

## 📦 Stocks Included

|Symbol|Company|Starting Price|
|-|-|-|
|AAPL|Apple Inc.|$175.00|
|TSLA|Tesla Inc.|$210.00|
|GOOG|Alphabet Inc.|$140.00|
|AMZN|Amazon.com Inc.|$185.00|
|MSFT|Microsoft Corp.|$420.00|

\---

## 🛠️ Built With

* **Python 3.10+** — core language
* **tkinter** — desktop UI framework (built-in)
* **matplotlib** — charts and candlestick visualization
* **json** — save/load state
* **csv** — trade history export
* **random** — Gaussian price simulation

\---

## 📁 Save Files

|File|Contents|
|-|-|
|`portfolio.json`|Balance, holdings, market history, day counter, news feed|
|`history.csv`|All trades — time, day, action, symbol, quantity, price, total|

To start a fresh game, delete both files before running.

\---

## 🔭 Future Ideas

* \[ ] RSI divergence detection
* \[ ] Multiple portfolios / accounts
* \[ ] Export charts as PNG
* \[ ] Custom stock list
* \[ ] Dark/light theme toggle
* \[ ] Backtesting mode

\---

## 👨‍💻 Author

**Parth**
AI \& Data Science Engineering — 2nd Semester
Dwarkadas J. Sanghvi College of Engineering (DMCE), Mumbai

> \*"Built from scratch as a college project, grown into a full trading terminal."\*

\---

## 📄 License

This project is for educational purposes.
Free to use, modify, and share with attribution.

