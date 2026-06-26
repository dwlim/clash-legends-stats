from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .army_decoder import build_site_payload, load_jsonl
from .settings import DAILY_DIR, SNAPSHOT_DIR, SITE_DATA_DIR, SITE_DIR


def ensure_site_dirs() -> None:
    (SITE_DATA_DIR / "daily").mkdir(parents=True, exist_ok=True)
    (SITE_DATA_DIR / "snapshots").mkdir(parents=True, exist_ok=True)
    (SITE_DATA_DIR / "days").mkdir(parents=True, exist_ok=True)


def latest_daily_path() -> Path | None:
    files = sorted(DAILY_DIR.glob("legend_*.jsonl"))
    return files[-1] if files else None


def latest_snapshot_path() -> Path | None:
    files = sorted(SNAPSHOT_DIR.glob("top200_*.json"))
    return files[-1] if files else None


def copy_tree(src_dir: Path, dest_dir: Path, pattern: str) -> list[str]:
    copied: list[str] = []
    for src in sorted(src_dir.glob(pattern)):
        dest = dest_dir / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied.append(str(dest.relative_to(SITE_DIR)))
    return copied


def write_manifest(daily_path: Path | None, snapshot_path: Path | None, site_payload_path: Path | None) -> Path:
    days: list[dict[str, Any]] = []
    for daily_file in sorted(DAILY_DIR.glob("legend_*.jsonl")):
        date = daily_file.stem.removeprefix("legend_")
        payload_path = Path("data") / "days" / f"{date}.json"
        snapshot_name = f"top200_{date}.json"
        snapshot_rel = Path("data") / "snapshots" / snapshot_name
        days.append(
            {
                "date": date,
                "daily": str(Path("data") / "daily" / daily_file.name),
                "snapshot": str(snapshot_rel) if (SNAPSHOT_DIR / snapshot_name).exists() else None,
                "payload": str(payload_path),
            }
        )
    manifest: dict[str, Any] = {
        "published_at": datetime.now(timezone.utc).isoformat(),
        "latest_daily": str(Path("data") / "daily" / daily_path.name) if daily_path else None,
        "latest_snapshot": str(Path("data") / "snapshots" / snapshot_path.name) if snapshot_path else None,
        "site_payload": str(Path("data") / site_payload_path.name) if site_payload_path else None,
        "days": days,
    }
    path = SITE_DATA_DIR / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
    return path


def build_site_json(daily_path: Path | None, snapshot_path: Path | None) -> Path | None:
    if not daily_path or not snapshot_path:
        return None
    snapshot = json.loads(snapshot_path.read_text())
    daily_attacks = load_jsonl(daily_path)
    tracking_day = str(snapshot.get("tracking_day") or daily_path.stem.removeprefix("legend_"))
    payload = build_site_payload(snapshot, daily_attacks, tracking_day)
    out_path = SITE_DATA_DIR / "site.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return out_path


def build_day_payloads() -> list[str]:
    payload_paths: list[str] = []
    for daily_file in sorted(DAILY_DIR.glob("legend_*.jsonl")):
        date = daily_file.stem.removeprefix("legend_")
        snapshot_path = SNAPSHOT_DIR / f"top200_{date}.json"
        if not snapshot_path.exists():
            continue
        snapshot = json.loads(snapshot_path.read_text())
        daily_attacks = load_jsonl(daily_file)
        payload = build_site_payload(snapshot, daily_attacks, date)
        out_path = SITE_DATA_DIR / "days" / f"{date}.json"
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        payload_paths.append(str(out_path.relative_to(SITE_DIR)))
    return payload_paths


def publish_site_data() -> dict[str, Any]:
    ensure_site_dirs()
    daily_copies = copy_tree(DAILY_DIR, SITE_DATA_DIR / "daily", "legend_*.jsonl")
    snapshot_copies = copy_tree(SNAPSHOT_DIR, SITE_DATA_DIR / "snapshots", "top200_*.json")
    day_payloads = build_day_payloads()
    daily_path = latest_daily_path()
    snapshot_path = latest_snapshot_path()
    site_payload_path = build_site_json(daily_path, snapshot_path)
    manifest_path = write_manifest(daily_path, snapshot_path, site_payload_path)
    return {
        "site_data_dir": str(SITE_DATA_DIR),
        "manifest_path": str(manifest_path),
        "site_payload_path": str(site_payload_path) if site_payload_path else None,
        "daily_files": daily_copies,
        "snapshot_files": snapshot_copies,
        "day_payloads": day_payloads,
        "latest_daily": str(daily_path) if daily_path else None,
        "latest_snapshot": str(snapshot_path) if snapshot_path else None,
    }
