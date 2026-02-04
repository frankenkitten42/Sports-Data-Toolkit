#!/usr/bin/env python3
"""
====================================================
snapshot_apisports.py
Version: 1.1

API-Sports browser + selector + snapshot tool

Modes:
  browse   -> explore sports / leagues / seasons
  select   -> add / show / clear selections
  snapshot -> pull raw data for all active selections
  key      -> manage your API-Sports key

Designed to integrate with normalize_odds.py

Changelog: See CHANGELOG.md
====================================================
"""

import os
import sys
import json
import getpass
import requests
from pathlib import Path
from datetime import datetime, timezone

# ==================================================
# CONFIG
# ==================================================

# API-Sports uses a different base URL per sport.
# Add new sports here as needed.
# Note: "basketball" includes NBA and 400+ international leagues
SPORT_URLS = {
    "afl":        "https://v1.afl.api-sports.io",
    "baseball":   "https://v1.baseball.api-sports.io",
    "basketball": "https://v1.basketball.api-sports.io",
    "f1":         "https://v1.formula-1.api-sports.io",
    "football":   "https://v3.football.api-sports.io",
    "handball":   "https://v1.handball.api-sports.io",
    "hockey":     "https://v1.hockey.api-sports.io",
    "mma":        "https://v1.mma.api-sports.io",
    "nfl":        "https://v1.american-football.api-sports.io",
    "rugby":      "https://v1.rugby.api-sports.io",
    "volleyball": "https://v1.volleyball.api-sports.io",
}

ROOT = Path("snapshots_apisports")
CONFIG_DIR = ROOT / "config"
SELECTIONS_FILE = CONFIG_DIR / "selections.json"
KEY_FILE = Path.home() / ".apisports_key"

# Default categories for traditional league-based sports
SNAPSHOT_CATEGORIES = ["fixtures", "odds", "lineups", "injuries", "results"]

# Sport-specific categories for non-league sports
SPORT_SPECIFIC_CATEGORIES = {
    "f1": ["races", "competitions", "teams", "circuits"],
    "mma": ["fights", "teams"]
}

def get_categories_for_sport(sport):
    """Get available categories for a sport"""
    return SPORT_SPECIFIC_CATEGORIES.get(sport, SNAPSHOT_CATEGORIES)

# ==================================================
# UTILITIES
# ==================================================

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def utc_ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

def pretty(obj):
    print(json.dumps(obj, indent=2))

def available_sports():
    return sorted(SPORT_URLS.keys())

def get_season_value(season_obj):
    """
    Pull the season identifier out of a season object regardless of
    which key the API used. Handles:
      {"season": "2023-2024", ...}   -> "2023-2024"
      {"season": 2024, ...}          -> 2024
      {"year": 2024, ...}            -> 2024
      bare int or string             -> returned as-is
    
    Returns the raw value (int or str).
    """
    if isinstance(season_obj, dict):
        return season_obj.get("season") or season_obj.get("year") or 0
    return season_obj

def get_season_sort_key(season_obj):
    """
    Get a sortable key for a season. Always returns a string to handle
    mixed int/string season values (some leagues use 2024, others "2023-2024").
    """
    val = get_season_value(season_obj)
    # Convert to string for consistent comparison
    # Pad integers to ensure proper sorting (2024 -> "2024", not "24")
    if isinstance(val, int):
        return f"{val:04d}"
    return str(val)

def format_season_display(season_obj):
    """
    Build a human-readable season label. For cross-year seasons
    (where start and end fall in different calendar years), shows
    the range. Otherwise just shows the season/year value.
      {"year": 2024, "start": "2024-08-02", "end": "2025-02-09"} -> "2024-2025"
      {"season": "2023-2024", ...}                                -> "2023-2024"
      {"season": 2024, "start": "2024-01-01", "end": "2024-12-31"} -> "2024"
    """
    if not isinstance(season_obj, dict):
        return str(season_obj)

    val = get_season_value(season_obj)
    start = season_obj.get("start", "")
    end = season_obj.get("end", "")

    # If we have both dates and they span different years, show range
    if start and end:
        start_year = start[:4]
        end_year = end[:4]
        if start_year != end_year:
            return f"{start_year}-{end_year}"

    return str(val)

