"""Sensor platform for Avinor flight data."""

from __future__ import annotations

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import async_ensure_setup, register_coordinator, unregister_coordinator
from .coordinator import AvinorDataCoordinator

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Avinor Flight Data"
CONF_AIRPORT = "airport"
CONF_DIRECTION = "direction"
CONF_TIME_FROM = "time_from"
CONF_TIME_TO = "time_to"
CONF_SEARCH_TEXT = "search_text"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_AIRPORT, default="TOS"): cv.string,
        vol.Optional(CONF_DIRECTION, default="A"): cv.string,
        vol.Optional(CONF_TIME_FROM, default="0"): cv.string,
        vol.Optional(CONF_TIME_TO, default="7"): cv.string,
        vol.Optional(CONF_SEARCH_TEXT, default=""): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Synchronous fallback that delegates to async setup."""

    def _async_add_entities(entities, update_before_add=False):
        add_entities(entities, update_before_add)

    hass.async_create_task(
        async_setup_platform(hass, config, _async_add_entities, discovery_info)
    )


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Avinor Flight Data sensor from YAML."""
    await async_ensure_setup(hass)

    name = config.get(CONF_NAME)
    coordinator = AvinorDataCoordinator(
        hass,
        params={
            "airport": config.get(CONF_AIRPORT),
            "direction": config.get(CONF_DIRECTION),
            "time_from": config.get(CONF_TIME_FROM),
            "time_to": config.get(CONF_TIME_TO),
            "search_text": config.get(CONF_SEARCH_TEXT),
        },
    )

    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        _LOGGER.warning("Initial Avinor data refresh failed")

    async_add_entities([AvinorFlightDataSensor(name, coordinator)])


class AvinorFlightDataSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Avinor Flight Data sensor."""

    _attr_icon = "mdi:airplane"

    def __init__(self, name, coordinator: AvinorDataCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = name

    @property
    def native_value(self):
        """Return the number of flights."""
        return len(self.coordinator.data or [])

    @property
    def extra_state_attributes(self):
        """Expose all flights in the sensor attributes."""
        return {"flights": self.coordinator.data or []}

    async def async_added_to_hass(self) -> None:
        """Register the entity's coordinator when added to Home Assistant."""
        await super().async_added_to_hass()
        if self.entity_id:
            register_coordinator(self.hass, self.entity_id, self.coordinator)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister the entity's coordinator when removed."""
        if self.entity_id:
            unregister_coordinator(self.hass, self.entity_id)
        await super().async_will_remove_from_hass()
