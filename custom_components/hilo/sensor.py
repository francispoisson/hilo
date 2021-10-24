from homeassistant.const import POWER_WATT
from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import logging
_LOGGER = logging.getLogger(__name__)
from .const import DOMAIN
from .hilo_device import HiloBaseEntity



async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    entities = []
    for d in hass.data[DOMAIN].devices:
        if "Power" in d.supported_attributes:
            d._entity = PowerSensor(d)
            entities.append(d._entity)
    async_add_entities(entities)

class PowerSensor(HiloBaseEntity, Entity):
    def __init__(self, d):
        self._name = d.name
        self._should_poll = True
        self.d = d
        _LOGGER.debug(f"Setting up PowerSensor entity: {self._name}")

    @property
    def state(self):
        return str(int(self._get('Power', 0)))

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def device_class(self):
        return "power"

    @property
    def unit_of_measurement(self):
        return POWER_WATT

    async def _async_update(self):
        return
