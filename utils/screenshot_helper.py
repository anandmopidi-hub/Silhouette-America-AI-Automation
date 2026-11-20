from pathlib import Path
from typing import Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from utils.common_helper import CommonHelper
from utils.logger import logger
from utils.wait_helper import WaitHelper

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "artifacts" / "screenshots"
PASSED_DIR = SCREENSHOTS_DIR / "passed"
FAILED_DIR = SCREENSHOTS_DIR / "failed"
SKIPPED_DIR = SCREENSHOTS_DIR / "skipped"

CommonHelper.ensure_directory(PASSED_DIR)
CommonHelper.ensure_directory(FAILED_DIR)
CommonHelper.ensure_directory(SKIPPED_DIR)


class ScreenshotHelper:
    """Centralized screenshot helper ensuring clean, stable DOM and UI state

    prior to capturing intentional test evidence screenshots.
    """

    @classmethod
    def dismiss_transient_elements(cls, page: Page) -> None:
        """Dismiss temporary UI elements such as My Cart drawer/popup, overlays,
        dropdowns, search autocomplete suggestions, menus, cookie popups, and loading indicators.
        """
        try:
            # 1. Blur active element to close open focus-triggered overlays/dropdowns
            try:
                page.evaluate("() => { if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); }")
                page.keyboard.press("Escape")
                page.wait_for_timeout(200)
            except Exception:
                pass

            # 2. Dismiss cookie/consent banners if present
            try:
                WaitHelper.handle_known_popups(page, timeout=1000)
            except Exception:
                pass

            # 3. Close Magento 'My Cart' drawer/popup if visible
            try:
                minicart_close = page.locator("#btn-minicart-close, .block-minicart .action.close, [data-action='close']").first
                if minicart_close.is_visible(timeout=500):
                    minicart_close.click(timeout=1000)
                    page.wait_for_timeout(200)
            except Exception:
                pass

            # 4. Hide lingering minicart or autocomplete popups via JS safely
            try:
                page.evaluate("""() => {
                    // Close/hide minicart popup if open
                    document.querySelectorAll('.minicart-wrapper .block-minicart, [data-block="minicart"] .block-minicart').forEach(el => {
                        el.style.display = 'none';
                    });
                    document.querySelectorAll('.ui-dialog').forEach(el => {
                        if (el.querySelector('.block-minicart') || (el.innerText && el.innerText.trim().startsWith('My Cart'))) {
                            el.style.display = 'none';
                        }
                    });
                    // Hide ONLY search autocomplete suggestion popup, never the main search results container
                    document.querySelectorAll(
                        '.kuQuickSearchAutoCompleteLayout, .kuQuickSearchResultsContainer, #klevuSearchingArea, .klevuQuickSearchingArea, #search_autocomplete, div.kuQuickSearchAutoComplete, div.search-autocomplete'
                    ).forEach(el => {
                        el.style.setProperty('display', 'none', 'important');
                    });
                }""")
            except Exception:
                pass

            # 5. Click neutral space on the page to trigger native blur/outside-click listeners
            try:
                page.locator("body").click(position={"x": 50, "y": 300}, timeout=1000)
            except Exception:
                pass

            # 5. Wait for any loading spinners or loaders to detach or disappear
            try:
                loading_mask = page.locator(".loading-mask, .loader, [data-role='loader'], .ku-loader, .klevu-loading").first
                if loading_mask.is_visible(timeout=500):
                    loading_mask.wait_for(state="hidden", timeout=3000)
            except Exception:
                pass

            # 6. Ensure DOM is stable
            WaitHelper.wait_for_dom_content_loaded(page, timeout=3000)
            page.wait_for_timeout(300)

        except Exception as e:
            logger.debug(f"Transient elements dismissal completed with non-blocking notice: {e}")

    @classmethod
    def capture_screenshot(
        cls,
        page: Page,
        test_name: str,
        status: str = "failed",
        handle_popups: bool = True,
        target_element: Optional[object] = None,
        custom_suffix: Optional[str] = None,
    ) -> Optional[Path]:
        """Capture screenshot following strict stability and clean evidence rules:

        1. Wait for DOMContentLoaded.
        2. Optionally scroll target element into view if provided.
        3. Dismiss transient UI elements (My Cart, autocomplete, popups, loaders).
        4. Wait for DOM and UI to stabilize.
        5. Capture screenshot into artifacts/screenshots/{passed|failed}/.
        """
        try:
            # Rule 1: Wait for DOMContentLoaded
            WaitHelper.wait_for_dom_content_loaded(page, timeout=5000)

            # Rule 2: Scroll target element into view if specified
            if target_element is not None:
                try:
                    from playwright.sync_api import Locator
                    loc = target_element if isinstance(target_element, Locator) else page.locator(str(target_element))
                    if loc.first.is_visible(timeout=2000):
                        loc.first.scroll_into_view_if_needed(timeout=2000)
                        page.wait_for_timeout(300)
                except Exception as e:
                    logger.debug(f"Target element scroll into view notice: {e}")

            # Rule 3: Dismiss transient UI elements (My Cart, autocomplete, cookie popups, etc.)
            if handle_popups:
                cls.dismiss_transient_elements(page)

            # Rule 4: Wait for state to settle
            try:
                page.wait_for_load_state("load", timeout=3000)
            except PlaywrightTimeoutError:
                pass

            # Target directory based on outcome
            if status.lower() == "passed":
                target_dir = PASSED_DIR
            elif status.lower() == "skipped":
                target_dir = SKIPPED_DIR
            else:
                target_dir = FAILED_DIR
            CommonHelper.ensure_directory(target_dir)

            timestamp = CommonHelper.get_timestamp()
            clean_name = CommonHelper.sanitize_filename(test_name)

            # Extract Test Case ID if present (e.g., E2E-HOME-001, E2E-ORDER_Purchase-001, E2E-Different_PDP-001)
            import re
            diff_pdp_match = re.search(r"E2E[-_]DIFFERENT[-_]PDP[-_](\d+)", test_name, re.IGNORECASE)
            order_tc_match = re.search(r"E2E[-_]ORDER[-_]PURCHASE[-_](\d+)", test_name, re.IGNORECASE)
            tc_match = re.search(r"(E2E[-_][A-Za-z0-9]+[-_]\d+)", test_name, re.IGNORECASE)
            suffix_part = f"_{CommonHelper.sanitize_filename(custom_suffix)}" if custom_suffix else ""
            if diff_pdp_match:
                tc_id = f"E2E-Different_PDP-{diff_pdp_match.group(1)}"
                file_name = f"{tc_id}{suffix_part}_{status.lower()}.png"
            elif order_tc_match:
                tc_id = f"E2E-ORDER_Purchase-{order_tc_match.group(1)}"
                file_name = f"{tc_id}{suffix_part}_{status.lower()}.png"
            elif tc_match:
                tc_id = tc_match.group(1).upper().replace("_", "-")
                file_name = f"{tc_id}{suffix_part}_{status.lower()}.png"
            else:
                file_name = f"{clean_name}_{status.lower()}_{timestamp}{suffix_part}.png"

            file_path = target_dir / file_name

            page.screenshot(path=str(file_path), full_page=True)
            logger.info(f"Captured {status} screenshot for '{test_name}' at: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Failed to capture screenshot for '{test_name}': {e}")
            return None
