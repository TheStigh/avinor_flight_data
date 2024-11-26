import voluptuous as vol
from homeassistant.helpers import config_validation as cv

# Import the coordinator
from .coordinator import AvinorDataCoordinator

async def async_setup(hass, config):
    """Set up the Avinor Flight Data component."""
    coordinator = AvinorDataCoordinator(hass)
    hass.data['avinor_coordinator'] = coordinator

    async def update_parameters_service(call):
        """Handle the service call to update parameters."""
        coordinator.params['airport'] = call.data.get('airport', coordinator.params['airport'])
        coordinator.params['direction'] = call.data.get('direction', coordinator.params['direction'])
        coordinator.params['timeFrom'] = call.data.get('time_from', coordinator.params['timeFrom'])
        coordinator.params['timeTo'] = call.data.get('time_to', coordinator.params['timeTo'])
        coordinator.params['searchText'] = call.data.get('search_text', coordinator.params['searchText'])
        await coordinator.async_request_refresh()

    hass.services.async_register(
        'avinor_flight_data',
        'update_parameters',
        update_parameters_service,
        schema=vol.Schema({
            vol.Optional('airport'): cv.string,
            vol.Optional('direction'): cv.string,
            vol.Optional('time_from'): cv.string,
            vol.Optional('time_to'): cv.string,
            vol.Optional('search_text'): cv.string,
            vol.Required('entity_id'): cv.entity_id,
        })
    )

    return True