def extract_league_info(league_obj, sport=None):
    """
    Pull (id, name) out of a league object regardless of API schema.
    Handles:
      - Flat:   {"id": 261, "name": "NBA", ...}
      - Nested: {"league": {"id": 261, "name": "NBA"}, ...}
      - Null:   {"id": null, "name": null, ...} — falls back to sport + type
      - String: "africa" — NBA API returns strings instead of objects
    Returns (id, name) or (None, None) if nothing usable is found.
    """
    # Handle string leagues (NBA API)
    if isinstance(league_obj, str):
        return 0, league_obj
    
    # Handle dict leagues (all other sports)
    if not isinstance(league_obj, dict):
        return None, None
    
    lid = league_obj.get("id")
    lname = league_obj.get("name")

    # If flat keys are null, check for a nested "league" object
    if lid is None or lname is None:
        nested = league_obj.get("league", {}) or {}
        lid = lid if lid is not None else nested.get("id")
        lname = lname if lname is not None else nested.get("name")

    # Still null — build a fallback from sport + type
    if lid is None or lname is None:
        league_type = league_obj.get("type", "unknown")
        lid = lid if lid is not None else 0
        lname = lname if lname is not None else f"{sport or 'unknown'} ({league_type})"

    return lid, lname

# ==================================================
# API KEY MANAGEMENT
# ==================================================

def get_api_key():
    env_key = os.environ.get("APISPORTS_KEY")
    if env_key:
        return env_key.strip()

    if KEY_FILE.exists():
        key = KEY_FILE.read_text().strip()
        if key:
            return key

    key = getpass.getpass("Enter API-Sports key: ").strip()
    if not key:
        raise RuntimeError("API key required")

    KEY_FILE.write_text(key + "\n")
    print(f"✅ API key saved to {KEY_FILE}")
    return key

def show_api_key():
    if not KEY_FILE.exists():
        print("❌ No API key saved")
        return

    key = KEY_FILE.read_text().strip()
    if not key:
        print("❌ API key file is empty")
        return

    masked = key[:4] + "…" + key[-4:]
    print(f"🔑 Stored API-Sports key: {masked}")

def set_api_key():
    key = getpass.getpass("Enter new API-Sports key: ").strip()
    if not key:
        print("❌ No key entered")
        return

    KEY_FILE.write_text(key + "\n")
    print(f"✅ API key saved to {KEY_FILE}")

def clear_api_key():
    if KEY_FILE.exists():
        KEY_FILE.unlink()
        print("🗑️  API key cleared")
    else:
        print("ℹ️  No API key to clear")

# ==================================================
# API CORE
# ==================================================

def get_base_url(sport):
    sport = sport.lower()
    if sport not in SPORT_URLS:
        print(f"❌ Unknown sport: {sport}")
        print(f"   Available: {', '.join(available_sports())}")
        sys.exit(1)
    return SPORT_URLS[sport]

def api_get(sport, endpoint, api_key, params=None):
    base_url = get_base_url(sport)
    headers = {"x-apisports-key": api_key}
    r = requests.get(
        f"{base_url}/{endpoint}",
        headers=headers,
        params=params or {},
        timeout=20
    )
    r.raise_for_status()
    return r.json()

def get_leagues(sport, api_key, league_id=None):
    """
    Fetch leagues for a sport. Some sports (NFL, etc.) require a season
    parameter or return empty results. This handles the retry logic.
    
    For sports without /leagues but with /seasons (F1, MMA), creates a
    synthetic league entry using the sport itself as the league.
    
    If league_id is provided, fetches that specific league.
    Otherwise fetches all leagues for the sport.
    
    Note: Some sports (formula1, mma) don't have a /leagues endpoint.
    """
    params = {}
    if league_id is not None:
        params["id"] = league_id
    
    # Try without season first
    data = api_get(sport, "leagues", api_key, params)
    
    # Check if endpoint doesn't exist
    if data.get("errors") and "endpoint" in str(data.get("errors")):
        # Try /seasons endpoint instead (F1, MMA)
        try:
            seasons_data = api_get(sport, "seasons", api_key, {})
            seasons = seasons_data.get("response", [])
            
            if seasons:
                # Create synthetic league entry
                sport_name = sport.upper()
                synthetic_league = {
                    "id": 1,
                    "name": sport_name,
                    "seasons": [{"season": s} for s in seasons]
                }
                return [synthetic_league]
        except:
            pass
        
        return []
    
    leagues = data.get("response", [])
    
    # If empty and we didn't specify a league ID, retry with current year
    if not leagues and league_id is None:
        current_year = datetime.now().year
        params["season"] = current_year
        data = api_get(sport, "leagues", api_key, params)
        leagues = data.get("response", [])
    
    return leagues

