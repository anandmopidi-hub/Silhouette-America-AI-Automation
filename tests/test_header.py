"""Silhouette America — Header Navigation E2E Test Suite.

Automates the 6 Header Navigation module test cases:
- E2E-HDR-001: Top-Level Navigation Links (Shop, Software, Machine, Tools & Mats, Materials, Accessories, Club Silhouette, Clearance 40% Off)
- E2E-HDR-002: Tools & Mats Dropdown Mega-Menu
- E2E-HDR-003: Materials Dropdown Mega-Menu
- E2E-HDR-004: Accessories Dropdown Mega-Menu
- E2E-HDR-005: Club Silhouette Resources Sub-Menu Links
- E2E-HDR-006: Clearance 40% Off Promotional Redirection
"""
from typing import Any, Dict, List
import pytest

from pages.header_page import HeaderPage
from utils.logger import logger


@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.regression
class TestHeader:
    """E2E test suite covering Silhouette America website Header Navigation components."""

    def test_e2e_hdr_001_top_level_navigation_links(
        self,
        header_page: HeaderPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-HDR-001: Verify all 8 top-level header navigation items.

        Navigation items tested:
        1. Shop
        2. Software
        3. Machine
        4. Tools & Mats
        5. Materials
        6. Accessories
        7. Club Silhouette
        8. Clearance 40% Off

        Verification criteria:
        - All 8 navigation items exist and are visible in the desktop header.
        - Navigating to each category resolves to a valid destination URL.
        - HTTP response status is successful (200 / non-error).
        - Page heading (H1) or page title accurately reflects the category.
        - Destination page is not a 404 or broken error page.
        """
        logger.info("========== EXECUTING E2E-HDR-001: Top-Level Navigation Links ==========")

        # Step 1: Open website homepage
        header_page.open_homepage()

        # Step 2: Dynamically inspect top-level navigation items
        items = header_page.get_top_level_navigation_items()
        assert len(items) == 8, f"Expected 8 top-level navigation items, found {len(items)}"
        logger.info(f"Discovered 8 top-level navigation items: {[item['label'] for item in items]}")

        # Step 3: Iterate through each top-level menu item and validate destination
        failures: List[str] = []
        for item in items:
            label = item["label"]
            logger.info(f"--- Testing Top-Level Navigation for '{label}' ---")
            result = header_page.navigate_to_top_level_menu(label)

            if not result["success"]:
                err = f"'{label}' failed: status={result['status']}, 404={result['is_404']}, URL={result['final_url']}"
                logger.error(err)
                failures.append(err)
            else:
                logger.info(
                    f"'{label}' passed -> Final URL: {result['final_url']} | "
                    f"Heading: '{result['heading']}' | Status: {result['status']}"
                )

        # Step 4: Capture evidence screenshot
        header_page.capture_evidence_screenshot(request.node.name)

        # Step 5: Assert zero failures across all 8 navigation items
        assert not failures, f"Top-level header navigation failed for items: {failures}"
        logger.info("E2E-HDR-001 completed successfully. All 8 top-level menu items validated.")

    def test_e2e_hdr_002_tools_mats_dropdown_links(
        self,
        header_page: HeaderPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-HDR-002: Verify Tools & Mats dropdown mega-menu child links.

        Verification criteria:
        - Tools & Mats trigger reveals mega-menu panel.
        - Child links are dynamically extracted and filtered.
        - Each child category navigates to a valid landing page.
        - HTTP response status is 200 (or non-error).
        - Page title or H1 heading corresponds to the category.
        - Zero broken (404) links.
        """
        logger.info("========== EXECUTING E2E-HDR-002: Tools & Mats Dropdown Mega-Menu ==========")

        results = header_page.validate_dropdown_mega_menu("toolmatmmenu")
        assert len(results) > 0, "No child links were validated for Tools & Mats dropdown."

        header_page.capture_evidence_screenshot(request.node.name)
        logger.info(f"E2E-HDR-002 completed successfully. Validated {len(results)} Tools & Mats links.")

    def test_e2e_hdr_003_materials_dropdown_links(
        self,
        header_page: HeaderPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-HDR-003: Verify Materials dropdown mega-menu child links.

        Verification criteria:
        - Materials trigger reveals mega-menu panel.
        - Child links are dynamically extracted and filtered.
        - Each child category navigates to a valid landing page.
        - HTTP response status is 200 (or non-error).
        - Page title or H1 heading corresponds to the category.
        - Zero broken (404) links.
        """
        logger.info("========== EXECUTING E2E-HDR-003: Materials Dropdown Mega-Menu ==========")

        results = header_page.validate_dropdown_mega_menu("materialmenu")
        assert len(results) > 0, "No child links were validated for Materials dropdown."

        header_page.capture_evidence_screenshot(request.node.name)
        logger.info(f"E2E-HDR-003 completed successfully. Validated {len(results)} Materials links.")

    def test_e2e_hdr_004_accessories_dropdown_links(
        self,
        header_page: HeaderPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-HDR-004: Verify Accessories dropdown mega-menu child links.

        Verification criteria:
        - Accessories trigger reveals mega-menu panel.
        - Child links are dynamically extracted and filtered.
        - Each child category navigates to a valid landing page.
        - HTTP response status is 200 (or non-error).
        - Page title or H1 heading corresponds to the category.
        - Zero broken (404) links.
        """
        logger.info("========== EXECUTING E2E-HDR-004: Accessories Dropdown Mega-Menu ==========")

        results = header_page.validate_dropdown_mega_menu("accemenu")
        assert len(results) > 0, "No child links were validated for Accessories dropdown."

        header_page.capture_evidence_screenshot(request.node.name)
        logger.info(f"E2E-HDR-004 completed successfully. Validated {len(results)} Accessories links.")

    def test_e2e_hdr_005_resources_sub_menu_links(
        self,
        header_page: HeaderPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-HDR-005: Verify Club Silhouette / Resources sub-menu links.

        Verification criteria:
        - Resources trigger reveals sub-menu panel.
        - Child links (About Us, FAQ, Tool Compatibility, User Manuals, Exclusive Classes, Creators Rewards)
          are dynamically extracted.
        - Handles target='_blank' popup window navigation (FAQ external help desk).
        - Each link navigates to a valid landing page with HTTP 200/non-error.
        - Zero broken (404) links.
        """
        logger.info("========== EXECUTING E2E-HDR-005: Club Silhouette Resources Sub-Menu Links ==========")

        results = header_page.validate_dropdown_mega_menu("resourcemenu")
        assert len(results) > 0, "No child links were validated for Resources sub-menu."

        header_page.capture_evidence_screenshot(request.node.name)
        logger.info(f"E2E-HDR-005 completed successfully. Validated {len(results)} Resources links.")

    def test_e2e_hdr_006_clearance_40_percent_off_redirection(
        self,
        header_page: HeaderPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-HDR-006: Verify Clearance 40% Off promotional header redirection.

        Verification criteria:
        - Clearance 40% Off element is located in the header.
        - Clicking or navigating via the promotional item directs to the clearance page.
        - Final URL contains '/clearance'.
        - Page heading or title confirms Clearance category.
        - Clearance product grid / sale items are present.
        - Page is not 404 or broken.
        """
        logger.info("========== EXECUTING E2E-HDR-006: Clearance 40% Off Promotional Redirection ==========")

        result = header_page.validate_clearance_promotional_redirection()
        assert result["success"], f"Clearance promotional redirection failed: {result}"
        assert "clearance" in result["final_url"].lower(), f"URL does not contain clearance: {result['final_url']}"
        assert not result["is_404"], f"Clearance page is a 404: {result['final_url']}"

        header_page.capture_evidence_screenshot(request.node.name)
        logger.info(
            f"E2E-HDR-006 completed successfully. Clearance promotional redirection verified at '{result['final_url']}'."
        )

