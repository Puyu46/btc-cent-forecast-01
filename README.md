# BTC cent forecast 01 — pull back toward the 24-hour average

Guess Bitcoin's (cbBTC/USDC) price 240 minutes after each checkpoint,
using the 4,320 one-minute closes leading up to it. One program,
Python 3.13 standard library only, offline and deterministic.

## The model

```
forecast = last_close + 0.30 * (mean(last 1440 closes) - last_close)
```

In words: take the last close and move 30% of the way back toward the
24-hour simple moving average, then round to the price grid's
5 decimals. When a case holds fewer than 1,440 closes, the mean is
taken over however many there are. The result is clamped to the
allowed range (0, 10,000,000).

## Why mean reversion, not trend-following

I tested both ideas locally on the kit's practice recording
(Nov 7–11, 2026). The practice answers for p00–p04 follow from the
next case's last close (the cases overlap by 68 hours); p05's answer
is pinned by the house's published baseline mean together with the
on-chain record that no swap happened just before its target. With
those answers, the starter's persistence baseline reproduces exactly
at **44,521.576667 cents** mean absolute error.

| model | official 6 cases (cents) | 65 hourly pseudo-cases (cents) |
|---|---|---|
| persistence (house baseline) | 44,521.58 | 44,159.01 |
| drift: mean log-return, last 720 min, extrapolated 240 min | 40,181.70 | 50,060.97 |
| EWMA drift, halflife 240 min, k=0.5 | 43,721.21 | 48,581.96 |
| median of past 240-minute changes | 46,177.75 | 48,262.29 |
| **mean reversion to 24h MA, k=0.30 (this entry)** | **44,279.98** | **41,271.89** |

Trend extrapolation wins on the official six only because Nov 10 was
a strong downtrend day; across the wider 65-case window it scores
about 13% *worse* than persistence. Mean reversion beats persistence
on the official six (−241.60 cents, −0.54%), on the 65 hourly
pseudo-cases (−2,887.11 cents, −6.5%, wins 36 of 65), and on each of
the three days Nov 8, 9 and 10 separately. The gain is a smooth
plateau for k in 0.15–0.40 rather than a tuned spike (k=0.25:
41,408.16; k=0.30: 41,271.89; k=0.40: 41,480.29 on the hourly set),
and capping the pull makes both sets worse, so there is no cap.

An honest caveat: the edge is small and noisy. The paired-difference
standard deviation is roughly 15,300 cents on the hourly set, so the
improvement is not statistically significant on six cases. Expect a
small improvement over persistence on the unseen final, not a large
one. Per-case errors of this entry on the official practice: p00
28,623 / p01 85,175 / p02 77,225 / p03 19,309 / p04 37,494 / p05
17,853 cents (persistence: 31,711 / 76,697 / 47,033 / 56,685 /
23,147 / 31,856).

## Run

```
MAKEFUN_INPUT_DIR=<kit>/input MAKEFUN_OUTPUT_DIR=<out> python3 main.py
```

It reads every `<id>.in` in the input directory and writes
`<id>.out` as `{"forecasts": [{"case": "<id>", "price": <number>}]}`.
A run takes well under a second per case, and two runs on the same
case write identical bytes.
