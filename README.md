# Clash Legends Stats

Small Clash of Clans Legends League tracker with a static GitHub Pages site.

## What it does

- Seeds a snapshot of the current global top 200 Legends players.
- Polls each tracked player's battle log once per hour.
- Keeps only legend attacks from the current Legends day.
- Appends only brand-new legend attacks into one daily JSONL file under `work/tracker_data/daily/`.
- Publishes the latest data into `site/data/` for GitHub Pages.
- Renders the ranking UI from `site/index.html`.

## Setup

```bash
cd ~/clash-legends-stats
cp .env.example .env
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Set `COC_API_TOKEN` in `.env` before running the poller.

## Run

Seed the current top 200 snapshot:

```bash
python poll_legends.py seed
```

Run the hourly poll:

```bash
python poll_legends.py poll
```

Or use the launcher script:

```bash
./run_hourly_poll.sh
```

To poll, publish, commit, and push in one step:

```bash
./run_hourly_sync.sh
```

Publish the latest raw files into the GitHub Pages site:

```bash
python poll_legends.py publish
```

## Cron

Example hourly cron entry:

```cron
0 * * * * cd /Users/daniel/clash-legends-stats && . .venv/bin/activate && python poll_legends.py poll >> work/tracker_data/cron.log 2>&1
```

If you want the site to update on every successful poll, run the sync helper from cron:

```cron
0 * * * * cd /Users/daniel/clash-legends-stats && ./run_hourly_sync.sh >> work/tracker_data/cron.log 2>&1
```

## Launchd

On macOS, the actual hourly job can run as a LaunchAgent:

```bash
launchctl bootstrap gui/$(id -u) /Users/daniel/Library/LaunchAgents/com.daniel.clash-legends-stats.sync.plist
launchctl enable gui/$(id -u)/com.daniel.clash-legends-stats.sync
launchctl kickstart -k gui/$(id -u)/com.daniel.clash-legends-stats.sync
```

To stop it later:

```bash
launchctl bootout gui/$(id -u) /Users/daniel/Library/LaunchAgents/com.daniel.clash-legends-stats.sync.plist
```

Logs land in `work/tracker_data/launchd.log` and `work/tracker_data/launchd.err`.

## GitHub Pages

The repo includes a Pages workflow at `.github/workflows/pages.yml`. Once this repository is on GitHub and Pages is enabled for the repo, pushing updated `site/` files to `main` will deploy the site automatically.

The intended flow is:

1. Run the hourly poll locally.
2. Run `python poll_legends.py publish`.
3. Commit the updated `site/` files.
4. Push to GitHub.
5. GitHub Pages serves the refreshed site.
