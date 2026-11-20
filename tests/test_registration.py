import os
import pytest
from pages.registration_page import RegistrationPage
from locators.registration_locators import RegistrationLocators
from utils.common_helper import CommonHelper
from utils.logger import logger

from utils.mcp_email_helper import McpEmailHelper


@pytest.mark.e2e
@pytest.mark.login
class TestRegistration:
    """Customer Registration E2E test suite covering valid registration,

    duplicate email prevention, invalid email, mandatory field validations,
    mobile format validation, password policy validation, invalid password validation,
    and required terms enforcement.
    """

    DEFAULT_FIRST_NAME = "QA"
    DEFAULT_LAST_NAME = "Automation"
    DEFAULT_DOB = "01/15/1995"
    DEFAULT_PASSWORD = "Password@123"
    DEFAULT_MOBILE = "1234567890"
    EXISTING_EMAIL = "anand.mopidi@magnetoitsolutions.com"

    @classmethod
    def generate_dynamic_email(cls) -> str:
        """Generate a unique test email following the user-preferred format."""
        base_email = os.getenv("TEST_REGISTRATION_EMAIL", "anand.mopidi@magnetoitsolutions.com")
        ts = CommonHelper.get_timestamp("%Y%m%d%H%M%S")
        if "@" in base_email:
            user, domain = base_email.split("@", 1)
            return f"{user}+QA{ts}@{domain}"
        return f"anand.mopidi+QA{ts}@magnetoitsolutions.com"

    # =========================================================================
    # E2E-REG-001: Valid Registration
    # =========================================================================

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_e2e_reg_001_create_account_valid_details(
        self, registration_page: RegistrationPage, request: pytest.FixtureRequest
    ) -> None:
        """E2E-REG-001: Create account with valid details and verify registration.

        Steps:
        1. Open Silhouette America site and navigate to registration form.
        2. Generate unique email address and fill mandatory user details.
        3. Submit registration form and wait for OTP verification view (#login-otp-combine).
        4. Retrieve live 6-digit OTP code dynamically via Gmail MCP or interactive terminal prompt.
        5. Enter OTP code, submit verification, and verify user reaches customer account area.
        6. Capture evidence screenshot and video for test verification.
        """
        logger.info("Executing E2E-REG-001: Create account with valid details.")
        registration_page.open_registration_page()

        unique_email = self.generate_dynamic_email()
        logger.info(f"Using dynamically generated unique email: '{unique_email}'")

        registration_page.fill_registration_form(
            first_name=self.DEFAULT_FIRST_NAME,
            last_name=self.DEFAULT_LAST_NAME,
            dob=self.DEFAULT_DOB,
            gender="Female",
            email=unique_email,
            mobile=self.DEFAULT_MOBILE,
            password=self.DEFAULT_PASSWORD,
            accept_terms=True,
        )

        registration_page.submit_registration()

        # Check if OTP verification step is displayed
        if registration_page.is_otp_input_visible():
            logger.info("OTP verification view is displayed (#login-otp-combine).")

            # Retrieve OTP dynamically via configured Gmail MCP
            mcp_helper = McpEmailHelper()
            otp_retrieved, otp_code, otp_status = mcp_helper.retrieve_registration_otp(
                recipient_email=unique_email,
                timeout_seconds=120,
                poll_interval=4,
            )

            logger.info(f"Gmail MCP OTP retrieval status: {otp_status}")
            assert otp_retrieved and otp_code, (
                f"Failed to retrieve dynamic OTP for '{unique_email}' via configured Gmail MCP. "
                f"Details: {otp_status}"
            )

            logger.info(f"Successfully retrieved OTP: '{otp_code}'. Submitting into registration OTP form...")
            registration_page.enter_otp(otp_code)

            # Wait for modal overlay to complete and close
            try:
                registration_page.page.locator(RegistrationLocators.REGISTRATION_OVERLAY).wait_for(state="hidden", timeout=10000)
                logger.info("Registration/Login overlay closed after OTP verification.")
            except Exception:
                pass

            # Check if user reached account area, or navigate to customer account area
            if not registration_page.is_account_area_displayed(timeout_ms=5000):
                logger.info("Post-OTP login completed on current page. Navigating to customer account area (/customer/account/)...")
                registration_page.navigate_to_account_area()

            # Verify authentication and arrival at customer account area
            reached_account = registration_page.is_account_area_displayed(timeout_ms=15000)
            current_url = registration_page.page.url
            logger.info(f"Account area navigation check: reached={reached_account}, current_url='{current_url}'")

            assert reached_account, (
                f"Expected user to reach customer account area (/customer/account/) after submitting OTP, "
                f"but current URL is: '{current_url}'"
            )
            assert RegistrationLocators.ACCOUNT_URL_PATH in current_url, (
                f"Expected '{RegistrationLocators.ACCOUNT_URL_PATH}' in URL, got: '{current_url}'"
            )

            registration_page.prepare_for_registration_evidence()
            registration_page.capture_evidence_screenshot(request.node.name, status="passed")
            logger.info("E2E-REG-001 completed successfully with dynamic OTP retrieval and account verification.")
        else:
            # If application creates account directly or redirects to account area
            reached_account = registration_page.is_account_area_displayed(timeout_ms=15000)
            assert reached_account, (
                "Expected user to reach account area or OTP verification screen after registration submission."
            )
            registration_page.prepare_for_registration_evidence()
            registration_page.capture_evidence_screenshot(request.node.name, status="passed")
            logger.info("E2E-REG-001 completed successfully (direct account creation).")

    # =========================================================================
    # E2E-REG-002: Existing Email Registration
    # =========================================================================

    @pytest.mark.functional
    def test_e2e_reg_002_existing_email_registration(
        self, registration_page: RegistrationPage, request: pytest.FixtureRequest
    ) -> None:
        """E2E-REG-002: Verify duplicate registration is prevented for existing email."""
        logger.info("Executing E2E-REG-002: Existing email registration.")
        registration_page.open_registration_page()

        logger.info(f"Filling registration form with existing email: '{self.EXISTING_EMAIL}'")
        registration_page.fill_registration_form(
            first_name=self.DEFAULT_FIRST_NAME,
            last_name=self.DEFAULT_LAST_NAME,
            dob=self.DEFAULT_DOB,
            gender="Male",
            email=self.EXISTING_EMAIL,
            mobile=self.DEFAULT_MOBILE,
            password=self.DEFAULT_PASSWORD,
            accept_terms=True,
        )

        registration_page.submit_registration()

        server_msg = registration_page.get_server_response_message(timeout_ms=7000)
        email_err = registration_page.get_field_error(RegistrationLocators.EMAIL_ERROR)
        actual_err = server_msg or email_err
        logger.info(f"Captured actual server response: '{server_msg}', email error: '{email_err}'")

        assert len(actual_err) > 0, "Expected duplicate email validation/error message, but none was displayed."
        assert any(
            kw in actual_err.lower()
            for kw in ["already", "exist", "account", "email", "registered", "taken", "duplicate", "error"]
        ), f"Unexpected duplicate email error message: '{actual_err}'"

        registration_page.prepare_for_registration_evidence()
        registration_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-REG-002 completed successfully.")

    # =========================================================================
    # E2E-REG-003: Invalid Email
    # =========================================================================

    @pytest.mark.functional
    def test_e2e_reg_003_invalid_email(
        self, registration_page: RegistrationPage, request: pytest.FixtureRequest
    ) -> None:
        """E2E-REG-003: Verify email format validation when invalid email is entered."""
        logger.info("Executing E2E-REG-003: Invalid email validation.")
        registration_page.open_registration_page()

        invalid_email = "abc@"
        logger.info(f"Filling registration form with invalid email: '{invalid_email}'")
        registration_page.fill_registration_form(
            first_name=self.DEFAULT_FIRST_NAME,
            last_name=self.DEFAULT_LAST_NAME,
            dob=self.DEFAULT_DOB,
            email=invalid_email,
            mobile=self.DEFAULT_MOBILE,
            password=self.DEFAULT_PASSWORD,
            accept_terms=True,
        )

        registration_page.submit_registration()

        email_err = registration_page.get_field_error(RegistrationLocators.EMAIL_ERROR)
        is_invalid = registration_page.is_input_invalid(RegistrationLocators.EMAIL_INPUT)
        modal_open = registration_page.is_registration_modal_open()
        logger.info(f"Captured actual email validation error: '{email_err}', is_invalid={is_invalid}, modal_open={modal_open}")

        assert len(email_err) > 0 or is_invalid or modal_open, "Email validation error was not displayed for invalid email."
        if email_err:
            assert any(kw in email_err.lower() for kw in ["valid email", "email", "valid", "format", "enter a valid"]), (
                f"Expected email format validation error, got: '{email_err}'"
            )

        registration_page.prepare_for_registration_evidence()
        registration_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-REG-003 completed successfully.")

    # =========================================================================
    # E2E-REG-004: Missing Mandatory Fields
    # =========================================================================

    @pytest.mark.functional
    def test_e2e_reg_004_missing_mandatory_fields(
        self, registration_page: RegistrationPage, request: pytest.FixtureRequest
    ) -> None:
        """E2E-REG-004: Verify required field validations when submitting empty form."""
        logger.info("Executing E2E-REG-004: Missing mandatory fields.")
        registration_page.open_registration_page()

        # Submit blank form without filling any required fields
        registration_page.submit_registration()

        errors = registration_page.get_validation_errors()
        logger.info(f"Captured {len(errors)} required field validation errors.")

        assert len(errors) >= 5, f"Expected at least 5 required field errors, found {len(errors)}: {errors}"

        # Verify specific required field errors
        fname_err = errors.get("firstname-error") or registration_page.get_field_error(RegistrationLocators.FIRST_NAME_ERROR)
        lname_err = errors.get("lastname-error") or registration_page.get_field_error(RegistrationLocators.LAST_NAME_ERROR)
        dob_err = errors.get("register-dob-error") or registration_page.get_field_error(RegistrationLocators.DOB_ERROR)
        email_err = errors.get("email-error") or registration_page.get_field_error(RegistrationLocators.EMAIL_ERROR)
        pwd_err = errors.get("reg-password-error") or registration_page.get_field_error(RegistrationLocators.PASSWORD_ERROR)
        terms_err = errors.get("terms_agreed-error") or registration_page.get_field_error(RegistrationLocators.TERMS_ERROR)

        for name, err in [
            ("First Name", fname_err),
            ("Last Name", lname_err),
            ("DOB", dob_err),
            ("Email", email_err),
            ("Password", pwd_err),
            ("Terms", terms_err),
        ]:
            assert "required" in err.lower(), f"Expected required validation on {name}, got: '{err}'"

        registration_page.prepare_for_registration_evidence()
        registration_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-REG-004 completed successfully.")

    # =========================================================================
    # E2E-REG-005: Invalid Mobile
    # =========================================================================

    @pytest.mark.functional
    def test_e2e_reg_005_invalid_mobile(
        self, registration_page: RegistrationPage, request: pytest.FixtureRequest
    ) -> None:
        """E2E-REG-005: Verify mobile format validation when entering invalid phone number."""
        logger.info("Executing E2E-REG-005: Invalid mobile validation.")
        registration_page.open_registration_page()

        invalid_mobile = "123"  # Fewer than 7 digits
        logger.info(f"Filling registration form with invalid mobile: '{invalid_mobile}'")
        registration_page.fill_registration_form(
            first_name=self.DEFAULT_FIRST_NAME,
            last_name=self.DEFAULT_LAST_NAME,
            dob=self.DEFAULT_DOB,
            email=self.generate_dynamic_email(),
            mobile=invalid_mobile,
            password=self.DEFAULT_PASSWORD,
            accept_terms=True,
        )

        registration_page.submit_registration()

        mobile_err = registration_page.get_field_error(RegistrationLocators.MOBILE_ERROR)
        is_invalid = registration_page.is_input_invalid(RegistrationLocators.MOBILE_INPUT)
        modal_open = registration_page.is_registration_modal_open()
        logger.info(f"Captured actual mobile validation error: '{mobile_err}', is_invalid={is_invalid}, modal_open={modal_open}")

        assert len(mobile_err) > 0 or is_invalid or modal_open, "Mobile validation error was not displayed for invalid mobile."
        if mobile_err:
            assert any(kw in mobile_err.lower() for kw in ["valid mobile", "digits", "mobile", "number", "valid", "7", "enter a valid"]), (
                f"Expected mobile format message, got: '{mobile_err}'"
            )

        registration_page.prepare_for_registration_evidence()
        registration_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-REG-005 completed successfully.")

    # =========================================================================
    # E2E-REG-006: Weak Password
    # =========================================================================

    @pytest.mark.functional
    def test_e2e_reg_006_weak_password(
        self, registration_page: RegistrationPage, request: pytest.FixtureRequest
    ) -> None:
        """E2E-REG-006: Verify password policy validation when entering a weak password."""
        logger.info("Executing E2E-REG-006: Weak password policy validation.")
        registration_page.open_registration_page()

        weak_password = "123"  # Less than minimum 8 characters
        logger.info(f"Filling registration form with weak password: '{weak_password}'")
        registration_page.fill_registration_form(
            first_name=self.DEFAULT_FIRST_NAME,
            last_name=self.DEFAULT_LAST_NAME,
            dob=self.DEFAULT_DOB,
            email=self.generate_dynamic_email(),
            mobile=self.DEFAULT_MOBILE,
            password=weak_password,
            accept_terms=True,
        )

        registration_page.submit_registration()

        pwd_err = registration_page.get_field_error(RegistrationLocators.PASSWORD_ERROR)
        logger.info(f"Captured actual password error: '{pwd_err}'")

        assert len(pwd_err) > 0, "Password policy validation was not displayed."
        assert (
            "8" in pwd_err
            or "symbol" in pwd_err.lower()
            or "character" in pwd_err.lower()
            or "minimum length" in pwd_err.lower()
            or "password" in pwd_err.lower()
        ), f"Expected minimum length policy error, got: '{pwd_err}'"

        registration_page.prepare_for_registration_evidence()
        registration_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-REG-006 completed successfully.")

    # =========================================================================
    # E2E-REG-007: Invalid Password Validation
    # =========================================================================

    @pytest.mark.functional
    def test_e2e_reg_007_invalid_password_validation(
        self, registration_page: RegistrationPage, request: pytest.FixtureRequest
    ) -> None:
        """E2E-REG-007: Verify password validation error when entering an invalid password."""
        logger.info("Executing E2E-REG-007: Invalid Password Validation.")
        registration_page.open_registration_page()

        invalid_password = "123"
        logger.info(f"Filling registration form with invalid password: '{invalid_password}'")
        registration_page.fill_registration_form(
            first_name=self.DEFAULT_FIRST_NAME,
            last_name=self.DEFAULT_LAST_NAME,
            dob=self.DEFAULT_DOB,
            email=self.generate_dynamic_email(),
            mobile=self.DEFAULT_MOBILE,
            password=invalid_password,
            accept_terms=True,
        )

        registration_page.submit_registration()

        pwd_err = registration_page.get_field_error(RegistrationLocators.PASSWORD_ERROR)
        logger.info(f"Captured actual password error: '{pwd_err}'")

        assert len(pwd_err) > 0, "Password validation error was not displayed."
        assert (
            "8" in pwd_err
            or "symbol" in pwd_err.lower()
            or "character" in pwd_err.lower()
            or "minimum length" in pwd_err.lower()
            or "password" in pwd_err.lower()
        ), f"Expected password length validation error, got: '{pwd_err}'"

        registration_page.prepare_for_registration_evidence()
        registration_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-REG-007 completed successfully.")

    # =========================================================================
    # E2E-REG-008: Register Without Required Terms
    # =========================================================================

    @pytest.mark.functional
    def test_e2e_reg_008_register_without_required_terms(
        self, registration_page: RegistrationPage, request: pytest.FixtureRequest
    ) -> None:
        """E2E-REG-008: Verify registration is prevented when required terms are unchecked."""
        logger.info("Executing E2E-REG-008: Register without required terms.")
        registration_page.open_registration_page()

        logger.info("Filling valid registration data with Terms unchecked.")
        registration_page.fill_registration_form(
            first_name=self.DEFAULT_FIRST_NAME,
            last_name=self.DEFAULT_LAST_NAME,
            dob=self.DEFAULT_DOB,
            email=self.generate_dynamic_email(),
            mobile=self.DEFAULT_MOBILE,
            password=self.DEFAULT_PASSWORD,
            accept_terms=False,
        )

        registration_page.submit_registration()

        terms_err = registration_page.get_field_error(RegistrationLocators.TERMS_ERROR)
        server_msg = registration_page.get_server_response_message(timeout_ms=2000)
        modal_open = registration_page.is_registration_modal_open()
        logger.info(f"Captured terms validation error: '{terms_err}', server message: '{server_msg}', modal_open={modal_open}")

        # Either client required validation on the checkbox, server message, or modal stays blocked
        assert len(terms_err) > 0 or len(server_msg) > 0 or modal_open, (
            "Terms validation message was not displayed and modal did not prevent registration when terms were unchecked."
        )
        if terms_err or server_msg:
            assert (
                "required" in terms_err.lower()
                or "agree" in server_msg.lower()
                or "terms" in server_msg.lower()
                or "field" in terms_err.lower()
            ), f"Unexpected terms validation state: field_err='{terms_err}', server_msg='{server_msg}'"

        registration_page.prepare_for_registration_evidence()
        registration_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-REG-008 completed successfully.")
