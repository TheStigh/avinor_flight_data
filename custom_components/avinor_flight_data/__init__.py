"""Avinor Flight Data integration setup and services."""

from __future__ import annotations

import logging
from collections.abc import MutableMapping
from typing import Any

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

DOMAIN = "avinor_flight_data"
SERVICE_UPDATE_PARAMETERS = "update_parameters"

DATA_COORDINATORS = "coordinators"
DATA_SERVICE_REGISTERED = "service_registered"

ATTR_AIRPORT = "airport"
ATTR_DIRECTION = "direction"
ATTR_ENTITY_ID = "entity_id"
ATTR_TIME_FROM = "time_from"
ATTR_TIME_TO = "time_to"
ATTR_SEARCH_TEXT = "search_text"

_LOGGER = logging.getLogger(__name__)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTITY_ID): cv.entity_id,
        vol.Optional(ATTR_AIRPORT): cv.string,
        vol.Optional(ATTR_DIRECTION): cv.string,
        vol.Optional(ATTR_TIME_FROM): cv.string,
        vol.Optional(ATTR_TIME_TO): cv.string,
        vol.Optional(ATTR_SEARCH_TEXT): cv.string,
    }
)


async def async_setup(hass, config):
    """Set up the Avinor Flight Data integration."""
    await async_ensure_setup(hass)
    return True


async def async_ensure_setup(hass) -> None:
    """Ensure integration data structures and services are initialized."""
    domain_data = hass.data.setdefault(
        DOMAIN,
        {
            DATA_COORDINATORS: {},
            DATA_SERVICE_REGISTERED: False,
        },
    )

    if domain_data[DATA_SERVICE_REGISTERED]:
        return

    async def update_parameters_service(call) -> None:
        """Update parameters for a target coordinator and refresh data."""
        coordinator = _resolve_service_coordinator(hass, call.data)
        if coordinator is None:
            return

        coordinator.params[ATTR_AIRPORT] = call.data.get(
            ATTR_AIRPORT, coordinator.params[ATTR_AIRPORT]
        )
        coordinator.params[ATTR_DIRECTION] = call.data.get(
            ATTR_DIRECTION, coordinator.params[ATTR_DIRECTION]
        )
        coordinator.params[ATTR_TIME_FROM] = call.data.get(
            ATTR_TIME_FROM, coordinator.params[ATTR_TIME_FROM]
        )
        coordinator.params[ATTR_TIME_TO] = call.data.get(
            ATTR_TIME_TO, coordinator.params[ATTR_TIME_TO]
        )
        coordinator.params[ATTR_SEARCH_TEXT] = call.data.get(
            ATTR_SEARCH_TEXT, coordinator.params[ATTR_SEARCH_TEXT]
        )
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_PARAMETERS,
        update_parameters_service,
        schema=SERVICE_SCHEMA,
    )
    domain_data[DATA_SERVICE_REGISTERED] = True


def register_coordinator(hass, entity_id: str, coordinator) -> None:
    """Register a coordinator for service targeting."""
    domain_data: MutableMapping[str, Any] = hass.data.setdefault(
        DOMAIN,
        {
            DATA_COORDINATORS: {},
            DATA_SERVICE_REGISTERED: False,
        },
    )
    domain_data[DATA_COORDINATORS][entity_id] = coordinator


def unregister_coordinator(hass, entity_id: str) -> None:
    """Unregister a coordinator when an entity is removed."""
    domain_data = hass.data.get(DOMAIN)
    if not domain_data:
        return
    domain_data[DATA_COORDINATORS].pop(entity_id, None)


def _resolve_service_coordinator(hass, service_data):
    """Find the coordinator targeted by a service call."""
    domain_data = hass.data.get(DOMAIN)
    if not domain_data:
        _LOGGER.warning("Service called before Avinor integration setup completed")
        return None

    coordinators = domain_data[DATA_COORDINATORS]
    entity_id = service_data.get(ATTR_ENTITY_ID)

    if entity_id:
        coordinator = coordinators.get(entity_id)
        if coordinator is None:
            _LOGGER.warning(
                "No Avinor coordinator found for entity_id '%s'.",
                entity_id,
            )
        return coordinator

    if len(coordinators) == 1:
        return next(iter(coordinators.values()))

    if not coordinators:
        _LOGGER.warning("No Avinor entities are currently registered.")
    else:
        _LOGGER.warning(
            "Multiple Avinor entities found; include entity_id in service call."
        )
    return None
