import json
from typing import Any, Dict, List, Optional
from playwright.sync_api import Page
from config.config import Config
from locators.login_locators import LoginLocators
from pages.base_page import BasePage
from utils.logger import logger


class LoginPage(BasePage):
    """Page Object Model representing Silhouette America Customer Login flow,

    supporting both the header popup login modal and the standalone login page.
    """

    def __init__(self, page: Page, config: Optional[Config] = None) -> None:
        super().__init__(page, config)

    # =========================================================================
    # Navigation & Modal Access
    # =========================================================================

    def open_login_modal(self) -> None:
        """Open the customer login modal via the header account menu trigger."""
        if self.is_customer_authenticated(timeout_ms=1000):
            logger.info("Customer is already authenticated. Skipping login modal opening.")
            return

        if self.is_login_modal_open():
            logger.info("Login modal is already open.")
            return

        current_url = self.get_current_url()
        if not current_url or current_url == "about:blank":
            logger.info(f"Navigating to base site: {self.config.base_url}")
            self.goto("", wait_until="domcontentloaded")

        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()

        logger.info("Opening Login modal via header account menu...")
        for attempt in range(3):
            self.ensure_minicart_closed()
            self.dismiss_cookie_consent_if_present()
            try:
                account_trigger = self.page.locator(LoginLocators.ACCOUNT_MENU_TRIGGER).first
                if account_trigger.is_visible(timeout=3000):
                    account_trigger.click(timeout=3000)
                    self.wait_for_timeout(600)
            except Exception as e:
                logger.debug(f"Account menu trigger click notice: {e}")

            try:
                signin_link = self.page.locator(LoginLocators.SIGN_IN_DROPDOWN_LINK).first
                if signin_link.is_visible(timeout=3000):
                    signin_link.click(timeout=3000)
                    self.wait_for_timeout(1000)
            except Exception as e:
                logger.debug(f"Sign in link click notice: {e}")

            popup_form = self.page.locator(LoginLocators.POPUP_LOGIN_FORM).first
            if popup_form.is_visible(timeout=2000):
                logger.info("Login popup form successfully opened and visible.")
                return

        # Fallback to standalone login page if popup modal could not be triggered
        if not self.is_login_modal_open():
            logger.info("Login modal not opened via header dropdown; navigating to standalone login page...")
            self.open_standalone_login_page()
            try:
                self.page.wait_for_selector(
                    f"{LoginLocators.POPUP_LOGIN_FORM}, {LoginLocators.STANDALONE_LOGIN_FORM}",
                    state="visible",
                    timeout=10000,
                )
            except Exception as e:
                logger.warning(f"Wait for login form notice: {e}")

    def open_standalone_login_page(self) -> None:
        """Navigate directly to the standalone login page (/customer/account/login)."""
        logger.info(f"Navigating to standalone login page: {LoginLocators.ACCOUNT_LOGIN_PATH}")
        self.goto(LoginLocators.ACCOUNT_LOGIN_PATH, wait_until="domcontentloaded")
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()

    def is_login_modal_open(self) -> bool:
        """Check whether the popup login form is currently visible."""
        try:
            return self.page.locator(LoginLocators.POPUP_LOGIN_FORM).first.is_visible(timeout=2000)
        except Exception:
            return False

    def close_login_modal(self) -> None:
        """Close the popup login modal using the cancel/close button."""
        try:
            close_btn = self.page.locator(LoginLocators.POPUP_CLOSE_BUTTON).first
            if close_btn.is_visible(timeout=1000):
                close_btn.click(timeout=1000)
                self.wait_for_timeout(500)
        except Exception as e:
            logger.debug(f"Notice closing login modal: {e}")

    # =========================================================================
    # Form Filling & Submission
    # =========================================================================

    def fill_credentials(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Fill username and password fields into the active login form."""
        masked_pwd = "****" if password else "<empty>"
        logger.info(f"Entering login credentials: email='{email}', password='{masked_pwd}'")

        if self.is_login_modal_open():
            popup_form = self.page.locator(LoginLocators.POPUP_LOGIN_FORM).first
            u_input = popup_form.locator("input[name='username'], #username").first
            p_input = popup_form.locator("input[name='popup-password'], #popup-password").first

            u_input.clear()
            if email is not None and email != "":
                u_input.fill(email)

            p_input.clear()
            if password is not None and password != "":
                p_input.fill(password)
        else:
            # Standalone form
            u_input = self.page.locator(LoginLocators.STANDALONE_USERNAME_INPUT).first
            p_input = self.page.locator(LoginLocators.STANDALONE_PASSWORD_INPUT).first

            u_input.clear()
            if email is not None and email != "":
                u_input.fill(email)

            p_input.clear()
            if password is not None and password != "":
                p_input.fill(password)

    def toggle_remember_me(self, check: bool = True) -> bool:
        """Toggle the Remember Me checkbox on the active login form."""
        logger.info(f"Setting 'Remember Me' checkbox to: {check}")
        cb = self.page.locator(
            f"{LoginLocators.POPUP_REMEMBER_ME_CHECKBOX}, {LoginLocators.STANDALONE_REMEMBER_ME}"
        ).first
        if not cb.is_visible(timeout=2000):
            logger.warning("Remember Me checkbox is not visible on the active login form.")
            return False

        current_state = cb.is_checked()
        if current_state != check:
            if check:
                cb.check()
            else:
                cb.uncheck()
            self.wait_for_timeout(300)

        actual_state = cb.is_checked()
        logger.info(f"Remember Me checkbox state is now: {actual_state}")
        return actual_state

    def is_remember_me_checked(self) -> bool:
        """Return the current checked state of the Remember Me checkbox."""
        cb = self.page.locator(
            f"{LoginLocators.POPUP_REMEMBER_ME_CHECKBOX}, {LoginLocators.STANDALONE_REMEMBER_ME}"
        ).first
        try:
            return cb.is_checked(timeout=2000)
        except Exception:
            return False

    def is_remember_me_available(self) -> bool:
        """Check if Remember Me option exists and is visible on the login form."""
        cb = self.page.locator(
            f"{LoginLocators.POPUP_REMEMBER_ME_CHECKBOX}, {LoginLocators.STANDALONE_REMEMBER_ME}"
        ).first
        try:
            return cb.is_visible(timeout=2000)
        except Exception:
            return False

    def submit_login(self) -> None:
        """Click the Submit / Sign In button on the active login form."""
        logger.info("Submitting login credentials...")
        if self.is_login_modal_open():
            submit_btn = self.page.locator(LoginLocators.POPUP_SUBMIT_BUTTON).first
            try:
                # Capture AJAX login response if triggered via popup modal
                with self.page.expect_response(
                    lambda resp: "customerlogin/ajax/login" in resp.url.lower(),
                    timeout=15000,
                ) as response_info:
                    submit_btn.click()
                resp = response_info.value
                logger.info(f"Login AJAX response received with HTTP status: {resp.status}")
                try:
                    data = resp.json()
                    if data.get("errors"):
                        err_msg = data.get("message", "Unknown authentication error")
                        logger.warning(f"Login failed on server: '{err_msg}'")
                    else:
                        logger.info("Login server response indicates success. Waiting for page reload/state change...")
                except Exception:
                    # In case of immediate page reload where response body stream is detached
                    pass
            except Exception as e:
                logger.debug(f"expect_response notice on popup login submit: {e}")
                if submit_btn.is_visible(timeout=1000):
                    submit_btn.click()

            # Wait for reload or DOM transition and handle Cloudflare if present
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass
            self.handle_cloudflare_if_present()
        else:
            submit_btn = self.page.locator(LoginLocators.STANDALONE_SUBMIT_BUTTON).first
            submit_btn.click()
            self.wait_for_dom_content_loaded()
            self.handle_cloudflare_if_present()
            self.wait_for_timeout(1500)

    # =========================================================================
    # Error & Validation Inspections
    # =========================================================================

    def get_response_error_message(self, timeout_ms: int = 6000) -> str:
        """Retrieve the visible server response error message (AJAX banner or page error)."""
        logger.info("Waiting for server response error message...")
        error_locator = self.page.locator(
            f"{LoginLocators.RESPONSE_ERROR_MSG}, .login-overlay .response-msg, .message-error"
        ).first

        try:
            error_locator.wait_for(state="visible", timeout=timeout_ms)
            msg = error_locator.inner_text().strip()
            logger.info(f"Captured response error message: '{msg}'")
            return msg
        except Exception as e:
            logger.debug(f"No response error message displayed within timeout: {e}")
            return ""

    def get_username_validation_error(self) -> str:
        """Retrieve field-level validation error message for the email / username input."""
        err = self.page.locator(
            f"{LoginLocators.POPUP_USERNAME_ERROR}, {LoginLocators.STANDALONE_EMAIL_ERROR}"
        ).first
        try:
            if err.is_visible(timeout=2000):
                return err.inner_text().strip()
        except Exception:
            pass
        return ""

    def get_password_validation_error(self) -> str:
        """Retrieve field-level validation error message for the password input."""
        err = self.page.locator(
            f"{LoginLocators.POPUP_PASSWORD_ERROR}, {LoginLocators.STANDALONE_PASSWORD_ERROR}"
        ).first
        try:
            if err.is_visible(timeout=2000):
                return err.inner_text().strip()
        except Exception:
            pass
        return ""

    def get_all_field_validation_errors(self) -> List[str]:
        """Return a list of all visible client-side validation error messages."""
        errors: List[str] = []
        loc = self.page.locator(
            f"{LoginLocators.ALL_FIELD_ERRORS}, form#login-form .mage-error:visible"
        )
        try:
            count = loc.count()
            for i in range(count):
                el = loc.nth(i)
                txt = el.inner_text().strip()
                if txt and txt not in errors:
                    errors.append(txt)
        except Exception:
            pass
        logger.info(f"Discovered field validation errors: {errors}")
        return errors

    # =========================================================================
    # Authentication & Session Verification
    # =========================================================================

    def is_customer_authenticated(self, timeout_ms: int = 15000) -> bool:
        """Dynamically verify if a customer is currently authenticated."""
        import time

        end_time = time.time() + (timeout_ms / 1000.0)
        while time.time() < end_time:
            # Handle any Cloudflare challenges if reloaded
            self.handle_cloudflare_if_present()

            # 1. Check local storage mage-cache-storage for customer session
            try:
                res = self.page.evaluate("""() => {
                    try {
                        const storage = window.localStorage.getItem('mage-cache-storage');
                        if (storage) {
                            const parsed = JSON.parse(storage);
                            if (parsed.customer && (parsed.customer.fullname || parsed.customer.firstname || parsed.customer.email)) {
                                return parsed.customer.fullname || parsed.customer.firstname || true;
                            }
                        }
                    } catch(e) {}
                    return false;
                }""")
                if bool(res):
                    logger.info(f"Customer verified authenticated via localStorage 'mage-cache-storage' ({res}).")
                    return True
            except Exception:
                # Execution context may be destroyed during post-login page reload/navigation
                pass

            # 2. Check DOM logged-in welcome message and user name element
            try:
                user_names = self.page.locator(
                    getattr(LoginLocators, "LOGGED_IN_USER_NAME", "span.user-name, .user-name.bs, span.user-link-dropdown:not(:has-text('Account'))")
                )
                for i in range(user_names.count()):
                    un = user_names.nth(i)
                    txt = un.inner_text().strip()
                    if un.is_visible() and txt and txt.lower() != "account":
                        logger.info(f"Customer verified authenticated via visible user name element: '{txt}'.")
                        return True
            except Exception:
                pass

            # 3. Check customer section API if localStorage not yet hydrated
            try:
                section_data = self.page.evaluate("""async () => {
                    try {
                        const resp = await fetch('/customer/section/load/?sections=customer');
                        if (resp.ok) {
                            const data = await resp.json();
                            if (data.customer && (data.customer.fullname || data.customer.firstname || data.customer.email)) {
                                return data.customer.fullname || data.customer.firstname || true;
                            }
                        }
                    } catch(e) {}
                    return false;
                }""")
                if bool(section_data):
                    logger.info(f"Customer verified authenticated via customer section API ({section_data}).")
                    return True
            except Exception:
                pass

            # 4. Check for Sign Out / Logout link in DOM
            try:
                signout = self.page.locator(
                    f"{LoginLocators.SIGN_OUT_LINK}, a:has-text('Logout'), a:has-text('Sign Out')"
                ).first
                if signout.is_visible(timeout=200):
                    logger.info("Customer verified authenticated via visible Sign Out link.")
                    return True
            except Exception:
                pass

            # 5. Check if current URL is inside customer account area
            try:
                curr_url = self.get_current_url()
                if "/customer/account" in curr_url and "/customer/account/login" not in curr_url:
                    title = self.get_title().lower()
                    if "my account" in title or "my address" in title or "silhouette" in title:
                        logger.info("Customer verified authenticated via active customer account route.")
                        return True
            except Exception:
                pass

            # 6. Check for active errors if login popup modal is still open
            if self.is_login_modal_open():
                err_msg = self.get_response_error_message(timeout_ms=300)
                if err_msg:
                    logger.warning(f"Login failed with visible server error banner: '{err_msg}'")
                    return False
                recaptcha_err = self.page.locator(LoginLocators.RECAPTCHA_LOGIN_ERROR).first
                if recaptcha_err.is_visible(timeout=300):
                    r_txt = recaptcha_err.inner_text().strip()
                    logger.warning(f"Login failed due to reCAPTCHA challenge: '{r_txt}'")
                    return False

            self.page.wait_for_timeout(400)

        logger.warning(f"Authentication verification timed out after {timeout_ms}ms: no customer session detected.")
        return False

    def get_authenticated_customer_info(self) -> Dict[str, Any]:
        """Retrieve customer session data from local storage or customer section."""
        try:
            data = self.page.evaluate("""async () => {
                try {
                    let cache = window.localStorage.getItem('mage-cache-storage');
                    if (cache) {
                        let parsed = JSON.parse(cache);
                        if (parsed.customer && (parsed.customer.fullname || parsed.customer.email)) {
                            return parsed.customer;
                        }
                    }
                    // If not yet populated in localStorage, fetch customer section directly
                    const resp = await fetch('/customer/section/load/?sections=customer');
                    if (resp.ok) {
                        const json = await resp.json();
                        return json.customer || {};
                    }
                } catch(e) {}
                return {};
            }""")
            return data or {}
        except Exception as e:
            logger.debug(f"Notice retrieving customer info from storage: {e}")
            return {}

    def get_session_cookies(self) -> List[Dict[str, Any]]:
        """Return the current context cookies."""
        return self.page.context.cookies()

    # =========================================================================
    # Logout & Route Protection
    # =========================================================================

    def logout_customer(self) -> None:
        """Log out the current customer session cleanly."""
        logger.info("Logging out current customer session...")
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()

        # Try clicking Sign Out in account menu first
        try:
            account_trigger = self.page.locator(LoginLocators.ACCOUNT_MENU_TRIGGER).first
            if account_trigger.is_visible(timeout=3000):
                account_trigger.click(timeout=3000)
                self.wait_for_timeout(800)
                signout_link = self.page.locator(LoginLocators.SIGN_OUT_LINK).first
                if signout_link.is_visible(timeout=2000):
                    logger.info("Clicking 'Sign Out' link from account menu...")
                    with self.page.expect_navigation(wait_until="domcontentloaded", timeout=15000):
                        signout_link.click()
                    self.wait_for_dom_content_loaded()
                    self.wait_for_timeout(1000)
                    return
        except Exception as e:
            logger.debug(f"Menu signout notice: {e}, falling back to logout URL")

        # Fallback to direct logout URL
        self.goto("customer/account/logout/", wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(1000)

    def navigate_to_protected_account(self) -> str:
        """Attempt to access the protected customer account URL (/customer/account/)."""
        logger.info(f"Navigating to protected customer account URL: {LoginLocators.ACCOUNT_URL_PATH}")
        self.goto(LoginLocators.ACCOUNT_URL_PATH, wait_until="domcontentloaded")
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()
        dest_url = self.get_current_url()
        logger.info(f"Protected URL resolved to destination: '{dest_url}'")
        return dest_url
