"""Platform for sensor integration."""
from homeassistant.components.binary_sensor import BinarySensorEntity

import logging

from homeassistant.components.sensor import (ENTITY_ID_FORMAT)

from datetime import timedelta

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
            
    add_entities([HiloEvent(hass.data[DOMAIN], 1)])

class HiloEvent(BinarySensorEntity):
    """Representation of a sensor."""

    def __init__(self, h, index):
        self.index = index
        self._name = 'Défi Hilo'
        self._state = None
        
        self._h = h
        
        #self._is_on = self._h.is_event
        
        self._should_poll = True

    @property
    def name(self):
        """Return the precision of the system."""
        return self._name

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def should_poll(self) -> bool:        
        return True
    
    @property    
    def device_class(self):
        """Return the device class of the sensor."""
        return None

    def update(self):
        self._h.update()
        #return
        #_LOGGER.warning( "binary")
        #if(self._h.is_event == True):
            #_LOGGER.warning( "True")
        #else:
            #_LOGGER.warning( "False")

        #self._state = self._h.is_event
        return self._state