# 🤖 Binance Futures Testnet Trading Bot

A clean, production-style Python CLI application for placing orders on the **Binance Futures Testnet (USDT-M)**.

---

## ✨ Features

- ✅ Place **MARKET** and **LIMIT** orders on Binance Futures Testnet
- ✅ Support for both **BUY** and **SELL** sides
- ✅ **STOP_LIMIT** order type (bonus)
- ✅ Full CLI with `argparse` — symbol, side, type, quantity, price, stop-price
- ✅ Structured code — separate client, orders, validators, and CLI layers
- ✅ Rotating file logger (`logs/trading_bot.log`) + console output
- ✅ Comprehensive exception handling (validation, API errors, network failures)
- ✅ Zero external dependencies beyond `requests`

---

## 📁 Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (signing, requests)
│   ├── orders.py          # Order placement logic (market, limit, stop-limit)
│   ├── validators.py      # Input validation helpers
│   ├── logging_config.py  # Rotating file + console logging setup
│   └── cli.py             # CLI entry point (argparse)
├── logs/
│   ├── market_order.log   # Sample MARKET order log
│   └── limit_order.log    # Sample LIMIT order log
├── README.md
└── requirements.txt
```

---

## ⚙️ Setup

### 1. Clone / unzip the project

```bash
git clone https://github.com/<your-username>/trading_bot.git
cd trading_bot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate.bat       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Binance Futures Testnet credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Sign in with GitHub
3. Navigate to **API Key** tab → generate a key pair
4. Copy your **API Key** and **Secret Key**

### 5. Add your credentials to `.env`

Copy the example file and fill in your real keys:

```bash
cp .env.example .env
```

Then open `.env` and replace the placeholders:

```env
BINANCE_API_KEY=your_actual_api_key
BINANCE_API_SECRET=your_actual_api_secret
```

> ⚠️ `.env` is in `.gitignore` — it will **never** be committed to Git.  
> Only `.env.example` (with empty placeholders) is tracked.

---

## 🚀 How to Run

Run the bot with `python -m bot.cli` from the `trading_bot/` directory.

### MARKET BUY

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### MARKET SELL

```bash
python -m bot.cli --symbol ETHUSDT --side SELL --type MARKET --quantity 0.1
```

### LIMIT BUY

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 60000
```

### LIMIT SELL (with custom time-in-force)

```bash
python -m bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 70000 --tif IOC
```

### STOP_LIMIT BUY (bonus order type)

```bash
python -m bot.cli \
  --symbol BTCUSDT \
  --side BUY \
  --type STOP_LIMIT \
  --quantity 0.01 \
  --price 68000 \
  --stop-price 67500
```

---

## 📋 CLI Reference

| Argument | Required | Description |
|---|---|---|
| `--symbol` | ✅ | Trading pair, e.g. `BTCUSDT` |
| `--side` | ✅ | `BUY` or `SELL` |
| `--type` | ✅ | `MARKET`, `LIMIT`, or `STOP_LIMIT` |
| `--quantity` | ✅ | Order quantity (base asset) |
| `--price` | LIMIT / STOP_LIMIT only | Limit price |
| `--stop-price` | STOP_LIMIT only | Trigger (stop) price |
| `--tif` | ❌ | Time-in-force: `GTC` (default), `IOC`, `FOK` |

---

## 📤 Sample Output

```
──────────────────────────────────────────────────
  ORDER REQUEST SUMMARY
──────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.01

──────────────────────────────────────────────────
  ORDER RESPONSE
──────────────────────────────────────────────────
  Order ID      : 3987654321
  Symbol        : BTCUSDT
  Side          : BUY
  Type          : MARKET
  Status        : FILLED
  Orig Qty      : 0.01000
  Executed Qty  : 0.01000
  Avg Price     : 67234.50000

──────────────────────────────────────────────────
  ✅  Order placed successfully!
──────────────────────────────────────────────────
```

---

## 📝 Logging

All activity is logged to **`logs/trading_bot.log`** (rotating, max 5 MB, 3 backups).

Log format:
```
2025-06-01 10:12:03 | INFO     | trading_bot | ORDER REQUEST  -> {...}
2025-06-01 10:12:03 | INFO     | trading_bot | ORDER RESPONSE <- {...}
```

Console output shows `INFO` and above. The file captures `DEBUG` level too (full request details, HTTP status codes).

---

## ⚠️ Error Handling

| Scenario | Behaviour |
|---|---|
| Missing `--price` on LIMIT | Validation error, exits with code 1 |
| Invalid symbol / negative quantity | Validation error, exits with code 1 |
| Missing API credentials | Clear message with setup instructions |
| Binance API error (e.g. insufficient balance) | Error code + message printed and logged |
| Network timeout / connection failure | Exception caught, logged, user-friendly message |

---

## 📌 Assumptions

- All orders are placed against the **USDT-M Futures** market (not Coin-M).
- Testnet base URL: `https://testnet.binancefuture.com`
- Credentials are loaded from environment variables (not hardcoded or from a config file) for security.
- Quantity precision follows Binance testnet defaults — if you get a `LOT_SIZE` error, adjust your `--quantity` to match the symbol's step size (e.g. 0.001 for BTCUSDT).
- `STOP_LIMIT` maps to Binance's `STOP` order type which requires both `price` and `stopPrice`.

---

## 🛠️ Tech Stack

- **Python 3.8+**
- [`requests`](https://docs.python-requests.org/) — HTTP client
- Standard library only for everything else (`argparse`, `logging`, `hmac`, `hashlib`)

---

## 📄 License

MIT — free to use and modify.
