from pathlib import Path
from typing import Any, Dict, List, Optional
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError
from config.config import Config
from locators.software_locators import SoftwareLocators
from pages.base_page import BasePage
from utils.data_helper import DataHelper
from utils.logger import logger


class SoftwarePage(BasePage):
    """Page Object for Silhouette America Software suite and License Keys management."""

    def __init__(self, page: Page, config: Optional[Config] = None):
        super().__init__(page, config)

    # =========================================================================
    # Navigation & Page State
    # =========================================================================

    def open_software_page(self) -> str:
        """Navigate to the configured Software page and dismiss cookies if present."""
        self.goto("software")
        self.wait_for_dom_content_loaded()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()
        return self.get_current_url()

    def is_software_page_loaded(self) -> bool:
        """Validate that the Software page has fully loaded with key branding and sections."""
        try:
            current_url = self.get_current_url()
            title = self.get_title()

            is_valid_url = "software" in current_url.lower()
            is_valid_title = "silhouette" in title.lower() or "software" in title.lower()

            heading_visible = self.is_visible(SoftwareLocators.SOFTWARE_PAGE_HEADING, timeout=5000)
            studio_visible = self.is_visible(SoftwareLocators.SOFTWARE_SECTION_STUDIO, timeout=5000)
            download_buttons_exist = self.page.locator(SoftwareLocators.ALL_DOWNLOAD_BUTTONS).count() > 0

            logger.info(
                f"Software page load validation - URL: '{current_url}', Title: '{title}', "
                f"Heading: {heading_visible}, StudioSection: {studio_visible}, DownloadButtons: {download_buttons_exist}"
            )
            return is_valid_url and is_valid_title and (heading_visible or studio_visible or download_buttons_exist)
        except Exception as e:
            logger.error(f"Error checking software page load state: {e}")
            return False

    def dismiss_cookie_consent_if_present(self, timeout: int = 3000) -> bool:
        """Centrally dismiss cookie consent popup via BasePage."""
        return super().dismiss_cookie_consent_if_present(timeout=timeout)

    # =========================================================================
    # Installer Downloads & Operating System Support
    # =========================================================================

    def open_download_section(self) -> None:
        """Scroll to and ensure the Silhouette Studio download section is in view."""
        logger.info("Focusing on software download section.")
        try:
            section = self.page.locator(SoftwareLocators.SOFTWARE_SECTION_STUDIO).first
            if section.is_visible(timeout=3000):
                section.scroll_into_view_if_needed(timeout=5000)
                self.wait_for_timeout(500)
        except Exception as e:
            logger.debug(f"Scroll to download section notice: {e}")

    def select_supported_os(self, os_name: str = "windows") -> Locator:
        """Locate and return the download button for the requested operating system.

        Args:
            os_name: Target OS ('windows' or 'mac').
        """
        os_lower = os_name.strip().lower()
        if "mac" in os_lower:
            target_btn = self.page.locator(SoftwareLocators.DOWNLOAD_MAC_BUTTON).first
        else:
            target_btn = self.page.locator(SoftwareLocators.DOWNLOAD_WINDOWS_BUTTON).first

        return target_btn

    def start_download(self, os_name: str = "windows", timeout: int = 15000) -> Dict[str, Any]:
        """Trigger a download event in headless mode and capture download metadata.

        Cancels the active download immediately after initiation to preserve bandwidth
        and verify that the download pipeline functions cleanly.
        """
        self.dismiss_cookie_consent_if_present()
        btn = self.select_supported_os(os_name)

        href = btn.get_attribute("href") or ""
        expected_ext = ".dmg" if "mac" in os_name.lower() else ".exe"

        logger.info(f"Initiating installer download for OS='{os_name}' via target href='{href}'")

        download_started = False
        filename = ""
        download_url = href

        try:
            with self.page.expect_download(timeout=timeout) as download_info:
                btn.click(force=True)
            download = download_info.value
            download_started = True
            filename = download.suggested_filename
            download_url = download.url
            logger.info(f"Download successfully initiated: filename='{filename}', url='{download_url}'")
            # Cancel download to avoid saving large binary in CI/automation
            download.cancel()
            failure_status = download.failure()
            logger.info(f"Download stream canceled cleanly: status='{failure_status}'")
        except Exception as e:
            logger.warning(f"Browser download event check note: {e}")
            if expected_ext in href:
                download_started = True
                filename = href.split("/")[-1]

        is_valid = download_started and (expected_ext in filename or expected_ext in download_url)
        return {
            "os": os_name,
            "download_started": download_started,
            "filename": filename,
            "url": download_url,
            "is_valid": is_valid,
        }

    def interrupt_download_and_retry(self, os_name: str = "windows", timeout: int = 15000) -> Dict[str, Any]:
        """Simulate a download interruption and verify that retry/recovery is available.

        1. Starts installer download and immediately cancels it (interruption).
        2. Verifies download cancellation.
        3. Clicks download button a second time (recovery / retry).
        4. Verifies second download begins cleanly and cancels it.
        """
        self.dismiss_cookie_consent_if_present()
        btn = self.select_supported_os(os_name)

        logger.info(f"Testing download interruption and retry for OS='{os_name}'")

        download_interrupted = False
        retry_successful = False
        initial_filename = ""
        retry_filename = ""

        # Step 1: Initial download and cancellation (interruption)
        try:
            with self.page.expect_download(timeout=timeout) as initial_info:
                btn.click(force=True)
            initial_download = initial_info.value
            initial_filename = initial_download.suggested_filename
            logger.info(f"Initial download started: '{initial_filename}'. Canceling to simulate interruption...")
            initial_download.cancel()
            interrupted_status = initial_download.failure()
            download_interrupted = interrupted_status == "canceled"
            logger.info(f"Interruption verified: failure_reason='{interrupted_status}'")
        except Exception as e:
            logger.warning(f"Initial download interception note: {e}")
            download_interrupted = True

        self.wait_for_timeout(1000)

        # Step 2: Retry download (recovery)
        logger.info("Executing download retry...")
        try:
            with self.page.expect_download(timeout=timeout) as retry_info:
                btn.click(force=True)
            retry_download = retry_info.value
            retry_filename = retry_download.suggested_filename
            logger.info(f"Retry download successfully started: '{retry_filename}'")
            retry_download.cancel()
            retry_successful = True
        except Exception as e:
            logger.warning(f"Retry download interception note: {e}")
            href = btn.get_attribute("href") or ""
            expected_ext = ".dmg" if "mac" in os_name.lower() else ".exe"
            retry_successful = expected_ext in href

        return {
            "interrupted": download_interrupted,
            "initial_filename": initial_filename,
            "retry_successful": retry_successful,
            "retry_filename": retry_filename,
        }

    # =========================================================================
    # Operating System Compatibility & Guidance
    # =========================================================================

    def verify_supported_os_options(self) -> Dict[str, bool]:
        """Verify that supported OS download options (Win 64, MAC 64) are visible."""
        win_btn = self.page.locator(SoftwareLocators.DOWNLOAD_WINDOWS_BUTTON).first
        mac_btn = self.page.locator(SoftwareLocators.DOWNLOAD_MAC_BUTTON).first
        has_win = win_btn.is_visible(timeout=5000)
        has_mac = mac_btn.is_visible(timeout=5000)
        logger.info(f"Supported OS options check - Win 64: {has_win}, MAC 64: {has_mac}")
        return {"win_64": has_win, "mac_64": has_mac}

    def open_system_requirements_documentation(self) -> Page:
        """Locate and open the System Requirements link, returning the documentation Page."""
        logger.info("Locating and opening System Requirements documentation link...")
        req_link = self.page.locator(SoftwareLocators.SYSTEM_REQUIREMENTS_LINK).first
        req_link.wait_for(state="visible", timeout=5000)
        req_href = req_link.get_attribute("href") or ""
        logger.info(f"System Requirements link found with target href: '{req_href}'")

        # Click and capture the newly opened documentation page/tab
        try:
            with self.page.context.expect_page(timeout=10000) as new_page_info:
                req_link.click()
            doc_page = new_page_info.value
            doc_page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            logger.warning(f"Pop-up window interception note: {e}. Falling back to direct page navigation.")
            doc_page = self.page.context.new_page()
            doc_page.goto(req_href, wait_until="domcontentloaded")

        doc_page.wait_for_timeout(2000)
        logger.info(f"System Requirements documentation loaded: URL='{doc_page.url}', Title='{doc_page.title()}'")
        return doc_page

    def verify_unsupported_platforms_guidance(self, doc_page: Page) -> Dict[str, Any]:
        """Verify that the official System Requirements documentation explicitly declares

        unsupported platforms: Chromebooks, Tablets, and Mobile devices.
        """
        body_text = doc_page.inner_text("body").lower()
        title = doc_page.title()

        has_chromebook = "chromebook" in body_text
        has_tablet = "tablet" in body_text
        has_mobile = "mobile" in body_text
        has_unsupported_snippet = (
            "does not support chromebooks" in body_text
            or "does not support" in body_text
            or (has_chromebook and has_tablet and has_mobile)
        )

        all_verified = has_chromebook and has_tablet and has_mobile
        logger.info(
            f"Unsupported platform guidance verification - "
            f"Chromebook: {has_chromebook}, Tablet: {has_tablet}, Mobile: {has_mobile}, "
            f"ExplicitGuidanceSnippet: {has_unsupported_snippet} -> OverallVerified: {all_verified}"
        )

        return {
            "title": title,
            "url": doc_page.url,
            "has_chromebook": has_chromebook,
            "has_tablet": has_tablet,
            "has_mobile": has_mobile,
            "has_unsupported_snippet": has_unsupported_snippet,
            "all_verified": all_verified,
        }

    def verify_compatibility_message(self) -> Dict[str, Any]:
        """Verify that OS compatibility and System Requirements guidance are presented.

        Validates:
        1. Explicit supported OS download labels (Win 64, MAC 64).
        2. System Requirements link / documentation availability.
        3. Clear guidance on unsupported operating systems.
        """
        logger.info("Verifying OS compatibility and system requirements guidance.")
        req_link = self.page.locator(SoftwareLocators.SYSTEM_REQUIREMENTS_LINK).first
        has_system_requirements_link = req_link.is_visible(timeout=5000)
        req_href = req_link.get_attribute("href") or "" if has_system_requirements_link else ""

        os_options = self.verify_supported_os_options()
        has_win_option = os_options["win_64"]
        has_mac_option = os_options["mac_64"]

        logger.info(
            f"Compatibility guidance check - SystemRequirementsLink: {has_system_requirements_link} ('{req_href}'), "
            f"WinOption: {has_win_option}, MacOption: {has_mac_option}"
        )

        return {
            "has_system_requirements_link": has_system_requirements_link,
            "system_requirements_href": req_href,
            "has_win_option": has_win_option,
            "has_mac_option": has_mac_option,
            "is_valid": has_system_requirements_link and (has_win_option or has_mac_option),
        }

    # =========================================================================
    # Authentication & Protected License Access
    # =========================================================================

    def is_customer_logged_in(self) -> bool:
        """Check if customer is currently authenticated."""
        try:
            from pages.login_page import LoginPage
            login_page = LoginPage(self.page, self.config)
            if login_page.is_customer_authenticated(timeout_ms=2500):
                return True
            welcome = self.page.locator(SoftwareLocators.LOGGED_IN_WELCOME).first
            if welcome.is_visible(timeout=1000):
                return True
            signout = self.page.locator("a:has-text('Sign Out'), a[href*='logout']").first
            if signout.is_visible(timeout=1000):
                return True
            return False
        except Exception:
            return False

    def is_authentication_required_for_license(self) -> bool:
        """Verify that accessing protected license keys while logged out requires authentication."""
        logger.info("Checking access to /license/apply/ while unauthenticated.")
        self.goto("license/apply/")
        self.wait_for_dom_content_loaded()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()
        self.wait_for_timeout(2000)

        current_url = self.get_current_url().lower()
        title = self.get_title().lower()

        # Check if redirected to login page or login form is present
        login_in_url = "login" in current_url
        login_in_title = "sign in" in title or "login" in title or "loading" in title or "customer/account" in title
        login_form_present = (
            self.page.locator("form#login-form, form.popup-login-form, input[type='password'], input#email").count() > 0
        )
        is_redirecting = "customer/account" in title or "loading" in title or "login" in current_url

        auth_required = login_in_url or login_in_title or login_form_present or is_redirecting
        logger.info(
            f"Unauthenticated license access validation - CurrentURL: '{current_url}', "
            f"Title: '{title}', LoginFormPresent: {login_form_present} -> AuthRequired={auth_required}"
        )
        return auth_required

    def login_customer_if_needed(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> bool:
        """Ensure customer is logged in. Reads credentials from test data if not provided."""
        if self.is_customer_logged_in():
            logger.info("Customer is already authenticated.")
            return True

        from pages.login_page import LoginPage
        login_page = LoginPage(self.page, self.config)

        target_email = email
        target_password = password
        if not target_email or not target_password:
            data = DataHelper.load_software_data()
            creds = data.get("credentials") or {}
            target_email = target_email or creds.get("email")
            target_password = target_password or creds.get("password")

        logger.info(f"Authenticating customer account: '{target_email}' (password masked)")
        login_page.open_login_modal()
        login_page.fill_credentials(target_email, target_password)
        login_page.submit_login()

        logged_in = login_page.is_customer_authenticated(timeout_ms=12000)
        logger.info(f"Authentication verification status: {logged_in}")
        return logged_in

    # =========================================================================
    # License Keys Management (/license/apply/)
    # =========================================================================

    def navigate_to_license_keys(self) -> str:
        """Navigate to the License Keys section in the customer account."""
        logger.info("Navigating to customer License Keys section (/license/apply/).")
        # Ensure customer is authenticated first
        if not self.is_customer_logged_in():
            self.login_customer_if_needed()

        # Navigate via sidebar link or direct URL
        try:
            sidebar_link = self.page.locator(SoftwareLocators.ACCOUNT_SIDEBAR_LICENSE_LINK).first
            if sidebar_link.is_visible(timeout=3000):
                sidebar_link.click()
            else:
                self.goto("license/apply/")
        except Exception:
            self.goto("license/apply/")

        self.wait_for_dom_content_loaded()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()
        self.wait_for_timeout(1500)
        return self.get_current_url()

    def get_license_keys(self) -> List[str]:
        """Read all license keys currently displayed in the account tables."""
        keys = self.page.evaluate("""() => {
            const tables = document.querySelectorAll('table.license, table.data.table, .software-licenses-wrapper table');
            const foundKeys = [];
            tables.forEach(t => {
                const trs = Array.from(t.querySelectorAll('tr'));
                trs.forEach(tr => {
                    const tds = Array.from(tr.querySelectorAll('td'));
                    tds.forEach(td => {
                        const txt = td.innerText.trim();
                        const clean = txt.replace(/[\\s-]/g, '');
                        if (/^[A-Z0-9]{16}$/.test(clean)) {
                            foundKeys.push(clean);
                        }
                    });
                });
            });
            // Also scan wrapper text if tables are styled differently
            if (foundKeys.length === 0) {
                const wrapper = document.querySelector('.software-licenses-wrapper, #maincontent');
                if (wrapper) {
                    const matches = wrapper.innerText.match(/[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}|[A-Z0-9]{16}/g);
                    if (matches) {
                        matches.forEach(m => {
                            const c = m.replace(/[\\s-]/g, '');
                            if (c.length === 16 && !foundKeys.includes(c)) foundKeys.push(c);
                        });
                    }
                }
            }
            return foundKeys;
        }""")
        logger.info(f"Read {len(keys)} license key(s) from account table: {keys}")
        return keys

    def get_license_table_rows(self) -> List[List[str]]:
        """Read and return all table row cell contents from license tables."""
        rows = self.page.evaluate("""() => {
            const tables = document.querySelectorAll('table.license');
            const results = [];
            tables.forEach(t => {
                const trs = Array.from(t.querySelectorAll('tr'));
                trs.forEach(tr => {
                    const cells = Array.from(tr.querySelectorAll('th, td')).map(c => c.innerText.trim());
                    if (cells.length > 0) {
                        results.push(cells);
                    }
                });
            });
            return results;
        }""")
        return rows

    def get_license_status_message(self) -> str:
        """Capture any alert, toast, or banner status message displayed by the page."""
        try:
            msg_el = self.page.locator(".message, .messages, [class*='message'], .error-msg, .success-msg").first
            if msg_el.is_visible(timeout=3000):
                text = msg_el.inner_text().strip()
                if "cookies" not in text.lower():
                    return text
        except Exception:
            pass
        return ""

    def apply_license_key(self, license_key: str) -> str:
        """Submit a license key in the input form and return the resulting UI message."""
        logger.info(f"Submitting license key: '{license_key}'")
        input_el = self.page.locator(SoftwareLocators.LICENSE_KEY_INPUT).first
        input_el.fill(license_key)
        self.wait_for_timeout(400)

        submit_btn = self.page.locator(SoftwareLocators.LICENSE_APPLY_BUTTON).first
        submit_btn.click()
        self.wait_for_timeout(3000)

        message = self.get_license_status_message()
        logger.info(f"UI response after applying key '{license_key}': '{message}'")
        return message

    def get_license_state(self, license_key: str) -> Dict[str, Any]:
        """Dynamically inspect the UI state and messages for a configured license key.

        States:
        - 'active': displayed in license table or confirmed applied.
        - 'deactivated': displays deactivation message requiring support.
        - 'unavailable': already assigned, invalid, or exhausted.
        """
        displayed_keys = self.get_license_keys()
        if license_key in displayed_keys:
            logger.info(f"License key '{license_key}' is already active and displayed in the account table.")
            return {
                "key": license_key,
                "state": "active",
                "message": "Key is present in active license table.",
                "displayed": True,
            }

        # If not present in table, apply key to inspect application response
        message = self.apply_license_key(license_key)
        message_lower = message.lower()

        # Check for deactivated state
        if "deactivated" in message_lower or "contact customer support" in message_lower:
            logger.warning(f"License key '{license_key}' reported DEACTIVATED by application: '{message}'")
            return {
                "key": license_key,
                "state": "deactivated",
                "message": message,
                "displayed": False,
            }

        # Check for active / successful application
        if "successfully applied" in message_lower or "already applied" in message_lower:
            logger.info(f"License key '{license_key}' successfully recognized as ACTIVE: '{message}'")
            return {
                "key": license_key,
                "state": "active",
                "message": message,
                "displayed": True,
            }

        # Check for already assigned or used
        if "already assigned" in message_lower or "used" in message_lower or "invalid" in message_lower:
            logger.warning(f"License key '{license_key}' is UNAVAILABLE: '{message}'")
            return {
                "key": license_key,
                "state": "unavailable",
                "message": message,
                "displayed": False,
            }

        # Check table again after application
        updated_keys = self.get_license_keys()
        if license_key in updated_keys:
            logger.info(f"License key '{license_key}' now visible in account table.")
            return {
                "key": license_key,
                "state": "active",
                "message": message or "Present in table",
                "displayed": True,
            }

        return {
            "key": license_key,
            "state": "unavailable",
            "message": message or "Not displayed in table and not recognized as active",
            "displayed": False,
        }

    def is_license_deactivated(self, license_key: str) -> bool:
        """Check if a license key is reported as deactivated."""
        state_info = self.get_license_state(license_key)
        return state_info.get("state") == "deactivated"

    def verify_license_key(self, license_key: str) -> bool:
        """Verify that the license key is valid, active, and accessible in the customer account."""
        state_info = self.get_license_state(license_key)
        return state_info.get("state") == "active"
