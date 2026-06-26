from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

from dotenv import load_dotenv

from .client import ClashApiClient
from .settings import (
    DATA_DIR,
    DAILY_DIR,
    DAILY_SEEN_DIR,
    LEGEND_RESET_HOUR_UTC,
    MAX_ATTACKS_PER_PLAYER,
    SNAPSHOT_DIR,
    STATE_PATH,
    TOP_N,
)


@dataclass
class TrackerConfig:
    token: str


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_SEEN_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> TrackerConfig:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    token = os.getenv("COC_API_TOKEN", "").strip()
    if not token:
        raise SystemExit("COC_API_TOKEN is not set. Put it in ~/clash-legends-stats/.env")
    return TrackerConfig(token=token)


def load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {
        "active_tracking_day": None,
        "last_poll_at": None,
        "last_snapshot_at": None,
    }


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True))


def tracking_day_for(now_utc: datetime | None = None) -> str:
    now_utc = now_utc or datetime.now(timezone.utc)
    adjusted = now_utc - timedelta(hours=LEGEND_RESET_HOUR_UTC)
    return adjusted.date().isoformat()


def tracking_window_for(tracking_day: str) -> tuple[datetime, datetime]:
    start = datetime.fromisoformat(f"{tracking_day}T05:00:00+00:00")
    end = start + timedelta(days=1)
    return start, end


def api_player_tag(tag: str) -> str:
    return quote(tag, safe="")


def fetch_top_players(client: ClashApiClient, limit: int = TOP_N) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    after: str | None = None
    while len(items) < limit:
        params: dict[str, Any] = {"limit": min(100, limit - len(items))}
        if after:
            params["after"] = after
        payload = client.get_json("/locations/global/rankings/players", params=params)
        batch = payload.get("items", [])
        if not batch:
            break
        items.extend(batch)
        after = payload.get("paging", {}).get("cursors", {}).get("after")
        if not after:
            break
    return items[:limit]


def write_snapshot(tracking_day: str, players: list[dict[str, Any]], seeded_from_current: bool) -> Path:
    out = {
        "tracking_day": tracking_day,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seeded_from_current": seeded_from_current,
        "count": len(players),
        "players": players,
    }
    path = SNAPSHOT_DIR / f"top200_{tracking_day}.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    return path


def read_snapshot(tracking_day: str) -> dict[str, Any]:
    path = SNAPSHOT_DIR / f"top200_{tracking_day}.json"
    if not path.exists():
        raise FileNotFoundError(f"Snapshot not found for {tracking_day}: {path}")
    return json.loads(path.read_text())


def ensure_snapshot(client: ClashApiClient, tracking_day: str) -> Path:
    path = SNAPSHOT_DIR / f"top200_{tracking_day}.json"
    if path.exists():
        return path
    players = fetch_top_players(client, TOP_N)
    return write_snapshot(tracking_day, players, seeded_from_current=True)


def fetch_battlelog(client: ClashApiClient, tag: str) -> list[dict[str, Any]]:
    payload = client.get_json(f"/players/{api_player_tag(tag)}/battlelog")
    return payload.get("items", [])


