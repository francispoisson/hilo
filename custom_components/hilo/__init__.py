"""Hilo HA integration"""
import asyncio
import logging

from .api import Hilo

# from .utility_meter import async_setup_platform, utility_setup
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    CONF_LIGHT_AS_SWITCH,
    CONF_GENERATE_ENERGY_METERS,
    CONF_ENERGY_METER_PERIOD,
    CONF_HQ_PLAN_NAME,
    CONF_TARIFF_PLAN,
    DEFAULT_TARIFF_PLAN,
    DEFAULT_LIGHT_AS_SWITCH,
    MIN_SCAN_INTERVAL,
    DEFAULT_GENERATE_ENERGY_METERS,
    DEFAULT_ENERGY_METER_PERIOD,
    DEFAULT_HQ_PLAN_NAME,
)
import voluptuous as vol


from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
    SERVICE_RELOAD,
)
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.reload import async_reload_integration_platforms
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.helpers.entity_component import (
    EntityComponent,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(
                    CONF_LIGHT_AS_SWITCH, default=DEFAULT_LIGHT_AS_SWITCH
                ): cv.boolean,
                vol.Optional(
                    CONF_GENERATE_ENERGY_METERS, default=DEFAULT_GENERATE_ENERGY_METERS
                ): cv.boolean,
                vol.Optional(
                    CONF_HQ_PLAN_NAME, default=DEFAULT_HQ_PLAN_NAME
                ): cv.string,
                vol.Optional(
                    CONF_ENERGY_METER_PERIOD, default=DEFAULT_ENERGY_METER_PERIOD
                ): cv.string,
                vol.Optional(CONF_TARIFF_PLAN, default=DEFAULT_TARIFF_PLAN): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): (
                    vol.All(cv.time_period, vol.Clamp(min=MIN_SCAN_INTERVAL))
                ),
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = ["sensor", "climate", "switch", "binary_sensor", "light"]
COORDINATOR_AWARE_PLATFORMS = [SENSOR_DOMAIN, BINARY_SENSOR_DOMAIN]


async def async_setup(hass, config):
    async def reload_service_handler(service):
        conf = await component.async_prepare_reload()
        if conf is None:
            return
        await async_reload_integration_platforms(hass, DOMAIN, PLATFORMS)
        await _async_process_config(hass, conf)

    component = EntityComponent(_LOGGER, DOMAIN, hass)
    component.scan_interval = get_scan_interval(config)
    hass.services.async_register(
        DOMAIN, SERVICE_RELOAD, reload_service_handler, schema=vol.Schema({})
    )
    return await _async_process_config(hass, config)


def get_scan_interval(conf):
    return conf.get(DOMAIN, {}).get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)


async def _async_process_config(hass, config) -> bool:
    if DOMAIN not in config:
        return False
    conf = config.get(DOMAIN)

    load_tasks = []
    username = conf.get(CONF_USERNAME, "no username")
    password = conf.get(CONF_PASSWORD, "no password")
    hilo = Hilo(
        username,
        password,
        hass,
        get_scan_interval(config),
        conf.get(CONF_LIGHT_AS_SWITCH, DEFAULT_LIGHT_AS_SWITCH),
        conf.get(CONF_GENERATE_ENERGY_METERS, DEFAULT_GENERATE_ENERGY_METERS),
        conf.get(CONF_ENERGY_METER_PERIOD, DEFAULT_ENERGY_METER_PERIOD),
        conf.get(CONF_HQ_PLAN_NAME, DEFAULT_HQ_PLAN_NAME),
        conf.get(CONF_TARIFF_PLAN, DEFAULT_TARIFF_PLAN),
    )
    await hilo.async_update_all_devices()
    coordinator = _hilo_coordinator(hass, hilo)
    hass.data[DOMAIN] = hilo
    await asyncio.gather(coordinator.async_refresh())
    if not coordinator.last_update_success:
        _LOGGER.error("Hilo coordinator failed: " + str(coordinator.last_exception))
        return False
    for platform in PLATFORMS:
        try:
            load_tasks.append(
                discovery.async_load_platform(hass, platform, DOMAIN, {}, config)
            )
        except Exception as e:
            _LOGGER.exception(e)

    try:
        await asyncio.gather(*load_tasks)
    except Exception as err:
        _LOGGER.exception(err)
    return True


def _hilo_coordinator(hass, hilo):
    update_method = hilo.async_update
    return DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="hilo update coordinator",
        update_method=update_method,
        update_interval=hilo.scan_interval,
    )
