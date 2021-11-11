from datetime import timedelta, time
from homeassistant.components.utility_meter.const import (
    DAILY,
)

CONF_LIGHT_AS_SWITCH = "light_as_switch"
CONF_GENERATE_ENERGY_METERS = "generate_energy_meters"
CONF_HQ_PLAN_NAME = "hq_plan_name"
CONF_ENERGY_METER_PERIOD = "energy_meter_period"
CONF_TARIFF_PLAN = "tariff_plan"

DEFAULT_TARIFF_PLAN = "rate d"

TARIFF_LIST = ["high", "medium", "low"]
DEFAULT_GENERATE_ENERGY_METERS = False
DEFAULT_ENERGY_METER_PERIOD = DAILY
DEFAULT_HQ_PLAN_NAME = "hq_plan_name"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)
DEFAULT_LIGHT_AS_SWITCH = False
MIN_SCAN_INTERVAL = timedelta(seconds=15)
DOMAIN = "hilo"
# To prevent issues with automations for people that already deployed
# with the original code, the LightSwitch is dynamically added when
# light_as_switch boolean is enabled in configuration.
LIGHT_CLASSES = ["LightDimmer", "WhiteBulb", "ColorBulb", "LightSwitch"]
HILO_SENSOR_CLASSES = ["SmokeDetector", "Meter", "Gateway"]
CLIMATE_CLASSES = ["Thermostat"]
SWITCH_CLASSES = []

CONF_TARIFF = {
    "rate d": {
        "low_threshold": 40,
        "low": 0.06159,
        "medium": 0.09502,
        "high": 0,
        "access": 0.41168,
    },
    "flex d": {
        "low_threshold": 40,
        "low": 0.04336,
        "medium": 0.07456,
        "high": 50.65,
        "access": 0.41168,
    },
}

CONF_HIGH_PERIODS = {
    "am": {"from": time(6, 00, 00), "to": time(9, 0, 0)},
    "pm": {"from": time(16, 0, 0), "to": time(19, 0, 0)},
}