def timestamp_to_utc(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y%m%dT%H%M%S.000Z").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def is_legend_attack(item: dict[str, Any], window_start: datetime, window_end: datetime) -> bool:
    if item.get("battleType") != "legend" or item.get("attack") is not True:
        return False
    ts = timestamp_to_utc(item.get("battleTimestamp"))
    return bool(ts and window_start <= ts < window_end)


def daily_path_for(tracking_day: str) -> Path:
    return DAILY_DIR / f"legend_{tracking_day}.jsonl"


def seen_path_for(tracking_day: str) -> Path:
    return DAILY_SEEN_DIR / f"legend_{tracking_day}.json"


def attack_signature(tag: str | None, item: dict[str, Any]) -> str:
    return json.dumps(
        {
            "playerTag": tag,
            "battleTimestamp": item.get("battleTimestamp"),
            "opponentPlayerTag": item.get("opponentPlayerTag"),
            "armyShareCode": item.get("armyShareCode"),
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def load_seen_signatures(tracking_day: str) -> set[str]:
    seen_path = seen_path_for(tracking_day)
    if seen_path.exists():
        payload = json.loads(seen_path.read_text())
        if isinstance(payload, list):
            return {str(value) for value in payload}
    daily_path = daily_path_for(tracking_day)
    if not daily_path.exists():
        return set()
    seen: set[str] = set()
    for line in daily_path.read_text().splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        seen.add(
            attack_signature(
                payload.get("playerTag"),
                {
                    "battleTimestamp": payload.get("battleTimestamp"),
                    "opponentPlayerTag": payload.get("opponentTag"),
                    "armyShareCode": payload.get("armyShareCode"),
                },
            )
        )
    return seen


def save_seen_signatures(tracking_day: str, seen: set[str]) -> None:
    seen_path = seen_path_for(tracking_day)
    seen_path.write_text(json.dumps(sorted(seen), indent=2, ensure_ascii=False))


def poll_snapshot(client: ClashApiClient, tracking_day: str) -> tuple[Path, int]:
    snapshot = read_snapshot(tracking_day)
    window_start, window_end = tracking_window_for(tracking_day)
    now = datetime.now(timezone.utc)
    rows: list[dict[str, Any]] = []
    daily_path = daily_path_for(tracking_day)
    seen = load_seen_signatures(tracking_day)
    newly_appended = 0

    for player in snapshot.get("players", []):
        tag = player.get("tag")
        if not isinstance(tag, str) or not tag:
            continue
        try:
            battlelog = fetch_battlelog(client, tag)
            items = [item for item in battlelog if is_legend_attack(item, window_start, window_end)]
            items.sort(key=lambda item: item.get("battleTimestamp") or "")
            items = items[:MAX_ATTACKS_PER_PLAYER]
            new_items = []
            for item in items:
                signature = attack_signature(tag, item)
                if signature in seen:
                    continue
                seen.add(signature)
                new_items.append(item)
                daily_record = {
                    "tracking_day": tracking_day,
                    "polled_at": now.isoformat(),
                    "playerTag": tag,
                    "playerName": player.get("name"),
                    "playerTownHallLevel": player.get("townHallLevel"),
                    "battleTimestamp": item.get("battleTimestamp"),
                    "battleType": item.get("battleType"),
                    "opponentTag": item.get("opponentPlayerTag"),
                    "opponentName": item.get("opponentName"),
                    "opponentTownHallLevel": item.get("opponentTownHallLevel"),
                    "stars": item.get("stars"),
                    "destructionPercentage": item.get("destructionPercentage"),
                    "battleTime": item.get("battleTime"),
                    "armyShareCode": item.get("armyShareCode"),
                    "sourcePollAt": now.isoformat(),
                }
                with daily_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(daily_record, ensure_ascii=False) + "\n")
                newly_appended += 1
            rows.append(
                {
                    "tag": tag,
                    "name": player.get("name"),
                    "townHallLevel": player.get("townHallLevel"),
                    "fetched_at": now.isoformat(),
                    "items": new_items,
                    "new_item_count": len(new_items),
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "tag": tag,
                    "name": player.get("name"),
                    "townHallLevel": player.get("townHallLevel"),
                    "fetched_at": now.isoformat(),
                    "error": str(exc),
                    "items": [],
                }
            )

    state = load_state()
    state["active_tracking_day"] = tracking_day
    state["last_poll_at"] = now.isoformat()
    state["daily_poll_file"] = str(daily_path)
    state["daily_seen_file"] = str(seen_path_for(tracking_day))
    save_seen_signatures(tracking_day, seen)
    save_state(state)
    return daily_path, newly_appended


def poll() -> dict[str, Any]:
    ensure_dirs()
    config = load_config()
    client = ClashApiClient(config.token)
    tracking_day = tracking_day_for()
    snapshot_path = ensure_snapshot(client, tracking_day)
    daily_path, newly_appended = poll_snapshot(client, tracking_day)
    state = load_state()
    state["active_tracking_day"] = tracking_day
    state["last_snapshot_at"] = state.get("last_snapshot_at") or datetime.now(timezone.utc).isoformat()
    save_state(state)
    return {
        "action": "poll",
        "tracking_day": tracking_day,
        "snapshot_path": str(snapshot_path),
        "daily_path": str(daily_path),
        "newly_appended": newly_appended,
    }


def seed() -> dict[str, Any]:
    ensure_dirs()
    config = load_config()
    client = ClashApiClient(config.token)
    tracking_day = tracking_day_for()
    players = fetch_top_players(client, TOP_N)
    snapshot_path = write_snapshot(tracking_day, players, seeded_from_current=True)
    state = load_state()
    state["active_tracking_day"] = tracking_day
    state["last_snapshot_at"] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    return {
        "action": "seed",
        "tracking_day": tracking_day,
        "snapshot_path": str(snapshot_path),
        "count": len(players),
    }
