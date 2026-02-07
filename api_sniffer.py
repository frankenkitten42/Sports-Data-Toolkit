#!/usr/bin/env python3
"""
====================================================
api_sniffer.py
Version: 1.0

Generic API endpoint discovery and structure mapping tool

Automatically probes REST APIs to discover:
- Available endpoints
- Required vs optional parameters
- Response structure (flat/nested/arrays/primitives)
- Data relationships and hierarchies
- Parameter dependencies

Useful for onboarding new APIs without manual trial-and-error.
====================================================
"""

import sys
import json
import requests
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# ==================================================
# COMMON ENDPOINT PATTERNS
# ==================================================

# Common REST API endpoint names to try
COMMON_ENDPOINTS = [
    # Sports-specific
    "leagues", "seasons", "teams", "games", "matches", "fixtures",
    "players", "standings", "odds", "statistics", "events",
    "competitions", "tournaments", "races", "fights", "circuits",
    "drivers", "rankings", "schedules", "scores", "lineups",
    "injuries", "transfers", "venues", "referees",
    
    # Generic
    "status", "version", "info", "health", "data",
    "list", "search", "query"
]

# Common parameter names to try
COMMON_PARAMS = [
    "id", "league", "season", "year", "team", "player",
    "date", "from", "to", "start", "end", "limit", "offset",
    "country", "name", "status", "round", "stage"
]

# ==================================================
# STRUCTURE ANALYZER
# ==================================================

def analyze_value_type(value: Any) -> str:
    """Classify the type of a value"""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, list):
        if not value:
            return "array[empty]"
        first = value[0]
        return f"array[{analyze_value_type(first)}]"
    elif isinstance(value, dict):
        return "object"
    else:
        return f"unknown({type(value).__name__})"

def analyze_structure(data: Any, max_depth: int = 5, current_depth: int = 0) -> Dict:
    """
    Recursively analyze data structure
    Returns a schema-like representation
    """
    if current_depth >= max_depth:
        return {"type": "...", "note": "max depth reached"}
    
    if data is None:
        return {"type": "null"}
    
    if isinstance(data, (bool, int, float, str)):
        result = {"type": analyze_value_type(data)}
        # Include sample for non-strings or short strings
        if not isinstance(data, str) or len(data) < 50:
            result["sample"] = data
        return result
    
    if isinstance(data, list):
        if not data:
            return {"type": "array", "items": "empty"}
        
        # Analyze first few items to determine consistency
        first_type = analyze_value_type(data[0])
        consistent = all(analyze_value_type(item) == first_type for item in data[:5])
        
        result = {
            "type": "array",
            "length": len(data),
            "item_type": first_type
        }
        
        # Analyze structure of first item if it's an object
        if isinstance(data[0], dict):
            result["item_structure"] = analyze_structure(data[0], max_depth, current_depth + 1)
        elif isinstance(data[0], list):
            result["item_structure"] = analyze_structure(data[0], max_depth, current_depth + 1)
        
        return result
    
    if isinstance(data, dict):
        result = {
            "type": "object",
            "keys": list(data.keys()),
            "fields": {}
        }
        
        # Analyze each field
        for key, value in data.items():
            result["fields"][key] = analyze_structure(value, max_depth, current_depth + 1)
        
        return result
    
    return {"type": f"unknown({type(data).__name__})"}

# ==================================================
# ENDPOINT PROBER
# ==================================================