# ==================================================
# LEAGUE RESOLUTION
# ==================================================

def resolve_league(api_key, sport, league_input):
    """
    Takes a league name or ID string and resolves it to (id, name).
    Matching is case-insensitive and partial — e.g. "nba" matches "NBA".
    If multiple leagues match, shows them and asks the user to pick.
    """
    leagues = get_leagues(sport, api_key)

    matches = []
    for item in leagues:
        lid, lname = extract_league_info(item, sport)

        # Skip if extraction failed (shouldn't happen)
        if lid is None and lname is None:
            continue

        # Match by exact ID
        if league_input.isdigit() and int(league_input) == lid:
            return lid, lname

        # Match by partial name (case-insensitive)
        if league_input.lower() in lname.lower():
            matches.append((lid, lname))

    if not matches:
        print(f"❌ No leagues matching '{league_input}' in {sport}")
        print(f"   Run `browse leagues --sport {sport}` to see available leagues")
        return None, None

    if len(matches) == 1:
        return matches[0]

    # Multiple matches — show them and let user pick
    print(f"\n🔍 Multiple leagues match '{league_input}':")
    print("=" * 45)
    for i, (lid, name) in enumerate(matches, 1):
        print(f"  {i}.  {name} (ID: {lid})")

    try:
        choice = int(input("\n  Pick a number: ")) - 1
        if 0 <= choice < len(matches):
            return matches[choice]
    except (ValueError, EOFError, KeyboardInterrupt):
        pass

    print("❌ Invalid selection")
    return None, None

# ==================================================
# BROWSE MODE
# ==================================================

def browse_sports():
    print("\n🏟️  Available Sports")
    print("=" * 45)
    for sport in available_sports():
        print(f"  {sport}")
    print(f"\n  Total: {len(SPORT_URLS)} sports")

def browse_leagues(api_key, sport):
    if not sport:
        print("❌ --sport is required")
        print(f"   Available: {', '.join(available_sports())}")
        return

    print(f"\n🏟️  Leagues for: {sport}")
    print("=" * 45)
    leagues = get_leagues(sport, api_key)
    
    if not leagues:
        print(f"  ⚠️  No leagues found. This sport may not have a /leagues endpoint.")
        print(f"  Total: 0 leagues")
        return
    
    shown = 0
    for league in leagues:
        lid, lname = extract_league_info(league, sport)

        # Skip only if extraction failed completely (shouldn't happen)
        if lid is None and lname is None:
            continue

        # String leagues (NBA) don't have country info
        if isinstance(league, str):
            print(f"  {lid:>5}  {lname}")
        else:
            country = (league.get("country") or {}).get("name", "Unknown")
            print(f"  {lid:>5}  {lname} ({country})")
        shown += 1

    print(f"\n  Total: {shown} leagues")

