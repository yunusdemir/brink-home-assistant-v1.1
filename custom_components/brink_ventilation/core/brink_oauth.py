"""OAuth2 authentication for Brink Home new API."""
import asyncio
import hashlib
import logging
import re
import secrets
from base64 import urlsafe_b64encode
from urllib.parse import parse_qs, urlencode, urlparse

import aiohttp

_LOGGER = logging.getLogger(__name__)

# OAuth endpoints
IDSRV_BASE = "https://www.brink-home.com/idsrv"
AUTH_ENDPOINT = f"{IDSRV_BASE}/connect/authorize"
TOKEN_ENDPOINT = f"{IDSRV_BASE}/connect/token"
REDIRECT_URI = "https://www.brink-home.com/app"
CLIENT_ID = "spa"
SCOPES = "openid api role locale"


class BrinkOAuthClient:
    """Handles OAuth2 authentication for Brink Home API."""

    def __init__(self, session: aiohttp.ClientSession, username: str, password: str):
        """Initialize OAuth client."""
        self._session = session
        self._username = username
        self._password = password
        self._access_token = None
        self._refresh_token = None
        self._token_expiry = None

    def _generate_pkce(self):
        """Generate PKCE code verifier and challenge."""
        code_verifier = urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        return code_verifier, code_challenge

    async def authenticate(self):
        """
        Perform automated OAuth authentication flow.

        Steps:
        1. Request authorization page
        2. Submit login credentials
        3. Follow redirects to capture authorization code
        4. Exchange code for tokens
        """
        try:
            # Generate PKCE parameters
            code_verifier, code_challenge = self._generate_pkce()
            state = secrets.token_urlsafe(32)
            nonce = secrets.token_urlsafe(32)

            # Step 1: Request authorization
            auth_params = {
                'client_id': CLIENT_ID,
                'redirect_uri': REDIRECT_URI,
                'response_type': 'code',
                'scope': SCOPES,
                'state': state,
                'nonce': nonce,
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256',
                'response_mode': 'query'
            }

            auth_url = f"{AUTH_ENDPOINT}?{urlencode(auth_params)}"

            _LOGGER.debug("Requesting authorization page...")
            _LOGGER.debug(f"Authorization URL: {auth_url}")
            async with self._session.get(auth_url, allow_redirects=False) as response:
                _LOGGER.debug(f"Authorization response status: {response.status}")
                if response.status == 400:
                    error_text = await response.text()
                    _LOGGER.error(f"Authorization request error (400): {error_text}")
                    return False

                if response.status == 302:
                    # Got redirect - either to login page or with code
                    location = response.headers.get('Location', '')
                    _LOGGER.debug(f"Got 302 redirect to: {location[:200]}")
                    code = self._extract_code(location)
                    if code:
                        _LOGGER.debug(f"Found code in redirect: {code[:20]}...")
                        return await self._exchange_code_for_token(code, code_verifier)
                    else:
                        _LOGGER.debug("No code in redirect, following to login page...")
                        # Follow redirect to login page
                        async with self._session.get(location, allow_redirects=False) as login_page_response:
                            if login_page_response.status != 200:
                                _LOGGER.error(f"Failed to get login page: {login_page_response.status}")
                                return False
                            html = await login_page_response.text()
                elif response.status == 200:
                    html = await response.text()
                else:
                    _LOGGER.error(f"Authorization request failed: {response.status}")
                    return False

            # Step 2: Extract login form details
            form_action = self._extract_form_action(html)
            if not form_action:
                _LOGGER.error("Could not find login form")
                return False

            _LOGGER.debug(f"Extracted form action: {form_action}")
            antiforgery_token = self._extract_antiforgery_token(html)

            # Try to extract return URL from hidden field first, then from form action
            return_url = self._extract_return_url(html)
            if not return_url and 'ReturnUrl=' in form_action:
                # Extract from form action query parameter
                parsed = urlparse(form_action)
                query_params = parse_qs(parsed.query)
                return_url = query_params.get('ReturnUrl', [''])[0]

            _LOGGER.debug(f"Extracted return URL: {return_url}")

            # Step 3: Submit login credentials
            # Form action is already a full path, just need the base domain
            login_url = f"https://www.brink-home.com{form_action}"
            _LOGGER.debug(f"Posting login to: {login_url}")
            login_data = {
                'Username': self._username,
                'Password': self._password,
                'ReturnUrl': return_url,
                '__RequestVerificationToken': antiforgery_token,
                'button': 'login',
                'RememberLogin': 'false'
            }

            _LOGGER.debug("Submitting login credentials...")
            async with self._session.post(
                login_url,
                data=login_data,
                allow_redirects=False
            ) as response:
                if response.status != 302:
                    _LOGGER.error(f"Login failed: {response.status}")
                    error_html = await response.text()
                    error_msg = self._extract_error_message(error_html)
                    if error_msg:
                        _LOGGER.error(f"Login error: {error_msg}")
                    return False

                # Step 4: Follow redirect chain to get authorization code
                location = response.headers.get('Location', '')
                code = await self._follow_redirects_for_code(location)

                if not code:
                    _LOGGER.error("Could not obtain authorization code")
                    return False

            # Step 5: Exchange code for tokens
            return await self._exchange_code_for_token(code, code_verifier)

        except Exception as e:
            _LOGGER.exception(f"OAuth authentication failed: {e}")
            return False

    async def _follow_redirects_for_code(self, initial_location):
        """Follow redirect chain until we get the authorization code."""
        location = initial_location
        max_redirects = 10
        redirect_count = 0

        while location and redirect_count < max_redirects:
            # Check if this redirect contains the code
            code = self._extract_code(location)
            if code:
                return code

            # Convert relative URLs to absolute
            if location.startswith('/'):
                location = f"https://www.brink-home.com{location}"

            # Follow the redirect
            redirect_count += 1
            _LOGGER.debug(f"Following redirect {redirect_count}: {location[:100]}")

            try:
                async with self._session.get(location, allow_redirects=False) as response:
                    _LOGGER.debug(f"Redirect {redirect_count} status: {response.status}")
                    if response.status == 302:
                        location = response.headers.get('Location', '')
                        _LOGGER.debug(f"Next location: {location[:200] if location else 'None'}")
                    elif response.status == 200:
                        _LOGGER.debug(f"Got 200 response, stopping redirect chain")
                        break
                    else:
                        _LOGGER.debug(f"Unexpected status {response.status}, stopping")
                        break
            except Exception as e:
                _LOGGER.error(f"Error following redirect: {e}")
                break

        return None

    def _extract_code(self, url):
        """Extract authorization code from URL."""
        if not url:
            return None

        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        return query_params.get('code', [None])[0]

    def _extract_form_action(self, html):
        """Extract login form action from HTML."""
        match = re.search(r'<form[^>]+action="([^"]+)"', html)
        return match.group(1) if match else None

    def _extract_antiforgery_token(self, html):
        """Extract anti-forgery token from HTML."""
        match = re.search(r'name="__RequestVerificationToken"[^>]+value="([^"]+)"', html)
        return match.group(1) if match else ''

    def _extract_return_url(self, html):
        """Extract return URL from HTML."""
        match = re.search(r'name="ReturnUrl"[^>]+value="([^"]+)"', html)
        return match.group(1) if match else ''

    def _extract_error_message(self, html):
        """Extract error message from login page."""
        match = re.search(r'<div[^>]+class="[^"]*alert[^"]*"[^>]*>([^<]+)', html)
        return match.group(1).strip() if match else None

    async def _exchange_code_for_token(self, code, code_verifier):
        """Exchange authorization code for access token."""
        _LOGGER.debug("Exchanging authorization code for tokens...")

        token_data = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'code': code,
            'code_verifier': code_verifier,
            'redirect_uri': REDIRECT_URI
        }

        try:
            async with self._session.post(TOKEN_ENDPOINT, data=token_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    _LOGGER.error(f"Token exchange failed: {response.status} - {error_text}")
                    return False

                tokens = await response.json()
                self._access_token = tokens.get('access_token')
                self._refresh_token = tokens.get('refresh_token')
                expires_in = tokens.get('expires_in', 3600)

                _LOGGER.info("✅ OAuth authentication successful")
                _LOGGER.debug(f"Token expires in {expires_in} seconds")
                _LOGGER.debug(f"Has refresh token: {self._refresh_token is not None}")

                return True

        except Exception as e:
            _LOGGER.exception(f"Token exchange error: {e}")
            return False

    async def refresh_access_token(self):
        """Refresh the access token using refresh token."""
        if not self._refresh_token:
            _LOGGER.warning("No refresh token available, re-authenticating...")
            return await self.authenticate()

        _LOGGER.debug("Refreshing access token...")

        token_data = {
            'grant_type': 'refresh_token',
            'client_id': CLIENT_ID,
            'refresh_token': self._refresh_token
        }

        try:
            async with self._session.post(TOKEN_ENDPOINT, data=token_data) as response:
                if response.status != 200:
                    _LOGGER.error(f"Token refresh failed: {response.status}")
                    # Fall back to full re-authentication
                    return await self.authenticate()

                tokens = await response.json()
                self._access_token = tokens.get('access_token')
                # Refresh token may be rotated
                if 'refresh_token' in tokens:
                    self._refresh_token = tokens['refresh_token']

                _LOGGER.info("✅ Access token refreshed")
                return True

        except Exception as e:
            _LOGGER.exception(f"Token refresh error: {e}")
            return await self.authenticate()

    def get_auth_headers(self):
        """Get authorization headers for API requests."""
        if not self._access_token:
            return {}

        return {
            'Authorization': f'Bearer {self._access_token}'
        }

    @property
    def is_authenticated(self):
        """Check if we have a valid access token."""
        return self._access_token is not None
