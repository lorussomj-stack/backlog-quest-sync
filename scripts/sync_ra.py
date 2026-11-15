#!/usr/bin/env python3
"""Create a secret-free RetroAchievements snapshot for Backlog Quest.

Requires RA_WEB_API_KEY as an environment variable; do not hardcode credentials.
"""
import datetime as dt
import json
import os
import pathlib
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USERNAME = "metsmjl"
ROOT = pathlib.Path(__file__).resolve().parents[1]
API_ROOT = "https://retroachievements.org/API/"
KEY = os.getenv("RA_WEB_API_KEY", "").strip()


def api(endpoint, **params):
    query = urlencode({"y": KEY, "u": USERNAME, **params})
    url = API_ROOT + endpoint + "?" + query
    try:
        # The key must never be written to logs or repository files.
        with urlopen(Request(url, headers={"User-Agent": "BacklogQuestTracker/1.0"}), timeout=35) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        raise RuntimeError("RetroAchievements API request failed (URL and API key hidden)") from None
    if isinstance(payload, dict) and ("Error" in payload or "error" in payload):
        raise RuntimeError("RetroAchievements API returned an error (details hidden)")
    return payload


def main():
    if not KEY:
        sys.exit("Missing RA_WEB_API_KEY GitHub Actions secret")

    # Complete library progress, paginated to prevent missing older games.
    all_games = []
    offset = 0
    while True:
        page = api("API_GetUserCompletionProgress.php", c=500, o=offset)
        rows = page.get("Results", [])
        all_games.extend(rows)
        offset += len(rows)
        if not rows or offset >= int(page.get("Total", 0)):
            break
        if offset > 5000:  # sanity limit; sufficient for a personal backlog
            break

    # Recent events provide actual achievement titles and descriptions.
    recent = api("API_GetUserRecentAchievements.php", m=10080)  # Last seven days
    if not isinstance(recent, list):
        raise RuntimeError("Unexpected recent-achievements response")

    # Get full list of earned/available achievements for GBC Pokemon TCG.
    tcg = None
    for game in all_games:
        title = str(game.get("Title", "")).casefold().replace("é", "e")
        console = str(game.get("ConsoleName", "")).casefold()
        if "pokemon trading card game" in title and "game boy color" in console:
            tcg = game
            break
    tcg_detail = None
    if tcg:
        details = api("API_GetGameInfoAndUserProgress.php", g=tcg["GameID"])
        achievements = details.get("Achievements", {})
        if not isinstance(achievements, dict):
            achievements = {}
        tcg_detail = {
            "id": tcg["GameID"],
            "title": details.get("Title", tcg.get("Title")),
            "earned": [
                {"id": int(a.get("ID", aid)), "title": a.get("Title"), "description": a.get("Description"),
                 "earned_at": a.get("DateEarned"), "hardcore_at": a.get("DateEarnedHardcore"),
                 "type": a.get("type")}
                for aid, a in achievements.items() if a.get("DateEarned") or a.get("DateEarnedHardcore")
            ],
            "num_earned": details.get("NumAwardedToUser"),
            "num_possible": details.get("NumAchievements"),
        }

    progress = {
        "username": USERNAME,
        "fetched_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source": "RetroAchievements Web API",
        "all_games": [
            {k: game.get(k) for k in ("GameID", "Title", "ConsoleName", "NumAwarded", "NumAwardedHardcore", "MaxPossible", "HighestAwardKind", "HighestAwardDate")}
            for game in all_games
        ],
        "recent_achievements_last_7_days": [
            {k: a.get(k) for k in ("Date", "GameID", "GameTitle", "ConsoleName", "Title", "Description", "Type", "AchievementID", "HardcoreMode")}
            for a in recent
        ],
        "pokemon_tcg_gbc": tcg_detail,
    }
    path = ROOT / "data" / "ra-progress.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(progress, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Snapshot updated: {len(all_games)} played games, {len(recent)} recent achievements; key not included")


if __name__ == "__main__":
    main()
