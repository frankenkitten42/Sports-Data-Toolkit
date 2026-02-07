# normalize_odds.py - What It Is & How to Use It

## 📋 Overview

**normalize_odds.py** is a **post-processing tool** that takes raw odds data collected by your snapshot scripts and converts it into a clean, analysis-ready format with probability calculations and vig removal.

### The Problem It Solves

When you collect odds data from APIs like The Odds API or API-Sports, you get:
- American odds format (-110, +150, etc.)
- Bookmaker "juice" (vigorish) baked into the probabilities
- Nested JSON structures that are hard to analyze

**normalize_odds.py** transforms this into:
- Multiple odds formats (American, Decimal)
- True implied probabilities
- **Fair probabilities** (with bookmaker vig removed)
- Flat CSV format perfect for spreadsheets and analysis

---

## 🔄 The Workflow

```
Step 1: Collect Raw Data              Step 2: Normalize & Analyze
┌─────────────────────────┐          ┌──────────────────────────┐
│ snapshot_oddsapi.py     │   JSON   │ normalize_odds.py        │
│ snapshot_apisports.py   │  ──────► │                          │
│                         │          │ • Convert odds formats   │
│ Saves to:               │          │ • Calculate probabilities│
│   snapshots/            │          │ • Remove bookmaker vig   │
│   snapshots_oddsapi/    │          │ • Export CSV + JSON      │
│   snapshots_apisports/  │          │                          │
└─────────────────────────┘          │ Saves to:                │
                                     │   normalized/            │
                                     └──────────────────────────┘
```

---

## 🎯 What It Does

### Input: Raw Odds Snapshot

From `snapshot_oddsapi.py`:
```json
{
  "events": [
    {
      "id": "abc123",
      "sport_key": "basketball_nba",
      "commence_time": "2024-11-15T20:00:00Z",
      "home_team": "Lakers",
      "away_team": "Celtics",
      "bookmakers": [
        {
          "key": "fanduel",
          "markets": [
            {
              "key": "h2h",
              "outcomes": [
                {"name": "Lakers", "price": -110},
                {"name": "Celtics", "price": +100}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### Output: Normalized Data

**JSON Output** (`normalized/snapshot_20241115.json`):
```json
[
  {
    "event_id": "abc123",
    "sport": "basketball_nba",
    "commence_time": "2024-11-15T20:00:00Z",
    "bookmaker": "fanduel",
    "market": "h2h",
    "outcome": "Lakers",
    "american_odds": -110,
    "decimal_odds": 1.9091,
    "implied_probability": 0.5238,
    "fair_probability": 0.5119,
    "last_update": "2024-11-15T19:45:00Z"
  },
  {
    "event_id": "abc123",
    "sport": "basketball_nba",
    "commence_time": "2024-11-15T20:00:00Z",
    "bookmaker": "fanduel",
    "market": "h2h",
    "outcome": "Celtics",
    "american_odds": 100,
    "decimal_odds": 2.0,
    "implied_probability": 0.5000,
    "fair_probability": 0.4881,
    "last_update": "2024-11-15T19:45:00Z"
  }
]
```

**CSV Output** (`normalized/snapshot_20241115.csv`):
```csv
event_id,sport,commence_time,bookmaker,market,outcome,american_odds,decimal_odds,implied_probability,fair_probability,last_update
abc123,basketball_nba,2024-11-15T20:00:00Z,fanduel,h2h,Lakers,-110,1.9091,0.5238,0.5119,2024-11-15T19:45:00Z
abc123,basketball_nba,2024-11-15T20:00:00Z,fanduel,h2h,Celtics,100,2.0,0.5000,0.4881,2024-11-15T19:45:00Z
```

---

## 📊 Key Features Explained

### 1. Odds Format Conversion

**American → Decimal**
```python
# American odds: -110
# Decimal odds: 1.9091

# Formula:
if american_odds > 0:
    decimal = 1 + (american_odds / 100)
else:
    decimal = 1 + (100 / abs(american_odds))
```

### 2. Implied Probability

**What the bookmaker thinks will happen**

```python
# Decimal odds: 1.9091
# Implied probability: 1 / 1.9091 = 0.5238 (52.38%)
```

### 3. Fair Probability (Vig Removal) ⭐

**The REAL probability after removing bookmaker's edge**

```
Lakers implied prob:  52.38%
Celtics implied prob: 50.00%
                     -------
Total:               102.38%  ← Bookmaker's 2.38% edge (vig)

After vig removal:
Lakers fair prob:  52.38% / 102.38% = 51.19%
Celtics fair prob: 50.00% / 102.38% = 48.81%
                                      -------
