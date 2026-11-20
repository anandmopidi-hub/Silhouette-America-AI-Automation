"""Page Object Model for Silhouette America Header Navigation.

Encapsulates header menu navigation, mega-menu dropdowns, child link discovery,
navigation response validation, and 404 error detection.
"""
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from playwright.sync_api import Locator, Page, Response, TimeoutError as PlaywrightTimeoutError

from config.config import Config
from locators.header_locators import HeaderLocators
from pages.base_page import BasePage
from utils.logger import logger


class HeaderPage(BasePage):
    """Page Object representing the Silhouette America Header Navigation module."""

    # Target 8 top-level menu keys mapped to their display names and primary link locators
    TOP_LEVEL_MENU_MAP: Dict[str, Dict[str, str]] = {
        "Shop": {
            "key": "shopmenu",
            "type": "link",
            "primary_locator": HeaderLocators.SHOP_LINK,
            "fallback_url": "eshop",
        },
        "Software": {
            "key": "softwaremenu",
            "type": "dropdown",
            "panel": HeaderLocators.SOFTWARE_PANEL,
            "primary_locator": HeaderLocators.SOFTWARE_PRIMARY_LINK,
            "fallback_url": "software",
        },
        "Machine": {
            "key": "machinemenu",
            "type": "dropdown",
            "panel": HeaderLocators.MACHINE_PANEL,
            "primary_locator": HeaderLocators.MACHINE_PRIMARY_LINK,
            "fallback_url": "machines",
        },
        "Tools & Mats": {
            "key": "toolmatmmenu",
            "type": "dropdown",
            "panel": HeaderLocators.TOOLS_MATS_PANEL,
            "primary_locator": HeaderLocators.TOOLS_MATS_PRIMARY_LINK,
            "fallback_url": "machine-tools-mats",
        },
        "Materials": {
            "key": "materialmenu",
            "type": "dropdown",
            "panel": HeaderLocators.MATERIALS_PANEL,
            "primary_locator": HeaderLocators.MATERIALS_PRIMARY_LINK,
            "fallback_url": "material",
        },
        "Accessories": {
            "key": "accemenu",
            "type": "dropdown",
            "panel": HeaderLocators.ACCESSORIES_PANEL,
            "primary_locator": HeaderLocators.ACCESSORIES_PRIMARY_LINK,
            "fallback_url": "accessories-parts",
        },
        "Club Silhouette": {
            "key": "clubsilmenu",
            "type": "link",
            "primary_locator": HeaderLocators.CLUB_SILHOUETTE_LINK,
            "fallback_url": "club-silhouette",
        },
        "Clearance 40% Off": {
            "key": "clearmenu",
            "type": "dropdown",
            "panel": HeaderLocators.CLEARANCE_PANEL,
            "primary_locator": HeaderLocators.CLEARANCE_PRIMARY_LINK,
            "fallback_url": "clearance",
        },
    }

    def __init__(self, page: Page, config: Optional[Config] = None) -> None:
        super().__init__(page, config)

    # =========================================================================
    # Navigation & Initial Page Setup
    # =========================================================================

    def open_homepage(self) -> None:
        """Navigate to the production homepage, resolve Cloudflare challenge,
        dismiss cookie consent, and ensure header is loaded.
        """
        logger.info("Opening production homepage: base URL")
        self.goto("")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()

        # Ensure header/branding is visible
        try:
            self.page.wait_for_selector(HeaderLocators.LOGO, state="visible", timeout=12000)
        except Exception:
            pass

    def dismiss_cookie_consent_if_present(self, timeout: int = 2500) -> bool:
        """Detect and click 'I Agree' on cookie consent banner if visible."""
        try:
            btn = self.page.locator(HeaderLocators.COOKIE_ACCEPT_BUTTON).first
            if btn.is_visible(timeout=timeout):
                logger.info("Cookie consent banner detected. Clicking 'I Agree'...")
                btn.click(timeout=timeout)
                btn.wait_for(state="hidden", timeout=timeout)
                logger.info("Cookie consent banner dismissed.")
                return True
        except Exception as e:
            logger.debug(f"Cookie consent handling notice: {e}")
        return False

    def is_404_page(self, target_page: Optional[Page] = None) -> bool:
        """Check whether the active page or target page displays a 404 or Page Not Found error."""
        active_page = target_page or self.page
        title = active_page.title().lower()
        if "404" in title or "page not found" in title:
            return True

        try:
            err_loc = active_page.locator(HeaderLocators.NOT_FOUND_INDICATORS).first
            if err_loc.is_visible(timeout=1000):
                return True
        except Exception:
            pass

        return False

    def get_destination_heading(self, target_page: Optional[Page] = None) -> str:
        """Capture the primary heading (h1 or .page-title) of the current page."""
        active_page = target_page or self.page
        try:
            h1 = active_page.locator(HeaderLocators.PAGE_HEADING).first
            if h1.is_visible(timeout=3000):
                return h1.inner_text().strip().split("\n")[0].strip()
        except Exception:
            pass
        return ""

    # =========================================================================
    # E2E-HDR-001: Top-Level Navigation Links
    # =========================================================================

    def get_top_level_navigation_items(self) -> List[Dict[str, Any]]:
        """Identify and extract metadata for all 8 required top-level navigation items dynamically.
        Returns:
            List of dicts containing item label, data-menu key, element tag, and href if present.
        """
        logger.info("Inspecting top-level header navigation items dynamically...")
        items: List[Dict[str, Any]] = []

        for label, meta in self.TOP_LEVEL_MENU_MAP.items():
            key = meta["key"]
            item_loc = self.page.locator(f"li[data-menu='{key}']").first
            assert item_loc.count() > 0, f"Top-level header menu item '{label}' (data-menu='{key}') not found in DOM."

            # Inspect element
            btn_or_link = item_loc.locator("button, a").first
            tag_name = btn_or_link.evaluate("e => e.tagName").upper()
            href = btn_or_link.get_attribute("href") or ""
            visible_text = item_loc.inner_text().strip().split("\n")[0].strip()

            items.append({
                "label": label,
                "menu_key": key,
                "type": meta["type"],
                "tag": tag_name,
                "href": href,
                "visible_text": visible_text,
            })
            logger.info(f"Identified top-level nav item: '{label}' -> Key: '{key}', Tag: {tag_name}, Href: '{href}'")

        assert len(items) == 8, f"Expected 8 top-level navigation items, found {len(items)}"
        return items

    def navigate_to_top_level_menu(self, menu_label: str) -> Dict[str, Any]:
        """Navigate to the destination page for a specific top-level menu item.

        Handles direct links (Shop, Club Silhouette) and mega-menu categories
        (Software, Machine, Tools & Mats, Materials, Accessories, Clearance)
        by clicking the primary category landing link.

        Returns:
            Dict containing navigation metrics:
            {
                "menu_label": str,
                "menu_key": str,
                "target_href": str,
                "final_url": str,
                "status": int,
                "title": str,
                "heading": str,
                "is_404": bool,
                "success": bool
            }
        """
        assert menu_label in self.TOP_LEVEL_MENU_MAP, f"Unknown top-level menu item: '{menu_label}'"
        meta = self.TOP_LEVEL_MENU_MAP[menu_label]
        key = meta["key"]
        menu_type = meta["type"]
        logger.info(f"Navigating to top-level menu item: '{menu_label}' ({key})")

        # Ensure we are on homepage first
        if self.get_current_url().rstrip("/") != self.config.base_url.rstrip("/"):
            self.open_homepage()

        item_el = self.page.locator(f"li[data-menu='{key}']").first
        assert item_el.is_visible(timeout=5000), f"Menu item '{menu_label}' not visible in header."

        captured_status = 200
        target_href = ""

        if menu_type == "link":
            # Direct link click
            link_el = item_el.locator("a").first
            target_href = link_el.get_attribute("href") or meta["fallback_url"]
            logger.info(f"Clicking direct link for '{menu_label}' (href: {target_href})...")

            try:
                with self.page.expect_navigation(wait_until="domcontentloaded", timeout=15000) as nav_info:
                    link_el.click()
                resp = nav_info.value
                if resp:
                    captured_status = resp.status
            except Exception as e:
                logger.debug(f"Direct click notice for '{menu_label}': {e}")
                self.goto(target_href, wait_until="domcontentloaded")

        else:
            # Dropdown mega-menu: hover/click to open panel, then click primary category link
            item_el.hover()
            self.wait_for_timeout(400)
            panel_loc = self.page.locator(meta["panel"]).first
            if not panel_loc.is_visible(timeout=2000):
                # Click to toggle if hover didn't open
                item_el.locator("button, a").first.click()
                self.wait_for_timeout(400)

            primary_link = self.page.locator(meta["primary_locator"]).first
            assert primary_link.count() > 0, f"Primary landing link not found for '{menu_label}' using '{meta['primary_locator']}'"
            target_href = primary_link.get_attribute("href") or meta["fallback_url"]
            logger.info(f"Clicking primary category link for '{menu_label}' (href: {target_href})...")

            try:
                with self.page.expect_navigation(wait_until="domcontentloaded", timeout=15000) as nav_info:
                    primary_link.click(force=True)
                resp = nav_info.value
                if resp:
                    captured_status = resp.status
            except Exception as e:
                logger.debug(f"Dropdown primary link click notice for '{menu_label}': {e}")
                self.goto(target_href, wait_until="domcontentloaded")

        # Destination stabilization
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()

        final_url = self.get_current_url()
        title = self.get_title()
        heading = self.get_destination_heading()
        is_404 = self.is_404_page()
        success = not is_404 and captured_status in [200, 301, 302, 304]

        result = {
            "menu_label": menu_label,
            "menu_key": key,
            "target_href": target_href,
            "final_url": final_url,
            "status": captured_status,
            "title": title,
            "heading": heading,
            "is_404": is_404,
            "success": success,
        }
        logger.info(
            f"Top-Level Nav Result [{menu_label}] -> Status: {captured_status}, "
            f"URL: {final_url}, Heading: '{heading}', Title: '{title}', 404: {is_404}"
        )
        return result

    # =========================================================================
    # Mega-Menu Dropdown Operations (E2E-HDR-002, 003, 004, 005)
    # =========================================================================

    def open_mega_menu(self, menu_key: str) -> Locator:
        """Hover over or click a top-level menu item to reveal its dropdown panel.
        Returns:
            The visible panel Locator.
        """
        logger.info(f"Opening mega-menu dropdown for: '{menu_key}'")
        item = self.page.locator(f"li[data-menu='{menu_key}']").first
        assert item.count() > 0, f"Menu item 'li[data-menu=\"{menu_key}\"]' not found in DOM."

        # Hover over the menu trigger
        item.hover()
        self.wait_for_timeout(400)

        # Identify panel locator
        trigger_btn = item.locator("button, a").first
        panel_id = trigger_btn.get_attribute("aria-controls")
        if panel_id:
            panel = self.page.locator(f"#{panel_id}").first
        else:
            panel = item.locator(".child-menu, .smallpopup, .submenu-panel").first

        if not panel.is_visible(timeout=2000):
            # Click button to toggle open if hover didn't activate
            trigger_btn.click()
            self.wait_for_timeout(500)

        assert panel.is_visible(timeout=5000), f"Mega-menu panel for '{menu_key}' did not become visible."
        logger.info(f"Mega-menu panel for '{menu_key}' is visible.")
        return panel

    def get_mega_menu_child_links(self, panel_locator: Locator) -> List[Dict[str, str]]:
        """Dynamically extract all valid, unique child links from a mega-menu panel.

        Filters out:
        - Empty hrefs
        - '#' and 'javascript:' hrefs
        - Empty link texts (e.g., decorative image banners)
        - Duplicates

        Returns:
            List of dicts: [{"text": str, "href": str, "target": str}]
        """
        links_loc = panel_locator.locator(HeaderLocators.PANEL_CHILD_LINKS)
        count = links_loc.count()
        valid_links: List[Dict[str, str]] = []
        seen_keys = set()

        for i in range(count):
            l = links_loc.nth(i)
            text = l.inner_text().strip().replace("\n", " ")
            href = l.get_attribute("href") or ""
            target = l.get_attribute("target") or "_self"

            # Filter conditions per requirements
            if not href or href.startswith("#") or href.startswith("javascript"):
                continue
            if not text:
                continue

            unique_key = (text.lower(), href.rstrip("/"))
            if unique_key in seen_keys:
                continue
            seen_keys.add(unique_key)

            valid_links.append({
                "text": text,
                "href": href,
                "target": target,
            })

        logger.info(f"Extracted {len(valid_links)} valid unique child links from panel.")
        return valid_links

    def validate_child_link(
        self,
        menu_key: str,
        link_info: Dict[str, str],
    ) -> Dict[str, Any]:
        """Navigate to a child link, validate its destination, and return to original state.

        Handles same-tab navigation and new-tab (target='_blank') popup navigation.
        """
        text = link_info["text"]
        href = link_info["href"]
        target = link_info.get("target", "_self")
        logger.info(f"Validating child link: '{text}' -> {href} (target={target})")

        captured_status = 200
        final_url = ""
        page_title = ""
        heading = ""
        is_404 = False

        if target == "_blank":
            # New tab / popup
            panel = self.open_mega_menu(menu_key)
            target_a = panel.locator(f"a:has-text('{text}')").first
            logger.info(f"Clicking link with target='_blank': expecting popup...")
            with self.page.expect_popup(timeout=15000) as popup_info:
                target_a.click(force=True)
            popup = popup_info.value
            popup.wait_for_load_state("domcontentloaded")

            final_url = popup.url
            page_title = popup.title()
            heading = self.get_destination_heading(target_page=popup)
            is_404 = self.is_404_page(target_page=popup)

            popup.close()
            logger.info(f"Popup validated and closed: URL='{final_url}', Title='{page_title}'")

        else:
            # Same tab navigation
            panel = self.open_mega_menu(menu_key)
            target_a = panel.locator(f"a:has-text('{text}')").first
            if target_a.count() == 0 or not target_a.is_visible(timeout=1000):
                target_a = panel.locator(f"a[href*='{href.split('/')[-1]}']").first

            try:
                with self.page.expect_navigation(wait_until="domcontentloaded", timeout=15000) as nav_info:
                    target_a.click(force=True)
                resp = nav_info.value
                if resp:
                    captured_status = resp.status
            except Exception as e:
                logger.debug(f"Click navigation notice for '{text}': {e}")
                # Fallback to direct navigation if click did not trigger Playwright expect_navigation
                resp = self.goto(href, wait_until="domcontentloaded")
                if resp:
                    captured_status = resp.status

            self.wait_for_dom_content_loaded()
            self.handle_cloudflare_if_present()
            self.dismiss_cookie_consent_if_present()

            final_url = self.get_current_url()
            page_title = self.get_title()
            heading = self.get_destination_heading()
            is_404 = self.is_404_page()

            # Return to original homepage before checking the next link
            logger.info("Returning to homepage for next link...")
            try:
                self.page.go_back(wait_until="domcontentloaded", timeout=8000)
                self.wait_for_dom_content_loaded()
                self.dismiss_cookie_consent_if_present()
            except Exception:
                pass
            if self.get_current_url().rstrip("/") != self.config.base_url.rstrip("/"):
                self.open_homepage()

        success = not is_404 and captured_status in [200, 301, 302, 304]
        res = {
            "text": text,
            "href": href,
            "final_url": final_url,
            "status": captured_status,
            "title": page_title,
            "heading": heading,
            "is_404": is_404,
            "success": success,
        }
        logger.info(f"Child link validation result: {res}")
        return res

    def validate_dropdown_mega_menu(
        self,
        menu_key: str,
        sample_limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Comprehensive workflow to open a mega-menu, extract child links,
        and validate their destinations.
        """
        logger.info(f"========== Validating Dropdown Mega-Menu for '{menu_key}' ==========")
        self.open_homepage()

        # Step 2 & 3: Open mega-menu and verify panel is visible
        panel = self.open_mega_menu(menu_key)

        # Step 5 & 6: Extract child links dynamically
        child_links = self.get_mega_menu_child_links(panel)
        assert len(child_links) > 0, f"No child links extracted from mega-menu '{menu_key}'"
        logger.info(f"Found {len(child_links)} child links to validate under '{menu_key}'.")

        # If sample_limit is provided, test up to sample_limit, otherwise test all
        links_to_test = child_links[:sample_limit] if sample_limit else child_links
        results: List[Dict[str, Any]] = []

        for idx, link_info in enumerate(links_to_test):
            logger.info(f"--- Validating link {idx + 1}/{len(links_to_test)}: '{link_info['text']}' ---")
            val_res = self.validate_child_link(menu_key=menu_key, link_info=link_info)
            results.append(val_res)
            assert val_res["success"], (
                f"Validation failed for child link '{link_info['text']}' -> {link_info['href']}: "
                f"Status={val_res['status']}, 404={val_res['is_404']}, URL={val_res['final_url']}"
            )

        logger.info(f"All {len(results)} tested child links validated successfully for '{menu_key}'.")
        return results

    # =========================================================================
    # E2E-HDR-006: Clearance 40% Off Promotional Redirection
    # =========================================================================

    def validate_clearance_promotional_redirection(self) -> Dict[str, Any]:
        """Validate the Clearance 40% Off promotional header link and destination page."""
        logger.info("Executing Clearance 40% Off Promotional Redirection validation...")
        self.open_homepage()

        # Step 2: Locate the Clearance item
        clear_item = self.page.locator(HeaderLocators.CLEARANCE_ITEM).first
        assert clear_item.is_visible(timeout=5000), "Clearance 40% Off item not visible in header."

        # Step 3 & 4: Open clearance dropdown and locate Sale Items / Clearance link
        clear_item.hover()
        self.wait_for_timeout(400)
        clear_panel = self.page.locator(HeaderLocators.CLEARANCE_PANEL).first
        if not clear_panel.is_visible(timeout=2000):
            clear_item.locator("button, a").first.click()
            self.wait_for_timeout(400)

        sale_link = self.page.locator(HeaderLocators.CLEARANCE_PRIMARY_LINK).first
        if sale_link.count() == 0:
            sale_link = clear_panel.locator("a[href*='clearance'], a").first
        assert sale_link.count() > 0, "Clearance destination link not found in clearance panel."
        href = sale_link.get_attribute("href") or "https://www.silhouetteamerica.com/clearance"
        logger.info(f"Clicking Clearance promotional link: {href}...")

        captured_status = 200
        try:
            with self.page.expect_navigation(wait_until="domcontentloaded", timeout=15000) as nav_info:
                sale_link.click(force=True)
            resp = nav_info.value
            if resp:
                captured_status = resp.status
        except Exception as e:
            logger.debug(f"Clearance navigation notice: {e}")
            self.goto("clearance", wait_until="domcontentloaded")

        # Step 6: Wait for destination page to load
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()

        # Step 7, 8, 9, 10, 11: Capture destination metrics
        final_url = self.get_current_url()
        title = self.get_title()
        heading = self.get_destination_heading()
        is_404 = self.is_404_page()

        # Check product items or clearance category content
        product_count = self.page.locator(HeaderLocators.CLEARANCE_PRODUCT_ITEMS).count()

        assert "clearance" in final_url.lower(), f"Expected 'clearance' in final URL, got '{final_url}'"
        assert not is_404, f"Clearance page returned 404 or page not found: '{final_url}'"
        assert heading.lower() == "clearance" or "clearance" in title.lower(), (
            f"Expected Clearance heading or title, got heading='{heading}', title='{title}'"
        )

        result = {
            "target_href": href,
            "final_url": final_url,
            "status": captured_status,
            "title": title,
            "heading": heading,
            "product_count": product_count,
            "is_404": is_404,
            "success": True,
        }
        logger.info(f"Clearance validation result: {result}")
        return result
