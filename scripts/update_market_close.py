import json
from datetime import datetime, timezone
from urllib.parse import quote
import requests

SYMBOLS = {"nifty50": "^NSEI", "sensex": "^BSESN", "banknifty": "^NSEBANK", "indiavix": "^INDIAVIX"}

def fetch(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol, safe='')}?range=10d&interval=1d&events=history"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    r.raise_for_status()
    result = r.json()["chart"]["result"][0]
    rows = [(ts, close) for ts, close in zip(result["timestamp"], result["indicators"]["quote"][0]["close"]) if close is not None]
    if not rows:
        raise RuntimeError(f"No closing data returned for {symbol}")
    ts, close = rows[-1]
    previous = rows[-2][1] if len(rows) > 1 else None
    change = close - previous if previous is not None else None
    pct = (change / previous * 100) if previous not in (None, 0) else None
    return {"symbol": symbol, "value": round(close, 2), "previous_close": round(previous, 2) if previous is not None else None, "change": round(change, 2) if change is not None else None, "change_pct": round(pct, 2) if pct is not None else None, "session_date": datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()}

out = {"updated_at_utc": datetime.now(timezone.utc).isoformat(), "source": "Yahoo Finance chart data", "indices": {key: fetch(symbol) for key, symbol in SYMBOLS.items()}}

with open("data/market-close.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)

print(json.dumps(out, indent=2))
