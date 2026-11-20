"""Page Object Model for Silhouette America Clearance / Sale Items module.

Encapsulates all actions, dynamic element extraction, filters, sorter,
product cards, editorial sections, and FAQ interactions.
"""
import re
from typing import Any, Dict, List, Optional, Tuple
from playwright.sync_api import Locator, Page, expect

from config.config import Config
from locators.clearance_locators import ClearanceLocators
from pages.base_page import BasePage
from utils.logger import logger


class ClearancePage(BasePage):
    """Page Object for Silhouette America Clearance / Sale Items page."""

    def __init__(self, page: Page, config: Optional[Config] = None) -> None:
        super().__init__(page, config)

    # =========================================================================
    # Navigation & Initial Setup
    # =========================================================================

    def open_homepage_and_wait_for_nav(self) -> None:
        """Open production homepage, handle cloudflare and cookie consent."""
        logger.info("Opening Silhouette America homepage...")
        self.goto("")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        try:
            self.page.wait_for_selector(ClearanceLocators.CLEARANCE_MENU_ITEM, state="visible", timeout=15000)
        except Exception:
            pass

    def dismiss_cookie_consent_if_present(self, timeout: int = 2500) -> bool:
        """Detect and click cookie accept button if visible."""
        try:
            btn = self.page.locator(ClearanceLocators.COOKIE_ACCEPT_BUTTON).first
            if btn.is_visible(timeout=timeout):
                logger.info("Dismissing cookie consent banner...")
                btn.click(timeout=timeout)
                btn.wait_for(state="hidden", timeout=timeout)
                return True
        except Exception as e:
            logger.debug(f"Cookie consent handling notice: {e}")
        return False

    def open_clearance_menu(self) -> Locator:
        """Hover or click the Clearance 40% Off navigation item to expose the mega-menu."""
        logger.info("Locating and opening Clearance navigation menu item...")
        panel = self.page.locator(ClearanceLocators.CLEARANCE_PANEL).first
        if panel.is_visible():
            logger.info("Clearance panel is already visible.")
            return panel

        menu_item = self.page.locator(ClearanceLocators.CLEARANCE_MENU_ITEM).first
        expect(menu_item).to_be_visible(timeout=8000)
        menu_item.hover()
        self.wait_for_timeout(400)

        if not panel.is_visible(timeout=2000):
            logger.info("Clearance panel not visible on hover; attempting click...")
            menu_item.locator("button, a").first.click()
            self.wait_for_timeout(400)

        expect(panel).to_be_visible(timeout=5000)
        return panel

    def get_sale_items_link(self) -> Locator:
        """Locate the 'Sale Items' link inside the clearance menu dynamically."""
        panel = self.open_clearance_menu()
        sale_link = panel.locator("a:has-text('Sale Items')").first
        if sale_link.count() == 0 or not sale_link.is_visible():
            sale_link = panel.locator("a[href*='/clearance']").first
        if sale_link.count() == 0 or not sale_link.is_visible():
            sale_link = self.page.locator("a[href*='/clearance']:has-text('Sale')").first
        expect(sale_link).to_be_visible(timeout=5000)
        return sale_link

    def navigate_to_clearance(self) -> Dict[str, Any]:
        """Navigate to the Clearance page via the header navigation link.
        Extracts destination href, executes navigation, and captures HTTP status.
        """
        sale_link = self.get_sale_items_link()
        target_href = sale_link.get_attribute("href") or "https://www.silhouetteamerica.com/clearance"
        logger.info(f"Navigating to Clearance via link href: '{target_href}'")

        captured_status: Optional[int] = None
        try:
            with self.page.expect_navigation(wait_until="domcontentloaded", timeout=20000) as nav_info:
                sale_link.click()
            resp = nav_info.value
            if resp:
                captured_status = resp.status
        except Exception as e:
            logger.debug(f"Clearance navigation event notice: {e}; falling back to direct goto...")
            resp = self.goto("clearance", wait_until="domcontentloaded")
            if resp:
                captured_status = resp.status

        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.wait_for_timeout(1000)

        final_url = self.get_current_url()
        logger.info(f"Clearance page loaded. Final URL: '{final_url}', HTTP Status: {captured_status}")
        return {
            "target_href": target_href,
            "final_url": final_url,
            "status": captured_status,
        }

    def open_clearance_page_direct(self) -> None:
        """Directly open the Clearance / Sale Items page."""
        logger.info("Opening Clearance page directly: /clearance")
        self.goto("clearance")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.wait_for_timeout(1500)

    # =========================================================================
    # Hero Section & Headings
    # =========================================================================

    def get_hero_heading(self) -> Locator:
        """Return the hero heading locator 'Real Deals. Real Savings. Shop Clearance Now.'."""
        heading = self.page.locator(ClearanceLocators.HERO_HEADING).first
        heading.scroll_into_view_if_needed()
        return heading

    def get_hero_section(self) -> Locator:
        """Return the hero section banner container."""
        return self.page.locator(ClearanceLocators.HERO_SECTION).first

    # =========================================================================
    # Layered Navigation / Filters
    # =========================================================================

    def get_filter_sidebar(self) -> Locator:
        """Return the filter sidebar container locator."""
        return self.page.locator(ClearanceLocators.FILTER_SIDEBAR).first

    def get_filter_group_elements(self) -> List[Locator]:
        """Return list of all filter group items on the page."""
        return self.page.locator(ClearanceLocators.FILTER_GROUPS).all()

    def get_filter_groups_names(self) -> List[str]:
        """Extract available filter group names from the live DOM."""
        names: List[str] = []
        for group in self.get_filter_group_elements():
            title_el = group.locator(ClearanceLocators.FILTER_GROUP_TITLE).first
            if title_el.count() > 0:
                txt = title_el.inner_text().strip()
                if txt and txt not in names:
                    names.append(txt)
        logger.info(f"Discovered filter groups dynamically: {names}")
        return names

    def expand_filter_group(self, group_name: str) -> Locator:
        """Expand a collapsed filter group accordion by name.
        Returns the filter group locator.
        """
        logger.info(f"Expanding filter group: '{group_name}'")
        group = self.page.locator(ClearanceLocators.FILTER_GROUPS).filter(
            has=self.page.locator(f"{ClearanceLocators.FILTER_GROUP_TITLE}:has-text('{group_name}')")
        ).first
        expect(group).to_be_visible(timeout=5000)

        title = group.locator(ClearanceLocators.FILTER_GROUP_TITLE).first
        content = group.locator(ClearanceLocators.FILTER_GROUP_CONTENT).first

        if not content.is_visible(timeout=1000):
            title.scroll_into_view_if_needed()
            title.click()
            self.wait_for_timeout(800)

        expect(content).to_be_visible(timeout=5000)
        return group

    def get_filter_options(self, group_name: str) -> List[Dict[str, Any]]:
        """Extract available filter options (label, count, href) for a given filter group."""
        group = self.expand_filter_group(group_name)
        content = group.locator(ClearanceLocators.FILTER_GROUP_CONTENT).first
        links = content.locator("a").all()

        options: List[Dict[str, Any]] = []
        for l in links:
            raw_text = l.inner_text().strip()
            # Extract count if present (e.g., 'Starter Bundle 2items' -> label='Starter Bundle', count=2)
            count_match = re.search(r"(\d+)\s*(?:item|items)?", raw_text, re.IGNORECASE)
            count = int(count_match.group(1)) if count_match else None
            # Clean label
            label = re.sub(r"\d+\s*(?:item|items)?", "", raw_text).strip()
            href = l.get_attribute("href") or ""
            options.append({
                "raw_text": raw_text,
                "label": label or raw_text,
                "count": count,
                "href": href,
                "locator": l,
            })
        logger.info(f"Extracted {len(options)} options for filter group '{group_name}': {[o['label'] for o in options]}")
        return options

    def select_filter_option(self, group_name: str, option_label: str) -> Dict[str, Any]:
        """Select a filter option by group name and option label.
        Waits for grid and URL update, returns verification metrics.
        """
        logger.info(f"Selecting filter: group='{group_name}', option='{option_label}'")
        group = self.expand_filter_group(group_name)
        content = group.locator(ClearanceLocators.FILTER_GROUP_CONTENT).first

        target_link = content.locator(f"a:has-text('{option_label}')").first
        expect(target_link).to_be_visible(timeout=5000)
        target_href = target_link.get_attribute("href") or ""

        target_link.scroll_into_view_if_needed()
        target_link.click()

        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(2000)

        new_url = self.get_current_url()
        active_items = self.get_applied_filters()
        product_count = self.get_product_cards_count()

        logger.info(
            f"Filter applied: '{option_label}'. New URL: '{new_url}', "
            f"Active filters: {active_items}, Resulting products: {product_count}"
        )
        return {
            "applied_option": option_label,
            "target_href": target_href,
            "new_url": new_url,
            "active_filters": active_items,
            "product_count": product_count,
        }

    def get_applied_filters(self) -> List[str]:
        """Extract all currently active filter labels from the active filter container."""
        applied: List[str] = []
        try:
            items = self.page.locator(ClearanceLocators.ACTIVE_FILTER_ITEMS).all()
            for item in items:
                txt = item.inner_text().strip().replace("\n", " ")
                if txt and txt not in applied:
                    applied.append(txt)
        except Exception as e:
            logger.debug(f"Notice extracting applied filters: {e}")
        return applied

    def clear_all_filters(self) -> bool:
        """Click the 'Clear All' button to reset layered navigation filters."""
        logger.info("Attempting to clear all applied filters...")
        clear_btn = self.page.locator(ClearanceLocators.FILTER_CLEAR_ALL_BTN).first
        if clear_btn.is_visible(timeout=3000):
            clear_btn.scroll_into_view_if_needed()
            clear_btn.click()
            self.wait_for_dom_content_loaded()
            self.wait_for_timeout(2000)
            logger.info(f"Filters cleared. Current URL: '{self.get_current_url()}'")
            return True
        else:
            logger.warning("Clear All button not visible; falling back to direct clearance URL reset.")
            self.open_clearance_page_direct()
            return True

    # =========================================================================
    # Product Grid & Product Cards
    # =========================================================================

    def get_product_cards(self) -> List[Locator]:
        """Return list of all visible product cards in the clearance grid."""
        return self.page.locator(ClearanceLocators.PRODUCT_CARDS).all()

    def get_product_cards_count(self) -> int:
        """Return the count of product cards rendered in the grid."""
        return self.page.locator(ClearanceLocators.PRODUCT_CARDS).count()

    def parse_price(self, price_str: str) -> Optional[float]:
        """Safely parse currency string into a float, stripping symbols and commas."""
        if not price_str:
            return None
        cleaned = re.sub(r"[^\d.]", "", price_str.strip())
        if cleaned:
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def get_product_card_details(self, card: Locator) -> Dict[str, Any]:
        """Extract all required dynamic attributes from a single product card."""
        # 1. Product Title
        title_el = card.locator(ClearanceLocators.PRODUCT_CARD_TITLE).first
        title = title_el.inner_text().strip() if title_el.count() > 0 else "Untitled Product"

        # 2. Product Image
        img_el = card.locator(ClearanceLocators.PRODUCT_CARD_IMAGE).first
        img_info: Dict[str, Any] = {}
        if img_el.count() > 0:
            try:
                img_info = img_el.evaluate(
                    "el => ({naturalWidth: el.naturalWidth, naturalHeight: el.naturalHeight, complete: el.complete, src: el.src})"
                )
            except Exception as e:
                logger.debug(f"Image inspection notice for '{title}': {e}")
                img_info = {"naturalWidth": 0, "naturalHeight": 0, "complete": False, "src": ""}

        # 3. Prices
        # In Magento clearance:
        # If discounted, .old-price has original price, .special-price has sale price
        old_price_el = card.locator(ClearanceLocators.PRODUCT_CARD_OLD_PRICE).first
        old_price_str = old_price_el.inner_text().strip() if old_price_el.count() > 0 else ""
        old_price_val = self.parse_price(old_price_str)

        special_price_el = card.locator(ClearanceLocators.PRODUCT_CARD_SPECIAL_PRICE).first
        if special_price_el.count() > 0:
            sale_price_str = special_price_el.inner_text().strip()
        else:
            # If no special-price element, the sale/current price is in the price container
            reg_price_el = card.locator(ClearanceLocators.PRODUCT_CARD_PRICE_REGULAR).first
            sale_price_str = reg_price_el.inner_text().strip() if reg_price_el.count() > 0 else ""
        sale_price_val = self.parse_price(sale_price_str)

        # 4. Badges
        # Discount badge (e.g. '45% Off')
        disc_el = card.locator(ClearanceLocators.PRODUCT_CARD_DISCOUNT_BADGE).first
        discount_badge_text = disc_el.inner_text().strip() if disc_el.count() > 0 else ""
        displayed_discount_pct: Optional[int] = None
        if discount_badge_text:
            pct_match = re.search(r"(\d+)\s*%", discount_badge_text)
            if pct_match:
                displayed_discount_pct = int(pct_match.group(1))

        # Clearance badge
        clearance_el = card.locator(ClearanceLocators.PRODUCT_CARD_CLEARANCE_BADGE).first
        clearance_badge_text = clearance_el.inner_text().strip() if clearance_el.count() > 0 else ""

        # 5. Explore Options CTA
        explore_cta_el = card.locator(ClearanceLocators.PRODUCT_CARD_EXPLORE_CTA).first
        has_explore_cta = explore_cta_el.count() > 0 and explore_cta_el.is_visible()
        cta_text = explore_cta_el.inner_text().strip() if explore_cta_el.count() > 0 else ""

        # 6. Mathematical discount verification: ((original - sale) / original) * 100
        calculated_discount_pct: Optional[float] = None
        if old_price_val is not None and sale_price_val is not None and old_price_val > 0:
            calculated_discount_pct = ((old_price_val - sale_price_val) / old_price_val) * 100

        details = {
            "title": title,
            "image": img_info,
            "old_price_str": old_price_str,
            "old_price": old_price_val,
            "sale_price_str": sale_price_str,
            "sale_price": sale_price_val,
            "discount_badge": discount_badge_text,
            "displayed_discount_pct": displayed_discount_pct,
            "calculated_discount_pct": calculated_discount_pct,
            "clearance_badge": clearance_badge_text,
            "has_explore_cta": has_explore_cta,
            "cta_text": cta_text,
            "has_both_prices": (old_price_val is not None and sale_price_val is not None),
            "is_sale_lower": (
                (sale_price_val < old_price_val)
                if (old_price_val is not None and sale_price_val is not None)
                else None
            ),
        }
        return details

    def get_all_products_details(self) -> List[Dict[str, Any]]:
        """Extract dynamic card details from all rendered product cards."""
        cards = self.get_product_cards()
        logger.info(f"Extracting details from {len(cards)} visible product cards...")
        return [self.get_product_card_details(card) for card in cards]

    # =========================================================================
    # Sorter Dropdown & Ordering
    # =========================================================================

    def get_available_sort_options(self) -> List[Dict[str, Any]]:
        """Extract available options from the sorter dropdown."""
        sorter = self.page.locator(ClearanceLocators.SORTER_DROPDOWN).first
        expect(sorter).to_be_visible(timeout=5000)
        options: List[Dict[str, Any]] = []
        for opt in sorter.locator("option").all():
            txt = opt.inner_text().strip()
            val = opt.get_attribute("value") or ""
            if txt and txt.lower() != "sort by":
                options.append({
                    "text": txt,
                    "value": val,
                    "selected": opt.evaluate("el => el.selected"),
                })
        logger.info(f"Available sort options: {options}")
        return options

    def select_sort_option(self, option_label_or_value: str) -> str:
        """Select a sort option on the sorter dropdown and wait for grid reload.
        Matches by label substring or exact value.
        """
        logger.info(f"Selecting sort option: '{option_label_or_value}'")
        sorter = self.page.locator(ClearanceLocators.SORTER_DROPDOWN).first
        sorter.scroll_into_view_if_needed()

        options = sorter.locator("option").all()
        target_val = ""
        for opt in options:
            txt = opt.inner_text().strip()
            val = opt.get_attribute("value") or ""
            if option_label_or_value.lower() in txt.lower() or option_label_or_value.lower() == val.lower():
                target_val = val
                break

        if target_val:
            sorter.select_option(value=target_val)
        else:
            sorter.select_option(label=option_label_or_value)

        # Wait for grid reload / URL update
        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(3000)

        current_url = self.get_current_url()
        logger.info(f"Sort option applied. Resulting URL: '{current_url}'")
        return current_url

    def get_current_sorter_value(self) -> str:
        """Return the current value selected in the sorter dropdown."""
        sorter = self.page.locator(ClearanceLocators.SORTER_DROPDOWN).first
        return sorter.input_value()

    # =========================================================================
    # Editorial Sections & Customer Reviews
    # =========================================================================

    def get_editorial_sections(self) -> Dict[str, Locator]:
        """Return locators for the customer reviews section and all three editorial headings."""
        return {
            "customer_reviews": self.page.locator(ClearanceLocators.CUSTOMER_REVIEWS_HEADING).first,
            "quality": self.page.locator(ClearanceLocators.EDITORIAL_QUALITY_HEADING).first,
            "find": self.page.locator(ClearanceLocators.EDITORIAL_FIND_HEADING).first,
            "tips": self.page.locator(ClearanceLocators.EDITORIAL_TIPS_HEADING).first,
            "common_questions": self.page.locator(ClearanceLocators.FAQ_COMMON_QUESTIONS_HEADING).first,
        }

    # =========================================================================
    # Common Questions FAQ Accordion
    # =========================================================================

    def wait_for_faq_section_ready(self, timeout: int = 15000) -> None:
        """Wait for the FAQ section and collapsible widgets to be rendered and initialized."""
        try:
            self.page.wait_for_selector(ClearanceLocators.FAQ_ITEMS, state="visible", timeout=timeout)
            # Wait for Magento collapsible widget initialization (data-collapsible='true' or aria-expanded present)
            self.page.wait_for_function(
                "() => { const items = document.querySelectorAll('.faq_wrapper'); "
                "return items.length > 0 && Array.from(items).some(el => el.hasAttribute('data-collapsible') || el.hasAttribute('aria-expanded')); }",
                timeout=timeout,
            )
        except Exception as e:
            logger.debug(f"Notice waiting for FAQ section ready: {e}")

    def get_faq_items(self) -> List[Locator]:
        """Return list of all FAQ item locators (.faq_wrapper)."""
        self.wait_for_faq_section_ready()
        return self.page.locator(ClearanceLocators.FAQ_ITEMS).all()

    def get_faq_items_count(self) -> int:
        """Return count of FAQ items found on the page."""
        self.wait_for_faq_section_ready()
        return self.page.locator(ClearanceLocators.FAQ_ITEMS).count()

    def expand_faq_item(self, index: int) -> Dict[str, Any]:
        """Expand the FAQ accordion item at index and return its details."""
        self.wait_for_faq_section_ready()
        items = self.get_faq_items()
        assert index < len(items), f"FAQ index {index} out of bounds (found {len(items)} items)."
        item = items[index]

        # Scroll item into view
        item.scroll_into_view_if_needed()
        self.wait_for_timeout(300)

        q_el = item.locator(ClearanceLocators.FAQ_QUESTION).first
        a_el = item.locator(ClearanceLocators.FAQ_ANSWER).first
        expect(q_el).to_be_visible(timeout=5000)
        q_text = q_el.inner_text().strip()

        # Check if already expanded
        is_already_expanded = (
            item.get_attribute("aria-expanded") == "true"
            or "active" in (item.get_attribute("class") or "")
            or a_el.is_visible()
        )

        if not is_already_expanded:
            logger.info(f"Clicking FAQ item {index + 1} to expand: '{q_text}'")
            q_el.scroll_into_view_if_needed()
            self.wait_for_timeout(200)

            try:
                q_el.click(timeout=3000)
            except Exception as e:
                logger.debug(f"Standard click failed: {e}; attempting force click...")
                span_el = q_el.locator("span").first
                if span_el.count() > 0 and span_el.is_visible():
                    span_el.click(force=True)
                else:
                    q_el.click(force=True)

            try:
                a_el.wait_for(state="visible", timeout=5000)
            except Exception:
                # If still not visible, re-click once (in case of double-init or missed click)
                if not a_el.is_visible():
                    logger.warning(f"FAQ item {index + 1} answer not visible after initial click. Retrying click...")
                    q_el.click(force=True)
                    try:
                        a_el.wait_for(state="visible", timeout=5000)
                    except Exception:
                        pass

        # Allow animation to settle
        self.wait_for_timeout(300)

        is_visible = a_el.is_visible()
        a_text = a_el.inner_text().strip() if is_visible else ""
        item_class = item.get_attribute("class") or ""
        aria_expanded = item.get_attribute("aria-expanded") or q_el.get_attribute("aria-expanded")

        logger.info(
            f"Expanded FAQ {index + 1}: '{q_text}' -> Answer visible={is_visible}, "
            f"Active class={'active' in item_class}, aria-expanded={aria_expanded}"
        )
        return {
            "index": index,
            "question": q_text,
            "answer": a_text,
            "is_visible": is_visible,
            "item_class": item_class,
            "aria_expanded": aria_expanded,
        }

