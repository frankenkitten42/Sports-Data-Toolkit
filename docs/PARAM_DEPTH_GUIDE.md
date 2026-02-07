# Parameter Depth Levels - Quick Reference

Control how aggressively the API sniffer tests parameters with the `--param-depth` flag.

## Level Comparison

| Level    | API Calls/Endpoint | When to Use                          | Example                           |
|----------|-------------------|--------------------------------------|-----------------------------------|
| `none`   | 0                 | Just discover endpoints, no testing | Quick scan, very limited API quota |
| `basic`  | ~5                | Find working params for most cases   | **Default**, batch mode           |
| `full`   | ~25               | Deep analysis, all parameter combos  | Single API, unlimited quota       |

## none - Endpoint Discovery Only

**API Calls:** 0 per endpoint needing params

**What it does:**
- Probes which endpoints exist
- Shows which need parameters
- NO parameter testing

**Output:**
```
✅ Found 8 endpoints
  ✅ Ready: leagues, seasons
  📋 Needs params: teams, games, players, standings
  
  ℹ️  Parameter testing skipped (--param-depth none)
```

**Use when:**
- You have very limited API quota (<50 calls)
- Just want to see what endpoints exist
- Will test parameters manually later

---

## basic - Common Parameters (DEFAULT)

**API Calls:** ~5 per endpoint needing params

**Parameters tested:**
```python
{
    "season": [2024, 2023],
    "league": [1, 2, 12],  # 12=NBA
    "id": [1, 2],
    "team": [1, 2],
    "date": [today],
}
```

**What it does:**
- Tests most common parameters
- Single params only (no combinations)
- Enough to find working params for ~70% of endpoints

**Output:**
```
✅ Found 8 endpoints
  ✅ Ready: leagues, seasons
  📋 Needs params: teams, games, players, standings
  
  🔍 Testing parameters to get sample data... (depth: basic)
    ✅ /teams with league=12 → 30 records
       Fields: id, name, code, logo
    ✅ /games with season=2024 → 285 records
       Fields: id, date, teams, scores
    💡 Got sample data for 2/4 endpoints
    ⚠️  No working params found for: players, standings
```

**Use when:**
- Batch processing multiple APIs
- API has moderate rate limits (100-300 calls/hour)
- You want structural info without exhaustive testing
- **This is the recommended default**

---

## full - All Parameters & Combinations

**API Calls:** ~25 per endpoint needing params

**Parameters tested:**
```python
{
    "season": [2024, 2023, 2022, "2024-2025", "2023-2024"],
    "year": [2024, 2023, 2022],
    "date": [today, yesterday, last_week, "2024-01-01"],
    "league": [1, 2, 12, 39, 140],
    "team": [1, 2, 3, 10, 33, 50],
    "id": [1, 2, 3, 5, 10],
    "player": [1, 2, 3],
    # ... plus 15 more parameter types
}
```

**Plus combinations:**
- season + league
- team + season
- league + date
- team + date
- search + league

**What it does:**
- Tests all common parameters
- Tests parameter combinations
- Finds working params for ~95% of endpoints

**Output:**
```
✅ Found 8 endpoints
  📋 Needs params: teams, games, players, standings
  
  🔍 Testing parameters to get sample data... (depth: full)
    ✅ /teams with league=12 → 30 records
       Fields: id, name, code, logo, country
    ✅ /games with season=2024, league=2 → 285 records
       Fields: id, date, time, teams, scores, status
    ✅ /players with team=1, season=2024 → 53 records
       Fields: id, name, position, number, age
    ✅ /standings with season=2024, league=12 → 1 records
       Fields: league, season, standings
    💡 Got sample data for 4/4 endpoints
```

**Use when:**
- Processing 1-3 APIs only
- You have generous API limits (500+ calls/hour)
- Need complete structural documentation
- Preparing to integrate with the API

---

## Usage Examples

### Quick scan of 10 sports (no params)
```bash
python api_sniffer.py --batch all_sports.json --param-depth none -o scan.json
# Uses ~330 API calls total (33 endpoint probes × 10 sports)
```

### Default batch processing (4 sports, basic params)
```bash
python api_sniffer.py --batch american_sports.json --param-depth basic -o report.json
# Uses ~100-150 API calls (safe for most rate limits)
```

### Deep analysis of single API (full params)
```bash
python api_sniffer.py https://v1.basketball.api-sports.io \
  -H "x-apisports-key: YOUR_KEY" \
  --param-depth full \
  -o basketball_full.json
# Uses ~200-300 API calls (one sport, deep analysis)
```

---

## Recommendations by Scenario

**Scenario:** Exploring a completely new API
→ Use `--param-depth basic` first, then `full` for important endpoints

**Scenario:** Batch scan of 10+ sports
→ Use `--param-depth none` or split into groups of 3-4 with `basic`

**Scenario:** Building integration with 1-2 APIs
→ Use `--param-depth full` to get complete documentation

**Scenario:** API has strict rate limits (<100 calls/hour)
→ Use `--param-depth none`, test params manually for key endpoints

**Scenario:** Unlimited API quota (paid tier)
→ Use `--param-depth full` for everything!
