"""Platform for sensor integration."""
from homeassistant.const import POWER_WATT
from homeassistant.helpers.entity import Entity

from homeassistant.components.sensor import (ENTITY_ID_FORMAT)

from datetime import timedelta

from . import DOMAIN

SCAN_INTERVAL = timedelta(seconds=15)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
            
    for i in range(len(hass.data[DOMAIN].d)):
        add_entities([PowerSensor(hass.data[DOMAIN], i)])

class PowerSensor(Entity):
    """Representation of a sensor."""

    def __init__(self, h, index):
        self.index = index
        #self.entity_id = ENTITY_ID_FORMAT.format(h.d[index].deviceId)
        self._name = h.d[index].name
        
        self._h = h
        
        self._should_poll = True

    @property
    def name(self):
        """Return the precision of the system."""
        return self._h.d[self.index].name

    @property
    def should_poll(self) -> bool:        
        return True

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._h.d[self.index].Power is None:
            return '0'
        else:
            power_int = int(self._h.d[self.index].Power)
            round_power = round(power_int)
            return str(round_power)
    
    @property    
    def device_class(self):
        """Return the device class of the sensor."""
        return 'power'

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return POWER_WATT

    def update(self):
        return
        #self._h.update()
        if self._h.d[self.index].Power is None:
            self._state  = '0'
        else:
            power_int = int(self._h.d[self.index].Power)
            round_power = round(power_int)
            self._state  = str(round_power)
        return self._state
