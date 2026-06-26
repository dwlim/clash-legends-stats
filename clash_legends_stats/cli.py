from __future__ import annotations

import argparse
import json

from .site_publisher import publish_site_data
from .poller import poll, seed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clash Legends Stats hourly poller")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("poll", help="Poll the tracked top 200 Legends players")
    subparsers.add_parser("seed", help="Seed a top 200 snapshot for the current Legends day")
    subparsers.add_parser("publish", help="Publish the latest data files into the GitHub Pages site")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "poll":
        result = poll()
    elif args.command == "seed":
        result = seed()
    elif args.command == "publish":
        result = publish_site_data()
    else:
        parser.error(f"Unknown command: {args.command}")
        return 2

    print(json.dumps(result, indent=2))
    return 0