Total:                               100.00%  ← Now adds up correctly!
```

This is **crucial** for:
- Finding true value bets
- Comparing odds across bookmakers
- Building betting models
- Understanding real probabilities

---

## 🚀 How to Use It

### Step 1: Collect Odds Data

**Option A: Use The Odds API**
```bash
# Fetch NBA odds
python3 snapshot_oddsapi.py snapshot --sports basketball_nba

# Output: snapshots_oddsapi/basketball_nba/basketball_nba_20241115_194500.json
```

**Option B: Use API-Sports**
```bash
# Fetch odds from API-Sports
python3 snapshot_apisports.py snapshot

# Output: snapshots_apisports/basketball/odds_20241115_194500.json
```

### Step 2: Normalize the Data

**Basic Usage:**
```bash
# Normalize all snapshots in the snapshots/ folder
python3 normalize_odds.py

# Output:
#   ✅ Saved normalized JSON → normalized/snapshot_20241115_194500.json
#   ✅ Saved normalized CSV  → normalized/snapshot_20241115_194500.csv
```

**Configuration:**

Edit `normalize_odds.py` if needed:
```python
SNAPSHOT_FOLDER = "snapshots"           # Where to read raw data
NORMALIZED_FOLDER = "normalized"        # Where to save processed data
sport = "basketball_nba"                # Sport identifier (optional)
```

### Step 3: Analyze the Data

**Open CSV in spreadsheet:**
```bash
# Excel, Google Sheets, LibreOffice, etc.
open normalized/snapshot_20241115_194500.csv
```

**Or use Python:**
```python
import pandas as pd

df = pd.read_csv("normalized/snapshot_20241115_194500.csv")

# Find best odds for Lakers
lakers_odds = df[df['outcome'] == 'Lakers'].sort_values('decimal_odds', ascending=False)
print("Best Lakers odds:")
print(lakers_odds[['bookmaker', 'american_odds', 'decimal_odds', 'fair_probability']])

# Compare implied vs fair probabilities
df['vig'] = df['implied_probability'] - df['fair_probability']
print(f"\nAverage bookmaker edge: {df['vig'].mean():.2%}")
```

---

## 🔍 Real-World Example

### Scenario: Find Value Bets

```bash
# 1. Collect odds from multiple bookmakers
python3 snapshot_oddsapi.py snapshot --sports basketball_nba --markets h2h

# 2. Normalize the data
python3 normalize_odds.py

# 3. Analyze in Python
```

```python
import pandas as pd

df = pd.read_csv("normalized/basketball_nba_20241115.csv")

# Find games with the lowest vig (best odds)
game_vigs = df.groupby('event_id').apply(
    lambda x: (x['implied_probability'].sum() - 1.0) * 100
)

print("Games with lowest bookmaker edge:")
print(game_vigs.sort_values().head(10))

# Find bookmaker with best odds on average
bookmaker_avg_odds = df.groupby('bookmaker')['implied_probability'].mean()
print("\nBookmakers ranked by odds quality (lower is better):")
print(bookmaker_avg_odds.sort_values())
```

---

## 📁 File Structure

```
your-project/
├── snapshot_oddsapi.py          # Collect from The Odds API
├── snapshot_apisports.py        # Collect from API-Sports
├── normalize_odds.py            # Process and normalize ← THIS TOOL
│
├── snapshots/                   # Raw odds data (INPUT)
│   ├── basketball_nba_20241115_194500.json
│   └── basketball_nba_20241115_200000.json
│
└── normalized/                  # Processed data (OUTPUT)
    ├── basketball_nba_20241115_194500.json
    ├── basketball_nba_20241115_194500.csv
    ├── basketball_nba_20241115_200000.json
    └── basketball_nba_20241115_200000.csv
