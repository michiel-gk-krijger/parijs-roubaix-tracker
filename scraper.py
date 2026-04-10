import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


DATA_PATH = Path("data/standings.json")
TIMEOUT_SECONDS = 20
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PR-Tracker/1.0; +https://github.com/)",
}


SOURCES = {
    "elite_mannen": "https://racecenter.paris-roubaix.fr/en/",
    "vrouwen": "https://racecenter.paris-roubaix-femmes.fr/en/",
    "beloften": "https://www.procyclingstats.com/race/paris-roubaix-u23/2026/result",
    "junioren": "https://www.procyclingstats.com/race/paris-roubaix-juniors/2026/result",
}

STATUS_MAP = {
    "elite_mannen": "live",
    "vrouwen": "live",
    "beloften": "final",
    "junioren": "final",
}


def load_existing():
    if not DATA_PATH.exists():
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "junioren": [],
            "beloften": [],
            "vrouwen": [],
            "elite_mannen": [],
            "status": {},
        }

    try:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "junioren": [],
            "beloften": [],
            "vrouwen": [],
            "elite_mannen": [],
            "status": {},
        }


def normalize_text(value):
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def scrape_rows_from_table(html):
    soup = BeautifulSoup(html, "html.parser")

    candidates = soup.select("table tbody tr")
    rows = []

    for tr in candidates:
        cells = [normalize_text(td.get_text(" ", strip=True)) for td in tr.select("td")]
        if len(cells) < 3:
            continue

        position_match = re.search(r"\d+", cells[0])
        if not position_match:
            continue

        position = int(position_match.group(0))
        name = cells[1]
        team = cells[2] if len(cells) >= 3 else ""
        gap = cells[3] if len(cells) >= 4 else ""
        if not gap and position == 1:
            gap = "Leider"

        if name:
            rows.append(
                {
                    "position": position,
                    "name": name,
                    "team": team,
                    "gap": gap or "-",
                }
            )

        if len(rows) >= 30:
            break

    return rows


def fetch_category(url):
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    rows = scrape_rows_from_table(response.text)
    if not rows:
        raise ValueError("Geen bruikbare standings gevonden in HTML.")
    return rows


def main():
    existing = load_existing()
    updated = dict(existing)

    status = dict(existing.get("status", {}))
    updated_any = False

    for category, url in SOURCES.items():
        try:
            rows = fetch_category(url)
            updated[category] = rows
            status[category] = STATUS_MAP.get(category, "final")
            updated_any = True
            print(f"[OK] {category}: {len(rows)} rijen")
        except Exception as exc:
            # Belangrijk: bestaande data behouden als bron tijdelijk faalt.
            if category not in updated:
                updated[category] = existing.get(category, [])
            status[category] = status.get(category, STATUS_MAP.get(category, "final"))
            print(f"[WARN] {category}: bestaande data behouden ({exc})")

    updated["status"] = status
    if updated_any:
        updated["generated_at"] = datetime.now(timezone.utc).isoformat()
    else:
        updated["generated_at"] = existing.get("generated_at", datetime.now(timezone.utc).isoformat())

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DONE] Geschreven naar {DATA_PATH}")


if __name__ == "__main__":
    main()
