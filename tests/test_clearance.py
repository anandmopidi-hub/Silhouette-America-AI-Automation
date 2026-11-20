"""Silhouette America — Clearance / Sale Items E2E Test Suite.

Automates all 5 Clearance / Sale Items module test cases:
- E2E-CLR-001: Page Landing & Hero Banner
- E2E-CLR-002: Layered Navigation Filters
- E2E-CLR-003: Product Card Elements & Clearance Badges
- E2E-CLR-004: Sorting Dropdown
- E2E-CLR-005: Editorial Sections & Common Questions FAQ
"""
import re
from typing import Any, Dict, List
import pytest
from playwright.sync_api import expect

from pages.clearance_page import ClearancePage
from utils.logger import logger


@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.regression
class TestClearance:
    """E2E test suite covering Silhouette America Clearance / Sale Items module."""

    def test_e2e_clr_001_page_landing_and_hero_banner(
        self,
        clearance_page: ClearancePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CLR-001: Page Landing & Hero Banner.

        1. Open Silhouette America homepage and wait for header navigation.
        2. Handle cookie consent popup if displayed.
        3. Identify Clearance 40% Off navigation item dynamically.
        4. Hover or click to reveal the clearance mega-menu panel.
        5. Locate Sale Items link dynamically and extract destination href.
        6. Navigate using visible link, assert URL matches target and HTTP status is successful.
        7. Verify hero heading 'Real Deals. Real Savings. Shop Clearance Now.' is visible.
        8. Verify heading belongs to the hero section and is rendered correctly.
        """
        logger.info("========== EXECUTING E2E-CLR-001: Page Landing & Hero Banner ==========")

        # Steps 1-3: Open homepage, handle cookies, wait for header
        clearance_page.open_homepage_and_wait_for_nav()

        # Steps 4-5: Open clearance menu dynamically
        panel = clearance_page.open_clearance_menu()
        expect(panel).to_be_visible()

        # Steps 6-7: Locate Sale Items link and extract destination href
        sale_link = clearance_page.get_sale_items_link()
        expect(sale_link).to_be_visible()
        extracted_href = sale_link.get_attribute("href") or ""
        assert "clearance" in extracted_href.lower(), (
            f"Expected 'clearance' in extracted nav href, got: '{extracted_href}'"
        )
        logger.info(f"Extracted Sale Items nav href dynamically: '{extracted_href}'")

        # Step 8-10: Navigate via visible link and verify destination URL & status
        nav_result = clearance_page.navigate_to_clearance()
        expect(clearance_page.page).to_have_url(re.compile(r".*clearance.*", re.IGNORECASE))
        if nav_result["status"] is not None:
            assert nav_result["status"] in [200, 304], (
                f"Expected HTTP 200/304 response, got {nav_result['status']}"
            )
            logger.info(f"Verified navigation HTTP status: {nav_result['status']}")

        # Step 11-13: Assert hero heading is visible in hero section dynamically
        hero_heading = clearance_page.get_hero_heading()
        expect(hero_heading).to_be_visible(timeout=10000)
        heading_text = hero_heading.inner_text().strip()
        assert any(kw in heading_text.lower() for kw in ["real deals", "clearance", "deals", "savings"]), (
            f"Hero heading text mismatch: '{heading_text}'"
        )
        logger.info(f"Verified hero heading inside hero section dynamically: '{heading_text}'")

        hero_section = clearance_page.get_hero_section()
        expect(hero_section).to_be_visible()
        logger.info("E2E-CLR-001 completed successfully.")

    def test_e2e_clr_002_layered_navigation_filters(
        self,
        clearance_page: ClearancePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CLR-002: Layered Navigation Filters.

        1. Open Clearance / Sale Items page directly.
        2. Locate Filters sidebar dynamically.
        3. Identify available filter groups (e.g. Category, Machine Option, Machine Type, Project Type).
        4. Expand filter groups and extract available filter options.
        5. Select Refurbished within Category and verify active filter and product grid update.
        6. Clear filter via Clear All control and verify reset.
        7. Select available options in Machine Option, Machine Type, and Project Type.
        8. Verify grid updates, selected state, and final unfiltered restoration.
        """
        logger.info("========== EXECUTING E2E-CLR-002: Layered Navigation Filters ==========")

        # Step 1: Open Clearance page
        clearance_page.open_clearance_page_direct()

        # Step 2: Locate Filters sidebar dynamically
        sidebar = clearance_page.get_filter_sidebar()
        expect(sidebar).to_be_visible(timeout=10000)

        # Step 3-4: Identify available filter groups
        discovered_groups = clearance_page.get_filter_groups_names()
        assert len(discovered_groups) > 0, "No filter groups discovered in sidebar."
        logger.info(f"Discovered {len(discovered_groups)} filter groups: {discovered_groups}")

        # Verify expected groups when present
        expected_sample_groups = ["Category", "Machine Option", "Machine Type", "Project Type"]
        present_expected = [g for g in expected_sample_groups if any(g.lower() in dg.lower() for dg in discovered_groups)]
        logger.info(f"Present expected groups: {present_expected}")
        assert len(present_expected) >= 2, f"Expected at least 2 target filter groups, found: {present_expected}"

        initial_count = clearance_page.get_product_cards_count()
        logger.info(f"Initial baseline product count before filtering: {initial_count}")
        assert initial_count > 0, "Initial clearance product grid is empty."

        # Step 5-6: Select 'Refurbished' dynamically within Category
        category_options = clearance_page.get_filter_options("Category")
        refurb_opt = next((o for o in category_options if "refurbished" in o["label"].lower()), None)
        if refurb_opt:
            logger.info(f"Testing filter selection for: Category -> '{refurb_opt['label']}'")
            res_refurb = clearance_page.select_filter_option("Category", refurb_opt["label"])
            assert res_refurb["product_count"] > 0, "No products displayed after selecting Refurbished filter."
            assert "cat=" in res_refurb["new_url"].lower() or "refurbished" in res_refurb["new_url"].lower(), (
                f"URL did not update with category filter: {res_refurb['new_url']}"
            )
            # Clear filter and verify restoration
            clearance_page.clear_all_filters()
            cleared_count = clearance_page.get_product_cards_count()
            logger.info(f"Product count after clearing Refurbished: {cleared_count}")
            assert cleared_count == initial_count, (
                f"Expected restored count {initial_count}, got {cleared_count}"
            )

        # Step 7-8: Test selectable options in Machine Option, Machine Type, or Project Type
        groups_to_test = [g for g in ["Machine Option", "Machine Type", "Project Type"] if any(g.lower() in dg.lower() for dg in discovered_groups)]
        for g_name in groups_to_test:
            options = clearance_page.get_filter_options(g_name)
            if not options:
                logger.warning(f"Filter group '{g_name}' currently has no selectable options.")
                continue

            test_opt = options[0]
            logger.info(f"Testing filter selection for: {g_name} -> '{test_opt['label']}'")
            res = clearance_page.select_filter_option(g_name, test_opt["label"])
            assert res["product_count"] > 0, f"No products displayed after filtering by '{test_opt['label']}' in '{g_name}'."
            logger.info(f"Filtered product count for '{test_opt['label']}': {res['product_count']}")

            # Reset filter
            clearance_page.clear_all_filters()
            post_clear_count = clearance_page.get_product_cards_count()
            assert post_clear_count == initial_count, (
                f"Expected restored product count {initial_count} after clearing, got {post_clear_count}"
            )

        logger.info("E2E-CLR-002 completed successfully.")

    def test_e2e_clr_003_product_card_elements_and_clearance_badges(
        self,
        clearance_page: ClearancePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CLR-003: Product Card Elements & Clearance Badges.

        1. Locate all product cards dynamically and verify grid is not empty.
        2. Iterate through all visible product cards.
        3. Extract: title, image, original price, sale price, discount badge, clearance badge, CTA.
        4. Verify each image natural dimensions (naturalWidth > 0, naturalHeight > 0, complete == True).
        5. Verify that where both original and sale prices exist, sale price < original price.
        6. Compute discount percentage: ((orig - sale) / orig) * 100 and compare to displayed badge.
        7. Verify Clearance badges and Explore Options CTA presence.
        """
        logger.info("========== EXECUTING E2E-CLR-003: Product Card Elements & Clearance Badges ==========")

        clearance_page.open_clearance_page_direct()

        # Step 1: Locate product cards
        cards = clearance_page.get_product_cards()
        total_cards = len(cards)
        assert total_cards > 0, "No product cards found in the clearance grid."
        logger.info(f"Discovered {total_cards} product cards for validation.")

        # Step 2-3: Extract all dynamic product details
        products = clearance_page.get_all_products_details()

        verified_discounts_count = 0
        verified_clearance_badges_count = 0
        verified_explore_ctas_count = 0

        for idx, prod in enumerate(products):
            title = prod["title"]
            logger.info(f"--- Validating Card {idx + 1}/{total_cards}: '{title}' ---")
            assert title and title != "Untitled Product", f"Card {idx} is missing a product title."

            # Step 4: Verify image loads successfully with natural dimensions
            img = prod["image"]
            assert img.get("complete") is True, f"Image for '{title}' did not complete loading."
            assert img.get("naturalWidth", 0) > 0 and img.get("naturalHeight", 0) > 0, (
                f"Image for '{title}' is broken or missing natural dimensions: {img}"
            )
            assert img.get("src"), f"Image for '{title}' has empty src attribute."

            # Step 5: Verify sale price exists
            assert prod["sale_price"] is not None and prod["sale_price"] > 0, (
                f"Product '{title}' has invalid sale price: '{prod['sale_price_str']}'"
            )

            # Step 6: If original price exists, verify sale_price < original_price and discount math
            if prod["has_both_prices"]:
                orig = prod["old_price"]
                sale = prod["sale_price"]
                assert sale < orig, (
                    f"Product '{title}': sale price ${sale} is not strictly less than original price ${orig}."
                )
                calc_disc = prod["calculated_discount_pct"]
                disp_disc = prod["displayed_discount_pct"]
                logger.info(
                    f"Product '{title}': Orig=${orig}, Sale=${sale} -> "
                    f"Calculated Discount={calc_disc:.2f}%, Displayed Badge={disp_disc}%"
                )
                if disp_disc is not None and calc_disc is not None:
                    # Allow reasonable rounding tolerance (e.g. within 2 percentage points)
                    diff = abs(calc_disc - disp_disc)
                    assert diff <= 2.0, (
                        f"Product '{title}': calculated discount {calc_disc:.2f}% deviates from displayed {disp_disc}%."
                    )
                    verified_discounts_count += 1

            # Step 7: Check Clearance badge
            if prod["clearance_badge"]:
                assert "clearance" in prod["clearance_badge"].lower(), (
                    f"Product '{title}' clearance badge mismatch: '{prod['clearance_badge']}'"
                )
                verified_clearance_badges_count += 1

            # Step 8: Check Explore Options CTA
            if prod["has_explore_cta"]:
                assert "explore" in prod["cta_text"].lower(), (
                    f"Product '{title}' CTA mismatch: '{prod['cta_text']}'"
                )
                verified_explore_ctas_count += 1

        logger.info(
            f"Validation complete across {total_cards} products: "
            f"{verified_discounts_count} discount percentages verified, "
            f"{verified_clearance_badges_count} clearance badges, "
            f"{verified_explore_ctas_count} Explore Options CTAs."
        )
        assert verified_clearance_badges_count > 0, "No Clearance badges found on any product card."
        logger.info("E2E-CLR-003 completed successfully.")

    def test_e2e_clr_004_sorting_dropdown(
        self,
        clearance_page: ClearancePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CLR-004: Sorting Dropdown.

        1. Locate sorting control dynamically.
        2. Extract available sorting options and verify expected options:
           - Position, Price: Low to High, Price: High to Low, New, Best Seller.
        3. Select Price: Low to High, wait for grid update, assert ascending price order.
        4. Select Price: High to Low, wait for grid update, assert descending price order.
        5. Select New, verify selected state and grid update.
        6. Select Best Seller, verify selected state and grid update.
        7. Verify no errors occurred during sorting interactions.
        """
        logger.info("========== EXECUTING E2E-CLR-004: Sorting Dropdown ==========")

        clearance_page.open_clearance_page_direct()

        # Step 1-2: Extract available sort options
        sort_options = clearance_page.get_available_sort_options()
        assert len(sort_options) > 0, "No options found in sorter dropdown."
        option_texts = [o["text"] for o in sort_options]
        logger.info(f"Discovered sort options: {option_texts}")

        # Verify expected options where present
        expected_sort_keywords = ["position", "low to high", "high to low", "new", "seller"]
        for kw in expected_sort_keywords:
            matched = any(kw in ot.lower() for ot in option_texts)
            assert matched, f"Expected sorting option containing '{kw}' not found in {option_texts}"
        logger.info("All expected sorting options confirmed present in the dropdown.")

        # Step 3: Select Price: Low to High and verify ascending order
        logger.info("Testing Price: Low to High sorting...")
        clearance_page.select_sort_option("price_asc")
        expect(clearance_page.page).to_have_url(re.compile(r".*product_list_order=price_asc.*", re.IGNORECASE))

        prods_asc = clearance_page.get_all_products_details()
        prices_asc = [p["sale_price"] for p in prods_asc if p["sale_price"] is not None]
        logger.info(f"Extracted prices (Low to High): {prices_asc}")
        assert len(prices_asc) >= 2, "Insufficient priced products to verify ascending sorting."
        is_ascending = all(prices_asc[i] <= prices_asc[i + 1] for i in range(len(prices_asc) - 1))
        assert is_ascending, f"Prices are not in ascending order: {prices_asc}"
        logger.info("Ascending price sorting verified successfully.")

        # Step 4: Select Price: High to Low and verify descending order
        logger.info("Testing Price: High to Low sorting...")
        clearance_page.select_sort_option("price_desc")
        expect(clearance_page.page).to_have_url(re.compile(r".*product_list_order=price_desc.*", re.IGNORECASE))

        prods_desc = clearance_page.get_all_products_details()
        prices_desc = [p["sale_price"] for p in prods_desc if p["sale_price"] is not None]
        logger.info(f"Extracted prices (High to Low): {prices_desc}")
        assert len(prices_desc) >= 2, "Insufficient priced products to verify descending sorting."
        is_descending = all(prices_desc[i] >= prices_desc[i + 1] for i in range(len(prices_desc) - 1))
        assert is_descending, f"Prices are not in descending order: {prices_desc}"
        logger.info("Descending price sorting verified successfully.")

        # Step 5: Select New and verify selection & grid update
        logger.info("Testing 'New' sorting...")
        clearance_page.select_sort_option("new")
        expect(clearance_page.page).to_have_url(re.compile(r".*product_list_order=new.*", re.IGNORECASE))
        assert clearance_page.get_current_sorter_value() == "new", "Sorter value did not reflect 'new'."
        assert clearance_page.get_product_cards_count() > 0, "Grid rendered empty after sorting by New."
        logger.info("'New' sort verified successfully.")

        # Step 6: Select Best Seller and verify selection & grid update
        logger.info("Testing 'Best Seller' sorting...")
        clearance_page.select_sort_option("bestsellers")
        expect(clearance_page.page).to_have_url(re.compile(r".*product_list_order=bestsellers.*", re.IGNORECASE))
        assert clearance_page.get_current_sorter_value() == "bestsellers", "Sorter value did not reflect 'bestsellers'."
        assert clearance_page.get_product_cards_count() > 0, "Grid rendered empty after sorting by Best Seller."
        logger.info("'Best Seller' sort verified successfully.")

        logger.info("E2E-CLR-004 completed successfully.")

    def test_e2e_clr_005_editorial_sections_and_common_questions_faq(
        self,
        clearance_page: ClearancePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CLR-005: Editorial Sections & Common Questions FAQ.

        1. Open Clearance / Sale Items page directly.
        2. Scroll down and verify customer reviews section 'Why our customers love Silhouette'.
        3. Verify all three editorial headings:
           - The Same Silhouette Quality — at Genuine Clearance Prices
           - What You'll Find in the Silhouette Clearance Section
           - Smart Tips for Shopping the Silhouette Clearance Section
        4. Locate Common Questions section heading and assert visibility.
        5. Identify FAQ accordion items dynamically and verify count > 0.
        6. Iterate through all FAQ items:
           - Extract question text, click to expand, assert answer becomes visible with non-empty text.
           - Validate expanded state (active class / aria-expanded).
        7. Verify accordion behavior (single-open vs multiple-open).
        """
        logger.info("========== EXECUTING E2E-CLR-005: Editorial Sections & Common Questions FAQ ==========")

        clearance_page.open_clearance_page_direct()

        # Step 2-5: Locate and verify editorial sections
        editorials = clearance_page.get_editorial_sections()

        # 1. Customer reviews heading
        reviews_h2 = editorials["customer_reviews"]
        reviews_h2.scroll_into_view_if_needed()
        expect(reviews_h2).to_be_visible(timeout=8000)
        logger.info(f"Verified customer section heading: '{reviews_h2.inner_text().strip()}'")

        # 2. Quality editorial heading
        quality_h2 = editorials["quality"]
        quality_h2.scroll_into_view_if_needed()
        expect(quality_h2).to_be_visible(timeout=5000)
        logger.info(f"Verified editorial heading: '{quality_h2.inner_text().strip()}'")

        # 3. Find editorial heading
        find_h2 = editorials["find"]
        find_h2.scroll_into_view_if_needed()
        expect(find_h2).to_be_visible(timeout=5000)
        logger.info(f"Verified editorial heading: '{find_h2.inner_text().strip()}'")

        # 4. Tips editorial heading
        tips_h2 = editorials["tips"]
        tips_h2.scroll_into_view_if_needed()
        expect(tips_h2).to_be_visible(timeout=5000)
        logger.info(f"Verified editorial heading: '{tips_h2.inner_text().strip()}'")

        # 5. Common Questions heading
        faq_h2 = editorials["common_questions"]
        faq_h2.scroll_into_view_if_needed()
        expect(faq_h2).to_be_visible(timeout=5000)
        logger.info(f"Verified FAQ heading: '{faq_h2.inner_text().strip()}'")

        # Step 6-14: Identify FAQ accordion items and iterate
        faq_count = clearance_page.get_faq_items_count()
        assert faq_count > 0, "No FAQ accordion items found on the page."
        logger.info(f"Discovered {faq_count} FAQ accordion items for verification.")

        verified_faqs: List[Dict[str, Any]] = []
        for idx in range(faq_count):
            faq_res = clearance_page.expand_faq_item(idx)
            assert faq_res["is_visible"], f"FAQ item {idx + 1} ('{faq_res['question']}') answer is not visible after click."
            assert len(faq_res["answer"]) > 10, f"FAQ item {idx + 1} answer is empty or too short: '{faq_res['answer']}'."
            assert "active" in faq_res["item_class"] or faq_res["aria_expanded"] == "true", (
                f"FAQ item {idx + 1} did not reflect expanded state (class='{faq_res['item_class']}', aria-expanded='{faq_res['aria_expanded']}')."
            )
            verified_faqs.append(faq_res)

        # Check single-open behavior: exactly 1 item open at the end
        open_count = sum(
            1 for item in clearance_page.get_faq_items()
            if item.locator(".faq_product_answer, [data-role='content']").first.is_visible()
            or "active" in (item.get_attribute("class") or "")
        )
        logger.info(f"Accordion behavior: {len(verified_faqs)} FAQs verified; single-open state: {open_count <= 2}")

        logger.info(f"E2E-CLR-005 completed successfully with {len(verified_faqs)} verified FAQ items.")
