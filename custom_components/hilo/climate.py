import logging

from . import DOMAIN
import voluptuous as vol
from datetime import timedelta

import homeassistant.helpers.config_validation as cv

from homeassistant.components.climate import (
    PLATFORM_SCHEMA, ENTITY_ID_FORMAT, ClimateEntity)

from homeassistant.components.climate.const import (
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_FAN_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_PLATFORM,
    CONF_UNIT_OF_MEASUREMENT,
    ENTITY_MATCH_NONE,
    PRECISION_TENTHS,
    PRECISION_WHOLE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=15)

def setup_platform(hass, config, add_entities, discovery_info=None):
    
    registry = hass.data[DOMAIN]
    
    for i in range(len(registry.d)):
        if(registry.d[i].deviceType == 'Thermostat'):
            add_entities([HiloClimateEntity(registry, i)])

    # Return boolean to indicate that initialization was successfully.
    return True
    
class HiloClimateEntity(ClimateEntity):

    def __init__(self, h, index):
        """Init climate device."""
        #_LOGGER.warning( "%s", d.name)
        self.index = index
        #self.entity_id = ENTITY_ID_FORMAT.format(h.d[index].deviceId)
        self.operations = [HVAC_MODE_HEAT, HVAC_MODE_OFF]
        self._name = h.d[index].name
        self._has_operation = False
        if h.d[index].Heating == 0:
            self._def_hvac_mode = HVAC_MODE_OFF
        else:
            self._def_hvac_mode = HVAC_MODE_HEAT
#        self._min_temp = d.MinTempSetpoint
#        self._max_temp = d.MaxTempSetpoint
        self._temp_entity = None
        self._temp_entity_error = False
        self._should_poll = True
        
        self._h = h

    @property
    def name(self):
        """Return the precision of the system."""
        return self._h.d[self.index].name

    @property
    def should_poll(self) -> bool:        
        return True
        
    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_TENTHS

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature.""" 
        return self._h.d[self.index].CurrentTemperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._h.d[self.index].TargetTemperature
        
    def set_hvac_mode(self, hvac_mode):
        """Set operation mode."""
        return
        
    @property
    def hvac_mode(self):
        if self._h.d[self.index].Heating == 0:
            return HVAC_MODE_OFF
        else:
            return HVAC_MODE_HEAT

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return [HVAC_MODE_HEAT, HVAC_MODE_OFF]
    
    @property
    def supported_features(self):
        return SUPPORT_TARGET_TEMPERATURE

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            self._h.set_attribute('TargetTemperature', kwargs[ATTR_TEMPERATURE], self.index)
            self._h.d[self.index].TargetTemperature = kwargs[ATTR_TEMPERATURE]
            
    def update(self):
        return
        #self._h.update()
        
        #if self._h.d[self.index].Heating == 0:
        #    self._def_hvac_mode = HVAC_MODE_OFF
        #else:
        #    self._def_hvac_mode = HVAC_MODE_HEAT
        #if self._h.d[self.index].TargetTemperature is None:
        #    self._target_temperature = self._target_temperature
        #else:
        #    self._target_temperature = self._h.d[self.index].TargetTemperature

        #if self._h.d[self.index].CurrentTemperature is None:
        #    self._current_temperature = self._current_temperature   
        #else:
        #    self._current_temperature = self._h.d[self.index].CurrentTemperature    