def browse_seasons(api_key, sport, league_input):
    if not sport:
        print("❌ --sport is required")
        print(f"   Available: {', '.join(available_sports())}")
        return
    
    if league_input is None:
        print("❌ --league is required")
        print("   Run `browse leagues --sport <sport>` to find leagues")
        return

    league_id, league_name = resolve_league(api_key, sport, league_input)
    if league_id is None:
        return

    print(f"\n📅 Seasons for {league_name} ({sport})")
    print("=" * 45)
    leagues = get_leagues(sport, api_key, league_id)
    if not leagues:
        print("  ❌ League not found")
        return

    # String leagues don't have seasons data
    if isinstance(leagues[0], str):
        print("  ⚠️  This league doesn't provide season/category data")
        print("  Total: 0 seasons")
        return

    seasons = sorted(
        leagues[0].get("seasons", []),
        key=get_season_sort_key,
        reverse=True
    )

    for s in seasons:
        label = format_season_display(s)
        
        # Check if season has coverage data (league-based sports)
        if isinstance(s, dict) and "coverage" in s:
            coverage = s.get("coverage", {})
            tags = []
            if coverage.get("odds", False):
                tags.append("odds")
            if coverage.get("standings", False):
                tags.append("standings")
            if coverage.get("players", False):
                tags.append("players")
            if coverage.get("injuries", False):
                tags.append("injuries")

            tag_str = f"  [{', '.join(tags)}]" if tags else ""
            
            # Only show dates if they exist
            if isinstance(s, dict) and "start" in s and "end" in s:
                print(f"  {label:12}  {s['start']} → {s['end']}{tag_str}")
            else:
                print(f"  {label:12}{tag_str}")
        else:
            # Simple season (F1, MMA) - just show the year
            print(f"  {label:12}")

    print(f"\n  Total: {len(seasons)} seasons")

def coverage_to_categories(coverage):
    """
    Map the API coverage object to our snapshot category names.
    Handles schema differences across sports:

      Basketball/Hockey:
        coverage.games                        -> fixtures, results
        coverage.games.statistics.players     -> lineups
        coverage.odds                         -> odds
        coverage.standings                    -> standings
        coverage.players                      -> players, injuries (inferred)

      NFL:
        coverage.games                        -> fixtures, results
        coverage.games.statisitcs.players     -> lineups  (note: API typo)
        coverage.injuries                     -> injuries (explicit boolean)
        coverage.standings                    -> standings
        coverage.players                      -> players
    """
    categories = []

    games = coverage.get("games", {})
    if games:
        categories.append("fixtures")
        categories.append("results")

    # Injuries: NFL has it as an explicit top-level boolean.
    # Other sports don't list it — infer from players being available.
    if coverage.get("injuries", False):
        categories.append("injuries")
    elif coverage.get("players", False) and "injuries" not in coverage:
        categories.append("injuries")

    if coverage.get("odds", False):
        categories.append("odds")

    # Lineups: check both correct spelling and NFL's API typo
    stats = games.get("statistics") or games.get("statisitcs") or {}
    if stats.get("players", False):
        categories.append("lineups")

    if coverage.get("standings", False):
        categories.append("standings")

    if coverage.get("players", False):
        categories.append("players")

    return categories

def browse_categories(api_key, sport, league_input=None):
    if not sport:
        print("❌ --sport is required (limits API calls to one sport at a time)")
        print(f"   Available: {', '.join(available_sports())}")
        return

    # If a specific league was given, resolve it and fetch just that one
    if league_input:
        lid, lname = resolve_league(api_key, sport, league_input)
        if lid is None:
            return
        leagues_to_show = get_leagues(sport, api_key, lid)
    else:
        # Pull all leagues — seasons are already included in the response
        leagues_to_show = get_leagues(sport, api_key)
    
    # Check if sport has no data at all
    if not leagues_to_show:
        print(f"\n⚠️  {sport.upper()} doesn't have accessible data")
        print(f"   This sport may not be supported by the API.")
        print(f"   Total: 0 leagues")
        return

    print(f"\n📂 Categories for: {sport}")
    print("=" * 55)
    
    # Sport-specific category mappings for non-league sports
    SPORT_CATEGORIES = {
        "f1": ["races", "competitions", "teams", "circuits"],
        "mma": ["fights", "teams"]
    }

    for league in leagues_to_show:
        lid, lname = extract_league_info(league, sport)

        # Skip if extraction failed (shouldn't happen)
        if lid is None and lname is None:
            continue

        # String leagues don't have seasons data attached
        if isinstance(league, str):
            print(f"\n  {lname} ({lid})")
            print(f"  {'-' * 51}")
            print(f"    (No season/category data available for this league)")
            continue

        raw_seasons = league.get("seasons", [])
        if not raw_seasons:
            continue

        seasons = sorted(raw_seasons, key=get_season_sort_key, reverse=True)

        print(f"\n  {lname} ({lid})")
        print(f"  {'-' * 51}")

        for s in seasons:
            label = format_season_display(s)

            # Check if this is a synthetic league (F1, MMA)
            if sport in SPORT_CATEGORIES:
                categories = SPORT_CATEGORIES[sport]
                cat_str = "  ".join(categories)
                print(f"    {label:12}  {cat_str}")
            elif isinstance(s, dict):
                categories = coverage_to_categories(s.get("coverage", {}))
                cat_str = "  ".join(categories) if categories else "(no coverage data)"
                print(f"    {label:12}  {cat_str}")
            else:
                print(f"    {label:12}  (no coverage data)")

    print(f"\n  💡 Use `select add` to add leagues and seasons to your selections")

