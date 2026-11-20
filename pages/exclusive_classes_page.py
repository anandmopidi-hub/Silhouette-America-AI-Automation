"""Page Object for Silhouette America Exclusive Classes module.

Target URL: https://www.silhouetteamerica.com/exclusive-class
"""
from datetime import datetime
import re
from typing import Any, Dict, List, Optional
from playwright.sync_api import Locator, Page, Response

from locators.exclusive_classes_locators import ExclusiveClassesLocators
from pages.base_page import BasePage
from utils.logger import logger


class ExclusiveClassesPage(BasePage):
    """Page Object covering Silhouette America Exclusive Classes (/exclusive-class)."""

    def __init__(self, page: Page, config: Optional[Any] = None) -> None:
        super().__init__(page=page, config=config)
        self.exclusive_classes_path = "exclusive-class"

    # =========================================================================
    # Navigation Methods
    # =========================================================================

    def open_exclusive_classes_page(self) -> Optional[Response]:
        """Directly navigate to the Exclusive Classes page."""
        logger.info(f"Navigating to Exclusive Classes page: {self.exclusive_classes_path}")
        response = self.goto(self.exclusive_classes_path, wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.wait_for_grid_loaded()
        return response

    def navigate_from_homepage(self) -> bool:
        """Navigate to Exclusive Classes from the Homepage via Header Navigation link.

        Flow:
        1. Open application homepage.
        2. Wait for DOMContentLoaded.
        3. Hover over 'Resources' top menu.
        4. Locate the 'Exclusive Classes' navigation link.
        5. Click the link and wait for navigation.
        """
        logger.info("Opening homepage for navigation to Exclusive Classes...")
        self.goto("", wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()

        # Step 3: Hover 'Resources' desktop menu trigger
        res_trigger = self.page.locator(ExclusiveClassesLocators.NAV_RESOURCES_MENU).first
        if not res_trigger.is_visible():
            res_trigger = self.page.locator("nav.desktop-menu a:has-text('Resources'), a.fmlink:has-text('Resources')").first

        logger.info("Hovering over 'Resources' navigation menu item...")
        res_trigger.hover()
        self.wait_for_timeout(600)

        # Step 4: Locate actual Exclusive Classes link inside the opened Resources panel
        link = self.page.locator(ExclusiveClassesLocators.NAV_EXCLUSIVE_CLASSES_LINK).first
        try:
            link.wait_for(state="visible", timeout=4000)
        except Exception:
            # If panel didn't open via hover alone, click trigger button to toggle
            logger.info("Resources panel not opened on hover; clicking trigger button...")
            btn = res_trigger.locator("button, a").first
            if btn.count() > 0:
                btn.click()
            else:
                res_trigger.click()
            self.wait_for_timeout(600)
            link.wait_for(state="visible", timeout=5000)

        assert link.is_visible(), (
            "Actual 'Exclusive Classes' navigation link is not visible in Header menu."
        )

        logger.info(f"Clicking 'Exclusive Classes' navigation link (href='{link.get_attribute('href')}')...")
        link.click()
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.wait_for_grid_loaded()

        curr_url = self.get_current_url()
        logger.info(f"Successfully navigated to: {curr_url}")
        return "exclusive-class" in curr_url

    # =========================================================================
    # Page Landing & Banner Verification
    # =========================================================================

    def get_banner_text(self) -> str:
        """Extract the full hero banner heading text."""
        hero = self.page.locator(ExclusiveClassesLocators.PAGE_HERO_SECTION).first
        if hero.count() > 0:
            lines = hero.locator(ExclusiveClassesLocators.PAGE_HERO_TITLE_LINES).all()
            if lines:
                return " ".join(line.inner_text().strip() for line in lines)
            return hero.inner_text().strip()
        return ""

    def is_banner_text_visible(self, expected_banner: str = "Exclusive Classes for Exclusive Members") -> bool:
        """Verify that the hero banner text matches expected text."""
        actual_text = self.get_banner_text()
        logger.info(f"Retrieved hero banner text: '{actual_text}'")
        # Normalize whitespace and compare case-insensitively
        norm_actual = re.sub(r"\s+", " ", actual_text).strip().lower()
        norm_expected = re.sub(r"\s+", " ", expected_banner).strip().lower()
        return norm_expected in norm_actual or norm_actual in norm_expected

    def get_section_title(self) -> str:
        """Extract section title: 'Catch up on past classes'."""
        title_el = self.page.locator(ExclusiveClassesLocators.ARCHIVE_SECTION_TITLE).first
        if title_el.count() > 0 and title_el.is_visible(timeout=3000):
            return title_el.inner_text().strip()
        return ""

    def is_section_title_visible(self, expected_title: str = "Catch up on past classes") -> bool:
        """Verify section title visibility and text match."""
        actual_title = self.get_section_title()
        logger.info(f"Retrieved section title: '{actual_title}'")
        return expected_title.lower() in actual_title.lower()

    # =========================================================================
    # Class Cards Grid & Details
    # =========================================================================

    def wait_for_grid_loaded(self, timeout_ms: int = 10000) -> None:
        """Wait for the past classes archive grid and card items to finish loading."""
        try:
            # Wait for skeleton loader to disappear
            spinner = self.page.locator(ExclusiveClassesLocators.LOADING_SPINNER)
            if spinner.count() > 0:
                spinner.first.wait_for(state="hidden", timeout=timeout_ms)
        except Exception as e:
            logger.debug(f"Wait for spinner notice: {e}")

        # Small UI stabilization pause
        self.wait_for_timeout(500)

    def get_class_card_count(self) -> int:
        """Return the number of rendered real class cards (excluding skeletons/empty items)."""
        cards = self.page.locator(ExclusiveClassesLocators.CLASS_CARDS)
        return cards.count()

    def get_class_card_titles(self) -> List[str]:
        """Extract all visible class card titles."""
        cards = self.page.locator(ExclusiveClassesLocators.CLASS_CARDS)
        titles = []
        for i in range(cards.count()):
            card = cards.nth(i)
            t_loc = card.locator(ExclusiveClassesLocators.CARD_TITLE).first
            if t_loc.count() > 0:
                titles.append(t_loc.inner_text().strip())
        return titles

    def get_class_card_dates(self) -> List[str]:
        """Extract publication dates for rendered class cards."""
        cards = self.page.locator(ExclusiveClassesLocators.CLASS_CARDS)
        dates = []
        for i in range(cards.count()):
            card = cards.nth(i)
            d_loc = card.locator(ExclusiveClassesLocators.CARD_DATE).first
            if d_loc.count() > 0:
                dates.append(d_loc.inner_text().strip())
        return dates

    def get_class_card_details(self) -> List[Dict[str, Any]]:
        """Extract full details (title, date, duration) for each rendered class card."""
        cards = self.page.locator(ExclusiveClassesLocators.CLASS_CARDS)
        items = []
        for i in range(cards.count()):
            card = cards.nth(i)
            t_loc = card.locator(ExclusiveClassesLocators.CARD_TITLE).first
            d_loc = card.locator(ExclusiveClassesLocators.CARD_DATE).first
            dur_loc = card.locator(ExclusiveClassesLocators.CARD_DURATION).first

            title = t_loc.inner_text().strip() if t_loc.count() > 0 else ""
            date_str = d_loc.inner_text().strip() if d_loc.count() > 0 else ""
            duration = dur_loc.inner_text().strip() if dur_loc.count() > 0 else ""

            items.append({
                "index": i,
                "title": title,
                "date": date_str,
                "duration": duration,
            })
        return items

    # =========================================================================
    # Search Functionality
    # =========================================================================

    def identify_valid_search_keyword(self) -> str:
        """Dynamically identify a suitable search keyword from available class titles.

        Prevents hardcoding values that might not exist in production catalog.
        """
        titles = self.get_class_card_titles()
        assert len(titles) > 0, "Cannot identify search keyword: no class cards rendered."

        # Pick candidate words of length >= 4 that are alphanumeric from the first few titles
        for title in titles:
            words = re.findall(r"\b[A-Za-z]{4,}\b", title)
            for w in words:
                if w.lower() not in ("maker", "studio", "with", "from", "that", "this"):
                    logger.info(f"Dynamically identified valid search keyword: '{w}' (from title '{title}')")
                    return w

        # Fallback to first alphanumeric token >= 4 characters
        first_token = re.findall(r"\b[A-Za-z]{4,}\b", titles[0])
        keyword = first_token[0] if first_token else "Studio"
        logger.info(f"Dynamically selected keyword: '{keyword}'")
        return keyword

    def search_classes(self, keyword: str) -> None:
        """Enter a search query into the classes search input and trigger search."""
        logger.info(f"Performing class search with keyword: '{keyword}'")
        inp = self.page.locator(ExclusiveClassesLocators.SEARCH_INPUT).first
        assert inp.is_visible(timeout=5000), "Classes search input is not visible."

        inp.click()
        inp.fill("")
        inp.fill(keyword)
        # Trigger search via Enter key (which submits search on this custom filter component)
        inp.press("Enter")
        self.wait_for_timeout(1000)
        self.wait_for_grid_loaded()

    def clear_search(self) -> None:
        """Clear search input and restore full catalog."""
        logger.info("Clearing classes search input...")
        inp = self.page.locator(ExclusiveClassesLocators.SEARCH_INPUT).first
        inp.fill("")
        inp.press("Enter")
        self.wait_for_timeout(1000)
        self.wait_for_grid_loaded()

    # =========================================================================
    # Empty State Verification
    # =========================================================================

    def get_empty_state_message(self) -> str:
        """Extract the text of the empty-state message."""
        msg_loc = self.page.locator(ExclusiveClassesLocators.EMPTY_STATE_MESSAGE).first
        if msg_loc.count() > 0 and msg_loc.is_visible(timeout=3000):
            return msg_loc.inner_text().strip()

        # Fallback to empty item text
        item_loc = self.page.locator(ExclusiveClassesLocators.EMPTY_STATE_ITEM).first
        if item_loc.count() > 0 and item_loc.is_visible(timeout=3000):
            return item_loc.inner_text().strip()
        return ""

    def is_empty_state_displayed(self) -> bool:
        """Check if empty state is visible and 0 class cards are rendered."""
        card_count = self.get_class_card_count()
        msg = self.get_empty_state_message()
        is_empty = card_count == 0 and len(msg) > 0
        logger.info(f"Empty state check: card_count={card_count}, message='{msg}', is_empty={is_empty}")
        return is_empty

    # =========================================================================
    # Sorting & Filters
    # =========================================================================

    def open_sort_dropdown_if_closed(self) -> None:
        """Open the custom sort dropdown menu."""
        toggle = self.page.locator(ExclusiveClassesLocators.SORT_TOGGLE_BUTTON).first
        expanded = toggle.get_attribute("aria-expanded")
        if expanded != "true":
            logger.info("Opening custom sort dropdown menu...")
            toggle.dispatch_event("click")
            self.wait_for_timeout(400)

    def get_available_sort_options(self) -> List[str]:
        """Dynamically extract all available sorting option labels from the dropdown."""
        self.open_sort_dropdown_if_closed()
        options = self.page.locator(ExclusiveClassesLocators.SORT_OPTIONS)
        opt_texts = [options.nth(i).inner_text().strip() for i in range(options.count())]
        logger.info(f"Dynamically discovered sort options: {opt_texts}")
        return opt_texts

    def get_current_sort_label(self) -> str:
        """Get the currently selected sort option label text."""
        label_el = self.page.locator(ExclusiveClassesLocators.SORT_CURRENT_LABEL).first
        if label_el.count() > 0:
            return label_el.inner_text().strip()
        return ""

    def select_sort_option(self, option_text: str = "Latest added") -> bool:
        """Select a sorting option from the custom sort menu by text.

        Args:
            option_text: Name of the sort option (e.g., 'Latest added', 'Oldest', 'Title: A to Z').
        """
        logger.info(f"Selecting sort option: '{option_text}'")
        self.open_sort_dropdown_if_closed()

        opt = self.page.locator(f"{ExclusiveClassesLocators.SORT_OPTIONS}:has-text('{option_text}')").first
        assert opt.count() > 0, f"Sort option '{option_text}' not found in dropdown."

        opt.dispatch_event("click")
        self.wait_for_timeout(1000)
        self.wait_for_grid_loaded()

        current_label = self.get_current_sort_label()
        logger.info(f"Current sort label after selection: '{current_label}'")
        return option_text.lower() in current_label.lower()

    def verify_chronological_order_newest_first(self) -> bool:
        """Verify that rendered class cards are ordered newest first (descending).

        Parses publication dates (e.g., 'Oct 7, 2026', 'Sep 16, 2026').
        """
        dates_raw = self.get_class_card_dates()
        logger.info(f"Raw dates extracted for ordering verification: {dates_raw}")
        if len(dates_raw) < 2:
            logger.warning("Fewer than 2 dates available to verify ordering.")
            return True

        parsed_dates = []
        for d_str in dates_raw:
            try:
                # Format on cards: 'Oct 7, 2026', 'Sep 16, 2026'
                dt = datetime.strptime(d_str.strip(), "%b %d, %Y")
                parsed_dates.append(dt)
            except Exception as e:
                logger.warning(f"Failed to parse date string '{d_str}': {e}")

        if len(parsed_dates) >= 2:
            for idx in range(len(parsed_dates) - 1):
                assert parsed_dates[idx] >= parsed_dates[idx + 1], (
                    f"Date ordering violation at index {idx}: {parsed_dates[idx]} is older than {parsed_dates[idx + 1]}"
                )
            logger.info("Verified that class cards are strictly in chronological newest-first order.")
            return True

        return False
