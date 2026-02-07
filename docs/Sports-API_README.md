# API-Sports Snapshot Tool

A command-line tool for browsing and capturing sports data from API-Sports endpoints.

**Version:** 1.1  
**Released:** 2025-02-01

## Features

- Browse 11 sports with 1000+ leagues worldwide
- League name resolution (use "NBA" instead of numeric IDs)
- Season and category exploration
- Batch data collection via selections
- Support for league-based sports (NBA, NFL, MLB, etc.)
- Support for non-league sports (F1, MMA)
- Automatic handling of different API response schemas

## Supported Sports

- **afl** - Australian Football League
- **baseball** - International baseball (includes MLB)
- **basketball** - International basketball (includes NBA)
- **f1** - Formula 1 racing
- **football** - International football/soccer
- **handball** - International handball
- **hockey** - International hockey (includes NHL)
- **mma** - Mixed Martial Arts
- **nfl** - American Football (NFL, NCAA)
- **rugby** - International rugby
- **volleyball** - International volleyball

## Quick Start

### 1. Set your API key
```bash
python snapshot_apisports.py key set
```

### 2. Browse available data
```bash
# List all sports
python snapshot_apisports.py browse sports

# Find leagues for a sport
python snapshot_apisports.py browse leagues --sport basketball

# Check seasons for a league
python snapshot_apisports.py browse seasons --sport basketball --league NBA

# Preview available categories
python snapshot_apisports.py browse categories --sport nfl
```

### 3. Add selections
```bash
# Add NBA 2024-2025 season
python snapshot_apisports.py select add --sport basketball --league NBA --seasons 2024-2025

# Add NFL 2024 and 2025 seasons
python snapshot_apisports.py select add --sport nfl --league NFL --seasons 2024 2025

# Add F1 2024 season
python snapshot_apisports.py select add --sport f1 --league F1 --seasons 2024
```

### 4. Snapshot data
```bash
# Pull all categories for all selections
python snapshot_apisports.py snapshot

# Pull specific categories only
python snapshot_apisports.py snapshot --categories fixtures odds

# F1-specific categories
python snapshot_apisports.py snapshot --categories races teams
```

## Usage

### Browse Commands

```bash
# Browse sports
python snapshot_apisports.py browse sports

# Browse leagues
python snapshot_apisports.py browse leagues --sport <sport>

# Browse seasons
python snapshot_apisports.py browse seasons --sport <sport> --league <name or ID>

# Browse categories
python snapshot_apisports.py browse categories --sport <sport> [--league <name or ID>]
```

### Selection Commands

```bash
# Add selection
python snapshot_apisports.py select add --sport <sport> --league <name or ID> --seasons <season> [...]

# Show selections
python snapshot_apisports.py select show

# Clear selections
python snapshot_apisports.py select clear
```

### Snapshot Commands

```bash
# Snapshot all categories
python snapshot_apisports.py snapshot

# Snapshot specific categories
python snapshot_apisports.py snapshot --categories <cat1> <cat2> [...]

# Filter by date
python snapshot_apisports.py snapshot --date YYYY-MM-DD
```

### Key Management

```bash
# Show current key (masked)
python snapshot_apisports.py key show

# Set new key
python snapshot_apisports.py key set

# Clear saved key
python snapshot_apisports.py key clear
```

## Categories by Sport

### Traditional Sports (NBA, NFL, MLB, NHL, etc.)
- **fixtures** - Game schedules
- **odds** - Betting lines
- **lineups** - Team rosters
- **injuries** - Injury reports
- **results** - Final scores

### F1
- **races** - Race results
- **competitions** - Grand Prix events
- **teams** - Constructor information
- **circuits** - Track details

### MMA
- **fights** - Fight results
- **teams** - Fighter camps/gyms

## File Structure

Data is saved to:
```
snapshots_apisports/
  {sport}/
    {league}/
      {season}/
        {category}/
          {category}_YYYY-MM-DDTHH-MM-SS.json
```

Example:
```
snapshots_apisports/
  basketball/
    nba/
      2024-2025/
        fixtures/
          fixtures_2025-02-01T14-30-00.json
        odds/
          odds_2025-02-01T14-30-05.json
  f1/
    f1/
      2024/
        races/
          races_2025-02-01T14-35-00.json
```

## League Name Resolution

You can use league names instead of numeric IDs:

```bash
# Works with full names
python snapshot_apisports.py browse seasons --sport basketball --league "NBA"

# Works with partial names (case-insensitive)
python snapshot_apisports.py browse seasons --sport basketball --league nba

# Still works with numeric IDs
python snapshot_apisports.py browse seasons --sport basketball --league 12
```

If multiple leagues match, you'll get an interactive menu to choose.

## Testing

Run the test suite to verify all sports work correctly:

```bash
# Test API structure for all sports
python test_sports.py YOUR_API_KEY

# Integration test (runs actual commands)
python test_integration.py
```

## Requirements

- Python 3.7+
- `requests` library
- API-Sports API key

Install dependencies:
```bash
pip install requests
```

## Notes

### NBA Data Location
The API-Sports `nba` endpoint was removed in v1.1 because it was misleadingly named (contained regional leagues, not NBA data). 

**To get NBA data, use the `basketball` sport:**
```bash
python snapshot_apisports.py browse leagues --sport basketball
python snapshot_apisports.py browse seasons --sport basketball --league NBA
```

### F1 and MMA
F1 and MMA don't use traditional league structures. The tool creates synthetic "F1" and "MMA" leagues to maintain a consistent workflow.

### NHL Data
The `nhl` sport was removed because the API endpoint doesn't exist. NHL data is available under the `hockey` sport.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and migration guides.

## License

See LICENSE file for details.