# ==================================================
# SELECT MODE
# ==================================================

def load_selections():
    if not SELECTIONS_FILE.exists():
        return []
    text = SELECTIONS_FILE.read_text().strip()
    if not text:
        return []
    return json.loads(text)

def save_selections(selections):
    ensure_dir(CONFIG_DIR)
    SELECTIONS_FILE.write_text(json.dumps(selections, indent=2))

def selection_exists(selections, sport, league_id, season):
    for s in selections:
        if (s["sport"] == sport
                and s["league"]["id"] == league_id
                and s["season"] == season):
            return True
    return False

def add_selection(sport, league_id, league_name, seasons):
    selections = load_selections()
    added = 0

    for season in seasons:
        if selection_exists(selections, sport, league_id, season):
            print(f"  ⚠️  {sport} / {league_name} / {season} already selected")
            continue

        selections.append({
            "sport": sport,
            "league": {
                "id": league_id,
                "name": league_name
            },
            "season": season,
            "added_at": utc_ts()
        })
        added += 1
        print(f"  ✅ Added: {sport} / {league_name} / {season}")

    save_selections(selections)
    print(f"\n📋 {added} selection(s) added. Total active: {len(selections)}")

def show_selections():
    selections = load_selections()
    if not selections:
        print("📋 No active selections. Run `select add` to add some.")
        return

    print("\n📋 Active Selections")
    print("=" * 45)
    for i, s in enumerate(selections, 1):
        print(f"  {i}.  {s['sport']} / {s['league']['name']} / {s['season']}")
    print(f"\n  Total: {len(selections)} selection(s)")

def clear_selections():
    if SELECTIONS_FILE.exists():
        SELECTIONS_FILE.unlink()
        print("🗑️  All selections cleared")
    else:
        print("ℹ️  No selections to clear")

# ==================================================
# SNAPSHOT MODE
# ==================================================

# Map category names to API endpoints
# Traditional sports use "games" for fixtures/results
# F1 and MMA have direct 1:1 mappings
ENDPOINT_MAP = {
    # Traditional sports
    "fixtures": "games",
    "odds":     "odds",
    "lineups":  "lineups",
    "injuries": "injuries",
    "results":  "games",
    # F1
    "races":        "races",
    "competitions": "competitions",
    "circuits":     "circuits",
    # F1 and MMA
    "teams":   "teams",
    # MMA
    "fights":  "fights",
}

