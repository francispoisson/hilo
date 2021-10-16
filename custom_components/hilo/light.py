from homeassistant.components.light import (ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, PLATFORM_SCHEMA, LightEntity)

from datetime import timedelta

import logging

_LOGGER = logging.getLogger(__name__)

from . import DOMAIN

SCAN_IMTERVAL = timedelta(seconds=15)

def setup_platform(hass, config, add_entities, discovery_info=None):
    for i, d in hass.data[DOMAIN].d.items():
        if(d.deviceType in ['LightDimmer', 'WhiteBulb', 'ColorBulb']):
            add_entities([HiloDimmer(hass.data[DOMAIN], i)])
    return True

class HiloDimmer(LightEntity):
    def __init__(self, h, index):
        self.index = index
        #self.entity_id = ENTITY_ID_FORMAT.format('switch_' + str(h.d[index].deviceId))
        self._name = h.d[index].name
        self._state = h.d[index].OnOff
        self._brightness = h.d[index].Intensity*255
        self._h = h
        self._should_poll = True
        _LOGGER.debug(f"Setting up Dimmer entity: {self._name}")

    @property
    def name(self):
        return self._h.d[self.index].name

    @property
    def is_on(self):
        return self._h.d[self.index].OnOff

    @property
    def brightness(self):
        return self._h.d[self.index].Intensity*255

    @property
    def available(self):
        return not self._h.d[self.index].Disconnected

    @property
    def should_poll(self) -> bool:        
        return True

    @property
    def supported_features(self):
        """Flag supported features."""
        supports = SUPPORT_BRIGHTNESS
        return supports

    def turn_on(self, **kwargs):
        _LOGGER.info(f"[{self.name}] Tunring on")
        self._h.set_attribute('OnOff', True, self.index)
        if ATTR_BRIGHTNESS in kwargs:
            _LOGGER.info(f"[{self._name}] Setting brightness to {kwargs[ATTR_BRIGHTNESS]}")
            self._h.set_attribute('Intensity', kwargs[ATTR_BRIGHTNESS]/255, self.index)
        return self.is_on
    
    def turn_off(self, **kwargs):
        _LOGGER.info(f"[{self.name}] Turning off")
        self._h.set_attribute('OnOff', False, self.index)
        return self.is_on

    def update(self):
        return self.is_on
