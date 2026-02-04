# Sports API Tools

A collection of powerful Python tools for working with sports APIs, with a focus on API-Sports integration.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: AAL](https://img.shields.io/badge/License-AAL-yellow.svg)](https://opensource.org/licenses/attribution-php)

## 🛠️ Tools

### 1. API Sniffer (v2.0) - API Discovery & Analysis Tool
Automatically discover and document REST API endpoints, structures, and parameters.

**Key Features:**
- 🔍 Auto-discovers all available endpoints
- 🎯 Smart parameter testing with 3 depth levels
- 📊 Batch mode - process multiple APIs at once
- 📄 Dual output - JSON + human-readable summaries
- ⚡ Rate limit aware

**Quick Start:**
```bash
# Discover a single API
python3 api_sniffer.py https://v1.basketball.api-sports.io \
  -H "x-apisports-key: YOUR_KEY" \
  --param-depth basic

# Batch process multiple sports
python3 api_sniffer.py --batch examples/apisports_batch_american.json \
  --param-depth basic \
  -o sports_report.json
```

**Documentation:** [API_SNIFFER_GUIDE.md](docs/API_SNIFFER_GUIDE.md)

---

### 2. Snapshot API-Sports (v1.1) - Data Collection Tool
Comprehensive sports data collector for API-Sports with support for NFL, NBA, Formula 1, MMA, and more.

**Key Features:**
- 🏈 Multi-sport support (NFL, NBA, F1, MMA, etc.)
- 📊 Flexible data collection (leagues, seasons, games, teams, players)
- 🔄 Handles inconsistent API structures across sports
- 💾 Saves to JSON with clean formatting

**Quick Start:**
```bash
# Collect NBA data
python3 snapshot_apisports.py basketball \
  --key YOUR_KEY \
  --leagues 12 \
  --seasons 2024 \
  --collection games

# Collect NFL data
python3 snapshot_apisports.py american-football \
  --key YOUR_KEY \
  --leagues 1 \
  --seasons 2024 \
  --collection games
```

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [API_SNIFFER_GUIDE.md](docs/API_SNIFFER_GUIDE.md) | Complete guide for api_sniffer.py |
| [PARAM_DEPTH_GUIDE.md](docs/PARAM_DEPTH_GUIDE.md) | Parameter depth levels reference |
| [CHANGELOG.md](docs/CHANGELOG.md) | Version history and updates |

---

## 🚀 Installation

### Requirements
```bash
# Python 3.7 or higher
python3 --version

# Install requests library
pip install requests
```

### Download
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Make scripts executable (optional)
chmod +x snapshot_apisports.py
chmod +x api_sniffer.py
```

---

## 📖 Usage Examples

### Example 1: Discover API Structure Before Collecting Data
```bash
# Step 1: Discover what endpoints and parameters are available
python3 api_sniffer.py https://v1.basketball.api-sports.io \
  -H "x-apisports-key: YOUR_KEY" \
  --param-depth full \
  -o basketball_structure.json

# Step 2: Review the structure
cat basketball_structure_summary.txt

# Step 3: Collect data using snapshot tool
python3 snapshot_apisports.py basketball \
  --key YOUR_KEY \
  --leagues 12 \
  --seasons 2024 \
  --collection games
```

### Example 2: Batch Discover All Sports
```bash
# Discover all 11 sports with basic parameter testing
export APISPORTS_KEY="your_key_here"
python3 api_sniffer.py --batch examples/apisports_batch.json \
  --param-depth basic \
  -o all_sports_discovery.json

# Review the clean summary
cat all_sports_discovery_summary.txt
```

### Example 3: Quick Endpoint Scan (No Parameter Testing)
```bash
# Fast scan - just see what endpoints exist
python3 api_sniffer.py https://v1.football.api-sports.io \
  -H "x-apisports-key: YOUR_KEY" \
  --param-depth none \
  -o football_scan.json
```

---

## 🎯 Common Workflows

### Workflow 1: Exploring a New Sport API
1. Run `api_sniffer.py` with `--param-depth none` for quick scan
2. Review summary to see available endpoints
3. Run again with `--param-depth full` for 2-3 key endpoints
4. Use `snapshot_apisports.py` to collect actual data

### Workflow 2: Batch API Documentation
1. Create batch config with sports you need
2. Run `api_sniffer.py --batch` with `--param-depth basic`
3. Save reports for team reference
4. Update configs as APIs change

---

## 🔑 API Keys

Both tools require an API-Sports key. Get yours at: https://api-sports.io/

**Set as environment variable:**
```bash
export APISPORTS_KEY="your_key_here"
```

**Or pass directly:**
```bash
# api_sniffer.py
python3 api_sniffer.py https://api.url -H "x-apisports-key: YOUR_KEY"

# snapshot_apisports.py
python3 snapshot_apisports.py basketball --key YOUR_KEY
```

---

## 📊 Batch Configuration Files

Pre-configured batch files are in the `examples/` directory:

| File | Sports Included | Use Case |
|------|----------------|----------|
| `apisports_batch.json` | All 11 sports | Complete API discovery |
| `apisports_batch_american.json` | Basketball, NFL, Baseball, Hockey | American sports only |
| `apisports_batch_international.json` | Football, F1, Rugby, MMA | International sports |

**Usage:**
```bash
python3 api_sniffer.py --batch examples/apisports_batch_american.json \
  --param-depth basic \
  -o american_sports.json
```

---

## ⚠️ Rate Limits

API-Sports has rate limits on free and paid tiers:
- **Free tier:** Usually 100-300 calls/hour
- **Paid tier:** 500-5,000 calls/hour

**api_sniffer.py depth levels:**
- `none`: ~35 calls per API (endpoint discovery only)
- `basic`: ~100-150 calls per API (recommended)
- `full`: ~250-350 calls per API (comprehensive)

**Recommendations:**
- Use `--param-depth basic` for batch processing
- Use `--param-depth full` for 1-3 APIs at a time
- Split large batches across multiple runs

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📜 License

Attribution Assurance License - see LICENSE file for details

---

## 🆘 Support

- **Issues:** Open a GitHub issue
- **Documentation:** See `docs/` directory
- **Examples:** See `examples/` directory

---

## 📈 Version History

See [CHANGELOG.md](docs/CHANGELOG.md) for detailed version history.

**Current Versions:**
- api_sniffer.py: v2.0
- snapshot_apisports.py: v1.1

---

## 🎉 Acknowledgments

Built for efficient sports data collection and API exploration. Special focus on API-Sports.io integration.

**Happy API exploring! 🚀**
