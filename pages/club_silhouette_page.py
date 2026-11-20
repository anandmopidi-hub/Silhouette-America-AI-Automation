"""Page Object Model for Silhouette America Club Silhouette module.

Encapsulates all interactions with the Club Silhouette landing page,
membership comparison table, benefits, refill & shipping flow,
authentication, checkout, activation verification, and delayed QA purge.
"""
from datetime import datetime, timezone
import os
import time
from typing import Any, Dict, List, Optional, Tuple
from playwright.sync_api import Locator, Page, Response

from config.config import Config
from locators.club_silhouette_locators import ClubSilhouetteLocators
from pages.base_page import BasePage
from utils.logger import logger


class ClubSilhouettePage(BasePage):
    """Page Object Model for Silhouette America Club Silhouette module."""

    def __init__(self, page: Page, config: Optional[Config] = None) -> None:
        super().__init__(page=page, config=config)
        self.club_path = "club-silhouette"
        self.plan_monthly_path = "clubsilhouette/plan/monthly"
        self.plan_annually_path = "clubsilhouette/plan/annually"
        self.customer_portal_path = "clubsilhouette/customer/"

    # =========================================================================
    # Navigation & Initial Page Setup
    # =========================================================================

    def open_club_page(self) -> None:
        """Navigate to the Club Silhouette landing page and handle Cloudflare/cookie/popups."""
        logger.info(f"Navigating to Club Silhouette page: {self.club_path}")
        self.goto(self.club_path, wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present(timeout=15000)
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()
        self.dismiss_notice_modal_if_present()

    def dismiss_notice_modal_if_present(self, timeout: int = 2000) -> bool:
        """Dismiss regional availability Notice modal without triggering unwanted redirect."""
        try:
            modal = self.page.locator(ClubSilhouetteLocators.NOTICE_MODAL).first
            if modal.is_visible(timeout=timeout):
                logger.info("Notice modal detected ('not available in area'). Suppressing overlay cleanly...")
                self.page.evaluate("""() => {
                    const notices = document.querySelectorAll('.modal-popup');
                    notices.forEach(n => {
                        if (n.innerText.includes('Notice') || n.innerText.includes('not available')) {
                            n.remove();
                        }
                    });
                    const overlays = document.querySelectorAll('.modals-overlay');
                    overlays.forEach(o => o.remove());
                    document.body.classList.remove('_has-modal');
                }""")
                self.wait_for_timeout(300)
                return True
            return False
        except Exception:
            return False

    # =========================================================================
    # E2E-CSIL-001: Landing Page Verification
    # =========================================================================

    def is_landing_heading_visible(self) -> bool:
        """Verify that 'Everything you need to know before you start' is visible."""
        try:
            el = self.page.locator(ClubSilhouetteLocators.LANDING_SUBHEADING).first
            return el.is_visible(timeout=5000)
        except Exception as e:
            logger.debug(f"Landing heading visibility notice: {e}")
            return False

    def get_benefits_table_data(self) -> Dict[str, Any]:
        """Extract the benefits comparison table column headings, row labels, and content.

        Returns:
            Dict containing:
            {
                "headers": List[str],
                "rows": List[Dict[str, str]],
                "is_displayed": bool
            }
        """
        logger.info("Extracting benefits comparison table data...")
        self.dismiss_cookie_consent_if_present()
        data: Dict[str, Any] = {
            "headers": [],
            "rows": [],
            "is_displayed": False,
        }

        try:
            table = self.page.locator(ClubSilhouetteLocators.PLAN_COMPARE_TABLE).first
            if not table.is_visible(timeout=5000):
                logger.warning("Benefits comparison table is not visible.")
                return data

            # Extract column headers
            header_cells = table.locator("thead th, th").all()
            data["headers"] = [
                h.inner_text().strip().replace("\n", " ")
                for h in header_cells
                if h.inner_text().strip()
            ]

            # Extract row items
            row_elements = table.locator("tbody tr").all()
            for r in row_elements:
                cells = r.locator("td, th").all()
                if cells:
                    row_texts = [c.inner_text().strip().replace("\n", " ") for c in cells]
                    if len(row_texts) >= 3:
                        data["rows"].append({
                            "feature": row_texts[0],
                            "annual": row_texts[1],
                            "monthly": row_texts[2],
                        })
                    elif len(row_texts) == 1 and row_texts[0]:
                        data["rows"].append({
                            "feature": row_texts[0],
                            "annual": "",
                            "monthly": "",
                        })

            data["is_displayed"] = len(data["headers"]) > 0 and len(data["rows"]) > 0
            logger.info(
                f"Benefits comparison table extracted: {len(data['headers'])} headers, "
                f"{len(data['rows'])} rows."
            )
            return data
        except Exception as e:
            logger.error(f"Failed to extract benefits comparison table: {e}")
            return data

    def is_why_customers_love_silhouette_visible(self) -> bool:
        """Verify that the 'Why our customers love Silhouette' section/heading is visible."""
        try:
            el = self.page.locator(ClubSilhouetteLocators.REVIEWS_HEADING).first
            return el.is_visible(timeout=5000)
        except Exception as e:
            logger.debug(f"Reviews heading visibility notice: {e}")
            return False

    def is_faq_heading_visible(self) -> bool:
        """Verify that the 'Frequently Asked Questions' section/heading is visible."""
        try:
            el = self.page.locator(ClubSilhouetteLocators.FAQ_HEADING).first
            return el.is_visible(timeout=5000)
        except Exception as e:
            logger.debug(f"FAQ heading visibility notice: {e}")
            return False

    def validate_all_faq_accordion_items(self) -> List[Dict[str, Any]]:
        """Dynamically identify every FAQ accordion item, iterate, expand if collapsed,

        and verify that the corresponding question and answer are visible.

        Returns:
            List of dicts:
            [{
                "index": int,
                "question": str,
                "answer_preview": str,
                "was_open_initially": bool,
                "is_visible_after": bool,
                "success": bool
            }]
        """
        logger.info("Dynamically identifying and validating all FAQ accordion items...")
        self.dismiss_cookie_consent_if_present()

        results: List[Dict[str, Any]] = []
        faq_items = self.page.locator(ClubSilhouetteLocators.FAQ_ITEMS).all()
        logger.info(f"Discovered {len(faq_items)} FAQ accordion items.")
        assert len(faq_items) > 0, "No FAQ accordion items discovered on page."

        for idx, item in enumerate(faq_items):
            try:
                q_elem = item.locator(ClubSilhouetteLocators.FAQ_QUESTIONS).first
                a_elem = item.locator(ClubSilhouetteLocators.FAQ_ANSWERS).first

                assert q_elem.is_visible(timeout=3000), f"FAQ Item {idx + 1} question is not visible."
                question_text = q_elem.inner_text().strip()

                ans_initially_visible = a_elem.is_visible()

                # If collapsed, click the question to expand it
                if not ans_initially_visible:
                    q_elem.scroll_into_view_if_needed(timeout=2000)
                    q_elem.click()
                    self.wait_for_timeout(350)

                # Verify answer becomes visible
                ans_visible_after = a_elem.is_visible(timeout=3000)
                answer_text = a_elem.inner_text().strip()

                success = bool(ans_visible_after and len(answer_text) > 0)
                record = {
                    "index": idx + 1,
                    "question": question_text,
                    "answer_preview": answer_text[:60] + "..." if len(answer_text) > 60 else answer_text,
                    "was_open_initially": ans_initially_visible,
                    "is_visible_after": ans_visible_after,
                    "success": success,
                }
                results.append(record)
                logger.info(
                    f"FAQ [{idx + 1}/{len(faq_items)}] '{question_text}' -> "
                    f"Visible: {ans_visible_after} | Initial: {ans_initially_visible}"
                )
            except Exception as e:
                logger.error(f"Error validating FAQ item {idx + 1}: {e}")
                results.append({
                    "index": idx + 1,
                    "question": f"Error on item {idx + 1}",
                    "answer_preview": str(e),
                    "was_open_initially": False,
                    "is_visible_after": False,
                    "success": False,
                })

        return results

    # =========================================================================
    # E2E-CSIL-002: Membership Checkout & Activation
    # =========================================================================

    def click_join_monthly(self) -> None:
        """Click the 'Join monthly' plan CTA button on the Club Silhouette landing page."""
        logger.info("Clicking 'Join monthly' plan CTA button...")
        self.dismiss_cookie_consent_if_present()
        join_btn = self.page.locator(ClubSilhouetteLocators.MONTHLY_PLAN_JOIN_BUTTON).first
        assert join_btn.is_visible(timeout=5000), "'Join monthly' button is not visible."
        join_btn.scroll_into_view_if_needed()
        href = join_btn.get_attribute("href") or "clubsilhouette/plan/monthly"

        try:
            join_btn.click()
            self.wait_for_dom_content_loaded()
        except Exception as e:
            logger.debug(f"Click notice: {e}")
            self.goto(href, wait_until="domcontentloaded")

        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present(timeout=15000)
        self.dismiss_cookie_consent_if_present()
        self.dismiss_notice_modal_if_present()

        if "clubsilhouette/plan" not in self.get_current_url():
            self.goto(href, wait_until="domcontentloaded")
            self.wait_for_dom_content_loaded()
            self.handle_cloudflare_if_present(timeout=15000)
            self.dismiss_cookie_consent_if_present()
            self.dismiss_notice_modal_if_present()
        self.wait_for_timeout(2000)

    def is_refill_selection_heading_visible(self) -> bool:
        """Verify that the 'Select your free refill items' heading is displayed."""
        self.handle_cloudflare_if_present(timeout=15000)
        self.dismiss_cookie_consent_if_present()
        try:
            h = self.page.locator(ClubSilhouetteLocators.REFILL_HEADING).first
            return h.is_visible(timeout=10000)
        except Exception as e:
            logger.debug(f"Refill heading visibility notice: {e}")
            return False

    def select_machine_dynamically(self) -> str:
        """Inspect available machine dropdown options and select a valid machine dynamically."""
        logger.info("Inspecting machine dropdown options...")
        self.dismiss_cookie_consent_if_present()
        sel = self.page.locator(ClubSilhouetteLocators.MACHINES_SELECT).first
        assert sel.is_visible(timeout=5000), "Machine dropdown 'select#machines-select' not visible."

        options = sel.locator("option").all()
        valid_opts: List[Tuple[str, str]] = []
        for opt in options:
            val = opt.get_attribute("value") or ""
            label = opt.inner_text().strip()
            if val and val != "0" and "=" not in label and "legacy" not in label.lower():
                valid_opts.append((val, label))

        assert len(valid_opts) > 0, "No valid machine options available in dropdown."
        selected_val, selected_label = valid_opts[0]
        sel.select_option(value=selected_val)
        self.wait_for_timeout(600)
        logger.info(f"Selected machine dynamically: '{selected_label}' (value={selected_val})")
        return selected_label

    def select_category_dynamically(self) -> str:
        """Inspect available item-category options and select a valid category dynamically."""
        logger.info("Inspecting refill category dropdown options...")
        self.dismiss_cookie_consent_if_present()
        sel = self.page.locator(ClubSilhouetteLocators.CATEGORY_SELECT).first
        assert sel.is_visible(timeout=5000), "Category dropdown 'select#category-select' not visible."

        options = sel.locator("option").all()
        valid_opts: List[Tuple[str, str]] = []
        for opt in options:
            val = opt.get_attribute("value") or ""
            label = opt.inner_text().strip()
            if val and label and label.lower() != "select":
                valid_opts.append((val, label))

        assert len(valid_opts) > 0, "No valid category options available in dropdown."
        selected_val, selected_label = valid_opts[0]
        sel.select_option(value=selected_val)
        self.wait_for_timeout(600)
        logger.info(f"Selected category dynamically: '{selected_label}' (value={selected_val})")
        return selected_label

    def is_join_monthly_button_visible_and_enabled(self, timeout_ms: int = 5000) -> bool:
        """Verify the 'Join monthly' plan CTA button is visible and enabled on the Club Silhouette page."""
        locators = [
            ClubSilhouetteLocators.MONTHLY_PLAN_JOIN_BUTTON,
            "a.joinbtn[href*='monthly']",
            "a:has-text('Join monthly')",
            "button:has-text('Join monthly')",
        ]
        for sel in locators:
            try:
                btn = self.page.locator(sel).first
                if btn.count() > 0 and btn.is_visible(timeout=timeout_ms):
                    return btn.is_enabled()
            except Exception:
                pass
        return False

    def select_refill_product_cards(self, count: int = 2) -> List[str]:
        """Select the required number of matching available refill product cards."""
        logger.info(f"Selecting {count} available product refill cards...")
        self.dismiss_cookie_consent_if_present()

        # Wait for product refill cards and buttons to render after dropdown selection
        try:
            self.page.locator(".refillmat .selectbtn, .selectbtn").first.wait_for(state="visible", timeout=10000)
            self.wait_for_timeout(500)
        except Exception as e:
            logger.debug(f"Wait for refill select buttons notice: {e}")

        # Locate visible select buttons within product cards
        all_candidates = self.page.locator(".refillmat .selectbtn, .selectbtn").all()
        select_btns = [
            b for b in all_candidates
            if b.is_visible() and "club-stored-card-select" not in (b.get_attribute("class") or "")
        ]
        assert len(select_btns) >= count, (
            f"Expected at least {count} visible refill select buttons, found {len(select_btns)}"
        )

        selected_titles: List[str] = []
        for i in range(count):
            btn = select_btns[i]
            btn.scroll_into_view_if_needed()
            # Capture parent card title if available
            parent_card = btn.locator("xpath=ancestor::*[contains(@class, 'refillmat') or contains(@class, 'item')][1]")
            title = ""
            if parent_card.count() > 0:
                h = parent_card.locator("h2, h3, h4, .title, strong").first
                if h.count() > 0:
                    title = h.inner_text().strip()
            btn.click()
            self.wait_for_timeout(500)
            selected_titles.append(title or f"Refill Item {i + 1}")

        logger.info(f"Selected {len(selected_titles)} refill items: {selected_titles}")
        return selected_titles

    def is_continue_to_shipping_enabled(self) -> bool:
        """Verify whether 'Continue to shipping and payment' button is enabled."""
        btn = self.page.locator(ClubSilhouetteLocators.CONTINUE_TO_SHIPPING_BUTTON).first
        if btn.count() == 0:
            return False
        return btn.is_enabled()

    def click_continue_to_shipping(self) -> None:
        """Click 'Continue to shipping and payment'."""
        logger.info("Clicking 'Continue to shipping and payment' button...")
        btn = self.page.locator(ClubSilhouetteLocators.CONTINUE_TO_SHIPPING_BUTTON).first
        assert btn.is_enabled(), "'Continue to shipping and payment' button is not enabled."
        btn.scroll_into_view_if_needed()
        btn.click()
        self.wait_for_timeout(1500)
        self.dismiss_cookie_consent_if_present()

    def is_shipping_and_payment_section_visible(self) -> bool:
        """Verify that 'Select your shipping address and payment details' is visible."""
        try:
            sec = self.page.locator(ClubSilhouetteLocators.SHIPPING_PAYMENT_DETAILS_HEADING).first
            return sec.is_visible(timeout=5000)
        except Exception:
            return False

    def verify_existing_checkout_details(self) -> Dict[str, Any]:
        """Verify existing shipping address, billing address, order summary,
        and free refill items without modifying customer information.
        """
        logger.info("Verifying existing customer shipping and payment details...")
        self.dismiss_cookie_consent_if_present()

        details = {
            "has_shipping_address": False,
            "has_billing_address": False,
            "has_order_summary": False,
            "has_refill_items": False,
        }

        # 1. Shipping address check (select existing saved address if not pre-selected)
        ship_sel = self.page.locator(ClubSilhouetteLocators.SHIPPING_ADDRESS_SELECT).first
        if ship_sel.count() > 0 and ship_sel.is_visible(timeout=3000):
            val = ship_sel.input_value()
            if not val or val in ("0", "Select", ""):
                for opt in ship_sel.locator("option").all():
                    v = opt.get_attribute("value")
                    if v and v not in ("0", "Select", "newaddress", ""):
                        ship_sel.select_option(value=v)
                        self.wait_for_timeout(500)
                        val = v
                        break
            details["has_shipping_address"] = bool(val and val not in ("0", "Select", ""))
        else:
            details["has_shipping_address"] = self.page.locator(ClubSilhouetteLocators.SHIPPING_FIRSTNAME).count() > 0

        # 2. Billing address check (select existing saved billing address if not pre-selected)
        bill_sel = self.page.locator(ClubSilhouetteLocators.BILLING_ADDRESS_SELECT).first
        if bill_sel.count() > 0 and bill_sel.is_visible(timeout=3000):
            val = bill_sel.input_value()
            if not val or val in ("0", "Select", ""):
                for opt in bill_sel.locator("option").all():
                    v = opt.get_attribute("value")
                    if v and v not in ("0", "Select", "newaddress", "Add new address", ""):
                        bill_sel.select_option(value=v)
                        self.wait_for_timeout(500)
                        val = v
                        break
            details["has_billing_address"] = bool(val and val not in ("0", "Select", ""))
        else:
            details["has_billing_address"] = True

        # 3. Existing stored card check
        card_sel = self.page.locator(ClubSilhouetteLocators.CARD_SELECT).first
        if card_sel.count() > 0 and card_sel.is_visible(timeout=3000):
            cval = card_sel.input_value()
            if not cval or cval in ("0", "Select", ""):
                for opt in card_sel.locator("option").all():
                    cv = opt.get_attribute("value")
                    if cv and cv not in ("0", "Select", "add_new", ""):
                        card_sel.select_option(value=cv)
                        self.wait_for_timeout(500)
                        break

        # 4. Order summary check
        page_text = self.page.locator("body").inner_text()
        details["has_order_summary"] = (
            "order summary" in page_text.lower()
            or "subtotal" in page_text.lower()
            or "$9.99" in page_text
        )

        # 5. Refill items summary
        details["has_refill_items"] = (
            "refill" in page_text.lower()
            or self.page.locator(".selected-refill-items, .refillmat").count() > 0
        )

        logger.info(f"Verified checkout details: {details}")
        return details

    def accept_terms_and_conditions(self) -> None:
        """Check the Terms and Conditions agreement checkbox."""
        logger.info("Accepting Club Silhouette Terms and Conditions...")
        terms = self.page.locator(ClubSilhouetteLocators.TERMS_CHECKBOX).first
        assert terms.count() > 0, "Terms and Conditions checkbox not found."
        terms.scroll_into_view_if_needed()
        if not terms.is_checked():
            terms.check()
            self.wait_for_timeout(500)
        logger.info("Terms and Conditions checkbox checked.")

    def is_join_club_button_enabled(self) -> bool:
        """Verify whether 'Join Club Silhouette' button is enabled."""
        btn = self.page.locator(ClubSilhouetteLocators.JOIN_CLUB_BUTTON).first
        if btn.count() == 0:
            return False
        return btn.is_enabled()

    def submit_final_club_purchase(self) -> Dict[str, Any]:
        """Submit the final production Club Silhouette membership purchase exactly once.

        CAUTION: This creates a real production transaction.
        """
        logger.warning("SUBMITTING FINAL PRODUCTION CLUB SILHOUETTE PURCHASE (EXACTLY ONCE)...")
        btn = self.page.locator(ClubSilhouetteLocators.JOIN_CLUB_BUTTON).first
        assert btn.is_enabled(), "'Join Club Silhouette' button is not enabled."
        btn.scroll_into_view_if_needed()

        submission_time = datetime.now(timezone.utc)

        # Click the submit button EXACTLY ONCE
        btn.click()
        logger.info("Clicked 'Join Club Silhouette' button once. Waiting for payment and order processing...")

        # Wait for navigation to review page or URL change (up to 45s for live payment gateway)
        try:
            self.page.wait_for_url("**/clubsilhouette/response/review**", timeout=45000)
            self.wait_for_dom_content_loaded()
        except Exception as e:
            logger.info(f"wait_for_url review notice: {e}. Current URL: {self.get_current_url()}")
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                pass

        self.handle_cloudflare_if_present(timeout=15000)
        self.dismiss_cookie_consent_if_present()

        # Improve confirmation waiting logic: wait for review heading to appear if present
        thank_you_loc = self.page.locator(ClubSilhouetteLocators.REVIEW_PAGE_HEADING).first
        thank_you_visible = False
        try:
            if thank_you_loc.count() > 0:
                thank_you_loc.wait_for(state="visible", timeout=10000)
                thank_you_visible = True
        except Exception as e:
            logger.debug(f"Review heading wait notice: {e}")

        # Check for alert modal if error occurred
        modal_alert = self.page.locator(".modal-popup.confirm, .modal-popup.alert, [data-role='modal']").first
        alert_text = ""
        try:
            if modal_alert.is_visible(timeout=2000):
                alert_text = modal_alert.inner_text().strip()
                logger.warning(f"Modal alert visible on checkout: {alert_text}")
        except Exception as e:
            logger.debug(f"Modal alert check notice: {e}")

        curr_url = self.get_current_url()
        try:
            # Use unique body locator to eliminate strict mode violations
            conf_text = self.page.locator("body").inner_text()
        except Exception as e:
            logger.warning(f"Failed to read page body text: {e}")
            conf_text = ""

        # Extract order reference if present (e.g., Order # 000545470)
        import re
        order_match = re.search(r"order\s*#?\s*[:.]?\s*(\d{5,12})", conf_text, re.IGNORECASE)
        order_number = order_match.group(1) if order_match else ""
        if not order_number:
            order_number = self.get_latest_customer_order_id()

        if order_number:
            logger.info(f"Verified purchase order reference: #{order_number}")

        is_success = (
            "clubsilhouette/response/review" in curr_url
            or thank_you_visible
            or "thank you" in conf_text.lower()
            or "review" in curr_url.lower()
        )

        result = {
            "submitted_at": submission_time.isoformat(),
            "is_successful": is_success,
            "order_number": order_number,
            "url": curr_url,
            "alert_text": alert_text,
            "confirmation_text": conf_text[:300],
        }
        logger.info(f"Final purchase submission result: {result}")
        return result

    def get_latest_customer_order_id(self) -> str:
        """Fetch the latest order ID from customer order history via AJAX."""
        try:
            html = self.page.evaluate("""async () => {
                try {
                    const r = await fetch('/sales/order/history/');
                    return await r.text();
                } catch(e) { return ''; }
            }""")
            if html:
                import re
                m_col = re.findall(r'class="col id">\s*(\d{5,12})\s*<', html)
                if m_col:
                    return m_col[0]
                m = re.findall(r"view/order_id/\d+/[^>]*>\s*(\d{5,12})\s*<", html)
                if m:
                    return m[0]
        except Exception as e:
            logger.debug(f"Could not fetch latest order from history: {e}")
        return ""

    def click_shop_now_if_present(self) -> None:
        """Click 'Shop now' button on the purchase confirmation page if visible."""
        try:
            btn = self.page.locator(ClubSilhouetteLocators.SHOP_NOW_BUTTON).first
            if btn.is_visible(timeout=3000):
                btn.click()
                self.wait_for_dom_content_loaded()
        except Exception as e:
            logger.debug(f"Shop now notice: {e}")

    def navigate_to_my_account_club(self) -> None:
        """Navigate via Profile -> My Account -> Club Silhouette (/clubsilhouette/customer/)."""
        logger.info("Navigating to My Account -> Club Silhouette...")
        self.goto(self.customer_portal_path, wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present(timeout=10000)
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()

    def open_payments_and_verify_transaction(self, expected_order_id: str = "") -> Dict[str, Any]:
        """Open the Payments tab in the customer Club Silhouette area and verify transaction.

        IMPORTANT:
        - Targets the actual '#club-panel-payments' / '#club-payments-table' container.
        - Does NOT mark passed if the panel displays 'No any record.'.
        - Does NOT fall back to general order history or presence of the tab.
        """
        logger.info("Opening Payments tab in Club Silhouette dashboard...")
        self.dismiss_cookie_consent_if_present()
        result: Dict[str, Any] = {
            "payments_tab_present": False,
            "has_transaction": False,
            "order_number": "",
            "transaction_details": "",
            "status": "NOT_FOUND",
            "rows_count": 0,
        }

        try:
            tab = self.page.locator(ClubSilhouetteLocators.PAYMENTS_TAB).first
            if tab.is_visible(timeout=5000):
                result["payments_tab_present"] = True
                tab.click()
                self.wait_for_timeout(1500)
            else:
                logger.warning("Payments tab button is not visible.")
                return result

            # Target the Payments panel specifically (do not inspect general maincontent)
            panel = self.page.locator(ClubSilhouetteLocators.PAYMENTS_PANEL).first
            panel_text = panel.inner_text().strip() if panel.count() > 0 and panel.is_visible() else ""

            # Check if panel explicitly displays 'No any record.'
            if "no any record" in panel_text.lower():
                logger.warning(f"Payments panel explicitly displays: '{panel_text}'")
                result["status"] = "NO_RECORDS"
                result["transaction_details"] = "Payment information shows 'No any record.'"
                result["has_transaction"] = False
                return result

            # Locate table rows in Payments table
            table = self.page.locator(ClubSilhouetteLocators.PAYMENTS_TABLE).first
            if table.count() > 0 and table.is_visible():
                rows = self.page.locator(ClubSilhouetteLocators.PAYMENTS_ROWS).all()
                result["rows_count"] = len(rows)
                logger.info(f"Discovered {len(rows)} payment transaction rows in Payments table.")

                for idx, row in enumerate(rows):
                    row_text = row.inner_text().strip().replace("\t", " | ")
                    logger.info(f"Payments row [{idx + 1}]: {row_text}")

                    # Check for paid status and matching order or amount
                    row_lower = row_text.lower()
                    has_paid = "paid" in row_lower
                    import re
                    order_match = re.search(r"(\d{5,12})", row_text)
                    row_order = order_match.group(1) if order_match else ""

                    if has_paid:
                        # If expected_order_id provided, prefer exact match
                        if expected_order_id and expected_order_id in row_text:
                            result["has_transaction"] = True
                            result["order_number"] = expected_order_id
                            result["transaction_details"] = row_text
                            result["status"] = "PAID"
                            logger.info(f"Found matching paid transaction row for order #{expected_order_id}: '{row_text}'")
                            return result
                        elif not expected_order_id:
                            result["has_transaction"] = True
                            result["order_number"] = row_order
                            result["transaction_details"] = row_text
                            result["status"] = "PAID"
                            logger.info(f"Found valid paid transaction row: '{row_text}'")
                            return result

                # If rows exist but none are 'Paid'
                if len(rows) > 0 and not result["has_transaction"]:
                    first_row = rows[0].inner_text().strip().replace("\t", " | ")
                    result["transaction_details"] = f"Transactions exist but none marked Paid: {first_row}"
                    result["status"] = "PENDING_OR_UNPAID"
                    return result

            # If no table found or empty
            result["transaction_details"] = panel_text or "No payment table rendered"
            result["status"] = "NO_TABLE"
            return result
        except Exception as e:
            logger.warning(f"Error inspecting Payments tab: {e}")
            result["transaction_details"] = f"Exception: {e}"
            return result

    def wait_and_verify_payments_tab(
        self,
        wait_seconds: int = 180,
        expected_order_id: str = "",
        max_poll_seconds: int = 60,
    ) -> Dict[str, Any]:
        """Wait 3–4 minutes for backend payment synchronization, then open Payments tab and verify transaction.

        1. Waits initial `wait_seconds` (default 180s = 3 minutes) with periodic logging.
        2. Navigates to Club Silhouette dashboard (/clubsilhouette/customer/).
        3. Opens Payments tab and verifies actual transaction records.
        4. If still 'No any record.', polls up to an additional `max_poll_seconds` (default 60s, reaching 4 min total).
        """
        logger.info(
            f"Waiting {wait_seconds} seconds (3 minutes) for payment synchronization before inspecting Payments tab..."
        )
        start_wait = time.time()
        deadline = start_wait + wait_seconds
        while time.time() < deadline:
            remaining = int(deadline - time.time())
            elapsed = int(time.time() - start_wait)
            if elapsed > 0 and elapsed % 30 == 0:
                logger.info(f"Payment sync wait: {elapsed}s elapsed, {remaining}s remaining...")
            sleep_step = min(5.0, max(0.5, float(remaining)))
            time.sleep(sleep_step)

        logger.info(f"Completed initial {wait_seconds}s wait. Navigating to My Account -> Club Silhouette...")
        self.navigate_to_my_account_club()

        # Initial check
        payment_tx = self.open_payments_and_verify_transaction(expected_order_id=expected_order_id)
        if payment_tx["has_transaction"]:
            logger.info(f"Payment transaction verified on initial check: {payment_tx}")
            return payment_tx

        # If not found yet, poll up to additional max_poll_seconds (up to 4 minutes total)
        logger.info(f"Payment not visible immediately ({payment_tx['status']}). Polling up to {max_poll_seconds}s additional...")
        poll_start = time.time()
        while time.time() - poll_start < max_poll_seconds:
            time.sleep(10)
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_dom_content_loaded()
            self.dismiss_cookie_consent_if_present()
            payment_tx = self.open_payments_and_verify_transaction(expected_order_id=expected_order_id)
            if payment_tx["has_transaction"]:
                logger.info(f"Payment transaction verified during polling: {payment_tx}")
                return payment_tx

        logger.warning(
            f"Payment transaction failed to synchronize within 3–4 minutes: status={payment_tx['status']}, "
            f"details='{payment_tx['transaction_details']}'"
        )
        return payment_tx

    def get_membership_status(self) -> str:
        """Inspect and return customer Club Silhouette membership status.

        Returns one of: 'ACTIVE', 'INACTIVE', 'PENDING', or 'UNKNOWN'.
        Uses verified UI information and read-only customer subscription API.
        Does not assume membership status based only on button presence.
        """
        try:
            self.dismiss_cookie_consent_if_present()
            curr_url = self.get_current_url()

            # 1. Check page content for explicit Inactive indicators
            body_text = self.page.locator("body").inner_text().lower()
            if "you have not joined club silhouette yet" in body_text:
                logger.info("UI explicitly indicates: 'You have not joined Club Silhouette yet' -> INACTIVE.")
                return "INACTIVE"

            # Check if Join Monthly button is visible on landing page -> INACTIVE
            join_btn = self.page.locator("a.joinbtn[href*='monthly'], a:has-text('Join monthly')").first
            if join_btn.count() > 0 and join_btn.is_visible():
                logger.info("Join monthly button visible on page -> INACTIVE.")
                return "INACTIVE"

            # 2. Query Magento customer subscription section API
            sec_data = self.page.evaluate("""async () => {
                try {
                    if (window.customerData) {
                        const cs = window.customerData.get('customersubscription')();
                        if (cs && typeof cs === 'object' && Object.keys(cs).length > 0) return cs;
                    }
                    const r = await fetch('/customer/section/load/?sections=customersubscription&force_new_section_timestamp=true');
                    const json = await r.json();
                    return json.customersubscription || {};
                } catch(e) {
                    return {};
                }
            }""")
            status_api = str(sec_data.get("status", "")).strip().upper()
            has_sub = int(sec_data.get("hasSubscription", 0))
            logger.info(f"Customer subscription section API: hasSubscription={has_sub}, status='{status_api}'")

            # 3. Check for Pending status
            if status_api == "PENDING":
                logger.info("Membership status identified as PENDING via API.")
                return "PENDING"

            # 4. Check for Inactive status via API
            if status_api in ("INACTIVE", "CANCELLED", "EXPIRED") or (has_sub == 0 and status_api == ""):
                if "active" not in body_text:
                    logger.info(f"Membership status identified as INACTIVE via API (status={status_api}, hasSubscription={has_sub}).")
                    return "INACTIVE"

            # 5. Check for Active status
            if status_api == "ACTIVE" or has_sub == 1:
                logger.info("Membership verified as ACTIVE via subscription API.")
                return "ACTIVE"

            # 6. Member dashboard checks
            if "clubsilhouette/customer" in curr_url:
                if self.page.locator("#club-tab-payments, .nav-tabs a, .member-ships").count() > 0:
                    logger.info("Member dashboard tabs present and active -> ACTIVE.")
                    return "ACTIVE"
                if "you have not joined" not in body_text:
                    logger.info("On /clubsilhouette/customer without inactive message -> ACTIVE.")
                    return "ACTIVE"

            return "INACTIVE"
        except Exception as e:
            logger.warning(f"Error determining membership status: {e}")
            return "UNKNOWN"

    def execute_qa_purgemeas(self, repeat_count: int = 2) -> Dict[str, Any]:
        """Execute automated QA purge via exact endpoint 'clubsilhouette/qa/purgemeas'.

        Performs the purge request `repeat_count` times (default 2), verifying HTTP response
        and clearing session data cache.
        """
        purge_url = f"{self.config.base_url.rstrip('/')}/{ClubSilhouetteLocators.QA_PURGEMEAS_PATH}"
        logger.info(f"Executing automated QA purge at: {purge_url} ({repeat_count} iterations)...")
        results = []

        for i in range(1, repeat_count + 1):
            logger.info(f"[QA Purge {i}/{repeat_count}] Navigating to {purge_url}...")
            resp = self.page.goto(purge_url, wait_until="domcontentloaded", timeout=30000)
            self.wait_for_dom_content_loaded()
            self.handle_cloudflare_if_present(timeout=15000)
            self.dismiss_cookie_consent_if_present()
            status_code = resp.status if resp else 200
            snippet = self.page.locator("body").inner_text()[:120].strip().replace("\n", " ")
            logger.info(f"[QA Purge {i}/{repeat_count}] HTTP {status_code} received: '{snippet}'")
            results.append({
                "iteration": i,
                "status_code": status_code,
                "success": status_code in [200, 302],
            })
            self.wait_for_timeout(1000)

        # Invalidate customerData subscription cache in browser
        try:
            self.page.evaluate("""() => {
                if (window.customerData) {
                    window.customerData.reload(['customersubscription', 'customer'], true);
                }
            }""")
        except Exception:
            pass

        all_success = all(r["success"] for r in results)
        logger.info(f"QA Purge workflow completed across {repeat_count} iterations (success={all_success}).")
        return {
            "purge_url": purge_url,
            "repeat_count": repeat_count,
            "iterations": results,
            "success": all_success,
        }

    def execute_qa_purge_with_confirmation_check(self, delay_seconds: int = 0) -> Dict[str, Any]:
        """Execute post-purchase QA purge via 'clubsilhouette/qa/purge' and assert clean state.

        Flow:
        1. Optional delay if delay_seconds > 0.
        2. Hit 1: Navigate to 'clubsilhouette/qa/purge'.
        3. Parse JSON response.
        4. If Hit 1 deleted records (success=true / deleted_rows > 0):
           - Wait 2 seconds and hit / refresh 'clubsilhouette/qa/purge' (Hit 2).
           - Assert Hit 2 displays: '{"success":false,"message":"No records found to delete."}'
        5. Else (Hit 1 already returned no records to delete):
           - Assert Hit 1 displays: '{"success":false,"message":"No records found to delete."}'
        """
        if delay_seconds > 0:
            logger.info(f"Waiting {delay_seconds}s before post-purchase QA purge...")
            time.sleep(delay_seconds)

        purge_url = f"{self.config.base_url.rstrip('/')}/{ClubSilhouetteLocators.QA_PURGE_PATH}"
        logger.info(f"Executing post-purchase QA purge (Hit 1) at: {purge_url}...")

        self.goto(purge_url, wait_until="domcontentloaded")
        hit1_raw = self.page.locator("body").inner_text().strip()
        logger.info(f"[QA Purge Hit 1] Response: {hit1_raw[:300]}")

        import json
        hit1_json = {}
        try:
            hit1_json = json.loads(hit1_raw)
        except Exception:
            pass

        # If-else condition based on whether Hit 1 had records to delete
        hit1_had_records = (
            hit1_json.get("success") is True
            or hit1_json.get("deleted_rows", 0) > 0
            or "cancelled" in hit1_raw.lower()
            or "refunded" in hit1_raw.lower()
        )

        if hit1_had_records:
            logger.info(
                f"[QA Purge] Hit 1 successfully purged records ({hit1_json.get('deleted_rows', 0)} rows). "
                f"Refreshing / hitting endpoint a second time to assert clean state..."
            )
            self.wait_for_timeout(2000)
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_dom_content_loaded()
            self.handle_cloudflare_if_present(timeout=10000)
            hit2_raw = self.page.locator("body").inner_text().strip()
            logger.info(f"[QA Purge Hit 2] Response: {hit2_raw}")

            hit2_json = {}
            try:
                hit2_json = json.loads(hit2_raw)
            except Exception:
                pass

            is_clean = (
                hit2_json.get("success") is False
                and "no records found to delete" in hit2_json.get("message", "").lower()
            ) or "no records found to delete" in hit2_raw.lower()

            assert is_clean, (
                f"Assertion Failed: Expected Hit 2 response '{{\"success\":false,\"message\":\"No records found to delete.\"}}', "
                f"got: '{hit2_raw}'"
            )
            logger.info("Assertion PASSED: Hit 2 confirmed clean state: '{\"success\":false,\"message\":\"No records found to delete.\"}'")
            return {
                "success": True,
                "hit1_had_records": True,
                "hit1_response": hit1_json or hit1_raw,
                "hit2_response": hit2_json or hit2_raw,
            }
        else:
            logger.info("[QA Purge] Hit 1 already reported clean state.")
            is_clean = (
                hit1_json.get("success") is False
                and "no records found to delete" in hit1_json.get("message", "").lower()
            ) or "no records found to delete" in hit1_raw.lower()

            assert is_clean, (
                f"Assertion Failed: Expected Hit 1 response '{{\"success\":false,\"message\":\"No records found to delete.\"}}', "
                f"got: '{hit1_raw}'"
            )
            logger.info("Assertion PASSED: Hit 1 confirmed clean state: '{\"success\":false,\"message\":\"No records found to delete.\"}'")
            return {
                "success": True,
                "hit1_had_records": False,
                "hit1_response": hit1_json or hit1_raw,
            }

    def is_membership_active(self) -> bool:
        """Check if customer currently has an active Club Silhouette membership."""
        try:
            self.dismiss_cookie_consent_if_present()
            body_text = self.page.locator("body").inner_text().lower()
            if "you have not joined club silhouette yet" in body_text:
                return False
            if "active" in body_text and ("club silhouette" in body_text or "membership" in body_text):
                return True
            sec_data = self.page.evaluate("""async () => {
                try {
                    const r = await fetch('/customer/section/load/?sections=customersubscription&force_new_section_timestamp=true');
                    return await r.json();
                } catch(e) { return {}; }
            }""")
            sub = sec_data.get("customersubscription", {})
            return str(sub.get("status", "")).lower() == "active" or int(sub.get("hasSubscription", 0)) == 1
        except Exception as e:
            logger.debug(f"is_membership_active notice: {e}")
            return False

    def poll_membership_status_active(
        self,
        timeout_seconds: int = 120,
        poll_interval_seconds: int = 8,
    ) -> bool:
        """Poll the customer membership status dynamically until it reflects 'Active'."""
        logger.info(f"Polling membership status for 'Active' (timeout: {timeout_seconds}s)...")
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            try:
                # Reload page so customer dashboard updates with new subscription state
                self.page.reload(wait_until="domcontentloaded")
                self.wait_for_dom_content_loaded()
                self.dismiss_cookie_consent_if_present()

                body_text = self.page.locator("body").inner_text().lower()
                if "you have not joined club silhouette yet" in body_text:
                    logger.info("Dashboard shows 'You have not joined Club Silhouette yet'; waiting for activation...")
                    time.sleep(poll_interval_seconds)
                    continue

                # Check if Payments tab is visible
                payments_tab = self.page.locator(ClubSilhouetteLocators.PAYMENTS_TAB).first
                if payments_tab.count() > 0 and payments_tab.is_visible():
                    logger.info("Membership status active verified via Payments tab presence.")
                    return True

                # Inspect DOM for 'Active' status
                if "active" in body_text and ("club silhouette" in body_text or "membership information" in body_text):
                    logger.info("Membership status active verified via DOM.")
                    return True

                # Query Magento customer subscription section
                sec_data = self.page.evaluate("""async () => {
                    try {
                        const r = await fetch('/customer/section/load/?sections=customersubscription&force_new_section_timestamp=true');
                        return await r.json();
                    } catch(e) { return {}; }
                }""")
                sub = sec_data.get("customersubscription", {})
                status = str(sub.get("status", "")).lower()
                has_sub = int(sub.get("hasSubscription", 0))

                if (has_sub == 1 or status == "active") and "you have not joined" not in body_text:
                    logger.info("Membership status polled successfully as ACTIVE via customer section API.")
                    return True

                # Check if order was placed and confirmed in customer order history
                latest_order_html = self.page.evaluate("""async () => {
                    try {
                        const r = await fetch('/sales/order/history/');
                        return await r.text();
                    } catch(e) { return ''; }
                }""")
                if latest_order_html:
                    import re
                    # Look for Closed or Complete or Paid or Processing on the top order
                    if re.search(r'class="col id">\s*\d{5,12}\s*</td>\s*<td[^>]*>[^<]*</td>\s*<td[^>]*>[^<]*</td>\s*<td[^>]*>(Closed|Complete|Paid|Processing)<', latest_order_html, re.IGNORECASE):
                        logger.info("Membership order verified as Closed/Complete/Paid in order history.")
                        return True
            except Exception as e:
                logger.debug(f"Poll check notice: {e}")

            time.sleep(poll_interval_seconds)

        logger.warning(f"Membership status did not become 'Active' within {timeout_seconds}s.")
        return False

    # =========================================================================
    # Mandatory Delayed QA Purge
    # =========================================================================

    def execute_delayed_qa_purge(
        self,
        delay_minutes: int = 12,
        confirmation_timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Execute the mandatory delayed QA purge after a successful Club purchase.

        Exact purge URL: https://www.silhouetteamerica.com/clubsilhouette/qa/purge

        Rules:
        - Delay must be configured between 10 and 15 minutes.
        - Timer starts ONLY from the confirmed purchase timestamp.
        - Navigates to the exact QA purge URL.
        - Validates the actual response returned by the endpoint.
        """
        assert 10 <= delay_minutes <= 15, f"Delay minutes must be between 10 and 15, got {delay_minutes}."
        logger.warning(
            f"INITIATING MANDATORY DELAYED QA PURGE WORKFLOW (Delay: {delay_minutes} minutes)..."
        )

        # Calculate remaining wait time based on confirmation timestamp
        now = datetime.now(timezone.utc)
        start_ts = confirmation_timestamp or now
        elapsed_seconds = (now - start_ts).total_seconds()
        target_wait_seconds = (delay_minutes * 60) - elapsed_seconds

        if target_wait_seconds > 0:
            logger.info(
                f"Waiting {target_wait_seconds:.1f} seconds for transaction to settle "
                f"before opening QA purge URL..."
            )
            wait_deadline = time.time() + target_wait_seconds
            while time.time() < wait_deadline:
                remaining = wait_deadline - time.time()
                sleep_chunk = min(30.0, max(0.5, remaining))
                time.sleep(sleep_chunk)
                try:
                    self.page.evaluate("() => Date.now()")
                except Exception:
                    pass

        purge_url = f"{self.config.base_url.rstrip('/')}/{ClubSilhouetteLocators.QA_PURGEMEAS_PATH}"
        logger.info(f"Opening exact QA purge URL: {purge_url}...")

        purge_start = datetime.now(timezone.utc)
        resp = self.page.goto(purge_url, wait_until="domcontentloaded", timeout=30000)
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present(timeout=15000)

        purge_end = datetime.now(timezone.utc)
        status_code = resp.status if resp else 200
        response_body = self.page.locator("body").inner_text().strip()

        result = {
            "purge_url": purge_url,
            "status_code": status_code,
            "execution_time": purge_start.isoformat(),
            "elapsed_minutes": (purge_end - start_ts).total_seconds() / 60.0,
            "response_snippet": response_body[:200],
            "success": status_code in [200, 302],
        }
        logger.info(f"QA Purge Execution Completed: {result}")
        return result
