from typing import Any, List, Optional, Union
from playwright.sync_api import Locator, Page, Response, TimeoutError as PlaywrightTimeoutError
from config.config import Config, get_config
from utils.logger import logger
from utils.wait_helper import WaitHelper


class BasePage:
    """Foundational Base Page providing common, reusable Playwright interactions

    and assertions for all future Page Objects.

    Business-specific methods (such as login, add_to_cart, checkout) should NOT
    be placed here; they belong in specialized Page Objects inheriting from BasePage.
    """

    def __init__(self, page: Page, config: Optional[Config] = None):
        """Initialize the BasePage.

        Args:
            page: Playwright Page instance.
            config: Framework configuration instance.
        """
        self.page = page
        self.config = config or get_config()
        self.timeout = self.config.timeout
        self._cdp_session = None

    def _resolve_locator(self, target: Union[str, Locator]) -> Locator:
        """Resolve either a CSS/XPath string or an existing Locator into a Locator object."""
        if isinstance(target, str):
            return self.page.locator(target)
        return target

    # =========================================================================
    # Navigation Methods
    # =========================================================================

    def goto(self, path_or_url: str = "", wait_until: str = "domcontentloaded") -> Optional[Response]:
        """Navigate to a given path (relative to BASE_URL) or absolute URL.

        Args:
            path_or_url: URL or relative path (e.g., '/shop' or 'https://...').
            wait_until: Navigation wait condition ('load', 'domcontentloaded', 'networkidle', 'commit').
        """
        url = path_or_url if path_or_url.startswith("http") else f"{self.config.base_url.rstrip('/')}/{path_or_url.lstrip('/')}"
        logger.info(f"Navigating to URL: {url} (wait_until={wait_until})")
        response = self.page.goto(url, wait_until=wait_until, timeout=self.timeout)  # type: ignore
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        return response

    def reload(self, wait_until: str = "domcontentloaded") -> Optional[Response]:
        """Reload the current page."""
        logger.info("Reloading current page")
        response = self.page.reload(wait_until=wait_until, timeout=self.timeout)  # type: ignore
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        return response

    def go_back(self, wait_until: str = "domcontentloaded") -> Optional[Response]:
        """Navigate back in browser history."""
        logger.info("Navigating back in browser history")
        response = self.page.go_back(wait_until=wait_until, timeout=self.timeout)  # type: ignore
        self.wait_for_dom_content_loaded()
        self.dismiss_cookie_consent_if_present()
        return response

    def go_forward(self, wait_until: str = "domcontentloaded") -> Optional[Response]:
        """Navigate forward in browser history."""
        logger.info("Navigating forward in browser history")
        response = self.page.go_forward(wait_until=wait_until, timeout=self.timeout)  # type: ignore
        self.wait_for_dom_content_loaded()
        self.dismiss_cookie_consent_if_present()
        return response

    # =========================================================================
    # Cloudflare Challenge & Centralized Cookie Consent Management
    # =========================================================================

    def handle_cloudflare_if_present(self, timeout: int = 15000) -> bool:
        """Handle Cloudflare challenge screen if present, waiting for automatic resolution."""
        try:
            title = self.get_title().lower()
            is_challenge = "just a moment" in title or "cloudflare" in title or "attention required" in title
            if not is_challenge:
                try:
                    challenge_text = self.page.locator(
                        "text='Checking your browser', text='one-time security check', text='Verifying you are human'"
                    ).first
                    if challenge_text.is_visible(timeout=500):
                        is_challenge = True
                except Exception:
                    pass

            if is_challenge:
                logger.info("Cloudflare challenge screen active. Waiting for automatic resolution...")
                self.page.wait_for_function(
                    """() => {
                        const title = document.title.toLowerCase();
                        const body = document.body ? document.body.innerText.toLowerCase() : '';
                        const hasTitle = title.includes('just a moment') || title.includes('cloudflare');
                        const hasBody = body.includes('checking your browser') || body.includes('one-time security check') || body.includes('verifying you are human');
                        return !hasTitle && !hasBody;
                    }""",
                    timeout=timeout,
                )
                self.wait_for_dom_content_loaded()
                self.wait_for_timeout(1000)
                return True
        except Exception as e:
            logger.debug(f"Cloudflare challenge wait notice: {e}")
        return False

    def dismiss_cookie_consent_if_present(self, timeout: int = 3000) -> bool:
        """Centrally detect and dismiss cookie consent popup ('I Agree') if visible.

        Required behavior:
        1. When the cookie consent popup is visible, click 'I Agree' first.
        2. Wait until the cookie popup is completely dismissed.
        3. Only after the popup is closed, continue with intended test steps.
        4. Make sure automation continues on the intended page, NOT 'My Cart' drawer.
        5. Verify the page is stable before continuing.
        """
        cookie_accept_selectors = [
            "button[data-amgdprcookie-js='accept']",
            "button:has-text('I Agree')",
            "button:has-text('I agree')",
            ".amgdprcookie-button.-allow",
            "button#onetrust-accept-btn-handler",
            "button:has-text('Accept All Cookies')",
            "button:has-text('Accept Cookies')",
        ]
        cookie_container_selectors = [
            "[data-amcookie-js='bar']",
            ".amgdprcookie-bar-container",
            ".modal-popup._show.amgdprcookie-bar-container",
            ".modal-popup._show:has-text('We use cookies')",
            ".amgdprcookie-bar-template",
        ]

        dismissed = False
        try:
            # 1. Detect if accept button is visible or appears within brief window
            accept_btn = None
            for sel in cookie_accept_selectors:
                try:
                    loc = self.page.locator(sel).first
                    if loc.is_visible(timeout=800):
                        accept_btn = loc
                        break
                except Exception:
                    continue

            # Fallback polling if not immediately visible
            if not accept_btn:
                for sel in cookie_accept_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if loc.is_visible(timeout=timeout):
                            accept_btn = loc
                            break
                    except Exception:
                        continue

            if accept_btn:
                logger.info("Cookie consent banner detected. Clicking 'I Agree' first...")
                accept_btn.click(timeout=timeout)
                dismissed = True

                # 2. Wait until the cookie popup is completely dismissed
                logger.info("Waiting for cookie consent popup to be completely dismissed...")
                for c_sel in cookie_container_selectors:
                    try:
                        c_loc = self.page.locator(c_sel).first
                        if c_loc.count() > 0:
                            c_loc.wait_for(state="hidden", timeout=timeout)
                    except Exception:
                        pass

                try:
                    accept_btn.wait_for(state="hidden", timeout=timeout)
                except Exception:
                    pass

                # If container stubbornly remains visible, click close button or hide
                for c_sel in cookie_container_selectors:
                    try:
                        c_loc = self.page.locator(c_sel).first
                        if c_loc.is_visible(timeout=300):
                            close_btn = self.page.locator("button.action-close[data-amcookie-js='close-cookiebar']").first
                            if close_btn.is_visible(timeout=300):
                                close_btn.click(timeout=1000)
                                c_loc.wait_for(state="hidden", timeout=2000)
                    except Exception:
                        pass

                # Dismiss backdrop overlay if still displayed
                try:
                    overlay = self.page.locator(".modals-overlay._show, .modals-overlay").first
                    if overlay.is_visible(timeout=300):
                        overlay.wait_for(state="hidden", timeout=2000)
                except Exception:
                    pass

                logger.info("Cookie consent popup completely dismissed.")
                self.wait_for_timeout(300)

        except Exception as e:
            logger.debug(f"Cookie consent handling notice: {e}")

        # 3. Ensure automation continues on intended page, NOT 'My Cart' drawer
        self.ensure_minicart_closed()

        # 4. Verify page is stable
        self.wait_for_dom_content_loaded()

        return dismissed

    def ensure_minicart_closed(self) -> None:
        """Verify that the Magento 'My Cart' / minicart drawer is not open.

        If opened by stray hover/click event or overlay shift, close it cleanly
        so automation stays on the intended page.
        """
        try:
            minicart = self.page.locator(".block-minicart:visible, .mage-dropdown-dialog:visible")
            if minicart.count() > 0 and minicart.first.is_visible(timeout=300):
                logger.info("'My Cart' drawer detected as open. Dismissing to stay on intended page...")
                close_btn = self.page.locator("#btn-minicart-close, .block-minicart .action.close, [data-action='close']").first
                if close_btn.is_visible(timeout=500):
                    close_btn.click(timeout=1000)
                else:
                    self.page.keyboard.press("Escape")
                self.wait_for_timeout(300)

                # Safe fallback to guarantee drawer is closed
                if minicart.first.is_visible(timeout=300):
                    self.page.evaluate("""() => {
                        document.querySelectorAll('.minicart-wrapper .block-minicart, [data-block="minicart"] .block-minicart, .mage-dropdown-dialog').forEach(el => {
                            el.style.display = 'none';
                        });
                    }""")
        except Exception as e:
            logger.debug(f"Minicart check notice: {e}")

    # =========================================================================
    # Action Methods
    # =========================================================================

    def click(self, target: Union[str, Locator], timeout: Optional[int] = None) -> None:
        """Click an element."""
        loc = self._resolve_locator(target)
        logger.debug(f"Clicking element: {target}")
        loc.click(timeout=timeout or self.timeout)

    def double_click(self, target: Union[str, Locator], timeout: Optional[int] = None) -> None:
        """Double click an element."""
        loc = self._resolve_locator(target)
        logger.debug(f"Double clicking element: {target}")
        loc.dblclick(timeout=timeout or self.timeout)

    def force_click(self, target: Union[str, Locator], timeout: Optional[int] = None) -> None:
        """Force click an element, bypassing actionability checks."""
        loc = self._resolve_locator(target)
        logger.debug(f"Force clicking element: {target}")
        loc.click(force=True, timeout=timeout or self.timeout)

    def hover(self, target: Union[str, Locator], timeout: Optional[int] = None) -> None:
        """Hover over an element."""
        loc = self._resolve_locator(target)
        logger.debug(f"Hovering over element: {target}")
        loc.hover(timeout=timeout or self.timeout)

    def fill(self, target: Union[str, Locator], value: str, timeout: Optional[int] = None) -> None:
        """Fill an input field with text (clears existing value first)."""
        loc = self._resolve_locator(target)
        logger.debug(f"Filling element: {target} with value: '{value}'")
        loc.fill(value, timeout=timeout or self.timeout)

    def type_text(self, target: Union[str, Locator], text: str, delay: int = 50, timeout: Optional[int] = None) -> None:
        """Type characters sequentially into an element with a specified delay."""
        loc = self._resolve_locator(target)
        logger.debug(f"Typing text into element: {target} (delay={delay}ms)")
        loc.press_sequentially(text, delay=delay, timeout=timeout or self.timeout)

    def clear(self, target: Union[str, Locator], timeout: Optional[int] = None) -> None:
        """Clear text from an input field."""
        loc = self._resolve_locator(target)
        logger.debug(f"Clearing input element: {target}")
        loc.clear(timeout=timeout or self.timeout)

    def press_key(self, target: Union[str, Locator], key: str, timeout: Optional[int] = None) -> None:
        """Press a keyboard key on an element (e.g., 'Enter', 'Tab', 'Escape')."""
        loc = self._resolve_locator(target)
        logger.debug(f"Pressing key '{key}' on element: {target}")
        loc.press(key, timeout=timeout or self.timeout)

    def select_option(
        self,
        target: Union[str, Locator],
        value: Optional[str] = None,
        label: Optional[str] = None,
        index: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> List[str]:
        """Select an option in a `<select>` dropdown by value, label, or index."""
        loc = self._resolve_locator(target)
        logger.debug(f"Selecting dropdown option for: {target}")
        return loc.select_option(value=value, label=label, index=index, timeout=timeout or self.timeout)

    # =========================================================================
    # Validation & Inspection Methods
    # =========================================================================

    def get_text(self, target: Union[str, Locator], timeout: Optional[int] = None) -> str:
        """Retrieve inner text of an element."""
        loc = self._resolve_locator(target)
        text = loc.inner_text(timeout=timeout or self.timeout)
        return text.strip()

    def get_attribute(self, target: Union[str, Locator], name: str, timeout: Optional[int] = None) -> Optional[str]:
        """Retrieve value of an attribute from an element."""
        loc = self._resolve_locator(target)
        return loc.get_attribute(name, timeout=timeout or self.timeout)

    def get_input_value(self, target: Union[str, Locator], timeout: Optional[int] = None) -> str:
        """Retrieve current value of an input or textarea element."""
        loc = self._resolve_locator(target)
        return loc.input_value(timeout=timeout or self.timeout)

    def is_visible(self, target: Union[str, Locator], timeout: Optional[int] = None) -> bool:
        """Check if an element is visible on the page."""
        loc = self._resolve_locator(target)
        try:
            return loc.first.is_visible(timeout=timeout or 3000)
        except Exception:
            return False

    def is_hidden(self, target: Union[str, Locator], timeout: Optional[int] = None) -> bool:
        """Check if an element is hidden or detached."""
        loc = self._resolve_locator(target)
        try:
            return loc.first.is_hidden(timeout=timeout or 3000)
        except Exception:
            return True

    def is_enabled(self, target: Union[str, Locator], timeout: Optional[int] = None) -> bool:
        """Check if an element is enabled."""
        loc = self._resolve_locator(target)
        try:
            return loc.first.is_enabled(timeout=timeout or self.timeout)
        except Exception:
            return False

    def is_disabled(self, target: Union[str, Locator], timeout: Optional[int] = None) -> bool:
        """Check if an element is disabled."""
        loc = self._resolve_locator(target)
        try:
            return loc.first.is_disabled(timeout=timeout or self.timeout)
        except Exception:
            return False

    def is_checked(self, target: Union[str, Locator], timeout: Optional[int] = None) -> bool:
        """Check if a checkbox or radio button is checked."""
        loc = self._resolve_locator(target)
        try:
            return loc.first.is_checked(timeout=timeout or self.timeout)
        except Exception:
            return False

    # =========================================================================
    # Browser / Page State Methods
    # =========================================================================

    def get_current_url(self) -> str:
        """Return the current URL of the page."""
        return self.page.url

    def get_title(self) -> str:
        """Return the current title of the page."""
        return self.page.title()

    def wait_for_url(self, url_or_pattern: Any, timeout: Optional[int] = None) -> None:
        """Wait for the page URL to match a string, regex pattern, or predicate."""
        logger.debug(f"Waiting for URL pattern: {url_or_pattern}")
        self.page.wait_for_url(url_or_pattern, timeout=timeout or self.timeout)

    # =========================================================================
    # Waiting Methods
    # =========================================================================

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: Optional[int] = None) -> Locator:
        """Wait for a selector to reach a specific state ('attached', 'detached', 'visible', 'hidden')."""
        return self.page.wait_for_selector(selector, state=state, timeout=timeout or self.timeout)  # type: ignore

    def wait_for_dom_content_loaded(self, timeout: Optional[int] = None) -> None:
        """Wait for the DOMContentLoaded event."""
        WaitHelper.wait_for_dom_content_loaded(self.page, timeout=timeout or self.timeout)

    def wait_for_network_idle(self, timeout: Optional[int] = None) -> None:
        """Wait for network to be idle."""
        WaitHelper.wait_for_network_idle(self.page, timeout=timeout or self.timeout)

    def wait_for_timeout(self, milliseconds: int) -> None:
        """Pause execution for a given duration in milliseconds (use sparingly)."""
        logger.debug(f"Explicit timeout pause for {milliseconds}ms")
        self.page.wait_for_timeout(milliseconds)

    # =========================================================================
    # Common Scroll & Execution Helpers
    # =========================================================================

    def scroll_to_element(self, target: Union[str, Locator], timeout: Optional[int] = None) -> None:
        """Scroll the page until the target element is in view."""
        loc = self._resolve_locator(target)
        logger.debug(f"Scrolling to element: {target}")
        loc.scroll_into_view_if_needed(timeout=timeout or self.timeout)

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the current page."""
        logger.debug("Scrolling to bottom of the page")
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def evaluate_js(self, expression: str, arg: Any = None) -> Any:
        """Execute a JavaScript expression in the context of the page."""
        logger.debug(f"Evaluating JS expression: {expression}")
        return self.page.evaluate(expression, arg)

    def set_viewport(self, width: int, height: int) -> None:
        """Set the browser page viewport size."""
        logger.info(f"Setting viewport size to {width}x{height}")
        self.page.set_viewport_size({"width": width, "height": height})
        self.wait_for_timeout(300)

    def has_horizontal_overflow(self) -> bool:
        """Check if the document has horizontal scroll overflow exceeding the window viewport."""
        return bool(self.evaluate_js("() => document.documentElement.scrollWidth > window.innerWidth"))

    def emulate_slow_network(
        self,
        latency_ms: int = 300,
        download_kbps: int = 750,
        upload_kbps: int = 500,
    ) -> None:
        """Simulate network throttling (approx. Slow/Fast 3G) using Chrome DevTools Protocol."""
        logger.info(
            f"Emulating slow network: latency={latency_ms}ms, "
            f"download={download_kbps}kbps, upload={upload_kbps}kbps"
        )
        try:
            self._cdp_session = self.page.context.new_cdp_session(self.page)
            self._cdp_session.send(
                "Network.emulateNetworkConditions",
                {
                    "offline": False,
                    "latency": latency_ms,
                    "downloadThroughput": download_kbps * 1024 // 8,
                    "uploadThroughput": upload_kbps * 1024 // 8,
                },
            )
        except Exception as e:
            logger.warning(f"CDP network throttling not available or supported: {e}")

    def reset_network_throttling(self) -> None:
        """Reset network conditions to normal unthrottled state."""
        if hasattr(self, "_cdp_session") and self._cdp_session:
            logger.info("Resetting CDP network conditions")
            try:
                self._cdp_session.send(
                    "Network.emulateNetworkConditions",
                    {
                        "offline": False,
                        "latency": 0,
                        "downloadThroughput": -1,
                        "uploadThroughput": -1,
                    },
                )
                self._cdp_session.detach()
            except Exception as e:
                logger.debug(f"Error resetting CDP session: {e}")
            finally:
                self._cdp_session = None

    # =========================================================================
    # Intentional Screenshot & Clean UI Evidence Helpers
    # =========================================================================

    def dismiss_transient_elements(self) -> None:
        """Dismiss temporary UI elements (My Cart drawer, autocomplete, popups, loaders)."""
        from utils.screenshot_helper import ScreenshotHelper
        ScreenshotHelper.dismiss_transient_elements(self.page)

    def capture_evidence_screenshot(
        self,
        test_name: str,
        target_element: Optional[Union[str, Locator]] = None,
        status: str = "passed",
        custom_suffix: Optional[str] = None,
    ) -> Optional[Any]:
        """Capture intentional evidence screenshot for validated state of a test case.

        Ensures the expected result is visible, transient elements are closed, and UI is stable.
        """
        from utils.screenshot_helper import ScreenshotHelper
        suffix_info = f" (suffix={custom_suffix})" if custom_suffix else ""
        logger.info(f"Capturing intentional evidence screenshot for '{test_name}' [{status.upper()}]{suffix_info}")
        screenshot_path = ScreenshotHelper.capture_screenshot(
            page=self.page,
            test_name=test_name,
            status=status,
            handle_popups=True,
            target_element=target_element,
            custom_suffix=custom_suffix,
        )
        if screenshot_path:
            setattr(self.page, "_evidence_screenshot_path", str(screenshot_path))
        return screenshot_path
