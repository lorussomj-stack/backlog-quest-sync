# Backlog Quest: RetroAchievements Sync

This repository uses GitHub Actions to fetch progress for RetroAchievements username `metsmjl` once daily and commit a sanitized JSON snapshot. The repository may be **public**, but the RetroAchievements Web API key must be saved in **GitHub Actions Secrets**, never committed.

## One-time setup

1. Upload `.github/workflows/sync-retroachievements.yml`, `scripts/sync_ra.py`, and `data/quest-baseline.json` to these exact paths on the repository's default branch. You can drag the three *folders* from the extracted package into GitHub's **Add file → Upload files** screen. The `.github` folder is hidden on Mac: use Command + Shift + Period in Finder to display it.
2. Navigate to **Settings → Secrets and variables → Actions → New repository secret**.
3. Name the secret `RA_WEB_API_KEY`, paste your RetroAchievements **Web API** key, and save. Never paste it into a file, README, issue, or workflow log.
4. Open **Actions → Sync RetroAchievements → Run workflow**, choose `main`, and run. On success, the workflow commits `data/ra-progress.json`.
5. The workflow runs daily; you'll need a separate ChatGPT scheduled task to check the public snapshot and issue a refreshed Backlog Quest dashboard on changes.

## What gets saved

- Full-game completion/achievement counts, recent unlocks, and earned achievements for Pokémon Trading Card Game (GBC).
- The current **manual Backlog Quest baseline** in `data/quest-baseline.json` is preserved: 20 XP from completed Kirby's Dream Land and Super Mario Land; DuckTales and Donkey Kong '94 retired; Science, Rock, Lightning, Grass medals on Pokémon TCG; kid-reserved games are excluded from solo quests.
- No API key or login credential is ever written to a file. The public snapshot exposes gaming history only.

## Important caveats

- A RetroAchievements game mastering status is not identical to beating a game. The dashboard should not auto-award completion XP solely from progress percentages; use an explicit victory achievement or a direct confirmation.
- GitHub Actions schedules can be delayed. If the workflow fails, open the run logs; the script intentionally hides URLs containing secrets in errors.
- Because you shared your key in a conversation, consider rotating it before saving a replacement in GitHub Actions Secrets.

## Latest manual status (November 15, 2026)

Pokémon Trading Card Game is at 4/8 Master Medals (Science, Rock, Lightning, Grass). 20 XP total from Kirby’s Dream Land and Super Mario Land.
