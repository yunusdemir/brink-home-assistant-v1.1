"""Brink Home API v1.1 client with OAuth2 authentication."""
import logging
from typing import Any, Dict, List, Optional

import aiohttp

from .brink_oauth import BrinkOAuthClient

_LOGGER = logging.getLogger(__name__)

API_URL = "https://www.brink-home.com/portal/api/v1.1/"


class BrinkAPIv1_1:
    """Client for Brink Home API v1.1 with OAuth2."""

    def __init__(self, session: aiohttp.ClientSession, username: str, password: str):
        """Initialize the API client."""
        self._session = session
        self._oauth = BrinkOAuthClient(session, username, password)
        self._systems_cache = None

    async def login(self):
        """Authenticate using OAuth2."""
        return await self._oauth.authenticate()

    async def refresh_token(self):
        """Refresh the OAuth access token."""
        return await self._oauth.refresh_access_token()

    def _get_headers(self):
        """Get headers for API requests including OAuth token."""
        return {
            **self._oauth.get_auth_headers(),
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'HomeAssistant-BrinkVentilation/2.0',
        }

    async def get_systems(self) -> List[Dict[str, Any]]:
        """Get list of systems."""
        try:
            async with self._session.get(
                f"{API_URL}systems",
                params={'pageSize': 10},
                headers=self._get_headers()
            ) as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to get systems: {response.status}")
                    return []

                data = await response.json()
                items = data.get('items', [])

                # Map to consistent format
                systems = []
                for item in items:
                    systems.append({
                        'system_id': item.get('systemShareId'),
                        'gateway_id': item.get('systemShareId'),  # v1.1 uses systemShareId for both
                        'name': item.get('systemName', ''),
                        'serial_number': item.get('serialNumber', ''),
                        'is_owner': item.get('isSystemOwner', False),
                        'access_level': item.get('accessLevel', 0),
                    })

                self._systems_cache = systems
                _LOGGER.debug(f"Found {len(systems)} system(s)")
                return systems

        except Exception as e:
            _LOGGER.exception(f"Error getting systems: {e}")
            return []

    async def get_description_values(self, system_id: int, gateway_id: int) -> Dict[str, Any]:
        """Get all parameter values for a system.

        Args:
            system_id: System share ID (same as gateway_id in v1.1)
            gateway_id: Not used in v1.1, kept for compatibility

        Returns:
            Dictionary of parameter values organized by name
        """
        try:
            async with self._session.get(
                f"{API_URL}systems/{system_id}/uidescription",
                headers=self._get_headers()
            ) as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to get UI description: {response.status}")
                    return {}

                data = await response.json()
                root = data.get('root', {})
                nav_items = root.get('navigationItems', [])

                # Parse parameters into flat dictionary
                result = {}

                for component_nav in nav_items:
                    component_name = component_nav.get('name')
                    component_id = component_nav.get('componentId')

                    _LOGGER.debug(f"Processing component: {component_name} (ID: {component_id})")

                    # Get all parameter groups
                    for param_nav in component_nav.get('navigationItems', []):
                        param_groups = param_nav.get('parameterGroups', [])

                        for group in param_groups:
                            parameters = group.get('parameters', [])

                            for param in parameters:
                                param_name = param.get('name')
                                param_id = param.get('id')

                                # Build parameter data structure compatible with old API
                                param_data = {
                                    'id': param_id,
                                    'component_id': component_id,
                                    'value': param.get('value'),
                                    'type': param.get('controlType'),
                                    'read_write': param.get('readWrite'),
                                    'unit': param.get('unit', ''),
                                    'value_state': param.get('valueState'),
                                    'has_statistics': param.get('hasStatistics', False),
                                }

                                # Add list items if available (for select controls)
                                if 'listItems' in param:
                                    param_data['values'] = param['listItems']

                                result[param_name] = param_data

                                _LOGGER.debug(f"  Added parameter: {param_name} = {param_data['value']}")

                _LOGGER.debug(f"Extracted {len(result)} parameters")
                return result

        except Exception as e:
            _LOGGER.exception(f"Error getting description values: {e}")
            return {}

    async def set_ventilation_value(
        self, system_id: int, gateway_id: int, parameter_id: int, value: int
    ):
        """Set ventilation level.

        Args:
            system_id: System share ID
            gateway_id: Not used in v1.1
            parameter_id: Parameter ID to set
            value: New value
        """
        try:
            request_data = {
                'value': str(value)
            }

            async with self._session.put(
                f"{API_URL}parameters/{parameter_id}",
                json=request_data,
                headers=self._get_headers()
            ) as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to set ventilation value: {response.status}")
                    text = await response.text()
                    _LOGGER.error(f"Response: {text}")
                    return False

                _LOGGER.info(f"Successfully set parameter {parameter_id} to {value}")
                return True

        except Exception as e:
            _LOGGER.exception(f"Error setting ventilation value: {e}")
            return False

    async def set_mode_value(
        self, system_id: int, gateway_id: int, parameter_id: int, value: int
    ):
        """Set operating mode.

        Args:
            system_id: System share ID
            gateway_id: Not used in v1.1
            parameter_id: Parameter ID to set
            value: New value
        """
        return await self.set_ventilation_value(system_id, gateway_id, parameter_id, value)

    @property
    def is_authenticated(self):
        """Check if authenticated."""
        return self._oauth.is_authenticated
