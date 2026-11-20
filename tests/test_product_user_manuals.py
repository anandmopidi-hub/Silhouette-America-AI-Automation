"""Silhouette America — Product User Manuals E2E Test Suite.

Automates all 5 Product User Manuals module test cases:
- E2E-MAN-001: Page Landing, Tabs & Static Sections
- E2E-MAN-002: Machine Tab Actions
- E2E-MAN-003: Software Tab Actions
- E2E-MAN-004: Supply Tab Actions
- E2E-MAN-005: Legacy Machine Tab Actions
"""
import pytest

from pages.product_user_manuals_page import ProductUserManualsPage
from utils.logger import logger


@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.regression
class TestProductUserManuals:
    """E2E test suite covering Silhouette America Product User Manuals module."""

    def test_e2e_man_001_page_landing_tabs_and_static_sections(
        self,
        product_user_manuals_page: ProductUserManualsPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-MAN-001: Page Landing, Tabs & Static Sections.

        1. Open the Product User Manuals URL.
        2. Wait for DOMContentLoaded and stable page rendering.
        3. Handle the cookie consent popup using existing helper.
        4. Verify the main heading: 'User Manuals'.
        5. Verify all four tabs: Machine, Software, Supply, Legacy Machine.
        6. Verify each tab is visible and clickable.
        7. Verify the customer section heading: 'Why our customers love Silhouette'.
        8. Record the actual page title and relevant UI elements.
        """
        logger.info("========== EXECUTING E2E-MAN-001: Page Landing, Tabs & Static Sections ==========")

        # Steps 1-3: Open URL, wait for stable render, handle Cloudflare & cookies
        response = product_user_manuals_page.open_product_user_manuals_page()
        if response is not None:
            assert response.status < 400, (
                f"Expected successful HTTP status for Product User Manuals, got {response.status}"
            )
            logger.info(f"Landing page HTTP status verified: {response.status}")

        page_title = product_user_manuals_page.get_title()
        curr_url = product_user_manuals_page.get_current_url()
        assert "product-user-manual" in curr_url, f"Unexpected URL: '{curr_url}'"
        assert page_title, "Actual page title should not be empty."
        logger.info(f"Recorded page title: '{page_title}' | URL: '{curr_url}'")

        # Step 4: Verify main heading 'User Manuals'
        main_heading = product_user_manuals_page.get_main_heading_text()
        assert "user manuals" in main_heading.lower(), (
            f"Expected main heading 'User Manuals', got: '{main_heading}'"
        )
        logger.info(f"Verified main heading: '{main_heading}'")

        # Steps 5-6: Verify all 4 tabs are present, visible, and clickable
        expected_tabs = ["Machine", "Software", "Supply", "Legacy Machine"]
        tabs_status = product_user_manuals_page.get_all_tabs_status()
        discovered_names = [t["text"] for t in tabs_status]
        logger.info(f"Discovered tabs: {discovered_names}")

        for tab_info in tabs_status:
            assert tab_info["visible"], f"Tab '{tab_info['name']}' is not visible."
            assert tab_info["enabled"], f"Tab '{tab_info['name']}' is not clickable/enabled."
            assert tab_info["name"].lower() in tab_info["text"].lower(), (
                f"Expected tab text '{tab_info['name']}', got '{tab_info['text']}'"
            )

        assert len(tabs_status) == len(expected_tabs), (
            f"Expected {len(expected_tabs)} tabs, found {len(tabs_status)}: {discovered_names}"
        )

        # Verify each tab is interactive (switch across all and restore default Machine tab)
        for tab_name in expected_tabs:
            assert product_user_manuals_page.select_tab(tab_name), (
                f"Failed to activate tab '{tab_name}' when clicked."
            )
        assert product_user_manuals_page.select_tab("Machine"), "Failed to return to default 'Machine' tab."

        # Step 7: Verify customer section heading 'Why our customers love Silhouette'
        customer_heading = product_user_manuals_page.get_customer_section_heading_text()
        assert "why our customers love silhouette" in customer_heading.lower(), (
            f"Expected customer section heading 'Why our customers love Silhouette', got: '{customer_heading}'"
        )
        logger.info(f"Verified customer section heading: '{customer_heading}'")

        # Step 8: Record actual page title and UI metadata
        request.node.user_properties.append(("page_title", page_title))
        request.node.user_properties.append(("tabs", discovered_names))
        request.node.user_properties.append(("customer_heading", customer_heading))

        product_user_manuals_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-MAN-001 PASSED: Page Landing, Tabs & Static Sections Verified ==========")

    def test_e2e_man_002_machine_tab_actions(
        self,
        product_user_manuals_page: ProductUserManualsPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-MAN-002: Machine Tab Actions.

        1. Select the Machine tab.
        2. Verify that machine product cards are displayed.
        3. Dynamically capture the first available product card title.
        4. Click its User Manual link.
        5. Handle new tab / popup / same-tab navigation according to site behavior.
        6. Verify the document loads successfully and check HTTP response status.
        7. Return to the Product User Manuals page.
        8. If a Safety Manual link exists on the card, verify it using the same approach.
        9. Return to the Machine tab.
        10. Click View Product.
        11. Verify that the destination PDP heading matches the dynamically captured product title.
        12. Return to the User Manuals page.
        """
        logger.info("========== EXECUTING E2E-MAN-002: Machine Tab Actions ==========")

        product_user_manuals_page.open_product_user_manuals_page()

        # Step 1-2: Select Machine tab & verify product cards
        assert product_user_manuals_page.select_tab("Machine"), "Failed to select 'Machine' tab."
        cards_count = product_user_manuals_page.get_cards_count("Machine")
        assert cards_count > 0, "Expected machine product cards to be displayed, found 0."
        logger.info(f"Machine tab displays {cards_count} product cards.")

        # Step 3: Dynamically capture first product card title
        captured_title = product_user_manuals_page.get_card_title("Machine", card_index=0)
        assert captured_title, "First machine product card title was empty."

        # Steps 4-7: Click User Manual, verify load & HTTP status, return
        user_manual_res = product_user_manuals_page.open_manual_and_verify(
            tab_name="Machine", action_type="User Manual", card_index=0
        )
        assert user_manual_res["success"], (
            f"Machine User Manual failed to load: {user_manual_res}"
        )
        if user_manual_res["http_status"] is not None:
            assert user_manual_res["http_status"] < 400, (
                f"Machine User Manual returned error HTTP status: {user_manual_res['http_status']}"
            )
        assert user_manual_res.get("is_pdf_content") or "pdf" in user_manual_res.get("content_type", "").lower(), (
            f"Machine User Manual is not a valid accessible PDF: {user_manual_res}"
        )
        logger.info(
            f"Verified Machine User Manual: url={user_manual_res['final_url']}, "
            f"status={user_manual_res['http_status']} ({user_manual_res['response_source']})"
        )

        # Step 8: If Safety Manual exists, verify using same approach
        if product_user_manuals_page.has_card_action("Machine", "Safety Manual", card_index=0):
            safety_res = product_user_manuals_page.open_manual_and_verify(
                tab_name="Machine", action_type="Safety Manual", card_index=0
            )
            assert safety_res["success"], (
                f"Machine Safety Manual failed to load: {safety_res}"
            )
            if safety_res["http_status"] is not None:
                assert safety_res["http_status"] < 400, (
                    f"Machine Safety Manual returned error HTTP status: {safety_res['http_status']}"
                )
            assert safety_res.get("is_pdf_content") or "pdf" in safety_res.get("content_type", "").lower(), (
                f"Machine Safety Manual is not a valid accessible PDF: {safety_res}"
            )
            logger.info(
                f"Verified Machine Safety Manual: url={safety_res['final_url']}, "
                f"status={safety_res['http_status']} ({safety_res['response_source']})"
            )

        # Step 9: Ensure Machine tab is active
        assert product_user_manuals_page.select_tab("Machine"), "Failed to return to Machine tab."

        # Steps 10-11: Click View Product and verify destination PDP heading/title matches
        dest_info = product_user_manuals_page.click_view_product_and_capture("Machine", card_index=0)
        assert not dest_info["is_404"], f"Machine View Product led to 404/error page: {dest_info['url']}"
        assert dest_info["page_title"], "Destination PDP page title was empty."
        assert product_user_manuals_page.verify_destination_matches_product(captured_title, dest_info), (
            f"Machine PDP heading/title mismatch for '{captured_title}': "
            f"H1='{dest_info['h1_text']}', Title='{dest_info['page_title']}'"
        )

        # Step 12: Return to User Manuals page
        assert product_user_manuals_page.return_to_user_manuals_page(), (
            "Failed to return to Product User Manuals page after Machine View Product."
        )

        request.node.user_properties.append(("captured_machine", captured_title))
        request.node.user_properties.append(("pdp_title", dest_info["page_title"]))

        product_user_manuals_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-MAN-002 PASSED: Machine Tab Actions Verified ==========")

    def test_e2e_man_003_software_tab_actions(
        self,
        product_user_manuals_page: ProductUserManualsPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-MAN-003: Software Tab Actions.

        1. Select the Software tab.
        2. Verify the tab's active state.
        3. Verify software product cards are displayed.
        4. Dynamically capture the first available software title.
        5. Click User Manual and verify the document opens successfully.
        6. Return to the User Manuals page.
        7. Click View Product.
        8. Verify the destination PDP heading/title matches the captured software title.
        9. Return to the User Manuals page.
        """
        logger.info("========== EXECUTING E2E-MAN-003: Software Tab Actions ==========")

        product_user_manuals_page.open_product_user_manuals_page()

        # Steps 1-2: Select Software tab and verify active state
        assert product_user_manuals_page.select_tab("Software"), "Software tab did not enter active state."

        # Step 3: Verify software product cards are displayed
        cards_count = product_user_manuals_page.get_cards_count("Software")
        assert cards_count > 0, "Expected software product cards to be displayed, found 0."
        logger.info(f"Software tab displays {cards_count} product cards.")

        # Step 4: Dynamically capture first software title
        captured_title = product_user_manuals_page.get_card_title("Software", card_index=0)
        assert captured_title, "First software card title was empty."

        # Steps 5-6: Click User Manual, verify document opens & HTTP status, return
        manual_res = product_user_manuals_page.open_manual_and_verify(
            tab_name="Software", action_type="User Manual", card_index=0
        )
        assert manual_res["success"], f"Software User Manual failed to load: {manual_res}"
        if manual_res["http_status"] is not None:
            assert manual_res["http_status"] < 400, (
                f"Software User Manual returned error HTTP status: {manual_res['http_status']}"
            )
        logger.info(
            f"Verified Software User Manual: url={manual_res['final_url']}, "
            f"status={manual_res['http_status']} ({manual_res['response_source']})"
        )

        # Ensure Software tab remains selected before View Product
        if not product_user_manuals_page.is_tab_active("Software"):
            product_user_manuals_page.select_tab("Software")

        # Steps 7-8: Click View Product and verify destination PDP heading/title matches
        dest_info = product_user_manuals_page.click_view_product_and_capture("Software", card_index=0)
        assert not dest_info["is_404"], f"Software View Product led to 404/error page: {dest_info['url']}"
        assert dest_info["page_title"], "Destination Software PDP page title was empty."
        assert product_user_manuals_page.verify_destination_matches_product(captured_title, dest_info), (
            f"Software destination mismatch for '{captured_title}': "
            f"H1='{dest_info['h1_text']}', Title='{dest_info['page_title']}'"
        )

        # Step 9: Return to User Manuals page
        assert product_user_manuals_page.return_to_user_manuals_page(), (
            "Failed to return to Product User Manuals page after Software View Product."
        )

        request.node.user_properties.append(("captured_software", captured_title))
        request.node.user_properties.append(("pdp_title", dest_info["page_title"]))

        product_user_manuals_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-MAN-003 PASSED: Software Tab Actions Verified ==========")

    def test_e2e_man_004_supply_tab_actions(
        self,
        product_user_manuals_page: ProductUserManualsPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-MAN-004: Supply Tab Actions.

        1. Select the Supply tab.
        2. Verify the tab's active state.
        3. Verify supply product cards are displayed.
        4. Dynamically capture the first available supply title.
        5. Click User Manual and verify the document opens successfully.
        6. Return to the User Manuals page.
        7. Click View Product.
        8. Verify the destination PDP heading matches the captured supply title.
        9. Return to the User Manuals page.
        """
        logger.info("========== EXECUTING E2E-MAN-004: Supply Tab Actions ==========")

        product_user_manuals_page.open_product_user_manuals_page()

        # Steps 1-2: Select Supply tab and verify active state
        assert product_user_manuals_page.select_tab("Supply"), "Supply tab did not enter active state."

        # Step 3: Verify supply product cards are displayed
        cards_count = product_user_manuals_page.get_cards_count("Supply")
        assert cards_count > 0, "Expected supply product cards to be displayed, found 0."
        logger.info(f"Supply tab displays {cards_count} product cards.")

        # Step 4: Dynamically capture first supply title
        captured_title = product_user_manuals_page.get_card_title("Supply", card_index=0)
        assert captured_title, "First supply card title was empty."

        # Steps 5-6: Click User Manual, verify document opens & HTTP status, return
        manual_res = product_user_manuals_page.open_manual_and_verify(
            tab_name="Supply", action_type="User Manual", card_index=0
        )
        assert manual_res["success"], f"Supply User Manual failed to load: {manual_res}"
        if manual_res["http_status"] is not None:
            assert manual_res["http_status"] < 400, (
                f"Supply User Manual returned error HTTP status: {manual_res['http_status']}"
            )
        logger.info(
            f"Verified Supply User Manual: url={manual_res['final_url']}, "
            f"status={manual_res['http_status']} ({manual_res['response_source']})"
        )

        # Ensure Supply tab remains selected before View Product
        if not product_user_manuals_page.is_tab_active("Supply"):
            product_user_manuals_page.select_tab("Supply")

        # Steps 7-8: Click View Product and verify destination PDP heading/title matches
        dest_info = product_user_manuals_page.click_view_product_and_capture("Supply", card_index=0)
        assert not dest_info["is_404"], f"Supply View Product led to 404/error page: {dest_info['url']}"
        assert dest_info["page_title"], "Destination Supply PDP page title was empty."
        assert product_user_manuals_page.verify_destination_matches_product(captured_title, dest_info), (
            f"Supply PDP mismatch for '{captured_title}': "
            f"H1='{dest_info['h1_text']}', Title='{dest_info['page_title']}'"
        )

        # Step 9: Return to User Manuals page
        assert product_user_manuals_page.return_to_user_manuals_page(), (
            "Failed to return to Product User Manuals page after Supply View Product."
        )

        request.node.user_properties.append(("captured_supply", captured_title))
        request.node.user_properties.append(("pdp_title", dest_info["page_title"]))

        product_user_manuals_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-MAN-004 PASSED: Supply Tab Actions Verified ==========")

    def test_e2e_man_005_legacy_machine_tab_actions(
        self,
        product_user_manuals_page: ProductUserManualsPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-MAN-005: Legacy Machine Tab Actions.

        1. Select the Legacy Machine tab.
        2. Verify the tab's active state.
        3. Verify legacy machine product cards are displayed.
        4. Dynamically identify the first available legacy machine card.
        5. Click its User Manual link.
        6. Verify that the document opens successfully.
        7. Check the document response status where available and identify any 404 or failed response.
        8. Return to the User Manuals page.
        9. Verify the customer section heading remains visible.
        """
        logger.info("========== EXECUTING E2E-MAN-005: Legacy Machine Tab Actions ==========")

        product_user_manuals_page.open_product_user_manuals_page()

        # Steps 1-2: Select Legacy Machine tab and verify active state
        assert product_user_manuals_page.select_tab("Legacy Machine"), (
            "Legacy Machine tab did not enter active state."
        )

        # Step 3: Verify legacy machine cards are displayed
        cards_count = product_user_manuals_page.get_cards_count("Legacy Machine")
        assert cards_count > 0, "Expected legacy machine product cards to be displayed, found 0."
        logger.info(f"Legacy Machine tab displays {cards_count} product cards.")

        # Step 4: Dynamically identify first legacy machine card
        captured_title = product_user_manuals_page.get_card_title("Legacy Machine", card_index=0)
        assert captured_title, "First legacy machine card title was empty."

        # Steps 5-8: Click User Manual link, verify opening and check HTTP status (detect 404/failed)
        manual_res = product_user_manuals_page.open_manual_and_verify(
            tab_name="Legacy Machine", action_type="User Manual", card_index=0
        )
        assert not manual_res["is_404_or_failed"], (
            f"Legacy Machine User Manual returned failed HTTP status {manual_res['http_status']}: "
            f"{manual_res['final_url']}"
        )
        assert manual_res["success"], (
            f"Legacy Machine User Manual failed to open cleanly: {manual_res}"
        )
        assert manual_res.get("is_pdf_content") or "pdf" in manual_res.get("content_type", "").lower(), (
            f"Legacy Machine User Manual is not a valid accessible PDF: {manual_res}"
        )
        logger.info(
            f"Verified Legacy Machine User Manual: url={manual_res['final_url']}, "
            f"status={manual_res['http_status']} ({manual_res['response_source']})"
        )

        # Verify we are on Product User Manuals page
        assert "product-user-manual" in product_user_manuals_page.get_current_url(), (
            "Not on Product User Manuals page after closing document tab."
        )

        # Step 9: Verify customer section heading remains visible
        assert product_user_manuals_page.is_customer_section_heading_visible(
            "Why our customers love Silhouette"
        ), "Customer section heading 'Why our customers love Silhouette' is not visible."

        request.node.user_properties.append(("captured_legacy", captured_title))
        request.node.user_properties.append(("manual_status", manual_res["http_status"]))

        product_user_manuals_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-MAN-005 PASSED: Legacy Machine Tab Actions Verified ==========")