class EndpointProbe:
    def __init__(self, base_url: str, headers: Dict[str, str] = None, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.timeout = timeout
        self.results = {}
    
    def probe_endpoint(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Probe a single endpoint with optional parameters
        Returns analysis of response
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params or {},
                timeout=self.timeout
            )
            
            # Parse response
            try:
                data = response.json()
            except:
                data = None
            
            result = {
                "status_code": response.status_code,
                "success": 200 <= response.status_code < 300,
                "content_type": response.headers.get("content-type", ""),
                "params_used": params or {},
            }
            
            # Analyze response structure
            if data is not None:
                result["response_type"] = "json"
                
                # Check for common error patterns
                if isinstance(data, dict):
                    # Extract error info but don't mark as failed if it's just param requirements
                    error_data = data.get("error") or data.get("errors")
                    if error_data:
                        result["error"] = error_data
                        # Only mark as failed if it's a real error, not just param requirements
                        error_str = str(error_data).lower()
                        if "endpoint" in error_str or "not found" in error_str or "forbidden" in error_str:
                            result["success"] = False
                    
                    # Extract useful metadata
                    result["response_keys"] = list(data.keys())
                    
                    # Look for data in common locations
                    response_data = (
                        data.get("response") or
                        data.get("data") or
                        data.get("results") or
                        data
                    )
                    
                    result["data_location"] = "root"
                    if "response" in data:
                        result["data_location"] = "response"
                    elif "data" in data:
                        result["data_location"] = "data"
                    elif "results" in data:
                        result["data_location"] = "results"
                    
                    # Analyze structure
                    result["structure"] = analyze_structure(response_data, max_depth=5)
                else:
                    result["structure"] = analyze_structure(data, max_depth=5)
            else:
                result["response_type"] = "non-json"
                result["content_length"] = len(response.content)
            
            return result
        
        except requests.Timeout:
            return {"error": "timeout", "success": False}
        except requests.RequestException as e:
            return {"error": str(e)[:100], "success": False}
    
    def discover_endpoints(self, endpoints: List[str] = None) -> Dict:
        """
        Try multiple endpoints to see which exist
        """
        endpoints = endpoints or COMMON_ENDPOINTS
        
        print(f"Probing {len(endpoints)} potential endpoints...")
        working_endpoints = {}
        
        for endpoint in endpoints:
            result = self.probe_endpoint(endpoint)
            
            # Endpoint "exists" if we got a valid response (even if it has errors about params)
            status_ok = result.get("status_code") == 200
            
            # Check error patterns
            error = result.get("error", {})
            error_str = str(error).lower()
            
            # Endpoint doesn't exist
            if result.get("status_code") == 404:
                print(f"  ❌ /{endpoint}")
                continue
            if "endpoint" in error_str and "exist" in error_str:
                print(f"  ❌ /{endpoint}")
                continue
            
            # Endpoint exists but needs parameters
            needs_params = (
                "required" in error_str or
                "parameter" in error_str or
                isinstance(error, dict) and any("required" in str(v).lower() for v in error.values())
            )
            
            # Endpoint exists and works
            if status_ok:
                working_endpoints[endpoint] = result
                
                if needs_params:
                    print(f"  📋 /{endpoint} (needs params)")
                elif result.get("structure", {}).get("length") == 0:
                    print(f"  ⚠️  /{endpoint} (empty)")
                else:
                    print(f"  ✅ /{endpoint}")
            else:
                # Some other error - show it
                print(f"  ❌ /{endpoint}")
        
        return working_endpoints
        
        return working_endpoints
    
    def test_parameters(self, endpoint: str, params_to_test: Dict[str, List]) -> Dict:
        """
        Test different parameter combinations
        params_to_test = {"season": [2024, 2023], "league": [1, 2]}
        """
        print(f"\nTesting parameters for /{endpoint}...")
        
        # First try without params
        baseline = self.probe_endpoint(endpoint, {})
        results = {"no_params": baseline}
        
        # Try each parameter individually
        for param_name, param_values in params_to_test.items():
            for value in param_values:
                test_params = {param_name: value}
                result = self.probe_endpoint(endpoint, test_params)
                
                key = f"{param_name}={value}"
                results[key] = result
                
                if result.get("success") and not baseline.get("success"):
                    print(f"  ✅ {param_name}={value} makes it work!")
                elif result.get("success"):
                    # Compare to baseline
                    base_len = baseline.get("structure", {}).get("length", 0)
                    test_len = result.get("structure", {}).get("length", 0)
                    if test_len != base_len:
                        print(f"  🔍 {param_name}={value} changes result (count: {base_len} → {test_len})")
        
        return results
    
    def generate_report(self, output_file: str = None):
        """Generate a comprehensive report of findings"""
        report = {
            "api_base_url": self.base_url,
            "scan_timestamp": datetime.now().isoformat(),
            "findings": self.results
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Report saved to {output_file}")
        
        return report

# ==================================================
# SMART DISCOVERY MODE
# ==================================================

def smart_discovery(base_url: str, headers: Dict = None):
    """
    Intelligent API discovery workflow
    """
    probe = EndpointProbe(base_url, headers)
    
    print("=" * 60)
    print("API STRUCTURE DISCOVERY")
    print("=" * 60)
    print(f"Target: {base_url}\n")
    
    # Step 1: Discover working endpoints
    working = probe.discover_endpoints()
    
    if not working:
        print("\n❌ No working endpoints found")
        return
    
    print(f"\n✅ Found {len(working)} working endpoints")
    print("=" * 60)
    
    # Step 2: Analyze each working endpoint
    for endpoint, result in working.items():
        print(f"\n📍 /{endpoint}")
        print("-" * 60)
        
        structure = result.get("structure", {})
        print(f"Response type: {structure.get('type', 'unknown')}")
        
        if structure.get("type") == "array":
            print(f"Array length: {structure.get('length', 0)}")
            print(f"Item type: {structure.get('item_type', 'unknown')}")
            
            if structure.get("item_structure"):
                item = structure["item_structure"]
                if item.get("type") == "object":
                    keys = item.get('keys', [])
                    print(f"Item keys: {', '.join(keys[:10])}")
                    if len(keys) > 10:
                        print(f"           ... and {len(keys) - 10} more")
        
        elif structure.get("type") == "object":
            keys = structure.get('keys', [])
            print(f"Keys: {', '.join(keys[:10])}")
            if len(keys) > 10:
                print(f"      ... and {len(keys) - 10} more")
        
        # Check if it looks like it needs parameters
        if structure.get("length", 1) == 0 or result.get("error"):
            print("⚠️  Empty response or error - testing parameters...")
            
            # Try common parameter combinations
            test_params = {
                "season": [2024, 2023, 2022],
                "league": [1, 2, 12],
                "year": [2024, 2023],
                "id": [1, 2, 3]
            }
            
            found_working = False
            
            # Try single params
            for param_name, values in test_params.items():
                if found_working:
                    break
                for value in values:
                    test_result = probe.probe_endpoint(endpoint, {param_name: value})
                    test_structure = test_result.get("structure", {})
                    
                    if test_structure.get("length", 0) > 0:
                        print(f"✅ Works with {param_name}={value}")
                        print(f"   Returns: {test_structure.get('length')} {test_structure.get('item_type', 'items')}")
                        found_working = True
                        break
            
            # Try combinations if single params didn't work
            if not found_working:
                for season_val in test_params["season"][:2]:
                    if found_working:
                        break
                    for league_val in test_params["league"][:2]:
                        combo = {"season": season_val, "league": league_val}
                        test_result = probe.probe_endpoint(endpoint, combo)
                        test_structure = test_result.get("structure", {})
                        
                        if test_structure.get("length", 0) > 0:
                            print(f"✅ Works with season={season_val}, league={league_val}")
                            print(f"   Returns: {test_structure.get('length')} {test_structure.get('item_type', 'items')}")
                            found_working = True
                            break
    
    # Step 3: Look for hierarchical relationships
    print("\n" + "=" * 60)
    print("DETECTED PATTERNS")
    print("=" * 60)
    
    # Look for endpoints that might be related
    if "leagues" in working and "seasons" in working:
        print("\n🔗 Likely hierarchy: leagues → seasons")
    
    if "teams" in working and "players" in working:
        print("🔗 Likely hierarchy: teams → players")
    
    if "games" in working or "fixtures" in working or "matches" in working:
        print("🔗 Event data available (games/fixtures/matches)")
    
    # Save full report
    probe.results = working
    probe.generate_report("api_discovery_report.json")
    
    return working

# ==================================================
# BATCH PROCESSING
# ==================================================

def print_batch_template():
    """Print example batch config file"""
    template = {
        "description": "API-Sports Multi-Sport Discovery",
        "api_key": "YOUR_API_KEY_HERE",
        "timeout": 10,
        "apis": [
            {
                "name": "basketball",
                "base_url": "https://v1.basketball.api-sports.io",
                "headers": {
                    "x-apisports-key": "{{api_key}}"
                }
            },
            {
                "name": "nfl",
                "base_url": "https://v1.american-football.api-sports.io",
                "headers": {
                    "x-apisports-key": "{{api_key}}"
                }
            },
            {
                "name": "f1",
                "base_url": "https://v1.formula-1.api-sports.io",
                "headers": {
                    "x-apisports-key": "{{api_key}}"
                }
            }
        ]
    }
    
    print("=" * 60)
    print("BATCH CONFIG FILE TEMPLATE")
    print("=" * 60)
    print("\nSave this as 'apis.json' then run:")
    print("  python api_sniffer.py --batch apis.json -o report.json\n")
    print(json.dumps(template, indent=2))
    print("\n" + "=" * 60)
    print("NOTES:")
    print("=" * 60)
    print("""
- {{api_key}} is replaced with the value from "api_key" field
- You can add as many APIs as you want in the "apis" array
- Each API can have different headers
- "timeout" is optional (default: 10 seconds)
- "name" is used in the output report to identify each API

RATE LIMIT TIP:
- Parameter testing uses 5-15 API calls per endpoint
- Most APIs limit calls to 100-500 per hour
- For 10+ APIs, split into smaller batches:
    • Day 1: apisports_batch_american.json (4 sports)
    • Day 2: apisports_batch_international.json (4 sports)
    • Day 3: apisports_batch_other.json (remaining)

OUTPUT FILES:
- report.json - Full technical data (for programmatic use)
- report_summary.txt - Clean human-readable summary
""")

def run_batch_discovery(config_file: str, output_file: str = None, timeout: int = 10, param_depth: str = "basic"):
    """
    Process multiple APIs from a config file
    """
    try:
        with open(config_file) as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_file}")
        print(f"   Run 'python api_sniffer.py --batch-template' to see example format")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return
    
    # Extract global settings
    api_key = config.get("api_key", "")
    global_timeout = config.get("timeout", timeout)
    apis = config.get("apis", [])
    
    if not apis:
        print("❌ No APIs defined in config file")
        print("   Add APIs to the 'apis' array")
        return
    
    print("=" * 60)
    print("BATCH API DISCOVERY")
    print("=" * 60)
    print(f"Config: {config_file}")
    print(f"APIs to process: {len(apis)}")
    print(f"Description: {config.get('description', 'N/A')}")
    print("=" * 60)
    
    results = {
        "batch_config": config_file,
        "scan_timestamp": datetime.now().isoformat(),
        "description": config.get("description", ""),
        "apis": {}
    }
    
    for i, api_config in enumerate(apis, 1):
        name = api_config.get("name", f"api_{i}")
        base_url = api_config.get("base_url")
        
        if not base_url:
            print(f"\n⚠️  Skipping {name}: no base_url defined")
            continue
        
        print(f"\n[{i}/{len(apis)}] Processing: {name}")
        print(f"URL: {base_url}")
        
        # Build headers with variable substitution
        headers = {}
        for key, value in api_config.get("headers", {}).items():
            # Replace {{api_key}} placeholder
            if isinstance(value, str):
                value = value.replace("{{api_key}}", api_key)
            headers[key] = value
        
        # Run discovery
        probe = EndpointProbe(base_url, headers, global_timeout)
        working = probe.discover_endpoints()
        
        # Categorize endpoints
        ready = []
        needs_params = []
        empty = []
        
        if working:
            print(f"✅ Found {len(working)} endpoints")
            
            for endpoint, result in working.items():
                error = result.get("error", {})
                error_str = str(error).lower()
                
                if "required" in error_str or "parameter" in error_str:
                    needs_params.append(endpoint)
                elif result.get("structure", {}).get("length") == 0:
                    empty.append(endpoint)
                else:
                    ready.append(endpoint)
            
            # Show summary
            if ready:
                print(f"  ✅ Ready: {', '.join(ready)}")
            if needs_params:
                print(f"  📋 Needs params: {', '.join(needs_params)}")
            if empty:
                print(f"  ⚠️  Empty: {', '.join(empty)}")
            
            # Test parameters for endpoints that need them
            if needs_params or empty:
                # Skip testing if param_depth is none
                if param_depth == "none":
                    print(f"\n  ℹ️  Parameter testing skipped (--param-depth none)")
                else:
                    print(f"\n  🔍 Testing parameters to get sample data... (depth: {param_depth})")
                    
                    # Get current date for date-based queries
                    today = datetime.now().strftime("%Y-%m-%d")
                    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                    
                    # BASIC parameters - most likely to work, fewer API calls (~5 per endpoint)
                    basic_params = {
                        "season": [2024, 2023],
                        "league": [1, 2, 12],  # 12=NBA
                        "id": [1, 2],
                        "team": [1, 2],
                        "date": [today],
                    }
                    
                    # FULL parameters - all possibilities (~25 per endpoint)
                    full_params = {
                        # Time-based
                        "season": [2024, 2023, 2022, "2024-2025", "2023-2024"],
                        "year": [2024, 2023, 2022],
                        "date": [today, yesterday, last_week, "2024-01-01"],
                        
                        # Entity IDs
                        "league": [1, 2, 12, 39, 140],  # 12=NBA, 39=Premier League, 140=La Liga
                        "team": [1, 2, 3, 10, 33, 50],  # More team IDs to try
                        "id": [1, 2, 3, 5, 10],
                        "player": [1, 2, 3],
                        "game": [1, 2, 3],
                        "fixture": [1, 2, 3],
                        
                        # Search/filter
                        "country": ["USA", "England", "Spain", "France", "Brazil"],
                        "search": ["a", "smith", "united"],  # Common search terms
                        "name": ["a", "united"],
                        
                        # Status/state
                        "status": ["FT", "NS", "LIVE"],  # Finished, Not Started, Live
                        "live": ["all", "1"],
                        
                        # Ranges
                        "last": [5, 10],
                        "next": [5, 10],
                        "round": [1, 2, "Regular Season"],
                        
                        # Other common
                        "type": ["league", "cup"],
                        "timezone": ["UTC", "America/New_York"],
                        "h2h": ["1-2", "33-34"],  # Head to head team matchups
                    }
                    
                    # Choose parameter set based on depth
                    test_params = basic_params if param_depth == "basic" else full_params
                    
                    successful_tests = 0
                    failed_endpoints = []
                
                for endpoint in (needs_params + empty):
                    found_working = False
                    
                    # Try single params first
                    for param_name, values in test_params.items():
                        if found_working:
                            break
                        for value in values:
                            test_result = probe.probe_endpoint(endpoint, {param_name: value})
                            
                            # Success if we got data
                            if test_result.get("success") and not test_result.get("error"):
                                structure = test_result.get("structure", {})
                                data_count = structure.get("length", 0)
                                
                                if data_count > 0:
                                    # Update the endpoint result with working params
                                    working[endpoint]["sample_params"] = {param_name: value}
                                    working[endpoint]["sample_structure"] = structure
                                    working[endpoint]["sample_data_count"] = data_count
                                    
                                    # Show structure preview
                                    item_struct = structure.get("item_structure", {})
                                    if item_struct.get("type") == "object":
                                        keys = item_struct.get("keys", [])
                                        print(f"    ✅ /{endpoint} with {param_name}={value} → {data_count} records")
                                        print(f"       Fields: {', '.join(keys[:8])}")
                                        if len(keys) > 8:
                                            print(f"               ... and {len(keys) - 8} more")
                                    else:
                                        print(f"    ✅ /{endpoint} with {param_name}={value} → {data_count} records")
                                    
                                    successful_tests += 1
                                    found_working = True
                                    break  # Found working params, move to next endpoint
                        
                        if found_working:
                            break  # Found working params for this endpoint
                    
                    # If single param didn't work, try combinations
                    if not found_working:
                        # Common parameter combinations
                        combos_to_try = [
                            # Season + League (games, standings, teams)
                            ("season", [2024, 2023], "league", [1, 2, 12]),
                            # Team + Season (players, games)
                            ("team", [1, 2, 33], "season", [2024, 2023]),
                            # League + Date (fixtures, games)
                            ("league", [1, 2, 12], "date", [today, yesterday]),
                            # Team + Date (recent games)
                            ("team", [1, 2], "date", [today, last_week]),
                            # Search + League (finding specific teams/players)
                            ("search", ["a"], "league", [1, 2]),
                        ]
                        
                        for param1_name, param1_values, param2_name, param2_values in combos_to_try:
                            if found_working:
                                break
                            
                            for val1 in param1_values[:2]:  # Try first 2 values
                                if found_working:
                                    break
                                for val2 in param2_values[:2]:
                                    combo_params = {param1_name: val1, param2_name: val2}
                                    test_result = probe.probe_endpoint(endpoint, combo_params)
                                    
                                    if test_result.get("success") and not test_result.get("error"):
                                        structure = test_result.get("structure", {})
                                        data_count = structure.get("length", 0)
                                        
                                        if data_count > 0:
                                            working[endpoint]["sample_params"] = combo_params
                                            working[endpoint]["sample_structure"] = structure
                                            working[endpoint]["sample_data_count"] = data_count
                                            
                                            # Show structure preview
                                            item_struct = structure.get("item_structure", {})
                                            params_str = ", ".join(f"{k}={v}" for k, v in combo_params.items())
                                            if item_struct.get("type") == "object":
                                                keys = item_struct.get("keys", [])
                                                print(f"    ✅ /{endpoint} with {params_str} → {data_count} records")
                                                print(f"       Fields: {', '.join(keys[:8])}")
                                                if len(keys) > 8:
                                                    print(f"               ... and {len(keys) - 8} more")
                                            else:
                                                print(f"    ✅ /{endpoint} with {params_str} → {data_count} records")
                                            
                                            successful_tests += 1
                                            found_working = True
                                            break
                            
                            if found_working:
                                break
                    
                    # Track failures
                    if not found_working:
                        failed_endpoints.append(endpoint)
                
                # Show summary of parameter testing
                if successful_tests > 0:
                    print(f"    💡 Got sample data for {successful_tests}/{len(needs_params + empty)} endpoints")
                
                if failed_endpoints:
                    print(f"    ⚠️  No working params found for: {', '.join(failed_endpoints)}")

        else:
            print(f"❌ No endpoints found")
        
        results["apis"][name] = {
            "base_url": base_url,
            "working_endpoints": list(working.keys()),
            "endpoint_count": len(working),
            "ready_endpoints": ready,
            "needs_params": needs_params,
            "empty_endpoints": empty,
            "details": working
        }
    
    # Save consolidated report
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n" + "=" * 60)
        print(f"📄 Technical report saved to {output_file}")
        
        # Generate clean summary
        generate_clean_summary(results, output_file)
    else:
        print(f"\n" + "=" * 60)
        print("BATCH RESULTS:")
        print(json.dumps(results, indent=2))
    
    # Summary
    print(f"\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Sport':<15} {'Total':<7} {'Ready':<7} {'Needs Params':<13} {'Got Samples':<12}")
    print("-" * 60)
    
    for name, data in results["apis"].items():
        total = data['endpoint_count']
        ready = len(data['ready_endpoints'])
        needs = len(data['needs_params'])
        
        # Count how many endpoints got sample data
        samples = 0
        for endpoint_data in data['details'].values():
            if "sample_params" in endpoint_data:
                samples += 1
        
        print(f"{name:<15} {total:<7} {ready:<7} {needs:<13} {samples:<12}")
    
    print(f"\n💡 Two reports generated:")
    print(f"   • {output_file or 'report.json'} - Technical details (for code)")
    print(f"   • {output_file.replace('.json', '_summary.txt') if output_file else 'report_summary.txt'} - Readable summary (for humans)")

def generate_clean_summary(results: Dict, output_file: str):
    """
    Generate a human-readable summary separate from the technical report
    """
    summary_file = output_file.replace('.json', '_summary.txt')
    
    with open(summary_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("API STRUCTURE DISCOVERY - SUMMARY REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Scan Date: {results['scan_timestamp']}\n")
        f.write(f"Description: {results.get('description', 'N/A')}\n")
        f.write("=" * 80 + "\n\n")
        
        for sport_name, sport_data in results['apis'].items():
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"SPORT: {sport_name.upper()}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Base URL: {sport_data['base_url']}\n")
            f.write(f"Total Endpoints: {sport_data['endpoint_count']}\n\n")
            
            for endpoint_name, endpoint_data in sport_data['details'].items():
                f.write("-" * 80 + "\n")
                f.write(f"Endpoint: /{endpoint_name}\n")
                f.write("-" * 80 + "\n")
                
                # Show if it needs params
                if "sample_params" in endpoint_data:
                    params_str = ", ".join(f"{k}={v}" for k, v in endpoint_data["sample_params"].items())
                    f.write(f"Parameters: {params_str}\n")
                    f.write(f"Returns: {endpoint_data.get('sample_data_count', 0)} records\n\n")
                    
                    # Show structure
                    structure = endpoint_data.get("sample_structure", {})
                    item_struct = structure.get("item_structure", {})
                    
                    if item_struct.get("type") == "object":
                        f.write("Fields:\n")
                        fields = item_struct.get("fields", {})
                        
                        for field_name, field_info in fields.items():
                            field_type = field_info.get("type", "unknown")
                            sample = field_info.get("sample", "")
                            
                            if sample:
                                # Truncate long samples
                                if isinstance(sample, str) and len(sample) > 40:
                                    sample = sample[:37] + "..."
                                f.write(f"  • {field_name:<20} {field_type:<12} (e.g., {sample})\n")
                            else:
                                f.write(f"  • {field_name:<20} {field_type}\n")
                    else:
                        f.write(f"Returns: {structure.get('item_type', 'unknown')} array\n")
                
                elif endpoint_data.get("structure", {}).get("length", 0) > 0:
                    # Works without params
                    structure = endpoint_data.get("structure", {})
                    f.write(f"Parameters: None required\n")
                    f.write(f"Returns: {structure.get('length', 0)} records\n\n")
                    
                    item_struct = structure.get("item_structure", {})
                    if item_struct.get("type") == "object":
                        f.write("Fields:\n")
                        fields = item_struct.get("fields", {})
                        
                        for field_name, field_info in fields.items():
                            field_type = field_info.get("type", "unknown")
                            sample = field_info.get("sample", "")
                            
                            if sample:
                                if isinstance(sample, str) and len(sample) > 40:
                                    sample = sample[:37] + "..."
                                f.write(f"  • {field_name:<20} {field_type:<12} (e.g., {sample})\n")
                            else:
                                f.write(f"  • {field_name:<20} {field_type}\n")
                    elif structure.get("type") == "array":
                        f.write(f"Returns: Array of {structure.get('item_type', 'unknown')}\n")
                else:
                    # Needs params but we didn't find working ones
                    error = endpoint_data.get("error", "")
                    f.write(f"Status: Requires parameters (not tested)\n")
                    if error:
                        f.write(f"Error: {str(error)[:100]}\n")
                
                f.write("\n")
    
    print(f"📄 Clean summary saved to {summary_file}")
    print(f"   (Human-readable format with field types and examples)")
    return summary_file


# ==================================================
# CLI
# ==================================================

def main():
    import sys
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    
    parser = argparse.ArgumentParser(
        prog='api_sniffer.py',
        description="""
API Structure Discovery Tool - Automatically probe and map REST API endpoints

Discovers:
  • Which endpoints exist (tries 30+ common patterns)
  • Response structure (flat/nested/arrays/primitives)
  • Required vs optional parameters
  • Data relationships and hierarchies
  
Saves hours of manual API exploration and debugging!
        """,
        epilog="""
Examples:
  # Full auto-discovery (recommended for new APIs)
  %(prog)s https://api.example.com -H "Authorization: Bearer TOKEN"
  
  # Probe specific endpoints only
  %(prog)s https://api.example.com -e users -e teams -e games
  
  # Multiple headers
  %(prog)s https://api.example.com -H "X-API-Key: KEY" -H "Accept: application/json"
  
  # Save detailed report
  %(prog)s https://api.example.com -H "Auth: TOKEN" -o api_report.json
  
  # Real example - API-Sports
  %(prog)s https://v1.basketball.api-sports.io -H "x-apisports-key: YOUR_KEY"
  
  # Batch mode - process multiple APIs from config file
  %(prog)s --batch apis.json -o batch_report.json
  
  # Generate batch config template
  %(prog)s --batch-template > my_apis.json
  
  # Control parameter testing depth
  %(prog)s --batch apis.json --param-depth none    # Skip param testing (fastest)
  %(prog)s --batch apis.json --param-depth basic   # Common params only (default, ~5 calls/endpoint)
  %(prog)s --batch apis.json --param-depth full    # All params (~25 calls/endpoint)

IMPORTANT BATCH TIPS:
  • Parameter testing uses many API calls:
      - none: 0 calls (just discovers endpoints)
      - basic: ~5 calls per endpoint needing params
      - full: ~25 calls per endpoint needing params
  • Most APIs have rate limits (often 100-500 calls/hour)
  • For large batches (10+ APIs), use --param-depth basic or none
  • Use --param-depth full only for 1-3 APIs at a time
  • Batch reports generate TWO files:
      - {filename}.json - Full technical details (for code)
      - {filename}_summary.txt - Clean readable format (for humans)

For detailed usage, see API_SNIFFER_GUIDE.md
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "base_url",
        metavar="BASE_URL",
        nargs='?',  # Make optional for batch mode
        help="Base URL of the API (e.g., https://api.example.com)"
    )
    
    parser.add_argument(
        "--batch", "-b",
        metavar="CONFIG_FILE",
        help="Process multiple APIs from JSON config file (see --batch-template for format)"
    )
    
    parser.add_argument(
        "--batch-template",
        action="store_true",
        help="Print example batch config file and exit"
    )
    
    parser.add_argument(
        "--header", "-H",
        metavar="HEADER",
        action="append",
        help="Add HTTP header in format 'Key: Value' (can be repeated for multiple headers)"
    )
    
    parser.add_argument(
        "--endpoint", "-e",
        metavar="NAME",
        action="append",
        help="Probe specific endpoint(s) instead of auto-discovery (can be repeated)"
    )
    
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Save detailed JSON report to file (default: print to console only)"
    )
    
    parser.add_argument(
        "--timeout",
        metavar="SECONDS",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)"
    )
    
    parser.add_argument(
        "--param-depth",
        metavar="LEVEL",
        choices=["none", "basic", "full"],
        default="basic",
        help="Parameter testing depth: none (skip), basic (5 common params), full (22 params + combos). Default: basic"
    )
    
    args = parser.parse_args()
    
    # Handle batch template request
    if args.batch_template:
        print_batch_template()
        return
    
    # Handle batch mode
    if args.batch:
        run_batch_discovery(args.batch, args.output, args.timeout, args.param_depth)
        return
    
    # Validate single-API mode
    if not args.base_url:
        parser.error("BASE_URL is required (unless using --batch mode)")
    
    # Parse headers
    headers = {}
    if args.header:
        for h in args.header:
            if ':' in h:
                key, value = h.split(':', 1)
                headers[key.strip()] = value.strip()
    
    # Run discovery
    if args.endpoint:
        # Probe specific endpoints
        probe = EndpointProbe(args.base_url, headers, args.timeout)
        for endpoint in args.endpoint:
            result = probe.probe_endpoint(endpoint)
            print(f"\n/{endpoint}:")
            print(json.dumps(result, indent=2))
    else:
        # Full discovery mode
        smart_discovery(args.base_url, headers)

if __name__ == "__main__":
    main()
