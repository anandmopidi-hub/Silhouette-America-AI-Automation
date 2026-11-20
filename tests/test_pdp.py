import re
import pytest
from pages.pdp_page import PdpPage
from utils.logger import logger


@pytest.mark.e2e
class TestPdp:
    """Product Detail Page (PDP) E2E test suite covering product metadata,

    regular and sale pricing, configurable variants, option validation,
    cart addition, out-of-stock handling, quantity boundaries, and reload persistence.
    """

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_e2e_pdp_001_open_pdp(self, pdp_page: PdpPage, request: pytest.FixtureRequest) -> None:
        """E2E-PDP-001: Open Product Detail Page and verify correct page loads."""
        logger.info("Executing E2E-PDP-001: Open Product Detail Page.")
        current_url = pdp_page.open_pdp("cameo-mat")

        assert "cameo-mat" in current_url.lower(), (
            f"Expected 'cameo-mat' in destination URL, got: '{current_url}'"
        )
        assert pdp_page.is_pdp_loaded(expected_slug_or_name="cameo-mat"), (
            "PDP failed to load or key layout elements are missing."
        )

        # Intentional validated evidence capture
        pdp_page.prepare_for_pdp_evidence()
        pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-PDP-001 completed successfully.")

    @pytest.mark.functional
    def test_e2e_pdp_002_verify_product_information(self, pdp_page: PdpPage, request: pytest.FixtureRequest) -> None:
        """E2E-PDP-002: Verify product name, actually displayed images, SKU, description, and specifications."""
        logger.info("Executing E2E-PDP-002: Verify Product Information.")
        pdp_page.open_pdp("cameo-mat")

        # 1. Product Name Validation (dynamically against actual UI)
        product_name = pdp_page.get_product_name()
        assert len(product_name) > 0, "Product name is missing or empty."
        assert "cameo" in product_name.lower(), f"Expected 'cameo' in product name, got: '{product_name}'"
        logger.info(f"Verified product name: '{product_name}'")

        # 2. SKU Validation (dynamically against actual UI)
        sku = pdp_page.get_product_sku()
        assert len(sku) > 0, "Product SKU is missing or empty."
        assert re.match(r"^[A-Z0-9\-]+$", sku), f"SKU format is invalid: '{sku}'"
        assert "cameo" in sku.lower() or "mat" in sku.lower(), f"Unexpected SKU value: '{sku}'"
        logger.info(f"Verified product SKU: '{sku}'")

        # 3. Product Images Actually Displayed Validation (dynamic count & click-through verification)
        assert pdp_page.is_product_image_visible(), "Active product image is not visible or loaded."
        image_count = pdp_page.get_product_image_count()
        assert image_count > 0, f"Expected at least 1 actual displayed gallery image, found {image_count}."
        logger.info(f"Verified actual gallery image count: {image_count}")

        # Click through each gallery image thumbnail and verify dynamic rendering and loading
        displayed_image_urls = pdp_page.click_through_gallery_images()
        assert len(displayed_image_urls) == image_count, (
            f"Mismatch between detected gallery count ({image_count}) and displayed images ({len(displayed_image_urls)})."
        )
        for idx, img_url in enumerate(displayed_image_urls, start=1):
            assert img_url.startswith("http") or img_url.startswith("//"), (
                f"Image {idx} URL is invalid: '{img_url}'"
            )
            assert any(ext in img_url.lower() for ext in [".webp", ".jpg", ".jpeg", ".png"]), (
                f"Image {idx} does not have a valid image format extension: '{img_url}'"
            )
        logger.info(f"Verified all {len(displayed_image_urls)} displayed product images loaded with valid URLs.")

        # 4. Description Validation (dynamically against actual UI)
        description = pdp_page.get_product_description()
        assert len(description) > 20, (
            f"Expected detailed product description, got '{description}' (length={len(description)})"
        )
        assert description != product_name and description != sku, (
            "Description must be distinct from product name and SKU."
        )
        logger.info(f"Verified product description is populated ({len(description)} chars).")

        # 5. Specifications Validation (dynamically if available)
        if pdp_page.has_specifications():
            specs = pdp_page.get_product_specifications()
            assert len(specs) > 0, "Product specifications detected but content is empty."
            logger.info(f"Verified product specifications ({len(specs)} chars).")
        else:
            logger.info("Specifications section is not present on this product category (accessory); handled gracefully.")

        # Intentional validated evidence capture
        pdp_page.prepare_for_pdp_evidence()
        pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-PDP-002 completed successfully.")

    @pytest.mark.functional
    def test_e2e_pdp_003_verify_regular_price(self, pdp_page: PdpPage, request: pytest.FixtureRequest) -> None:
        """E2E-PDP-003: Verify correct regular price is displayed on PDP."""
        logger.info("Executing E2E-PDP-003: Verify Regular Price.")
        pdp_page.open_pdp("cameo-mat")

        price = pdp_page.get_regular_price()
        assert len(price) > 0, "Regular price is empty or not displayed."
        assert "$" in price, f"Expected currency symbol '$' in regular price, got: '{price}'"

        # Validate currency format (e.g. $14.99)
        price_match = re.search(r"\$\s*(\d+(\.\d{2})?)", price)
        assert price_match is not None, f"Price '{price}' does not match standard currency format."

        numeric_val = float(price_match.group(1))
        assert numeric_val > 0, f"Expected price greater than 0, got: {numeric_val}"
        logger.info(f"Verified regular price dynamically: '{price}' (numeric={numeric_val})")

        # Intentional validated evidence capture
        pdp_page.prepare_for_pdp_evidence()
        pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-PDP-003 completed successfully.")

    @pytest.mark.functional
    def test_e2e_pdp_004_verify_sale_price(self, pdp_page: PdpPage, request: pytest.FixtureRequest) -> None:
        """E2E-PDP-004: Verify both sale/current price and original/regular price on a sale product."""
        logger.info("Executing E2E-PDP-004: Verify Sale Price.")
        # Target verified sale product: Silhouette Cameo 4 Pro
        pdp_page.open_pdp("cameo-pro")

        sale_price = pdp_page.get_sale_price()
        original_price = pdp_page.get_original_price()

        assert sale_price is not None, "Sale price (special price) is not displayed on sale product PDP."
        assert original_price is not None, "Original price (old price) is not displayed on sale product PDP."
        assert "$" in sale_price, f"Expected currency symbol '$' in sale price, got: '{sale_price}'"
        assert "$" in original_price, f"Expected currency symbol '$' in original price, got: '{original_price}'"

        sale_num_match = re.search(r"(\d+(\.\d{2})?)", sale_price)
        orig_num_match = re.search(r"(\d+(\.\d{2})?)", original_price)
        assert sale_num_match is not None, f"Could not parse numeric value from sale price '{sale_price}'"
        assert orig_num_match is not None, f"Could not parse numeric value from original price '{original_price}'"

        sale_num = float(sale_num_match.group(1))
        orig_num = float(orig_num_match.group(1))

        assert sale_num < orig_num, (
            f"Expected sale price ({sale_num}) to be strictly less than original price ({orig_num})."
        )
        logger.info(
            f"Verified sale pricing dynamically: Sale Price='{sale_price}' (${sale_num:.2f}) < "
            f"Original Price='{original_price}' (${orig_num:.2f})"
        )

        # Intentional validated evidence capture
        pdp_page.prepare_for_pdp_evidence()
        pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-PDP-004 completed successfully.")

    @pytest.mark.functional
    def test_e2e_pdp_005_select_valid_variant(self, pdp_page: PdpPage, request: pytest.FixtureRequest) -> None:
        """E2E-PDP-005: Select valid variant and verify selected state and price update."""
        logger.info("Executing E2E-PDP-005: Select Valid Variant.")
        pdp_page.open_pdp("cameo-mat")

        initial_price = pdp_page.get_regular_price()
        initial_selected = pdp_page.get_selected_variants()
        logger.info(f"Initial state: price='{initial_price}', selected={initial_selected}")

        target_variant = '12" x 24"'
        pdp_page.select_variant(target_variant)

        updated_selected = pdp_page.get_selected_variants()
        assert any(target_variant in s for s in updated_selected), (
            f"Expected variant '{target_variant}' to be selected, found: {updated_selected}"
        )

        updated_price = pdp_page.get_regular_price()
        logger.info(f"Updated state after selecting '{target_variant}': price='{updated_price}', selected={updated_selected}")

        init_num = float(re.search(r"(\d+(\.\d{2})?)", initial_price).group(1))
        updated_num = float(re.search(r"(\d+(\.\d{2})?)", updated_price).group(1))
        assert updated_num > init_num, (
            f"Expected updated price (${updated_num}) for '{target_variant}' to exceed base price (${init_num})."
        )

        # Intentional validated evidence capture
        pdp_page.prepare_for_pdp_evidence()
        pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-PDP-005 completed successfully.")

    @pytest.mark.functional
    def test_e2e_pdp_006_attempt_add_without_mandatory_option(
        self,
        pdp_page: PdpPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-PDP-006: Attempt to add configurable product without selecting mandatory option."""
        logger.info("Executing E2E-PDP-006: Attempt Add Without Mandatory Option.")
        pdp_page.open_pdp("cameo-mat")

        # Deselect active swatch option to simulate missing required selection
        pdp_page.deselect_active_variant()
        pdp_page.click_add_to_cart()

        assert pdp_page.is_mandatory_option_error_displayed(), (
            "Expected mandatory option validation error ('This is a required field.') was not displayed."
        )
        error_text = pdp_page.get_mandatory_option_error_text()
        logger.info(f"Captured mandatory option validation message: '{error_text}'")

        # Ensure cart was NOT updated
        assert pdp_page.get_cart_count() == 0, "Cart count increased unexpectedly after validation failure."

        # Intentional validated evidence capture
        pdp_page.prepare_for_pdp_evidence()
        pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-PDP-006 completed successfully.")

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_e2e_pdp_007_add_available_product_to_cart(
        self,
        pdp_page: PdpPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-PDP-007: Add an in-stock available product to cart and verify cart count/state."""
        logger.info("Executing E2E-PDP-007: Add Available Product to Cart.")
        pdp_page.open_pdp("cameo-mat")

        initial_count = pdp_page.get_cart_count()
        assert initial_count == 0, f"Expected clean initial cart count (0), got {initial_count}"

        pdp_page.click_add_to_cart()

        assert pdp_page.is_product_added_to_cart(timeout=8000), (
            "Product addition confirmation message or cart counter update failed."
        )

        updated_count = pdp_page.get_cart_count()
        assert updated_count >= 1, f"Expected cart count >= 1 after adding product, found {updated_count}"
        logger.info(f"Cart count successfully updated from {initial_count} to {updated_count}.")

        # Intentional validated evidence capture
        pdp_page.prepare_for_pdp_evidence()
        pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-PDP-007 completed successfully.")

    @pytest.mark.functional
    def test_e2e_pdp_008_attempt_purchase_unavailable_product(
        self,
        pdp_page: PdpPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-PDP-008: Attempt Purchase Unavailable Product.

        Steps:
        1. Open target out-of-stock product PDP (Silhouette Alta Platform Tape).
        2. Verify product displays 'Out Of Stock' / unavailable state badge dynamically.
        3. Extract dynamic stock status label text and assert unavailable indicator.
        4. Assert Add to Cart purchase button is not available or disabled.
        5. Capture evidence screenshot and video for test verification.
        """
        logger.info("Executing E2E-PDP-008: Attempt Purchase Unavailable Product.")
        # Target verified out-of-stock item: Silhouette Alta Platform Tape
        pdp_page.open_pdp("alta-platform-tape")

        assert pdp_page.is_out_of_stock(), (
            "Expected product to display out-of-stock / unavailable state badge."
        )
        status_text = pdp_page.get_stock_status_text()
        logger.info(f"Verified out-of-stock badge text: '{status_text}'")
        assert "out of stock" in status_text.lower() or "unavailable" in status_text.lower(), (
            f"Unexpected stock status badge text: '{status_text}'"
        )

        assert not pdp_page.is_add_to_cart_available(), (
            "Add to Cart button is unexpectedly available and enabled for an out-of-stock product."
        )

        # Intentional validated evidence capture
        pdp_page.prepare_for_pdp_evidence()
        pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-PDP-008 completed successfully.")

    @pytest.mark.functional
    def test_e2e_pdp_009_add_boundary_quantity(self, pdp_page: PdpPage, request: pytest.FixtureRequest) -> None:
        """E2E-PDP-009: Verify minimum and maximum boundary quantity enforcement on PDP."""
        logger.info("Executing E2E-PDP-009: Add Boundary Quantity (Min/Max).")

        # 1. Open PDP: loads page, resolves Cloudflare challenge, detects cookie popup, clicks 'I Agree', and stabilizes
        pdp_page.open_pdp("cameo-mat")

        # Ensure cookie popup is completely dismissed and PDP is stable before starting quantity steps
        pdp_page.dismiss_cookie_consent_if_present(timeout=5000)
        pdp_page.wait_for_timeout(1000)

        # Scroll quantity controls into view so interactions and errors are clearly visible in video
        pdp_page.scroll_quantity_into_view()
        pdp_page.wait_for_timeout(500)

        # =========================================================================
        # 2. Minimum Boundary Validation
        # =========================================================================
        logger.info("--- Starting Minimum Boundary Validation ---")
        initial_qty = pdp_page.get_quantity()
        assert initial_qty == 1, f"Expected default quantity of 1, got: {initial_qty}"

        # Minimum limit: decrement button when at 1 must not drop below 1
        qty_after_minus = pdp_page.decrement_quantity()
        assert qty_after_minus == 1, (
            f"Quantity allowed decrementing below minimum (1), got: {qty_after_minus}"
        )
        logger.info("Verified minimum quantity enforcement: decrease button maintains 1.")

        # Test incrementing quantity to 2
        qty_after_plus = pdp_page.increment_quantity()
        assert qty_after_plus == 2, f"Expected quantity to increase to 2, got: {qty_after_plus}"
        logger.info("Verified quantity increment button increases value to 2.")

        # Decrement back to 1
        qty_restored = pdp_page.decrement_quantity()
        assert qty_restored == 1, f"Expected quantity restored to 1, got: {qty_restored}"

        # Verify boundary validation rules from application data-validate attribute
        rules = pdp_page.get_quantity_validation_rules()
        assert rules["min_allowed"] == 1, f"Expected minAllowed=1 in validation rules, got: {rules.get('min_allowed')}"
        assert rules["max_allowed"] == 10000, f"Expected maxAllowed=10000 in validation rules, got: {rules.get('max_allowed')}"

        # Trigger minimum boundary violation (zero quantity)
        zero_error = pdp_page.trigger_quantity_validation_with_zero()
        pdp_page.wait_for_timeout(1500)  # Pause so video clearly captures zero error state
        assert "greater than 0" in zero_error.lower(), (
            f"Expected 'Please enter a quantity greater than 0.' error for 0 quantity, got: '{zero_error}'"
        )
        logger.info(f"Verified minimum boundary violation message: '{zero_error}'")

        # Capture evidence screenshot for minimum boundary check (showing 0 and error)
        pdp_page.capture_evidence_screenshot(request.node.name, custom_suffix="min_boundary")

        # =========================================================================
        # 3. Maximum Boundary Validation
        # =========================================================================
        logger.info("--- Starting Maximum Boundary Validation ---")
        # Test valid maximum boundary (10000)
        pdp_page.set_quantity(10000)
        pdp_page.wait_for_timeout(1500)  # Pause so video clearly captures 10000 accepted in input
        qty_at_max = pdp_page.get_quantity()
        assert qty_at_max == 10000, f"Expected quantity to be set to 10000, got: {qty_at_max}"
        max_error_at_10000 = pdp_page.get_quantity_error_text()
        assert max_error_at_10000 == "", (
            f"Unexpected error for valid maximum quantity (10000): '{max_error_at_10000}'"
        )
        logger.info("Verified valid maximum boundary quantity (10000) is accepted without error.")

        # Test exceeding maximum boundary (10001)
        exceeded_error = pdp_page.trigger_quantity_validation(10001)
        pdp_page.wait_for_timeout(1500)  # Pause so video clearly captures exceeded error state
        assert len(exceeded_error) > 0, "Expected validation error when exceeding maximum quantity (10001)."
        assert "maximum" in exceeded_error.lower() and "10000" in exceeded_error, (
            f"Expected 'The maximum you may purchase is 10000.' error, got: '{exceeded_error}'"
        )
        logger.info(f"Verified exceeded maximum boundary error message: '{exceeded_error}'")

        # Capture evidence screenshot for maximum boundary check (showing 10001 and error)
        pdp_page.capture_evidence_screenshot(request.node.name, custom_suffix="max_boundary")

        # =========================================================================
        # 4. Final Evidence
        # =========================================================================
        # Capture primary test evidence screenshot
        pdp_page.prepare_for_pdp_evidence()
        pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-PDP-009 completed successfully.")

    @pytest.mark.functional
    def test_e2e_pdp_010_refresh_pdp_after_selecting_options(
        self,
        pdp_page: PdpPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-PDP-010: Refresh PDP after selecting options and verify application behavior."""
        logger.info("Executing E2E-PDP-010: Refresh PDP After Selecting Options.")
        pdp_page.open_pdp("cameo-mat")

        initial_selected = pdp_page.get_selected_variants()
        logger.info(f"Initial default variants: {initial_selected}")

        target_variant = '12" x 24"'
        pdp_page.select_variant(target_variant)
        selected_after_click = pdp_page.get_selected_variants()
        assert any(target_variant in s for s in selected_after_click), (
            f"Target variant '{target_variant}' was not selected."
        )
        logger.info(f"Variant selected prior to refresh: {selected_after_click}")

        # Refresh the page
        pdp_page.reload()
        pdp_page.wait_for_dom_content_loaded()
        pdp_page.dismiss_cookie_consent_if_present()
        pdp_page.wait_for_timeout(1500)

        # Verify application behavior upon refresh
        selected_after_refresh = pdp_page.get_selected_variants()
        logger.info(f"Observed variant state after refresh: {selected_after_refresh}")

        # The application resets to default initial variant state upon reload (verified behavior)
        assert pdp_page.is_pdp_loaded(), "PDP failed to reload stably after refresh."
        assert len(selected_after_refresh) > 0, "No variant selected after refresh."
        assert initial_selected == selected_after_refresh, (
            f"Expected option to reset to default state {initial_selected}, got: {selected_after_refresh}"
        )
        logger.info(
            f"Verified reload behavior: Variant selection reset to default initial state {initial_selected}."
        )

        # Intentional validated evidence capture
        pdp_page.prepare_for_pdp_evidence()
        pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-PDP-010 completed successfully.")
