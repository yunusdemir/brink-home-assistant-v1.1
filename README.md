[![GitHub Release](https://img.shields.io/github/release/yunusdemir/brink-home-assistant-v1.1.svg?style=for-the-badge&color=blue)](https://github.com/yunusdemir/brink-home-assistant-v1.1/releases)

![Project Maintenance](https://img.shields.io/badge/maintainer-Yunus%20Demir-blue.svg?style=for-the-badge)

# Brink-Home Ventilation (API v1.1 with OAuth2)

Custom component for Home Assistant. This component is designed to integrate the [Brink-Home](https://www.brink-home.com/) systems with [ebus Brink Emodule](https://www.brinkclimatesystems.nl/documenten/brink-home-emodule-imodule-614491.pdf).

**This version uses Brink API v1.1 with OAuth2 authentication** and includes additional sensors for temperature, airflow, and humidity monitoring.

<img width="503" alt="Screenshot 2023-05-08 at 21 14 39" src="https://user-images.githubusercontent.com/28056781/236899814-e903fbb0-e007-4938-aa2c-0e04e91fbb36.png">

## Installation

### HACS (Custom Repository)

- Go to the [HACS](https://hacs.xyz) panel
- Click the 3 dots in the top right corner
- Select "Custom repositories"
- Add this repository URL: `https://github.com/yunusdemir/brink-home-assistant-v1.1`
- Category: Integration
- Click "Add"
- Search for 'Brink-Home Ventilation'
- Click 'Download'

### Manually

- Download or clone this repository
- Copy the `custom_components/brink_ventilation_1-1` folder to your Home Assistant `config/custom_components/` directory
- Restart Home Assistant
- Go to Configuration > Integrations
- Click "+ Add Integration"
- Search for "Brink-home Ventilation" and follow the setup

### WORKING ON:
- Brink Flair 200
- Brink Renovent 180
- Brink Renovent 300
- Brink Renovent 400 Plus
- Brink Flair 325
- Please tell me, it should work with all Brink ventilation systems
