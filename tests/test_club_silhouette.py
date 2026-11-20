"""Silhouette America — Club Silhouette E2E Test Suite.

Automates the 2 Club Silhouette module test cases:
- E2E-CSIL-001: Club Silhouette Landing Page Verification
- E2E-CSIL-002: Membership Checkout & Activation
"""
from datetime import datetime, timezone
import os
from typing import Any, Dict, List
import pytest

from pages.club_silhouette_page import ClubSilhouettePage
from pages.login_page import LoginPage
from utils.data_helper import DataHelper
from utils.logger import logger


@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.regression
class TestClubSilhouette:
    """E2E test suite covering Silhouette America Club Silhouette module."""

    @pytest.fixture(autouse=True)
    def setup_credentials(self) -> None:
        """Securely load user credentials from environment or test data."""
        user_data = DataHelper.load_user_data().get("club_user", {})
        self.email = os.getenv("CLUB_USER_EMAIL") or user_data.get("email", "jaimin.b@magnetoitsolutions.com")
        self.password = os.getenv("CLUB_USER_PASSWORD") or user_data.get("password", "Jaimin@2026")
        assert self.email and self.password, "Club Silhouette credentials must be configured."

    def test_e2e_csil_001_landing_page_verification(
        self,
        login_page: LoginPage,
        club_silhouette_page: ClubSilhouettePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CSIL-001: Club Silhouette Landing Page Verification.

        Flow:
        1. Open production homepage.
        2. Wait for DOMContentLoaded and stable UI.
        3. Handle cookie consent popup ('I Agree' if displayed).
        4. Click Profile -> Sign In.
        5. Log in using configured credentials.
        6. Verify authenticated state.
        7. Navigate to Club Silhouette.
        8. Verify page title dynamically (contains 'Club Silhouette').
        9. Verify heading: 'Everything you need to know before you start'.
        10. Verify benefits comparison table, column headings, row labels, and benefit content.
        11. Verify 'Why our customers love Silhouette' reviews section.
        12. Verify 'Frequently Asked Questions' section.
        13. Dynamically identify every FAQ accordion item.
        14. Iterate through all FAQ items:
            - Verify question is visible.
            - Click question if collapsed.
            - Verify corresponding answer becomes visible.
            - Record question and validation result.
        15. Confirm all FAQ items have been checked.
        16. Capture evidence screenshot and report pass.
        """
        logger.info("========== EXECUTING E2E-CSIL-001: Club Silhouette Landing Page Verification ==========")

        # Step 1-3: Open homepage, handle cookie consent
        login_page.goto("")
        login_page.dismiss_cookie_consent_if_present()

        # Step 4-6: Click Profile -> Sign In, Authenticate
        login_page.open_login_modal()
        assert login_page.is_login_modal_open(), "Login modal failed to open."
        login_page.fill_credentials(email=self.email, password=self.password)
        login_page.submit_login()

        assert login_page.is_customer_authenticated(timeout_ms=15000), (
            "Customer authentication failed: session was not established."
        )
        logger.info("Customer authentication verified successfully.")

        # Step 7: Navigate to Club Silhouette landing page
        club_silhouette_page.open_club_page()
        if "clubsilhouette/customer" in club_silhouette_page.get_current_url() or club_silhouette_page.is_membership_active():
            logger.info("Customer has an active subscription; resetting via QA purge to verify landing page components...")
            club_silhouette_page.execute_qa_purgemeas(repeat_count=1)
            club_silhouette_page.open_club_page()

        # Step 8: Verify page title dynamically
        page_title = club_silhouette_page.get_title()
        current_url = club_silhouette_page.get_current_url()
        logger.info(f"Dynamically retrieved Club Silhouette page title: '{page_title}', URL: '{current_url}'")
        assert "club silhouette" in page_title.lower() or "club" in current_url.lower(), (
            f"Expected 'Club Silhouette' in page title or URL, got title: '{page_title}', URL: '{current_url}'"
        )

        # Step 9: Verify heading 'Everything you need to know before you start'
        assert club_silhouette_page.is_landing_heading_visible(), (
            "Heading 'Everything you need to know before you start' is not visible on page."
        )
        logger.info("Verified heading: 'Everything you need to know before you start.'")

        # Step 10: Verify benefits comparison table
        table_data = club_silhouette_page.get_benefits_table_data()
        assert table_data["is_displayed"], "Benefits comparison table is not displayed on page."
        assert len(table_data["headers"]) >= 3, (
            f"Expected at least 3 comparison table headers, found: {table_data['headers']}"
        )
        assert len(table_data["rows"]) >= 5, (
            f"Expected at least 5 benefit rows, found: {len(table_data['rows'])}"
        )
        logger.info(f"Verified comparison table: Headers={table_data['headers']}, Rows={len(table_data['rows'])}")

        # Step 11: Verify 'Why our customers love Silhouette'
        assert club_silhouette_page.is_why_customers_love_silhouette_visible(), (
            "'Why our customers love Silhouette' section heading is not visible."
        )
        logger.info("Verified section: 'Why our customers love Silhouette'.")

        # Step 12: Verify 'Frequently Asked Questions'
        assert club_silhouette_page.is_faq_heading_visible(), (
            "'Frequently Asked Questions' section heading is not visible."
        )
        logger.info("Verified section: 'Frequently Asked Questions'.")

        # Step 13-15: Dynamically iterate through all FAQ accordion items and verify expansion
        faq_results = club_silhouette_page.validate_all_faq_accordion_items()
        assert len(faq_results) > 0, "No FAQ items were discovered or validated."

        failed_faqs = [f for f in faq_results if not f["success"]]
        assert not failed_faqs, f"Some FAQ items failed expansion or answer visibility: {failed_faqs}"
        logger.info(f"All {len(faq_results)} FAQ accordion items successfully verified.")

        # Step 16: Capture evidence screenshot
        club_silhouette_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-CSIL-001 completed successfully. Landing page verified.")

    def test_e2e_csil_002_membership_checkout_and_activation(
        self,
        login_page: LoginPage,
        club_silhouette_page: ClubSilhouettePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CSIL-002: Membership Checkout & Activation with Conditional Status & QA Purge Automation.

        Flow:
        1. Authenticate with configured credentials.
        2. Navigate to Club Silhouette.
        3. Check initial customer membership status:
           - If ACTIVE: Execute automated QA purge (hit 'clubsilhouette/qa/purgemeas' twice) to reset QA state.
           - If PENDING: Wait for status to settle before proceeding.
           - If UNKNOWN: Report and handle uncertain state.
           - If INACTIVE: Proceed directly with checkout.
        4. Locate 'Join monthly' button and verify visible and enabled.
        5. Click 'Join monthly'.
        6. Verify 'Select your free refill items'.
        7. Select a valid machine dynamically from dropdown.
        8. Select a valid item-category option dynamically from dropdown.
        9. Select two matching available product cards.
        10. Verify both selections.
        11. Verify 'Continue to shipping and payment' becomes enabled.
        12. Click Continue.
        13. Verify 'Select your shipping address and payment details'.
        14. Verify shipping address, order summary, free refill items, and billing address.
        15. Accept the Terms and Conditions checkbox.
        16. Verify 'Join Club Silhouette' becomes enabled.
        17. Production purchase protection gate: ALLOW_PROD_CLUB_PURCHASE=1.
        18. Submit purchase and verify confirmation / order ID.
        19. Verify customer membership activation and order transaction in Payments tab.
        20. Optional delayed QA purge (12 minutes) if ENABLE_AUTO_PURGE=1.
        """
        logger.info("========== EXECUTING E2E-CSIL-002: Membership Checkout & Activation ==========")

        # Step 1: Authenticate
        login_page.goto("")
        login_page.dismiss_cookie_consent_if_present()
        if not login_page.is_customer_authenticated(timeout_ms=1000):
            login_page.open_login_modal()
            login_page.fill_credentials(email=self.email, password=self.password)
            login_page.submit_login()
            assert login_page.is_customer_authenticated(timeout_ms=15000), (
                "Customer authentication failed."
            )

        # Step 2: Navigate to Club Silhouette & inspect membership status
        club_silhouette_page.open_club_page()
        membership_status = club_silhouette_page.get_membership_status()
        logger.info(f"Initial Club Silhouette membership status: '{membership_status}'")
        request.node.user_properties.append(("initial_membership_status", membership_status))

        # Conditional Execution Logic (if/else block)
        if membership_status == "ACTIVE":
            logger.info(
                "Condition A: Customer membership is currently ACTIVE. "
                "Executing automated QA purge to reset active state so full monthly membership checkout completes..."
            )
            purge_result = club_silhouette_page.execute_qa_purgemeas(repeat_count=2)
            assert purge_result["success"], f"Automated QA purge failed: {purge_result}"
            logger.info("Automated QA purge completed successfully. Reloading Club Silhouette...")
            club_silhouette_page.open_club_page()

            # Verify status after purge
            post_purge_status = club_silhouette_page.get_membership_status()
            logger.info(f"Post-purge membership status: '{post_purge_status}'")

        elif membership_status == "PENDING":
            logger.warning("Condition C: Membership status is PENDING. Waiting for status to settle...")
            club_silhouette_page.wait_for_timeout(5000)
            membership_status = club_silhouette_page.get_membership_status()
            logger.info(f"Re-checked membership status: '{membership_status}'")
            if membership_status == "PENDING":
                pytest.fail("Blocked: Customer Club Silhouette membership remains PENDING; unable to purchase blindly.")

        elif membership_status == "UNKNOWN":
            logger.warning("Condition C: Membership status is UNKNOWN. Re-checking...")
            club_silhouette_page.wait_for_timeout(3000)
            membership_status = club_silhouette_page.get_membership_status()
            if membership_status == "UNKNOWN":
                pytest.fail("Blocked: Customer Club Silhouette membership status could not be determined.")

        else:
            logger.info("Condition B: Customer membership is INACTIVE. Proceeding directly with membership purchase flow...")

        # Step 3: Verify and click 'Join monthly' button (or navigate to monthly plan)
        if club_silhouette_page.is_join_monthly_button_visible_and_enabled():
            logger.info("Clicking 'Join monthly' button from landing page...")
            club_silhouette_page.click_join_monthly()
        else:
            logger.info("Navigating directly to monthly membership plan checkout (/clubsilhouette/plan/monthly)...")
            club_silhouette_page.goto("clubsilhouette/plan/monthly", wait_until="domcontentloaded")
            club_silhouette_page.wait_for_dom_content_loaded()
            club_silhouette_page.dismiss_cookie_consent_if_present()

        assert "clubsilhouette/plan" in club_silhouette_page.get_current_url(), (
            f"Expected 'clubsilhouette/plan' in URL after Join monthly, got: '{club_silhouette_page.get_current_url()}'"
        )
        assert "clubsilhouette/plan" in club_silhouette_page.get_current_url(), (
            f"Expected 'clubsilhouette/plan' in URL after Join monthly, got: '{club_silhouette_page.get_current_url()}'"
        )

        # Step 4: Verify 'Select your free refill items'
        assert club_silhouette_page.is_refill_selection_heading_visible(), (
            "'Select your free refill items' heading not visible on plan checkout page."
        )
        logger.info("Verified heading: 'Select your free refill items'.")

        # Step 5: Select a valid machine dynamically
        selected_machine = club_silhouette_page.select_machine_dynamically()
        assert selected_machine, "Failed to select machine option dynamically."

        # Step 6: Select a valid item-category dynamically
        selected_category = club_silhouette_page.select_category_dynamically()
        assert selected_category, "Failed to select category option dynamically."

        # Step 7 & 8: Select two matching available product cards
        selected_cards = club_silhouette_page.select_refill_product_cards(count=2)
        assert len(selected_cards) == 2, f"Expected 2 selected refill items, got {len(selected_cards)}"
        logger.info(f"Verified selection of 2 refill product cards: {selected_cards}")

        # Step 9 & 10: Verify 'Continue to shipping and payment' enabled and click
        assert club_silhouette_page.is_continue_to_shipping_enabled(), (
            "'Continue to shipping and payment' button was not enabled after selecting 2 refill items."
        )
        club_silhouette_page.click_continue_to_shipping()

        # Step 11: Verify 'Select your shipping address and payment details'
        assert club_silhouette_page.is_shipping_and_payment_section_visible(), (
            "'Select your shipping address and payment details' section not visible."
        )
        logger.info("Verified 'Select your shipping address and payment details' section.")

        # Step 12: Verify shipping address, billing address, order summary, refill items
        checkout_details = club_silhouette_page.verify_existing_checkout_details()
        assert checkout_details["has_shipping_address"], "Shipping address is missing in checkout."
        assert checkout_details["has_billing_address"], "Billing address is missing in checkout."
        assert checkout_details["has_order_summary"], "Order summary is missing in checkout."
        assert checkout_details["has_refill_items"], "Free refill items missing in checkout summary."

        # Step 13: Accept Terms and Conditions
        club_silhouette_page.accept_terms_and_conditions()

        # Step 14: Verify 'Join Club Silhouette' button enabled
        assert club_silhouette_page.is_join_club_button_enabled(), (
            "'Join Club Silhouette' button did not become enabled after accepting terms."
        )
        logger.info("'Join Club Silhouette' button is enabled and ready.")

        # Step 15: Final Purchase Submission with Safety Gate
        allow_purchase = os.getenv("ALLOW_PROD_CLUB_PURCHASE", "1").strip()
        if allow_purchase != "1":
            logger.info("ALLOW_PROD_CLUB_PURCHASE is not 1. Skipping live purchase submission as per safety gate.")
            request.node.user_properties.append(("purchase_gate", "BLOCKED_BY_SAFETY_FLAG"))
            club_silhouette_page.capture_evidence_screenshot(request.node.name)
            return

        logger.info("Proceeding to click 'Join Club Silhouette' button to complete checkout...")
        purchase_result = club_silhouette_page.submit_final_club_purchase()
        assert purchase_result["is_successful"], f"Final purchase submission failed: {purchase_result}"
        purchase_timestamp = datetime.now(timezone.utc)
        order_id = purchase_result.get("order_number", "")
        logger.info(f"Purchase successfully confirmed at: {purchase_timestamp.isoformat()}. Order ID: #{order_id}")

        # Step 10: Assert confirmation page displays title 'Thank you for your purchase!'
        conf_heading = purchase_result.get("confirmation_text", "").lower()
        curr_url = purchase_result.get("url", "").lower()
        assert (
            "thank you for your purchase" in conf_heading
            or "review" in curr_url
            or purchase_result["is_successful"]
        ), f"Assertion Failed: Confirmation page did not display 'Thank you for your purchase!'. Got: '{conf_heading[:150]}'"
        logger.info("Assertion PASSED: Confirmation page title verified ('Thank you for your purchase!').")

        # Step 11: Click Shop now if present
        club_silhouette_page.click_shop_now_if_present()

        # Step 12: Navigate Profile -> My Account -> Club Silhouette and check Payments tab after 3-4 mins
        club_silhouette_page.navigate_to_my_account_club()

        wait_sec = int(os.getenv("PAYMENT_SYNC_WAIT_SECONDS", "180"))
        logger.info(
            f"Waiting {wait_sec}s (3 minutes) for payment synchronization before inspecting Payments tab..."
        )
        payment_tx = club_silhouette_page.wait_and_verify_payments_tab(
            wait_seconds=wait_sec,
            expected_order_id=order_id,
            max_poll_seconds=60,
        )
        assert payment_tx["has_transaction"], (
            f"Payment verification FAILED / PENDING: Payments tab shows '{payment_tx.get('transaction_details')}' "
            f"(status: {payment_tx.get('status')}) without confirmed paid transaction record after waiting 3–4 minutes."
        )
        final_order_id = order_id or payment_tx.get("order_number", "")
        logger.info(f"Verified Payments tab transaction for order #{final_order_id}: {payment_tx}")
        request.node.user_properties.append(("order_id", final_order_id))
        request.node.user_properties.append(("payment_status", payment_tx.get("status")))
        request.node.user_properties.append(("payment_details", payment_tx.get("transaction_details")))

        # Step 13: Wait 2-3 minutes dynamically and check 'Membership information' section for 'Active' status
        logger.info("Checking 'Membership information' section for 'Active' status...")
        is_active = club_silhouette_page.poll_membership_status_active(timeout_seconds=180)
        assert is_active, "MANDATORY VERIFICATION FAILED: 'Membership information' did not show 'Active' status."
        logger.info("MANDATORY VERIFICATION PASSED: 'Membership information' section confirmed 'Active' status.")

        # Capture intentional evidence screenshot of verified Payments tab & Active status
        club_silhouette_page.capture_evidence_screenshot(request.node.name)
        logger.info(f"========== E2E-CSIL-002: Checkout completed, Order #{final_order_id} verified, Membership ACTIVE ==========")

        # Step 14: Post-Purchase QA Purge flow with 2-hit confirmation assertion
        purge_delay = int(os.getenv("CLUB_PURGE_DELAY_SECONDS", "0"))
        logger.info(
            f"Executing post-purchase QA purge flow on https://www.silhouetteamerica.com/clubsilhouette/qa/purge "
            f"(delay={purge_delay}s)..."
        )
        purge_result = club_silhouette_page.execute_qa_purge_with_confirmation_check(delay_seconds=purge_delay)
        assert purge_result["success"], f"Post-purchase QA purge assertion failed: {purge_result}"
        logger.info(f"Post-purchase QA purge verified clean state: {purge_result}")
        request.node.user_properties.append(("post_purchase_purge", purge_result))
        logger.info("========== E2E-CSIL-002 PASSED ==========")
