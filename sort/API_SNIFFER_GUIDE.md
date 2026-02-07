# API Sniffer - Complete Guide

**Version:** 2.0  
**Updated:** February 2026

A powerful REST API discovery and analysis tool that automatically probes endpoints, tests parameters, and generates comprehensive documentation of API structures.

---

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Parameter Depth Levels](#parameter-depth-levels)
5. [Batch Mode](#batch-mode)
6. [Understanding Output](#understanding-output)
7. [Complete Usage Examples](#complete-usage-examples)
8. [Rate Limit Management](#rate-limit-management)
9. [Tips & Best Practices](#tips--best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Features

### Core Capabilities
- ✅ **Auto-discovery** - Automatically finds all available endpoints
- ✅ **Smart parameter testing** - Tests 22+ common parameters to find working combinations
- ✅ **Structure analysis** - Maps response schemas with nested objects and arrays
- ✅ **Batch processing** - Process multiple APIs from a single config file
- ✅ **Dual output** - Technical JSON + human-readable summary reports
- ✅ **Rate limit aware** - Three testing depth levels to control API usage

### What It Discovers
- Which endpoints exist (200 OK vs 404 Not Found)
- Which endpoints need parameters vs return data immediately
- Working parameter combinations for each endpoint
- Complete response structures with field types
- Sample values for all fields
- Array item counts and nested object structures

---

## Installation

### Requirements
```bash
# Python 3.7 or higher
python3 --version

# Required package
pip install requests --break-system-packages
```

### Download
```bash
# Save api_sniffer.py to your preferred location
chmod +x api_sniffer.py
```

---

## Quick Start

### Basic Discovery (Single API)
```bash
# Discover all endpoints with basic parameter testing
python3 api_sniffer.py https://api.example.com \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Output:**
```
🔍 API Sniffer - Starting discovery...

🌐 Probing base URL...
✅ Base URL accessible

🔍 Discovering endpoints...
  ✅ /users (200) - Ready to use
  📋 /teams (200) - Needs parameters  
  ✅ /leagues (200) - Ready to use
  ❌ /players (404) - Does not exist

✅ Found 3 endpoints

🔍 Testing parameters to get sample data... (depth: basic)
  ✅ /teams with league=12 → 30 records
     Fields: id, name, code, logo

💡 Got sample data for 1/1 endpoints

📄 Full report: api_report.json
📄 Summary report: api_report_summary.txt
```

### View Results
```bash
# Human-readable summary
cat api_report_summary.txt

# Full technical details (for code integration)
cat api_report.json
```

---

## Parameter Depth Levels

Control how aggressively the tool tests parameters using `--param-depth`:

### Level Comparison

| Level    | Calls/Endpoint | Parameters Tested | When to Use                      |
|----------|----------------|-------------------|----------------------------------|
| `none`   | 0              | None              | Quick scan, limited API quota    |
| `basic`  | ~5             | 5 common params   | **Default** - batch processing   |
| `full`   | ~25            | 22 params + combos| Deep analysis, generous quota    |

### none - Endpoint Discovery Only

**What it does:**
- Probes which endpoints exist (200 vs 404)
- Shows which need parameters
- NO parameter testing

**Usage:**
```bash
python3 api_sniffer.py https://api.example.com \
  -H "Auth: TOKEN" \
  --param-depth none
```

**When to use:**
- Limited API quota (<50 calls available)
- Just want endpoint list
- Will test parameters manually

---

### basic - Common Parameters (DEFAULT)

**What it does:**
- Tests 5 most common parameters:
  - `season`: [2024, 2023]
  - `league`: [1, 2, 12]
  - `id`: [1, 2]
  - `team`: [1, 2]
  - `date`: [today]
- Finds working params for ~70% of endpoints

**Usage:**
```bash
python3 api_sniffer.py https://api.example.com \
  -H "Auth: TOKEN" \
  --param-depth basic  # This is the default
```

**When to use:**
- Batch processing multiple APIs
- Moderate rate limits (100-300 calls/hour)
- **Recommended for most use cases**

---

### full - All Parameters & Combinations

**What it does:**
- Tests 22 different parameters including:
  - Time-based: season, year, date
  - Entity IDs: league, team, player, game, fixture
  - Search: country, search, name
  - Status: status, live
  - Ranges: last, next, round
  - Other: type, timezone, h2h
- Tests 5 smart parameter combinations:
  - season + league
  - team + season
  - league + date
  - team + date
  - search + league
- Finds working params for ~95% of endpoints

**Usage:**
```bash
python3 api_sniffer.py https://api.example.com \
  -H "Auth: TOKEN" \
  --param-depth full
```

**When to use:**
- Processing 1-3 APIs only
- Generous API limits (500+ calls/hour)
- Need complete documentation
- Preparing for production integration

---

## Batch Mode

Process multiple APIs from a single configuration file.

### Generate Template
```bash
python3 api_sniffer.py --batch-template > my_apis.json
```

### Config Format
```json
{
  "apis": [
    {
      "name": "basketball",
      "base_url": "https://v1.basketball.api-sports.io",
      "headers": {
        "x-apisports-key": "{{api_key}}"
      }
    },
    {
      "name": "football",
      "base_url": "https://v3.football.api-sports.io",
      "headers": {
        "x-apisports-key": "{{api_key}}"
      }
    }
  ]
}
```

**Features:**
- `{{api_key}}` placeholder - automatically substituted
- Custom headers per API
- Friendly names for each API

### Run Batch
```bash
# Set your API key
export APISPORTS_KEY="your_key_here"

# Run batch with basic testing (recommended)
python3 api_sniffer.py --batch my_apis.json \
  --param-depth basic \
  -o batch_report.json

# Skip parameter testing (fastest)
python3 api_sniffer.py --batch my_apis.json \
  --param-depth none \
  -o batch_report.json
```

### Batch Output
Creates two files:
1. `batch_report.json` - Full technical details
2. `batch_report_summary.txt` - Clean human-readable format

Example summary:
```
═══════════════════════════════════════════════════════
API DISCOVERY BATCH REPORT
═══════════════════════════════════════════════════════

Basketball API
  Base URL: https://v1.basketball.api-sports.io
  Endpoints: 8 found

  Endpoint: /teams
  Parameters: league=12
  Returns: 30 records
  
  Fields:
    • id                   integer      (e.g., 132)
    • name                 string       (e.g., Boston Celtics)
    • code                 string       (e.g., BOS)

───────────────────────────────────────────────────────

Football API
  Base URL: https://v3.football.api-sports.io
  Endpoints: 11 found
  ...
```

---

## Understanding Output

### Endpoint Status Icons

During discovery, you'll see these icons:

| Icon | Meaning | Description |
|------|---------|-------------|
| ✅ | Ready | Endpoint exists and returned data |
| 📋 | Needs params | Endpoint exists but requires parameters |
| ⚠️ | Empty | Endpoint exists but returned no data |
| ❌ | Not found | Endpoint doesn't exist (404) |

### Parameter Testing Results

```
🔍 Testing parameters to get sample data... (depth: basic)
  ✅ /teams with league=12 → 30 records
     Fields: id, name, code, logo
  ✅ /games with season=2024 → 285 records
     Fields: id, date, teams, scores
  💡 Got sample data for 2/4 endpoints
  ⚠️  No working params found for: players, standings
```

**Key indicators:**
- **✅** Shows successful parameter combination
- **💡** Summary of success rate
- **⚠️** Lists endpoints that need manual investigation

### JSON Output Structure

```json
{
  "base_url": "https://api.example.com",
  "endpoints": {
    "/teams": {
      "status_code": 200,
      "success": true,
      "sample_params": {"league": 12},
      "structure": {
        "type": "array",
        "length": 30,
        "item_structure": {
          "id": {"type": "integer", "sample": 132},
          "name": {"type": "string", "sample": "Boston Celtics"},
          "logo": {"type": "string", "sample": "https://..."}
        }
      }
    }
  }
}
```

---

## Complete Usage Examples

### 1. Quick Scan (No Parameter Testing)
```bash
# Just discover what endpoints exist - 0 parameter calls
python3 api_sniffer.py https://v1.basketball.api-sports.io \
  -H "x-apisports-key: $APISPORTS_KEY" \
  --param-depth none \
  -o basketball_scan.json

# Uses: ~35 API calls (endpoint probes only)
```

### 2. Standard Discovery (Recommended)
```bash
# Discover endpoints + test common parameters
python3 api_sniffer.py https://v1.basketball.api-sports.io \
  -H "x-apisports-key: $APISPORTS_KEY" \
  --param-depth basic \
  -o basketball_basic.json

# Uses: ~80-120 API calls
```

### 3. Deep Analysis
```bash
# Complete documentation with all parameters
python3 api_sniffer.py https://v1.basketball.api-sports.io \
  -H "x-apisports-key: $APISPORTS_KEY" \
  --param-depth full \
  -o basketball_full.json

# Uses: ~200-300 API calls
```

### 4. Batch Processing (Multiple Sports)
```bash
# Create config for 4 American sports
cat > american_sports.json << 'EOF'
{
  "apis": [
    {
      "name": "basketball",
      "base_url": "https://v1.basketball.api-sports.io",
      "headers": {"x-apisports-key": "{{api_key}}"}
    },
    {
      "name": "football-nfl",
      "base_url": "https://v1.american-football.api-sports.io",
      "headers": {"x-apisports-key": "{{api_key}}"}
    },
    {
      "name": "baseball",
      "base_url": "https://v1.baseball.api-sports.io",
      "headers": {"x-apisports-key": "{{api_key}}"}
    },
    {
      "name": "hockey",
      "base_url": "https://v1.hockey.api-sports.io",
      "headers": {"x-apisports-key": "{{api_key}}"}
    }
  ]
}
EOF

# Run batch with basic testing
export APISPORTS_KEY="your_key"
python3 api_sniffer.py --batch american_sports.json \
  --param-depth basic \
  -o american_sports_report.json

# Uses: ~300-500 API calls total
# Creates: american_sports_report.json + american_sports_report_summary.txt
```

### 5. Probe Specific Endpoints Only
```bash
# Only test specific endpoints you care about
python3 api_sniffer.py https://api.example.com \
  -H "Auth: TOKEN" \
  -e users -e teams -e games \
  --param-depth full
```

### 6. Multiple Headers
```bash
python3 api_sniffer.py https://api.example.com \
  -H "Authorization: Bearer TOKEN" \
  -H "X-API-Version: 2" \
  -H "Accept: application/json"
```

---

## Rate Limit Management

Most APIs have rate limits. Here's how to work within them:

### Typical Rate Limits
- **Free tier:** 100-300 calls/hour
- **Paid tier:** 500-5000 calls/hour
- **Enterprise:** Often unlimited

### API Call Usage by Depth Level

| Scenario | none | basic | full |
|----------|------|-------|------|
| Single API (~30 endpoints) | 35 | 100-150 | 250-350 |
| Batch 4 APIs (~120 endpoints) | 130 | 400-600 | 1000-1400 |
| Batch 10 APIs (~300 endpoints) | 330 | 1000-1500 | 2500-3500 |

### Strategies for Limited Quotas

**If you have 100-300 calls/hour:**
```bash
# Option 1: Quick scan only
python3 api_sniffer.py --batch all_apis.json --param-depth none

# Option 2: Process one API with basic testing
python3 api_sniffer.py https://single-api.com -H "Auth: KEY" --param-depth basic
```

**If you have 500-1000 calls/hour:**
```bash
# Process 3-4 APIs with basic testing
python3 api_sniffer.py --batch small_batch.json --param-depth basic
```

**If you have 1000+ calls/hour:**
```bash
# Full batch with full testing
python3 api_sniffer.py --batch all_apis.json --param-depth full
```

### Split Large Batches

For 10+ APIs with limited quota:

```bash
# Day 1: American sports
python3 api_sniffer.py --batch american.json --param-depth basic

# Day 2: International sports  
python3 api_sniffer.py --batch international.json --param-depth basic

# Day 3: Combat sports
python3 api_sniffer.py --batch combat.json --param-depth basic
```

---

## Tips & Best Practices

### 1. Start Small
```bash
# Always start with a quick scan
python3 api_sniffer.py https://new-api.com -H "Auth: KEY" --param-depth none

# Review results, then do basic testing
python3 api_sniffer.py https://new-api.com -H "Auth: KEY" --param-depth basic
```

### 2. Use Summary Files
```bash
# Always check the _summary.txt file first
cat report_summary.txt

# Only look at JSON when integrating into code
cat report.json
```

### 3. Save Your Batch Configs
```bash
# Keep reusable configs for different scenarios
configs/
  ├── all_sports.json          # All 11 sports
  ├── american_sports.json     # 4 sports
  ├── international.json       # 4 sports
  └── quick_scan.json          # Critical APIs only
```

### 4. Version Your Reports
```bash
# Add dates to report filenames
python3 api_sniffer.py --batch apis.json -o report_2026-02-04.json

# Compare changes over time
diff report_2026-02-04_summary.txt report_2026-01-15_summary.txt
```

### 5. Environment Variables for API Keys
```bash
# Never commit API keys! Use environment variables
export APISPORTS_KEY="your_key_here"
export EXAMPLE_API_KEY="another_key"

# Reference in batch config with {{api_key}} placeholder
```

### 6. Combine with Other Tools
```bash
# Generate report, then process with jq
python3 api_sniffer.py https://api.com -H "Auth: KEY" -o report.json
cat report.json | jq '.endpoints | keys'  # List all endpoints

# Or use with grep
cat report_summary.txt | grep "✅"  # Show only working endpoints
```

---

## Troubleshooting

### Issue: "Authentication failed"
```bash
# Check your API key is correct
echo $APISPORTS_KEY

# Verify header format (some APIs use different names)
python3 api_sniffer.py https://api.com -H "x-api-key: KEY"  # vs
python3 api_sniffer.py https://api.com -H "Authorization: Bearer KEY"
```

### Issue: "No working params found"
```bash
# Try full depth testing
python3 api_sniffer.py https://api.com -H "Auth: KEY" --param-depth full

# Some endpoints may need specific parameters not in our list
# Check API documentation for required parameters
```

### Issue: Rate limit exceeded
```bash
# Use lower depth level
python3 api_sniffer.py --batch apis.json --param-depth none

# Or split batch into smaller groups
# Process 2-3 APIs at a time instead of 10
```

### Issue: Endpoints showing ❌ but they exist
```bash
# API might require base authentication even for 404s
# Or endpoint might need specific URL format
# Check API documentation for exact endpoint paths
```

### Issue: Empty responses (⚠️)
```bash
# Endpoint exists but has no data
# Try with parameter testing
python3 api_sniffer.py https://api.com -H "Auth: KEY" --param-depth basic

# Or check if data exists for your account
# Some endpoints return empty if you have no data
```

---

## Command Reference

### Full CLI Syntax
```
python3 api_sniffer.py [BASE_URL] [OPTIONS]

Options:
  BASE_URL              API base URL (e.g., https://api.example.com)
  -H, --header          HTTP header (can be used multiple times)
  -e, --endpoint        Specific endpoint to probe (can be used multiple times)
  -o, --output          Output file path (creates .json and _summary.txt)
  --timeout             Request timeout in seconds (default: 10)
  --param-depth         Parameter testing depth: none, basic, full (default: basic)
  --batch               Process multiple APIs from config file
  --batch-template      Generate example batch config
  -h, --help            Show help message
```

### Common Patterns
```bash
# Single API, default options
python3 api_sniffer.py https://api.example.com -H "Auth: KEY"

# Batch mode
python3 api_sniffer.py --batch config.json -o report.json

# Skip parameter testing
python3 api_sniffer.py https://api.com -H "Auth: KEY" --param-depth none

# Full analysis
python3 api_sniffer.py https://api.com -H "Auth: KEY" --param-depth full

# Specific endpoints only
python3 api_sniffer.py https://api.com -H "Auth: KEY" -e users -e teams
```

---

## Real-World Example: API-Sports

API-Sports provides 11 different sport APIs, each on a separate subdomain. Here's how to efficiently discover all of them:

### Step 1: Create Batch Config
```bash
python3 api_sniffer.py --batch-template > apisports_all.json

# Edit to add all 11 sports
nano apisports_all.json
```

### Step 2: Quick Scan (No Parameter Testing)
```bash
# Fast scan to see what endpoints exist
export APISPORTS_KEY="your_key_here"
python3 api_sniffer.py --batch apisports_all.json \
  --param-depth none \
  -o apisports_scan.json

# Uses: ~330 API calls
# Time: ~2-3 minutes
```

### Step 3: Deep Dive on Key Sports
```bash
# Create smaller config with just 3-4 sports you use most
# Then run with full testing
python3 api_sniffer.py --batch apisports_priority.json \
  --param-depth full \
  -o apisports_priority_full.json

# Uses: ~400-600 API calls
# Time: ~5-7 minutes
```

### Step 4: Review Results
```bash
# Check summary
cat apisports_scan_summary.txt

# Find specific endpoints
cat apisports_scan_summary.txt | grep "✅" | grep "teams"

# View full structure for integration
cat apisports_scan.json | jq '.apis.basketball.endpoints."/teams"'
```

---

## Version History

### v2.0 (February 2026)
- Added parameter depth levels (none, basic, full)
- Implemented batch processing mode
- Dual output format (JSON + summary)
- Improved visual feedback with clear status icons
- Expanded from 4 to 22 test parameters
- Added smart parameter combinations
- Rate limit awareness and guidance

### v1.1 (February 2026)
- Enhanced structure analysis (depth 2→5)
- Added parameter testing
- Improved error handling

### v1.0 (February 2026)
- Initial release
- Basic endpoint discovery
- Structure analysis

---

## Support & Feedback

For issues, questions, or suggestions, the tool outputs clear error messages and suggestions. Common issues are covered in the [Troubleshooting](#troubleshooting) section.

**Pro tip:** Always run with `--param-depth none` first on new APIs to understand their structure before committing to more API calls!

---

**Happy API discovering! 🚀**
