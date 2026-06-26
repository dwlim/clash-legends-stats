from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "work" / "tracker_data"
SITE_DIR = PROJECT_ROOT / "site"
SITE_DATA_DIR = SITE_DIR / "data"
SNAPSHOT_DIR = DATA_DIR / "snapshots"
POLL_DIR = DATA_DIR / "polls"
DAILY_DIR = DATA_DIR / "daily"
DAILY_SEEN_DIR = DATA_DIR / "daily_seen"
EXPORT_DIR = DATA_DIR / "exports"
REPORT_DIR = DATA_DIR / "reports"
STATE_PATH = DATA_DIR / "state.json"

BASE_URL = "https://api.clashofclans.com/v1"
TOP_N = 200
LEGEND_RESET_HOUR_UTC = 5
MAX_ATTACKS_PER_PLAYER = 8
