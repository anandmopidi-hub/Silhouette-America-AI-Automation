import time
from typing import Callable, List, Optional, Union
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError
from utils.logger import logger


class WaitHelper:
    """Reusable synchronization and explicit wait utilities utilizing

    Playwright's event-driven and state-based mechanisms instead of arbitrary sleeps.
    """

    @staticmethod
    def wait_for_dom_content_loaded(page: Page, timeout: Optional[int] = None) -> None:
        """Wait for the DOMContentLoaded state on the page."""
        try:
            page.wait_for_load_state("domcontentloaded", timeout=timeout)
        except PlaywrightTimeoutError as e:
            logger.warning(f"Timeout waiting for domcontentloaded state: {e}")

    @staticmethod
    def wait_for_network_idle(page: Page, timeout: Optional[int] = None) -> None:
        """Wait until network is idle (no connections for at least 500 ms)."""
        try:
            page.wait_for_load_state("networkidle", timeout=timeout)
        except PlaywrightTimeoutError as e:
            logger.warning(f"Timeout waiting for networkidle state: {e}")

    @staticmethod
    def wait_for_visible(
        target: Union[Page, Locator],
        selector: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Locator:
        """Wait for a selector (on Page) or Locator to become visible."""
        if isinstance(target, Page):
            if not selector:
                raise ValueError("A selector string is required when passing a Page instance.")
            locator = target.locator(selector)
        else:
            locator = target

        locator.wait_for(state="visible", timeout=timeout)
        return locator

    @staticmethod
    def wait_for_hidden(
        target: Union[Page, Locator],
        selector: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """Wait for a selector (on Page) or Locator to be hidden or detached."""
        if isinstance(target, Page):
            if not selector:
                raise ValueError("A selector string is required when passing a Page instance.")
            locator = target.locator(selector)
        else:
            locator = target

        locator.wait_for(state="hidden", timeout=timeout)

    @staticmethod
    def wait_for_url_contains(page: Page, text: str, timeout: Optional[int] = None) -> bool:
        """Wait for the current URL to contain a specific substring."""
        try:
            page.wait_for_url(lambda u: text in u, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    @staticmethod
    def wait_for_condition(
        condition: Callable[[], bool],
        timeout_sec: float = 10.0,
        poll_interval_sec: float = 0.25,
        error_message: str = "Condition not met within timeout",
    ) -> bool:
        """Poll a predicate condition until it evaluates to True or timeout expires."""
        end_time = time.monotonic() + timeout_sec
        while time.monotonic() < end_time:
            try:
                if condition():
                    return True
            except Exception:
                pass
            time.sleep(poll_interval_sec)
        raise TimeoutError(f"{error_message} (waited {timeout_sec}s)")

    @staticmethod
    def handle_known_popups(
        page: Page,
        popup_selectors: Optional[List[str]] = None,
        timeout: int = 3000,
    ) -> bool:
        """Attempt to dismiss known popups/overlays (e.g. cookies, promotions)

        if they appear, waiting for them to detach.
        """
        default_selectors = [
            "button[data-amgdprcookie-js='accept']",
            "button:has-text('I Agree')",
            "button:has-text('I agree')",
            ".amgdprcookie-button.-allow",
            "button#onetrust-accept-btn-handler",
            "button:has-text('Accept All Cookies')",
            "button:has-text('Accept Cookies')",
            "button.action-close[data-amcookie-js='close-cookiebar']",
        ]
        container_selectors = [
            "[data-amcookie-js='bar']",
            ".amgdprcookie-bar-container",
            ".modal-popup._show.amgdprcookie-bar-container",
            ".modal-popup._show:has-text('We use cookies')",
            ".amgdprcookie-bar-template",
        ]
        selectors = popup_selectors or default_selectors
        dismissed = False

        for sel in selectors:
            try:
                loc = page.locator(sel).first
                if loc.is_visible():
                    logger.info(f"Cookie/popup banner detected with selector: {sel}. Clicking to dismiss...")
                    loc.click(timeout=timeout)
                    # Wait for button to hide
                    try:
                        loc.wait_for(state="hidden", timeout=timeout)
                    except Exception:
                        pass
                    # Wait for container to hide completely
                    for c_sel in container_selectors:
                        try:
                            c_loc = page.locator(c_sel).first
                            if c_loc.count() > 0:
                                c_loc.wait_for(state="hidden", timeout=timeout)
                        except Exception:
                            pass
                    logger.info(f"Handled and completely dismissed popup with selector: {sel}")
                    dismissed = True
                    break
            except Exception:
                continue

        if not dismissed and selectors:
            try:
                primary = page.locator(selectors[0]).first
                if primary.is_visible(timeout=timeout):
                    logger.info(f"Primary cookie/popup selector visible: {selectors[0]}. Clicking...")
                    primary.click(timeout=timeout)
                    try:
                        primary.wait_for(state="hidden", timeout=timeout)
                    except Exception:
                        pass
                    for c_sel in container_selectors:
                        try:
                            c_loc = page.locator(c_sel).first
                            if c_loc.count() > 0:
                                c_loc.wait_for(state="hidden", timeout=timeout)
                        except Exception:
                            pass
                    logger.info(f"Handled and completely dismissed popup with selector: {selectors[0]}")
                    dismissed = True
            except Exception:
                pass

        return dismissed
