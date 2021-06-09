from homeassistant.components.light import (ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, PLATFORM_SCHEMA, LightEntity)

from datetime import timedelta

import logging

_LOGGER = logging.getLogger(__name__)

from . import DOMAIN

SCAN_IMTERVAL = timedelta(seconds=15)

def setup_platform(hass, config, add_entities, discovery_info=None):
    for i in range(len(hass.data[DOMAIN].d)):
        if(hass.data[DOMAIN].d[i].deviceType == 'LightDimmer'):
            add_entities([HiloDimmer(hass.data[DOMAIN], i)])

class HiloDimmer(LightEntity):
    def __init__(self, h, index):
        self.index = index
        #self.entity_id = ENTITY_ID_FORMAT.format('switch_' + str(h.d[index].deviceId))
        self._name = h.d[index].name
        self._state = None
        self._brightness = None
        
        self._h = h
        
        self._should_poll = True

    @property
    def name(self):
        return self._h.d[self.index].name

    @property
    def is_on(self):
        return self._state

    @property
    def brightness(self):
        """Return the brightness of the light.
        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        self._brightness = self._h.d[self.index].Intensity/100*255

        return self._brightness        
 
    @property
    def should_poll(self) -> bool:        
        return True

    @property
    def supported_features(self):
        """Flag supported features."""
        supports = SUPPORT_BRIGHTNESS
        return supports

    def turn_on(self, **kwargs):
        self._h.set_attribute('Intensity', kwargs[ATTR_BRIGHTNESS]/255*100, self.index)
        self._h.set_attribute('OnOff', 'True', self.index)
        self._h.d[self.index].OnOff = True
        self._state = True
    
    def turn_off(self, **kwargs):
        self._h.set_attribute('OnOff', 'False', self.index)
        self._h.d[self.index].OnOff = False
        self._state = False

    def update(self):
        #self._h.update()

        self._brightness = self._h.d[self.index].Intensity/100*255

        if(self._h.d[self.index].OnOff == 'True'):
            self._state = True
        if(self._h.d[self.index].OnOff == 'False'):
            self._state = False
        return self._state