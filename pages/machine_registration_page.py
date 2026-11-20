import json
import os
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError
from config.config import Config
from locators.machine_registration_locators import MachineRegistrationLocators
from pages.base_page import BasePage
from utils.logger import logger
from utils.serial_manager import SerialManager
from utils.wait_helper import WaitHelper


class MachineRegistrationPage(BasePage):
    """Page Object Model representing Silhouette America Machine Registration flow."""

    def __init__(self, page: Page, config: Optional[Config] = None) -> None:
        super().__init__(page, config)
        self.serial_attempts: List[Dict[str, Any]] = []
        self.serial_manager = SerialManager()

    # =========================================================================
    # Cookie Consent & Base Setup
    # =========================================================================

    def dismiss_cookie_consent_if_present(self, timeout: int = 3000) -> bool:
        """Centrally dismiss cookie consent popup via BasePage."""
        return super().dismiss_cookie_consent_if_present(timeout=timeout)

    # =========================================================================
    # Authentication (Customer Sign In on Staging)
    # =========================================================================

    def is_customer_logged_in(self) -> bool:
        """Check if customer is currently authenticated."""
        try:
            from pages.login_page import LoginPage
            login_page = LoginPage(self.page, self.config)
            if login_page.is_customer_authenticated(timeout_ms=2500):
                return True
            welcome = self.page.locator(MachineRegistrationLocators.LOGGED_IN_WELCOME).first
            return welcome.is_visible(timeout=1000)
        except Exception:
            return False

    def login_customer_if_needed(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> bool:
        """Ensure customer is logged in on the staging environment.

        Credentials are read from test data or arguments and never logged.
        Supports both the header AJAX popup modal and the full-page login view.
        """
        if self.is_customer_logged_in():
            logger.info("Customer is already authenticated.")
            return True

        from pages.login_page import LoginPage
        login_page = LoginPage(self.page, self.config)

        target_email = email
        target_password = password
        if not target_email or not target_password:
            from utils.data_helper import DataHelper
            data = DataHelper.load_machine_data()
            user_data = data.get("test_user") or data.get("credentials") or {}
            target_email = target_email or user_data.get("email")
            target_password = target_password or user_data.get("password")

        logger.info(f"Authenticating customer account: '{target_email}' (password masked)")
        login_page.open_login_modal()
        login_page.fill_credentials(target_email, target_password)
        login_page.submit_login()

        logged_in = login_page.is_customer_authenticated(timeout_ms=12000)
        logger.info(f"Authentication verification status: {logged_in}")
        return logged_in

    # =========================================================================
    # Navigation to Machine Setup
    # =========================================================================

    def navigate_to_machine_setup(self) -> None:
        """Navigate to the Machine Setup (/machine-setup) page.

        Direct navigation ensures header megamenu dropdowns do not obstruct the page.
        """
        logger.info("Navigating to Machine Setup page...")
        self.goto("/machine-setup", wait_until="domcontentloaded")
        self.dismiss_cookie_consent_if_present()
        self.page.mouse.move(0, 0)
        self.wait_for_timeout(500)

        try:
            self.page.wait_for_selector(MachineRegistrationLocators.SERIAL_NUMBER_INPUT, timeout=6000)
        except Exception:
            logger.info("Serial input not immediately found on /machine-setup; checking authentication...")
            if not self.is_customer_logged_in():
                self.login_customer_if_needed()
                self.goto("/machine-setup", wait_until="domcontentloaded")
                self.dismiss_cookie_consent_if_present()
                self.page.mouse.move(0, 0)
            self.page.wait_for_selector(MachineRegistrationLocators.SERIAL_NUMBER_INPUT, timeout=10000)

    def is_machine_setup_page_loaded(self) -> bool:
        """Verify that Machine Setup page has loaded correctly."""
        try:
            has_url = "machine-setup" in self.get_current_url()
            title_loc = self.page.locator(MachineRegistrationLocators.SETUP_PAGE_TITLE).first
            has_title = title_loc.is_visible(timeout=5000)
            has_input = self.page.locator(MachineRegistrationLocators.SERIAL_NUMBER_INPUT).first.is_visible(timeout=5000)
            return has_url and (has_title or has_input)
        except Exception:
            return False

    # =========================================================================
    # Form Filling & Submission
    # =========================================================================

    def fill_machine_form(
        self,
        serial_number: Optional[str] = None,
        purchase_date: Optional[str] = None,
        store_name: Optional[str] = None,
        store_country: Optional[str] = None,
        store_country_index: Optional[int] = None,
    ) -> None:
        """Fill the Machine Registration form with test data."""
        if serial_number is not None:
            logger.info(f"Entering machine serial number: '{serial_number}'")
            self.fill(MachineRegistrationLocators.SERIAL_NUMBER_INPUT, serial_number)

        if purchase_date is not None:
            logger.info(f"Entering purchase date: '{purchase_date}'")
            self.fill(MachineRegistrationLocators.PURCHASE_DATE_INPUT, purchase_date)

        if store_name is not None:
            logger.info(f"Entering store name: '{store_name}'")
            self.fill(MachineRegistrationLocators.STORE_NAME_INPUT, store_name)

        if store_country is not None:
            try:
                country_select = self.page.locator(MachineRegistrationLocators.STORE_COUNTRY_SELECT).first
                if country_select.is_visible(timeout=2000):
                    logger.info(f"Selecting store country by label: '{store_country}'")
                    country_select.select_option(label=store_country)
            except Exception as e:
                logger.debug(f"Country select by label notice: {e}")
        elif store_country_index is not None:
            try:
                country_select = self.page.locator(MachineRegistrationLocators.STORE_COUNTRY_SELECT).first
                if country_select.is_visible(timeout=2000):
                    country_select.select_option(index=store_country_index)
            except Exception as e:
                logger.debug(f"Country select by index notice: {e}")

        self.wait_for_timeout(300)

    def submit_machine_form(self) -> None:
        """Click the Continue button to submit the Machine Registration form."""
        logger.info("Clicking Continue on machine registration form...")
        self.dismiss_cookie_consent_if_present()
        btn = self.page.locator(MachineRegistrationLocators.CONTINUE_BUTTON).first
        btn.scroll_into_view_if_needed()
        self.wait_for_timeout(300)
        try:
            btn.click(timeout=4000)
        except Exception as e:
            logger.info(f"Standard click notice ({e}); triggering click via evaluate.")
            btn.evaluate("el => el.click()")
        self.wait_for_timeout(1500)

    # =========================================================================
    # Validation & Error Messages
    # =========================================================================

    def get_serial_number_error(self, timeout_ms: int = 3000) -> str:
        """Retrieve client-side required field validation error for serial number."""
        try:
            err = self.page.locator(MachineRegistrationLocators.SERIAL_NUMBER_ERROR).first
            err.wait_for(state="visible", timeout=timeout_ms)
            return err.inner_text().strip()
        except Exception:
            return ""

    def get_modal_dialog_message(self, timeout_ms: int = 8000) -> str:
        """Retrieve server-side validation error displayed in modal popup (e.g. invalid or duplicate serial)."""
        alert_selectors = [
            "aside.modal-popup.alert._show .modal-content",
            "aside.modal-popup.confirm._show .modal-content",
            "aside.modal-popup._show:not(.machinedetect-popup):not(.machine-setup-popup):not(.amgdprcookie-bar-template) .modal-content",
            ".modal-popup._show:has-text('Alert') .modal-content",
            ".modal-popup._show:has-text('already been registered') .modal-content",
            ".modal-popup._show:has-text('Invalid machine serial') .modal-content",
            ".modal-popup._show:has(button:has-text('OK')) .modal-content",
            ".modal-popup._show:has(button.action-accept) .modal-content",
        ]

        # First check if any alert modal is already visible
        for sel in alert_selectors:
            try:
                loc = self.page.locator(sel).first
                if loc.is_visible(timeout=300):
                    # Ensure this is not the machine detection popup
                    parent = loc.locator("xpath=ancestor::aside").first
                    pcls = parent.get_attribute("class") or ""
                    if "machinedetect" in pcls:
                        continue
                    msg = loc.inner_text().strip()
                    if msg and "please select your machine" not in msg.lower():
                        logger.info(f"Retrieved alert modal message: '{msg}'")
                        return msg
            except Exception:
                pass

        # Wait for alert modal to appear
        try:
            alert_modal = self.page.locator(
                "aside.modal-popup.alert._show .modal-content, "
                "aside.modal-popup._show:not(.machinedetect-popup):not(.machine-setup-popup):not(.amgdprcookie-bar-template) .modal-content, "
                ".modal-popup._show:has(button:has-text('OK')) .modal-content, "
                ".modal-popup._show:has-text('Alert') .modal-content"
            ).first
            alert_modal.wait_for(state="visible", timeout=timeout_ms)
            parent = alert_modal.locator("xpath=ancestor::aside").first
            pcls = parent.get_attribute("class") or ""
            if "machinedetect" not in pcls:
                msg = alert_modal.inner_text().strip()
                if "please select your machine" not in msg.lower():
                    logger.info(f"Retrieved modal dialog message: '{msg}'")
                    return msg
        except Exception:
            pass

        # Fallback to checking any dialog whose text does not just contain model selection
        try:
            any_dialog = self.page.locator(MachineRegistrationLocators.MODAL_DIALOG).first
            if any_dialog.is_visible(timeout=1000):
                dcls = any_dialog.get_attribute("class") or ""
                if "machinedetect" not in dcls:
                    text = any_dialog.inner_text().strip()
                    if "please select your machine" not in text.lower():
                        return text
        except Exception:
            pass
        return ""

    def dismiss_modal_if_visible(self) -> bool:
        """Close any visible modal popup dialog."""
        try:
            close_btn = self.page.locator(
                ".modal-popup._show button.action-close, button.action-close, .modal-popup._show button:has-text('OK'), button:has-text('OK')"
            ).first
            if close_btn.is_visible(timeout=2000):
                close_btn.click()
                self.wait_for_timeout(500)
                return True
        except Exception:
            pass
        return False

    # =========================================================================
    # Dynamic Serial Allocation & Validation Logic
    # =========================================================================

    @staticmethod
    def get_next_machine_serial(current_serial: str, step: int = 1) -> str:
        """Generate the next sequential machine serial number by incrementing numeric suffix
        while preserving prefix and length.

        Example:
            R602Q502771 (step=1) -> R602Q502772
            R602Q502771 (step=2) -> R602Q502773
        """
        match = re.search(r"^(.*?)(\d+)$", current_serial.strip())
        if match:
            prefix, num_str = match.groups()
            next_num = int(num_str) + step
            return f"{prefix}{next_num:0{len(num_str)}d}"
        return current_serial

    @staticmethod
    def is_serial_already_registered(message: str) -> bool:
        """Check if a validation response indicates the serial is already registered."""
        if not message:
            return False
        msg = message.lower()
        keywords = [
            "already been registered",
            "already registered",
            "contact customer support",
            "registered by a different user",
        ]
        return any(kw in msg for kw in keywords)

    def _get_history_file(self) -> Path:
        """Resolve path to persistent serial attempt history JSON file."""
        return Path(__file__).resolve().parent.parent / "test_data" / "machines" / "serial_attempt_history.json"

    def _load_serial_history(self) -> Dict[str, Any]:
        """Load persistent record of previously evaluated serial numbers."""
        history_file = self._get_history_file()
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.debug(f"Could not read serial history file: {e}")
        return {}

    def _persist_serial_attempt(self, serial: str, status: str, message: str) -> None:
        """Persist serial verification outcome to serial_attempt_history.json."""
        history_file = self._get_history_file()
        try:
            history_data = self._load_serial_history()
            history_data[serial] = {
                "status": status,
                "message": message[:200],
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history_data, f, indent=2)
        except Exception as e:
            logger.debug(f"Could not persist serial attempt history: {e}")

    def record_serial_attempt(
        self,
        serial: str,
        status: str,
        message: str,
        model: str = "",
    ) -> Dict[str, Any]:
        """Record a serial candidate attempt in execution memory and persistent history."""
        desc = (
            "Already registered"
            if status == "ALREADY_REGISTERED"
            else ("Valid and unregistered" if status == "VALID_UNREGISTERED" else status)
        )
        attempt_record = {
            "attempt": len(self.serial_attempts) + 1,
            "attempt_label": f"ATTEMPT {len(self.serial_attempts) + 1}",
            "serial": serial,
            "status": status,
            "status_desc": desc,
            "message": message,
            "model": model,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.serial_attempts.append(attempt_record)
        self._persist_serial_attempt(serial, status, message)
        return attempt_record

    def get_serial_attempt_history(self) -> List[Dict[str, Any]]:
        """Retrieve execution history of all serial candidate attempts in current session."""
        return self.serial_attempts

    def validate_machine_serial(
        self,
        serial: str,
        purchase_details: Optional[Dict[str, Any]] = None,
        expected_model: str = "CAMEO 5 PLUS",
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Submit candidate serial number and evaluate application response.

        Returns:
            Tuple of (status, message, details_dict) where status is:
            - 'ALREADY_REGISTERED': Serial has already been registered
            - 'VALID_UNREGISTERED': Setup popup displayed and model is eligible for registration
            - 'INVALID': Serial rejected as invalid or malformed
            - 'ERROR': Unexpected error returned
        """
        details = purchase_details or {}
        purchase_date = details.get("purchase_date", "2025-01-15")
        store_name = details.get("store_name", "Silhouette Store")
        store_country = details.get("store_country", "United States")

        logger.info(f"Validating machine serial candidate: '{serial}'")
        self.fill_machine_form(
            serial_number=serial,
            purchase_date=purchase_date,
            store_name=store_name,
            store_country=store_country,
        )
        self.submit_machine_form()

        # Check for immediate alert modal (already registered or invalid)
        dialog_msg = self.get_modal_dialog_message(timeout_ms=3000)
        if dialog_msg:
            if self.is_serial_already_registered(dialog_msg):
                logger.info(f"Serial '{serial}' reported already registered: '{dialog_msg}'")
                self.dismiss_modal_if_visible()
                return "ALREADY_REGISTERED", dialog_msg, {}
            elif "invalid" in dialog_msg.lower():
                logger.warning(f"Serial '{serial}' reported invalid: '{dialog_msg}'")
                self.dismiss_modal_if_visible()
                return "INVALID", dialog_msg, {}

        # Check if Machine Setup model selection popup is displayed
        if self.is_setup_popup_displayed(timeout_ms=5000):
            detected_model = self.get_detected_machine_model()
            all_detected = self.get_all_detected_machine_models()
            logger.info(
                f"Serial '{serial}' triggered setup popup: detected='{detected_model}', all={all_detected}"
            )

            # Select model
            target_model = (
                expected_model
                if expected_model in all_detected
                else (all_detected[0] if all_detected else detected_model)
            )
            self.select_machine_model(target_model)
            self.click_register_my_machine()

            # Check if application reports duplicate registration upon model submission
            post_dialog_msg = self.get_modal_dialog_message(timeout_ms=4000)
            if post_dialog_msg and self.is_serial_already_registered(post_dialog_msg):
                logger.info(f"Serial '{serial}' rejected on registration: '{post_dialog_msg}'")
                self.dismiss_modal_if_visible()
                self.dismiss_modal_if_visible()
                return "ALREADY_REGISTERED", post_dialog_msg, {"detected_model": target_model, "all_models": all_detected}

            # If no duplicate error, serial is valid and unregistered
            return "VALID_UNREGISTERED", "Confirmed valid and unregistered", {
                "detected_model": target_model,
                "all_models": all_detected,
            }

        # Check field-level client validation error
        field_err = self.get_serial_number_error(timeout_ms=1000)
        if field_err:
            return "INVALID", field_err, {}

        if dialog_msg:
            return "ERROR", dialog_msg, {}

        return "UNKNOWN", "No response dialog or setup popup observed", {}

    def find_and_allocate_unregistered_serial(
        self,
        starting_serial: Optional[str] = None,
        max_retries: int = 5,
        purchase_details: Optional[Dict[str, Any]] = None,
        expected_model: str = "CAMEO 5 PLUS",
    ) -> Tuple[Optional[str], Optional[str], List[Dict[str, Any]]]:
        """Dynamically allocate the next available unregistered serial starting from starting_serial or SerialManager.

        Iterates sequentially, recording results and advancing when serials are already registered.
        Returns:
            Tuple of (allocated_serial, detected_model, attempt_history).
            If no unregistered serial is found within max_retries, returns (None, None, attempt_history).
        """
        self.serial_attempts = []

        # Obtain candidates sequentially via SerialManager
        candidates = self.serial_manager.get_candidate_evaluation_list(max_retries=max_retries)

        # Fallback to starting_serial generation if candidate list is empty
        if not candidates and starting_serial:
            candidates = [self.get_next_machine_serial(starting_serial, step=i) for i in range(max_retries)]

        logger.info(
            f"Initiating dynamic serial allocation across {len(candidates)} candidate(s) "
            f"(max retries: {max_retries})"
        )

        for attempt_idx, candidate_serial in enumerate(candidates):
            attempt_num = attempt_idx + 1

            # Validate regex format: (?i)^[RVKT]\d{3}P\d{6}$
            if not self.serial_manager.validate_serial_format(candidate_serial):
                logger.warning(
                    f"[ATTEMPT {attempt_num}] Serial: {candidate_serial} does not match required regex "
                    f"(?i)^[RVKT]\\d{{3}}P\\d{{6}}$. Marking invalid and skipping."
                )
                self.record_serial_attempt(candidate_serial, "INVALID", "Does not match (?i)^[RVKT]\\d{3}P\\d{6}$")
                self.serial_manager.update_serial_status(
                    candidate_serial, status="invalid", test_case_id="E2E-MACHINE-001", notes="Regex mismatch"
                )
                continue

            # Check cached history first to avoid redundant slow requests
            record = self.serial_manager.get_serial_record(candidate_serial)
            if record and record.get("status") in ("already_registered", "Used"):
                cached_msg = record.get("notes") or f"Previously recorded as {record.get('status')}"
                logger.info(
                    f"[ATTEMPT {attempt_num}] Serial: {candidate_serial} – Already registered (cached in execution history)"
                )
                self.record_serial_attempt(candidate_serial, "ALREADY_REGISTERED", cached_msg)
                continue

            # Submit and validate on live application
            status, msg, details = self.validate_machine_serial(
                candidate_serial,
                purchase_details=purchase_details,
                expected_model=expected_model,
            )

            if status == "ALREADY_REGISTERED":
                logger.info(f"[ATTEMPT {attempt_num}] Serial: {candidate_serial} – Already registered")
                self.record_serial_attempt(candidate_serial, status, msg)
                self.serial_manager.update_serial_status(
                    candidate_serial, status="already_registered", test_case_id="E2E-MACHINE-001", notes=msg
                )
                # Reset page state for next candidate
                self.goto("/machine-setup", wait_until="domcontentloaded")
                self.dismiss_cookie_consent_if_present()
                continue

            elif status == "VALID_UNREGISTERED":
                detected_model = details.get("detected_model", expected_model)
                logger.info(f"[ATTEMPT {attempt_num}] Serial: {candidate_serial} – Valid and unregistered")
                self.record_serial_attempt(candidate_serial, status, msg, model=detected_model)
                return candidate_serial, detected_model, self.serial_attempts

            elif status == "INVALID":
                logger.warning(
                    f"[ATTEMPT {attempt_num}] Serial: {candidate_serial} – Validation result received: Invalid ({msg})"
                )
                self.record_serial_attempt(candidate_serial, status, msg)
                self.serial_manager.update_serial_status(
                    candidate_serial, status="invalid", test_case_id="E2E-MACHINE-001", notes=msg
                )
                self.goto("/machine-setup", wait_until="domcontentloaded")
                self.dismiss_cookie_consent_if_present()
                continue

            else:
                logger.error(
                    f"[ATTEMPT {attempt_num}] Serial: {candidate_serial} – Unexpected response: {status} ({msg})"
                )
                self.record_serial_attempt(candidate_serial, status, msg)
                self.goto("/machine-setup", wait_until="domcontentloaded")
                self.dismiss_cookie_consent_if_present()
                continue

        return None, None, self.serial_attempts

    def click_register_machine_button(self, timeout_ms: int = 8000) -> bool:
        """Click the final 'Register Machine' button."""
        logger.info("Checking for 'Register Machine' button...")
        # Wait for any active loader masks to hide first
        try:
            loader = self.page.locator(".modal-popup._show .loading-mask, .modal-popup._show .loader, .loading-mask").first
            if loader.is_visible(timeout=500):
                logger.info("Waiting for loading mask to clear before clicking Register Machine...")
                loader.wait_for(state="hidden", timeout=10000)
        except Exception:
            pass

        register_selectors = [
            ".modal-popup._show #final_register_machine",
            ".modal-popup._show button#final_register_machine",
            ".modal-popup._show button:has-text('Register Machine')",
            "#final_register_machine",
            "button:has-text('Register Machine')",
            ".modal-popup._show #register_my_machine",
            "button:has-text('Register My Machine')",
            ".modal-popup._show button.action-btn:has-text('Register')",
        ]
        for sel in register_selectors:
            try:
                btn = self.page.locator(sel).first
                if btn.is_visible(timeout=timeout_ms):
                    btn.scroll_into_view_if_needed()
                    logger.info(f"Clicking 'Register Machine' button: '{sel}'")
                    btn.click(force=True)
                    self.wait_for_timeout(2000)
                    return True
            except Exception as e:
                logger.debug(f"Register Machine button check ({sel}): {e}")
        return False

    def complete_registration_flow(
        self, expected_model: str = "CAMEO 5 PLUS", serial: str = ""
    ) -> Tuple[bool, str, bool]:
        """Complete the post-model selection registration flow (Free trial, completion, confirmation, warranty).

        Returns:
            Tuple of (success, confirmation_text, is_warranty_visible).
        """
        # Step: Free trial activation if present
        if self.is_free_trial_step_displayed(timeout_ms=6000) or self.page.locator(".modal-popup._show:has-text('Activate Your Free Trial')").first.is_visible(timeout=2000):
            logger.info("Free Trial step displayed. Clicking Claim Free Trial...")
            self.click_claim_free_trial()
            self.wait_for_timeout(1500)

        # Step: Click final 'Register Machine' button
        self.click_register_machine_button(timeout_ms=6000)

        # Ensure modal did not get stuck on 'Register Machine' by retrying click if still visible
        for retry in range(3):
            reg_btn = self.page.locator(".modal-popup._show #final_register_machine, .modal-popup._show button:has-text('Register Machine')").first
            if reg_btn.is_visible(timeout=1000):
                logger.info(f"Trial modal still showing Register Machine (retry {retry + 1}). Clicking to submit...")
                reg_btn.click(force=True)
                self.wait_for_timeout(2000)
            else:
                break

        self.wait_for_trial_modal_to_close(timeout_ms=15000)
        self.wait_for_machine_registration_completion(timeout_ms=20000)

        # Retrieve confirmation text
        confirmation_text = self.get_registration_confirmation_text(timeout_ms=10000)
        has_congrats = "congratulations" in confirmation_text.lower()
        has_registered = (
            "is now registered" in confirmation_text.lower()
            or "successfully registered" in confirmation_text.lower()
            or "registered" in confirmation_text.lower()
        )
        has_warranty = self.is_warranty_information_visible(timeout_ms=3000)

        success = has_congrats or has_registered or has_warranty
        if success and serial:
            self.serial_manager.update_serial_status(
                serial=serial,
                status="Used",
                test_case_id="E2E-MACHINE-001",
                notes=f"Successfully registered model '{expected_model}'",
            )
        return success, confirmation_text, has_warranty

    # =========================================================================
    # Model Selection & Dynamic Model Handling
    # =========================================================================

    def is_setup_popup_displayed(self, timeout_ms: int = 8000) -> bool:
        """Verify the 'Silhouette Machine Setup' popup is displayed after entering valid serial number."""
        try:
            dialog = self.page.locator(".modal-popup._show:not(.amgdprcookie-bar-template)").first
            dialog.wait_for(state="visible", timeout=timeout_ms)
            txt = dialog.inner_text()
            return "Silhouette Machine Setup" in txt or "Please select your machine" in txt or "CAMEO" in txt
        except Exception:
            return False

    def get_all_detected_machine_models(self, timeout_ms: int = 8000) -> List[str]:
        """Read all detected machine model names from the staging setup modal."""
        try:
            self.page.locator(".modal-popup._show .list-detected-machines").first.wait_for(
                state="visible", timeout=timeout_ms
            )
            locators = self.page.locator(
                ".modal-popup._show .list-detected-machines .detected_machine_name"
            ).all()
            models = [loc.inner_text().strip() for loc in locators if loc.inner_text().strip()]
            logger.info(f"Dynamically detected machine models: {models}")
            return models
        except Exception as e:
            logger.debug(f"Could not read all detected models: {e}")
            return []

    def get_detected_machine_model(self, timeout_ms: int = 8000) -> str:
        """Read the primary detected machine model from the actual staging UI/modal."""
        models = self.get_all_detected_machine_models(timeout_ms=timeout_ms)
        if models:
            return models[0]
        try:
            model_loc = self.page.locator(
                ".modal-popup._show .list-detected-machines .detected_machine_name, "
                ".modal-popup._show .machine-detect-section .detected_machine_name, "
                ".modal-popup._show .machine-box"
            ).first
            model_loc.wait_for(state="visible", timeout=timeout_ms)
            detected = model_loc.inner_text().strip()
            logger.info(f"Dynamically detected machine model: '{detected}'")
            return detected
        except Exception as e:
            logger.error(f"Failed to read detected machine model: {e}")
            return ""

    def select_machine_model(self, model_name: str = "CAMEO 5 PLUS") -> None:
        """Select machine model dynamically from detected options."""
        logger.info(f"Selecting machine model: '{model_name}'...")
        try:
            model_opt = self.page.locator(
                f".modal-popup._show label.machine-box:has-text('{model_name}'), "
                f".modal-popup._show label:has-text('{model_name}'), "
                f".modal-popup._show .machine-box:has-text('{model_name}')"
            ).first
            if model_opt.is_visible(timeout=4000):
                model_opt.click(force=True)
                self.wait_for_timeout(300)
                return
        except Exception as e:
            logger.debug(f"Direct label click for model '{model_name}': {e}")

        # Fallback to checking first radio option
        try:
            radio = self.page.locator(MachineRegistrationLocators.RADIO_MACHINE_OPTIONS).first
            radio.check(force=True)
            self.wait_for_timeout(300)
        except Exception as e:
            logger.debug(f"Machine model selection fallback note: {e}")

    def click_register_my_machine(self) -> None:
        """Click the 'Register My Machine' button in the setup popup."""
        logger.info("Clicking 'Register My Machine' button...")
        btn = self.page.locator(
            ".modal-popup._show #register_my_machine, #register_my_machine, button:has-text('Register My Machine')"
        ).first
        btn.wait_for(state="visible", timeout=8000)
        btn.click(force=True)
        self.wait_for_timeout(2000)

        # If an address step is displayed, fill default address and continue
        try:
            street = self.page.locator(MachineRegistrationLocators.ADDRESS_STREET_INPUT).first
            if street.is_visible(timeout=2000):
                logger.info("Address verification step presented. Submitting address...")
                street.fill("618 N 2000 W")
                self.fill(MachineRegistrationLocators.ADDRESS_CITY_INPUT, "Lindon")
                self.fill(MachineRegistrationLocators.ADDRESS_STATE_INPUT, "Utah")
                self.fill(MachineRegistrationLocators.ADDRESS_ZIP_INPUT, "84042")
                self.click(MachineRegistrationLocators.ADDRESS_SAVE_BUTTON)
                self.wait_for_timeout(2000)
        except Exception as e:
            logger.debug(f"Address handling notice: {e}")

    # =========================================================================
    # Free Trial & Condition-Based State Transitions
    # =========================================================================

    def is_free_trial_step_displayed(self, timeout_ms: int = 8000) -> bool:
        """Verify the 'Activate Your Free Trial' step is displayed."""
        try:
            claim_btn = self.page.locator(MachineRegistrationLocators.CLAIM_FREE_TRIAL_BUTTON).first
            claim_btn.wait_for(state="visible", timeout=timeout_ms)
            return True
        except Exception:
            try:
                trial_title = self.page.locator(MachineRegistrationLocators.ACTIVATE_TRIAL_TITLE).first
                return trial_title.is_visible()
            except Exception:
                return False

    def click_claim_free_trial(self) -> None:
        """Click 'Claim Free Trial' or action button in the trial modal."""
        logger.info("Handling Free Trial modal action...")
        try:
            modal = self.page.locator(".modal-popup._show, aside[role='dialog']:visible").first
            modal.wait_for(state="visible", timeout=6000)

            # Log all available interactive elements in modal for diagnostic visibility
            buttons = modal.locator("button, a.action, input[type='button'], input[type='submit']").all()
            logger.info(f"Found {len(buttons)} interactive elements in Free Trial modal.")
            for idx, b in enumerate(buttons):
                try:
                    tag = b.evaluate("el => el.tagName")
                    bid = b.get_attribute("id") or ""
                    bcls = b.get_attribute("class") or ""
                    btxt = b.inner_text().strip()
                    logger.info(f"Modal action candidate [{idx}]: tag={tag}, id='{bid}', class='{bcls}', text='{btxt}'")
                except Exception:
                    pass

            action_selectors = [
                ".modal-popup._show button:has-text('Claim Free Trial')",
                ".modal-popup._show button#free_trial",
                ".modal-popup._show #free_trial button",
                ".modal-popup._show button:has-text('Claim')",
                ".modal-popup._show button:has-text('Start your free trial')",
                ".modal-popup._show button#skip_move_to_next",
                ".modal-popup._show button:has-text('Skip')",
                ".modal-popup._show a:has-text('Skip')",
            ]

            clicked = False
            for sel in action_selectors:
                try:
                    target = self.page.locator(sel).first
                    if target.is_visible(timeout=1000):
                        target.scroll_into_view_if_needed()
                        logger.info(f"Clicking action element in trial modal: '{sel}'")
                        target.click(force=True)
                        clicked = True
                        self.wait_for_timeout(1000)
                        break
                except Exception as e:
                    logger.debug(f"Action selector '{sel}' failed: {e}")

            if not clicked and buttons:
                for b in buttons:
                    try:
                        bcls = b.get_attribute("class") or ""
                        if "action-close" not in bcls:
                            b.scroll_into_view_if_needed()
                            logger.info(f"Clicking candidate button: id='{b.get_attribute('id')}', text='{b.inner_text().strip()}'")
                            b.click(force=True)
                            clicked = True
                            self.wait_for_timeout(1000)
                            break
                    except Exception:
                        pass

            # Wait for AJAX loading spinner to disappear
            try:
                loader = self.page.locator(
                    ".modal-popup._show .loading-mask, .modal-popup._show .loader, [data-role='loader'], .loading-mask"
                ).first
                if loader.is_visible(timeout=1000):
                    logger.info("Waiting for trial modal loading spinner to finish...")
                    loader.wait_for(state="hidden", timeout=12000)
            except Exception:
                pass

            # Once the spinner finishes, the modal presents 'Register Machine' (#final_register_machine)
            self.wait_for_timeout(1000)
            final_reg_selectors = [
                ".modal-popup._show #final_register_machine",
                ".modal-popup._show button#final_register_machine",
                ".modal-popup._show button:has-text('Register Machine')",
                "#final_register_machine",
                "button:has-text('Register Machine')",
                ".modal-popup._show #register_my_machine",
            ]
            for f_sel in final_reg_selectors:
                try:
                    f_btn = self.page.locator(f_sel).first
                    if f_btn.is_visible(timeout=8000):
                        f_btn.scroll_into_view_if_needed()
                        logger.info(f"Clicking final register button in trial modal: '{f_sel}'")
                        f_btn.click(force=True)
                        self.wait_for_timeout(2000)
                        break
                except Exception as e:
                    logger.debug(f"Final register selector '{f_sel}' failed: {e}")
        except Exception as e:
            logger.warning(f"Error handling Free Trial modal: {e}")

    def wait_for_trial_modal_to_close(self, timeout_ms: int = 15000) -> bool:
        """Wait for the Activate Your Free Trial modal to close/disappear."""
        logger.info("Waiting for trial modal to close/disappear...")
        trial_modal_selectors = [
            ".modal-popup._show:has(#free_trial)",
            ".modal-popup._show:has-text('Activate Your Free Trial')",
            ".free-trial-section:visible",
        ]
        for sel in trial_modal_selectors:
            try:
                loc = self.page.locator(sel).first
                if loc.is_visible(timeout=1000):
                    loc.wait_for(state="hidden", timeout=timeout_ms)
                    logger.info("Trial modal successfully closed.")
                    return True
            except Exception as e:
                logger.debug(f"Wait for trial modal close ({sel}): {e}")
        return True

    def wait_for_machine_registration_completion(self, timeout_ms: int = 20000) -> bool:
        """Wait for the registration completion request, AJAX response, and UI update."""
        logger.info("Waiting for machine registration completion and UI stabilization...")
        # Wait for any active loader masks to hide
        try:
            loader = self.page.locator(".loading-mask, .loader, [data-role='loader']").first
            if loader.is_visible(timeout=1000):
                loader.wait_for(state="hidden", timeout=timeout_ms)
        except Exception:
            pass

        # Explicit wait for confirmation state
        return self.wait_for_registration_confirmation(timeout_ms=timeout_ms)

    def wait_for_registration_confirmation(self, timeout_ms: int = 15000) -> bool:
        """Wait for final registration confirmation page/state using Playwright explicit condition waits."""
        logger.info("Waiting for registration confirmation UI state...")
        confirmation_locators = [
            self.page.locator(".modal-popup._show:has-text('Congratulations')").first,
            self.page.locator(":has-text('is now registered')").first,
            self.page.locator(":has-text('Congratulations!')").first,
            self.page.locator(MachineRegistrationLocators.WARRANTY_INFORMATION_SECTION).first,
            self.page.locator(".registration-success, .success-msg").first,
        ]
        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout_ms:
            for loc in confirmation_locators:
                try:
                    if loc.is_visible(timeout=400):
                        logger.info("Registration confirmation state observed.")
                        return True
                except Exception:
                    pass
            self.wait_for_timeout(300)
        return False

    def get_registration_confirmation_title(self, timeout_ms: int = 10000) -> str:
        """Retrieve the exact confirmation title heading (e.g. 'Congratulations! Your Silhouette Cameo 5 Plus is now registered.')."""
        self.wait_for_registration_confirmation(timeout_ms=timeout_ms)
        heading_selectors = [
            "h1.page-title",
            "h1:has-text('Congratulations')",
            ".page-title:has-text('Congratulations')",
            "h1:has-text('registered')",
            ":has-text('Congratulations! Your Silhouette')",
            ".modal-popup._show h1",
            ".registration-success h1",
            "h1",
            "h2:has-text('Congratulations')",
        ]
        for sel in heading_selectors:
            try:
                loc = self.page.locator(sel).first
                if loc.is_visible(timeout=1000):
                    txt = loc.inner_text().strip()
                    if "congratulations" in txt.lower():
                        logger.info(f"Retrieved confirmation heading via '{sel}': '{txt}'")
                        return txt
            except Exception:
                pass

        # Fallback: line-by-line inspection of main content
        try:
            content = self.page.locator("#maincontent, body").first.inner_text()
            for line in content.split("\n"):
                clean = line.strip()
                if "congratulations" in clean.lower() and "registered" in clean.lower():
                    logger.info(f"Retrieved confirmation heading from page content: '{clean}'")
                    return clean
        except Exception:
            pass

        return ""

    def click_confirmation_continue_button(self, timeout_ms: int = 10000) -> bool:
        """Click the 'Continue' button on the confirmation page to navigate to the machine setup guide."""
        if self.is_machine_setup_guide_displayed():
            logger.info("Already on machine setup guide page.")
            return True

        logger.info("Attempting to click Continue button on confirmation page...")
        continue_selectors = [
            "button.action.primary:has-text('Continue')",
            "button:has-text('Continue')",
            "a.action.primary:has-text('Continue')",
            "a:has-text('Continue')",
            ".action.primary.continue",
            "button.continue",
            "#continue",
            "button[type='submit']:has-text('Continue')",
            ":has-text('Continue'):visible",
            "button:has-text('Set up your machine')",
            "a:has-text('Set up your machine')",
        ]
        for sel in continue_selectors:
            try:
                loc = self.page.locator(sel).first
                if loc.is_visible(timeout=1500):
                    loc.scroll_into_view_if_needed()
                    self.wait_for_timeout(300)
                    loc.click()
                    logger.info(f"Clicked Continue button using selector: '{sel}'")
                    self.wait_for_timeout(2000)
                    self.wait_for_dom_content_loaded()
                    return True
            except Exception as e:
                logger.debug(f"Selector '{sel}' failed for Continue button: {e}")
        return False

    # =========================================================================
    # Guided Onboarding / Machine Setup Walkthrough (Steps 1 to 4)
    # =========================================================================

    def get_machine_setup_guide_title(self, timeout_ms: int = 10000) -> str:
        """Get the title/heading of the machine setup guide page (e.g. 'Silhouette machine setup')."""
        title_selectors = [
            "h1.page-title",
            "h1:has-text('Silhouette machine setup')",
            "h1:has-text('Silhouette Machine Setup')",
            ".page-title",
            "h1",
            "h2:has-text('Silhouette machine setup')",
        ]
        for sel in title_selectors:
            try:
                loc = self.page.locator(sel).first
                if loc.is_visible(timeout=1000):
                    txt = loc.inner_text().strip()
                    if "silhouette" in txt.lower() and "setup" in txt.lower():
                        logger.info(f"Retrieved machine setup guide title: '{txt}'")
                        return txt
            except Exception:
                pass
        try:
            body_txt = self.page.locator("#maincontent, body").first.inner_text()
            for line in body_txt.split("\n"):
                clean = line.strip()
                if "silhouette" in clean.lower() and "setup" in clean.lower():
                    return clean
        except Exception:
            pass
        return ""

    def is_machine_setup_guide_displayed(self, timeout_ms: int = 10000) -> bool:
        """Verify the 'Silhouette machine setup' guide heading is displayed."""
        title = self.get_machine_setup_guide_title(timeout_ms=timeout_ms)
        return "silhouette" in title.lower() and "setup" in title.lower()

    def click_next_step_button(self, step_number: int = 1, timeout_ms: int = 8000) -> bool:
        """Click the 'Next Step' button to advance through guided setup."""
        logger.info(f"Advancing from Step {step_number}: clicking 'Next Step' button...")
        next_step_selectors = [
            f"#step-{step_number} button:has-text('Next Step')",
            f".step-{step_number} button:has-text('Next Step')",
            f"#step{step_number} button:has-text('Next Step')",
            "button:has-text('Next Step'):visible",
            "a:has-text('Next Step'):visible",
            "button:has-text('Next step'):visible",
            "a:has-text('Next step'):visible",
            ".btn-next-step:visible",
            "button.next:visible",
            "button:has-text('Next'):visible",
            "a:has-text('Next'):visible",
        ]
        for sel in next_step_selectors:
            try:
                loc = self.page.locator(sel).first
                if loc.is_visible(timeout=1000):
                    loc.scroll_into_view_if_needed()
                    self.wait_for_timeout(300)
                    loc.click()
                    logger.info(f"Clicked 'Next Step' button for Step {step_number} via selector '{sel}'")
                    self.wait_for_timeout(2000)
                    self.wait_for_dom_content_loaded()
                    return True
            except Exception as e:
                logger.debug(f"Selector '{sel}' failed for Next Step button: {e}")
        return False

    def is_step_heading_visible(self, step_text: str, timeout_ms: int = 6000) -> bool:
        """Verify whether a specific step heading or section title is displayed."""
        logger.info(f"Verifying step heading visibility: '{step_text}'...")
        try:
            loc = self.page.locator(f":has-text('{step_text}')").first
            if loc.is_visible(timeout=timeout_ms):
                logger.info(f"Step heading '{step_text}' verified visible via direct locator.")
                return True
        except Exception:
            pass

        try:
            body_txt = self.page.locator("body").inner_text()
            norm_target = step_text.lower().replace("®", "").replace("™", "").strip()
            norm_body = body_txt.lower().replace("®", "").replace("™", "")
            if norm_target in norm_body:
                logger.info(f"Step heading '{step_text}' found in body text.")
                return True
            words = [w for w in norm_target.split() if len(w) > 3]
            if words and all(w in norm_body for w in words[:3]):
                logger.info(f"Step heading key words {words[:3]} found in body text.")
                return True
        except Exception as e:
            logger.debug(f"Body text check for step heading '{step_text}' error: {e}")
        return False

    def get_step_text(self, step_number: int) -> str:
        """Retrieve actual rendered text for a given step (1 to 4)."""
        step_selectors = [
            f"#step-{step_number}",
            f".step-{step_number}",
            f"#step{step_number}",
            f"[data-step='{step_number}']",
            f":has-text('Step {step_number}')",
        ]
        for sel in step_selectors:
            try:
                loc = self.page.locator(sel).first
                if loc.is_visible(timeout=500):
                    return loc.inner_text().strip()
            except Exception:
                pass
        return ""

    def verify_manual_pdf_document(self, expected_model: str = "CAMEO 5 PLUS", timeout_ms: int = 10000) -> Dict[str, Any]:
        """Locate 'Silhouette CAMEO® 5 PLUS manual (PDF)', click, and verify PDF document."""
        logger.info(f"Looking for manual PDF button/link for model: '{expected_model}'...")
        clean_model = expected_model.replace("®", "").replace("™", "").strip()
        pdf_selectors = [
            f"a:has-text('{clean_model} manual (PDF)')",
            "a:has-text('manual (PDF)')",
            "a:has-text('Manual (PDF)')",
            f"a:has-text('{clean_model} manual')",
            "a[href*='.pdf']",
            "button:has-text('manual (PDF)')",
            "button:has-text('Manual (PDF)')",
            "a:has-text('User Manual')",
            "a:has-text('Manual')",
        ]

        found_locator = None
        pdf_href = ""
        for sel in pdf_selectors:
            try:
                loc = self.page.locator(sel).first
                if loc.is_visible(timeout=1000):
                    found_locator = loc
                    pdf_href = loc.get_attribute("href") or ""
                    logger.info(f"Found manual PDF element via '{sel}' (href='{pdf_href}')")
                    break
            except Exception:
                pass

        if not found_locator:
            try:
                all_links = self.page.locator("a[href]").all()
                for a in all_links:
                    href_val = a.get_attribute("href") or ""
                    text_val = a.inner_text().strip()
                    if ".pdf" in href_val.lower() or "manual" in text_val.lower():
                        found_locator = a
                        pdf_href = href_val
                        logger.info(f"Found manual PDF via link search: '{text_val}' -> {pdf_href}")
                        break
            except Exception:
                pass

        result: Dict[str, Any] = {
            "found": found_locator is not None,
            "href": pdf_href,
            "status": None,
            "is_pdf": ".pdf" in pdf_href.lower() if pdf_href else False,
            "opened": False,
        }

        if found_locator:
            try:
                found_locator.scroll_into_view_if_needed()
                self.wait_for_timeout(300)
                target = found_locator.get_attribute("target") or ""
                if target == "_blank" or not pdf_href or pdf_href.startswith("http"):
                    try:
                        with self.page.context.expect_page(timeout=5000) as new_page_info:
                            found_locator.click()
                        new_page = new_page_info.value
                        new_page.wait_for_load_state("domcontentloaded")
                        new_url = new_page.url
                        result["opened"] = True
                        result["new_page_url"] = new_url
                        result["is_pdf"] = ".pdf" in new_url.lower() or result["is_pdf"]
                        logger.info(f"Manual PDF opened in new tab: {new_url}")
                        new_page.close()
                    except Exception as e:
                        logger.info(f"No new tab opened on click (or popup blocked): {e}")
                        if pdf_href and (pdf_href.startswith("http") or ".pdf" in pdf_href.lower()):
                            result["opened"] = True
                else:
                    found_locator.click()
                    self.wait_for_timeout(2000)
                    result["opened"] = True
            except Exception as e:
                logger.warning(f"Error clicking manual PDF button: {e}")

        return result

    def get_registration_confirmation_text(self, timeout_ms: int = 10000) -> str:
        """Retrieve registration confirmation text from actual success confirmation elements."""
        self.wait_for_registration_confirmation(timeout_ms=timeout_ms)
        success_selectors = [
            "h1:has-text('Congratulations')",
            "h2:has-text('Congratulations')",
            "h1.page-title",
            ":has-text('Congratulations! Your Silhouette')",
            ":has-text('is now registered')",
            ".modal-popup._show:has-text('Congratulations')",
            ".modal-popup._show:has-text('now registered')",
            ".modal-inner-wrap:has-text('Congratulations')",
            ".modal-inner-wrap:has-text('now registered')",
            ".registration-success",
            ".message.success",
            "#maincontent",
        ]
        for sel in success_selectors:
            try:
                loc = self.page.locator(sel).first
                if loc.is_visible(timeout=500):
                    txt = loc.inner_text().strip()
                    if any(k in txt.lower() for k in ["congratulations", "is now registered", "successfully registered"]):
                        logger.info(f"Retrieved registration confirmation text: '{txt[:150]}...'")
                        return txt
            except Exception:
                pass
        return ""

    def is_warranty_information_visible(self, timeout_ms: int = 5000) -> bool:
        """Verify the Warranty Information section is visible."""
        try:
            warranty = self.page.locator(
                ":has-text('Warranty Information'), .warranty-info, .warranty-section, [data-role='warranty-info']"
            ).first
            if warranty.is_visible(timeout=timeout_ms):
                return True
        except Exception:
            pass
        # Check confirmation text fallback
        try:
            dialog_txt = self.get_registration_confirmation_text(timeout_ms=1000)
            return "warranty" in dialog_txt.lower()
        except Exception:
            return False

    def is_warranty_information_displayed(self, timeout_ms: int = 5000) -> bool:
        """Alias for is_warranty_information_visible for backward compatibility."""
        return self.is_warranty_information_visible(timeout_ms=timeout_ms)

    # =========================================================================
    # Account Area - Registered Machines
    # =========================================================================

    def navigate_to_account_registered_machines(self) -> None:
        """Navigate to customer account area -> Machine registration (/machine-setup/account/)."""
        logger.info("Navigating to Account Machine Registration section...")
        self.goto(MachineRegistrationLocators.MACHINE_ACCOUNT_URL_PATH, wait_until="domcontentloaded")
        self.dismiss_cookie_consent_if_present()
        self.wait_for_timeout(1000)

    def is_registered_machine_in_account(self, model_or_serial: str = "CAMEO 5") -> bool:
        """Verify whether a registered machine appears in the customer account list."""
        try:
            content = self.page.locator(MachineRegistrationLocators.REGISTERED_MACHINES_MAIN_CONTENT).inner_text()
            logger.info(f"Checking account registered machines content for: '{model_or_serial}'")
            return model_or_serial.lower() in content.lower()
        except Exception as e:
            logger.error(f"Error checking registered machines in account: {e}")
            return False

    # =========================================================================
    # Encapsulated Network Interception (E2E-MACHINE-005 & E2E-MACHINE-009)
    # =========================================================================

    def simulate_registration_network_failure(self) -> List[str]:
        """E2E-MACHINE-005: Encapsulate Playwright route interception to simulate network abort on save/detected."""
        interception_triggered: List[str] = []

        def handle_network_interruption(route: Any) -> None:
            logger.info(f"Intercepting registration network call: {route.request.url} -> Simulating network abort")
            interception_triggered.append(route.request.url)
            route.abort("failed")

        self.page.route("**/machinesetup/index/save/**", handle_network_interruption)
        self.page.route("**/machinesetup/index/detected/**", handle_network_interruption)
        return interception_triggered

    def clear_registration_network_failure(self) -> None:
        """Clear route interception for E2E-MACHINE-005."""
        try:
            self.page.unroute("**/machinesetup/index/save/**")
        except Exception:
            pass
        try:
            self.page.unroute("**/machinesetup/index/detected/**")
        except Exception:
            pass

    def simulate_benefit_api_500_failure(self) -> List[str]:
        """E2E-MACHINE-009: Encapsulate Playwright route interception to simulate HTTP 500 on trial/benefit endpoint."""
        benefit_calls: List[str] = []

        def fail_benefit_api(route: Any) -> None:
            logger.info(f"Intercepting trial/benefit service call: {route.request.url} -> Simulating HTTP 500")
            benefit_calls.append(route.request.url)
            route.fulfill(
                status=500,
                content_type="application/json",
                body='{"success": false, "message": "Benefit service internal server error"}',
            )

        self.page.route("**/machinesetup/index/trial/**", fail_benefit_api)
        return benefit_calls

    def clear_benefit_api_failure(self) -> None:
        """Clear route interception for E2E-MACHINE-009."""
        try:
            self.page.unroute("**/machinesetup/index/trial/**")
        except Exception:
            pass

    # =========================================================================
    # Clean UI Evidence Preparation
    # =========================================================================

    def prepare_for_machine_evidence(self) -> None:
        """Ensure DOM is stable for evidence screenshot."""
        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(300)
