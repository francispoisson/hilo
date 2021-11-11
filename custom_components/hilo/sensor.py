from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    ENERGY_WATT_HOUR,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
    POWER_WATT,
)
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
)
from homeassistant.components.integration.sensor import (
    TRAPEZOIDAL_METHOD,
    IntegrationSensor,
)
from homeassistant.helpers.restore_state import RestoreEntity

from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify
import homeassistant.util.dt as dt_util
import logging

_LOGGER = logging.getLogger(__name__)
from .const import DOMAIN, CONF_TARIFF
from .managers import UtilityManager, EnergyManager
from .hilo_device import HiloBaseEntity
SENSOR_ATTRIBUTES = ["Power", "CurrentTemperature"]
async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    domain_config = hass.data[DOMAIN]
    power_entities = []
    temperature_entities = []
    energy_entities = []
    cost_entities = []
    if domain_config.generate_energy_meters:
        energy_manager = await EnergyManager().init(hass, domain_config.energy_meter_period)
        utility_manager = UtilityManager(domain_config.energy_meter_period)
    for d in domain_config.devices:
        # We really only care about devices with a power meter or temperature
        if "Power" in d.supported_attributes:
            d._power_entity = PowerSensor(d, domain_config.scan_interval)
            power_entities.append(d._power_entity)
            # If we opt out the geneneration of meters we just create the power sensors
            if not domain_config.generate_energy_meters:
                continue
            # This creates the sensor using the "integration" platform
            d._energy_entity = EnergySensor(d)
            energy_entities.append(d._energy_entity)
            energy_entity = f"hilo_energy_{slugify(d.name)}"
            if energy_entity == "hilo_energy_total":
                _LOGGER.error(
                    "An hilo entity can't be named 'total' because it conflicts with the generate name for the smart energy meter"
                )
                continue
            if d.name == "SmartEnergyMeter":
                energy_entity = "hilo_energy_total"
            utility_manager.add_meter(energy_entity)
            energy_manager.add_to_dashboard(energy_entity)
        if "CurrentTemperature" in d.supported_attributes:
            d._temperature_entity = TemperatureSensor(d, domain_config.scan_interval)
            temperature_entities.append(d._temperature_entity)

    async_add_entities(power_entities + energy_entities + temperature_entities)
    if not domain_config.generate_energy_meters:
        return
    # Creating cost sensors based on plan
    # This will generate hilo_cost_(low|medium|high) sensors which can be
    # refered later in the energy dashboard based on the tarif selected
    for tarif, amount in CONF_TARIFF.get(domain_config.hq_plan_name).items():
        sensor_name = f"hilo_rate_{tarif}"
        cost_entities.append(
            HiloCostSensor(sensor_name, domain_config.hq_plan_name, amount)
        )
    cost_entities.append(
        HiloCostSensor("hilo_rate_current", domain_config.hq_plan_name)
    )
    async_add_entities(cost_entities)
    # This setups the utility_meter platform
    await utility_manager.update(hass, config, async_add_entities)
    # This sends the entities to the energy dashboard
    await energy_manager.update()

class TemperatureSensor(HiloBaseEntity, Entity):
    def __init__(self, d, scan_interval):
        super().__init__(d, scan_interval)
        self._name = f"{self._name}_temperature"
        _LOGGER.debug(f"Setting up TemperatureSensor entity: {self._name}")

    @property
    def state(self):
        return str(int(self._get("CurrentTemperature", 0)))

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

    async def _async_update(self):
        return

class PowerSensor(HiloBaseEntity, Entity):
    def __init__(self, d, scan_interval):
        super().__init__(d, scan_interval)
        self._name = f"{self._name}_power"
        _LOGGER.debug(f"Setting up PowerSensor entity: {self._name}")

    @property
    def state(self):
        return str(int(self._get("Power", 0)))

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def device_class(self):
        return DEVICE_CLASS_POWER

    @property
    def unit_of_measurement(self):
        return POWER_WATT

    async def _async_update(self):
        # Other devices are updated within their own
        # classes. If we don't escape them, they will
        # be double-polled
        if self.d.device_type != "Meter":
            return
        _LOGGER.debug(f"{self.d._tag} Updating")
        await self.d.async_update_device()

class HiloCostSensor(RestoreEntity):
    def __init__(self, name, plan_name, amount=0):
        self.data = None
        self._name = name
        self.plan_name = plan_name
        self._amount = amount
        self._last_update = dt_util.utcnow()
        _LOGGER.info(f"Initializing energy cost sensor {name} {plan_name} ")

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return "mdi:cash"

    @property
    def state(self):
        return self._amount

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def device_class(self):
        return "monetary"

    @property
    def unit_of_measurement(self):
        return "$/kWh"

    @property
    def device_state_attributes(self):
        return {"last_update": self._last_update, "Cost": self.state}

    async def async_added_to_hass(self):
        """Handle entity about to be added to hass event."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._last_update = dt_util.utcnow()
            self._amount = last_state.state

    async def async_update(self):
        return

class EnergySensor(IntegrationSensor):
    def __init__(self, d):
        self.d = d
        self._name = f"hilo_energy_{slugify(self.d.name)}"
        self._unit_of_measurement = ENERGY_WATT_HOUR
        self._unit_prefix = None
        self._last_update = None
        if self.d.name == "SmartEnergyMeter":
            self._name = "hilo_energy_total"
            self._unit_of_measurement = ENERGY_KILO_WATT_HOUR
            self._unit_prefix = "k"
        if d.device_type == "Thermostat":
            self._unit_of_measurement = ENERGY_KILO_WATT_HOUR
            self._unit_prefix = "k"
        self._source = f"sensor.{slugify(self.d.name)}_power"
        super().__init__(
            self._source,
            self._name,
            2,
            self._unit_prefix,
            "h",
            self._unit_of_measurement,
            TRAPEZOIDAL_METHOD,
        )
        self._state = 0
        self._last_period = 0
        _LOGGER.debug(f"Setting up EnergySensor entity: {self._name}")

    @property
    def icon(self):
        return "mdi:lightning-bolt"

    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT

    @property
    def device_class(self):
        return DEVICE_CLASS_ENERGY

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        _LOGGER.debug(f"Added to hass: {self._name}")
        await super().async_added_to_hass()
        if state := await self.async_get_last_state():
            self._state = state.state
