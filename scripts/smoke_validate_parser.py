"""Standalone smoke test for Avinor XML parsing."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def _find_text(node: ET.Element, *tags: str) -> str | None:
    """Return first non-empty XML text for a set of tag candidates."""
    for tag in tags:
        value = node.findtext(tag)
        if value:
            return value
    return None


def parse_flights(xml_text: str, search_text: str | None = None) -> list[dict[str, Any]]:
    """Parse Avinor XML into flight dictionaries."""
    root = ET.fromstring(xml_text)
    flights: list[dict[str, Any]] = []
    normalized_search = (search_text or "").strip().lower() or None

    for flight in root.findall(".//flight"):
        status_node = flight.find("status")
        flight_info = {
            "uniqueID": flight.get("uniqueID") or flight.get("uniqueId"),
            "airline": _find_text(flight, "airline"),
            "flight_id": _find_text(flight, "flight_id", "flightId"),
            "dom_int": _find_text(flight, "dom_int"),
            "schedule_time": _find_text(flight, "schedule_time"),
            "arr_dep": _find_text(flight, "arr_dep"),
            "airport": _find_text(flight, "airport"),
            "status": {
                "code": status_node.get("code") if status_node is not None else None,
                "time": status_node.get("time") if status_node is not None else None,
            },
        }

        if normalized_search:
            blob = _search_blob(flight_info)
            if normalized_search not in blob:
                continue
        flights.append(flight_info)

    return flights


def _search_blob(flight_info: dict[str, Any]) -> str:
    """Flatten flight fields into a lowercase search string."""
    flattened_parts: list[str] = []
    for value in flight_info.values():
        if isinstance(value, dict):
            flattened_parts.extend(str(v).lower() for v in value.values() if v)
        elif value:
            flattened_parts.append(str(value).lower())
    return " ".join(flattened_parts)


def run_smoke_checks(flights: list[dict[str, Any]]) -> None:
    """Run minimal parser checks and raise on failure."""
    if not flights:
        raise ValueError("No flights parsed from XML")

    required_fields = ("flight_id", "airline", "schedule_time", "airport")
    for idx, flight in enumerate(flights):
        missing = [field for field in required_fields if not flight.get(field)]
        if missing:
            raise ValueError(f"Flight #{idx} missing fields: {', '.join(missing)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test Avinor XML parser.")
    parser.add_argument(
        "--sample",
        default="scripts/sample_avinor_response.xml",
        help="Path to XML sample file.",
    )
    parser.add_argument(
        "--search",
        default=None,
        help="Optional search text filter.",
    )
    parser.add_argument(
        "--print-first",
        action="store_true",
        help="Print the first parsed flight as JSON.",
    )
    args = parser.parse_args()

    sample_path = Path(args.sample)
    if not sample_path.exists():
        raise FileNotFoundError(f"Sample file not found: {sample_path}")

    xml_text = sample_path.read_text(encoding="utf-8")
    flights = parse_flights(xml_text, search_text=args.search)
    run_smoke_checks(flights)

    print(f"OK: parsed {len(flights)} flight(s) from {sample_path}")
    if args.print_first:
        print(json.dumps(flights[0], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
