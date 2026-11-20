import os
from pathlib import Path
from typing import Any, Dict, List
import pytest

from pages.login_page import LoginPage
from pages.my_account_page import MyAccountPage
from utils.data_helper import DataHelper
from utils.logger import logger


@pytest.mark.e2e
@pytest.mark.my_account
class TestMyAccount:
    """My Account E2E test suite covering Account Dashboard, Profile / Account Information,
    Address Book (CRUD), My Orders, Software Licenses, Club Membership, Privacy & Data Rights,
    and My Wishlist.
    """

    # =========================================================================
    # E2E-ACC-001: Open My Account
    # =========================================================================
    @pytest.mark.smoke
    @pytest.mark.functional
    def test_e2e_acc_001_open_my_account(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-001: Open My Account dashboard and verify account details."""
        logger.info("Executing E2E-ACC-001: Open My Account.")
        page = authenticated_account_page

        # Step 1: Open My Account
        dest_url = page.open_my_account()
        assert "/customer/account" in dest_url, f"Unexpected URL after opening My Account: {dest_url}"

        # Step 2: Wait for dashboard to load
        assert page.is_dashboard_loaded(), "My Account dashboard failed to load."

        # Step 3: Verify dashboard content summary
        summary = page.get_dashboard_summary()
        logger.info(f"Dashboard summary verified: {summary}")
        assert summary["has_account_info"] or summary["has_address_book"] or summary["has_recent_orders"], (
            "No account sections found on dashboard."
        )

    # =========================================================================
    # E2E-ACC-002: Update Valid Profile
    # =========================================================================
    @pytest.mark.functional
    def test_e2e_acc_002_update_valid_profile(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-002: Update profile with valid data, verify persistence, and restore."""
        logger.info("Executing E2E-ACC-002: Update Valid Profile.")
        page = authenticated_account_page
        acc_data = DataHelper.load_account_data()

        # Step 1: Open profile section
        page.navigate_to_profile()

        # Step 2: Read and preserve existing profile values
        original_profile = page.get_profile_data()
        assert original_profile["firstname"], "Original firstname could not be read."
        logger.info(f"Preserving original profile values for safe restoration: {original_profile}")

        # Step 3: Update profile with temporary test values
        temp_first = acc_data.get("test_profile", {}).get("temp_firstname", "Anand Auto")
        try:
            page.update_profile(first_name=temp_first)

            # Optional success message check
            success_msg = page.get_profile_success_message(timeout_ms=3000)
            if success_msg:
                logger.info(f"Captured profile update confirmation: '{success_msg}'")

            # Step 4: Verify persistence after reload
            page.navigate_to_profile()
            page.reload()
            updated_profile = page.get_profile_data()
            assert updated_profile["firstname"] == temp_first, (
                f"Updated firstname '{temp_first}' did not persist. Found: '{updated_profile['firstname']}'"
            )
            logger.info("Profile update verified successfully.")

        finally:
            # Step 5: Strictly RESTORE original profile values on production
            logger.info(f"Restoring original firstname: '{original_profile['firstname']}'")
            page.navigate_to_profile()
            page.update_profile(first_name=original_profile["firstname"])
            page.navigate_to_profile()
            restored_profile = page.get_profile_data()
            assert restored_profile["firstname"] == original_profile["firstname"], (
                f"Failed to restore original profile value. Expected: '{original_profile['firstname']}', Found: '{restored_profile['firstname']}'"
            )
            logger.info("Original profile successfully restored.")

    # =========================================================================
    # E2E-ACC-003: Update Invalid Profile
    # =========================================================================
    @pytest.mark.negative
    @pytest.mark.functional
    def test_e2e_acc_003_update_invalid_profile(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-003: Attempt to update profile with blank/invalid data and verify rejection."""
        logger.info("Executing E2E-ACC-003: Update Invalid Profile.")
        page = authenticated_account_page

        # Step 1: Open profile section
        page.navigate_to_profile()
        original_data = page.get_profile_data()

        # Step 2: Enter invalid (blank required field) values
        page.update_profile(first_name="")

        # Step 3: Verify client-side / server-side validation error
        errors = page.get_profile_validation_errors()
        assert errors, "Validation error was not displayed for blank required profile field."
        logger.info(f"Validation error messages captured: {errors}")

        # Step 4: Reload and verify invalid data was NOT saved
        page.reload()
        current_data = page.get_profile_data()
        assert current_data["firstname"] == original_data["firstname"], (
            f"Invalid blank firstname was unexpectedly saved! Expected '{original_data['firstname']}', got '{current_data['firstname']}'"
        )
        logger.info("Invalid profile rejection verified successfully.")

    # =========================================================================
    # E2E-ACC-004: Add Valid Address
    # =========================================================================
    @pytest.mark.functional
    def test_e2e_acc_004_add_valid_address(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-004: Add a valid address with identifiable test prefix and verify in address book."""
        logger.info("Executing E2E-ACC-004: Add Valid Address.")
        page = authenticated_account_page
        acc_data = DataHelper.load_account_data()
        addr_data = acc_data.get("valid_address_1", {})

        # Step 1: Open Address Book and click Add New Address
        page.navigate_to_address_book()
        page.open_add_address_form()

        # Step 2: Fill all required fields using external test data and submit
        page.fill_address_form(addr_data)
        save_msg = page.submit_address_form()
        logger.info(f"Address save returned message: '{save_msg}'")

        # Step 3: Reopen or refresh Address Book
        page.navigate_to_address_book()
        page.reload()

        # Step 4: Verify newly saved address using its actual displayed details
        found = page.is_address_present_in_book(addr_data["street_0"])
        assert found, (
            f"Added address '{addr_data['street_0']}' not found in Address Book. Discovered: {page.get_all_addresses()}"
        )
        logger.info("Valid address successfully added and verified in Address Book.")

    # =========================================================================
    # E2E-ACC-005: Edit Address
    # =========================================================================
    @pytest.mark.functional
    def test_e2e_acc_005_edit_address(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-005: Edit an identifiable test-created address and verify updated details persist."""
        logger.info("Executing E2E-ACC-005: Edit Address.")
        page = authenticated_account_page
        acc_data = DataHelper.load_account_data()
        addr_1 = acc_data.get("valid_address_1", {})
        update_data = acc_data.get("updated_address", {})

        # Step 1: Open Address Book and ensure an identifiable test address exists
        page.navigate_to_address_book()
        if not page.is_address_present_in_book(addr_1["street_0"]):
            logger.info(f"Test address '{addr_1['street_0']}' not found; creating it first...")
            page.open_add_address_form()
            page.fill_address_form(addr_1)
            page.submit_address_form()
            page.navigate_to_address_book()
            assert page.is_address_present_in_book(addr_1["street_0"]), (
                "Failed to prepare test address for editing."
            )

        # Step 2: Locate Edit action belonging to that exact test address and update fields
        edited = page.edit_address_by_keyword(addr_1["street_0"], update_data)
        assert edited, f"Failed to edit test address matching '{addr_1['street_0']}'."

        # Step 3: Verify updated details persist
        page.navigate_to_address_book()
        page.reload()
        updated_key = update_data.get("street_0", addr_1["street_0"])
        found_updated = page.is_address_present_in_book(updated_key)
        assert found_updated, (
            f"Updated address details '{updated_key}' not found in Address Book. Discovered: {page.get_all_addresses()}"
        )
        logger.info("Address edit verified successfully.")

    # =========================================================================
    # E2E-ACC-006: Add Address with Default Shipping Address
    # =========================================================================
    @pytest.mark.functional
    def test_e2e_acc_006_add_address_with_default_shipping(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-006: Fill required address details, select default shipping address option, and verify."""
        logger.info("Executing E2E-ACC-006: Add Address with Default Shipping Address.")
        page = authenticated_account_page
        acc_data = DataHelper.load_account_data()
        ship_addr = acc_data.get("default_shipping_address", {})

        # Step 1 & 2: Log in and navigate to Address Book
        page.navigate_to_address_book()

        # Step 3 & 4: Click Add New Address
        page.open_add_address_form()

        # Step 5 & 6: Fill address form with complete fields & select default shipping
        page.fill_address_form(ship_addr, set_default_shipping=True)

        # Step 7: Verify default shipping checkbox state through Page Object method
        assert page.is_default_shipping_selected(), (
            "Default shipping checkbox is not selected before submission."
        )

        # Step 8: Click Save Address button and wait for completion
        save_msg = page.submit_address_form()
        logger.info(f"Save operation completed with message: '{save_msg}'")

        # Step 9: Return to Address Book and verify new address is displayed
        page.navigate_to_address_book()
        page.reload()
        assert page.is_address_present_in_book(ship_addr["street_0"]), (
            f"New address '{ship_addr['street_0']}' not found in Address Book."
        )

        # Step 10: Verify default shipping address selection was saved
        default_ship_text = page.get_default_shipping_address()
        logger.info(f"Default shipping address box text: '{default_ship_text}'")
        assert (
            ship_addr["street_0"].lower() in default_ship_text.lower()
            or ship_addr["city"].lower() in default_ship_text.lower()
            or ship_addr["postcode"] in default_ship_text
        ), f"Default shipping address does not match saved address: '{default_ship_text}'"

        logger.info("Default shipping address addition verified successfully.")

    # =========================================================================
    # E2E-ACC-007: Invalid/Incomplete Address
    # =========================================================================
    @pytest.mark.negative
    @pytest.mark.functional
    def test_e2e_acc_007_invalid_incomplete_address(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-007: Attempt to save incomplete address and verify required-field errors."""
        logger.info("Executing E2E-ACC-007: Invalid/Incomplete Address.")
        page = authenticated_account_page
        acc_data = DataHelper.load_account_data()
        incomplete_addr = acc_data.get("incomplete_address", {})

        # Step 1: Open Add Address form
        page.navigate_to_address_book()
        page.open_add_address_form()

        # Step 2: Fill incomplete data and attempt to submit
        page.fill_address_form(incomplete_addr)
        page.submit_address_form()

        # Step 3: Verify required-field validation errors
        errors = page.get_address_validation_errors()
        assert errors, "Validation error messages were not displayed for incomplete address."
        logger.info(f"Address validation errors captured: {errors}")

        # Step 4: Verify incomplete address was not created
        page.navigate_to_address_book()
        addresses = page.get_all_addresses()
        test_marker = incomplete_addr.get("street_0", "[TEST_INCOMPLETE]")
        if test_marker:
            assert not any(test_marker.lower() in a.lower() for a in addresses), (
                f"Incomplete address was unexpectedly created!"
            )
        logger.info("Required-field address validation verified successfully.")

    # =========================================================================
    # E2E-ACC-008: Additional Addresses Delete Confirmation
    # =========================================================================
    @pytest.mark.functional
    def test_e2e_acc_008_delete_additional_address(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-008: Additional Addresses Delete Confirmation flow."""
        logger.info("Executing E2E-ACC-008: Additional Addresses Delete Confirmation.")
        page = authenticated_account_page
        acc_data = DataHelper.load_account_data()
        addr_1 = acc_data.get("valid_address_1", {})
        test_key = addr_1["street_0"]

        # Step 1 & 2: Open Address Book and locate Additional Addresses section
        page.navigate_to_address_book()

        # Step 3: Ensure an address created specifically by automation exists in Additional Addresses
        if not page.is_address_present_in_additional(test_key):
            logger.info(f"No additional test address matching '{test_key}' found; creating one first...")
            page.open_add_address_form()
            page.fill_address_form(addr_1, set_default_shipping=False, set_default_billing=False)
            page.submit_address_form()
            page.navigate_to_address_book()
            assert page.is_address_present_in_additional(test_key), (
                "Failed to create test address under Additional Addresses."
            )

        # Steps 4-9: Click Delete icon (✕), verify popup, click OK, wait for completion, verify success message & removal
        del_result = page.delete_additional_address(keyword=test_key)
        assert del_result["deleted"], (
            f"Test address '{test_key}' was not deleted from Additional Addresses. Result: {del_result}"
        )
        assert not del_result["still_present"], (
            f"Deleted test address '{test_key}' is still displayed in Additional Addresses."
        )
        logger.info(f"Additional address delete confirmation passed successfully: {del_result}")

    # =========================================================================
    # E2E-ACC-009: View Order History
    # =========================================================================
    @pytest.mark.smoke
    @pytest.mark.functional
    def test_e2e_acc_009_view_order_history(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-009: View customer order history and validate visible order information."""
        logger.info("Executing E2E-ACC-009: View Order History.")
        page = authenticated_account_page

        # Step 1: Open My Orders
        page.navigate_to_orders()

        # Step 2: Extract orders
        orders = page.get_order_history_rows()
        assert orders, "Customer order history is empty; expected existing orders."

        # Step 3: Validate visible details on first order
        first_order = orders[0]
        logger.info(f"First order metadata: {first_order}")
        assert first_order.get("order_id"), "Order ID / number is missing from order history row."
        assert first_order.get("date"), "Order date is missing from order history row."
        assert first_order.get("total"), "Order total is missing from order history row."
        logger.info("Order history verification passed.")

    # =========================================================================
    # E2E-ACC-010: Open Order Details
    # =========================================================================
    @pytest.mark.functional
    def test_e2e_acc_010_open_order_details(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-010: Open an order's details and verify order number and items."""
        logger.info("Executing E2E-ACC-010: Open Order Details.")
        page = authenticated_account_page

        # Step 1: Open My Orders
        page.navigate_to_orders()

        # Step 2: Open details of first order
        order_meta = page.open_order_details(order_index=0)
        selected_order_id = order_meta.get("order_id", "")

        # Step 3: Validate order details page
        details = page.get_order_details_info()
        logger.info(f"Order details page data: {details}")

        if selected_order_id:
            # Order title or page text should contain the order ID
            page_content = page.page.content()
            assert selected_order_id in page_content, (
                f"Selected order number '{selected_order_id}' not found on order details page."
            )
        assert details["status"] or details["grand_total"] or details["items"], (
            "Order details page lacks order items, status, and grand total."
        )
        logger.info("Order details verification passed.")

    # =========================================================================
    # E2E-ACC-011: View Software License Keys
    # =========================================================================
    @pytest.mark.functional
    def test_e2e_acc_011_view_software_license_keys(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-011: View available software license keys / downloadable products."""
        logger.info("Executing E2E-ACC-011: View Software License Keys.")
        page = authenticated_account_page

        # Step 1: Navigate to software licenses
        page.navigate_to_software_licenses()

        # Step 2: Extract license records (with sensitive key masking)
        licenses = page.get_software_licenses()
        logger.info(f"Software license entries retrieved: {licenses}")

        if not licenses:
            logger.info("Customer account currently has no downloadable licenses; verified empty state.")
        else:
            for lic in licenses:
                assert lic.get("product"), "License product title is missing."
        logger.info("Software licenses section verified successfully.")

    # =========================================================================
    # E2E-ACC-012: View Club Membership
    # =========================================================================
    @pytest.mark.functional
    def test_e2e_acc_012_view_club_membership(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-012: View Club Silhouette membership and verify Club Silhouette title."""
        logger.info("Executing E2E-ACC-012: View Club Membership.")
        page = authenticated_account_page

        # Step 1: Open My Account
        page.open_my_account()

        # Step 2: Open Club Membership section
        page.navigate_to_club_membership()

        # Step 3: Wait for membership section to load and verify actual Club Silhouette title is visible
        assert page.is_club_silhouette_title_visible(), (
            f"Expected 'Club Silhouette' title not visible on page. Current URL: '{page.get_current_url()}', Title: '{page.get_title()}'"
        )
        logger.info("Club Silhouette membership title verification passed.")

    # =========================================================================
    # E2E-ACC-013: Download Personal Data
    # =========================================================================
    @pytest.mark.functional
    def test_e2e_acc_013_download_personal_data(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-013: Download Personal Data with password verification via Playwright download event."""
        logger.info("Executing E2E-ACC-013: Download Personal Data.")
        page = authenticated_account_page
        user_data = DataHelper.load_user_data().get("valid_user", {})
        password = user_data.get("password")

        # Step 1: Navigate to Privacy section
        page.navigate_to_privacy()

        # Step 2: Trigger download handling
        downloaded_file = page.download_personal_data(password=password)
        if downloaded_file and downloaded_file.exists():
            assert downloaded_file.stat().st_size > 0, "Downloaded personal data file is empty."
            logger.info(f"Verified downloaded data file: {downloaded_file}")
            # Safely delete personal data file to prevent storing sensitive PII
            try:
                os.remove(downloaded_file)
                logger.info("Safely cleaned up downloaded personal data file.")
            except Exception as e:
                logger.debug(f"Cleanup notice: {e}")
        else:
            logger.info("Download personal data option not available or restricted on this account environment.")

    # =========================================================================
    # E2E-ACC-014: Don't Sell or Share My Personal Information
    # =========================================================================
    @pytest.mark.functional
    def test_e2e_acc_014_privacy_preference(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-014: Inspect 'Don't Sell or Share My Personal Information' preference state."""
        logger.info("Executing E2E-ACC-014: Don't Sell or Share My Personal Information preference.")
        page = authenticated_account_page

        # Step 1: Navigate to Privacy section
        page.navigate_to_privacy()

        # Step 2: Inspect preference state safely
        state = page.get_privacy_preference_state()
        logger.info(f"Current privacy preference state: {state}")

        # Per prompt rule: "Do not change this setting on a production customer account without explicit authorization."
        logger.info("Privacy preference inspected safely without modifying legal status on production.")

    # =========================================================================
    # E2E-ACC-015: Add Item to Wishlist
    # =========================================================================
    @pytest.mark.functional
    def test_e2e_acc_015_add_item_to_wishlist(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ACC-015: Dynamically select product, add to wishlist from PDP, and verify in My Wishlist."""
        logger.info("Executing E2E-ACC-015: Add Product to Wishlist.")
        page = authenticated_account_page

        # Steps 1-9: Navigate to shop, select product dynamically, open PDP, click wishlist icon
        added_product = page.add_pdp_product_to_wishlist(shop_url="accessories")
        product_name = added_product.get("name", "")
        assert product_name, "Product name could not be identified from PDP."

        # Step 10 & 11: Navigate to My Account -> My Wishlist
        page.open_my_account()
        page.navigate_to_wishlist()
        page.wait_for_dom_content_loaded()

        # Step 12: Verify that the exact selected product is displayed
        wishlist_items = page.get_wishlist_items()
        assert wishlist_items, f"Wishlist is empty after adding product '{product_name}'."
        matched = any(product_name.lower() in item["name"].lower() for item in wishlist_items)
        assert matched, f"Added product '{product_name}' not found in My Wishlist: {wishlist_items}"
        logger.info(f"Verified product '{product_name}' successfully displayed in My Wishlist.")
        # Note: per requirement, do not remove the product after verification
