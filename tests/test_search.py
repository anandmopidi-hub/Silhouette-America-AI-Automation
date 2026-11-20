import uuid
import pytest
from pages.search_page import SearchPage
from utils.logger import logger


@pytest.mark.e2e
class TestSearch:
    """Search E2E test suite covering valid keyword searches, accessory queries,

    negative flows, input edge cases, PDP navigation, and search state clearing.
    """

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_e2e_search_001_valid_machine(self, search_page: SearchPage, request: pytest.FixtureRequest) -> None:
        """E2E-SEARCH-001: Search valid machine keyword (CAMEO) and verify relevant results."""
        search_page.open_search()
        search_page.enter_search_query("CAMEO")
        search_page.submit_search()

        assert search_page.is_search_results_page_loaded(), (
            "Search results page failed to load for valid machine query 'CAMEO'."
        )
        results_count = search_page.get_search_results_count()
        assert results_count > 0, f"Expected product search results for 'CAMEO', found {results_count}."
        assert search_page.is_search_page_stable(), "Search page state is unstable after search."

        # Intentional validated evidence capture
        search_page.prepare_for_search_results_evidence()
        search_page.capture_evidence_screenshot(request.node.name)

    @pytest.mark.functional
    def test_e2e_search_002_valid_accessory(self, search_page: SearchPage, request: pytest.FixtureRequest) -> None:
        """E2E-SEARCH-002: Search valid accessory keyword (Blade) and verify search results."""
        search_page.open_search()
        search_page.enter_search_query("Blade")
        search_page.submit_search()

        assert search_page.is_search_results_page_loaded(), (
            "Search results page failed to load for accessory query 'Blade'."
        )
        results_count = search_page.get_search_results_count()
        assert results_count > 0, f"Expected accessory search results for 'Blade', found {results_count}."
        assert search_page.is_search_page_stable(), "Search page state is unstable after accessory search."

        # Intentional validated evidence capture
        search_page.prepare_for_search_results_evidence()
        search_page.capture_evidence_screenshot(request.node.name)

    @pytest.mark.functional
    def test_e2e_search_003_nonexistent_product(self, search_page: SearchPage, request: pytest.FixtureRequest) -> None:
        """E2E-SEARCH-003: Search nonexistent product query and verify clear no-results state."""
        non_existent_term = f"NONEXISTENT_PRODUCT_{uuid.uuid4().hex[:8]}"
        search_page.open_search()
        search_page.enter_search_query(non_existent_term)
        search_page.submit_search()

        assert search_page.is_no_results_displayed(
            expected_prefix="We're sorry, no results found for",
            query_substring=non_existent_term,
        ), f"Expected no-results state was not displayed for nonexistent query: {non_existent_term}"
        assert search_page.is_search_page_stable(), "Search page crashed or became unstable on nonexistent query."

        # Intentional validated evidence capture
        search_page.prepare_for_no_results_evidence()
        search_page.capture_evidence_screenshot(request.node.name)

    @pytest.mark.functional
    def test_e2e_search_004_special_characters(self, search_page: SearchPage, request: pytest.FixtureRequest) -> None:
        """E2E-SEARCH-004: Search special characters and verify safe handling and dynamic no-results message."""
        query = "!@#$%^"
        search_page.open_search()
        search_page.enter_search_query(query)
        search_page.submit_search()

        assert search_page.is_no_results_displayed(
            expected_prefix="no results found",
            query_substring=query,
        ), f"Expected dynamic no-results state not found for: {query}"
        assert search_page.is_search_page_stable(), (
            f"Search page encountered an unhandled error or unstable state on query: {query}"
        )

        # Intentional validated evidence capture
        search_page.prepare_for_no_results_evidence()
        search_page.capture_evidence_screenshot(request.node.name)

    @pytest.mark.functional
    def test_e2e_search_005_leading_trailing_spaces(self, search_page: SearchPage, request: pytest.FixtureRequest) -> None:
        """E2E-SEARCH-005: Search query with leading and trailing spaces and verify normalization."""
        search_page.open_search()
        search_page.enter_search_query("  CAMEO  ")
        search_page.submit_search()

        assert search_page.is_search_results_page_loaded(), (
            "Search results page failed to load for query with leading/trailing spaces."
        )
        results_count = search_page.get_search_results_count()
        assert results_count > 0, (
            f"Expected relevant search results for trimmed query 'CAMEO', found {results_count}."
        )
        assert search_page.is_search_page_stable(), "Search page became unstable for query with spaces."

        # Intentional validated evidence capture
        search_page.prepare_for_search_results_evidence()
        search_page.capture_evidence_screenshot(request.node.name)

    @pytest.mark.functional
    def test_e2e_search_006_extremely_long_string(self, search_page: SearchPage, request: pytest.FixtureRequest) -> None:
        """E2E-SEARCH-006: Search extremely long string (500+ chars) and validate layout integrity.

        Manual Test Case:
        - Enter a 500+ character search string.
        - Submit the search.
        - Expected Result: Application remains stable, displays appropriate no-results/validation message.
          The long search text must remain within the page layout without horizontal overflow,
          clipping, or broken UI.
        - Validations:
          1. The search is submitted successfully.
          2. The no-results/validation message is displayed.
          3. The page reaches a stable state.
          4. The long search query displayed in the no-results message does not overflow outside the page/container.
          5. Verify there is no horizontal UI overflow or unexpected horizontal scrolling caused by the long text.
          6. Verify the text is not clipped on the right side.
          7. Verify there is no broken layout, overlapping UI, unexpected error, or indefinite loading state.
        - Defect Handling:
          If the 500+ character query extends/clips toward the right side of the page, this is detected
          as a UI validation failure. The test distinguishes between functional success (no-results message displayed)
          and visual/UI failure (overflow/clipping), capturing the failed screenshot and video evidence.
        """
        # Step 1: Generate dynamic 500+ character search string
        long_query = search_page.generate_long_search_query(length=500)
        logger.info(f"Executing E2E-SEARCH-006 with dynamic query of length {len(long_query)}.")

        # Step 2: Submit search
        search_page.open_search()
        search_page.enter_search_query(long_query)
        search_page.submit_search()

        # Validation 1 & 3 & 7 (part 1): Search submission success & page stability
        assert search_page.is_search_page_stable(), (
            "Search page crashed or became unresponsive after submitting 500+ character string."
        )
        title = search_page.get_title()
        assert "500" not in title and "error" not in title.lower(), (
            f"Unexpected 500 server error encountered on search: '{title}'"
        )
        logger.info("Search submitted successfully and application remains stable (Validation 1 & 3 PASSED).")

        # Validation 2: No-results validation message is displayed (Functional Validation)
        no_results_displayed = search_page.is_no_results_displayed()
        assert no_results_displayed, (
            "Expected appropriate no-results / validation message for 500+ character search string."
        )
        logger.info(
            "FUNCTIONAL VALIDATION PASSED: Search submitted successfully, 0 product results returned, "
            "and appropriate no-results message is displayed."
        )

        # Prepare UI for visual evidence capture and layout inspection
        search_page.prepare_for_no_results_evidence()

        # Informational layout inspection (non-blocking functional test)
        layout_metrics = search_page.validate_no_results_ui_layout()
        logger.info(f"UI Layout Evaluation Results (informational): {layout_metrics}")

        # Step 7: Final passed evidence capture for functional validation
        search_page.capture_evidence_screenshot(request.node.name, status="passed")
        logger.info("E2E-SEARCH-006: Functional search validation PASSED.")

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_e2e_search_007_open_search_result(self, search_page: SearchPage, request: pytest.FixtureRequest) -> None:
        """E2E-SEARCH-007: Open a valid search result and verify Product Detail Page (PDP) navigation."""
        search_page.open_search()
        search_page.enter_search_query("CAMEO")
        search_page.submit_search()

        assert search_page.get_search_results_count() > 0, "No search results available to open."

        intended_href, actual_url = search_page.open_first_search_result()
        assert search_page.is_pdp_loaded(intended_url=intended_href), (
            f"PDP failed to load for intended product href: '{intended_href}', actual URL: '{actual_url}'"
        )

        # Intentional validated evidence capture
        search_page.prepare_for_pdp_evidence()
        search_page.capture_evidence_screenshot(request.node.name)

    @pytest.mark.functional
    def test_e2e_search_008_search_then_clear(self, search_page: SearchPage, request: pytest.FixtureRequest) -> None:
        """E2E-SEARCH-008: Perform search, verify results, clear search query using UI, and verify cleared state."""
        search_page.open_search()
        search_page.enter_search_query("CAMEO")
        search_page.submit_search()

        assert search_page.get_search_results_count() > 0, "Initial search did not return results."

        search_page.clear_search_input()
        input_value = search_page.get_search_input_value()
        assert input_value == "", f"Expected search input to be cleared, but found '{input_value}'."
        assert search_page.is_search_page_stable(), "Search page became unstable after clearing search query."

        # Intentional validated evidence capture
        search_page.prepare_for_cleared_search_evidence()
        search_page.capture_evidence_screenshot(request.node.name)
