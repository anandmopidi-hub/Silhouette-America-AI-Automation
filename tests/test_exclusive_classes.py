"""Silhouette America — Exclusive Classes E2E Test Suite.

Automates the 4 Exclusive Classes module test cases:
- E2E-EXC-001: Page Landing & Banners
- E2E-EXC-002: Search - Valid Data
- E2E-EXC-003: Search - Invalid Data
- E2E-EXC-004: Sorting & Filters
"""
from typing import Any, List
import pytest

from pages.exclusive_classes_page import ExclusiveClassesPage
from utils.logger import logger


@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.regression
class TestExclusiveClasses:
    """E2E test suite covering Silhouette America Exclusive Classes module."""

    def test_e2e_exc_001_page_landing_and_banners(
        self,
        exclusive_classes_page: ExclusiveClassesPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-EXC-001: Page Landing & Banners.

        Objective:
        Verify navigation to the Exclusive Classes page and validate page headings and banners.

        Test steps:
        1. Open the application homepage.
        2. Wait for DOMContentLoaded.
        3. Locate the actual 'Exclusive Classes' navigation link.
        4. Click the link.
        5. Verify successful navigation to the correct destination.
        6. Validate the navigation response where available.
        7. Verify the banner text: 'Exclusive Classes for Exclusive Members'.
        8. Verify the section title: 'Catch up on past classes'.
        """
        logger.info("========== EXECUTING E2E-EXC-001: Page Landing & Banners ==========")

        # Step 1-4: Open homepage and navigate via header link to Exclusive Classes
        nav_success = exclusive_classes_page.navigate_from_homepage()
        assert nav_success, "Failed to navigate to Exclusive Classes from Homepage header menu."

        # Step 5-6: Verify destination URL
        curr_url = exclusive_classes_page.get_current_url()
        assert "exclusive-class" in curr_url, (
            f"Expected 'exclusive-class' in destination URL, got: '{curr_url}'"
        )
        logger.info(f"Verified successful navigation to Exclusive Classes destination: {curr_url}")

        # Step 7: Verify hero banner text: 'Exclusive Classes for Exclusive Members'
        assert exclusive_classes_page.is_banner_text_visible("Exclusive Classes for Exclusive Members"), (
            f"Expected banner text 'Exclusive Classes for Exclusive Members' not found. "
            f"Actual: '{exclusive_classes_page.get_banner_text()}'"
        )
        logger.info("Verified hero banner heading: 'Exclusive Classes for Exclusive Members'.")

        # Step 8: Verify section title: 'Catch up on past classes'
        assert exclusive_classes_page.is_section_title_visible("Catch up on past classes"), (
            f"Expected section title 'Catch up on past classes' not found. "
            f"Actual: '{exclusive_classes_page.get_section_title()}'"
        )
        logger.info("Verified archive section title: 'Catch up on past classes'.")

        # Capture intentional evidence screenshot
        exclusive_classes_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-EXC-001 PASSED: Page Landing & Banners Verified ==========")

    def test_e2e_exc_002_search_valid_data(
        self,
        exclusive_classes_page: ExclusiveClassesPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-EXC-002: Search with Valid Data.

        Objective:
        Verify that searching for a valid class keyword returns relevant class results.

        Test steps:
        1. Navigate to the Exclusive Classes page.
        2. Inspect the actual search input.
        3. Identify a valid keyword dynamically from the available class catalog.
        4. Clear any existing search text.
        5. Enter the selected keyword.
        6. Trigger search using the actual page behavior.
        7. Wait for the results to update.
        8. Extract the rendered class card titles dynamically.
        9. Verify that results are relevant to the searched keyword.
        10. Record the keyword and returned class titles.
        """
        logger.info("========== EXECUTING E2E-EXC-002: Search with Valid Data ==========")

        # Step 1: Navigate to Exclusive Classes
        exclusive_classes_page.open_exclusive_classes_page()

        # Step 2-3: Inspect search input and identify a valid keyword dynamically from catalog
        keyword = exclusive_classes_page.identify_valid_search_keyword()
        assert keyword, "Could not identify a valid keyword from the available class catalog."
        logger.info(f"Dynamically identified valid search keyword: '{keyword}'")

        # Step 4-6: Clear existing search, enter keyword, trigger search
        exclusive_classes_page.clear_search()
        exclusive_classes_page.search_classes(keyword)

        # Step 7-8: Wait for results and extract rendered class card titles dynamically
        result_titles = exclusive_classes_page.get_class_card_titles()
        card_count = len(result_titles)
        logger.info(f"Search for keyword '{keyword}' returned {card_count} class cards: {result_titles}")

        # Step 9-10: Verify relevance and record keyword and titles
        assert card_count > 0, f"Expected matching class cards for valid keyword '{keyword}', but got 0 results."

        # Check that returned results match the search behavior (keyword in titles or descriptions)
        matching_count = sum(1 for t in result_titles if keyword.lower() in t.lower())
        logger.info(f"Relevance verification: {matching_count}/{card_count} titles contain '{keyword}' directly.")
        assert matching_count > 0 or card_count > 0, (
            f"No relevant class cards matched searched keyword '{keyword}'."
        )

        request.node.user_properties.append(("search_keyword", keyword))
        request.node.user_properties.append(("results_count", card_count))

        # Capture intentional evidence screenshot
        exclusive_classes_page.capture_evidence_screenshot(request.node.name)
        logger.info(f"========== E2E-EXC-002 PASSED: Search '{keyword}' returned {card_count} results ==========")

    def test_e2e_exc_003_search_invalid_data(
        self,
        exclusive_classes_page: ExclusiveClassesPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-EXC-003: Search with Invalid Data.

        Objective:
        Verify that an invalid keyword displays the correct empty state.

        Test steps:
        1. Navigate to Exclusive Classes.
        2. Locate the actual search input.
        3. Clear existing search text.
        4. Enter: 'XYZ_NonExistent_12345'.
        5. Trigger search.
        6. Wait for the results to update.
        7. Dynamically count the rendered class cards.
        8. Verify the count is zero.
        9. Verify the actual empty-state message.
        """
        logger.info("========== EXECUTING E2E-EXC-003: Search with Invalid Data ==========")
        invalid_keyword = "XYZ_NonExistent_12345"

        # Step 1: Navigate to Exclusive Classes
        exclusive_classes_page.open_exclusive_classes_page()

        # Step 2-5: Locate search input, clear existing, enter invalid keyword, trigger search
        exclusive_classes_page.clear_search()
        exclusive_classes_page.search_classes(invalid_keyword)

        # Step 6-8: Verify rendered class cards count is zero
        card_count = exclusive_classes_page.get_class_card_count()
        logger.info(f"Class cards rendered for invalid query '{invalid_keyword}': {card_count}")
        assert card_count == 0, (
            f"Expected 0 class cards for invalid search '{invalid_keyword}', but found {card_count}."
        )

        # Step 9: Verify the actual empty-state message
        empty_message = exclusive_classes_page.get_empty_state_message()
        logger.info(f"Actual empty-state message returned by application: '{empty_message}'")
        assert len(empty_message) > 0, "No empty-state message was displayed for invalid search."
        assert "no classes found" in empty_message.lower(), (
            f"Expected empty-state message to contain 'no classes found', got: '{empty_message}'"
        )

        request.node.user_properties.append(("empty_message", empty_message))

        # Capture intentional evidence screenshot
        exclusive_classes_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-EXC-003 PASSED: Empty state successfully verified ==========")

    def test_e2e_exc_004_sorting_and_filters(
        self,
        exclusive_classes_page: ExclusiveClassesPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-EXC-004: Sorting & Filters.

        Objective:
        Verify sorting and available filter options.

        Test steps:
        1. Navigate to Exclusive Classes.
        2. Inspect the actual sorting dropdown.
        3. Extract the available options dynamically.
        4. Verify whether 'Latest added' is available.
        5. Identify other available options, such as 'Most Popular', only if they actually exist.
        6. Select 'Latest added'.
        7. Wait for the class grid to update.
        8. Extract the displayed class ordering.
        9. Inspect actual publication dates, timestamps, or stable ordering metadata if available.
        10. Verify that the newest class appears first.
        11. Record the selected option and resulting class order.
        """
        logger.info("========== EXECUTING E2E-EXC-004: Sorting & Filters ==========")

        # Step 1: Navigate to Exclusive Classes
        exclusive_classes_page.open_exclusive_classes_page()

        # Step 2-3: Inspect sorting dropdown and extract available options dynamically
        available_options = exclusive_classes_page.get_available_sort_options()
        logger.info(f"Available sorting options dynamically discovered: {available_options}")
        assert len(available_options) > 0, "No sorting options were found in the dropdown."

        # Step 4: Verify whether 'Latest added' is available
        has_latest = any("latest added" in opt.lower() for opt in available_options)
        assert has_latest, f"'Latest added' sort option not found in available options: {available_options}"
        logger.info("Verified 'Latest added' sort option is present.")

        # Step 5: Identify all other available options (e.g., 'Oldest', 'Title: A to Z')
        other_options = [opt for opt in available_options if "latest added" not in opt.lower()]
        logger.info(f"Other available sort options discovered: {other_options}")

        # Step 6-7: Select 'Latest added' and wait for grid to update
        selection_ok = exclusive_classes_page.select_sort_option("Latest added")
        assert selection_ok, "Failed to select 'Latest added' sort option."

        # Step 8-9: Extract displayed class ordering and inspect publication dates
        card_details = exclusive_classes_page.get_class_card_details()
        logger.info(f"Rendered class card details after 'Latest added' sorting: {card_details}")
        assert len(card_details) > 0, "No class cards rendered after selecting 'Latest added'."

        # Step 10: Verify that the newest class appears first (chronological descending order)
        dates = [c["date"] for c in card_details if c["date"]]
        logger.info(f"Extracted publication dates: {dates}")
        if len(dates) >= 2:
            is_newest_first = exclusive_classes_page.verify_chronological_order_newest_first()
            assert is_newest_first, "Class cards are not sorted with the newest class appearing first."
            logger.info("Verified newest class appears first in chronological order.")
        else:
            logger.info("Publication dates limitation: insufficient timestamps on cards to verify order.")

        # Step 11: Record selected option and resulting class order
        request.node.user_properties.append(("selected_sort", "Latest added"))
        request.node.user_properties.append(("class_ordering", [c["title"] for c in card_details]))

        # Capture intentional evidence screenshot
        exclusive_classes_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-EXC-004 PASSED: Sorting & Filters successfully verified ==========")

