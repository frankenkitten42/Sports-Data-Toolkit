import json
import os
import csv

SNAPSHOT_FOLDER = "snapshots"
NORMALIZED_FOLDER = "normalized"

sport = "basketball_nba"

def american_to_decimal(odds):
    if odds > 0:
        return 1 + odds / 100
    else:
        return 1 + 100 / abs(odds)

def compute_implied_prob(decimal_odds):
    return 1 / decimal_odds

def remove_vig(probabilities):
    """
    Remove bookmaker vig using the simple method:
    divide each probability by the sum of probabilities.
    """
    total = sum(probabilities)
    return [p / total for p in probabilities]


def normalize_snapshot_file(filename):
    with open(os.path.join(SNAPSHOT_FOLDER, filename), "r") as f:
        snapshot = json.load(f)

    normalized_rows = []

    for event in snapshot.get("events", []):
        event_id = event.get("id")
        sport = event.get("sport_key")
        commence_time = event.get("commence_time")
        home_team = event.get("home_team")
        away_team = event.get("away_team")

        for bookmaker in event.get("bookmakers", []):
            bookmaker_name = bookmaker.get("key")
            last_update = bookmaker.get("last_update")

            for market in bookmaker.get("markets", []):
                market_key = market.get("key")

                # Convert American odds → decimal → implied probabilities
                decimal_odds_list = [
                    american_to_decimal(o.get("price")) for o in market.get("outcomes", [])
                ]
                implied_probs = [compute_implied_prob(d) for d in decimal_odds_list]
                fair_probs = remove_vig(implied_probs)

                for idx, outcome in enumerate(market.get("outcomes", [])):
                    outcome_name = outcome.get("name")
                    american_odds = outcome.get("price")
                    decimal_odds = decimal_odds_list[idx]
                    implied_prob = implied_probs[idx]
                    fair_prob = fair_probs[idx]

                    row = {
                        "event_id": event_id,
                        "sport": sport,
                        "commence_time": commence_time,
                        "bookmaker": bookmaker_name,
                        "market": market_key,
                        "outcome": outcome_name,
                        "american_odds": american_odds,
                        "decimal_odds": round(decimal_odds, 4),
                        "implied_probability": round(implied_prob, 4),
                        "fair_probability": round(fair_prob, 4),
                        "last_update": last_update
                    }

                    normalized_rows.append(row)

    return normalized_rows

def normalize_all_snapshots():
    os.makedirs(NORMALIZED_FOLDER, exist_ok=True)

    for filename in os.listdir(SNAPSHOT_FOLDER):
        if not filename.endswith(".json"):
            continue

        print(f"Normalizing {filename}...")
        normalized_rows = normalize_snapshot_file(filename)

        # Save normalized JSON
        json_file = os.path.join(NORMALIZED_FOLDER, filename)
        with open(json_file, "w") as f:
            json.dump(normalized_rows, f, indent=2)

        # Save normalized CSV
        csv_file = json_file.replace(".json", ".csv")
        if normalized_rows:
            with open(csv_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=normalized_rows[0].keys())
                writer.writeheader()
                writer.writerows(normalized_rows)
                                                                                                                                             print(f"✅ Saved normalized JSON → {json_file}")
        print(f"✅ Saved normalized CSV  → {csv_file}")

if __name__ == "__main__":
    normalize_all_snapshots()