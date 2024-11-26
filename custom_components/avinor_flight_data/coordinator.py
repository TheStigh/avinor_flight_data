import logging
import requests
import xml.etree.ElementTree as ET
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=5)

class AvinorDataCoordinator(DataUpdateCoordinator):
    """Data coordinator to fetch flight data."""

    def __init__(self, hass):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name="Avinor Flight Data",
            update_interval=SCAN_INTERVAL,
        )
        self.params = {
            "airport": "TOS",
            "timeFrom": "0",
            "timeTo": "7",
            "direction": "A",
            "searchText": ""
        }

    async def _async_update_data(self):
        """Fetch data from Avinor."""
        url = (
            f"https://flydata.avinor.no/XmlFeed.asp?"
            f"airport={self.params['airport']}&"
            f"timeFrom={self.params['timeFrom']}&"
            f"timeTo={self.params['timeTo']}&"
            f"direction={self.params['direction']}"
        )
        try:
            response = await self.hass.async_add_executor_job(
                requests.get, url, {'timeout': 10}
            )
            response.raise_for_status()
            root = ET.fromstring(response.content)

            flights = []
            search_text = self.params['searchText'].lower() if self.params['searchText'] else None

            for flight in root.findall(".//flight"):
                # Build the flight_info dictionary based on the provided XML example
                flight_info = {
                    "uniqueID": flight.get("uniqueID"),
                    "airline": flight.findtext("airline"),
                    "flight_id": flight.findtext("flight_id"),
                    "dom_int": flight.findtext("dom_int"),
                    "schedule_time": flight.findtext("schedule_time"),
                    "arr_dep": flight.findtext("arr_dep"),
                    "airport": flight.findtext("airport"),
                    "status": {
                        "code": flight.find("status").get("code") if flight.find("status") is not None else None,
                        "time": flight.find("status").get("time") if flight.find("status") is not None else None,
                    },
                    # Add other elements as needed
                }

                # Convert all values to strings and concatenate them for search
                flight_text = ' '.join(
                    str(value).lower() if not isinstance(value, dict) else ' '.join(str(v).lower() for v in value.values() if v)
                    for value in flight_info.values() if value
                )

                # Check if the search text is in the flight text
                if search_text and search_text not in flight_text:
                    continue  # Skip this flight if it doesn't match the search

                flights.append(flight_info)

            return flights

        except Exception as error:
            raise UpdateFailed(f"Error fetching data: {error}") from error
