# normalize_odds.py - Quick Reference Card

## 🎯 One-Line Summary
**Converts raw odds snapshots into clean CSV/JSON with probability calculations and bookmaker vig removed**

---

## 📋 The 3-Step Workflow

```bash
# Step 1: Collect odds data
python3 snapshot_oddsapi.py snapshot --sports basketball_nba

# Step 2: Normalize the data
python3 normalize_odds.py

# Step 3: Analyze
open normalized/basketball_nba_20241115.csv
```

---

## 🔄 What It Does

### INPUT
```json
{
  "events": [{
    "id": "abc123",
    "home_team": "Lakers",
    "bookmakers": [{
      "key": "fanduel",
      "markets": [{
        "outcomes": [
          {"name": "Lakers", "price": -110}
        ]
      }]
    }]
  }]
}
```

### OUTPUT (CSV)
```csv
event_id,outcome,american_odds,decimal_odds,implied_probability,fair_probability
abc123,Lakers,-110,1.9091,0.5238,0.5119
```

---

## 📊 Key Calculations

### American → Decimal
```python
-110 → 1.9091
+150 → 2.50
```

### Implied Probability
```python
1.9091 → 52.38%
(1 / decimal_odds)
```

### Fair Probability (VIG REMOVAL) ⭐
```python
Lakers: 52.38%  ┐
Celtics: 50.00% │ Total: 102.38% (2.38% vig)
                ┘
After removal:
Lakers: 51.19%  ┐
Celtics: 48.81% │ Total: 100.00% ✓
                ┘
```

---

## 💡 Why Fair Probability Matters

### Bookmaker's Odds (With Vig)
```
Heads: -110 (52.38%)
Tails: -110 (52.38%)
Total: 104.76%  ← Bookmaker guarantees profit
```

### Fair Odds (Without Vig)
```
Heads: 50.00%
Tails: 50.00%
Total: 100.00%  ← True probabilities
```

**Value Bet = When your model's probability > fair_probability**

---

## 📁 File Structure

```
snapshots/              ← Raw data from snapshot scripts
  └── basketball_nba_20241115.json

normalize_odds.py       ← Run this after collecting snapshots

normalized/             ← Clean output for analysis
  ├── basketball_nba_20241115.json
  └── basketball_nba_20241115.csv  ← Open in Excel!
```

---

## ⚙️ Configuration

```python
# Edit these in normalize_odds.py if needed:
SNAPSHOT_FOLDER = "snapshots"       # Where raw data is
NORMALIZED_FOLDER = "normalized"    # Where to save output
```

---

## 🎓 Output Fields Explained

| Field | What It Is | Example |
|-------|------------|---------|
| **american_odds** | What you see on sportsbooks | -110 |
| **decimal_odds** | European format | 1.9091 |
| **implied_probability** | What bookmaker thinks | 52.38% |
| **fair_probability** | True probability (vig removed) | 51.19% ⭐ |

---

## 🚀 Common Use Cases

### 1. Find Best Bookmaker Odds
```python
import pandas as pd
df = pd.read_csv("normalized/nba.csv")

# Lowest implied probability = best odds
best_odds = df.groupby('outcome').apply(
    lambda x: x.nsmallest(1, 'implied_probability')
)
```

### 2. Calculate Bookmaker Edge
```python
# Average vig across all bets
df['vig'] = df['implied_probability'] - df['fair_probability']
print(f"Average bookmaker edge: {df['vig'].mean():.2%}")
```

### 3. Find Value Bets
```python
# Your model says Lakers have 55% chance
# Bookmaker says 51.19% (fair probability)
# → VALUE BET! (55% > 51.19%)
```

---

## 🔧 Troubleshooting

**"No such file or directory: snapshots/"**
- Create the folder: `mkdir snapshots`
- Or run a snapshot script first

**"No JSON files found"**
- Make sure snapshot scripts saved to `snapshots/` folder
- Check filename ends with `.json`

**"Empty output"**
- Check snapshot JSON has "events" key
- Verify format matches The Odds API structure

---

## 📚 Pro Tips

✅ **Run after every snapshot** - Keep data fresh and normalized
✅ **CSV for quick analysis** - Opens in any spreadsheet
✅ **JSON for databases** - Easy to import
✅ **Track fair_probability** - That's your edge over bookmakers
✅ **Compare bookmakers** - Find who offers best value

---

## 🎯 Remember

1. **Snapshot First** → Raw odds data
2. **Normalize Second** → Clean CSV/JSON
3. **Analyze Third** → Find value bets

**normalize_odds.py bridges the gap between raw API data and actionable insights!** 🚀

---

## Quick Command Reference

```bash
# Collect odds
python3 snapshot_oddsapi.py snapshot --sports basketball_nba

# Normalize all snapshots
python3 normalize_odds.py

# Open in spreadsheet
open normalized/*.csv

# Analyze with Python
python3
>>> import pandas as pd
>>> df = pd.read_csv("normalized/basketball_nba_20241115.csv")
>>> df.head()
```

---

**For detailed explanation, see: NORMALIZE_ODDS_EXPLAINED.md**
