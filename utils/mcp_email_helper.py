"""Gmail / Email MCP Integration Helper.

Integrates with the environment's configured Model Context Protocol (MCP) server
and OAuth credentials defined in ~/.gemini/config/mcp_config.json and
~/.gemini/antigravity-ide/mcp_oauth_tokens.json to query threads and retrieve
verification OTP codes dynamically for any generated test email address.
"""

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import requests
from utils.logger import logger


class McpEmailHelper:
    """Helper client to interact with the configured Gmail MCP / Gmail API service."""

    DEFAULT_MCP_CONFIG_PATH = Path(
        os.path.expanduser("~/.gemini/config/mcp_config.json")
    )
    DEFAULT_TOKENS_PATH = Path(
        os.path.expanduser("~/.gemini/antigravity-ide/mcp_oauth_tokens.json")
    )

    def __init__(
        self,
        config_path: Optional[Path] = None,
        tokens_path: Optional[Path] = None,
    ):
        self.config_path = config_path or self.DEFAULT_MCP_CONFIG_PATH
        self.tokens_path = tokens_path or self.DEFAULT_TOKENS_PATH
        self.server_url: Optional[str] = None
        self.oauth_client_id: Optional[str] = None
        self.oauth_client_secret: Optional[str] = None
        self.auth_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self._load_config()
        self._load_tokens()

    def _load_config(self) -> None:
        """Load Gmail MCP configuration from mcp_config.json."""
        if not self.config_path.exists():
            logger.warning(f"MCP configuration file not found at: {self.config_path}")
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            servers = config.get("mcpServers", {})
            gmail_cfg = servers.get("gmail", {})
            self.server_url = gmail_cfg.get("serverUrl")
            oauth = gmail_cfg.get("oauth", {})
            self.oauth_client_id = oauth.get("clientId")
            self.oauth_client_secret = oauth.get("clientSecret")

            # Check if an auth token is provided via environment or headers
            self.auth_token = os.getenv("GMAIL_MCP_AUTH_TOKEN") or os.getenv("GOOGLE_OAUTH_ACCESS_TOKEN")
            self.refresh_token = os.getenv("GMAIL_REFRESH_TOKEN")
            headers = gmail_cfg.get("headers", {})
            if "Authorization" in headers:
                self.auth_token = headers["Authorization"].replace("Bearer ", "").strip()

            # Check for local project .env or config/gmail_token.json
            project_root = Path(__file__).resolve().parent.parent
            env_file = project_root / ".env"
            if env_file.exists() and not self.auth_token:
                try:
                    with open(env_file, "r", encoding="utf-8") as ef:
                        for line in ef:
                            line = line.strip()
                            if line.startswith("GMAIL_MCP_AUTH_TOKEN="):
                                self.auth_token = line.split("=", 1)[1].strip().strip('"').strip("'")
                            elif line.startswith("GOOGLE_OAUTH_ACCESS_TOKEN="):
                                self.auth_token = line.split("=", 1)[1].strip().strip('"').strip("'")
                            elif line.startswith("GMAIL_REFRESH_TOKEN="):
                                self.refresh_token = line.split("=", 1)[1].strip().strip('"').strip("'")
                except Exception as e:
                    logger.debug(f"Could not read local .env file: {e}")

            token_json_file = project_root / "config" / "gmail_token.json"
            if token_json_file.exists() and not self.auth_token:
                try:
                    with open(token_json_file, "r", encoding="utf-8") as tj:
                        tdata = json.load(tj)
                        self.auth_token = tdata.get("access_token") or tdata.get("token")
                        if not self.refresh_token:
                            self.refresh_token = tdata.get("refresh_token")
                except Exception as e:
                    logger.debug(f"Could not read config/gmail_token.json: {e}")

            logger.info(
                f"Loaded MCP Gmail configuration: serverUrl='{self.server_url}', "
                f"clientId='{self.oauth_client_id[:12] if self.oauth_client_id else 'None'}...'"
            )
        except Exception as e:
            logger.error(f"Error loading MCP configuration from {self.config_path}: {e}")

    def _load_tokens(self) -> None:
        """Load active OAuth tokens from the IDE OAuth session cache if available."""
        if not self.tokens_path.exists():
            return

        try:
            with open(self.tokens_path, "r", encoding="utf-8") as f:
                tokens_data = json.load(f)

            # Match by serverUrl or first entry
            entry = None
            if self.server_url and self.server_url in tokens_data:
                entry = tokens_data[self.server_url]
            elif tokens_data:
                entry = next(iter(tokens_data.values()))

            if entry and isinstance(entry, dict):
                token_info = entry.get("token", {})
                if not self.auth_token:
                    self.auth_token = token_info.get("access_token")
                self.refresh_token = token_info.get("refresh_token")
                if not self.oauth_client_id:
                    self.oauth_client_id = entry.get("client_id")
                if not self.oauth_client_secret:
                    self.oauth_client_secret = entry.get("client_secret")

                logger.info("Successfully loaded active OAuth token from MCP token cache.")
        except Exception as e:
            logger.warning(f"Could not read tokens from {self.tokens_path}: {e}")

    def refresh_access_token_if_needed(self) -> bool:
        """Refresh the Google OAuth access token using refresh_token if expired."""
        if not (self.refresh_token and self.oauth_client_id and self.oauth_client_secret):
            return False

        try:
            token_url = "https://oauth2.googleapis.com/token"
            payload = {
                "client_id": self.oauth_client_id,
                "client_secret": self.oauth_client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
            }
            resp = requests.post(token_url, data=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                new_token = data.get("access_token")
                if new_token:
                    self.auth_token = new_token
                    logger.info("Successfully refreshed Google OAuth access token.")
                    return True
        except Exception as e:
            logger.warning(f"Failed to refresh OAuth access token: {e}")
        return False

    def retrieve_registration_otp(
        self,
        recipient_email: str,
        timeout_seconds: int = 60,
        poll_interval: int = 4,
    ) -> Tuple[bool, Optional[str], str]:
        """Search mailbox dynamically for registration OTP sent to recipient_email.

        Args:
            recipient_email: The exact generated email address (e.g. anand.mopidi+QA...@...).
            timeout_seconds: Maximum time to poll for the verification email.
            poll_interval: Interval between polling attempts in seconds.

        Returns:
            (success, otp_code, status_detail)
        """
        logger.info(
            f"Searching dynamically for registration OTP for '{recipient_email}' "
            f"via configured Gmail MCP (timeout={timeout_seconds}s)..."
        )

        clean_recipient = recipient_email.strip().lower()
        start_time = time.time()
        last_error = ""

        # 1. Check for manual / pre-configured OTP in environment
        static_otp = os.getenv("REGISTRATION_OTP")
        if static_otp and len(static_otp.strip()) == 6 and static_otp.strip().isdigit():
            logger.info(f"Using pre-configured REGISTRATION_OTP from environment: '{static_otp.strip()}'")
            return True, static_otp.strip(), f"OTP {static_otp.strip()} retrieved from REGISTRATION_OTP environment variable."

        # Normalize headers
        if not self.auth_token:
            self._load_tokens()

        if not self.auth_token and not self.refresh_token:
            msg = (
                "Gmail MCP authentication required: No valid OAuth access token or refresh token found. "
                "Your organization (magnetoitsolutions.com) policy has blocked automated Google OAuth access."
            )
            # Interactive terminal prompt fallback
            is_interactive = False
            try:
                is_interactive = sys.stdin.isatty() or (sys.stdin.readable() and not sys.stdin.closed)
            except Exception:
                pass

            if is_interactive:
                print("\n" + "=" * 80)
                print("[ACTION REQUIRED] Corporate Google Workspace policy blocked automated Gmail MCP.")
                print(f"Silhouette America sent a 6-digit OTP code to: {recipient_email}")
                print("Please check your email inbox and enter the 6-digit OTP code below:")
                print("=" * 80)
                try:
                    for _ in range(3):
                        user_otp = input("Enter 6-digit OTP Code: ").strip()
                        if user_otp and len(user_otp) == 6 and user_otp.isdigit():
                            logger.info(f"Using OTP code entered interactively: '{user_otp}'")
                            return True, user_otp, f"OTP {user_otp} provided interactively via terminal."
                        elif not user_otp:
                            break
                        print("Invalid OTP format. Must be exactly 6 digits (e.g. 123456). Please try again:")
                except Exception as ex:
                    logger.warning(f"Interactive input failed: {ex}")

            logger.error(msg)
            return False, None, msg

        while time.time() - start_time < timeout_seconds:
            headers = {"Authorization": f"Bearer {self.auth_token}"}

            try:
                # Query recent Silhouette Customer Verification messages
                query = 'Silhouette "Customer Verification"'
                url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={query}&maxResults=10"
                resp = requests.get(url, headers=headers, timeout=15)

                if resp.status_code == 401:
                    logger.warning("OAuth access token expired. Attempting token refresh...")
                    if self.refresh_access_token_if_needed():
                        continue
                    is_interactive = False
                    try:
                        is_interactive = sys.stdin.isatty() or (sys.stdin.readable() and not sys.stdin.closed)
                    except Exception:
                        pass
                    if is_interactive:
                        print("\n" + "=" * 80)
                        print("[ACTION REQUIRED] OAuth token expired or blocked by organization policy.")
                        print(f"Silhouette America sent a 6-digit OTP code to: {recipient_email}")
                        print("Please check your email inbox and enter the 6-digit OTP code below:")
                        print("=" * 80)
                        try:
                            for _ in range(3):
                                user_otp = input("Enter 6-digit OTP Code: ").strip()
                                if user_otp and len(user_otp) == 6 and user_otp.isdigit():
                                    logger.info(f"Using OTP code entered interactively: '{user_otp}'")
                                    return True, user_otp, f"OTP {user_otp} provided interactively via terminal."
                                elif not user_otp:
                                    break
                                print("Invalid OTP format. Must be exactly 6 digits (e.g. 123456). Please try again:")
                        except Exception as ex:
                            logger.warning(f"Interactive input failed: {ex}")
                    return False, None, "OAuth access token expired and could not be refreshed."
                elif resp.status_code != 200:
                    last_error = f"HTTP {resp.status_code}: {resp.text}"
                    time.sleep(poll_interval)
                    continue

                msg_list = resp.json().get("messages", [])
                logger.info(f"Found {len(msg_list)} Silhouette verification message(s). Inspecting recipients...")

                for m in msg_list:
                    msg_id = m.get("id")
                    if not msg_id:
                        continue

                    msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}"
                    m_resp = requests.get(msg_url, headers=headers, timeout=10)
                    if m_resp.status_code != 200:
                        continue

                    m_data = m_resp.json()
                    payload = m_data.get("payload", {})
                    headers_list = payload.get("headers", [])
                    to_header = next((h["value"] for h in headers_list if h.get("name", "").lower() == "to"), "")

                    # Verify recipient matches our exact generated unique email
                    if clean_recipient in to_header.lower():
                        snippet = m_data.get("snippet", "")
                        match = re.search(r"\b(\d{6})\b", snippet)
                        if match:
                            otp_code = match.group(1)
                            logger.info(
                                f"Successfully retrieved OTP: '{otp_code}' for '{recipient_email}' "
                                f"from message id '{msg_id}'."
                            )
                            return True, otp_code, f"OTP {otp_code} retrieved successfully for {recipient_email}."

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Error querying Gmail during OTP poll: {e}")

            time.sleep(poll_interval)

        return (
            False,
            None,
            f"Timed out after {timeout_seconds}s waiting for OTP email sent to '{recipient_email}'. "
            f"Last error: {last_error}",
        )
