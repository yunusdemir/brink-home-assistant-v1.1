"""Constant values for the Brink Home component."""
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
)

DOMAIN = "brink_ventilation_1-1"
DEFAULT_NAME = "Brink"
DEFAULT_MODEL = "Zone"

DATA_CLIENT = "brink_client"
DATA_COORDINATOR = "coordinator"
DATA_DEVICES = "systems"

DEFAULT_SCAN_INTERVAL = 30

API_URL = "https://www.brink-home.com/portal/api/portal/"

# Define sensor types with their properties
SENSOR_TYPES = {
    "co2": {
        "device_class": SensorDeviceClass.CO2,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": CONCENTRATION_PARTS_PER_MILLION,
        "icon": "mdi:molecule-co2",
        "pattern": r"(?=.*\bPPM\b)(?=.*\bCO2\b)",
    },
    "bypass": {
        "device_class": None,
        "state_class": None,
        "unit": None,
        "icon": "mdi:valve",
        "pattern": r"Status Bypassklappe",
    },
    "mode_timer": {
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
        "unit": UnitOfTime.MINUTES,
        "icon": "mdi:timer-outline",
        "pattern": r"Restlaufzeit Betriebsartfunktion",
    },
    "fresh_air_temp": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "pattern": r"Frischlufttemperatur",
    },
    "supply_air_temp": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer-lines",
        "pattern": r"Zulufttemperatur",
    },
    "supply_air_flow": {
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": "m³/h",
        "icon": "mdi:air-filter",
        "pattern": r"Ist-Wert Luftdurchsatz Zuluft",
    },
    "exhaust_air_flow": {
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": "m³/h",
        "icon": "mdi:air-filter",
        "pattern": r"Ist-Wert Luftdurchsatz Abluft",
    },
    "humidity": {
        "device_class": SensorDeviceClass.HUMIDITY,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": PERCENTAGE,
        "icon": "mdi:water-percent",
        "pattern": r"Relative Feuchte",
    },
}
