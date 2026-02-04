#!/usr/bin/env python3

# ============================================================
# Snapshot OddsAPI Script
# Version: 1.1
#
# Description:
#   Production-ready snapshot
#   The Odds API. Supports:
#     - Multi-sport odds snapshots
#     - JSON
#     - API key management (set/show/clear)
#     - Doctor command for key & quota validation
#
# Environment:
#   - Python 3.10+
#   - Designed for Termux / Linux (aarch64 friendly)
#
# Author:
#   David Smiley
#
# Status:
#   Stable – V1.0 baseline
#
# Copyright (c) 2026 David Smiley
# ============================================================

import os
import sys
import json
import time
import getpass
import requests
import argparse
from datetime import datetime, timezone
from pathlib import Path

# =========================
# Config
# =========================

BASE_URL = "https://api.the-odds-api.com/v4"
DEFAULT_REGIONS = "us"
DEFAULT_MARKETS = "h2h,spreads,totals"

DATA_DIR = Path("snapshots_oddsapi")
KEY_FILE = Path.home() / ".oddsapi_key"

# =========================
# Filesystem Safety
# =========================

def ensure_directories():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)

# =========================
# API Key Handling
# =========================

def get_api_key():
    # 1️⃣ Environment variable always wins
    env_key = os.getenv("ODDS_API_KEY")
    if env_key:
        return env_key.strip()

    # 2️⃣ Load from file if present
    if KEY_FILE.exists():
        key = KEY_FILE.read_text().strip()
        if len(key) > 64:
            raise RuntimeError(
                "API key looks corrupted (too long). "
                "Reset API key with: python snapshot_oddsapi.py key set"
            )
        if key:
            return key

    # 3️⃣ Prompt user once
    print("🔑 OddsAPI key not found.")
    api_key = getpass.getpass("Enter OddsAPI key: ").strip()

    if not api_key:
        raise RuntimeError("No API key provided")

    # 4️⃣ OVERWRITE — never append
    KEY_FILE.write_text(api_key + "\n")
    print(f"✅ API key saved to {KEY_FILE}")
    return api_key

# =========================
# Helper Functions
# =========================

def clear_api_key():
    if KEY_FILE.exists():
        KEY_FILE.unlink()
        print("🗑️  API key cleared")
    else:
        print("ℹ️  No API key to clear")

def set_api_key():
    api_key = getpass.getpass("Enter new OddsAPI key: ").strip()
    if not api_key:
        print("❌ No key entered")
        return

    KEY_FILE.write_text(api_key + "\n")
    print(f"✅ API key saved to {KEY_FILE}")

def show_api_key():
    if not KEY_FILE.exists():
        print("❌ No API key saved")
        return

    key = KEY_FILE.read_text().strip()
    if not key:
        print("❌ API key file is empty")
        return

    masked = key[:4] + "…" + key[-4:]
    print(f"🔑 Stored OddsAPI key: {masked}")

# =========================
# Doctor Command
# =========================

def doctor_oddsapi(api_key):
    print("🩺 OddsAPI Doctor Check")
    print("=" * 45)

    url = f"{BASE_URL}/sports"
    params = {"apiKey": api_key}

    try:
        resp = requests.get(url, params=params, timeout=10)
    except Exception as e:
        print("❌ Network error:", e)
        print("\n💡 Check your internet connection and try again.")
        return

    print(f"HTTP Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ API key invalid or request rejected")
        print(resp.text[:500])
        print("\n💡 To fix your key, run:")
        print("     python snapshot_oddsapi.py key set")
        return

    remaining = resp.headers.get("x-requests-remaining")
    used = resp.headers.get("x-requests-used")

    print("\n📊 API Usage")
    if used:
        print(f"  Used:      {used}")
    if remaining:
        print(f"  Remaining: {remaining}")
    if not used and not remaining:
        print("  (No usage headers returned)")

    print("\n✅ API key is valid")
    print(f"🕒 Checked at {datetime.now(timezone.utc).isoformat()}")


# =========================
# List Sports
# =========================


