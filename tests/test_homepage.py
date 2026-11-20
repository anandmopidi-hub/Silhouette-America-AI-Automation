import pytest
from pages.home_page import HomePage


@pytest.mark.e2e
class TestHomepage:
    """Homepage E2E test suite covering critical navigation, brand elements, and footer links."""

    @pytest.mark.smoke
    def test_e2e_home_001_homepage_load(self, home_page: HomePage) -> None:
        """E2E-HOME-001: Verify that the Silhouette America production homepage loads successfully."""
        home_page.open_homepage()
        assert home_page.is_homepage_loaded(), "Homepage failed to load or key branding elements are missing."

    @pytest.mark.functional
    def test_e2e_home_002_logo_navigation(self, home_page: HomePage) -> None:
        """E2E-HOME-002: Verify clicking the Silhouette America logo returns to the homepage."""
        home_page.open_homepage()
        home_page.click_logo()
        assert home_page.is_homepage_loaded(), "Logo click did not maintain or return to the homepage."

    @pytest.mark.functional
    def test_e2e_home_003_navigate_to_machines(self, home_page: HomePage) -> None:
        """E2E-HOME-003: Verify Homepage -> Machines navigation."""
        home_page.open_homepage()
        destination_url = home_page.navigate_to_machines()
        assert home_page.is_expected_destination_loaded("machines"), (
            f"Expected 'machines' in destination URL, got '{destination_url}'"
        )

    @pytest.mark.functional
    def test_e2e_home_004_navigate_to_accessories(self, home_page: HomePage, request: pytest.FixtureRequest) -> None:
        """E2E-HOME-004: Verify Homepage -> Accessories navigation."""
        home_page.open_homepage()
        destination_url = home_page.navigate_to_accessories()
        assert home_page.is_expected_destination_loaded("accessories"), (
            f"Expected 'accessories' in destination URL, got '{destination_url}'"
        )

        # Intentional validated evidence capture
        home_page.prepare_for_destination_evidence()
        home_page.capture_evidence_screenshot(request.node.name)

    @pytest.mark.functional
    def test_e2e_home_005_navigate_to_supplies_materials(self, home_page: HomePage, request: pytest.FixtureRequest) -> None:
        """E2E-HOME-005: Verify Homepage -> Supplies/Materials navigation."""
        home_page.open_homepage()
        destination_url = home_page.navigate_to_supplies_materials()
        assert home_page.is_expected_destination_loaded("material"), (
            f"Expected 'material' in destination URL, got '{destination_url}'"
        )

        # Intentional validated evidence capture
        home_page.prepare_for_destination_evidence()
        home_page.capture_evidence_screenshot(request.node.name)

    @pytest.mark.functional
    def test_e2e_home_006_navigate_to_software(self, home_page: HomePage) -> None:
        """E2E-HOME-006: Verify Homepage -> Software navigation."""
        home_page.open_homepage()
        destination_url = home_page.navigate_to_software()
        assert home_page.is_expected_destination_loaded("software"), (
            f"Expected 'software' in destination URL, got '{destination_url}'"
        )

    @pytest.mark.functional
    def test_e2e_home_007_navigate_to_design_store(self, home_page: HomePage) -> None:
        """E2E-HOME-007: Verify Homepage -> Design Store navigation."""
        home_page.open_homepage()
        intended_url = home_page.get_design_store_intended_url()
        dest_page, dest_url = home_page.navigate_to_design_store()

        assert home_page.is_expected_destination_loaded("silhouettedesignstore", target_page=dest_page), (
            f"Expected destination URL to contain 'silhouettedesignstore' (intended: '{intended_url}'), got '{dest_url}'"
        )
        assert home_page.is_design_store_loaded(target_page=dest_page), (
            "Design Store destination page indicators (logo, search, or branding) failed to load."
        )
        dest_page.wait_for_timeout(1000)

    @pytest.mark.functional
    def test_e2e_home_008_navigate_to_club_silhouette(self, home_page: HomePage) -> None:
        """E2E-HOME-008: Verify Homepage -> Club Silhouette navigation."""
        home_page.open_homepage()
        destination_url = home_page.navigate_to_club_silhouette()
        assert home_page.is_expected_destination_loaded("club-silhouette"), (
            f"Expected 'club-silhouette' in destination URL, got '{destination_url}'"
        )

    @pytest.mark.functional
    def test_e2e_home_009_navigate_to_support(self, home_page: HomePage) -> None:
        """E2E-HOME-009: Verify Homepage -> Support navigation."""
        home_page.open_homepage()
        dest_page, dest_url = home_page.navigate_to_support()
        try:
            assert "freshdesk.com" in dest_url.lower() or "support" in dest_url.lower(), (
                f"Expected Support/FAQ destination, got '{dest_url}'"
            )
        finally:
            if dest_page != home_page.page:
                dest_page.close()

    @pytest.mark.regression
    def test_e2e_home_010_verify_critical_footer_links(self, home_page: HomePage) -> None:
        """E2E-HOME-010: Verify critical Homepage footer links."""
        home_page.open_homepage()
        results = home_page.verify_critical_footer_links()
        failed_links = [name for name, status in results.items() if not status]
        assert not failed_links, f"The following critical footer links failed destination verification: {failed_links}"

    @pytest.mark.functional
    def test_e2e_home_011_promotional_banner(self, home_page: HomePage) -> None:
        """E2E-HOME-011: Verify active promotional banner navigation."""
        home_page.open_homepage()
        intended_url = home_page.get_active_promotion_intended_url()
        dest_page, dest_url = home_page.open_promotion()
        if dest_page is None:
            pytest.skip("No active promotional banner found on the homepage.")

        assert home_page.verify_promotion_destination(dest_page, intended_url), (
            f"Promotional banner destination failed verification: intended='{intended_url}', actual='{dest_url}'"
        )

    @pytest.mark.functional
    def test_e2e_home_012_invalid_navigation_handling(self, home_page: HomePage) -> None:
        """E2E-HOME-012: Verify invalid route navigation and controlled error/fallback handling."""
        result = home_page.verify_invalid_route()
        assert result["is_valid_handling"], (
            f"Invalid route was not handled safely: status={result.get('status_code')}, url={result.get('final_url')}"
        )

    @pytest.mark.functional
    def test_e2e_home_013_homepage_slow_network(self, home_page: HomePage) -> None:
        """E2E-HOME-013: Verify Homepage loads and reaches usable state under slow network conditions."""
        try:
            home_page.emulate_slow_network(latency_ms=300, download_kbps=750, upload_kbps=500)
            home_page.open_homepage()
            assert home_page.verify_homepage_usable(timeout=45000), (
                "Homepage failed to reach a usable state under slow network conditions."
            )
        finally:
            home_page.reset_network_throttling()

    @pytest.mark.functional
    def test_e2e_home_014_mobile_viewport(self, home_page: HomePage) -> None:
        """E2E-HOME-014: Verify Homepage responsive layout and usability in mobile viewport (375x812)."""
        home_page.set_viewport(375, 812)
        home_page.open_homepage()
        result = home_page.verify_responsive_layout(width=375, height=812)
        assert result["is_usable"], f"Mobile responsive layout validation failed: {result['details']}"

    @pytest.mark.functional
    def test_e2e_home_015_tablet_viewport(self, home_page: HomePage) -> None:
        """E2E-HOME-015: Verify Homepage responsive layout and usability in tablet viewport (768x1024)."""
        home_page.set_viewport(768, 1024)
        home_page.open_homepage()
        result = home_page.verify_responsive_layout(width=768, height=1024)
        assert result["is_usable"], f"Tablet responsive layout validation failed: {result['details']}"

    @pytest.mark.functional
    def test_e2e_home_016_customer_reviews_section(
        self,
        home_page: HomePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-HOME-016: Customer Reviews Section.

        Verify visibility of "Why our customers love Silhouette" and
        "Trusted by Thousands of Makers Worldwide" headings, including carousel arrow functionality.
        """
        # Step 1: Open homepage
        home_page.open_homepage()

        # Step 2: Scroll to "Why our customers love Silhouette"
        reached = home_page.scroll_to_customer_reviews()
        assert reached, "Failed to scroll to Customer Reviews section on homepage."

        # Step 3: Verify heading visibility
        assert home_page.is_customer_reviews_heading_visible(), (
            "Section heading 'Why our customers love Silhouette' is not visible."
        )

        # Step 4: Verify left/right arrows
        arrows = home_page.are_carousel_arrows_visible()
        assert arrows["next"], "Right carousel navigation arrow (Next review) is not visible."
        assert arrows["prev"], "Left carousel navigation arrow (Previous review) is not visible."

        # Step 5: Click right arrow and verify next review
        next_res = home_page.navigate_carousel_next_and_verify()
        assert next_res["success"], f"Failed to advance carousel slide on right arrow click: {next_res}"

        # Step 6: Click left arrow and verify previous review
        prev_res = home_page.navigate_carousel_prev_and_verify()
        assert prev_res["success"], f"Failed to return to previous carousel slide on left arrow click: {prev_res}"

        # Step 7: Verify "Trusted by Thousands of Makers Worldwide" heading
        assert home_page.verify_trusted_makers_heading(), (
            "Heading 'Trusted by Thousands of Makers Worldwide' failed verification."
        )

        # Capture intentional evidence screenshot
        home_page.capture_evidence_screenshot(request.node.name)

    @pytest.mark.functional
    def test_e2e_home_017_customer_reviews_navigation(
        self,
        home_page: HomePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-HOME-017: Customer Reviews Navigation.

        Verify "Read our customer reviews" and "View more reviews" buttons
        navigate to the correct customer reviews page.
        """
        # Step 1: Open homepage
        home_page.open_homepage()

        # Step 2: Click "Read our customer reviews"
        reached = home_page.scroll_to_customer_reviews()
        assert reached, "Failed to locate Customer Reviews section on homepage."
        dest_url_1 = home_page.click_read_customer_reviews_badge()

        # Step 3: Verify destination URL and page loading
        assert "reviews" in dest_url_1.lower(), (
            f"Expected 'reviews' in destination URL after ribbon click, got '{dest_url_1}'"
        )
        assert home_page.is_reviews_destination_loaded(), (
            "Reviews destination page failed to load with valid heading and URL."
        )

        # Step 4: Return to homepage
        home_page.open_homepage()

        # Step 5: Scroll to "Customer reviews"
        reached_again = home_page.scroll_to_customer_reviews()
        assert reached_again, "Failed to return and scroll to Customer Reviews on homepage."

        # Step 6: Verify heading
        assert home_page.is_customer_reviews_heading_visible(), (
            "Customer reviews heading 'Why our customers love Silhouette' not visible on return."
        )

        # Step 7-8: Scroll to "View more reviews" and click it
        dest_url_2 = home_page.click_view_more_reviews_footer()

        # Step 9: Verify destination URL and page loading
        assert "reviews" in dest_url_2.lower(), (
            f"Expected 'reviews' in destination URL after footer click, got '{dest_url_2}'"
        )
        assert home_page.is_reviews_destination_loaded(), (
            "Reviews destination page failed to load after clicking secondary/footer link."
        )

        # Capture intentional evidence screenshot
        home_page.capture_evidence_screenshot(request.node.name)



