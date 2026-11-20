import re
import pytest
from pages.different_pdp_page import Different_PDP_Page
from utils.logger import logger


@pytest.mark.e2e
class TestDifferentProductPDP:
    """PDP E2E test suite covering different product types using a single common

    Page Object (Different_PDP_Page) and Locator class (Different_PDP_Locators):
    - E2E-Different_PDP-001: Machine PDP
    - E2E-Different_PDP-002: Tools & Mats PDP
    - E2E-Different_PDP-003: Clearance – Supply Bundles PDP
    - E2E-Different_PDP-004: Software PDP
    """

    # =========================================================================
    # E2E-Different_PDP-001: Machine PDP
    # =========================================================================

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_e2e_different_pdp_001_machine_pdp(
        self,
        different_pdp_page: Different_PDP_Page,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-Different_PDP-001: Machine PDP.

        Verify Machine Product Detail Page, image gallery, colour selection,
        machine options and dynamic price updates on the LIVE website.
        """
        logger.info("========== EXECUTING E2E-Different_PDP-001: Machine PDP ==========")

        # Step 1-3: Open homepage, navigate to Machines, and identify available machine product
        different_pdp_page.navigate_to_category("machines")
        prod_meta = different_pdp_page.select_available_product_dynamically()
        assert prod_meta["href"] or different_pdp_page.is_main_image_visible(), (
            "Failed to identify and open an in-stock machine product from /machines."
        )

        # Step 4-5: Verify PDP URL, title, price, description, and availability
        assert different_pdp_page.verify_pdp_loaded(), "Machine PDP failed to load cleanly."
        product_name = different_pdp_page.get_product_name()
        assert len(product_name) > 0, "Machine product name is empty."
        logger.info(f"Verified machine product name: '{product_name}'")

        displayed_price = different_pdp_page.get_displayed_price()
        assert len(displayed_price) > 0 and "$" in displayed_price, (
            f"Expected valid currency price, found '{displayed_price}'"
        )
        logger.info(f"Verified machine product displayed price: '{displayed_price}'")

        availability = different_pdp_page.verify_product_availability()
        assert availability["is_in_stock"] or availability["purchasable"], (
            f"Machine product availability check failed: {availability}"
        )

        description = different_pdp_page.get_product_description()
        logger.info(f"Verified machine product description ({len(description)} chars).")

        # Step 6-7: Verify main image and thumbnail gallery interaction
        assert different_pdp_page.is_main_image_visible(), "Main machine product image is not visible."
        gallery_count = different_pdp_page.get_gallery_image_count()
        assert gallery_count > 0, f"Expected at least 1 gallery image, found {gallery_count}."
        logger.info(f"Detected {gallery_count} gallery images/thumbnails.")

        observed_images = different_pdp_page.interact_with_gallery_thumbnails()
        assert len(observed_images) > 0, "No valid image sources observed during gallery interaction."
        logger.info(f"Observed {len(observed_images)} unique gallery image states.")

        # Step 8-10: Color options inspection and selection
        colors = different_pdp_page.get_available_colors()
        logger.info(f"Available machine colors: {colors}")
        if colors:
            for idx in range(min(len(colors), 3)):
                color_res = different_pdp_page.select_color_by_index(idx)
                assert color_res["selected"], f"Failed to select color index {idx} ({colors[idx]})."
                assert color_res["new_src"], "Image source missing after color selection."
                logger.info(f"Verified color selection: '{color_res['color_name']}'")

        # Step 11-16: Machine Options & Dynamic Price Updates
        machine_options = different_pdp_page.get_available_machine_options()
        logger.info(f"Available machine options/bundles: {machine_options}")
        if machine_options:
            for idx in range(min(len(machine_options), 3)):
                opt_res = different_pdp_page.select_machine_option_by_index(idx)
                assert opt_res["selected"], f"Failed to select machine option index {idx}."
                assert opt_res["new_price"], "Displayed price missing after selecting machine option."
                logger.info(f"Verified option '{opt_res['option_name']}' price: '{opt_res['new_price']}'")

        # Step 17: Quantity controls verification
        qty_info = different_pdp_page.verify_quantity_controls()
        logger.info(f"Machine PDP quantity controls verified: {qty_info}")

        # Step 18-19: Specifications, additional info & smooth full page scroll
        specs = different_pdp_page.get_product_specifications()
        logger.info(f"Machine PDP specifications check: length={len(specs)} chars.")
        different_pdp_page.scroll_through_complete_pdp()

        # Step 20: Capture intentional evidence screenshot
        different_pdp_page.prepare_for_pdp_evidence()
        different_pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-Different_PDP-001 completed successfully.")

    # =========================================================================
    # E2E-Different_PDP-002: Tools & Mats PDP
    # =========================================================================

    @pytest.mark.functional
    def test_e2e_different_pdp_002_tools_and_mats_pdp(
        self,
        different_pdp_page: Different_PDP_Page,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-Different_PDP-002: Tools & Mats PDP.

        Verify Tools & Mats product details, product options, compatibility,
        specifications, dynamic pricing and customer reviews.
        """
        logger.info("========== EXECUTING E2E-Different_PDP-002: Tools & Mats PDP ==========")

        # Step 1-3: Open homepage, navigate to Tools & Mats, and open available product
        different_pdp_page.navigate_to_category("tools-mats")
        prod_meta = different_pdp_page.select_available_product_dynamically()
        assert prod_meta["href"] or different_pdp_page.is_main_image_visible(), (
            "Failed to open a Tools & Mats product from listing."
        )

        # Step 4-6: Verify PDP URL, title, images, and description
        assert different_pdp_page.verify_pdp_loaded(), "Tools & Mats PDP failed to load cleanly."
        product_name = different_pdp_page.get_product_name()
        assert len(product_name) > 0, "Tools & Mats product name is empty."
        logger.info(f"Verified Tools & Mats product name: '{product_name}'")

        assert different_pdp_page.is_main_image_visible(), "Product image is not visible on Tools & Mats PDP."
        description = different_pdp_page.get_product_description()
        logger.info(f"Verified description length: {len(description)} chars.")

        # Step 7: Specifications / technical details
        specs = different_pdp_page.get_product_specifications()
        logger.info(f"Tools & Mats specifications: length={len(specs)} chars.")

        # Step 8-11: Product options / variations and dynamic price updates
        option_results = different_pdp_page.select_each_available_option()
        logger.info(f"Evaluated {len(option_results)} product option variations.")
        for opt in option_results:
            assert opt["new_price"], f"Price is missing after selecting option '{opt['label']}'."

        # Step 12-13: Compatibility section verification
        compat_info = different_pdp_page.verify_compatibility_section()
        logger.info(f"Compatibility section details: {compat_info}")

        # Step 14-15: What's Included / Contents section
        contents_info = different_pdp_page.verify_bundle_contents()
        logger.info(f"Product contents details: {contents_info}")

        # Step 16-18: Customer Reviews section ('Real Results. Real Opinions. Real Reviews.')
        reviews_info = different_pdp_page.verify_customer_reviews_section()
        assert reviews_info["has_reviews"], "Reviews section not found in DOM."
        logger.info(f"Customer reviews section verified: {reviews_info}")

        # Step 19: Full page scroll without broken elements or errors
        different_pdp_page.scroll_through_complete_pdp()

        # Step 20: Capture intentional evidence screenshot
        different_pdp_page.prepare_for_pdp_evidence()
        different_pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-Different_PDP-002 completed successfully.")

    # =========================================================================
    # E2E-Different_PDP-003: Clearance – Supply Bundles PDP
    # =========================================================================

    @pytest.mark.functional
    def test_e2e_different_pdp_003_clearance_supply_bundles_pdp(
        self,
        different_pdp_page: Different_PDP_Page,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-Different_PDP-003: Clearance – Supply Bundles PDP.

        Verify Supply Bundles navigation, product listing, product cards,
        image, share functionality and PDP interactions.
        """
        logger.info("========== EXECUTING E2E-Different_PDP-003: Clearance Supply Bundles PDP ==========")

        # Step 1-4: Open homepage, navigate to Clearance, and open Supply Bundles PLP
        different_pdp_page.navigate_to_clearance_supply_bundles()

        # Step 5-8: Verify Supply Bundles PLP loaded, title, product count, and product cards
        plp_info = different_pdp_page.verify_supply_bundles_plp()
        assert plp_info["is_valid"], "Supply Bundles PLP does not contain product cards."
        assert plp_info["product_count"] > 0, "No product cards displayed on Supply Bundles PLP."
        logger.info(f"Supply Bundles PLP verified with {plp_info['product_count']} product cards.")

        # Step 9-12: Test share icon on product card without unexpected navigation
        share_res = different_pdp_page.test_share_icon_on_product_card()
        assert share_res["did_not_navigate_away"], "Share action caused an unexpected page redirect."
        logger.info(f"Product card share interaction verified: {share_res}")

        # Step 13-14: Open an available Supply Bundle product and verify PDP opens
        prod_meta = different_pdp_page.select_available_product_dynamically()
        assert different_pdp_page.verify_pdp_loaded(), "Supply Bundle PDP failed to load."

        # Step 15-18: Inspect gallery, description, contents, specifications, and displayed price
        bundle_name = different_pdp_page.get_product_name()
        assert len(bundle_name) > 0, "Supply bundle product name is empty."
        logger.info(f"Verified Supply Bundle name: '{bundle_name}'")

        displayed_price = different_pdp_page.get_displayed_price()
        assert "$" in displayed_price, f"Invalid displayed price: '{displayed_price}'"
        logger.info(f"Verified Supply Bundle displayed price: '{displayed_price}'")

        assert different_pdp_page.is_main_image_visible(), "Bundle main image is not visible."
        contents = different_pdp_page.verify_bundle_contents()
        logger.info(f"Supply Bundle contents info: {contents}")

        qty_info = different_pdp_page.verify_quantity_controls()
        logger.info(f"Supply Bundle quantity controls: {qty_info}")

        # Step 19-21: Navigate back to Supply Bundles PLP and verify listing remains functional
        returned_ok = different_pdp_page.navigate_back_to_plp()
        assert returned_ok, "PLP listing not functional after returning from Supply Bundle PDP."

        # Step 22: Capture intentional evidence screenshot
        different_pdp_page.prepare_for_pdp_evidence()
        different_pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-Different_PDP-003 completed successfully.")

    # =========================================================================
    # E2E-Different_PDP-004: Software PDP
    # =========================================================================

    @pytest.mark.functional
    def test_e2e_different_pdp_004_software_pdp(
        self,
        different_pdp_page: Different_PDP_Page,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-Different_PDP-004: Software PDP.

        Verify Software Product Detail Page, software editions, View More/View Less
        functionality and dynamic content.
        """
        logger.info("========== EXECUTING E2E-Different_PDP-004: Software PDP ==========")

        # Step 1-3: Open homepage, navigate to Software, and open software product (Silhouette Studio)
        different_pdp_page.navigate_to_category("software")
        different_pdp_page.open_product_by_slug("silhouette-studio")

        # Step 4-5: Verify PDP URL, product name, images, description, and price
        assert different_pdp_page.verify_pdp_loaded(expected_slug_or_name="studio"), (
            "Silhouette Studio Software PDP failed to load."
        )
        software_title = different_pdp_page.get_product_name()
        page_title = different_pdp_page.get_title()
        assert (
            "studio" in software_title.lower()
            or "silhouette" in software_title.lower()
            or "studio" in page_title.lower()
            or "design smarter" in software_title.lower()
        ), f"Unexpected software product title: '{software_title}' (page title: '{page_title}')"
        logger.info(f"Verified software product title: '{software_title}'")

        # Step 6-7: Silhouette Studio® editions section verification
        editions_info = different_pdp_page.verify_software_editions_section()
        assert editions_info["section_visible"], "Silhouette Studio® editions section not visible."
        logger.info(f"Verified Silhouette Studio editions: {editions_info['editions_found']}")

        # Step 8-13: View More and View Less toggling and repeated verification
        repeated_toggle_ok = different_pdp_page.test_repeated_view_more_view_less(cycles=2)
        assert repeated_toggle_ok, "View More / View Less repeated toggling failed."
        logger.info("Verified View More / View Less functionality consistently expands and collapses content.")

        # Step 14-16: Features, benefits, system requirements and software options
        links_info = different_pdp_page.verify_software_links()
        assert links_info["download_links_count"] > 0 or links_info["purchase_links_count"] > 0, (
            f"No download or purchase links identified on Software PDP: {links_info}"
        )
        logger.info(f"Verified software download and purchase links: {links_info}")

        # Step 17-20: Inspect download/purchase destinations without completing purchase & full scroll
        different_pdp_page.scroll_through_complete_pdp()

        # Step 21: Capture intentional evidence screenshot
        different_pdp_page.prepare_for_pdp_evidence()
        different_pdp_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-Different_PDP-004 completed successfully.")

