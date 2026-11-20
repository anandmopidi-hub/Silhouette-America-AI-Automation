from typing import Any, Dict, List, Optional, Tuple
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError
from config.config import Config
from locators.catalog_locators import CatalogLocators
from locators.home_locators import HomeLocators
from pages.base_page import BasePage
from utils.logger import logger
from utils.wait_helper import WaitHelper


class CatalogPage(BasePage):
    """Page Object for Silhouette America Catalog and Category Listing (PLP) functionality."""

    def __init__(self, page: Page, config: Optional[Config] = None):
        super().__init__(page, config)

    # =========================================================================
    # Navigation & Page State Methods
    # =========================================================================

    def open_category(self, category_slug: str = "accessories-parts") -> str:
        """Navigate directly to a category page, resolve any Cloudflare challenges, and dismiss cookies."""
        slug = category_slug.lstrip("/")
        logger.info(f"Opening catalog category page: '{slug}'")
        self.goto(slug)
        self.wait_for_dom_content_loaded()

        # Handle Cloudflare challenge screen if present
        try:
            if "just a moment" in self.get_title().lower():
                logger.info("Cloudflare challenge screen active. Waiting for automatic resolution...")
                self.page.wait_for_function(
                    "!document.title.toLowerCase().includes('just a moment')",
                    timeout=10000,
                )
                self.wait_for_dom_content_loaded()
        except Exception:
            pass

        self.dismiss_cookie_consent_if_present()
        self.wait_for_timeout(1000)
        return self.get_current_url()

    def dismiss_cookie_consent_if_present(self) -> None:
        """Dismiss cookie consent banner if visible on the catalog page."""
        try:
            accept_btn = self.page.locator(HomeLocators.COOKIE_ACCEPT_BUTTON).first
            if accept_btn.is_visible(timeout=2000):
                logger.info("Cookie consent banner detected on catalog page. Clicking 'I Agree'.")
                accept_btn.click()
                self.wait_for_timeout(500)
        except Exception:
            pass

    def is_catalog_page_loaded(self, expected_title_keyword: Optional[str] = None) -> bool:
        """Validate that the catalog/listing page loaded with main layout indicators.

        Checks:
        1. Main content and product grid/wrapper are present.
        2. Title contains expected keyword (if provided) and no 500 error.
        3. Page title (h1) or category title is visible.
        """
        current_url = self.get_current_url()
        title = self.get_title()

        title_valid = "500" not in title and "error" not in title.lower()
        if expected_title_keyword:
            title_valid = title_valid and expected_title_keyword.lower() in title.lower()

        h1_visible = self.is_visible(CatalogLocators.PAGE_TITLE, timeout=5000)
        grid_or_products = (
            self.is_visible(CatalogLocators.PRODUCT_GRID, timeout=5000)
            or self.get_product_count() > 0
            or self.is_no_products_message_displayed()
        )

        is_loaded = title_valid and h1_visible and grid_or_products
        logger.info(
            f"Catalog page load validation: URL='{current_url}', Title='{title}', "
            f"h1_visible={h1_visible}, grid_or_products={grid_or_products} -> is_loaded={is_loaded}"
        )
        return is_loaded

    def get_category_title(self) -> str:
        """Return the category page heading (h1) text."""
        try:
            title_elem = self.page.locator(CatalogLocators.PAGE_TITLE).first
            if title_elem.is_visible(timeout=3000):
                return title_elem.inner_text().strip()
        except Exception:
            pass
        return ""

    # =========================================================================
    # Product Grid & Card Methods
    # =========================================================================

    def get_product_count(self) -> int:
        """Return the count of visible product card items on the current page."""
        products = self.page.locator(CatalogLocators.PRODUCT_ITEMS)
        count = products.count()
        logger.info(f"Detected {count} product items on catalog listing.")
        return count

    def get_product_names(self) -> List[str]:
        """Extract and return text names of visible product items."""
        names = []
        products = self.page.locator(CatalogLocators.PRODUCT_ITEMS)
        for i in range(products.count()):
            try:
                name_elem = products.nth(i).locator(CatalogLocators.PRODUCT_ITEM_NAME).first
                txt = name_elem.inner_text().strip()
                if txt:
                    names.append(txt)
            except Exception:
                pass
        logger.info(f"Extracted {len(names)} product names from catalog listing.")
        return names

    def get_product_prices(self) -> List[str]:
        """Extract and return price strings of visible product items."""
        prices = []
        products = self.page.locator(CatalogLocators.PRODUCT_ITEMS)
        for i in range(products.count()):
            try:
                price_elem = products.nth(i).locator(CatalogLocators.PRODUCT_ITEM_PRICE).first
                txt = price_elem.inner_text().strip()
                if txt:
                    prices.append(txt)
            except Exception:
                pass
        logger.info(f"Extracted {len(prices)} product prices from catalog listing.")
        return prices

    def get_product_hrefs(self) -> List[str]:
        """Extract and return destination href URLs of visible product items."""
        hrefs = []
        products = self.page.locator(CatalogLocators.PRODUCT_ITEMS)
        for i in range(products.count()):
            try:
                link_elem = products.nth(i).locator(CatalogLocators.PRODUCT_ITEM_LINK).first
                href = link_elem.get_attribute("href")
                if href:
                    hrefs.append(href)
            except Exception:
                pass
        return hrefs

    # =========================================================================
    # Filter / Layered Navigation Methods
    # =========================================================================

    def is_filters_sidebar_visible(self) -> bool:
        """Check if the layered navigation filter sidebar is visible."""
        return self.is_visible(CatalogLocators.FILTER_BLOCK, timeout=4000)

    def get_available_filter_groups(self) -> List[str]:
        """Return list of available filter group names (e.g., ['Category', 'Project Type', 'Color', ...])."""
        groups = []
        filter_items = self.page.locator(CatalogLocators.FILTER_ITEMS)
        for i in range(filter_items.count()):
            try:
                title_elem = filter_items.nth(i).locator(CatalogLocators.FILTER_TITLE).first
                txt = title_elem.inner_text().strip()
                if txt and txt != "Filters:":
                    groups.append(txt)
            except Exception:
                pass
        logger.info(f"Discovered {len(groups)} filter groups: {groups}")
        return groups

    def get_filter_options_in_group(self, group_name: str) -> List[Tuple[str, str]]:
        """Return list of (option_label, href) for a given filter group name."""
        options = []
        filter_items = self.page.locator(CatalogLocators.FILTER_ITEMS)
        for i in range(filter_items.count()):
            item = filter_items.nth(i)
            title = item.locator(CatalogLocators.FILTER_TITLE).first.inner_text().strip()
            if group_name.lower() in title.lower():
                links = item.locator(CatalogLocators.FILTER_OPTION_LINK)
                for j in range(links.count()):
                    opt_link = links.nth(j)
                    opt_text = opt_link.inner_text().strip()
                    opt_href = opt_link.get_attribute("href") or ""
                    if opt_text and opt_href:
                        options.append((opt_text, opt_href))
                break
        logger.info(f"Found {len(options)} options in filter group '{group_name}'.")
        return options

    def apply_filter(
        self,
        group_name: Optional[str] = None,
        option_label: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Apply a filter option dynamically or by specified group and label.

        Returns:
            Tuple of (applied_group_name, applied_option_label)
        """
        logger.info(f"Applying filter: group='{group_name}', option='{option_label}'")
        filter_items = self.page.locator(CatalogLocators.FILTER_ITEMS)

        target_link = None
        applied_group = ""
        applied_label = ""

        for i in range(filter_items.count()):
            item = filter_items.nth(i)
            title_elem = item.locator(CatalogLocators.FILTER_TITLE).first
            title = title_elem.inner_text().strip()

            if group_name and group_name.lower() not in title.lower():
                continue

            # Ensure filter group accordion is expanded if collapsed
            content = item.locator(CatalogLocators.FILTER_CONTENT).first
            if not content.is_visible(timeout=1000):
                logger.info(f"Expanding collapsed filter group '{title}'.")
                title_elem.click()
                self.wait_for_timeout(500)

            links = item.locator(CatalogLocators.FILTER_OPTION_LINK)
            for j in range(links.count()):
                link = links.nth(j)
                txt = link.inner_text().strip()
                href = link.get_attribute("href")

                if not txt or not href:
                    continue

                if option_label:
                    if option_label.lower() in txt.lower():
                        target_link = link
                        applied_group = title
                        applied_label = txt.split()[0]
                        break
                else:
                    # Pick first valid option
                    target_link = link
                    applied_group = title
                    applied_label = txt.split()[0]
                    break

            if target_link:
                break

        if not target_link:
            raise RuntimeError(f"No suitable filter option found for group='{group_name}', label='{option_label}'")

        logger.info(f"Clicking filter: '{applied_label}' in group '{applied_group}'.")
        target_link.scroll_into_view_if_needed()
        target_link.click(force=True)
        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(2000)
        logger.info(f"Filter applied. New URL: '{self.get_current_url()}'")
        return applied_group, applied_label

    def get_applied_filters(self) -> List[str]:
        """Return list of currently active filter labels from the 'Now Shopping by' container."""
        applied = []
        try:
            current_block = self.page.locator(CatalogLocators.FILTER_CURRENT_CONTAINER).first
            if current_block.count() > 0:
                items = self.page.locator(CatalogLocators.FILTER_CURRENT_ITEMS)
                for i in range(items.count()):
                    txt = items.nth(i).inner_text().strip()
                    if txt:
                        applied.append(txt)
                if not applied:
                    raw_text = current_block.inner_text().replace("Now Shopping by", "").strip()
                    if raw_text:
                        applied = [raw_text]
        except Exception:
            pass
        logger.info(f"Currently applied filters: {applied}")
        return applied

    def is_filter_applied(self, filter_text: str) -> bool:
        """Check if a specific filter label is reflected in the active filters block or URL query params."""
        current_url = self.get_current_url().lower()
        applied = [a.lower() for a in self.get_applied_filters()]
        clean_text = filter_text.strip().lower()

        in_applied_block = any(clean_text in a for a in applied)
        # Check query parameters in URL
        has_query_params = "?" in current_url
        in_url = has_query_params and (clean_text in current_url or "cat=" in current_url or "compatible" in current_url)

        is_applied = in_applied_block or (has_query_params and in_url)
        logger.info(
            f"Check if filter '{filter_text}' applied: in_block={in_applied_block}, in_url={in_url} -> {is_applied}"
        )
        return is_applied

    def clear_all_filters(self) -> None:
        """Click the 'Clear All' button to remove all applied filters."""
        logger.info("Clearing all applied catalog filters.")
        clear_btn = self.page.locator(CatalogLocators.FILTER_CLEAR_ALL).first
        if clear_btn.is_visible(timeout=3000):
            clear_btn.scroll_into_view_if_needed()
            clear_btn.click()
            self.wait_for_dom_content_loaded()
            self.wait_for_timeout(2000)
            logger.info(f"Cleared all filters via Clear All control. New URL: '{self.get_current_url()}'")
        else:
            logger.warning("Clear All button was not visible; checking if any filters were applied.")

    def apply_zero_result_filter_combination(self) -> None:
        """Navigate to a deterministic, overly restrictive filter combination that yields 0 products.

        Example: Alta 3D Printer parts (?cat=649) + Cameo 5 cutting machine (?compatible_machines=2437).
        """
        logger.info("Applying restrictive filter combination for zero results (Alta Parts + Cameo 5).")
        self.open_category("accessories-parts?cat=649&compatible_machines=2437")
        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(1500)

    def is_no_products_message_displayed(self) -> bool:
        """Verify that the empty catalog state message 'We can't find products matching the selection.' is visible."""
        try:
            msg = self.page.locator(CatalogLocators.NO_PRODUCTS_NOTICE).first
            if msg.is_visible(timeout=3000):
                logger.info(f"No products message visible: '{msg.inner_text().strip()}'")
                return True
        except Exception:
            pass

        # Fallback check on page main text
        try:
            main_text = self.page.locator(CatalogLocators.MAIN_CONTENT).first.inner_text()
            if "can't find products" in main_text.lower() or "no products" in main_text.lower():
                return True
        except Exception:
            pass

        return False

    # =========================================================================
    # Sorter / Toolbar Methods
    # =========================================================================

    def get_available_sort_options(self) -> List[str]:
        """Return list of sort option display texts from the sorter dropdown."""
        options = []
        sorter = self.page.locator(CatalogLocators.SORTER_SELECT).first
        if sorter.is_visible(timeout=3000):
            for opt in sorter.locator("option").all():
                txt = opt.inner_text().strip()
                if txt and txt.lower() != "sort by":
                    options.append(txt)
        logger.info(f"Available sort options: {options}")
        return options

    def apply_sort_option(self, option_label_or_value: str = "Price: Low to high") -> str:
        """Select a sort option in the sorter dropdown and wait for listing update."""
        logger.info(f"Selecting sort option: '{option_label_or_value}'")
        sorter = self.page.locator(CatalogLocators.SORTER_SELECT).first
        sorter.scroll_into_view_if_needed()

        # Try selecting by label, value, or index
        matched = False
        options = sorter.locator("option").all()
        target_val = ""
        for opt in options:
            label = opt.inner_text().strip()
            val = opt.get_attribute("value") or ""
            if (
                option_label_or_value.lower() in label.lower()
                or option_label_or_value.lower() == val.lower()
            ):
                target_val = val
                matched = True
                break

        if matched and target_val:
            sorter.select_option(value=target_val)
        else:
            sorter.select_option(label=option_label_or_value)

        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(2000)
        logger.info(f"Sorted listing loaded. URL: '{self.get_current_url()}'")
        return self.get_current_url()

    def get_current_sort_value(self) -> str:
        """Return the current selected value of the sorter dropdown."""
        sorter = self.page.locator(CatalogLocators.SORTER_SELECT).first
        return sorter.input_value()

    # =========================================================================
    # Pagination Methods
    # =========================================================================

    def has_next_page(self) -> bool:
        """Check if the Next page control is visible and available on the page."""
        next_btn = self.page.locator(CatalogLocators.PAGINATION_NEXT_BUTTON).first
        try:
            return next_btn.is_visible(timeout=2000)
        except Exception:
            return False

    def is_next_page_available(self) -> bool:
        """Alias for has_next_page."""
        return self.has_next_page()

    def go_to_next_page(self) -> Tuple[int, str]:
        """Click the Next page pagination button and wait for the new page of products to load.

        Returns:
            Tuple of (new_page_number, new_page_url)
        """
        logger.info("Navigating to next catalog page via Next button.")
        next_btn = self.page.locator(CatalogLocators.PAGINATION_NEXT_BUTTON).first
        next_btn.scroll_into_view_if_needed()
        next_btn.click()
        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(2000)

        current_page = self.get_current_page_number()
        current_url = self.get_current_url()
        logger.info(f"Navigated to page {current_page} (URL: '{current_url}').")
        return current_page, current_url

    def get_current_page_number(self) -> int:
        """Extract the current active page number from pagination or URL."""
        current_elem = self.page.locator(CatalogLocators.PAGINATION_CURRENT_PAGE).first
        try:
            if current_elem.is_visible(timeout=1000):
                txt = current_elem.inner_text().strip()
                digits = [int(w) for w in txt.split() if w.isdigit()]
                if digits:
                    return digits[0]
        except Exception:
            pass

        # Fallback to URL query parameter ?p=
        import re

        match = re.search(r"[?&]p=(\d+)", self.get_current_url())
        if match:
            return int(match.group(1))

        return 1

    def get_last_page_number(self) -> int:
        """Determine the final/highest available page number from pagination links."""
        page_nums = []
        page_links = self.page.locator(CatalogLocators.PAGINATION_PAGE_LINKS)
        for i in range(page_links.count()):
            try:
                txt = page_links.nth(i).inner_text().strip()
                digits = [int(w) for w in txt.split() if w.isdigit()]
                if digits:
                    page_nums.extend(digits)
            except Exception:
                pass

        current = self.get_current_page_number()
        page_nums.append(current)

        last_page = max(page_nums) if page_nums else 1
        logger.info(f"Discovered highest available page number: {last_page}")
        return last_page

    def go_to_page(self, page_number: int) -> None:
        """Navigate directly to a specific page number."""
        logger.info(f"Navigating to catalog page number {page_number}.")
        current_url = self.get_current_url()
        import re

        if "p=" in current_url:
            target_url = re.sub(r"p=\d+", f"p={page_number}", current_url)
        else:
            sep = "&" if "?" in current_url else "?"
            target_url = f"{current_url}{sep}p={page_number}"

        self.page.goto(target_url, wait_until="domcontentloaded")
        self.wait_for_timeout(2000)

    # =========================================================================
    # Intentional Evidence Preparation Methods
    # =========================================================================

    def prepare_for_catalog_evidence(self) -> None:
        """Ensure catalog products are in viewport, transient elements dismissed, and state stable."""
        logger.info("Preparing catalog evidence state for screenshot.")
        try:
            self.page.evaluate("window.scrollTo(0, 200)")
        except Exception:
            pass
        self.dismiss_transient_elements()
        self.wait_for_timeout(300)

    def prepare_for_filtered_evidence(self) -> None:
        """Ensure filtered products and active filter tokens are visible, popups closed."""
        logger.info("Preparing filtered catalog evidence state for screenshot.")
        try:
            current_block = self.page.locator(CatalogLocators.FILTER_CURRENT_CONTAINER).first
            if current_block.is_visible(timeout=1000):
                current_block.scroll_into_view_if_needed()
            else:
                self.page.evaluate("window.scrollTo(0, 150)")
        except Exception:
            pass
        self.dismiss_transient_elements()
        self.wait_for_timeout(300)

    def prepare_for_sorted_evidence(self) -> None:
        """Ensure sorted product cards are visible, popups closed."""
        logger.info("Preparing sorted catalog evidence state for screenshot.")
        try:
            sorter = self.page.locator(CatalogLocators.SORTER_SELECT).first
            if sorter.is_visible(timeout=1000):
                sorter.scroll_into_view_if_needed()
            else:
                self.page.evaluate("window.scrollTo(0, 200)")
        except Exception:
            pass
        self.dismiss_transient_elements()
        self.wait_for_timeout(300)

    def prepare_for_pagination_evidence(self) -> None:
        """Scroll pagination controls and surrounding products into view for evidence."""
        logger.info("Preparing pagination evidence state for screenshot.")
        try:
            pag = self.page.locator(CatalogLocators.PAGINATION_CONTAINER).first
            if pag.is_visible(timeout=2000):
                pag.scroll_into_view_if_needed()
            else:
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        except Exception:
            pass
        self.dismiss_transient_elements()
        self.wait_for_timeout(300)
