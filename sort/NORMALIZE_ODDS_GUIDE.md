# Normalize Odds - Complete Guide

**Version:** 1.0  
**Purpose:** Standardize odds data across multiple providers and formats

A tool for normalizing sports betting odds data from different providers into a unified, consistent format. Handles various odds formats, bookmaker naming conventions, and data structures.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Odds Formats](#odds-formats)
6. [Usage Examples](#usage-examples)
7. [Configuration](#configuration)
8. [Output Format](#output-format)
9. [API Reference](#api-reference)
10. [Advanced Usage](#advanced-usage)
11. [Troubleshooting](#troubleshooting)

---

## Overview

`normalize_odds.py` solves a common problem in sports data: different providers use different formats, naming conventions, and data structures for the same information. This tool:

- Converts between odds formats (American, Decimal, Fractional, Implied Probability)
- Standardizes team names and league identifiers
- Normalizes bookmaker names
- Unifies data structures across providers
- Handles missing or malformed data gracefully

### Why Normalize Odds?

**Without normalization:**
```json
// Provider A (API-Sports)
{"home_team": "Los Angeles Lakers", "odds": "-110", "format": "american"}

// Provider B (BALLDONTLIE)
{"homeTeam": "LA Lakers", "odds": 1.91, "format": "decimal"}

// Provider C (Historical CSV)
{"Home": "L.A. Lakers", "HomeOdds": "10/11"}
```

**After normalization:**
```json
{
  "home_team": "Los Angeles Lakers",
  "home_team_id": "lakers",
  "odds_american": -110,
  "odds_decimal": 1.91,
  "odds_fractional": "10/11",
  "implied_probability": 0.524,
  "provider": "api-sports"
}
```

---

## Features

### Odds Format Conversion
- ✅ **American odds** (e.g., -110, +150)
- ✅ **Decimal odds** (e.g., 1.91, 2.50)
- ✅ **Fractional odds** (e.g., 10/11, 3/2)
- ✅ **Implied probability** (e.g., 0.524, 52.4%)
- ✅ Bidirectional conversion (any format to any format)

### Data Standardization
- ✅ Team name normalization
- ✅ League/competition identifiers
- ✅ Bookmaker name standardization
- ✅ Date/time format unification
- ✅ Field name mapping

### Multi-Provider Support
- ✅ API-Sports format
- ✅ BALLDONTLIE format
- ✅ CSV historical data
- ✅ Custom formats (configurable)

### Data Quality
- ✅ Validates odds values
- ✅ Handles missing data
- ✅ Detects format errors
- ✅ Reports data quality issues
- ✅ Configurable tolerance for conversions

---

## Installation

### Requirements
```bash
# Python 3.7 or higher
python3 --version

# No external dependencies required (uses standard library)
```

### Download
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/sports-data-toolkit.git
cd sports-data-toolkit/normalization

# Or download directly
wget https://raw.githubusercontent.com/YOUR_USERNAME/sports-data-toolkit/main/normalization/normalize_odds.py
```

---

## Quick Start

### Basic Usage

```bash
# Normalize odds from a single file
python3 normalize_odds.py --input raw_odds.json --output normalized_odds.json

# Specify source provider
python3 normalize_odds.py --input raw_odds.json --provider api-sports

# Convert to specific format
python3 normalize_odds.py --input raw_odds.json --format decimal

# Process multiple files
python3 normalize_odds.py --input *.json --output normalized/
```

### Python Usage

```python
from normalize_odds import OddsNormalizer

# Initialize normalizer
normalizer = OddsNormalizer()

# Normalize single odds value
american_odds = -110
decimal = normalizer.american_to_decimal(american_odds)
print(f"Decimal: {decimal}")  # Output: 1.91

# Normalize complete data
raw_data = {
    "home_team": "LA Lakers",
    "odds": "-110",
    "provider": "api-sports"
}
normalized = normalizer.normalize(raw_data)
print(normalized)
```

---

## Odds Formats

### American Odds (Moneyline)

**Format:** Positive (+150) or Negative (-110)

**Interpretation:**
- Negative: Amount you must bet to win $100
- Positive: Amount you win if you bet $100

**Examples:**
```
-110: Bet $110 to win $100 (implied probability: 52.4%)
+150: Bet $100 to win $150 (implied probability: 40.0%)
-200: Bet $200 to win $100 (implied probability: 66.7%)
+200: Bet $100 to win $200 (implied probability: 33.3%)
```

### Decimal Odds (European)

**Format:** Decimal number ≥ 1.00

**Interpretation:**
- Total payout per $1 wagered (includes stake)

**Examples:**
```
1.91: Bet $1, get $1.91 back (profit: $0.91)
2.50: Bet $1, get $2.50 back (profit: $1.50)
1.50: Bet $1, get $1.50 back (profit: $0.50)
```

### Fractional Odds (British)

**Format:** Fraction (e.g., 10/11, 3/2)

**Interpretation:**
- Profit per unit staked

**Examples:**
```
10/11: Profit $10 for every $11 staked
3/2:   Profit $3 for every $2 staked
1/2:   Profit $1 for every $2 staked
5/1:   Profit $5 for every $1 staked
```

### Implied Probability

**Format:** Decimal between 0 and 1 (or percentage)

**Interpretation:**
- Bookmaker's implied probability of outcome

**Examples:**
```
0.524 (52.4%): Even money bet, slightly favored
0.667 (66.7%): Strong favorite
0.333 (33.3%): Underdog
```

### Conversion Examples

| American | Decimal | Fractional | Implied % |
|----------|---------|------------|-----------|
| -110     | 1.91    | 10/11      | 52.4%     |
| +150     | 2.50    | 3/2        | 40.0%     |
| -200     | 1.50    | 1/2        | 66.7%     |
| +200     | 3.00    | 2/1        | 33.3%     |
| -150     | 1.67    | 4/6        | 60.0%     |

---

## Usage Examples

### Example 1: Convert CSV Historical Data

```bash
# Input: Football-Data.co.uk CSV with multiple bookmaker odds
python3 normalize_odds.py \
  --input epl_2023.csv \
  --provider football-data-uk \
  --output normalized_epl_2023.json

# Output includes all odds formats + normalized team names
```

### Example 2: Normalize API Response

```python
from normalize_odds import OddsNormalizer

# Raw API-Sports response
api_sports_data = {
    "fixture": {
        "id": 12345,
        "date": "2024-11-15T20:00:00Z"
    },
    "teams": {
        "home": {"name": "Los Angeles Lakers"},
        "away": {"name": "Boston Celtics"}
    },
    "bookmakers": [{
        "name": "Bet365",
        "bets": [{
            "name": "Match Winner",
            "values": [
                {"value": "Home", "odd": "1.91"},
                {"value": "Away", "odd": "2.00"}
            ]
        }]
    }]
}

normalizer = OddsNormalizer()
normalized = normalizer.normalize_api_sports(api_sports_data)

# Normalized output with all formats
print(normalized["home_odds"])
# {
#   "decimal": 1.91,
#   "american": -110,
#   "fractional": "10/11",
#   "implied_probability": 0.524
# }
```

### Example 3: Batch Processing

```python
import glob
from normalize_odds import OddsNormalizer

normalizer = OddsNormalizer()

# Process all JSON files in a directory
for file in glob.glob("raw_data/*.json"):
    with open(file) as f:
        raw_data = json.load(f)
    
    normalized = normalizer.normalize(raw_data, auto_detect=True)
    
    output_file = f"normalized/{os.path.basename(file)}"
    with open(output_file, 'w') as f:
        json.dump(normalized, f, indent=2)
```

### Example 4: Merge Multiple Providers

```python
from normalize_odds import OddsNormalizer, OddsMerger

normalizer = OddsNormalizer()
merger = OddsMerger()

# Get odds from multiple providers
api_sports_odds = normalizer.normalize(api_sports_data, provider="api-sports")
balldontlie_odds = normalizer.normalize(balldontlie_data, provider="balldontlie")
historical_odds = normalizer.normalize(historical_csv, provider="football-data")

# Merge into single dataset
merged = merger.merge([api_sports_odds, balldontlie_odds, historical_odds])

# Result includes all bookmakers, all formats, consensus odds
print(merged["consensus_odds"])  # Average across all providers
```

---

## Configuration

### Config File Format

Create `odds_normalizer_config.json`:

```json
{
  "team_mappings": {
    "LA Lakers": "Los Angeles Lakers",
    "L.A. Lakers": "Los Angeles Lakers",
    "Lakers": "Los Angeles Lakers"
  },
  "league_mappings": {
    "NBA": "nba",
    "National Basketball Association": "nba"
  },
  "bookmaker_mappings": {
    "Bet 365": "bet365",
    "Bet-365": "bet365",
    "B365": "bet365"
  },
  "default_format": "decimal",
  "precision": 2,
  "validate_odds": true,
  "include_all_formats": true
}
```

### Load Configuration

```python
from normalize_odds import OddsNormalizer

normalizer = OddsNormalizer(config_file="odds_normalizer_config.json")
```

---

## Output Format

### Standard Normalized Format

```json
{
  "match_id": "unique_identifier",
  "date": "2024-11-15T20:00:00Z",
  "sport": "basketball",
  "league": "nba",
  "home_team": "Los Angeles Lakers",
  "home_team_id": "lakers",
  "away_team": "Boston Celtics",
  "away_team_id": "celtics",
  "bookmakers": [
    {
      "bookmaker": "bet365",
      "bookmaker_id": "bet365",
      "markets": {
        "match_winner": {
          "home": {
            "decimal": 1.91,
            "american": -110,
            "fractional": "10/11",
            "implied_probability": 0.524
          },
          "away": {
            "decimal": 2.00,
            "american": +100,
            "fractional": "1/1",
            "implied_probability": 0.500
          }
        },
        "spread": {
          "home": {
            "line": -2.5,
            "decimal": 1.91,
            "american": -110
          },
          "away": {
            "line": +2.5,
            "decimal": 1.91,
            "american": -110
          }
        },
        "total": {
          "over": {
            "line": 215.5,
            "decimal": 1.91,
            "american": -110
          },
          "under": {
            "line": 215.5,
            "decimal": 1.91,
            "american": -110
          }
        }
      }
    }
  ],
  "consensus": {
    "match_winner": {
      "home_decimal": 1.91,
      "away_decimal": 2.00
    }
  },
  "metadata": {
    "providers": ["api-sports", "balldontlie"],
    "normalized_at": "2024-11-15T18:30:00Z",
    "normalizer_version": "1.0"
  }
}
```

---

## API Reference

### OddsNormalizer Class

```python
class OddsNormalizer:
    def __init__(self, config_file=None):
        """Initialize normalizer with optional config file"""
        
    def american_to_decimal(self, american_odds):
        """Convert American odds to Decimal"""
        
    def decimal_to_american(self, decimal_odds):
        """Convert Decimal odds to American"""
        
    def american_to_fractional(self, american_odds):
        """Convert American odds to Fractional"""
        
    def decimal_to_fractional(self, decimal_odds):
        """Convert Decimal odds to Fractional"""
        
    def to_implied_probability(self, odds, format="decimal"):
        """Convert odds to implied probability"""
        
    def normalize(self, data, provider=None, auto_detect=False):
        """Normalize odds data from any provider"""
        
    def normalize_team_name(self, team_name):
        """Standardize team name"""
        
    def normalize_bookmaker(self, bookmaker_name):
        """Standardize bookmaker name"""
```

### Conversion Functions

```python
# American to other formats
decimal = normalizer.american_to_decimal(-110)  # 1.91
fractional = normalizer.american_to_fractional(-110)  # "10/11"
probability = normalizer.to_implied_probability(-110, "american")  # 0.524

# Decimal to other formats
american = normalizer.decimal_to_american(1.91)  # -110
fractional = normalizer.decimal_to_fractional(1.91)  # "10/11"

# Fractional to other formats
decimal = normalizer.fractional_to_decimal("10/11")  # 1.91
american = normalizer.fractional_to_american("10/11")  # -110
```

---

## Advanced Usage

### Custom Provider Format

```python
# Define custom provider format
custom_provider = {
    "name": "my_custom_api",
    "team_field": "TeamName",
    "odds_field": "Price",
    "odds_format": "decimal",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

normalizer = OddsNormalizer()
normalizer.register_provider(custom_provider)

# Now normalize data from your custom API
normalized = normalizer.normalize(raw_data, provider="my_custom_api")
```

### Validation & Quality Checks

```python
from normalize_odds import OddsValidator

validator = OddsValidator()

# Validate odds make sense
is_valid = validator.validate_odds(1.91)  # True
is_valid = validator.validate_odds(0.5)   # False (too low)
is_valid = validator.validate_odds(100)   # False (too high)

# Check for arbitrage opportunities
home_odds = 2.10
away_odds = 2.10
has_arb = validator.check_arbitrage(home_odds, away_odds)  # True (overround < 100%)

# Validate complete dataset
report = validator.validate_dataset(normalized_data)
print(report["errors"])
print(report["warnings"])
```

### Calculate Overround (Vig/Juice)

```python
from normalize_odds import calculate_overround

# Two-way market (moneyline)
home_decimal = 1.91
away_decimal = 2.00
overround = calculate_overround([home_decimal, away_decimal])
print(f"Overround: {overround}%")  # ~102.3% (bookmaker's edge)

# Three-way market (soccer)
home = 2.10
draw = 3.40
away = 3.60
overround = calculate_overround([home, draw, away])
print(f"Overround: {overround}%")  # Bookmaker's margin
```

---

## Troubleshooting

### Issue: "Invalid odds format"

```python
# Problem: Mixed formats in data
data = {"odds": "-110"}  # String instead of number

# Solution: Use strict=False
normalizer = OddsNormalizer(strict=False)
normalized = normalizer.normalize(data)
# Automatically detects and converts string to number
```

### Issue: "Team name not found in mapping"

```python
# Problem: New team variation
raw_team = "L.A Lakers"  # Different from mapping

# Solution 1: Add to config
config["team_mappings"]["L.A Lakers"] = "Los Angeles Lakers"

# Solution 2: Use fuzzy matching
normalizer = OddsNormalizer(fuzzy_matching=True, threshold=0.8)
normalized_name = normalizer.normalize_team_name("L.A Lakers")
# Matches "Los Angeles Lakers" with 80%+ similarity
```

### Issue: "Conversion precision loss"

```python
# Problem: Fractional odds lose precision
fractional = "10/11"
decimal = normalizer.fractional_to_decimal(fractional)  # 1.909090...

# Solution: Set precision
normalizer = OddsNormalizer(precision=2)
decimal = normalizer.fractional_to_decimal("10/11")  # 1.91
```

### Issue: "Provider auto-detection fails"

```python
# Problem: Can't detect provider from data structure
normalized = normalizer.normalize(data, auto_detect=True)  # Fails

# Solution: Explicitly specify provider
normalized = normalizer.normalize(data, provider="api-sports")
```

---

## Common Use Cases

### Use Case 1: Compare Odds Across Bookmakers

```python
# Get best odds for a match
bookmakers_odds = [
    {"name": "bet365", "home": 1.91, "away": 2.00},
    {"name": "pinnacle", "home": 1.95, "away": 1.98},
    {"name": "betfair", "home": 1.93, "away": 1.99}
]

best_home = max(bookmakers_odds, key=lambda x: x["home"])
best_away = max(bookmakers_odds, key=lambda x: x["away"])

print(f"Best home odds: {best_home['name']} @ {best_home['home']}")
print(f"Best away odds: {best_away['name']} @ {best_away['away']}")
```

### Use Case 2: Build Historical Database

```python
# Normalize 20 years of Football-Data.co.uk CSVs
import pandas as pd
from normalize_odds import OddsNormalizer

normalizer = OddsNormalizer()

for year in range(2000, 2024):
    df = pd.read_csv(f"raw/epl_{year}.csv")
    
    normalized_data = []
    for _, row in df.iterrows():
        normalized = normalizer.normalize_csv_row(row, provider="football-data")
        normalized_data.append(normalized)
    
    # Save to database or file
    with open(f"normalized/epl_{year}.json", 'w') as f:
        json.dump(normalized_data, f)
```

### Use Case 3: Machine Learning Training Data

```python
# Create ML-ready features from normalized odds
from normalize_odds import create_ml_features

normalized_matches = load_normalized_data()
features_df = create_ml_features(normalized_matches)

# Features include:
# - Odds in all formats
# - Implied probabilities
# - Overround
# - Odds movement (if historical)
# - Consensus odds
# - Bookmaker-specific patterns

print(features_df.head())
```

---

## Version History

### v1.0 (Current)
- Initial release
- Support for American, Decimal, Fractional formats
- API-Sports, BALLDONTLIE provider support
- CSV historical data normalization
- Team and bookmaker name mapping
- Configurable precision and validation

---

## Contributing

Contributions welcome! Key areas:
- Additional provider formats
- More sports-specific mappings
- Performance optimizations
- Additional validation rules

---

## License

Academic Free License (AAL) - See LICENSE file for details

---

**Questions?** Open an issue on GitHub or check the examples in the `examples/` directory.
