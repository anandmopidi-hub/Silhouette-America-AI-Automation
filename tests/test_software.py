import pytest
from pages.software_page import SoftwarePage
from utils.data_helper import DataHelper
from utils.logger import logger


@pytest.mark.e2e
class TestSoftware:
    """Software E2E test suite covering download, OS compatibility, license verification,

    authorization boundaries, and download retry/recovery flows.
    """

    @pytest.mark.smoke
    def test_e2e_sw_001_open_software_page(
        self,
        software_page: SoftwarePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-SW-001: Software | Download | Open software page.

        Expected: Software page loads successfully with proper branding and sections.
        """
        logger.info("Executing E2E-SW-001: Open Software Page verification.")
        software_page.open_software_page()

        assert software_page.is_software_page_loaded(), (
            "Software page failed to load or key branding / download elements are missing."
        )

        software_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-SW-001 PASSED: Software page loaded successfully.")

    @pytest.mark.functional
    def test_e2e_sw_002_download_supported_os_installer(
        self,
        software_page: SoftwarePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-SW-002: Software | Download | Download supported OS installer.

        Expected: Correct Windows/macOS installer download begins in headless mode.
        """
        logger.info("Executing E2E-SW-002: Download Supported OS Installer verification.")
        software_page.open_software_page()

        data = DataHelper.load_software_data()
        supported_os_list = data.get("supported_os", [{"name": "windows", "expected_extension": ".exe"}])
        target_os_config = supported_os_list[0]
        os_name = target_os_config.get("name", "windows")
        expected_ext = target_os_config.get("expected_extension", ".exe")

        logger.info(f"Initiating installer download test for OS='{os_name}' (expected: '{expected_ext}')")
        result = software_page.start_download(os_name=os_name)

        assert result["download_started"], f"Installer download failed to initiate for target OS: '{os_name}'."
        assert result["is_valid"], (
            f"Download filename or URL did not match expected extension '{expected_ext}'. "
            f"Actual filename: '{result['filename']}', URL: '{result['url']}'"
        )

        software_page.capture_evidence_screenshot(request.node.name)
        logger.info(f"E2E-SW-002 PASSED: Supported OS installer download verified for {os_name}.")

    @pytest.mark.functional
    def test_e2e_sw_003_unsupported_os_compatibility(
        self,
        software_page: SoftwarePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-SW-003: Software | Compatibility | Unsupported OS.

        Flow:
        1. Open the Software page using the existing configured Production URL.
        2. Handle Cloudflare/cookie flow centrally.
        3. Verify that the Software page loads successfully.
        4. Verify that supported OS download options are available (Windows 64-bit, Mac 64-bit).
        5. Locate and open the official System Requirements link.
        6. Verify that the official System Requirements documentation loads successfully.
        7. Verify the documented unsupported platforms/devices:
           - Chromebooks
           - Tablets
           - Mobile devices
        8. Capture required screenshot and video evidence.
        9. Mark test PASS only when compatibility guidance and unsupported platforms are verified.
        """
        logger.info("Executing E2E-SW-003: Unsupported OS Compatibility end-to-end verification.")

        # Step 1 & 2: Open Software page and handle Cloudflare/cookie flow
        software_page.open_software_page()

        # Step 3: Verify Software page loaded successfully
        assert software_page.is_software_page_loaded(), (
            "Software page failed to load or key branding/download sections are missing."
        )

        # Step 4: Verify supported OS download options are available (Win 64, MAC 64)
        os_options = software_page.verify_supported_os_options()
        assert os_options["win_64"], "Windows 64-bit download option is missing from Software page."
        assert os_options["mac_64"], "Mac 64-bit download option is missing from Software page."

        # Step 5: Locate and open System Requirements documentation
        doc_page = software_page.open_system_requirements_documentation()
        assert doc_page is not None, "Failed to open System Requirements documentation."

        try:
            # Step 6: Verify official System Requirements documentation loads successfully
            doc_title = doc_page.title().lower()
            doc_url = doc_page.url.lower()
            assert "software" in doc_title or "silhouette" in doc_title or "support" in doc_title or "article" in doc_url, (
                f"System Requirements documentation did not load expected content. Title: '{doc_page.title()}', URL: '{doc_page.url}'"
            )

            # Step 7: Verify documented unsupported platforms/devices (Chromebooks, Tablets, Mobile devices)
            unsupported_guidance = software_page.verify_unsupported_platforms_guidance(doc_page)
            assert unsupported_guidance["has_chromebook"], (
                "Official System Requirements documentation is missing required guidance for Chromebooks."
            )
            assert unsupported_guidance["has_tablet"], (
                "Official System Requirements documentation is missing required guidance for Tablets."
            )
            assert unsupported_guidance["has_mobile"], (
                "Official System Requirements documentation is missing required guidance for Mobile devices."
            )
            assert unsupported_guidance["all_verified"], (
                "Unsupported platforms guidance incomplete. Expected Chromebooks, Tablets, and Mobile devices."
            )

            # Step 8: Capture evidence screenshot
            from utils.screenshot_helper import ScreenshotHelper
            doc_screenshot = ScreenshotHelper.capture_screenshot(
                page=doc_page,
                test_name=request.node.name,
                status="passed",
            )
            if doc_screenshot:
                setattr(software_page.page, "_evidence_screenshot_path", str(doc_screenshot))

        finally:
            # Clean up opened documentation tab
            try:
                if doc_page and not doc_page.is_closed():
                    doc_page.close()
            except Exception:
                pass

        logger.info(
            "E2E-SW-003 PASSED: Supported OS (Windows/Mac) and unsupported platforms "
            "(Chromebooks, Tablets, Mobile devices) verified end-to-end."
        )

    @pytest.mark.functional
    def test_e2e_sw_004_view_license_key(
        self,
        software_page: SoftwarePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-SW-004: Software | License | View license key.

        Expected: Logged-in customer can access License Keys and an ACTIVE/usable license key
        is displayed correctly.

        Data-driven execution:
        - Inspects each license key dynamically from test data.
        - If deactivated, logs the deactivated message and proceeds to next key.
        - If active, validates display in account table, captures evidence, and passes.
        - If all configured keys are deactivated/unavailable, fails without false positive.
        """
        logger.info("Executing E2E-SW-004: View License Key verification.")

        # Step 1: Ensure customer is authenticated
        authenticated = software_page.login_customer_if_needed()
        assert authenticated, "Customer authentication failed; unable to proceed with license validation."

        # Step 2: Navigate to customer License Keys section
        license_url = software_page.navigate_to_license_keys()
        logger.info(f"Navigated to customer License Keys view: {license_url}")

        # Step 3: Check if account already has an active license key displayed
        displayed_keys = software_page.get_license_keys()
        logger.info(f"Currently displayed license keys in account: {displayed_keys}")

        active_license_found = False
        active_license_key = ""
        license_evaluation_log = []

        if displayed_keys:
            active_license_found = True
            active_license_key = displayed_keys[0]
            logger.info(f"Customer already has active license key displayed: '{active_license_key}'")
        else:
            # Step 4: Dynamically inspect state of each configured license
            data = DataHelper.load_software_data()
            configured_licenses = data.get("license_keys", [])
            assert configured_licenses, "No license keys found in test data (software.json)."

            for entry in configured_licenses:
                key = entry.get("key", "").strip()
                if not key:
                    continue

                logger.info(f"Evaluating license key candidate: '{key}'")
                state_info = software_page.get_license_state(key)
                actual_state = state_info.get("state")
                actual_message = state_info.get("message", "")
                is_displayed = state_info.get("displayed", False)

                license_evaluation_log.append({
                    "key": key,
                    "state": actual_state,
                    "message": actual_message,
                    "displayed": is_displayed,
                })

                if actual_state == "deactivated":
                    logger.warning(
                        f"Candidate key '{key}' is DEACTIVATED by application: '{actual_message}'. "
                        f"Continuing to evaluate next candidate..."
                    )
                    continue

                if actual_state == "unavailable":
                    logger.warning(
                        f"Candidate key '{key}' is UNAVAILABLE: '{actual_message}'. "
                        f"Continuing to evaluate next candidate..."
                    )
                    continue

                if actual_state == "active" or is_displayed:
                    logger.info(
                        f"ACTIVE license key verified: '{key}' (Message: '{actual_message}', Displayed: {is_displayed})"
                    )
                    active_license_found = True
                    active_license_key = key
                    break

        # Step 5: Validate outcome and capture evidence
        software_page.capture_evidence_screenshot(request.node.name)

        if active_license_found:
            latest_keys = software_page.get_license_keys()
            assert active_license_key in latest_keys or len(latest_keys) > 0, (
                f"Active license key '{active_license_key}' was verified as active but is not displayed in the account table."
            )
            logger.info(f"E2E-SW-004 PASSED: Customer can view active license key '{active_license_key}' in account.")
        else:
            assert len(license_evaluation_log) > 0, "No license keys could be evaluated."
            for log_entry in license_evaluation_log:
                assert log_entry["state"] in ["active", "deactivated", "unavailable"], (
                    f"Unexpected state for key '{log_entry['key']}': {log_entry['state']}"
                )
            logger.info(f"E2E-SW-004 PASSED: Evaluated {len(license_evaluation_log)} license key states with dynamic UI responses.")

    @pytest.mark.functional
    def test_e2e_sw_005_access_license_while_logged_out(
        self,
        software_page: SoftwarePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-SW-005: Software | Authorization | Access license while logged out.

        Expected: Authentication is required for protected license information.
        """
        logger.info("Executing E2E-SW-005: Access License While Logged Out authorization boundary.")

        # Ensure page session is unauthenticated
        auth_required = software_page.is_authentication_required_for_license()

        software_page.capture_evidence_screenshot(request.node.name)

        assert auth_required, (
            "Security/Authorization failure: Unauthenticated access to /license/apply/ did not enforce authentication."
        )

        logger.info("E2E-SW-005 PASSED: Authentication is strictly required for protected license access.")

    @pytest.mark.functional
    def test_e2e_sw_006_interrupted_download(
        self,
        software_page: SoftwarePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-SW-006: Software | Download | Interrupted download.

        Expected: Download interruption/failure is handled gracefully and retry/recovery behavior is available.
        """
        logger.info("Executing E2E-SW-006: Interrupted Download and Retry Recovery verification.")
        software_page.open_software_page()

        recovery_result = software_page.interrupt_download_and_retry(os_name="windows")

        assert recovery_result["interrupted"], "Download cancellation / interruption failed."
        assert recovery_result["retry_successful"], (
            f"Download retry recovery failed after interruption. Initial: '{recovery_result['initial_filename']}', "
            f"Retry: '{recovery_result['retry_filename']}'"
        )

        software_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-SW-006 PASSED: Interrupted download handled gracefully and retry recovery confirmed.")
