# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-04

### Added

#### api_sniffer.py v2.0 (NEW TOOL)
- **Parameter depth levels** - Control API call usage with 3 levels:
  - `none`: Endpoint discovery only (0 calls/endpoint)
  - `basic`: Common parameters (5 calls/endpoint) - DEFAULT
  - `full`: All parameters + combinations (25 calls/endpoint)
- **Batch processing mode** - Process multiple APIs from single config file
- **Dual output format** - JSON for code + human-readable summary for review
- **22 test parameters** - Comprehensive parameter testing with smart combinations
- **Visual feedback** - Clear status icons (✅📋⚠️❌) for endpoint states
- **Rate limit awareness** - Built-in guidance for managing API quotas
- **Auto-help display** - Shows help when run with no arguments
- **Batch config templates** - Generate example configs with `--batch-template`

#### Documentation
- Added `API_SNIFFER_GUIDE.md` - Complete usage guide for api_sniffer.py
- Added `PARAM_DEPTH_GUIDE.md` - Detailed parameter depth level reference
- Added batch configuration examples:
  - `apisports_batch.json` - All 11 sports
  - `apisports_batch_american.json` - 4 American sports
  - `apisports_batch_international.json` - 4 International sports

### Changed

#### snapshot_apisports.py v1.0 → v1.1
- **NFL fixes**:
  - Fixed season parameter handling (now properly sends `season` param)
  - Improved error messages for missing season requirements
- **NBA fixes**:
  - Fixed endpoint configuration (removed incorrect `league_id` parameter)
  - Now correctly returns NBA data instead of regional leagues
- **Formula 1 support**:
  - Added handling for non-traditional data hierarchy
  - Support for races, circuits, and F1-specific structure
- **MMA support**:
  - Added support for fight-based data structure
  - Handles events, fighters, and bout data
- **Data handling improvements**:
  - Enhanced normalization for mixed data types
  - Better error handling for inconsistent API responses
  - Improved handling of empty/null responses across sports

#### Documentation
- Updated README.md with both tools
- Added version information to all files
- Improved inline code documentation

### Fixed
- NFL: Season parameter now properly included in API requests
- NBA: Endpoint configuration corrected to return actual NBA data
- Mixed data types: Better handling of integer/string inconsistencies
- Error messages: More descriptive output for debugging

---

## [1.0.0] - 2026-02-03

### Added

#### snapshot_apisports.py v1.0 (Initial Release)
- Multi-sport data collection tool
- Support for sports: Basketball (NBA), American Football (NFL), Formula 1, MMA
- Collection types: leagues, seasons, games, teams, players, standings
- Command-line interface with clear options
- JSON output with clean formatting
- Error handling and validation
- API-Sports.io integration

#### Features
- Flexible sport selection via command-line
- League and season filtering
- Multiple collection types per run
- Automatic data structure handling
- Pretty-printed JSON output
- Response metadata tracking

---

## Version Comparison

| Version | Tools | Key Features |
|---------|-------|--------------|
| v2.0.0  | api_sniffer.py v2.0<br>snapshot_apisports.py v1.1 | API discovery, batch mode, parameter depth levels, NFL/NBA/F1/MMA fixes |
| v1.0.0  | snapshot_apisports.py v1.0 | Multi-sport data collection, JSON output |

---

## Upgrade Guide

### From v1.0.0 to v2.0.0

#### snapshot_apisports.py Users
No breaking changes! Your existing commands will work the same, but you'll get:
- Better NFL data collection (automatic season handling)
- Correct NBA endpoint behavior
- F1 and MMA support

**Before (v1.0):**
```bash
python3 snapshot_apisports.py basketball --key KEY --leagues 12 --seasons 2024
```

**After (v1.1) - Same command, better results:**
```bash
python3 snapshot_apisports.py basketball --key KEY --leagues 12 --seasons 2024
```

#### New Tool: api_sniffer.py
Use before running snapshot to understand API structure:

```bash
# Discover API structure first
python3 api_sniffer.py https://v1.basketball.api-sports.io \
  -H "x-apisports-key: YOUR_KEY" \
  --param-depth basic

# Then collect data with snapshot
python3 snapshot_apisports.py basketball --key YOUR_KEY --leagues 12 --seasons 2024
```

---

## Roadmap

### Planned for v2.1
- [ ] Add more sports to snapshot_apisports.py (Rugby, Volleyball, etc.)
- [ ] Add data export formats (CSV, Excel) to snapshot tool
- [ ] Improve api_sniffer parameter guessing for sport-specific endpoints
- [ ] Add caching to api_sniffer for large batch runs

### Planned for v3.0
- [ ] Unified data collection + discovery workflow
- [ ] Database export support
- [ ] Scheduled data collection (cron-like)
- [ ] Data validation and quality checks

---

## Contributors

- David - Creator and maintainer

---

## Links

- [GitHub Repository](https://github.com/YOUR_USERNAME/YOUR_REPO)
- [API-Sports Documentation](https://api-sports.io/documentation)
- [Issue Tracker](https://github.com/YOUR_USERNAME/YOUR_REPO/issues)