def snapshot(api_key, categories, date=None):
    selections = load_selections()
    if not selections:
        print("❌ No active selections. Run `select add` first.")
        return

    print(f"\n📥 Snapshotting {len(selections)} selection(s)")
    print("=" * 45)

    for sel in selections:
        sport = sel["sport"]
        league_id = sel["league"]["id"]
        league_name = sel["league"]["name"]
        season = sel["season"]
        
        # Use sport-specific categories if default categories were passed
        # (user didn't specify --categories)
        sport_categories = get_categories_for_sport(sport)
        active_categories = categories if categories != SNAPSHOT_CATEGORIES else sport_categories

        for category in active_categories:
            # Check if category is valid for this sport
            if category not in ENDPOINT_MAP:
                print(f"\n  ⚠️  Unknown category '{category}' - skipping")
                continue
            
            # F1 and MMA don't use league param (synthetic league)
            if sport in SPORT_SPECIFIC_CATEGORIES:
                params = {"season": season}
            else:
                params = {
                    "league": league_id,
                    "season": season,
                }

            if date:
                params["date"] = date

            if category == "results":
                params["status"] = "FT"

            endpoint = ENDPOINT_MAP[category]

            print(f"\n  📥 {sport} / {league_name} / {season} / {category}")

            try:
                data = api_get(sport, endpoint, api_key, params)
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                continue

            out_dir = (
                ROOT /
                sport /
                league_name.lower().replace(" ", "_") /
                str(season) /
                category
            )
            ensure_dir(out_dir)

            out_file = out_dir / f"{category}_{utc_ts()}.json"
            out_file.write_text(json.dumps(data, indent=2))

            records = len(data.get("response", []))
            print(f"  ✅ {records} records → {out_file}")

    print("\n🎯 Snapshot complete.")

# ==================================================
# HELP
# ==================================================

def print_help():
    print(f"""
API-Sports Snapshot Tool
========================

Usage:
  python snapshot_apisports.py <command> [options]

Commands:
  browse <what>            Explore available data
  select <action>          Manage your active selections
  snapshot [options]       Pull data for all active selections
  key <action>             Manage your API key

Browse:
  browse sports            List all supported sports
  browse leagues           List leagues for a sport
  browse seasons           List seasons for a league
  browse categories        Show available data categories by league/season

Browse Options:
  --sport <sport>          Required for leagues, seasons, and categories
  --league <name or ID>    Optional for categories. Required for seasons.
                           Accepts a league name or ID — partial name
                           matching is supported (e.g. "nba" matches "NBA")

Select Actions:
  select add               Add a sport/league/season to your selections
  select show              Show all active selections
  select clear             Clear all selections

Select Options (for add):
  --sport <sport>          Sport name (required)
  --league <name or ID>    League name or ID (required)
  --seasons <s> [...]      One or more seasons (required)

Snapshot Options:
  --categories <cat> [...]  Categories to pull (default: all available for each sport)
                            Traditional sports: {', '.join(SNAPSHOT_CATEGORIES)}
                            F1: races, competitions, teams, circuits
                            MMA: fights, teams
  --date <YYYY-MM-DD>       Filter by date (optional)

Key Actions:
  key show                 Show saved key (masked)
  key set                  Save a new API key
  key clear                Delete saved API key

Supported Sports:
  {', '.join(available_sports())}

Examples:
  # Browse available sports
  python snapshot_apisports.py browse sports
  
  # Find NBA in basketball leagues
  python snapshot_apisports.py browse leagues --sport basketball
  python snapshot_apisports.py browse seasons --sport basketball --league NBA
  
  # Check NFL seasons and categories
  python snapshot_apisports.py browse categories --sport nfl
  python snapshot_apisports.py browse seasons --sport nfl --league NFL
  
  # Add selections for tracking
  python snapshot_apisports.py select add --sport basketball --league NBA --seasons 2023-2024 2024-2025
  python snapshot_apisports.py select add --sport nfl --league NFL --seasons 2024 2025
  python snapshot_apisports.py select add --sport baseball --league MLB --seasons 2024
  python snapshot_apisports.py select add --sport hockey --league NHL --seasons 2023-2024
  python snapshot_apisports.py select add --sport f1 --league F1 --seasons 2024 2025
  python snapshot_apisports.py select add --sport mma --league MMA --seasons 2024
  
  # Pull data
  python snapshot_apisports.py snapshot
  python snapshot_apisports.py snapshot --categories fixtures odds
  python snapshot_apisports.py snapshot --categories races teams  # F1 specific
  python snapshot_apisports.py snapshot --categories results --date 2024-12-15
""")

# ==================================================
# MAIN
# ==================================================

