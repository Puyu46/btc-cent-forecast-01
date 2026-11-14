# btc-cent-forecast-01 — Bitcoin's price 240 minutes ahead.
#
# Model: mild mean reversion toward the 24-hour simple moving average.
#   forecast = last_close + 0.30 * (mean(last 1440 closes) - last_close)
#
# Why this shape (measured on the kit's practice recording, Nov 7-11 2026):
#   - Trend extrapolation looks good on the 6 official practice cases
#     only because Nov 10 was a steep downtrend day; on 65 hourly
#     pseudo-cases cut from the same recording it scores about 13%
#     WORSE than the persistence baseline.
#   - Pulling 30% of the way back to the 24h mean beats persistence on
#     both sets: 44,279.98 vs 44,521.58 cents MAE on the official 6,
#     and 41,271.89 vs 44,159.01 cents on the 65 hourly pseudo-cases,
#     winning on each of the three days Nov 8, 9 and 10.
#   - The gain is a smooth plateau for k between 0.15 and 0.40, not a
#     tuned spike, and capping the pull makes both sets worse, so no
#     cap is applied.
#   - The edge is small and noisy (paired-difference SD around
#     15,300 cents on the hourly set), so the honest expectation for
#     the unseen final is a modest improvement over persistence, not
#     a dramatic one.
#
# Deterministic, standard library only, no network, no randomness:
# the same case file always produces the same output bytes, and a
# run takes well under a second.
#
# Usage: python3 main.py — reads $MAKEFUN_INPUT_DIR (else /input) for
# every <id>.in and writes $MAKEFUN_OUTPUT_DIR/<id>.out (else /output)
# as {"forecasts": [{"case": "<id>", "price": <number>}]}, with the
# price rounded to the grid's 5 decimals and clamped to
# (0, 10,000,000).

import json
import math
import os
from pathlib import Path

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

WINDOW = 1440               # one-minute closes averaged: the last 24 hours
PULL = 0.30                 # fraction of the gap to the 24h mean to close
MIN_PRICE = 0.00001         # smallest positive price on the 5-decimal grid
MAX_PRICE = 9_999_999.99999  # largest grid price below the 10,000,000 cap


def price5(value):
    """Round a price onto the 5-decimal grid, inside (0, 10,000,000)."""
    clamped = min(MAX_PRICE, max(MIN_PRICE, value))
    return round(clamped * 1e5) / 1e5


def forecast(prices):
    """Forecast one case: prices are one-minute closes, last = checkpoint."""
    if not prices:
        raise ValueError("case has no prices")
    last = prices[-1]
    if not isinstance(last, (int, float)) or not math.isfinite(last):
        raise ValueError("last price is not a finite number")
    window = prices[-WINDOW:]
    mean_24h = sum(window) / len(window)
    return price5(last + PULL * (mean_24h - last))


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    inputs = sorted(INPUT_DIR.glob("*.in"))
    for path in inputs:
        case_id = path.name[: -len(".in")]
        with path.open("r", encoding="utf-8") as handle:
            case = json.load(handle)
        markets = case.get("markets")
        if not isinstance(markets, list) or len(markets) != 1:
            raise ValueError(f"{path.name} does not hold exactly one market")
        prices = markets[0].get("prices")
        if not isinstance(prices, list) or not prices:
            raise ValueError(f"{path.name} holds no prices")
        output = {"forecasts": [{"case": case_id, "price": forecast(prices)}]}
        with (OUTPUT_DIR / f"{case_id}.out").open("w", encoding="utf-8") as handle:
            handle.write(json.dumps(output) + "\n")


if __name__ == "__main__":
    main()
