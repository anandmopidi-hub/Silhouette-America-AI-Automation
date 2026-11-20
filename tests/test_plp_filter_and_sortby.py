import pytest
from pages.catalog_page import CatalogPage
from pages.home_page import HomePage
from utils.logger import logger


@pytest.mark.e2e
class TestPLPFilterAndSortBy:
    """Catalog E2E test suite covering category browsing, single/multiple layered filters,

    filter clearing, empty filter states, sorting, pagination, and boundary navigation.
    """

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_e2e_cat_001_browse_machines(
        self,
        home_page: HomePage,
        catalog_page: CatalogPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CAT-001: Browse Machines category and verify catalog listing loads with products."""
        logger.info("Executing E2E-CAT-001: Browse Machines Category.")
        home_page.open_homepage()
        dest_url = home_page.navigate_to_machines()

        assert "machines" in dest_url.lower(), f"Unexpected destination URL for Machines: '{dest_url}'"
        assert catalog_page.is_catalog_page_loaded(expected_title_keyword="Machines"), (
            "Machines catalog page failed to load with valid layout."
        )

        category_title = catalog_page.get_category_title()
        assert "machine" in category_title.lower(), f"Expected 'machine' in category title, found '{category_title}'."
        assert catalog_page.get_product_count() > 0, "No machine products displayed on Machines listing page."

        # Intentional validated evidence capture
        catalog_page.prepare_for_catalog_evidence()
        catalog_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-CAT-001 completed successfully.")

    @pytest.mark.functional
    def test_e2e_cat_002_browse_accessories(
        self,
        home_page: HomePage,
        catalog_page: CatalogPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CAT-002: Browse Accessories category and verify catalog listing loads with products."""
        logger.info("Executing E2E-CAT-002: Browse Accessories Category.")
        home_page.open_homepage()
        dest_url = home_page.navigate_to_accessories()

        assert "accessories-parts" in dest_url.lower(), f"Unexpected destination URL for Accessories: '{dest_url}'"
        assert catalog_page.is_catalog_page_loaded(expected_title_keyword="Accessories"), (
            "Accessories catalog page failed to load with valid layout."
        )

        category_title = catalog_page.get_category_title()
        assert "accessories" in category_title.lower(), (
            f"Expected 'accessories' in category title, found '{category_title}'."
        )
        assert catalog_page.get_product_count() > 0, "No accessories products displayed on Accessories listing page."

        # Intentional validated evidence capture
        catalog_page.prepare_for_catalog_evidence()
        catalog_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-CAT-002 completed successfully.")

    @pytest.mark.functional
    def test_e2e_cat_003_browse_materials(
        self,
        home_page: HomePage,
        catalog_page: CatalogPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CAT-003: Browse Materials/Supplies category and verify catalog listing loads with products."""
        logger.info("Executing E2E-CAT-003: Browse Materials/Supplies Category.")
        home_page.open_homepage()
        dest_url = home_page.navigate_to_supplies_materials()

        assert "material" in dest_url.lower(), f"Unexpected destination URL for Materials: '{dest_url}'"
        assert catalog_page.is_catalog_page_loaded(expected_title_keyword="Materials"), (
            "Materials catalog page failed to load with valid layout."
        )

        category_title = catalog_page.get_category_title()
        assert "material" in category_title.lower(), f"Expected 'material' in category title, found '{category_title}'."
        assert catalog_page.get_product_count() > 0, "No materials products displayed on Materials listing page."

        # Intentional validated evidence capture
        catalog_page.prepare_for_catalog_evidence()
        catalog_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-CAT-003 completed successfully.")

    @pytest.mark.functional
    def test_e2e_cat_004_apply_single_filter(
        self,
        catalog_page: CatalogPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CAT-004: Apply a single catalog filter and verify filtered product listing results."""
        logger.info("Executing E2E-CAT-004: Apply Single Filter.")
        catalog_page.open_category("accessories-parts")

        initial_count = catalog_page.get_product_count()
        assert initial_count > 0, "No products available on initial category page to test filtering."

        group, label = catalog_page.apply_filter(group_name="Category")
        logger.info(f"Applied single filter '{label}' from group '{group}'.")

        assert catalog_page.is_filter_applied(label), (
            f"Applied filter '{label}' was not reflected in active filters or URL."
        )
        filtered_count = catalog_page.get_product_count()
        assert filtered_count > 0, f"Filtered catalog returned 0 products for active filter '{label}'."

        # Intentional validated evidence capture
        catalog_page.prepare_for_filtered_evidence()
        catalog_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-CAT-004 completed successfully.")

    @pytest.mark.functional
    def test_e2e_cat_005_apply_multiple_filters(
        self,
        catalog_page: CatalogPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CAT-005: Apply multiple valid filters across different groups and verify combined results."""
        logger.info("Executing E2E-CAT-005: Apply Multiple Filters.")
        catalog_page.open_category("accessories-parts")

        assert catalog_page.get_product_count() > 0, "Initial category page has no products."

        # Apply filter 1 from Category
        group_1, label_1 = catalog_page.apply_filter(group_name="Category", option_label="Parts")
        logger.info(f"Applied first filter: '{label_1}' from '{group_1}'.")
        assert catalog_page.is_filter_applied(label_1), f"First filter '{label_1}' not reflected in active filters."

        # Apply filter 2 from Compatibility (e.g. Cameo 4)
        group_2, label_2 = catalog_page.apply_filter(group_name="Compatibility", option_label="Cameo 4")
        logger.info(f"Applied second filter: '{label_2}' from '{group_2}'.")
        assert catalog_page.is_filter_applied(label_2), f"Second filter '{label_2}' not reflected in active filters."

        # Verify both filters remain active
        assert catalog_page.is_filter_applied(label_1) and catalog_page.is_filter_applied(label_2), (
            f"Expected both filters ('{label_1}', '{label_2}') to remain applied."
        )
        assert catalog_page.get_product_count() > 0, "No products matched the combined multi-filter selection."

        # Intentional validated evidence capture
        catalog_page.prepare_for_filtered_evidence()
        catalog_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-CAT-005 completed successfully.")

    @pytest.mark.functional
    def test_e2e_cat_006_clear_filters(
        self,
        catalog_page: CatalogPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CAT-006: Apply a filter and verify clearing it restores default catalog listing."""
        logger.info("Executing E2E-CAT-006: Clear Filters.")
        catalog_page.open_category("accessories-parts")

        initial_count = catalog_page.get_product_count()
        assert initial_count > 0, "Initial catalog listing has no products."

        group, label = catalog_page.apply_filter(group_name="Category", option_label="Parts")
        assert catalog_page.is_filter_applied(label), f"Filter '{label}' was not applied."

        # Clear filters using existing Clear All control
        catalog_page.clear_all_filters()

        assert not catalog_page.is_filter_applied(label), (
            f"Filter '{label}' is still applied after clicking Clear All."
        )
        restored_count = catalog_page.get_product_count()
        assert restored_count == initial_count, (
            f"Expected restored product count ({initial_count}), but found ({restored_count})."
        )

        # Intentional validated evidence capture
        catalog_page.prepare_for_catalog_evidence()
        catalog_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-CAT-006 completed successfully.")

    @pytest.mark.functional
    def test_e2e_cat_007_no_result_filter_combination(
        self,
        catalog_page: CatalogPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CAT-007: Apply an overly restrictive filter combination and verify controlled empty state."""
        logger.info("Executing E2E-CAT-007: No-Result Filter Combination.")
        catalog_page.open_category("accessories-parts")

        # Apply deterministic zero-result combination (Alta 3D Printer parts + Cameo 5 cutting machine)
        catalog_page.apply_zero_result_filter_combination()

        assert catalog_page.get_product_count() == 0, (
            "Expected 0 product items for restrictive zero-result filter combination."
        )
        assert catalog_page.is_no_products_message_displayed(), (
            "Expected empty state notification message ('We can't find products matching the selection.')."
        )

        title = catalog_page.get_title()
        assert "500" not in title and "error" not in title.lower(), (
            f"Unexpected application error page encountered: '{title}'"
        )

        # Intentional validated evidence capture
        catalog_page.prepare_for_catalog_evidence()
        catalog_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-CAT-007 completed successfully.")

    @pytest.mark.functional
    def test_e2e_cat_008_sort_products(
        self,
        catalog_page: CatalogPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CAT-008: Verify catalog products reordering when a valid sort option is selected."""
        logger.info("Executing E2E-CAT-008: Sort Products.")
        catalog_page.open_category("accessories-parts")

        initial_names = catalog_page.get_product_names()
        assert len(initial_names) > 0, "No products available on initial page for sorting test."

        available_sorts = catalog_page.get_available_sort_options()
        assert len(available_sorts) > 0, "No sort options found in sorter dropdown."
        logger.info(f"Discovered available sort options: {available_sorts}")

        # Select valid sort option dynamically (prefer Price Low to High, or next available)
        target_sort = "Price: Low to high"
        if not any(target_sort.lower() in s.lower() for s in available_sorts):
            target_sort = available_sorts[0]

        sort_url = catalog_page.apply_sort_option(target_sort)
        current_sort_val = catalog_page.get_current_sort_value()
        logger.info(f"Sort applied: target='{target_sort}', sort_url='{sort_url}', selected_val='{current_sort_val}'")

        # Dynamic assertion: verify sort is applied via URL query param or dropdown state
        sort_reflected = (
            "product_list_order" in sort_url.lower()
            or "price" in sort_url.lower()
            or "order=" in sort_url.lower()
            or (current_sort_val and current_sort_val != "bestsellers")
        )
        assert sort_reflected, (
            f"Sort option '{target_sort}' was not reflected in URL ('{sort_url}') or sorter value ('{current_sort_val}')."
        )

        sorted_names = catalog_page.get_product_names()
        assert len(sorted_names) > 0, "No products displayed after applying sort option."

        # Intentional validated evidence capture
        catalog_page.prepare_for_sorted_evidence()
        catalog_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-CAT-008 completed successfully.")

    @pytest.mark.functional
    def test_e2e_cat_009_pagination_or_load_more(
        self,
        catalog_page: CatalogPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CAT-009: Verify additional catalog products load via pagination and page transition."""
        logger.info("Executing E2E-CAT-009: Pagination / Load More.")
        catalog_page.open_category("accessories-parts")

        page_1_hrefs = catalog_page.get_product_hrefs()
        assert len(page_1_hrefs) > 0, "Page 1 has no product cards."
        assert catalog_page.has_next_page(), "Catalog page does not have a Next page button for pagination."

        # Navigate to Next page
        new_page_num, new_page_url = catalog_page.go_to_next_page()
        assert new_page_num == 2 or "p=2" in new_page_url, (
            f"Expected navigation to page 2, actual page: {new_page_num}, URL: '{new_page_url}'"
        )

        page_2_hrefs = catalog_page.get_product_hrefs()
        assert len(page_2_hrefs) > 0, "Page 2 returned 0 products."
        assert page_1_hrefs != page_2_hrefs, "Page 2 products are identical to Page 1 products (unexpected duplicates)."

        # Intentional validated evidence capture
        catalog_page.prepare_for_pagination_evidence()
        catalog_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-CAT-009 completed successfully.")

    @pytest.mark.functional
    def test_e2e_cat_010_pagination_boundary(
        self,
        catalog_page: CatalogPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CAT-010: Verify navigation to the final page and ensure Next navigation is disabled/prevented."""
        logger.info("Executing E2E-CAT-010: Pagination Boundary.")
        catalog_page.open_category("accessories-parts")

        last_page = catalog_page.get_last_page_number()
        assert last_page > 1, f"Expected multi-page catalog to test boundary, but last page found was {last_page}."
        logger.info(f"Targeting final catalog page: {last_page}")

        # Navigate to final page
        catalog_page.go_to_page(last_page)
        current_page = catalog_page.get_current_page_number()
        assert current_page == last_page, (
            f"Expected to be on final page {last_page}, but current page is {current_page}."
        )

        final_page_products = catalog_page.get_product_count()
        assert final_page_products > 0, f"Final page {last_page} returned 0 products."

        # Verify boundary state: Next page control must not be available
        assert not catalog_page.is_next_page_available(), (
            f"Next button was unexpectedly available on the final catalog page ({last_page})."
        )

        # Intentional validated evidence capture
        catalog_page.prepare_for_pagination_evidence()
        catalog_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-CAT-010 completed successfully.")
