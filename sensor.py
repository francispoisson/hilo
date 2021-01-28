"""Platform for sensor integration."""
from homeassistant.const import POWER_WATT
from homeassistant.helpers.entity import Entity

from homeassistant.components.sensor import (ENTITY_ID_FORMAT)

from datetime import timedelta

from . import DOMAIN

SCAN_INTERVAL = timedelta(seconds=60)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    h = hass.data[DOMAIN]
    
    for i in range(len(h.d)):
        if(h.d[i].deviceType == 'Meter'):
            add_entities([PowerSensor(h, h.d[i],i)])

class PowerSensor(Entity):
    """Representation of a sensor."""

    def __init__(self, h, d, index):
        self.index = index
        self.entity_id = ENTITY_ID_FORMAT.format(d.deviceId)
        self._name = d.name
        
        self._d = d
        
        self._h = h
        
        self._should_poll = True

    @property
    def name(self):
        """Return the precision of the system."""
        return self._d.name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._d.Power
    
    @property    
    def device_class(self):
        """Return the device class of the sensor."""
        return 'power'

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return POWER_WATT

    def update(self):
        self._h.update_device(self.index)
        self._d = self._h.d[self.index] 

        self._state  = self._d.Power
