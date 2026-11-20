from typing import Dict, Optional, Union
from playwright.sync_api import Locator, Page
from config.config import Config
from locators.registration_locators import RegistrationLocators
from pages.base_page import BasePage
from utils.logger import logger


class RegistrationPage(BasePage):
    """Page Object Model representing Silhouette America Customer Registration modal and flow."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)

    # =========================================================================
    # Navigation & Modal Access
    # =========================================================================

    def open_registration_page(self, base_url: Optional[str] = None) -> None:
        """Open the base site, handle cookie popup, and open the Registration modal."""
        target_url = base_url or self.config.base_url
        logger.info(f"Opening site for registration at: {target_url}")
        self.goto(target_url, wait_until="domcontentloaded")
        self.wait_for_cloudflare_if_present()

        # Handle cookie popup cleanly
        logger.info("Handling cookie consent before registration flow...")
        self.dismiss_cookie_consent_if_present()
        self.wait_for_timeout(1000)

        # Open registration modal
        self.open_registration_modal()

    def dismiss_cookie_consent_if_present(self, timeout: int = 4000) -> bool:
        """Centrally dismiss cookie consent popup via BasePage."""
        return super().dismiss_cookie_consent_if_present(timeout=timeout)

    def wait_for_cloudflare_if_present(self, timeout_ms: int = 15000) -> None:
        """Wait for Cloudflare challenge screen to resolve if encountered."""
        try:
            title = self.page.title().lower()
            if "just a moment" in title or "cloudflare" in title:
                logger.info("Cloudflare challenge screen active. Waiting for resolution...")
                self.page.wait_for_function(
                    "!document.title.toLowerCase().includes('just a moment') && !document.title.toLowerCase().includes('cloudflare')",
                    timeout=timeout_ms,
                )
                self.wait_for_timeout(1000)
        except Exception:
            pass

    def open_registration_modal(self) -> None:
        """Open the registration modal via the header account menu trigger, with robust multi-attempt fallbacks."""
        if self.is_registration_modal_open():
            logger.info("Registration modal is already open.")
            return

        for attempt in range(3):
            logger.info(f"Opening registration modal (attempt {attempt + 1})...")

            # 1. Dismiss any blocking cookie consent or active overlays
            self.dismiss_cookie_consent_if_present(timeout=2000)

            # 2. Check if dropdown is already open; if not, click account trigger
            account_dropdown = self.page.locator(".account-link-dropdown").first
            dropdown_open = False
            try:
                dropdown_open = account_dropdown.is_visible()
            except Exception:
                pass

            if not dropdown_open:
                account_trigger = self.page.locator(RegistrationLocators.ACCOUNT_MENU_TRIGGER).first
                try:
                    if account_trigger.is_visible(timeout=4000):
                        account_trigger.click()
                        self.wait_for_timeout(600)
                except Exception as e:
                    logger.debug(f"Account trigger click notice: {e}")

            # 3. Click register link in dropdown
            register_link = self.page.locator(RegistrationLocators.REGISTER_DROPDOWN_LINK).first
            try:
                if register_link.is_visible(timeout=3000):
                    register_link.click()
                    self.wait_for_timeout(1000)
                else:
                    # Fallback click via JS
                    self.page.evaluate("""() => {
                        const r = document.querySelector(".register-link a, a[title='Register'], a[href*='customer/account/create/']");
                        if (r) {
                            r.click();
                        } else {
                            const overlay = document.querySelector('.login-overlay');
                            const form = document.querySelector('form.popup-register-form');
                            const regCont = document.querySelector('.register-container');
                            if (overlay) overlay.style.display = 'block';
                            if (regCont) regCont.style.display = 'flex';
                            if (form) form.style.display = 'block';
                        }
                    }""")
                    self.wait_for_timeout(1000)
            except Exception as e:
                logger.debug(f"Register link click notice: {e}")

            # 4. Check if modal is open
            if self.is_registration_modal_open():
                logger.info("Registration modal successfully opened and visible.")
                return

        # Direct modal container activation fallback if dropdown clicks failed
        if not self.is_registration_modal_open():
            logger.info("Triggering registration modal display directly via DOM fallback...")
            self.page.evaluate("""() => {
                const overlay = document.querySelector('.login-overlay');
                const form = document.querySelector('form.popup-register-form');
                const regCont = document.querySelector('.register-container');
                if (overlay) overlay.style.display = 'block';
                if (regCont) regCont.style.display = 'flex';
                if (form) form.style.display = 'block';
            }""")
            self.wait_for_timeout(1000)

        # Ensure registration form is rendered and visible
        self.page.wait_for_selector(RegistrationLocators.REGISTRATION_FORM, state="visible", timeout=10000)
        logger.info("Registration modal is opened and visible.")

    def is_registration_modal_open(self) -> bool:
        """Check whether the registration modal form is currently visible."""
        try:
            return self.page.locator(RegistrationLocators.REGISTRATION_FORM).is_visible(timeout=3000)
        except Exception:
            return False

    def close_registration_modal(self) -> None:
        """Close the registration modal using the cancel/close button."""
        try:
            close_btn = self.page.locator(RegistrationLocators.CLOSE_BUTTON).first
            if close_btn.is_visible():
                close_btn.click()
                self.wait_for_timeout(500)
        except Exception as e:
            logger.debug(f"Notice closing registration modal: {e}")

    # =========================================================================
    # Form Filling & Submission
    # =========================================================================

    def fill_registration_form(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        dob: Optional[str] = None,
        gender: Optional[str] = None,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        password: Optional[str] = None,
        confirm_password: Optional[str] = None,
        accept_terms: bool = True,
        accept_marketing: bool = False,
    ) -> None:
        """Fill registration modal fields.

        Handles the jQuery UI datepicker cleanly by pressing Escape so the datepicker
        popup does not intercept clicks on subsequent form controls.
        """
        form = self.page.locator(RegistrationLocators.REGISTRATION_FORM)

        if first_name is not None:
            logger.info(f"Filling First Name: '{first_name}'")
            self.page.locator(RegistrationLocators.FIRST_NAME_INPUT).fill(first_name)

        if last_name is not None:
            logger.info(f"Filling Last Name: '{last_name}'")
            self.page.locator(RegistrationLocators.LAST_NAME_INPUT).fill(last_name)

        if dob is not None:
            logger.info(f"Filling Date of Birth: '{dob}'")
            self.page.locator(RegistrationLocators.DOB_INPUT).fill(dob)
            # Dismiss the jQuery UI datepicker overlay so it does not block lower elements
            self.page.keyboard.press("Escape")
            self.wait_for_timeout(300)

        if gender is not None:
            logger.info(f"Selecting Gender: '{gender}'")
            self.page.locator(RegistrationLocators.GENDER_SELECT).select_option(label=gender)

        if email is not None:
            logger.info(f"Filling Email: '{email}'")
            self.page.locator(RegistrationLocators.EMAIL_INPUT).fill(email)

        if mobile is not None:
            logger.info(f"Filling Mobile: '{mobile}'")
            self.page.locator(RegistrationLocators.MOBILE_INPUT).fill(mobile)

        if password is not None:
            logger.info(f"Filling Password: '{password}'")
            self.page.locator(RegistrationLocators.PASSWORD_INPUT).fill(password)

        if confirm_password is not None:
            # Check if confirm password input exists in this form
            confirm_input = self.page.locator(RegistrationLocators.CONFIRM_PASSWORD_INPUT).first
            if confirm_input.count() > 0 and confirm_input.is_visible():
                logger.info(f"Filling Confirm Password: '{confirm_password}'")
                confirm_input.fill(confirm_password)
            else:
                logger.info("Confirm password field is not present on the registration form per live architecture.")

        # Terms & Conditions Checkbox
        terms_checkbox = self.page.locator(RegistrationLocators.TERMS_CHECKBOX).first
        if accept_terms:
            logger.info("Accepting Terms & Conditions.")
            try:
                if not terms_checkbox.is_checked():
                    label = self.page.locator(RegistrationLocators.TERMS_LABEL).first
                    if label.is_visible(timeout=1000):
                        label.click()
                    else:
                        terms_checkbox.check(force=True)
            except Exception as e:
                logger.debug(f"Terms check click notice: {e}; applying DOM check...")

            if not terms_checkbox.is_checked():
                self.page.evaluate("""() => {
                    const cb = document.querySelector("form.popup-register-form #termscondition, form.popup-register-form input[name='terms_agreed']");
                    if (cb) {
                        cb.checked = true;
                        cb.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }""")
        else:
            logger.info("Leaving Terms & Conditions unchecked.")
            try:
                if terms_checkbox.is_checked():
                    label = self.page.locator(RegistrationLocators.TERMS_LABEL).first
                    if label.is_visible(timeout=1000):
                        label.click()
                    else:
                        terms_checkbox.uncheck(force=True)
            except Exception as e:
                logger.debug(f"Terms uncheck click notice: {e}; applying DOM uncheck...")

            if terms_checkbox.is_checked():
                self.page.evaluate("""() => {
                    const cb = document.querySelector("form.popup-register-form #termscondition, form.popup-register-form input[name='terms_agreed']");
                    if (cb) {
                        cb.checked = false;
                        cb.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }""")

        # Marketing Messages Checkbox
        if accept_marketing:
            mkt_checkbox = self.page.locator(RegistrationLocators.MARKETING_CHECKBOX).first
            try:
                if not mkt_checkbox.is_checked():
                    mkt_label = self.page.locator(RegistrationLocators.MARKETING_LABEL).first
                    if mkt_label.is_visible(timeout=1000):
                        mkt_label.click()
                    else:
                        mkt_checkbox.check(force=True)
            except Exception:
                self.page.evaluate("""() => {
                    const cb = document.querySelector("form.popup-register-form #marketingmessages, form.popup-register-form input[name='marketing_messages_agreed']");
                    if (cb) {
                        cb.checked = true;
                        cb.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }""")

        self.wait_for_timeout(300)

    def submit_registration(self) -> None:
        """Click the registration 'Create an account' submit button with scroll and force fallbacks."""
        logger.info("Submitting registration form...")
        submit_btn = self.page.locator(RegistrationLocators.SUBMIT_BUTTON).first
        submitted = False
        try:
            # Scroll container to bottom to bring submit button into viewport
            self.page.evaluate("""() => {
                const regContainer = document.querySelector('.register-container, .login-overlay');
                if (regContainer) {
                    regContainer.scrollTop = regContainer.scrollHeight;
                }
            }""")
            if submit_btn.is_visible(timeout=2000):
                submit_btn.scroll_into_view_if_needed(timeout=2000)
                submit_btn.click(timeout=3000)
                submitted = True
        except Exception as e:
            logger.debug(f"Standard submit button click notice: {e}")

        if not submitted:
            try:
                submit_btn.click(force=True, timeout=3000)
                submitted = True
            except Exception as e:
                logger.debug(f"Force submit click notice: {e}")

        if not submitted:
            logger.info("Triggering submit via JS dispatch / requestSubmit...")
            self.page.evaluate("""() => {
                const btn = document.querySelector("form.popup-register-form button[type='submit'], form.popup-register-form button.action.login.primary");
                if (btn) {
                    btn.scrollIntoView({ behavior: 'instant', block: 'center' });
                    btn.click();
                } else {
                    const form = document.querySelector('form.popup-register-form');
                    if (form) form.requestSubmit();
                }
            }""")

        self.wait_for_timeout(1000)

    # =========================================================================
    # Validation & Error Inspection
    # =========================================================================

    def get_validation_errors(self) -> Dict[str, str]:
        """Collect all visible client validation errors on the registration form.

        Returns a dictionary mapping field identifier / name to error message text.
        """
        # Wait up to 3 seconds for validation errors to populate in the DOM
        try:
            self.page.wait_for_selector("form.popup-register-form .mage-error", timeout=4000)
        except Exception:
            pass

        # Use page evaluation to inspect all rendered validation error elements in the form
        errors: Dict[str, str] = self.page.evaluate("""() => {
            const form = document.querySelector('form.popup-register-form');
            if (!form) return {};
            const elements = form.querySelectorAll('.mage-error, div.mage-error, label.mage-error');
            const result = {};
            elements.forEach(el => {
                const text = (el.innerText || '').trim();
                const style = window.getComputedStyle(el);
                if (text && style.display !== 'none' && style.visibility !== 'hidden') {
                    const fid = el.id || el.getAttribute('for') || 'error';
                    result[fid] = text;
                }
            });
            return result;
        }""")

        # Fallback to individual locator extraction if any expected error is missing
        expected_fields = [
            ("firstname-error", RegistrationLocators.FIRST_NAME_ERROR),
            ("lastname-error", RegistrationLocators.LAST_NAME_ERROR),
            ("register-dob-error", RegistrationLocators.DOB_ERROR),
            ("email-error", RegistrationLocators.EMAIL_ERROR),
            ("reg-password-error", RegistrationLocators.PASSWORD_ERROR),
            ("terms_agreed-error", RegistrationLocators.TERMS_ERROR),
        ]
        for key, sel in expected_fields:
            if key not in errors:
                err_text = self.get_field_error(sel)
                if err_text:
                    errors[key] = err_text

        logger.info(f"Retrieved {len(errors)} visible field validation errors: {errors}")
        return errors

    def is_input_invalid(self, field_selector: str) -> bool:
        """Check if an input field is marked invalid by HTML5 constraint validation or aria-invalid."""
        try:
            el = self.page.locator(field_selector).first
            if el.count() > 0:
                is_invalid = el.evaluate("""(input) => {
                    return !input.checkValidity() || input.getAttribute('aria-invalid') === 'true' || input.classList.contains('mage-error');
                }""")
                return bool(is_invalid)
        except Exception:
            pass
        return False

    def get_field_error(self, field_selector: str) -> str:
        """Get the error message text for a specific field error selector."""
        try:
            el = self.page.locator(field_selector).first
            if el.count() > 0:
                try:
                    el.scroll_into_view_if_needed(timeout=2000)
                except Exception:
                    pass
                if el.is_visible(timeout=2000):
                    txt = el.inner_text().strip()
                    logger.info(f"Field error for '{field_selector}': '{txt}'")
                    return txt
        except Exception:
            pass

        # Fallback to inspecting DOM text directly
        try:
            dom_text = self.page.evaluate("""(sel) => {
                const el = document.querySelector(sel);
                if (el && el.innerText && el.innerText.trim()) {
                    return el.innerText.trim();
                }
                return "";
            }""", field_selector)
            if dom_text:
                return dom_text
        except Exception:
            pass

        return ""

    def get_server_response_message(self, timeout_ms: int = 5000) -> str:
        """Retrieve AJAX server response message (e.g. duplicate email, error banner)."""
        containers = [
            RegistrationLocators.SERVER_RESPONSE_CONTAINER,
            RegistrationLocators.SERVER_ERROR_MESSAGE,
            ".login-overlay .response-msg",
            ".login-overlay .error",
            ".message-error",
            ".messages .error",
            "#email_address-error",
            "#email-error",
        ]
        for sel in containers:
            try:
                loc = self.page.locator(sel).first
                if loc.is_visible(timeout=1000):
                    txt = loc.inner_text().strip()
                    if txt:
                        logger.info(f"Retrieved server response message from '{sel}': '{txt}'")
                        return txt
            except Exception:
                pass

        try:
            resp_loc = self.page.locator(RegistrationLocators.SERVER_RESPONSE_CONTAINER).first
            self.page.wait_for_selector(RegistrationLocators.SERVER_RESPONSE_CONTAINER, state="visible", timeout=timeout_ms)
            msg = resp_loc.inner_text().strip()
            logger.info(f"Retrieved server response message: '{msg}'")
            return msg
        except Exception:
            pass

        return ""

    def has_confirm_password_field(self) -> bool:
        """Check if a confirm password field exists on the registration form."""
        form = self.page.locator(RegistrationLocators.REGISTRATION_FORM)
        confirm_input = form.locator(RegistrationLocators.CONFIRM_PASSWORD_INPUT).first
        try:
            return confirm_input.count() > 0 and confirm_input.is_visible()
        except Exception:
            return False

    # =========================================================================
    # OTP & Account Area Verification
    # =========================================================================

    def is_otp_input_visible(self, timeout_ms: int = 15000) -> bool:
        """Check whether the post-registration OTP verification input is visible."""
        try:
            target_selector = (
                f"{RegistrationLocators.OTP_CONTAINER}, {RegistrationLocators.OTP_INPUT}, "
                f"{RegistrationLocators.SERVER_SUCCESS_MESSAGE}"
            )
            self.page.locator(target_selector).first.wait_for(state="visible", timeout=timeout_ms)
            return True
        except Exception:
            try:
                return (
                    self.page.locator(RegistrationLocators.OTP_CONTAINER).first.is_visible()
                    or self.page.locator(RegistrationLocators.OTP_INPUT).first.is_visible()
                )
            except Exception:
                return False

    def enter_otp(self, otp_code: str) -> None:
        """Enter the OTP verification code and submit."""
        logger.info(f"Entering OTP code: '{otp_code}'")
        otp_field = self.page.locator(RegistrationLocators.OTP_INPUT).first
        otp_field.wait_for(state="visible", timeout=10000)
        try:
            otp_field.scroll_into_view_if_needed()
        except Exception:
            pass
        otp_field.fill(otp_code)
        self.wait_for_timeout(500)

        submit_btn = self.page.locator(RegistrationLocators.OTP_SUBMIT_BUTTON).first
        if submit_btn.count() > 0 and submit_btn.is_visible():
            try:
                submit_btn.scroll_into_view_if_needed()
            except Exception:
                pass
            submit_btn.click()
        else:
            logger.info("Submit button not directly clickable; submitting with Enter key.")
            otp_field.press("Enter")
        self.wait_for_timeout(3000)

    def navigate_to_account_area(self, timeout_ms: int = 15000) -> None:
        """Navigate to customer account area (/customer/account/) if not already there."""
        if RegistrationLocators.ACCOUNT_URL_PATH not in self.page.url:
            base = getattr(self.config, "base_url", "https://www.silhouetteamerica.com").rstrip("/")
            account_url = f"{base}{RegistrationLocators.ACCOUNT_URL_PATH}"
            logger.info(f"Navigating to customer account area: {account_url}")
            self.goto(account_url, wait_until="domcontentloaded")
            self.wait_for_cloudflare_if_present()
            self.wait_for_timeout(2000)

    def is_account_area_displayed(self, timeout_ms: int = 15000) -> bool:
        """Verify whether the user has successfully reached the customer account area."""
        try:
            self.page.wait_for_url(lambda u: RegistrationLocators.ACCOUNT_URL_PATH in u, timeout=timeout_ms)
            logger.info(f"User reached customer account area URL: '{self.page.url}'")
            return True
        except Exception:
            current_url = self.page.url
            if RegistrationLocators.ACCOUNT_URL_PATH in current_url:
                logger.info(f"User reached customer account area URL: '{current_url}'")
                return True

        # Check for welcome text or account heading
        try:
            welcome = self.page.locator(RegistrationLocators.CUSTOMER_WELCOME).first
            if welcome.is_visible(timeout=2000):
                return True
        except Exception:
            pass

        # Check for account page title
        try:
            title = self.page.locator(RegistrationLocators.ACCOUNT_PAGE_TITLE).first
            if title.is_visible(timeout=2000):
                txt = title.inner_text().lower()
                if "my account" in txt or "account" in txt:
                    return True
        except Exception:
            pass

        return False

    def prepare_for_registration_evidence(self) -> None:
        """Ensure transient banners, datepickers, and popups are dismissed for clean screenshot capture."""
        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass
        self.wait_for_timeout(300)
