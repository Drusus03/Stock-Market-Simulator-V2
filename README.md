# 📈 Stock Market Simulator V2 MAX

> A professional-grade paper trading terminal built entirely in Python —
> no web framework, no database, just clean modular Python.

<br>

**Built by Parth — AI & Data Science Engineering, DMCE Mumbai**
**Datta Meghe College of Engineering (DMCE), Navi Mumbai**

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
- 🏆 Best performing stock (live holdings)
- 📉 Worst performing stock (live holdings)

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

### 📰 Market News Events
- 10% daily probability of a major news event per stock
- Bad news: −5% to −15% price shock
- Good news: +5% to +15% price shock
- Full news feed saved and restored on reload

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
├── main.py           ← UI — tkinter trading terminal (~2,174 lines)
├── market.py         ← Stock universe, price simulation, news events
├── trading.py        ← Buy / sell logic with validation
├── portfolio.py      ← Portfolio state, save/load, P&L calculations
├── history.py        ← Trade log, CSV export
├── bot.py            ← SMA, EMA, RSI, MACD, scoring engine
├── state.py          ← Central AppState singleton + callback system
│
├── run.bat           ← One-click launcher (Windows)
├── requirements.txt  ← Python dependencies
├── portfolio.json    ← Save file (auto-generated on first save)
├── history.csv       ← Trade history (auto-generated on first save)
└── test-phase1.py    ← Backend verification — 18 automated tests
```

---

## ⚙️ Requirements

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 / macOS 10.15 / Ubuntu 20.04 | Windows 11 / Ubuntu 22.04 |
| **Python** | 3.10 | 3.11 or 3.13 |
| **RAM** | 512 MB free | 1 GB free |
| **Display** | 1100 × 700 | 1440 × 900 or higher |
| **Storage** | 150 MB (Python + matplotlib + project) | 300 MB |

### Python Dependencies

| Package | Version | Purpose | Install Required |
|---------|---------|---------|-----------------|
| `matplotlib` | ≥ 3.7.0 | Charts, candlestick, embedded figures | ✅ Yes |
| `tkinter` | Built-in | Desktop UI framework | ❌ No (comes with Python) |
| `json` | Built-in | Save/load simulator state | ❌ No |
| `csv` | Built-in | Trade history export | ❌ No |
| `random` | Built-in | Gaussian price simulation | ❌ No |
| `collections` | Built-in | `deque` for tick history buffer | ❌ No |
| `datetime` | Built-in | Timestamps, clock display | ❌ No |

> **Only one package needs to be installed: `matplotlib`**
> Everything else is part of Python's standard library.

### `requirements.txt`

```
matplotlib>=3.7.0
```

---

## 🚀 Installation & Setup

### Step 1 — Install Python

Download Python 3.10 or higher from [python.org](https://www.python.org/downloads/)

During installation on Windows:
- ✅ Check **"Add Python to PATH"**
- ✅ Check **"Install pip"**

Verify installation:
```bash
python3 --version
# Expected: Python 3.10.x or higher
```

---

### Step 2 — Download the Project

**Option A — Clone with Git (recommended):**
```bash
git clone https://github.com/Drusus03/Stock-Market-Simulator-V2.git
cd Stock-Market-Simulator-V2
```

**Option B — Download ZIP:**
1. Click the green **Code** button on GitHub
2. Click **Download ZIP**
3. Extract the ZIP to a folder of your choice
4. Open that folder in terminal

---

### Step 3 — Install Dependencies

This project requires only **one external package** — matplotlib.

**Windows:**
```bash
python3 -m pip install matplotlib
```

**macOS / Linux:**
```bash
pip3 install matplotlib
```

**Or install from requirements.txt:**
```bash
python3 -m pip install -r requirements.txt
```

> ⚠️ **Windows users:** Always use `python3 -m pip install` (not just `pip install`)
> to ensure the package installs into the correct Python version.

Verify matplotlib installed correctly:
```bash
python3 -c "import matplotlib; print(matplotlib.__version__)"
# Expected: 3.7.x or higher
```

---

### Step 4 — Verify tkinter (Python's built-in UI)

tkinter comes bundled with Python on Windows and macOS.
On Linux it may need a separate install:

```bash
# Test if tkinter is available:
python3 -c "import tkinter; print('tkinter OK')"
```

If you see `ModuleNotFoundError` on Linux:
```bash
# Ubuntu / Debian:
sudo apt-get install python3-tk

# Fedora:
sudo dnf install python3-tkinter

# Arch:
sudo pacman -S tk
```

---

### Step 5 — Run the App

**Method 1 — Terminal (recommended):**
```bash
cd Stock-Market-Simulator-V2
python3 main.py
```

**Method 2 — One-click launcher (Windows only):**
Double-click `run.bat` in the project folder.

> ⚠️ **Never double-click `main.py` directly.**
> This changes the working directory and save files
> (`portfolio.json`, `history.csv`) will fail to write
> with a `Permission denied` error.

---

### Step 6 — Verify Backend (Optional but Recommended)

Run the 18-test backend verification suite:
```bash
python3 test-phase1.py
```

Expected output:
```
✅ Test 1  PASS — market.get_market_data()
✅ Test 2  PASS — market.generate_tick()
...
✅ Test 18 PASS — AppState callback system

ALL 18 TESTS PASSED — Phase 1 complete ✅
```

If all 18 tests pass, the backend is fully functional and the app is ready to use.

---

## 🔧 Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: matplotlib` | Not installed | `python3 -m pip install matplotlib` |
| `ModuleNotFoundError: tkinter` | Linux missing package | `sudo apt-get install python3-tk` |
| `Permission denied: portfolio.json` | Double-clicked `main.py` | Use `run.bat` or run from terminal |
| `Permission denied: portfolio.json` | File open in another app | Close VS Code / Notepad, retry |
| Window opens but blank | Display scaling issue | Right-click → Properties → Compatibility → Override DPI |
| `python3` not recognized | Python not in PATH | Reinstall Python, check "Add to PATH" |

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
| **Statistics** | Weighted average buy price, moving averages, EMA |
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

**Gaussian Price Simulation (Random Walk)**
```
P_new = P_old × (1 + drift + volatility × ε)
where ε ~ N(0,1),  drift = 0.001,  volatility = 0.02
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
- **tkinter** — desktop UI framework (built-in)
- **matplotlib 3.7+** — charts, candlestick, embedded figures
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
Datta Meghe College of Engineering (DMCE), Navi Mumbai

> *"Built from scratch as a college project, grown into a full trading terminal."*

---

## 📄 License

**All Rights Reserved.**
This project is protected under a custom restrictive license.

✅ You may read and study this code for personal learning.
❌ You may NOT copy, submit, present, or use this in any hackathon,
competition, or academic submission without explicit permission from the author.

See [LICENSE](./LICENSE) for full terms.
