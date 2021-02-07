from homeassistant.helpers.entity import ToggleEntity

from homeassistant.components.sensor import (ENTITY_ID_FORMAT)

from datetime import timedelta

import logging

_LOGGER = logging.getLogger(__name__)

from . import DOMAIN

SCAN_IMTERVAL = timedelta(seconds=15)

def setup_platform(hass, config, add_entities, discovery_info=None):
    for i in range(len(hass.data[DOMAIN].d)):
        if(hass.data[DOMAIN].d[i].deviceType == 'LightSwitch'):
            add_entities([HiloSwitch(hass.data[DOMAIN], i)])

class HiloSwitch(ToggleEntity):
    def __init__(self, h, index):
        self.index = index
        #self.entity_id = ENTITY_ID_FORMAT.format('switch_' + str(h.d[index].deviceId))
        self._name = h.d[index].name
        self._state = None
        
        self._h = h
        
        self._should_poll = True

    @property
    def name(self):
        return self._h.d[self.index].name

    @property
    def is_on(self):
        return self._state
        
 
    @property
    def should_poll(self) -> bool:        
        return True

    def turn_on(self, **kwargs):
        self._h.set_attribute('OnOff', 'True', self.index)
        self._h.d[self.index].OnOff = True
        self._state = True
    
    def turn_off(self, **kwargs):
        self._h.set_attribute('OnOff', 'False', self.index)
        self._h.d[self.index].OnOff = False
        self._state = False

    def update(self):
        #self._h.update()

        if(self._h.d[self.index].OnOff == 'True'):
            self._state = True
        if(self._h.d[self.index].OnOff == 'False'):
            self._state = False
        return self._state