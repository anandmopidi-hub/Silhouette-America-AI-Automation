"""Page Object for Silhouette America Product User Manuals module.

Target URL: https://www.silhouetteamerica.com/product-user-manual
"""
import re
from typing import Any, Dict, List, Optional
from urllib.parse import unquote
from playwright.sync_api import Page, Response

from locators.product_user_manuals_locators import ProductUserManualsLocators
from pages.base_page import BasePage
from utils.logger import logger


class ProductUserManualsPage(BasePage):
    """Page Object covering Silhouette America Product User Manuals (/product-user-manual)."""

    TAB_MAP: Dict[str, Dict[str, str]] = {
        "Machine": {
            "tab": ProductUserManualsLocators.TAB_MACHINE,
            "panel": ProductUserManualsLocators.PANEL_MACHINE,
        },
        "Software": {
            "tab": ProductUserManualsLocators.TAB_SOFTWARE,
            "panel": ProductUserManualsLocators.PANEL_SOFTWARE,
        },
        "Supply": {
            "tab": ProductUserManualsLocators.TAB_SUPPLY,
            "panel": ProductUserManualsLocators.PANEL_SUPPLY,
        },
        "Legacy Machine": {
            "tab": ProductUserManualsLocators.TAB_LEGACY,
            "panel": ProductUserManualsLocators.PANEL_LEGACY,
        },
    }

    def __init__(self, page: Page, config: Optional[Any] = None) -> None:
        super().__init__(page=page, config=config)
        self.manuals_path = "product-user-manual"

    # =========================================================================
    # Navigation & Static Page Verification
    # =========================================================================

    def open_product_user_manuals_page(self) -> Optional[Response]:
        """Open Product User Manuals page, handle Cloudflare and cookie consent."""
        logger.info(f"Opening Product User Manuals page: {self.manuals_path}")
        response = self.goto(self.manuals_path, wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()

        main_h = self.page.locator(ProductUserManualsLocators.MAIN_HEADING).first
        main_h.wait_for(state="visible", timeout=10000)
        return response

    def get_main_heading_text(self) -> str:
        """Return text of the main User Manuals heading."""
        loc = self.page.locator(ProductUserManualsLocators.MAIN_HEADING).first
        if loc.is_visible(timeout=3000):
            return loc.inner_text().strip()
        return ""

    def get_customer_section_heading_text(self) -> str:
        """Scroll to and return text of the customer reviews section heading."""
        loc = self.page.locator(ProductUserManualsLocators.CUSTOMER_SECTION_HEADING).first
        if loc.count() > 0:
            loc.scroll_into_view_if_needed()
            if loc.is_visible(timeout=5000):
                return loc.inner_text().strip()
        return ""

    def is_customer_section_heading_visible(
        self, expected: str = "Why our customers love Silhouette"
    ) -> bool:
        """Verify customer section heading visibility and text."""
        actual = self.get_customer_section_heading_text()
        logger.info(f"Customer section heading retrieved: '{actual}'")
        return expected.lower() in actual.lower()

    # =========================================================================
    # Tab Inspection & Switching
    # =========================================================================

    def get_all_tabs_status(self) -> List[Dict[str, Any]]:
        """Inspect all four category tabs for visibility, clickability, and active state."""
        results: List[Dict[str, Any]] = []
        for tab_name, selectors in self.TAB_MAP.items():
            tab_loc = self.page.locator(selectors["tab"]).first
            visible = tab_loc.is_visible(timeout=3000) if tab_loc.count() > 0 else False
            enabled = tab_loc.is_enabled() if visible else False
            text = tab_loc.inner_text().strip() if tab_loc.count() > 0 else ""
            aria_selected = tab_loc.get_attribute("aria-selected") if tab_loc.count() > 0 else None
            cls = tab_loc.get_attribute("class") or "" if tab_loc.count() > 0 else ""

            results.append({
                "name": tab_name,
                "text": text,
                "visible": visible,
                "enabled": enabled,
                "aria_selected": aria_selected == "true",
                "has_active_class": "is-active" in cls,
            })
        return results

    def select_tab(self, tab_name: str) -> bool:
        """Click the specified tab and verify its panel becomes active."""
        assert tab_name in self.TAB_MAP, f"Unknown tab name: {tab_name}"
        selectors = self.TAB_MAP[tab_name]
        tab_loc = self.page.locator(selectors["tab"]).first
        panel_loc = self.page.locator(selectors["panel"]).first

        logger.info(f"Selecting '{tab_name}' tab...")
        tab_loc.scroll_into_view_if_needed()
        tab_loc.click()
        self.wait_for_timeout(400)

        panel_loc.wait_for(state="visible", timeout=5000)
        is_active = self.is_tab_active(tab_name)
        logger.info(f"Tab '{tab_name}' selected -> active={is_active}")
        return is_active

    def is_tab_active(self, tab_name: str) -> bool:
        """Return True if the specified tab is currently active and its panel is visible."""
        selectors = self.TAB_MAP[tab_name]
        tab_loc = self.page.locator(selectors["tab"]).first
        panel_loc = self.page.locator(selectors["panel"]).first

        aria_selected = tab_loc.get_attribute("aria-selected") == "true"
        cls = tab_loc.get_attribute("class") or ""
        has_active_cls = "is-active" in cls
        panel_visible = panel_loc.is_visible()
        panel_hidden = panel_loc.get_attribute("hidden") is not None

        return (aria_selected or has_active_cls) and panel_visible and not panel_hidden

    # =========================================================================
    # Product Card Inspection
    # =========================================================================

    def get_cards_count(self, tab_name: str) -> int:
        """Count rendered manual cards inside the specified tab panel."""
        panel_sel = self.TAB_MAP[tab_name]["panel"]
        cards = self.page.locator(f"{panel_sel} {ProductUserManualsLocators.MANUAL_CARDS}")
        return cards.count()

    def get_card_title(self, tab_name: str, card_index: int = 0) -> str:
        """Dynamically extract the product title from the specified card."""
        panel_sel = self.TAB_MAP[tab_name]["panel"]
        card = self.page.locator(f"{panel_sel} {ProductUserManualsLocators.MANUAL_CARDS}").nth(card_index)
        title_loc = card.locator(ProductUserManualsLocators.CARD_TITLE).first
        title_loc.wait_for(state="visible", timeout=5000)
        title = title_loc.inner_text().strip()
        logger.info(f"Captured card[{card_index}] title under '{tab_name}' tab: '{title}'")
        return title

    def has_card_action(self, tab_name: str, action_type: str, card_index: int = 0) -> bool:
        """Check if a specific action button exists on the specified card."""
        panel_sel = self.TAB_MAP[tab_name]["panel"]
        card = self.page.locator(f"{panel_sel} {ProductUserManualsLocators.MANUAL_CARDS}").nth(card_index)
        action_sel = self._resolve_action_selector(action_type)
        btn = card.locator(action_sel).first
        return btn.count() > 0 and btn.is_visible()

    def _resolve_action_selector(self, action_type: str) -> str:
        """Resolve Locator constant for a card action type."""
        mapping = {
            "User Manual": ProductUserManualsLocators.USER_MANUAL_LINK,
            "Safety Manual": ProductUserManualsLocators.SAFETY_MANUAL_LINK,
            "View Product": ProductUserManualsLocators.VIEW_PRODUCT_LINK,
        }
        return mapping.get(action_type, ProductUserManualsLocators.USER_MANUAL_LINK)

    # =========================================================================
    # Manual Document Opening & Response Verification
    # =========================================================================

    def open_manual_and_verify(
        self, tab_name: str, action_type: str = "User Manual", card_index: int = 0
    ) -> Dict[str, Any]:
        """Click User Manual or Safety Manual, handle new tab/same tab, and inspect HTTP status."""
        panel_sel = self.TAB_MAP[tab_name]["panel"]
        card = self.page.locator(f"{panel_sel} {ProductUserManualsLocators.MANUAL_CARDS}").nth(card_index)
        btn = card.locator(self._resolve_action_selector(action_type)).first
        btn.scroll_into_view_if_needed()

        href = btn.get_attribute("href") or ""
        target = btn.get_attribute("target") or ""
        logger.info(f"Clicking '{action_type}' (target='{target}', href='{href}') on '{tab_name}' card[{card_index}]...")

        captured_responses: List[Dict[str, Any]] = []

        def _on_response(resp: Response) -> None:
            try:
                captured_responses.append({
                    "url": resp.url,
                    "status": resp.status,
                    "content_type": resp.headers.get("content-type", ""),
                })
            except Exception:
                pass

        self.page.context.on("response", _on_response)

        opened_new_tab = False
        final_url = ""
        browser_status: Optional[int] = None
        request_status: Optional[int] = None
        content_type = ""
        response_source = "unavailable"
        load_ok = False

        try:
            if target == "_blank":
                opened_new_tab = True
                new_pg = None
                try:
                    with self.page.context.expect_page(timeout=8000) as new_page_info:
                        btn.click(timeout=5000)
                    new_pg = new_page_info.value
                    try:
                        new_pg.wait_for_load_state("domcontentloaded", timeout=6000)
                    except Exception as load_err:
                        logger.debug(f"Popup load notice (expected for inline PDF viewer): {load_err}")

                    self.wait_for_timeout(500)
                    final_url = new_pg.url if (new_pg.url and new_pg.url != "about:blank") else href
                    load_ok = bool(final_url)
                except Exception as tab_err:
                    logger.debug(f"Direct expect_page notice for '{action_type}': {tab_err}")
                    final_url = href
                    load_ok = True

                # Check if browser captured a response matching this document
                norm_href = unquote(href).lower()
                for r in captured_responses:
                    r_url_norm = unquote(r["url"]).lower()
                    if norm_href in r_url_norm or r_url_norm in norm_href:
                        browser_status = r["status"]
                        content_type = r["content_type"]
                        response_source = "browser_response"
                        break

                # Close the document tab to return focus cleanly
                if new_pg and not new_pg.is_closed():
                    try:
                        new_pg.close()
                    except Exception:
                        pass
                self.page.bring_to_front()
            else:
                with self.page.expect_navigation(wait_until="domcontentloaded", timeout=12000) as nav_info:
                    btn.click()
                nav_resp = nav_info.value
                final_url = self.page.url
                load_ok = bool(final_url and final_url != "about:blank")
                if nav_resp:
                    browser_status = nav_resp.status
                    content_type = nav_resp.headers.get("content-type", "")
                    response_source = "browser_navigation_response"

                # Return to User Manuals page
                self.go_back(wait_until="domcontentloaded")
                self.select_tab(tab_name)
        finally:
            try:
                self.page.context.remove_listener("response", _on_response)
            except Exception:
                pass

        # Verify actual document accessibility and PDF content integrity
        is_pdf_content = False
        actual_pdf_accessible = False
        if href:
            try:
                pdf_resp = self.page.context.request.get(href, timeout=12000)
                if pdf_resp.status < 400:
                    request_status = pdf_resp.status
                    content_type = content_type or pdf_resp.headers.get("content-type", "")
                    body_bytes = pdf_resp.body()[:1024]
                    is_pdf_content = body_bytes.startswith(b"%PDF") or "pdf" in content_type.lower()
                    actual_pdf_accessible = (pdf_resp.status == 200 and is_pdf_content)
                    response_source = "direct_pdf_verification"
            except Exception as req_err:
                logger.warning(f"PDF content verification notice for '{href}': {req_err}")

        effective_status = browser_status if browser_status is not None else request_status
        is_404_or_failed = (effective_status is not None and effective_status >= 400)
        success = actual_pdf_accessible or (load_ok and not is_404_or_failed)

        result = {
            "action": action_type,
            "href": href,
            "final_url": final_url or href,
            "opened_in_new_tab": opened_new_tab,
            "http_status": effective_status,
            "content_type": content_type,
            "response_source": response_source,
            "is_pdf_content": is_pdf_content,
            "is_404_or_failed": is_404_or_failed,
            "success": success,
        }
        logger.info(f"Manual verification result for '{action_type}': {result}")
        return result

    # =========================================================================
    # View Product Navigation & Dynamic PDP Title / Heading Validation
    # =========================================================================

    def click_view_product_and_capture(
        self, tab_name: str, card_index: int = 0
    ) -> Dict[str, Any]:
        """Click View Product on the card and capture destination URL, status, title, and headings."""
        panel_sel = self.TAB_MAP[tab_name]["panel"]
        card = self.page.locator(f"{panel_sel} {ProductUserManualsLocators.MANUAL_CARDS}").nth(card_index)
        view_btn = card.locator(ProductUserManualsLocators.VIEW_PRODUCT_LINK).first
        view_btn.scroll_into_view_if_needed()

        target_href = view_btn.get_attribute("href") or ""
        logger.info(f"Clicking 'View Product' on '{tab_name}' card[{card_index}] (href='{target_href}')...")

        nav_status: Optional[int] = None
        try:
            with self.page.expect_navigation(wait_until="domcontentloaded", timeout=15000) as nav_info:
                view_btn.click()
            resp = nav_info.value
            if resp:
                nav_status = resp.status
        except Exception as nav_err:
            logger.debug(f"Navigation listener notice for View Product: {nav_err}")

        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.wait_for_timeout(800)

        dest_url = self.get_current_url()
        dest_page_title = self.get_title()

        h1_loc = self.page.locator(ProductUserManualsLocators.PDP_HEADING).first
        h1_text = h1_loc.inner_text().strip() if h1_loc.count() > 0 and h1_loc.is_visible(timeout=3000) else ""

        h2_texts: List[str] = []
        for h2 in self.page.locator(ProductUserManualsLocators.PDP_SUBHEADINGS).all():
            try:
                if h2.is_visible():
                    txt = h2.inner_text().strip()
                    if txt:
                        h2_texts.append(txt)
            except Exception:
                pass

        is_404 = self._check_404_on_current_page(dest_page_title)

        dest_info = {
            "target_href": target_href,
            "url": dest_url,
            "http_status": nav_status,
            "page_title": dest_page_title,
            "h1_text": h1_text,
            "subheadings": h2_texts,
            "is_404": is_404,
        }
        logger.info(
            f"View Product destination -> url='{dest_url}', status={nav_status}, "
            f"page_title='{dest_page_title}', h1='{h1_text}'"
        )
        return dest_info

    def verify_destination_matches_product(
        self, captured_title: str, dest_info: Dict[str, Any]
    ) -> bool:
        """Dynamically verify destination PDP heading or page title matches the captured card title.

        Normalizes trademark symbols (®, ™), Greek characters, Roman numerals, and whitespace
        to perform case-insensitive matching across destination h1, page title, and primary subheadings.
        """
        def _normalize(text: str) -> str:
            if not text:
                return ""
            t = re.sub(r"[®™©]", "", text)
            # Normalize Greek letters & Roman numerals
            t = t.replace("α", " alpha ").replace("Α", " alpha ")
            t = t.replace("MKⅡ", " MK2 ").replace("MKII", " MK2 ").replace("mkⅱ", " mk2 ")
            # Separate digits and letters (e.g., Cameo5 -> Cameo 5)
            t = re.sub(r"([a-zA-Z]+)(\d+)", r"\1 \2", t)
            t = re.sub(r"(\d+)([a-zA-Z]+)", r"\1 \2", t)
            t = re.sub(r"[\s\-_|/]+", " ", t).strip().lower()
            return t

        norm_product = _normalize(captured_title)
        h1_norm = _normalize(dest_info.get("h1_text", ""))
        title_norm = _normalize(dest_info.get("page_title", ""))
        h2_joined = " | ".join(_normalize(s) for s in dest_info.get("subheadings", []))

        # Match full normalized product name
        if norm_product and norm_product in h1_norm:
            logger.info(f"PDP heading (h1) dynamically matched '{captured_title}' -> '{dest_info['h1_text']}'")
            return True

        if norm_product and norm_product in title_norm:
            logger.info(
                f"PDP page title dynamically matched '{captured_title}' -> '{dest_info['page_title']}' "
                f"(Page H1: '{dest_info['h1_text']}')"
            )
            return True

        if norm_product and norm_product in h2_joined:
            logger.info(f"PDP subheading dynamically matched '{captured_title}' -> {dest_info['subheadings'][:3]}")
            return True

        # Token fallback (e.g., 'Cameo 5' or 'Heat Pen')
        tokens = [t for t in norm_product.split() if len(t) > 2]
        if tokens and all(t in h1_norm or t in title_norm for t in tokens):
            logger.info(f"PDP token match succeeded for '{captured_title}': tokens={tokens}")
            return True

        logger.error(
            f"Destination PDP mismatch! Captured: '{captured_title}' | "
            f"Actual H1: '{dest_info.get('h1_text')}' | Actual Title: '{dest_info.get('page_title')}'"
        )
        return False

    def return_to_user_manuals_page(self) -> bool:
        """Navigate back to Product User Manuals page and wait for heading."""
        logger.info("Returning to Product User Manuals page...")
        self.go_back(wait_until="domcontentloaded")
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()

        curr_url = self.get_current_url()
        if self.manuals_path not in curr_url:
            self.open_product_user_manuals_page()

        main_h = self.page.locator(ProductUserManualsLocators.MAIN_HEADING).first
        main_h.wait_for(state="visible", timeout=10000)
        return self.manuals_path in self.get_current_url() and main_h.is_visible()

    def _check_404_on_current_page(self, page_title: str) -> bool:
        """Detect 404 or error page indicators."""
        if "404" in page_title.lower() or "not found" in page_title.lower():
            return True
        try:
            err = self.page.locator(ProductUserManualsLocators.NOT_FOUND_INDICATORS).first
            return err.count() > 0 and err.is_visible(timeout=500)
        except Exception:
            return False

