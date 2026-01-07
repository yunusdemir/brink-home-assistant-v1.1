"""Constant values for the Brink Home component."""
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import CONCENTRATION_PARTS_PER_MILLION

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
}
