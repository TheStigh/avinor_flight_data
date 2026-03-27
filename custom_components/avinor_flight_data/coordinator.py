"""Data coordinator for Avinor Flight Data."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from asyncio import TimeoutError
from datetime import timedelta
from typing import Any

from aiohttp import ClientError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

API_URL = "https://asrv.avinor.no/XmlFeed/v1.0"
SCAN_INTERVAL = timedelta(minutes=5)

_LOGGER = logging.getLogger(__name__)


class AvinorDataCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Fetch and hold Avinor flight data."""

    def __init__(self, hass, params: dict[str, str] | None = None) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Avinor Flight Data",
            update_interval=SCAN_INTERVAL,
        )
        self.session = async_get_clientsession(hass)
        self.params: dict[str, str] = {
            "airport": "TOS",
            "time_from": "0",
            "time_to": "7",
            "direction": "A",
            "search_text": "",
        }
        if params:
            self.params.update(params)

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch and parse flight data from Avinor."""
        request_params = {
            "airport": self.params["airport"],
            "TimeFrom": self.params["time_from"],
            "TimeTo": self.params["time_to"],
            "direction": self.params["direction"],
        }

        try:
            async with self.session.get(
                API_URL,
                params=request_params,
                timeout=10,
            ) as response:
                response.raise_for_status()
                payload = await response.text()
        except (ClientError, TimeoutError) as err:
            raise UpdateFailed(f"API request failed: {err}") from err

        try:
            root = ET.fromstring(payload)
        except ET.ParseError as err:
            raise UpdateFailed(f"Invalid XML from API: {err}") from err

        flights: list[dict[str, Any]] = []
        search_text = (self.params.get("search_text") or "").strip().lower() or None

        for flight in root.findall(".//flight"):
            flight_info = self._parse_flight(flight)
            if search_text and search_text not in self._flight_search_blob(flight_info):
                continue
            flights.append(flight_info)

        return flights

    @staticmethod
    def _parse_flight(flight: ET.Element) -> dict[str, Any]:
        """Extract relevant fields from a flight XML node."""
        status_node = flight.find("status")

        return {
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

    @staticmethod
    def _flight_search_blob(flight_info: dict[str, Any]) -> str:
        """Flatten flight fields into a lowercase search string."""
        flattened_parts: list[str] = []
        for value in flight_info.values():
            if isinstance(value, dict):
                flattened_parts.extend(str(v).lower() for v in value.values() if v)
            elif value:
                flattened_parts.append(str(value).lower())

        return " ".join(flattened_parts)


def _find_text(node: ET.Element, *tags: str) -> str | None:
    """Return first non-empty XML text for a set of tag candidates."""
    for tag in tags:
        value = node.findtext(tag)
        if value:
            return value
    return None
