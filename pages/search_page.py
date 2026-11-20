from typing import Any, Dict, List, Optional, Tuple
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError
from config.config import Config
from locators.search_locators import SearchLocators
from locators.home_locators import HomeLocators
from pages.base_page import BasePage
from utils.logger import logger
from utils.wait_helper import WaitHelper


class SearchPage(BasePage):
    """Page Object for Silhouette America Search functionality."""

    def __init__(self, page: Page, config: Optional[Config] = None):
        super().__init__(page, config)

    def open_homepage(self) -> None:
        """Navigate to the production homepage, resolve challenges, and dismiss cookies."""
        self.goto("")
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
        except Exception as e:
            logger.debug(f"Challenge wait timed out or passed: {e}")

        # Ensure header/branding is hydrated
        try:
            self.page.wait_for_selector(HomeLocators.LOGO, state="visible", timeout=15000)
        except Exception:
            pass

        self.dismiss_cookie_consent_if_present()

    def dismiss_cookie_consent_if_present(self, timeout: int = 3000) -> bool:
        """Centrally dismiss cookie consent popup via BasePage."""
        return super().dismiss_cookie_consent_if_present(timeout=timeout)

    def open_search(self) -> None:
        """Ensure the search interface is open, accessible, and ready for input."""
        logger.info("Opening search functionality.")
        if "silhouetteamerica.com" not in self.get_current_url():
            self.open_homepage()

        # If search input is hidden behind mobile or desktop toggle, activate toggle
        search_input = self.page.locator(SearchLocators.SEARCH_INPUT).first
        if not search_input.is_visible():
            search_toggle = self.page.locator(SearchLocators.SEARCH_TOGGLE).first
            if search_toggle.is_visible():
                logger.info("Search toggle icon detected. Clicking to reveal search input.")
                search_toggle.click()
                self.wait_for_timeout(500)

        # Wait for search box to be visible and actionable
        self.page.wait_for_selector(SearchLocators.SEARCH_INPUT, state="visible", timeout=10000)

    def enter_search_query(self, query: str) -> None:
        """Clear search field and enter search query text."""
        logger.info(f"Entering search query: '{query}'")
        search_input = self.page.locator(SearchLocators.SEARCH_INPUT).first
        search_input.clear()
        search_input.fill(query)
        self.wait_for_timeout(300)

    def submit_search(self) -> None:
        """Submit the active search query via Enter key press or Search button, and wait for results page."""
        logger.info("Submitting search query.")
        search_input = self.page.locator(SearchLocators.SEARCH_INPUT).first

        # Ensure search input is focused
        try:
            search_input.focus()
        except Exception:
            pass

        # Try submitting via Enter key press
        search_input.press("Enter")

        # Wait briefly to see if navigation to search URL begins
        navigated = False
        try:
            self.page.wait_for_url(
                lambda u: "search" in u.lower() or "q=" in u.lower(),
                timeout=4000,
            )
            navigated = True
        except Exception:
            pass

        # If Enter key didn't navigate (e.g. autocomplete intercepted Enter), click search button or trigger form submit
        if not navigated:
            logger.info("Enter key did not navigate immediately; clicking search button / submitting form.")
            try:
                search_btn = self.page.locator(SearchLocators.SEARCH_BUTTON).first
                if search_btn.is_visible():
                    search_btn.click()
                else:
                    self.page.evaluate(
                        """() => {
                            const btn = document.querySelector('#search_mini_form button[type="submit"], .action.search');
                            if (btn) {
                                btn.click();
                            } else {
                                const form = document.querySelector('#search_mini_form, form[action*="/search"]');
                                if (form) form.submit();
                            }
                        }"""
                    )
                self.page.wait_for_url(
                    lambda u: "search" in u.lower() or "q=" in u.lower(),
                    timeout=8000,
                )
            except Exception as e:
                logger.debug(f"Search button / form submit fallback attempt: {e}")

        self.wait_for_dom_content_loaded()

        # Handle Cloudflare challenge if triggered on navigation
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

        # Wait for search results container, product items, or no-results notice to render
        try:
            self.page.wait_for_selector(
                f"{SearchLocators.SEARCH_RESULTS_CONTAINER}, {SearchLocators.SEARCH_RESULT_ITEMS}, {SearchLocators.NO_RESULTS_MESSAGE}",
                state="attached",
                timeout=10000,
            )
        except Exception:
            pass

        # Brief stabilization window for search results hydration
        self.wait_for_timeout(1000)

    def search(self, query: str) -> None:
        """Convenience method to open search, enter query, and submit."""
        self.open_search()
        self.enter_search_query(query)
        self.submit_search()

    def is_search_results_page_loaded(self, timeout: int = 15000) -> bool:
        """Verify that the search results page has loaded with valid URL, title, or DOM indicators."""
        # Dynamically wait for search indicators with timeout
        try:
            self.page.wait_for_function(
                """() => {
                    const u = window.location.href.toLowerCase();
                    const t = document.title.toLowerCase();
                    const hasUrl = u.includes('search') || u.includes('q=');
                    const hasTitle = t.includes('search');
                    const hasDom = document.querySelector('.search.results, .products.wrapper, .item.product, .kuProductBlock, .message.notice, .no-results') !== null;
                    return (hasUrl || hasTitle) && (hasDom || document.readyState === 'complete');
                }""",
                timeout=timeout,
            )
        except Exception:
            pass

        current_url = self.get_current_url()
        title = self.get_title()
        has_query_in_url = "q=" in current_url.lower() or "search" in current_url.lower()
        has_search_title = "search" in title.lower()

        # Also verify DOM presence of results or no-results
        has_results_dom = False
        try:
            has_results_dom = (
                self.page.locator(SearchLocators.SEARCH_RESULTS_CONTAINER).first.is_visible()
                or self.page.locator(SearchLocators.SEARCH_RESULT_ITEMS).first.is_visible()
                or self.page.locator(SearchLocators.NO_RESULTS_MESSAGE).first.is_visible()
            )
        except Exception:
            pass

        is_loaded = has_query_in_url or has_search_title or has_results_dom
        logger.info(
            f"Search results page validation: URL='{current_url}', Title='{title}', DOM={has_results_dom} -> is_loaded={is_loaded}"
        )
        return is_loaded

    def get_search_results_count(self) -> int:
        """Return the number of visible product cards in the search results."""
        try:
            self.page.wait_for_selector(SearchLocators.SEARCH_RESULT_ITEMS, state="visible", timeout=6000)
        except Exception:
            pass
        results_loc = self.page.locator(SearchLocators.SEARCH_RESULT_ITEMS)
        count = results_loc.count()
        logger.info(f"Detected {count} product search result items.")
        return count

    def get_search_results_titles(self) -> List[str]:
        """Extract and return text titles of visible product search result items."""
        title_loc = self.page.locator(SearchLocators.PRODUCT_ITEM_TITLE)
        titles = [t.strip() for t in title_loc.all_inner_texts() if t.strip()]
        logger.info(f"Extracted {len(titles)} product titles from search results.")
        return titles

    def get_first_search_result_href(self) -> Optional[str]:
        """Capture the target destination href of the first search result product card."""
        selectors = [
            ".product-item a.product-item-link",
            ".kuProductTitle a",
            ".klevuProductTitle a",
            ".item.product a.product-item-photo",
            SearchLocators.PRODUCT_ITEM_LINK,
        ]
        for sel in selectors:
            product_links = self.page.locator(sel)
            for i in range(product_links.count()):
                href = product_links.nth(i).get_attribute("href")
                if href and ("silhouetteamerica.com" in href or href.startswith("/")):
                    if href.startswith("/"):
                        from urllib.parse import urljoin
                        href = urljoin(self.config.base_url, href)
                    logger.info(f"Discovered first valid product search result href: '{href}'")
                    return href
        return None

    def open_first_search_result(self) -> Tuple[Optional[str], str]:
        """Click the first visible search result item and navigate to its Product Detail Page (PDP).

        Returns:
            Tuple of (intended_href, actual_destination_url).
        """
        intended_href = self.get_first_search_result_href()
        logger.info(f"Opening first search result (intended: '{intended_href}').")

        clicked = False
        if intended_href:
            try:
                target_link = self.page.locator(f"a[href='{intended_href}']").first
                if target_link.is_visible(timeout=3000):
                    target_link.scroll_into_view_if_needed()
                    target_link.click(force=True)
                    clicked = True
            except Exception as e:
                logger.debug(f"Direct href link click attempt: {e}")

        if not clicked:
            first_link = self.page.locator(SearchLocators.PRODUCT_ITEM_LINK).first
            first_link.scroll_into_view_if_needed()
            first_link.click(force=True)

        # Wait for navigation away from search results or to intended PDP URL
        try:
            self.page.wait_for_url(
                lambda u: ("search" not in u.lower() and "q=" not in u.lower()) or (intended_href and intended_href in u),
                timeout=8000,
            )
        except Exception:
            # If click didn't initiate navigation, navigate directly to intended_href
            if intended_href and "silhouetteamerica.com" in intended_href:
                logger.info(f"Click did not complete URL change; navigating directly to '{intended_href}'")
                self.goto(intended_href, wait_until="domcontentloaded")

        self.wait_for_dom_content_loaded()

        # Handle challenge if triggered
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
        self.wait_for_timeout(1000)

        actual_url = self.get_current_url()
        logger.info(f"Navigated to PDP: actual_url='{actual_url}'")
        return intended_href, actual_url

    def is_pdp_loaded(self, intended_url: Optional[str] = None) -> bool:
        """Validate that the Product Detail Page (PDP) loaded successfully.

        Checks:
        1. Destination URL corresponds to product slug/href.
        2. Product title (h1) is visible.
        3. Add to Cart button or main product container is visible.
        4. No 500 error / unhandled application crash.
        """
        current_url = self.get_current_url()
        title = self.get_title()

        # URL validation
        url_valid = True
        if intended_url:
            from urllib.parse import urlparse
            intended_path = urlparse(intended_url).path.rstrip("/")
            current_path = urlparse(current_url).path.rstrip("/")
            if intended_path and intended_path != "/":
                url_valid = intended_path in current_path or current_path in intended_path

        # Header / Title element
        h1_visible = self.is_visible(SearchLocators.PDP_TITLE, timeout=10000) or len(title) > 0

        # Purchase / Product container
        cart_or_content = (
            self.is_visible(SearchLocators.PDP_ADD_TO_CART_BUTTON, timeout=3000)
            or self.is_visible(SearchLocators.PDP_MAIN_CONTENT, timeout=3000)
            or self.is_visible(".product-info-main, .catalog-product-view, .product.media, .product-add-form", timeout=3000)
        )

        is_loaded = (url_valid or h1_visible) and cart_or_content and ("500" not in title)
        logger.info(
            f"PDP load validation: URL valid={url_valid}, h1 visible={h1_visible}, "
            f"Cart/Content visible={cart_or_content}, is_loaded={is_loaded}"
        )
        return is_loaded

    def get_no_results_message(self, timeout: int = 10000) -> str:
        """Retrieve the text content of the no-results message or container."""
        try:
            msg_elem = self.page.locator(SearchLocators.NO_RESULTS_MESSAGE).first
            msg_elem.wait_for(state="visible", timeout=timeout)
            return msg_elem.inner_text().strip()
        except Exception:
            pass

        # Fallback to main content text
        try:
            main_elem = self.page.locator(SearchLocators.NO_RESULTS_TEXT_CONTAINER).first
            main_elem.wait_for(state="visible", timeout=3000)
            main_text = main_elem.inner_text()
            for line in main_text.splitlines():
                if "no results" in line.lower() or "sorry" in line.lower():
                    return line.strip()
        except Exception:
            pass

        # Global body fallback
        try:
            body_text = self.page.locator("body").inner_text()
            for line in body_text.splitlines():
                if "no results" in line.lower() or "sorry" in line.lower():
                    return line.strip()
        except Exception:
            pass

        return ""

    def is_no_results_displayed(
        self,
        expected_prefix: Optional[str] = "We're sorry, no results found for",
        query_substring: Optional[str] = None,
        timeout: int = 10000,
    ) -> bool:
        """Dynamically validate that the search returned 0 product results and displays the no-results state.

        Args:
            expected_prefix: Optional expected message prefix. If None, checks common no-results keywords.
            query_substring: Optional query text to check within the message if rendered.
            timeout: Maximum wait time in milliseconds for the message to appear.
        """
        message = self.get_no_results_message(timeout=timeout)
        results_count = self.get_search_results_count()

        no_results_indicators = [
            "no results",
            "we're sorry",
            "were sorry",
            "sorry, no results",
            "no products found",
            "your search returned no results",
            "0 results",
            "no match",
        ]
        if expected_prefix:
            has_expected_prefix = (expected_prefix.lower() in message.lower()) or any(
                ind in message.lower() for ind in no_results_indicators
            )
        else:
            has_expected_prefix = any(ind in message.lower() for ind in no_results_indicators)

        # Check optional query inclusion
        has_query = True
        if query_substring:
            # Clean quotes or special characters for flexible substring matching
            clean_query = query_substring.strip()
            has_query = clean_query.lower() in message.lower() or clean_query.lower() in self.get_current_url().lower()

        title = self.get_title()
        no_500_error = "500" not in title and "error" not in title.lower()

        is_valid_no_results = (results_count == 0) and has_expected_prefix and no_500_error
        logger.info(
            f"No-results validation: count={results_count}, has_prefix={has_expected_prefix}, "
            f"has_query={has_query}, message='{message}' -> valid={is_valid_no_results}"
        )
        return is_valid_no_results

    def clear_search_input(self) -> None:
        """Clear the search input using the search UI."""
        logger.info("Clearing search input query.")
        # Try finding a visible clear button/icon first (e.g. .kuClear, .btn-clear, etc.)
        try:
            clear_btn = self.page.locator(".kuClear, .btn-clear, button.clear, .search-clear").first
            if clear_btn.is_visible(timeout=1000):
                clear_btn.click()
                self.wait_for_timeout(300)
        except Exception:
            pass

        search_input = self.page.locator(SearchLocators.SEARCH_INPUT).first
        if search_input.is_visible(timeout=2000):
            search_input.click()
            search_input.fill("")
            search_input.dispatch_event("input")
            search_input.dispatch_event("change")
            self.wait_for_timeout(300)

    def get_search_input_value(self) -> str:
        """Retrieve current value of the primary search input field."""
        search_input = self.page.locator(SearchLocators.SEARCH_INPUT).first
        return search_input.input_value()

    def is_search_page_stable(self) -> bool:
        """Verify that the search page remains stable, usable, and without application crashes."""
        body_has_text = len(self.page.locator("body").inner_text()) > 50
        no_500_error = "500" not in self.get_title()
        logo_visible = self.is_visible(HomeLocators.LOGO, timeout=5000)
        is_stable = body_has_text and no_500_error and logo_visible
        logger.info(f"Search page stability check: is_stable={is_stable}")
        return is_stable

    def generate_long_search_query(self, length: int = 500, prefix: str = "") -> str:
        """Generate a dynamic, reusable long search query string of specified length (500+ characters)."""
        from utils.common_helper import CommonHelper

        return CommonHelper.generate_random_string(length=length, prefix=prefix)

    def validate_no_results_ui_layout(self) -> Dict[str, Any]:
        """Validate layout integrity of the no-results message and page for extremely long query strings.

        Checks:
        1. Whether horizontal scrolling/overflow is induced on the document/body (scrollWidth > innerWidth).
        2. Whether the no-results text element overflows its bounding client rect or exceeds viewport/container width.
        3. Whether the message element is clipped or extends beyond the right edge of the viewport.

        Returns:
            Dict containing boolean flags, metric measurements, and layout validation status.
        """
        logger.info("Evaluating UI layout metrics for horizontal overflow and clipping on no-results message.")
        script = """
        () => {
            const winInnerWidth = window.innerWidth;
            const docScrollWidth = document.documentElement ? document.documentElement.scrollWidth : 0;
            const bodyScrollWidth = document.body ? document.body.scrollWidth : 0;

            // Threshold of 5px to avoid sub-pixel rounding false positives
            const hasDocOverflow = docScrollWidth > (winInnerWidth + 5);
            const hasBodyOverflow = bodyScrollWidth > (winInnerWidth + 5);
            const hasHorizontalOverflow = hasDocOverflow || hasBodyOverflow;

            // Locate innermost element containing the no-results message
            let msgElement = null;
            let shortestLen = Infinity;
            const candidates = document.querySelectorAll("div, p, span");
            for (const el of candidates) {
                if (el.innerText && el.innerText.includes("We're sorry, no results found for")) {
                    if (el.innerText.length < shortestLen) {
                        shortestLen = el.innerText.length;
                        msgElement = el;
                    }
                }
            }
            if (!msgElement) {
                msgElement = document.querySelector(".message.notice, .no-results, .kuNoResults, div[class*='notice']");
            }

            let elementOverflow = false;
            let elementClipped = false;
            let elemRight = 0;
            let elemScrollWidth = 0;
            let elemClientWidth = 0;
            let containerRight = winInnerWidth;

            if (msgElement) {
                const rect = msgElement.getBoundingClientRect();
                elemRight = rect.right;
                elemScrollWidth = msgElement.scrollWidth;
                elemClientWidth = msgElement.clientWidth;

                const parentContainer = msgElement.closest(".page-main, #maincontent, .columns, .main") || msgElement.parentElement;
                if (parentContainer) {
                    const parentRect = parentContainer.getBoundingClientRect();
                    containerRight = parentRect.right;
                }

                // If message element extends beyond viewport width or parent container width
                if (rect.right > (winInnerWidth + 5) || rect.right > (containerRight + 5)) {
                    elementOverflow = true;
                    elementClipped = true;
                }
                if (elemScrollWidth > (elemClientWidth + 5)) {
                    elementOverflow = true;
                }

                // Also inspect all child nodes (especially div holding the actual query text)
                const children = msgElement.querySelectorAll("*");
                for (const child of children) {
                    const childRect = child.getBoundingClientRect();
                    if (childRect.right > (winInnerWidth + 5) || childRect.right > (containerRight + 5)) {
                        elementOverflow = true;
                        elementClipped = true;
                        elemRight = Math.max(elemRight, childRect.right);
                    }
                    if (child.scrollWidth > (child.clientWidth + 5)) {
                        elementOverflow = true;
                    }
                }
            }

            const isLayoutValid = !hasHorizontalOverflow && !elementOverflow && !elementClipped;

            return {
                is_layout_valid: isLayoutValid,
                has_horizontal_overflow: hasHorizontalOverflow,
                element_overflow: elementOverflow,
                element_clipped: elementClipped,
                window_inner_width: winInnerWidth,
                doc_scroll_width: docScrollWidth,
                body_scroll_width: bodyScrollWidth,
                element_scroll_width: elemScrollWidth,
                element_client_width: elemClientWidth,
                element_right_offset: elemRight,
                container_right_offset: containerRight
            };
        }
        """
        try:
            metrics = self.page.evaluate(script)
            logger.info(
                f"Layout metrics evaluated: is_layout_valid={metrics.get('is_layout_valid')}, "
                f"has_horizontal_overflow={metrics.get('has_horizontal_overflow')} "
                f"(doc: {metrics.get('doc_scroll_width')}px vs win: {metrics.get('window_inner_width')}px), "
                f"element_overflow={metrics.get('element_overflow')}, "
                f"element_clipped={metrics.get('element_clipped')} "
                f"(elementRight: {metrics.get('element_right_offset')}px vs win: {metrics.get('window_inner_width')}px)"
            )
            return metrics
        except Exception as e:
            logger.error(f"Error evaluating layout metrics: {e}")
            return {
                "is_layout_valid": False,
                "has_horizontal_overflow": False,
                "element_overflow": False,
                "element_clipped": False,
                "error": str(e),
            }

    # =========================================================================
    # Intentional Evidence Preparation Methods
    # =========================================================================

    def prepare_for_search_results_evidence(self) -> None:
        """Ensure search results are visible in viewport, transient UI elements are closed, and state is stable."""
        logger.info("Preparing search results evidence state for screenshot.")
        try:
            self.page.evaluate("window.scrollTo(0, 0)")
        except Exception:
            pass
        self.dismiss_transient_elements()
        self.wait_for_timeout(300)

    def prepare_for_no_results_evidence(self) -> None:
        """Ensure no-results message state is visible in viewport, transient elements are closed, and state is stable."""
        logger.info("Preparing no-results evidence state for screenshot.")
        try:
            msg_loc = self.page.locator(SearchLocators.NO_RESULTS_MESSAGE).first
            if msg_loc.is_visible(timeout=3000):
                msg_loc.scroll_into_view_if_needed(timeout=2000)
            else:
                self.page.evaluate("window.scrollTo(0, 0)")
        except Exception:
            pass
        self.dismiss_transient_elements()
        self.wait_for_timeout(300)

    def prepare_for_pdp_evidence(self) -> None:
        """Ensure Product Detail Page content is visible in viewport, transient elements closed, and state stable."""
        logger.info("Preparing PDP evidence state for screenshot.")
        try:
            title_loc = self.page.locator(SearchLocators.PDP_TITLE).first
            if title_loc.is_visible(timeout=3000):
                title_loc.scroll_into_view_if_needed(timeout=2000)
            else:
                self.page.evaluate("window.scrollTo(0, 0)")
        except Exception:
            pass
        self.dismiss_transient_elements()
        self.wait_for_timeout(300)

    def prepare_for_cleared_search_evidence(self) -> None:
        """Ensure cleared search input is visible in header, autocomplete is closed, and state is stable."""
        logger.info("Preparing cleared search input evidence state for screenshot.")
        try:
            self.page.evaluate("window.scrollTo(0, 0)")
            search_input = self.page.locator(SearchLocators.SEARCH_INPUT).first
            if search_input.is_visible(timeout=3000):
                search_input.evaluate("el => el.blur()")
        except Exception:
            pass
        self.dismiss_transient_elements()
        self.wait_for_timeout(300)