def main():
    ensure_dir(ROOT)

    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1]

    # --- key subcommand ---
    if cmd == "key":
        if len(sys.argv) < 3:
            print("Usage: key [show|set|clear]")
            return

        action = sys.argv[2]
        if action == "show":
            show_api_key()
        elif action == "set":
            set_api_key()
        elif action == "clear":
            clear_api_key()
        else:
            print(f"Unknown key command: {action}")
            print("Usage: key [show|set|clear]")
        return

    # --- browse subcommand ---
    if cmd == "browse":
        if len(sys.argv) < 3:
            print("Usage: browse [sports|leagues|seasons|categories]")
            return

        what = sys.argv[2]

        if what == "sports":
            browse_sports()
            return

        # Parse optional flags
        sport = None
        league_input = None
        args = sys.argv[3:]
        i = 0
        while i < len(args):
            if args[i] == "--sport" and i + 1 < len(args):
                sport = args[i + 1]
                i += 2
            elif args[i] == "--league" and i + 1 < len(args):
                league_input = args[i + 1]
                i += 2
            else:
                i += 1

        api_key = get_api_key()

        if what == "leagues":
            browse_leagues(api_key, sport)
        elif what == "seasons":
            browse_seasons(api_key, sport, league_input)
        elif what == "categories":
            browse_categories(api_key, sport, league_input)
        else:
            print(f"Unknown browse target: {what}")
            print("Usage: browse [sports|leagues|seasons|categories]")
        return

    # --- select subcommand ---
    if cmd == "select":
        if len(sys.argv) < 3:
            print("Usage: select [add|show|clear]")
            return

        action = sys.argv[2]

        if action == "show":
            show_selections()
            return

        if action == "clear":
            clear_selections()
            return

        if action == "add":
            sport = None
            league_input = None
            seasons = []

            args = sys.argv[3:]
            i = 0
            while i < len(args):
                if args[i] == "--sport" and i + 1 < len(args):
                    sport = args[i + 1]
                    i += 2
                elif args[i] == "--league" and i + 1 < len(args):
                    league_input = args[i + 1]
                    i += 2
                elif args[i] == "--seasons":
                    i += 1
                    while i < len(args) and not args[i].startswith("--"):
                        seasons.append(args[i])
                        i += 1
                else:
                    i += 1

            # Validate required fields
            missing = []
            if not sport:
                missing.append("--sport")
            if not league_input:
                missing.append("--league")
            if not seasons:
                missing.append("--seasons")

            if missing:
                print(f"❌ Missing required flags: {', '.join(missing)}")
                print("Usage: select add --sport <sport> --league <name or ID> --seasons <season> [...]")
                return

            api_key = get_api_key()
            league_id, league_name = resolve_league(api_key, sport, league_input)
            if league_id is None:
                return

            add_selection(sport, league_id, league_name, seasons)
            return

        print(f"Unknown select action: {action}")
        print("Usage: select [add|show|clear]")
        return

    # --- snapshot subcommand ---
    if cmd == "snapshot":
        categories = SNAPSHOT_CATEGORIES
        date = None

        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--categories":
                categories = []
                i += 1
                while i < len(args) and not args[i].startswith("--"):
                    # Check if category is valid (in ENDPOINT_MAP)
                    if args[i] in ENDPOINT_MAP:
                        categories.append(args[i])
                    else:
                        print(f"❌ Unknown category: {args[i]}")
                        all_categories = sorted(set(SNAPSHOT_CATEGORIES + 
                                                   [c for cats in SPORT_SPECIFIC_CATEGORIES.values() for c in cats]))
                        print(f"   Options: {', '.join(all_categories)}")
                        return
                    i += 1
            elif args[i] == "--date" and i + 1 < len(args):
                date = args[i + 1]
                i += 2
            else:
                i += 1

        if not categories:
            print("❌ No valid categories specified")
            all_categories = sorted(set(SNAPSHOT_CATEGORIES + 
                                       [c for cats in SPORT_SPECIFIC_CATEGORIES.values() for c in cats]))
            print(f"   Options: {', '.join(all_categories)}")
            return

        api_key = get_api_key()
        snapshot(api_key, categories, date)
        return

    # --- unrecognized ---
    print(f"Unknown command: {cmd}")
    print_help()


if __name__ == "__main__":
    main()
