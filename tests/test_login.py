import pytest
from pages.home_page import HomePage
from pages.login_page import LoginPage
from utils.common_helper import CommonHelper
from utils.data_helper import DataHelper
from utils.logger import logger


@pytest.mark.e2e
@pytest.mark.login
class TestLogin:
    """Login E2E test suite covering valid authentication, invalid password rejection,

    unregistered email validation, blank field checks, Remember Me session persistence,
    and complete logout with protected route access gating.
    """

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_e2e_login_001_valid_credentials(
        self,
        login_page: LoginPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-LOGIN-001: Login with valid credentials and verify authenticated dashboard & identity."""
        logger.info("Executing E2E-LOGIN-001: Login with Valid Credentials.")
        user_data = DataHelper.load_user_data().get("valid_user", {})
        email = user_data.get("email")
        password = user_data.get("password")
        expected_name = user_data.get("expected_name", "Anand Mopidi")

        assert email and password, "Valid user credentials missing from test data."

        # Step 1: Open Login modal via header account menu
        login_page.open_login_modal()
        assert login_page.is_login_modal_open(), "Login modal failed to open."

        # Step 2: Fill valid credentials and submit
        login_page.fill_credentials(email=email, password=password)
        login_page.submit_login()

        # Step 3: Dynamically verify successful authentication
        assert login_page.is_customer_authenticated(timeout_ms=10000), (
            "Customer authentication failed: session was not established after valid login submission."
        )

        # Step 4: Verify expected account identity where available
        cust_info = login_page.get_authenticated_customer_info()
        logger.info(f"Authenticated customer profile info: {cust_info}")
        if cust_info.get("fullname"):
            assert expected_name.lower() in cust_info.get("fullname", "").lower(), (
                f"Expected name '{expected_name}' not found in customer info: {cust_info}"
            )
        if cust_info.get("email"):
            assert email.lower() == cust_info.get("email", "").lower(), (
                f"Expected email '{email}' does not match customer profile: {cust_info}"
            )

        # Step 5: Verify customer account area access
        dest_url = login_page.navigate_to_protected_account()
        assert "customer/account" in dest_url.lower(), (
            f"Expected destination to be customer account, but got: '{dest_url}'"
        )

        # Intentional validated evidence capture
        login_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-LOGIN-001 completed successfully.")

    @pytest.mark.functional
    def test_e2e_login_002_invalid_password(
        self,
        login_page: LoginPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-LOGIN-002: Login with registered email and incorrect password; verify rejection message."""
        logger.info("Executing E2E-LOGIN-002: Invalid Password Verification.")
        user_data = DataHelper.load_user_data().get("invalid_password_user", {})
        email = user_data.get("email")
        wrong_password = user_data.get("password", "IncorrectPassword@999")

        assert email, "Registered email missing from invalid_password_user test data."

        # Step 1: Open Login modal
        login_page.open_login_modal()
        assert login_page.is_login_modal_open(), "Login modal failed to open."

        # Step 2: Fill credentials with wrong password and submit
        login_page.fill_credentials(email=email, password=wrong_password)
        login_page.submit_login()

        # Step 3: Dynamically verify actual error message
        error_msg = login_page.get_response_error_message(timeout_ms=8000)
        logger.info(f"Captured invalid password response message: '{error_msg}'")
        assert error_msg, "Expected error message banner was not displayed for invalid password."
        assert (
            "invalid login or password" in error_msg.lower()
            or "incorrect" in error_msg.lower()
            or "invalid" in error_msg.lower()
        ), f"Unexpected error message text received: '{error_msg}'"

        # Step 4: Confirm user remains unauthenticated
        assert not login_page.is_customer_authenticated(timeout_ms=2000), (
            "User was unexpectedly authenticated despite supplying an incorrect password."
        )

        # Intentional validated evidence capture
        login_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-LOGIN-002 completed successfully.")

    @pytest.mark.functional
    def test_e2e_login_003_unregistered_email(
        self,
        login_page: LoginPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-LOGIN-003: Login with unregistered email; verify rejection and application message."""
        logger.info("Executing E2E-LOGIN-003: Unregistered Email Verification.")
        unreg_config = DataHelper.load_user_data().get("unregistered_user", {})
        domain = unreg_config.get("domain", "magnetoitsolutions.com")
        unregistered_email = CommonHelper.generate_unique_email(prefix="unregistered_auto", domain=domain)
        test_password = unreg_config.get("password", "Password@123")

        logger.info(f"Targeting unregistered dynamic email: '{unregistered_email}'")

        # Step 1: Open Login modal
        login_page.open_login_modal()
        assert login_page.is_login_modal_open(), "Login modal failed to open."

        # Step 2: Fill unregistered email and password and submit
        login_page.fill_credentials(email=unregistered_email, password=test_password)
        login_page.submit_login()

        # Step 3: Dynamically verify rejection message
        error_msg = login_page.get_response_error_message(timeout_ms=8000)
        logger.info(f"Captured unregistered email response message: '{error_msg}'")
        assert error_msg, "Expected error message was not displayed for unregistered email."
        assert (
            "not registered" in error_msg.lower()
            or "invalid" in error_msg.lower()
            or "create an account" in error_msg.lower()
        ), f"Unexpected response message received: '{error_msg}'"

        # Step 4: Confirm no authenticated session created
        assert not login_page.is_customer_authenticated(timeout_ms=2000), (
            "Authenticated session unexpectedly created for unregistered email."
        )

        # Intentional validated evidence capture
        login_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-LOGIN-003 completed successfully.")

    @pytest.mark.functional
    def test_e2e_login_004_blank_fields(
        self,
        login_page: LoginPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-LOGIN-004: Leave email and password blank; verify client-side mandatory-field validation."""
        logger.info("Executing E2E-LOGIN-004: Blank Fields Mandatory Validation.")

        # Step 1: Open Login modal
        login_page.open_login_modal()
        assert login_page.is_login_modal_open(), "Login modal failed to open."

        # Step 2: Clear any inputs and submit empty form
        login_page.fill_credentials(email="", password="")
        login_page.submit_login()

        # Step 3: Verify mandatory-field validation messages
        u_err = login_page.get_username_validation_error()
        p_err = login_page.get_password_validation_error()
        all_errs = login_page.get_all_field_validation_errors()

        logger.info(f"Captured field errors: username='{u_err}', password='{p_err}', all={all_errs}")

        assert "required" in u_err.lower() or any("required" in e.lower() for e in all_errs), (
            f"Expected mandatory field validation for username/email, found: '{u_err}'"
        )
        assert "required" in p_err.lower() or any("required" in e.lower() for e in all_errs), (
            f"Expected mandatory field validation for password, found: '{p_err}'"
        )

        # Step 4: Confirm user is not authenticated
        assert not login_page.is_customer_authenticated(timeout_ms=2000), (
            "User was unexpectedly authenticated from a blank form submission."
        )

        # Intentional validated evidence capture
        login_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-LOGIN-004 completed successfully.")

    @pytest.mark.functional
    def test_e2e_login_005_remember_me(
        self,
        login_page: LoginPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-LOGIN-005: Verify Remember Me checkbox state, login with Remember Me, and verify session persistence."""
        logger.info("Executing E2E-LOGIN-005: Remember Me Verification.")
        user_data = DataHelper.load_user_data().get("valid_user", {})
        email = user_data.get("email")
        password = user_data.get("password")

        assert email and password, "Valid user credentials missing from test data."

        # Step 1: Open Login modal
        login_page.open_login_modal()
        assert login_page.is_login_modal_open(), "Login modal failed to open."

        # Step 2: Verify Remember Me option exists and check it
        assert login_page.is_remember_me_available(), "Remember Me checkbox is not available on login form."
        actual_checked = login_page.toggle_remember_me(check=True)
        assert actual_checked, "Remember Me checkbox could not be checked."
        assert login_page.is_remember_me_checked(), "Remember Me state reported unchecked after setting."

        # Step 3: Submit login with Remember Me active
        login_page.fill_credentials(email=email, password=password)
        login_page.submit_login()

        # Step 4: Verify authentication established
        assert login_page.is_customer_authenticated(timeout_ms=10000), (
            "Authentication failed when submitting with Remember Me checked."
        )

        # Step 5: Verify session persistence according to configured session policy
        cookies = login_page.get_session_cookies()
        cookie_names = [c.get("name", "") for c in cookies]
        logger.info(f"Captured active cookies after Remember Me login: {cookie_names}")

        has_session_cookie = any(
            "sess" in name.lower() or "mage" in name.lower() or "persistent" in name.lower()
            for name in cookie_names
        )
        assert has_session_cookie, (
            f"Expected session/persistent cookie not found among context cookies: {cookie_names}"
        )

        # Intentional validated evidence capture
        login_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-LOGIN-005 completed successfully.")

    @pytest.mark.functional
    def test_e2e_login_006_logout(
        self,
        login_page: LoginPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-LOGIN-006: Authenticate, execute logout, verify unauthenticated state & protected route gating."""
        logger.info("Executing E2E-LOGIN-006: Logout and Route Protection Verification.")
        user_data = DataHelper.load_user_data().get("valid_user", {})
        email = user_data.get("email")
        password = user_data.get("password")

        # Step 1: Authenticate customer
        login_page.open_login_modal()
        login_page.fill_credentials(email=email, password=password)
        login_page.submit_login()
        assert login_page.is_customer_authenticated(timeout_ms=10000), (
            "Initial authentication failed prior to logout test."
        )
        logger.info("Customer successfully authenticated before logout.")

        # Step 2: Execute Logout
        login_page.logout_customer()

        # Step 3: Verify the user is unauthenticated
        assert not login_page.is_customer_authenticated(timeout_ms=3000), (
            "Customer remains authenticated after logout was initiated."
        )
        logger.info("Customer session verified unauthenticated post-logout.")

        # Step 4: Attempt to access protected customer account URL
        protected_dest_url = login_page.navigate_to_protected_account()
        logger.info(f"Navigating to protected URL redirected to: '{protected_dest_url}'")

        # Verify access is redirected or requires authentication
        assert (
            "login" in protected_dest_url.lower()
            or not login_page.is_customer_authenticated(timeout_ms=2000)
        ), f"Protected account route was unexpectedly accessible without authentication: '{protected_dest_url}'"

        # Intentional validated evidence capture
        login_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-LOGIN-006 completed successfully.")

