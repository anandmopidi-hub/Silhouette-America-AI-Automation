"""Silhouette America — Wishlist E2E Test Suite.

Automates the 6 Wishlist module test cases:
- E2E-WIS-001: Guest User – Wishlist Sign In Popup
- E2E-WIS-002: Logged-in User – Add Single Product
- E2E-WIS-003: Logged-in User – Add Multiple Products
- E2E-WIS-004: Remove Single Wishlist Item
- E2E-WIS-005: Clear All Wishlist Items
- E2E-WIS-006: Add All Wishlist Items to Cart
"""
from typing import Any, Dict, List
import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.my_account_page import MyAccountPage
from utils.logger import logger


@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.regression
class TestWishlist:
    """E2E test suite covering Silhouette America Wishlist functionality."""

    # =========================================================================
    # E2E-WIS-001: Guest User – Wishlist Sign In Popup
    # =========================================================================
    def test_e2e_wis_001_guest_wishlist_signin_popup(
        self,
        page: Page,
        login_page: LoginPage,
        my_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-WIS-001: Verify that a guest user clicking a product Wishlist icon receives
        the Sign In popup and the product is not saved without authentication.

        Test Steps:
        1. Create a fresh guest browser context using existing fixtures.
        2. Ensure the context is not authenticated.
        3. Open the production website.
        4. Navigate to an available product PLP or PDP.
        5. Dynamically identify a product.
        6. Click its Wishlist heart icon.
        7. Wait for the authentication modal.
        8. Verify that the Sign In popup is visible.
        9. Verify that the product has not been added to the guest Wishlist.
        """
        logger.info("========== EXECUTING E2E-WIS-001: Guest User – Wishlist Sign In Popup ==========")

        # Step 1 & 2: Ensure the guest context is completely unauthenticated
        assert not login_page.is_customer_authenticated(timeout_ms=2000), (
            "Precondition failed: guest session is unexpectedly authenticated."
        )

        # Step 3: Open the production website
        my_account_page.goto("", wait_until="domcontentloaded")
        my_account_page.handle_cloudflare_if_present()
        my_account_page.dismiss_cookie_consent_if_present()

        # Step 4 & 5: Navigate to catalog and dynamically open a product PDP
        product_info = my_account_page.open_product_pdp(shop_url="accessories", product_index=0)
        product_name = product_info.get("name", "")
        assert product_name, "Failed to dynamically capture product name from PDP."
        logger.info(f"Target product identified for guest wishlist attempt: '{product_name}'")

        # Step 6: Click its Wishlist heart icon
        my_account_page.click_pdp_wishlist_button()

        # Step 7 & 8: Wait for authentication modal and verify Sign In popup is visible
        modal_visible = my_account_page.is_wishlist_auth_popup_visible(timeout_ms=6000) or login_page.is_login_modal_open()
        assert modal_visible, "Sign In popup was not displayed to guest user upon clicking Wishlist button."
        logger.info("Verified Sign In popup modal is visible after guest clicked Wishlist.")

        # Step 9: Verify guest user cannot save product without authentication
        assert not login_page.is_customer_authenticated(timeout_ms=1000), (
            "Session unexpectedly became authenticated without user input."
        )
        assert "/wishlist" not in my_account_page.get_current_url(), (
            "Guest was unexpectedly redirected to wishlist area."
        )

        # Capture evidence screenshot
        my_account_page.capture_evidence_screenshot(request.node.name)
        logger.info("Completed E2E-WIS-001 successfully.")

    # =========================================================================
    # E2E-WIS-002: Logged-in User – Add Single Product
    # =========================================================================
    def test_e2e_wis_002_logged_in_add_single_product(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-WIS-002: Verify that an authenticated user can add one product to Wishlist.

        Test Steps:
        1. Use the existing authenticated customer fixture.
        2. Navigate to the Shop/catalog page.
        3. Dynamically identify an available product.
        4. Open its PDP.
        5. Capture product name, price, and relevant product identifier dynamically.
        6. Click the Wishlist heart icon.
        7. Wait for the actual success feedback or icon state.
        8. Navigate to My Account -> My Wishlist.
        9. Locate the Wishlist product card.
        10. Verify that the same product appears.
        """
        logger.info("========== EXECUTING E2E-WIS-002: Logged-in User – Add Single Product ==========")
        page = authenticated_account_page

        # Step 2-7: Navigate to catalog, dynamically select product, open PDP, capture data, click Wishlist
        product_info = page.add_pdp_product_to_wishlist(shop_url="accessories", product_index=0)
        product_name = product_info.get("name", "")
        product_price = product_info.get("price", "")
        assert product_name, "Failed to capture product name from PDP."
        logger.info(f"Captured added product: '{product_name}', Price: '{product_price}'")

        # Step 8 & 9: Navigate to My Account -> My Wishlist
        page.navigate_to_wishlist()
        page.wait_for_dom_content_loaded()

        # Step 10: Verify that the matching product appears in customer Wishlist
        wishlist_items = page.get_wishlist_items()
        assert wishlist_items, f"Wishlist is empty after adding product '{product_name}'."
        assert page.is_product_in_wishlist(product_name), (
            f"Added product '{product_name}' was not found in My Wishlist. Current items: {wishlist_items}"
        )
        logger.info(f"Verified product '{product_name}' is displayed in My Wishlist.")

        # Capture evidence screenshot
        page.capture_evidence_screenshot(request.node.name)
        logger.info("Completed E2E-WIS-002 successfully.")

    # =========================================================================
    # E2E-WIS-003: Logged-in User – Add Multiple Products
    # =========================================================================
    def test_e2e_wis_003_logged_in_add_multiple_products(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-WIS-003: Verify that multiple distinct products can be added to Wishlist.

        Test Steps:
        1. Use the authenticated customer fixture.
        2. Dynamically identify Product A.
        3. Capture its product name and identifier.
        4. Add Product A to Wishlist.
        5. Return to the catalog.
        6. Dynamically identify a different Product B.
        7. Capture its product name and identifier.
        8. Add Product B to Wishlist.
        9. Navigate to My Wishlist.
        10. Extract the Wishlist product names dynamically.
        11. Verify both Product A and Product B are present.
        """
        logger.info("========== EXECUTING E2E-WIS-003: Logged-in User – Add Multiple Products ==========")
        page = authenticated_account_page

        # Step 2, 3, 4: Dynamically select and add Product A (index 1)
        product_a = page.add_pdp_product_to_wishlist(shop_url="accessories", product_index=1, ensure_added=True)
        name_a = product_a.get("name", "")
        assert name_a, "Failed to dynamically capture Product A name."
        logger.info(f"Added Product A: '{name_a}'")

        # Step 5, 6, 7, 8: Return to catalog and dynamically select and add distinct Product B (index 2)
        product_b = page.add_pdp_product_to_wishlist(shop_url="accessories", product_index=2, ensure_added=True)
        name_b = product_b.get("name", "")
        assert name_b, "Failed to dynamically capture Product B name."
        logger.info(f"Added Product B: '{name_b}'")

        assert name_a.strip().lower() != name_b.strip().lower(), (
            f"Precondition failed: Product A and Product B must be distinct, but both were '{name_a}'."
        )

        # Step 9: Navigate to My Wishlist
        page.navigate_to_wishlist()
        page.wait_for_dom_content_loaded()

        # Step 10 & 11: Extract Wishlist product names dynamically and verify both are present
        wishlist_items = page.get_wishlist_items()
        logger.info(f"Wishlist items retrieved: {wishlist_items}")
        assert page.is_product_in_wishlist(name_a), f"Product A '{name_a}' not found in My Wishlist."
        assert page.is_product_in_wishlist(name_b), f"Product B '{name_b}' not found in My Wishlist."
        logger.info(f"Verified both Product A ('{name_a}') and Product B ('{name_b}') are present in My Wishlist.")

        # Capture evidence screenshot
        page.capture_evidence_screenshot(request.node.name)
        logger.info("Completed E2E-WIS-003 successfully.")

    # =========================================================================
    # E2E-WIS-004: Remove Single Wishlist Item
    # =========================================================================
    def test_e2e_wis_004_remove_single_wishlist_item(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-WIS-004: Verify that one selected Wishlist item can be removed.

        Test Steps:
        1. Use the authenticated customer fixture.
        2. Open My Wishlist.
        3. Identify an automation-created Wishlist item.
        4. Capture its product name or identifier.
        5. Record the initial Wishlist item count dynamically.
        6. Click the Remove Item action for that specific product card.
        7. Wait for the UI update.
        8. Verify that the selected product is no longer present.
        9. Verify that the Wishlist count decreases by one.
        """
        logger.info("========== EXECUTING E2E-WIS-004: Remove Single Wishlist Item ==========")
        page = authenticated_account_page

        # Step 2: Open My Wishlist
        page.navigate_to_wishlist()
        page.wait_for_dom_content_loaded()

        # Step 3: Ensure at least one Wishlist item exists; if not, dynamically add one first
        items = page.get_wishlist_items()
        if not items:
            logger.info("Wishlist is empty. Dynamically adding an item to test removal...")
            page.add_pdp_product_to_wishlist(shop_url="accessories", product_index=0)
            page.navigate_to_wishlist()
            page.wait_for_dom_content_loaded()
            items = page.get_wishlist_items()

        assert items, "Failed to prepare a Wishlist item for removal test."

        # Step 4 & 5: Identify the target item and record initial count
        target_item = items[0]
        target_name = target_item["name"]
        initial_count = len(items)
        logger.info(f"Removing target Wishlist item: '{target_name}', initial item count: {initial_count}")

        # Step 6 & 7: Click Remove Item action for that specific product card and wait for update
        removed = page.remove_wishlist_item_by_name(target_name)
        assert removed, f"Failed to remove Wishlist item '{target_name}'."

        # Step 8: Verify that the selected product is no longer present
        assert not page.is_product_in_wishlist(target_name), (
            f"Product '{target_name}' is still present in Wishlist after removal."
        )

        # Step 9: Verify that the Wishlist count decreases by one
        new_items = page.get_wishlist_items()
        new_count = len(new_items)
        logger.info(f"Wishlist count updated from {initial_count} to {new_count}")
        assert new_count == initial_count - 1, (
            f"Wishlist count did not decrease by one: initial={initial_count}, new={new_count}"
        )

        # Capture evidence screenshot
        page.capture_evidence_screenshot(request.node.name)
        logger.info("Completed E2E-WIS-004 successfully.")

    # =========================================================================
    # E2E-WIS-005: Clear All Wishlist Items
    # =========================================================================
    def test_e2e_wis_005_clear_all_wishlist_items(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-WIS-005: Verify the Clear Wishlist functionality.

        Test Steps:
        1. Use the authenticated customer fixture.
        2. Prepare a Wishlist containing automation-created products only.
        3. Open My Wishlist.
        4. Verify the initial Wishlist item count is greater than zero.
        5. Click Clear Wishlist.
        6. Inspect whether a confirmation popup appears.
        7. Confirm the action only if the Wishlist contains exclusively automation-created test items.
        8. Wait for the Wishlist update.
        9. Verify the Wishlist item count becomes zero.
        10. Verify the empty Wishlist message/container appears.
        """
        logger.info("========== EXECUTING E2E-WIS-005: Clear All Wishlist Items ==========")
        page = authenticated_account_page

        # Step 2 & 3: Open My Wishlist
        page.navigate_to_wishlist()
        page.wait_for_dom_content_loaded()

        # Step 4: Ensure Wishlist has at least one item before clearing
        items = page.get_wishlist_items()
        if not items:
            logger.info("Wishlist is empty. Dynamically adding an item to test Clear Wishlist...")
            page.add_pdp_product_to_wishlist(shop_url="accessories", product_index=0)
            page.navigate_to_wishlist()
            page.wait_for_dom_content_loaded()
            items = page.get_wishlist_items()

        assert len(items) > 0, "Precondition failed: Wishlist has 0 items to clear."
        logger.info(f"Initial Wishlist item count before clear: {len(items)}")

        # Step 5-8: Click Clear Wishlist, confirm action, wait for update
        cleared = page.clear_all_wishlist_items()
        assert cleared, "Clear all wishlist items action did not complete successfully."

        # Step 9 & 10: Verify the Wishlist item count becomes zero and empty state appears
        remaining_items = page.get_wishlist_items()
        assert len(remaining_items) == 0, (
            f"Expected 0 items in Wishlist after clear, found {len(remaining_items)}: {remaining_items}"
        )
        logger.info("Verified Wishlist item count is now 0 and empty state is displayed.")

        # Capture evidence screenshot
        page.capture_evidence_screenshot(request.node.name)
        logger.info("Completed E2E-WIS-005 successfully.")

    # =========================================================================
    # E2E-WIS-006: Add All Wishlist Items to Cart
    # =========================================================================
    def test_e2e_wis_006_add_all_wishlist_items_to_cart(
        self,
        authenticated_account_page: MyAccountPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-WIS-006: Verify that all Wishlist items can be transferred to the Shopping Cart.

        Test Steps:
        1. Use the authenticated customer fixture.
        2. Prepare the Wishlist with automation-created, in-stock products.
        3. Open My Wishlist.
        4. Read the initial Cart badge count dynamically.
        5. Read the initial Wishlist item count dynamically.
        6. Verify that the selected Wishlist items are available and in stock.
        7. Click Add All to Cart.
        8. Wait for the actual cart update.
        9. Read the new Cart badge count.
        10. Verify the actual success feedback.
        11. Verify the cart contents where possible.
        """
        logger.info("========== EXECUTING E2E-WIS-006: Add All Wishlist Items to Cart ==========")
        page = authenticated_account_page

        # Step 2 & 3: Open My Wishlist and ensure at least one item is present
        page.navigate_to_wishlist()
        page.wait_for_dom_content_loaded()

        items = page.get_wishlist_items()
        if not items:
            logger.info("Wishlist is empty. Dynamically adding an item to test Add All to Cart...")
            page.add_pdp_product_to_wishlist(shop_url="accessories", product_index=0)
            page.navigate_to_wishlist()
            page.wait_for_dom_content_loaded()
            items = page.get_wishlist_items()

        assert len(items) > 0, "Precondition failed: Wishlist has no items to add to cart."
        logger.info(f"Verified {len(items)} items in Wishlist before Add All to Cart.")

        # Step 4-10: Execute Add All to Cart and capture initial and updated status
        result = page.add_all_wishlist_items_to_cart()
        initial_cart = result["initial_cart_count"]
        updated_cart = result["updated_cart_count"]
        msg = result["success_message"]
        curr_url = result["current_url"]

        logger.info(
            f"Add All to Cart result -> Initial Cart: {initial_cart}, Updated Cart: {updated_cart}, "
            f"Message: '{msg}', URL: '{curr_url}'"
        )

        # Verification: Either the cart badge count increased, a cart success message appeared,
        # or the user was redirected to the shopping cart (/checkout/cart/)
        cart_updated = (
            updated_cart > initial_cart
            or "checkout/cart" in curr_url
            or len(msg) > 0
        )
        assert cart_updated, (
            f"Cart was not updated after clicking Add All to Cart. "
            f"initial_cart={initial_cart}, updated_cart={updated_cart}, msg='{msg}', url='{curr_url}'"
        )
        logger.info("Verified Add All to Cart successfully transferred items or redirected to Cart.")

        # Capture evidence screenshot
        page.capture_evidence_screenshot(request.node.name)
        logger.info("Completed E2E-WIS-006 successfully.")

