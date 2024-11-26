import logging
from datetime import timedelta  # Add this line if it's missing
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
import voluptuous as vol


_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Avinor Flight Data"
SCAN_INTERVAL = timedelta(minutes=5)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Avinor Flight Data sensor."""
    name = config.get(CONF_NAME)

    coordinator = hass.data['avinor_coordinator']
    add_entities([AvinorFlightDataSensor(name, coordinator)], True)

class AvinorFlightDataSensor(SensorEntity):
    """Representation of an Avinor Flight Data sensor."""

    def __init__(self, name, coordinator):
        """Initialize the sensor."""
        self._name = name
        self.coordinator = coordinator
        self._state = None
        self._attributes = {}
        self.coordinator_context = object()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the number of flights."""
        return len(self.coordinator.data) if self.coordinator.data else 0

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {"flights": self.coordinator.data}

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """When entity is about to be removed from hass."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await self.coordinator.async_request_refresh()
