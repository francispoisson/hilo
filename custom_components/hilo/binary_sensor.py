from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT
import logging
from .const import DOMAIN, HILO_SENSOR_CLASSES
from .hilo_device import HiloBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    entities = []
    for d in hass.data[DOMAIN].devices:
        if d.device_type in HILO_SENSOR_CLASSES:
            d._entity = HiloSensor(d, hass.data[DOMAIN].scan_interval)
            entities.append(d._entity)
    async_add_entities(entities)


class HiloSensor(HiloBaseEntity, BinarySensorEntity):
    def __init__(self, d, scan_interval):
        super().__init__(d, scan_interval)
        if d.name == "SmartEnergyMeter":
            self._name = "Defi Hilo"
        else:
            self._name = d.name
        _LOGGER.debug(
            f"Setting up BinarySensor entity: {self._name} Scan: {scan_interval}"
        )
        self._state = False

    @property
    def state(self):
        return "on" if self._state else "off"

    async def _async_update(self):
        if self.d.name == "SmartEnergyMeter":
            self._state = await self.d._h.get_events()
        elif self.d.name == "hilo_gateway":
            await self.d.async_update_device()
            self._state = self.d.onlineStatus == "Online"
