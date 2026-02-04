# Changelog

All notable changes to snapshot_apisports.py will be documented in this file.

## [1.1] - 2025-02-01

### Major Fixes

#### League Resolution & Name Matching
- **Fixed:** Script now resolves league names in addition to IDs
- **Added:** Case-insensitive partial name matching (e.g., "nba" matches "NBA")
- **Added:** Interactive disambiguation when multiple leagues match a search term
- **Impact:** Users can now use `--league NBA` instead of having to look up numeric IDs

#### API Response Structure Handling
- **Fixed:** Handling for flat vs nested league schemas
  - Flat: `{"id": 261, "name": "NBA", ...}`
  - Nested: `{"league": {"id": 261, "name": "NBA"}, ...}`
  - String: `["africa", "orlando", "sacramento"]` (NBA API quirk)
- **Added:** `extract_league_info()` function to normalize across all schemas
- **Impact:** Script works with basketball, football, NFL, and previously broken NBA endpoint

#### Season Handling
- **Fixed:** Support for both `"season"` and `"year"` keys in API responses
  - Basketball/Hockey: `{"season": "2023-2024", ...}`
  - NFL/Football: `{"year": 2024, ...}`
- **Fixed:** Cross-year season display formatting (NFL 2024 season → "2024-2025")
- **Fixed:** Sorting crash when seasons are mixed types (integers and strings)
- **Added:** `get_season_value()` and `get_season_sort_key()` helpers
- **Impact:** browse_seasons and browse_categories work for all sports

#### NFL-Specific Fixes
- **Fixed:** Handle NFL API's `"statisitcs"` typo alongside correct `"statistics"` spelling
- **Fixed:** NFL's explicit `"injuries"` boolean in coverage object
- **Fixed:** NFL `/leagues` endpoint requiring `season` parameter
- **Added:** Automatic retry with current year when leagues endpoint returns empty
- **Impact:** NFL data now fully browsable and snapshotable

#### Non-League Sports (F1, MMA)
- **Fixed:** F1 and MMA don't have `/leagues` endpoint - they use `/seasons` directly
- **Added:** Synthetic league creation for sports with seasons but no leagues
  - F1 → Creates "F1" league with all available seasons
  - MMA → Creates "MMA" league with all available seasons
- **Added:** Sport-specific category mappings:
  - F1: races, competitions, teams, circuits
  - MMA: fights, teams
- **Fixed:** Snapshot params for F1/MMA (no league param, season-only)
- **Impact:** F1 and MMA are now fully functional with proper data structure

### Breaking Changes

#### Removed Sports
- **Removed:** `nba` sport (API was misleadingly named - contained regional leagues, not NBA)
  - NBA data is available under `basketball` sport, league "NBA"
  - This was causing massive user confusion
- **Removed:** `nhl` sport (domain doesn't exist)
  - NHL data is available under `hockey` sport

#### Renamed Sports
- **Renamed:** `formula1` → `f1` (shorter, more natural)

### Improvements

#### Browse Categories Command
- **Added:** `browse categories` command to preview available data categories by league/season
- **Added:** Sport-specific category display for F1 and MMA
- **Improved:** Coverage-to-categories mapping accuracy

#### Error Handling
- **Improved:** Graceful handling of sports without `/leagues` endpoint
- **Improved:** Better error messages when league ID/name is invalid
- **Added:** Null id/name handling for edge cases
- **Fixed:** Skip logic now checks extracted values, not raw API responses

#### Help & Documentation
- **Improved:** Help text now features American sports examples (NBA, NFL, MLB, NHL)
- **Added:** F1 and MMA usage examples
- **Updated:** Examples show league name matching instead of IDs
- **Added:** Sport-specific category documentation in help

#### Code Quality
- **Added:** Comprehensive test suite (`test_sports.py`, `test_integration.py`)
- **Fixed:** Multiple duplicate dictionary keys bugs
- **Fixed:** Broken function definitions and undefined function references
- **Improved:** Consistent error handling across all browse functions

### Technical Details

#### New Functions
- `extract_league_info(league_obj, sport)` - Normalize league data across schemas
- `get_season_value(season_obj)` - Extract season identifier from any format
- `get_season_sort_key(season_obj)` - Sortable key handling mixed int/string seasons
- `format_season_display(season_obj)` - Human-readable season labels
- `get_leagues(sport, api_key, league_id)` - Unified league fetching with retries
- `get_categories_for_sport(sport)` - Sport-specific category resolution
- `resolve_league(api_key, sport, league_input)` - League name/ID resolution

#### Updated Functions
- `browse_leagues()` - Added string league handling, null filtering
- `browse_seasons()` - Added season key normalization, simple season display
- `browse_categories()` - Added sport-specific categories, synthetic league support
- `snapshot()` - Added F1/MMA param handling, auto category selection
- `coverage_to_categories()` - Added NFL typo handling, explicit injuries check

#### Constants
- Added `SPORT_SPECIFIC_CATEGORIES` mapping
- Expanded `ENDPOINT_MAP` with F1/MMA endpoints
- Updated `SPORT_URLS` (removed nba/nhl, renamed formula1→f1)

### Migration Guide (1.0 → 1.1)

#### If you were using `nba` sport:
```bash
# Old (1.0)
python snapshot_apisports.py browse leagues --sport nba

# New (1.1)
python snapshot_apisports.py browse leagues --sport basketball
python snapshot_apisports.py browse seasons --sport basketball --league NBA
```

#### If you were using `formula1`:
```bash
# Old (1.0)
python snapshot_apisports.py browse leagues --sport formula1

# New (1.1)
python snapshot_apisports.py browse leagues --sport f1
python snapshot_apisports.py browse seasons --sport f1 --league F1
```

#### If you were using numeric league IDs:
```bash
# Old (1.0)
python snapshot_apisports.py select add --sport basketball --league 261 --seasons 2024

# New (1.1) - Both work, but names are easier
python snapshot_apisports.py select add --sport basketball --league NBA --seasons 2024
```

## [1.0] - 2025-01-31

### Initial Release
- Multi-sport browser and snapshot tool
- Support for 13 sports via API-Sports
- Browse leagues, seasons functionality
- Selection management (add/show/clear)
- Snapshot data pulling
- API key management

### Known Issues (Fixed in 1.1)
- NFL data not browsable (missing season param handling)
- F1 and MMA completely broken (no league endpoint)
- NBA endpoint returned wrong data (regional leagues instead of NBA)
- League resolution required numeric IDs (no name matching)
- Mixed season types caused sort crashes
- Nested league structures not handled
- Coverage mapping incomplete