def list_available_sports(api_key):
    url = f"{BASE_URL}/sports"
    resp = requests.get(url, params={"apiKey": api_key})
    resp.raise_for_status()

    sports = resp.json()

    print("\n🏟️ Available Sports")
    print("=" * 45)
    for s in sports:
        status = "ACTIVE" if s.get("active") else "inactive"
        print(f"  {s['key']:30} {status}")
    print(f"\n  Total: {len(sports)} sports")

# =========================
# Snapshot Logic
# =========================

def fetch_odds(api_key, sport, regions, markets):
    url = f"{BASE_URL}/sports/{sport}/odds/"
    params = {
        "apiKey": api_key,
        "regions": regions,
        "markets": markets,
        "oddsFormat": "decimal",
        "dateFormat": "iso"
    }

    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Failed for sport={sport} | "
            f"status={resp.status_code} | body={resp.text}"
        )

    usage = {
        "used": resp.headers.get("x-requests-used"),
        "remaining": resp.headers.get("x-requests-remaining")
    }

    return resp.json(), usage


def save_snapshot(data, sport):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = DATA_DIR / sport
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = out_dir / f"{sport}_{ts}.json"
    filename.write_text(json.dumps(data, indent=2))

    return filename


# =========================
# CLI
# =========================

def print_help():
    print(f"""
OddsAPI Snapshot Tool
=====================

Usage:
  python snapshot_oddsapi.py <command> [options]

Commands:
  doctor                   Check API key status and usage
  list                     List all available sports
  key <action>             Manage your API key
  snapshot [options]       Fetch and save odds data

Key Actions:
  key show                 Show saved key (masked)
  key set                  Save a new API key
  key clear                Delete saved API key

Snapshot Options:
  --sports <sport> [...]   Sports to fetch (required)
  --regions <region>       Region to pull from (default: {DEFAULT_REGIONS})
  --markets <markets>      Comma-separated markets (default: {DEFAULT_MARKETS})

Examples:
  python snapshot_oddsapi.py doctor
  python snapshot_oddsapi.py list
  python snapshot_oddsapi.py key show
  python snapshot_oddsapi.py snapshot --sports basketball_nba
  python snapshot_oddsapi.py snapshot --sports basketball_nba hockey_nhl --regions us --markets h2h,spreads
""")

def main():
    ensure_directories()

    if len(sys.argv) < 2:
        print_help()
        return

    # --- key subcommand ---
    if sys.argv[1] == "key":
        if len(sys.argv) < 3:
            print("Usage: key [show|set|clear]")
            return

        cmd = sys.argv[2]

        if cmd == "show":
            show_api_key()
        elif cmd == "set":
            set_api_key()
        elif cmd == "clear":
            clear_api_key()
        else:
            print(f"Unknown key command: {cmd}")
            print("Usage: key [show|set|clear]")
        return

    # --- doctor subcommand ---
    if sys.argv[1] == "doctor":
        api_key = get_api_key()
        doctor_oddsapi(api_key)
        return

    # --- list subcommand ---
    if sys.argv[1] == "list":
        api_key = get_api_key()
        list_available_sports(api_key)
        return

    # --- snapshot subcommand ---
    if sys.argv[1] == "snapshot":
        parser = argparse.ArgumentParser(
            description="OddsAPI snapshot fetcher"
        )

        parser.add_argument(
            "--sports",
            nargs="+",
            required=True,
            help="Sports keys to fetch (e.g. basketball_nba soccer_epl)"
        )

        parser.add_argument(
            "--regions",
            default=DEFAULT_REGIONS,
            help=f"Region to pull from (default: {DEFAULT_REGIONS})"
        )

        parser.add_argument(
            "--markets",
            default=DEFAULT_MARKETS,
            help=f"Comma-separated markets (default: {DEFAULT_MARKETS})"
        )

        args = parser.parse_args(sys.argv[2:])
        api_key = get_api_key()

        for sport in args.sports:
            print(f"\n📥 Fetching odds for: {sport}")
            data, usage = fetch_odds(
                api_key,
                sport,
                args.regions,
                args.markets
            )

            out_file = save_snapshot(data, sport)
            print(f"✅ {len(data)} games saved → {out_file}")
            print(f"   📊 Used: {usage['used']} | Remaining: {usage['remaining']}")

        return

    # --- unrecognized ---
    print(f"Unknown command: {sys.argv[1]}")
    print_help()


if __name__ == "__main__":
    main()
