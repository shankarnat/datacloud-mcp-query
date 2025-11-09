from __future__ import annotations

from datetime import datetime, timedelta
import logging
import os
import sys
import base64
import hashlib
import secrets
import time
from threading import Thread
import http.server
import webbrowser
from urllib.parse import parse_qs, urlparse
from typing import Tuple

import requests
from rfc3986 import builder as uri_builder

# Get logger for this module
logger = logging.getLogger(__name__)


class OAuthConfig:
    def __init__(self, client_id: str, client_secret: str, login_root: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.login_root = login_root
        self.redirect_uri = redirect_uri

    @classmethod
    def from_env(cls) -> "OAuthConfig":
        client_id = os.getenv("SF_CLIENT_ID")
        client_secret = os.getenv("SF_CLIENT_SECRET")
        login_root = os.getenv("SF_LOGIN_URL", "login.salesforce.com")
        redirect_uri = os.getenv(
            "SF_CALLBACK_URL", "http://localhost:55556/Callback")

        # Check for different auth methods
        username = os.getenv("SF_USERNAME")
        password = os.getenv("SF_PASSWORD")
        refresh_token = os.getenv("SF_REFRESH_TOKEN")
        jwt_private_key = os.getenv("SF_JWT_PRIVATE_KEY")

        # Check if any valid auth method is configured
        has_username_password = username and password and client_id and client_secret
        has_jwt = jwt_private_key and client_id
        has_refresh_token = refresh_token and client_id and client_secret
        has_browser_oauth = client_id and client_secret

        if not (has_username_password or has_jwt or has_refresh_token or has_browser_oauth):
            print("Error: No valid authentication method configured")
            print("Provide one of the following authentication methods:")
            print("1. SF_CLIENT_ID + SF_CLIENT_SECRET + SF_USERNAME + SF_PASSWORD (username-password flow)")
            print("2. SF_CLIENT_ID + SF_JWT_PRIVATE_KEY + SF_USERNAME (JWT bearer token flow)")
            print("3. SF_CLIENT_ID + SF_CLIENT_SECRET + SF_REFRESH_TOKEN (refresh token flow)")
            print("4. SF_CLIENT_ID + SF_CLIENT_SECRET (browser-based OAuth - local only)")
            sys.exit(1)

        return cls(client_id=client_id, client_secret=client_secret, login_root=login_root, redirect_uri=redirect_uri)


class _RequestHandler(http.server.BaseHTTPRequestHandler):  # pragma: no cover
    def do_GET(self):  # noqa: N802
        parts = urlparse(self.path)
        if parts.path.lower() != "/callback":
            self.send_error(404, "Not Found", "Not Found")
            return

        args = parse_qs(parts.query)
        self.server.oauth_result = args

        has_code = "code" in args
        response_content = f"Final Status: {has_code=}".encode("utf-8")
        response_content += b"\nYou can close this window now"
        self.send_response(200, "OK")
        self.send_header("Content-Type", "text")
        self.send_header("Content-Length", str(len(response_content)))
        self.end_headers()
        self.wfile.write(response_content)


def _generate_pkce_pair() -> Tuple[str, str]:
    """Generate PKCE code verifier and challenge for OAuth flow"""
    code_verifier = (
        base64.urlsafe_b64encode(secrets.token_bytes(
            32)).decode("utf-8").rstrip("=")
    )

    challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = (
        base64.urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")
    )

    return code_verifier, code_challenge


class OAuthSession:
    def __init__(self, config: OAuthConfig):
        self.config = config
        self.token: str | None = None
        self.exp: datetime | None = None
        self.instance_url: str | None = None
        self.refresh_token: str | None = os.getenv("SF_REFRESH_TOKEN")

    def _refresh_access_token(self) -> dict:
        """Use refresh token to get a new access token"""
        logger.info("Refreshing access token using refresh token")
        token_url = f"https://{self.config.login_root}/services/oauth2/token"

        response = requests.post(
            token_url,
            {
                "grant_type": "refresh_token",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "refresh_token": self.refresh_token,
            },
            headers={"Accept": "application/json"},
        )

        logger.info(f"Token refresh response: status={response.status_code}")

        if response.status_code >= 400:
            logger.error(f"Token refresh failed: {response.text}")

        response.raise_for_status()

        logger.info("Successfully refreshed access token")
        return response.json()

    def _username_password_flow(self) -> dict:
        """Use username-password flow for authentication"""
        logger.info("Using username-password flow for authentication")

        # Get environment variables
        username = os.getenv("SF_USERNAME")
        password = os.getenv("SF_PASSWORD")
        security_token = os.getenv("SF_SECURITY_TOKEN", "")

        if not username or not password:
            raise ValueError("SF_USERNAME and SF_PASSWORD are required for username-password authentication")

        # Salesforce requires password + security token concatenated
        password_with_token = password + security_token

        token_url = f"https://{self.config.login_root}/services/oauth2/token"

        response = requests.post(
            token_url,
            {
                "grant_type": "password",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "username": username,
                "password": password_with_token,
            },
            headers={"Accept": "application/json"},
        )

        logger.info(f"Username-password auth response: status={response.status_code}")

        if response.status_code >= 400:
            logger.error(f"Username-password auth failed: {response.text}")

        response.raise_for_status()

        logger.info("Successfully obtained access token via username-password")
        return response.json()

    def _jwt_bearer_token_flow(self) -> dict:
        """Use JWT bearer token flow for server-to-server authentication"""
        import jwt

        logger.info("Using JWT bearer token flow for authentication")

        # Get environment variables
        username = os.getenv("SF_USERNAME")
        private_key = os.getenv("SF_JWT_PRIVATE_KEY")

        if not username or not private_key:
            raise ValueError("SF_USERNAME and SF_JWT_PRIVATE_KEY are required for JWT authentication")

        # Decode private key if it's base64 encoded
        try:
            # Try to decode from base64 (for Heroku config vars)
            private_key_decoded = base64.b64decode(private_key).decode('utf-8')
        except Exception:
            # If it fails, assume it's already plain text
            private_key_decoded = private_key

        # Create JWT payload
        claim = {
            "iss": self.config.client_id,
            "sub": username,
            "aud": f"https://{self.config.login_root}",
            "exp": int(time.time()) + 300  # 5 minutes expiration
        }

        # Sign the JWT
        assertion = jwt.encode(claim, private_key_decoded, algorithm="RS256")

        # Exchange JWT for access token
        token_url = f"https://{self.config.login_root}/services/oauth2/token"

        response = requests.post(
            token_url,
            {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": assertion,
            },
            headers={"Accept": "application/json"},
        )

        logger.info(f"JWT token exchange response: status={response.status_code}")

        if response.status_code >= 400:
            logger.error(f"JWT token exchange failed: {response.text}")

        response.raise_for_status()

        logger.info("Successfully obtained access token via JWT")
        return response.json()

    def _run_oauth_flow(self, scopes: list[str]):
        logger.info(f"Starting OAuth flow with scopes: {scopes}")
        login_url = f"https://{self.config.login_root}/services/oauth2/authorize"
        token_exchange_url = f"https://{self.config.login_root}/services/oauth2/token"
        redirect_uri = self.config.redirect_uri

        code_verifier, code_challenge = _generate_pkce_pair()

        browser_uri: str = (
            uri_builder.URIBuilder(path=login_url)
            .add_query_from(
                {
                    "client_id": self.config.client_id,
                    "redirect_uri": redirect_uri,
                    "response_type": "code",
                    "scope": " ".join(scopes),
                    "prompt": "login",
                    "code_challenge": code_challenge,
                    "code_challenge_method": "S256",
                }
            )
            .finalize()
            .unsplit()
        )

        parsed_redirect = urlparse(redirect_uri)
        port = parsed_redirect.port

        logger.debug(f"Starting OAuth callback server on localhost:{port}")
        server = http.server.HTTPServer(("localhost", port), _RequestHandler)
        server.allow_reuse_address = True
        t = Thread(target=server.handle_request, daemon=True)
        t.start()

        logger.info(f"Opening browser for OAuth authorization")
        logger.debug(f"Browser URI: {browser_uri}")
        webbrowser.open_new_tab(browser_uri)
        while t.is_alive():
            t.join(10)

        oauth_result_args = server.oauth_result

        if "code" not in oauth_result_args:
            error_msg = "OAuth authentication failed - no authorization code received"
            if "error" in oauth_result_args:
                error_msg += f". Error: {oauth_result_args['error'][0]}"
                if "error_description" in oauth_result_args:
                    error_msg += f" - {oauth_result_args['error_description'][0]}"
            raise Exception(error_msg)

        code = oauth_result_args["code"][0]
        logger.info(f"Authorization code received, exchanging for access token")

        response = requests.post(
            token_exchange_url,
            {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
            },
            headers={"Accept": "application/json"},
        )

        logger.info(f"Token exchange response: status={response.status_code}, elapsed={response.elapsed.total_seconds():.2f}s")

        if response.status_code >= 400:
            logger.error(f"Token exchange failed: {response.text}")

        response.raise_for_status()

        logger.info("Successfully obtained access token")
        return response.json()

    def ensure_access(self) -> str:
        if self.exp is not None and datetime.now() > self.exp:
            self.exp = None
            self.token = None

        if self.token is None:
            # Priority 1: Username-Password flow (simplest for Heroku)
            username = os.getenv("SF_USERNAME")
            password = os.getenv("SF_PASSWORD")
            if username and password:
                logger.info("Using username-password for authentication")
                auth_info = self._username_password_flow()
            # Priority 2: JWT bearer token flow
            elif os.getenv("SF_JWT_PRIVATE_KEY"):
                logger.info("Using JWT bearer token for authentication")
                auth_info = self._jwt_bearer_token_flow()
            # Priority 3: Refresh token flow
            elif self.refresh_token:
                logger.info("Using refresh token for authentication")
                auth_info = self._refresh_access_token()
            # Priority 4: Browser-based OAuth flow (for local development)
            else:
                logger.info("Using browser-based OAuth flow")
                auth_info = self._run_oauth_flow(
                    ["api", "cdp_query_api", "cdp_profile_api"])
                # Store the refresh token for future use
                if "refresh_token" in auth_info:
                    self.refresh_token = auth_info["refresh_token"]
                    logger.info("Received refresh token - store this in SF_REFRESH_TOKEN env var for production use")

            self.token = auth_info["access_token"]
            self.exp = datetime.now() + timedelta(minutes=110)
            self.instance_url = auth_info["instance_url"]

        return self.token

    def get_token(self) -> str:
        return self.ensure_access()

    def get_instance_url(self) -> str:
        self.ensure_access()
        return self.instance_url
