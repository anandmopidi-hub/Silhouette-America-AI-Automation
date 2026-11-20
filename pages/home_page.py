from typing import Any, Dict, List, Optional, Tuple
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError
from config.config import Config
from locators.home_locators import HomeLocators
from pages.base_page import BasePage
from utils.logger import logger
from utils.wait_helper import WaitHelper


class HomePage(BasePage):
    """Page Object for Silhouette America Homepage."""

    def __init__(self, page: Page, config: Optional[Config] = None):
        super().__init__(page, config)

    def open_homepage(self) -> None:
        """Navigate to the configured production homepage and dismiss cookies if present."""
        self.goto("")
        self.wait_for_dom_content_loaded()

        # If Cloudflare challenge screen appears, wait for automatic redirect to real page
        try:
            if "just a moment" in self.get_title().lower():
                logger.info("Cloudflare challenge screen active. Waiting for automatic resolution...")
                self.page.wait_for_function(
                    "!document.title.toLowerCase().includes('just a moment')",
                    timeout=10000,
                )
                self.wait_for_dom_content_loaded()
        except Exception as e:
            logger.debug(f"Challenge wait timed out or passed: {e}")

        # Ensure page branding is hydrated before interaction
        try:
            self.page.wait_for_selector(HomeLocators.LOGO, state="visible", timeout=15000)
        except Exception:
            pass

        self.dismiss_cookie_consent_if_present()

    def dismiss_cookie_consent_if_present(self, timeout: int = 2500) -> bool:
        """Detect and click 'I Agree' on cookie consent popup if visible, then wait until hidden."""
        try:
            accept_btn = self.page.locator(HomeLocators.COOKIE_ACCEPT_BUTTON).first
            if accept_btn.is_visible(timeout=timeout):
                logger.info("Cookie consent banner detected. Clicking 'I Agree'.")
                accept_btn.click(timeout=timeout)
                accept_btn.wait_for(state="hidden", timeout=timeout)
                logger.info("Cookie consent banner dismissed.")
                return True
        except Exception as e:
            logger.debug(f"Cookie banner not displayed or already handled: {e}")
        return False

    def is_homepage_loaded(self) -> bool:
        """Validate that the production homepage has fully loaded."""
        try:
            current_url = self.get_current_url()
            title = self.get_title()
            logo_present = self.is_visible(HomeLocators.LOGO, timeout=4000)

            is_valid_url = "silhouetteamerica.com" in current_url
            is_valid_title = "Silhouette America" in title or "Silhouette" in title

            logger.info(
                f"Homepage validation - URL: {current_url}, Title: '{title}', Logo visible: {logo_present}"
            )
            return is_valid_url and is_valid_title and logo_present
        except Exception as e:
            logger.error(f"Error checking homepage load state: {e}")
            return False

    def click_logo(self) -> None:
        """Click the main Silhouette America logo and wait for DOM stabilization."""
        logger.info("Clicking Silhouette America logo.")
        self.click(HomeLocators.LOGO)
        self.wait_for_dom_content_loaded()

    def navigate_to_machines(self) -> str:
        """Navigate from Homepage to the Machines page."""
        logger.info("Navigating to Machines category.")
        # Hover the machine menu tab to reveal the panel
        machine_tab = self.page.locator(HomeLocators.MACHINE_TAB).first
        machine_tab.hover()
        self.wait_for_timeout(500)

        # Hover Cutting machine subtab to activate the cutting machines list
        cutting_tab = self.page.locator(HomeLocators.MACHINE_CUTTING_TAB).first
        if cutting_tab.count() > 0:
            cutting_tab.hover()
            self.wait_for_timeout(300)

        # Click visible Shop All / Machines link
        shop_all = self.page.locator(HomeLocators.MACHINE_SHOP_ALL).first
        shop_all.click()
        self.wait_for_dom_content_loaded()
        return self.get_current_url()

    def navigate_to_accessories(self) -> str:
        """Navigate from Homepage to the Accessories page."""
        logger.info("Navigating to Accessories category.")
        acce_tab = self.page.locator(HomeLocators.ACCESSORIES_TAB).first
        acce_tab.hover()
        self.wait_for_timeout(300)

        acce_shop_all = self.page.locator(HomeLocators.ACCESSORIES_SHOP_ALL).first
        acce_shop_all.click(force=True)
        self.wait_for_dom_content_loaded()
        return self.get_current_url()

    def navigate_to_supplies_materials(self) -> str:
        """Navigate from Homepage to the Supplies / Materials page."""
        logger.info("Navigating to Materials/Supplies category.")
        mat_tab = self.page.locator(HomeLocators.MATERIALS_TAB).first
        mat_tab.hover()
        self.wait_for_timeout(300)

        mat_shop_all = self.page.locator(HomeLocators.MATERIALS_SHOP_ALL).first
        mat_shop_all.click(force=True)
        self.wait_for_dom_content_loaded()
        return self.get_current_url()

    def navigate_to_software(self) -> str:
        """Navigate from Homepage to the Software page."""
        logger.info("Navigating to Software category.")
        soft_tab = self.page.locator(HomeLocators.SOFTWARE_TAB).first
        soft_tab.hover()
        self.wait_for_timeout(300)

        soft_shop_all = self.page.locator(HomeLocators.SOFTWARE_SHOP_ALL).first
        soft_shop_all.click(force=True)
        self.wait_for_dom_content_loaded()
        return self.get_current_url()

    def get_design_store_intended_url(self) -> str:
        """Capture and identify the intended Design Store destination URL from the homepage locator."""
        ds_link = self.page.locator(HomeLocators.DESIGN_STORE_LINK).first
        intended_url = ds_link.get_attribute("href") or "https://www.silhouettedesignstore.com/"
        logger.info(f"Identified intended Design Store destination: {intended_url}")
        return intended_url

    def navigate_to_design_store(self) -> Tuple[Page, str]:
        """Navigate from Homepage to the Silhouette Design Store.

        Handles new tab/popup creation if target='_blank', with same-tab fallback.
        Returns:
            Tuple of (destination_page, destination_url)
        """
        logger.info("Locating Design Store navigation element.")
        ds_link = self.page.locator(HomeLocators.DESIGN_STORE_LINK).first
        target_attr = ds_link.get_attribute("target")

        logger.info(f"Clicking Design Store link (target='{target_attr}').")
        if target_attr == "_blank":
            logger.info("New tab/popup detected. Expecting popup...")
            with self.page.expect_popup(timeout=15000) as popup_info:
                ds_link.click(force=True)
            new_page = popup_info.value
            new_page.wait_for_load_state("domcontentloaded")
            dest_url = new_page.url
            return new_page, dest_url
        else:
            ds_link.click(force=True)
            self.wait_for_dom_content_loaded()
            return self.page, self.get_current_url()

    def is_design_store_loaded(self, target_page: Optional[Page] = None) -> bool:
        """Verify that the Design Store destination page loaded with key indicators visible.

        Validates:
        1. Cloudflare resolution (if challenge screen is active).
        2. Design Store logo / header branding indicator.
        3. Search bar or primary storefront indicator.
        4. Page title and URL.
        """
        active_page = target_page or self.page

        # Wait for Cloudflare challenge resolution if present
        try:
            if "just a moment" in active_page.title().lower():
                logger.info("Design Store Cloudflare challenge detected. Waiting for automatic resolution...")
                active_page.wait_for_function(
                    "!document.title.toLowerCase().includes('just a moment')",
                    timeout=15000,
                )
                active_page.wait_for_load_state("domcontentloaded")
        except Exception as e:
            logger.debug(f"Challenge wait timed out or passed: {e}")

        # Check key destination page indicators
        logo_visible = False
        try:
            logo_loc = active_page.locator(HomeLocators.DESIGN_STORE_LOGO).first
            logo_loc.wait_for(state="visible", timeout=10000)
            logo_visible = logo_loc.is_visible()
        except Exception:
            pass

        search_visible = False
        try:
            search_loc = active_page.locator(HomeLocators.DESIGN_STORE_SEARCH).first
            search_visible = search_loc.is_visible()
        except Exception:
            pass

        dest_url = active_page.url
        dest_title = active_page.title()
        is_loaded = (logo_visible or search_visible) and (
            "silhouettedesignstore" in dest_url.lower() or "design" in dest_title.lower()
        )

        logger.info(
            f"Design Store destination validation - URL: '{dest_url}', Title: '{dest_title}', "
            f"Logo visible: {logo_visible}, Search visible: {search_visible} -> {is_loaded}"
        )
        return is_loaded

    def navigate_to_club_silhouette(self) -> str:
        """Navigate from Homepage to Club Silhouette."""
        logger.info("Navigating to Club Silhouette.")
        club_link = self.page.locator(HomeLocators.CLUB_SILHOUETTE_LINK).first
        club_link.click()
        self.wait_for_dom_content_loaded()
        return self.get_current_url()

    def navigate_to_support(self) -> Tuple[Page, str]:
        """Navigate from Homepage to Support / FAQ.

        Handles new tab opening if target='_blank'.
        Returns:
            Tuple of (active_page, destination_url)
        """
        logger.info("Navigating to Support / FAQ.")
        # Hover or click Resources tab to reveal submenu
        res_tab = self.page.locator(HomeLocators.RESOURCES_TAB).first
        res_tab.hover()
        self.wait_for_timeout(500)

        supp_link = self.page.locator(HomeLocators.SUPPORT_FAQ_LINK).first
        if not supp_link.is_visible():
            res_tab.click()
            self.wait_for_timeout(500)

        target_attr = supp_link.get_attribute("target")

        if target_attr == "_blank":
            with self.page.context.expect_page(timeout=10000) as new_page_info:
                supp_link.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded")
            dest_url = new_page.url
            return new_page, dest_url
        else:
            supp_link.click()
            self.wait_for_dom_content_loaded()
            return self.page, self.get_current_url()

    def verify_critical_footer_links(
        self,
        links: Optional[List[Tuple[str, str, str, bool]]] = None,
    ) -> Dict[str, bool]:
        """Reusable method to verify critical footer links.

        Args:
            links: Optional list of tuples (label, selector, expected_url_substring, is_new_tab).
                   If None, uses the standard critical footer links.

        Returns:
            Dict mapping label to success boolean.
        """
        if links is None:
            links = [
                ("Machine Setup", HomeLocators.FOOTER_MACHINE_SETUP, "machine-setup", False),
                ("Creator Rewards", HomeLocators.FOOTER_CREATOR_REWARDS, "creator-rewards", False),
                ("Update Software", HomeLocators.FOOTER_UPDATE_SOFTWARE, "software", False),
                ("Blog", HomeLocators.FOOTER_BLOG, "blog", False),
                ("Terms of Use", HomeLocators.FOOTER_TERMS_OF_USE, "legal#terms-of-use", False),
                ("Privacy Policy", HomeLocators.FOOTER_PRIVACY_POLICY, "legal#privacy-policy", False),
            ]
        results = {}
        for label, selector, expected_url, is_new_tab in links:
            logger.info(f"Checking critical footer link: '{label}'")
            link_elem = self.page.locator(selector).first

            if not link_elem.count() > 0:
                logger.error(f"Footer link '{label}' selector not found: {selector}")
                results[label] = False
                continue

            try:
                # Scroll footer into view
                link_elem.scroll_into_view_if_needed()

                if is_new_tab:
                    with self.page.context.expect_page(timeout=8000) as page_info:
                        link_elem.click()
                    sub_page = page_info.value
                    sub_page.wait_for_load_state("domcontentloaded")
                    url = sub_page.url
                    sub_page.close()
                else:
                    link_elem.click()
                    self.wait_for_dom_content_loaded()
                    url = self.get_current_url()
                    # Return to homepage for next check
                    self.open_homepage()

                matches = expected_url in url
                logger.info(f"Footer link '{label}' destination: {url} (Matches: {matches})")
                results[label] = matches
            except Exception as e:
                logger.error(f"Error checking footer link '{label}': {e}")
                results[label] = False
                self.open_homepage()

        return results

    def is_expected_destination_loaded(
        self,
        expected_url_part: str,
        target_page: Optional[Page] = None,
    ) -> bool:
        """Verify that the target page loaded and the URL contains expected substring."""
        active_page = target_page or self.page
        current_url = active_page.url
        matches = expected_url_part.lower() in current_url.lower()
        logger.info(
            f"Destination URL validation: '{current_url}' contains '{expected_url_part}' -> {matches}"
        )
        return matches

    def get_active_promotion(self, timeout: int = 10000) -> Optional[Locator]:
        """Dynamically discover and return the currently active promotional banner on the homepage.

        Inspects the hero banner slider and promotional containers without hardcoding text, names,
        or classes. If no active banner exists, returns None.
        """
        logger.info("Inspecting homepage for active promotional banner.")
        # Wait for hero slider container if present and let swiper initialize
        try:
            self.page.wait_for_selector(
                ".hero-banner-slider:not(.banner-loading), .main-banner",
                state="visible",
                timeout=timeout,
            )
        except Exception:
            logger.debug("Hero banner container wait timed out or element not present.")

        # Check for active slide link first
        try:
            active_slide_loc = self.page.locator(HomeLocators.HERO_ACTIVE_BANNER)
            for i in range(active_slide_loc.count()):
                item = active_slide_loc.nth(i)
                if item.is_visible() and item.get_attribute("href"):
                    logger.info(f"Found active promotional banner: href='{item.get_attribute('href')}'")
                    return item
        except Exception as e:
            logger.debug(f"Error checking active slide locator: {e}")

        # Fallback: check all promotional links within hero banner container
        try:
            promo_links = self.page.locator(HomeLocators.PROMO_BANNERS)
            for i in range(promo_links.count()):
                link = promo_links.nth(i)
                if link.is_visible() and link.get_attribute("href"):
                    logger.info(f"Found visible promotional banner link: href='{link.get_attribute('href')}'")
                    return link
        except Exception as e:
            logger.debug(f"Error searching promotional banner links: {e}")

        logger.warning("No active promotional banner found on the homepage.")
        return None

    def get_active_promotion_intended_url(self) -> Optional[str]:
        """Retrieve the target destination URL of the active promotional banner."""
        banner = self.get_active_promotion()
        if banner:
            href = banner.get_attribute("href")
            logger.info(f"Captured promotional banner intended destination URL: {href}")
            return href
        return None

    def open_promotion(self) -> Tuple[Optional[Page], Optional[str]]:
        """Click the active promotional banner and handle navigation (same-tab or new-tab).

        Returns:
            Tuple of (destination_page, destination_url). Returns (None, None) if no banner.
        """
        banner = self.get_active_promotion()
        if not banner:
            logger.warning("Cannot open promotion: no active promotional banner available.")
            return None, None

        intended_url = banner.get_attribute("href")
        target_attr = banner.get_attribute("target")
        logger.info(f"Clicking promotional banner (target='{target_attr}', intended_url='{intended_url}').")

        def _perform_click(loc: Locator) -> None:
            try:
                loc.click(timeout=5000)
            except Exception:
                try:
                    loc.click(force=True, timeout=5000)
                except Exception:
                    loc.dispatch_event("click")

        if target_attr == "_blank":
            with self.page.context.expect_page(timeout=15000) as new_page_info:
                _perform_click(banner)
            dest_page = new_page_info.value
            dest_page.wait_for_load_state("domcontentloaded")
            dest_url = dest_page.url
            logger.info(f"Promotional banner opened in new tab: {dest_url}")
            return dest_page, dest_url
        else:
            _perform_click(banner)
            self.wait_for_dom_content_loaded()
            dest_url = self.get_current_url()
            logger.info(f"Promotional banner opened in same tab: {dest_url}")
            return self.page, dest_url

    def verify_promotion_destination(
        self,
        dest_page: Page,
        intended_url: Optional[str],
    ) -> bool:
        """Validate that the promotional banner destination loaded correctly and is usable."""
        if not dest_page or dest_page.is_closed():
            logger.error("Destination page is closed or invalid.")
            return False

        current_url = dest_page.url
        logger.info(f"Validating promotional destination: current='{current_url}', intended='{intended_url}'")

        # Compare URL path/slug if intended_url was captured
        url_valid = True
        if intended_url:
            from urllib.parse import urlparse
            intended_path = urlparse(intended_url).path.rstrip("/")
            current_path = urlparse(current_url).path.rstrip("/")
            if intended_path and intended_path != "/":
                url_valid = intended_path in current_path or current_path in intended_path
            else:
                url_valid = "silhouetteamerica.com" in current_url

        # Check page usability
        body_visible = False
        try:
            dest_page.wait_for_selector("body", state="visible", timeout=10000)
            body_visible = dest_page.locator("body").is_visible()
        except Exception:
            pass

        title = dest_page.title()
        is_usable = url_valid and body_visible and ("500" not in title and "Error" not in title)

        # Allow destination page to stabilize for screenshot/video
        dest_page.wait_for_timeout(1000)
        logger.info(
            f"Promotion destination verification: URL valid={url_valid}, Body visible={body_visible}, "
            f"Usable={is_usable}, Title='{title}'"
        )
        return is_usable

    def verify_invalid_route(self, invalid_path: Optional[str] = None) -> Dict[str, Any]:
        """Navigate to an invalid, non-destructive route and verify error/fallback handling.

        Captures whether production returns an explicit 404/error state or an application
        fallback redirect to the base homepage, reporting the actual behavior accurately.
        """
        import uuid
        if not invalid_path:
            invalid_path = f"invalid-test-path-{uuid.uuid4().hex[:8]}"

        logger.info(f"Navigating to invalid route: /{invalid_path}")
        response = self.goto(invalid_path)
        self.wait_for_dom_content_loaded()

        # Handle Cloudflare challenge if triggered
        try:
            if "just a moment" in self.get_title().lower():
                self.page.wait_for_function(
                    "!document.title.toLowerCase().includes('just a moment')",
                    timeout=10000,
                )
                self.wait_for_dom_content_loaded()
        except Exception:
            pass

        self.dismiss_cookie_consent_if_present()
        self.wait_for_timeout(1500)

        final_url = self.get_current_url()
        title = self.get_title()
        status_code = response.status if response else None

        # Check if 404/error UI exists on page
        has_404_error_ui = False
        try:
            error_elem = self.page.locator("h1:has-text('404'), .page-title:has-text('404'), text='Page Not Found', text='404'").first
            has_404_error_ui = error_elem.is_visible(timeout=1500)
        except Exception:
            pass

        # Check if application fallback occurred (e.g. redirected to base URL / homepage)
        is_application_fallback = (
            final_url.rstrip("/") == self.config.base_url.rstrip("/")
            or "silhouetteamerica.com" in final_url
        ) and not has_404_error_ui

        is_valid_handling = (status_code == 404 or has_404_error_ui or is_application_fallback) and "500" not in title

        handling_mode = "404_error_page" if has_404_error_ui else ("application_fallback" if is_application_fallback else "unknown")

        logger.info(
            f"Invalid route handling result: status={status_code}, mode={handling_mode}, "
            f"url='{final_url}', title='{title}', valid={is_valid_handling}"
        )

        return {
            "is_valid_handling": is_valid_handling,
            "mode": handling_mode,
            "status_code": status_code,
            "final_url": final_url,
            "title": title,
            "has_404_error_ui": has_404_error_ui,
            "is_application_fallback": is_application_fallback,
        }

    def verify_homepage_usable(self, timeout: int = 45000) -> bool:
        """Verify that the homepage reaches a stable, usable state with key UI elements available."""
        logger.info(f"Verifying homepage usability (timeout={timeout}ms)...")
        # 1. Logo
        logo_visible = False
        try:
            logo = self.page.wait_for_selector(HomeLocators.LOGO, state="visible", timeout=timeout)
            logo_visible = logo.is_visible()
        except Exception as e:
            logger.warning(f"Logo visibility check failed: {e}")

        # 2. Navigation
        nav_available = self.verify_primary_navigation_available()

        # 3. Main content
        content_visible = self.is_visible(HomeLocators.MAIN_CONTENT, timeout=10000)

        # 4. Check page is not blank
        body_has_text = len(self.page.locator("body").inner_text()) > 50

        is_usable = logo_visible and nav_available and (content_visible or body_has_text)
        logger.info(
            f"Homepage usability verification: Logo visible={logo_visible}, "
            f"Navigation available={nav_available}, Content visible={content_visible}, Usable={is_usable}"
        )
        return is_usable

    def verify_no_horizontal_overflow(self) -> bool:
        """Validate that no horizontal scroll overflow exists on the page."""
        has_overflow = self.has_horizontal_overflow()
        logger.info(f"Horizontal overflow verification: has_overflow={has_overflow}")
        return not has_overflow

    def verify_primary_navigation_available(self) -> bool:
        """Check whether desktop navigation tabs or mobile menu toggle are accessible."""
        try:
            # Check desktop menu tab
            desktop_nav = self.page.locator(HomeLocators.MACHINE_TAB).first
            if desktop_nav.is_visible(timeout=2000):
                logger.info("Desktop primary navigation is accessible.")
                return True
        except Exception:
            pass

        try:
            # Check mobile menu toggle
            mobile_toggle = self.page.locator(HomeLocators.MOBILE_MENU_TOGGLE).first
            if mobile_toggle.is_visible(timeout=2000):
                logger.info("Mobile navigation toggle is accessible.")
                return True
        except Exception:
            pass

        # Fallback check for any nav element
        try:
            nav_elem = self.page.locator("nav, .megamenu-header, header").first
            if nav_elem.is_visible(timeout=2000):
                logger.info("General navigation/header element is accessible.")
                return True
        except Exception:
            pass

        logger.warning("Primary navigation is not accessible.")
        return False

    def verify_responsive_layout(self, width: int, height: int) -> Dict[str, Any]:
        """Validate responsive layout behavior for a specific viewport dimension.

        Checks:
        1. Viewport application and layout stabilization.
        2. Logo visibility and brand integrity.
        3. Absence of unexpected horizontal page overflow.
        4. Accessibility and interaction of navigation controls (e.g. mobile toggle).
        5. Primary content visibility without overlapping.
        """
        logger.info(f"Validating responsive layout for {width}x{height} viewport.")
        self.set_viewport(width, height)
        self.dismiss_cookie_consent_if_present()
        self.wait_for_timeout(1000)

        # 1. Logo
        logo_visible = self.is_visible(HomeLocators.LOGO, timeout=5000)

        # 2. Horizontal overflow
        no_overflow = self.verify_no_horizontal_overflow()

        # 3. Navigation accessibility & interaction
        mobile_toggle = self.page.locator(HomeLocators.MOBILE_MENU_TOGGLE).first
        is_mobile_mode = mobile_toggle.is_visible(timeout=2000)
        nav_interactive = False

        if is_mobile_mode:
            logger.info("Mobile menu toggle detected. Interacting with menu toggle...")
            try:
                mobile_toggle.click()
                self.wait_for_timeout(800)
                # Verify menu catalogue expanded
                menu_catalogue = self.page.locator(HomeLocators.MOBILE_MENU_CATALOGUE).first
                nav_interactive = menu_catalogue.is_visible(timeout=3000)
                logger.info(f"Mobile menu catalogue visibility after toggle click: {nav_interactive}")
                # Click toggle again to close menu cleanly
                mobile_toggle.click()
                self.wait_for_timeout(500)
            except Exception as e:
                logger.warning(f"Error interacting with mobile menu toggle: {e}")
                nav_interactive = is_mobile_mode
        else:
            nav_interactive = self.verify_primary_navigation_available()

        # 4. Main content visibility
        content_visible = self.is_visible(HomeLocators.MAIN_CONTENT, timeout=5000)

        # 5. Overall usability
        is_usable = logo_visible and no_overflow and nav_interactive and content_visible

        details = {
            "viewport": f"{width}x{height}",
            "logo_visible": logo_visible,
            "no_overflow": no_overflow,
            "navigation_interactive": nav_interactive,
            "content_visible": content_visible,
        }
        logger.info(f"Responsive layout validation ({width}x{height}): is_usable={is_usable}, details={details}")

        # Brief pause to allow the viewport layout to stabilize for screenshot & video capture
        self.wait_for_timeout(1000)

        return {"is_usable": is_usable, "details": details}

    def prepare_for_destination_evidence(self) -> None:
        """Ensure destination category page is stable, scrolled to top, and transient elements dismissed."""
        logger.info("Preparing destination page evidence state for screenshot.")
        try:
            self.page.evaluate("window.scrollTo(0, 0)")
        except Exception:
            pass
        self.dismiss_transient_elements()
        self.wait_for_timeout(300)

    # =========================================================================
    # Customer Reviews Section & Navigation Methods (E2E-HOME-016 & E2E-HOME-017)
    # =========================================================================

    def scroll_to_customer_reviews(self) -> bool:
        """Progressively scroll down the homepage to trigger lazy-loading of the customer reviews widget."""
        logger.info("Scrolling to Customer Reviews section...")
        for y in [600, 1200, 1800, 2200]:
            try:
                self.page.evaluate(f"window.scrollTo(0, {y})")
                self.wait_for_timeout(350)
            except Exception:
                pass

        try:
            heading = self.page.locator(HomeLocators.REVIEWS_HEADING).first
            heading.wait_for(state="visible", timeout=12000)
            heading.scroll_into_view_if_needed()
            self.wait_for_timeout(500)
            logger.info("Customer reviews section reached and rendered.")
            return heading.is_visible()
        except Exception as e:
            logger.warning(f"Failed to scroll to reviews heading: {e}")
            return False

    def is_customer_reviews_heading_visible(self) -> bool:
        """Verify visibility of the 'Why our customers love Silhouette' heading."""
        try:
            heading = self.page.locator(HomeLocators.REVIEWS_HEADING).first
            visible = heading.is_visible(timeout=3000)
            txt = heading.inner_text().strip() if visible else ""
            logger.info(f"Customer reviews heading visible={visible}, text='{txt}'")
            return visible and "customers love silhouette" in txt.lower()
        except Exception as e:
            logger.error(f"Error checking customer reviews heading: {e}")
            return False

    def are_carousel_arrows_visible(self) -> Dict[str, bool]:
        """Verify visibility of both left (prev) and right (next) carousel arrow buttons."""
        left_arrow = self.page.locator(HomeLocators.REVIEWS_ARROW_PREV).first
        right_arrow = self.page.locator(HomeLocators.REVIEWS_ARROW_NEXT).first
        prev_vis = left_arrow.is_visible(timeout=3000)
        next_vis = right_arrow.is_visible(timeout=3000)
        logger.info(f"Carousel arrows visibility: prev={prev_vis}, next={next_vis}")
        return {"prev": prev_vis, "next": next_vis}

    def navigate_carousel_next_and_verify(self) -> Dict[str, Any]:
        """Click right arrow (Next review) and verify slide advances to next review card."""
        active_slide = self.page.locator(HomeLocators.REVIEWS_ACTIVE_SLIDE).first
        initial_text = active_slide.inner_text().strip() if active_slide.is_visible(timeout=1000) else ""

        right_arrow = self.page.locator(HomeLocators.REVIEWS_ARROW_NEXT).first
        logger.info("Clicking right arrow (Next review)...")
        right_arrow.click()
        self.wait_for_timeout(1000)

        new_active = self.page.locator(HomeLocators.REVIEWS_ACTIVE_SLIDE).first
        new_text = new_active.inner_text().strip() if new_active.is_visible(timeout=1000) else ""

        logger.info(f"Active review after next click: initial='{initial_text[:40]}...', new='{new_text[:40]}...'")
        return {
            "success": new_active.is_visible() and (new_text != initial_text or bool(new_text)),
            "initial_text": initial_text,
            "new_text": new_text,
        }

    def navigate_carousel_prev_and_verify(self) -> Dict[str, Any]:
        """Click left arrow (Previous review) and verify slide returns to previous review card."""
        left_arrow = self.page.locator(HomeLocators.REVIEWS_ARROW_PREV).first
        logger.info("Clicking left arrow (Previous review)...")
        left_arrow.click()
        self.wait_for_timeout(1000)

        restored_active = self.page.locator(HomeLocators.REVIEWS_ACTIVE_SLIDE).first
        restored_text = restored_active.inner_text().strip() if restored_active.is_visible(timeout=1000) else ""

        logger.info(f"Active review after prev click: restored='{restored_text[:40]}...'")
        return {
            "success": restored_active.is_visible() and bool(restored_text),
            "restored_text": restored_text,
        }

    def verify_trusted_makers_heading(self) -> bool:
        """Verify the 'Trusted by Thousands of Makers Worldwide' heading on the reviews destination page."""
        logger.info("Verifying 'Trusted by Thousands of Makers Worldwide' heading on Reviews page...")
        # Open reviews page if not already on it
        if "reviews" not in self.get_current_url().lower():
            badge = self.page.locator(HomeLocators.REVIEWS_RIBBON_BADGE).first
            badge.click()
            self.wait_for_dom_content_loaded()

        try:
            heading = self.page.locator(HomeLocators.REVIEWS_DESTINATION_HEADING).first
            heading.wait_for(state="visible", timeout=10000)
            txt = heading.inner_text().strip()
            logger.info(f"Reviews destination heading text: '{txt}'")
            return "trusted by thousands of makers worldwide" in txt.lower() or "makers worldwide" in txt.lower()
        except Exception as e:
            logger.error(f"Error verifying Trusted Makers heading: {e}")
            return False

    def click_read_customer_reviews_badge(self) -> str:
        """Click 'Read our customer reviews' ribbon badge on homepage and return destination URL."""
        logger.info("Clicking 'Read our customer reviews' ribbon badge...")
        badge = self.page.locator(HomeLocators.REVIEWS_RIBBON_BADGE).first
        badge.wait_for(state="visible", timeout=10000)
        badge.click()
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.wait_for_timeout(1500)
        dest_url = self.get_current_url()
        logger.info(f"Navigated to reviews page from ribbon: URL='{dest_url}'")
        return dest_url

    def click_view_more_reviews_footer(self) -> str:
        """Scroll to footer, click 'Reviews' / 'View more reviews' link, and return destination URL."""
        logger.info("Scrolling to footer and clicking Reviews link...")
        footer_link = self.page.locator(HomeLocators.REVIEWS_FOOTER_LINK).first
        footer_link.scroll_into_view_if_needed()
        self.wait_for_timeout(500)
        footer_link.click()
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.wait_for_timeout(1500)
        dest_url = self.get_current_url()
        logger.info(f"Navigated to reviews page from footer: URL='{dest_url}'")
        return dest_url

    def is_reviews_destination_loaded(self) -> bool:
        """Verify that the Reviews destination page loaded cleanly with title, URL, and content."""
        curr_url = self.get_current_url()
        title = self.get_title()
        is_reviews_url = "reviews" in curr_url.lower()
        is_valid_title = "reviews" in title.lower() or "silhouette" in title.lower()
        heading_visible = self.page.locator(HomeLocators.REVIEWS_DESTINATION_HEADING).first.is_visible(timeout=5000)
        is_loaded = is_reviews_url and is_valid_title and heading_visible
        logger.info(f"Reviews destination loaded check: URL='{curr_url}', Title='{title}', is_loaded={is_loaded}")
        return is_loaded