```

---

## ⚙️ Technical Details

### Functions

**`american_to_decimal(odds)`**
- Converts American odds (-110, +150) to decimal format (1.91, 2.50)

**`compute_implied_prob(decimal_odds)`**
- Calculates implied probability from decimal odds
- Formula: 1 / decimal_odds

**`remove_vig(probabilities)`**
- Removes bookmaker vig/juice from probabilities
- Normalizes so probabilities sum to exactly 1.0 (100%)

**`normalize_snapshot_file(filename)`**
- Processes a single JSON snapshot file
- Returns list of normalized rows

**`normalize_all_snapshots()`**
- Processes all JSON files in SNAPSHOT_FOLDER
- Saves both JSON and CSV to NORMALIZED_FOLDER

### Output Fields

| Field | Description | Example |
|-------|-------------|---------|
| event_id | Unique game identifier | "abc123" |
| sport | Sport key | "basketball_nba" |
| commence_time | Game start time (UTC) | "2024-11-15T20:00:00Z" |
| bookmaker | Bookmaker identifier | "fanduel" |
| market | Betting market type | "h2h" (head-to-head/moneyline) |
| outcome | Team or outcome name | "Lakers" |
| american_odds | American odds format | -110 |
| decimal_odds | Decimal odds format | 1.9091 |
| implied_probability | Bookmaker's implied prob | 0.5238 (52.38%) |
| fair_probability | True prob (vig removed) | 0.5119 (51.19%) |
| last_update | When odds were updated | "2024-11-15T19:45:00Z" |

---

## 🎓 Understanding the Math

### Why Remove Vig?

Bookmakers don't offer fair odds. They build in an edge:

**Example:**
```
Fair coin flip:
  Heads: 50% probability
  Tails: 50% probability
  Total: 100%

Bookmaker's odds:
  Heads: -110 (52.38% implied probability)
  Tails: -110 (52.38% implied probability)
  Total: 104.76%  ← 4.76% is the bookmaker's edge!
```

The bookmaker guarantees profit regardless of outcome because probabilities sum to >100%.

**Removing vig:**
```python
heads_fair = 52.38% / 104.76% = 50.00%
tails_fair = 52.38% / 104.76% = 50.00%
Total: 100.00%  ← Now mathematically correct!
```

### Finding Value Bets

A value bet exists when:
```
fair_probability < (1 / decimal_odds)
```

Example:
```
Your model: Lakers have 55% chance to win
Bookmaker odds: Lakers +110 (decimal 2.10)
Bookmaker's implied probability: 1/2.10 = 47.6%

55% > 47.6%  ← VALUE BET!
You believe they have a better chance than the odds suggest
```

---

## 💡 Tips & Best Practices

### 1. Collect Multiple Snapshots
```bash
# Run every 5 minutes to track odds movement
while true; do
  python3 snapshot_oddsapi.py snapshot --sports basketball_nba
  python3 normalize_odds.py
  sleep 300
done
```

### 2. Compare Bookmakers
```python
# Find best odds for each outcome
df.groupby(['event_id', 'outcome']).apply(
    lambda x: x.nsmallest(1, 'implied_probability')
)
```

### 3. Track Odds Changes
```python
# Load multiple snapshots over time
import glob

dfs = []
for file in sorted(glob.glob("normalized/*.csv")):
    df = pd.read_csv(file)
    df['snapshot_file'] = file
    dfs.append(df)

all_data = pd.concat(dfs)

# See how odds changed for a specific game
game_history = all_data[all_data['event_id'] == 'abc123']
print(game_history[['outcome', 'american_odds', 'snapshot_file']])
```

### 4. Identify Sharp Money
```python
# Look for significant odds movements
# Sharp bettors cause line moves
```

---

## 🔗 Integration with Other Tools

### Works With:
- ✅ **snapshot_oddsapi.py** - Primary use case
- ✅ **snapshot_apisports.py** - API-Sports data (may need format adjustment)
- ✅ **Pandas** - For advanced data analysis
- ✅ **Excel/Google Sheets** - Direct CSV import
- ✅ **SQLite/PostgreSQL** - Load CSV into database

### Next Steps:
- Build historical odds database
- Create odds comparison dashboard
- Develop betting models
- Track bookmaker sharp/soft markets
- Identify arbitrage opportunities

---

## 🚨 Important Notes

1. **Always run normalize AFTER snapshot collection**
   - Snapshots create raw JSON
   - Normalize processes that JSON

2. **Check the SNAPSHOT_FOLDER path**
   - Default: `snapshots/`
   - Make sure your snapshot scripts save there
   - Or update the path in normalize_odds.py

3. **CSV is the easiest format for analysis**
   - Open directly in Excel/Google Sheets
   - Load into Pandas with one line
   - Import into databases easily

4. **Fair probabilities are your edge**
   - This is what separates casual from serious betting analysis
   - Use these to find value bets
   - Compare across bookmakers

---

## 📚 Summary

**What is it?**
- Post-processing tool for odds data

**What does it do?**
- Converts odds formats
- Calculates probabilities
- Removes bookmaker vig
- Exports CSV + JSON

**Why use it?**
- Clean, analysis-ready data
- True probabilities (not bookmaker-biased)
- Easy to work with in spreadsheets
- Perfect for building betting models

**When to use it?**
- After every snapshot collection
- Before any odds analysis
- When comparing bookmakers
- When building historical databases

---

**Questions? Check the code - it's only ~100 lines and well-commented!** 🚀
