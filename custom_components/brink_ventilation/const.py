"""Constant values for the Brink Home component."""
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import CONCENTRATION_PARTS_PER_MILLION, UnitOfTime

DOMAIN = "brink_ventilation"
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
}
