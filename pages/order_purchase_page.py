import re
from typing import Any, Dict, List, Optional
from playwright.sync_api import Locator, Page
from config.config import Config
from locators.order_purchase_locators import OrderPurchaseLocators
from pages.base_page import BasePage
from utils.logger import logger


class OrderPurchasePage(BasePage):
    """Page Object for Silhouette America Software Purchase, Checkout, and My Orders flows."""

    def __init__(self, page: Page, config: Optional[Config] = None) -> None:
        super().__init__(page, config)

    # =========================================================================
    # Navigation & Software PDP
    # =========================================================================

    def open_homepage(self) -> None:
        """Open the production homepage, handle cloudflare and dismiss cookie consent."""
        logger.info("Opening homepage for Order Purchase flow...")
        self.goto("", wait_until="domcontentloaded")
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()

    def clear_cart_if_needed(self) -> None:
        """Clear existing items from the cart to ensure a clean state for software purchase."""
        try:
            logger.info("Checking if cart contains existing items...")
            self.goto("checkout/cart", wait_until="domcontentloaded")
            self.wait_for_dom_content_loaded()
            self.handle_cloudflare_if_present()
            self.dismiss_cookie_consent_if_present()

            delete_btns = self.page.locator(".action.action-delete, a.btn-remove, [title='Remove item']").all()
            if delete_btns:
                logger.info(f"Clearing {len(delete_btns)} stale item(s) from cart...")
                for btn in delete_btns:
                    try:
                        if btn.is_visible():
                            btn.click()
                            self.wait_for_timeout(2000)
                    except Exception:
                        pass
                logger.info("Cart cleared.")
            else:
                logger.info("Cart is already empty or has no remove controls.")
        except Exception as e:
            logger.debug(f"Cart clear notice: {e}")

    def navigate_to_software_section(self) -> str:
        """Navigate to the main software landing section (/software)."""
        logger.info("Navigating to software section: /software")
        self.goto("software", wait_until="domcontentloaded")
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()
        return self.get_current_url()

    def open_software_product(self, product_slug: str = "silhouette-connect") -> str:
        """Navigate to an available software product page (e.g., Silhouette Connect)."""
        slug = product_slug.lstrip("/")
        logger.info(f"Opening software product page: '{slug}'")
        self.goto(slug, wait_until="domcontentloaded")
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()

        # Wait for product title or purchase button
        try:
            self.page.wait_for_selector(
                OrderPurchaseLocators.PDP_PURCHASE_BUTTON,
                state="visible",
                timeout=15000,
            )
        except Exception as e:
            logger.debug(f"Wait for PDP purchase button: {e}")

        curr_url = self.get_current_url()
        logger.info(f"Software product page loaded at: '{curr_url}'")
        return curr_url

    def verify_pdp(self) -> Dict[str, Any]:
        """Verify the Product Details Page has loaded with title, price, and purchase button."""
        title_elem = self.page.locator(OrderPurchaseLocators.PDP_TITLE).first
        title_text = title_elem.inner_text().strip() if title_elem.is_visible(timeout=5000) else self.get_title()

        price_elem = self.page.locator(OrderPurchaseLocators.PDP_PRICE).first
        price_text = price_elem.inner_text().strip() if price_elem.is_visible(timeout=5000) else ""

        purchase_btn = self.page.locator(OrderPurchaseLocators.PDP_PURCHASE_BUTTON).first
        purchase_btn_visible = purchase_btn.is_visible(timeout=5000)
        purchase_btn_text = purchase_btn.inner_text().strip() if purchase_btn_visible else ""

        logger.info(
            f"PDP verification: title='{title_text}', price='{price_text}', "
            f"purchase_button_visible={purchase_btn_visible} ('{purchase_btn_text}')"
        )
        return {
            "title": title_text,
            "price": price_text,
            "purchase_button_visible": purchase_btn_visible,
            "purchase_button_text": purchase_btn_text,
            "url": self.get_current_url(),
        }

    def click_purchase_on_pdp(self) -> None:
        """Click the Purchase button on the PDP and wait for cart addition."""
        self.dismiss_cookie_consent_if_present()
        purchase_btn = self.page.locator(OrderPurchaseLocators.PDP_PURCHASE_BUTTON).first
        assert purchase_btn.is_visible(timeout=5000), "Purchase button is not visible on PDP"

        logger.info(f"Clicking '{purchase_btn.inner_text().strip()}' button on PDP...")
        purchase_btn.click()

        # Wait for cart notification or counter update
        try:
            self.page.wait_for_selector(
                OrderPurchaseLocators.PDP_SUCCESS_MESSAGE,
                state="visible",
                timeout=8000,
            )
            success_msg = self.page.locator(OrderPurchaseLocators.PDP_SUCCESS_MESSAGE).first.inner_text().strip()
            logger.info(f"PDP addition message: '{success_msg}'")
        except Exception:
            logger.debug("Cart success banner not explicitly displayed or disappeared quickly.")

        self.wait_for_timeout(2000)

    # =========================================================================
    # Mini Cart
    # =========================================================================

    def open_minicart_and_verify(self) -> Dict[str, Any]:
        """Open the header mini cart and verify product name, price, quantity, and subtotal."""
        logger.info("Opening mini cart from header...")
        cart_trigger = self.page.locator(OrderPurchaseLocators.HEADER_CART_LINK).first
        assert cart_trigger.is_visible(timeout=5000), "Header mini cart trigger not visible"
        cart_trigger.click()
        self.wait_for_timeout(1500)

        # Wait for mini cart dropdown/panel
        minicart_wrapper = self.page.locator(OrderPurchaseLocators.MINICART_WRAPPER).first
        minicart_visible = minicart_wrapper.is_visible(timeout=5000)

        item_name_elem = self.page.locator(OrderPurchaseLocators.MINICART_ITEM_NAME).first
        item_name = item_name_elem.inner_text().strip() if item_name_elem.is_visible(timeout=3000) else ""

        item_price_elem = self.page.locator(OrderPurchaseLocators.MINICART_ITEM_PRICE).first
        item_price = item_price_elem.inner_text().strip() if item_price_elem.is_visible(timeout=3000) else ""

        item_qty_elem = self.page.locator(OrderPurchaseLocators.MINICART_ITEM_QTY).first
        item_qty = ""
        if item_qty_elem.is_visible(timeout=2000):
            item_qty = item_qty_elem.input_value() or item_qty_elem.get_attribute("data-item-qty") or "1"
        else:
            item_qty = "1"

        subtotal_elem = self.page.locator(OrderPurchaseLocators.MINICART_SUBTOTAL).first
        subtotal = subtotal_elem.inner_text().strip() if subtotal_elem.is_visible(timeout=3000) else item_price

        checkout_btn = self.page.locator(OrderPurchaseLocators.MINICART_CHECKOUT_BUTTON).first
        checkout_btn_visible = checkout_btn.is_visible(timeout=3000)

        logger.info(
            f"Mini cart details: product_name='{item_name}', price='{item_price}', "
            f"qty='{item_qty}', subtotal='{subtotal}', checkout_button_visible={checkout_btn_visible}"
        )

        return {
            "minicart_visible": minicart_visible,
            "product_name": item_name,
            "price": item_price,
            "qty": item_qty,
            "subtotal": subtotal,
            "checkout_button_visible": checkout_btn_visible,
        }

    def proceed_to_checkout_from_minicart(self) -> str:
        """Click the Checkout button in the mini cart to navigate to the Checkout page."""
        logger.info("Proceeding to checkout from mini cart...")
        checkout_btn = self.page.locator(OrderPurchaseLocators.MINICART_CHECKOUT_BUTTON).first
        assert checkout_btn.is_visible(timeout=5000), "Checkout button in mini cart not visible"

        checkout_btn.click()
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()

        # Wait for checkout URL
        try:
            self.page.wait_for_url("**/checkout/**", timeout=15000)
        except Exception:
            pass

        self.wait_for_timeout(3000)
        curr_url = self.get_current_url()
        logger.info(f"Navigated to checkout URL: '{curr_url}'")
        return curr_url

    # =========================================================================
    # Checkout Page & Customer Details
    # =========================================================================

    def verify_checkout_page_loaded(self) -> bool:
        """Verify the Checkout page is loaded and displays checkout sections."""
        curr_url = self.get_current_url()
        is_checkout_url = "checkout" in curr_url.lower()

        # Check for checkout container or progress bar or review & payments
        body_text = self.page.locator("body").inner_text().lower()
        has_checkout_content = (
            "review & payments" in body_text
            or "order summary" in body_text
            or "billing address" in body_text
            or "shipping" in body_text
        )

        is_loaded = is_checkout_url and has_checkout_content
        logger.info(f"Checkout page load verification: is_loaded={is_loaded}, url='{curr_url}'")
        return is_loaded

    def get_checkout_customer_email(self) -> str:
        """Retrieve the customer email dynamically from the checkout page."""
        # 1. Try JS checkoutConfig or mage-cache-storage
        try:
            js_email = self.page.evaluate(
                """() => {
                    if (window.checkoutConfig && window.checkoutConfig.customerData && window.checkoutConfig.customerData.email) {
                        return window.checkoutConfig.customerData.email;
                    }
                    try {
                        const mcs = JSON.parse(window.localStorage.getItem('mage-cache-storage') || '{}');
                        if (mcs.customer && mcs.customer.email) return mcs.customer.email;
                    } catch(e) {}
                    return '';
                }"""
            )
            if js_email and "@" in js_email:
                logger.info(f"Captured checkout customer email via JS evaluation: '{js_email}'")
                return js_email.strip()
        except Exception as e:
            logger.debug(f"JS checkout email evaluation notice: {e}")

        # 2. Try input / text locators
        for sel in [
            OrderPurchaseLocators.LOGGED_IN_EMAIL_TEXT,
            "#customer-email",
            "input[name='username']",
            ".customer-email",
            "[data-cy='logged-in-email']",
            ".checkout-container",
        ]:
            try:
                el = self.page.locator(sel).first
                if el.is_visible(timeout=1000):
                    val = el.input_value() if el.evaluate("e => e.tagName") == "INPUT" else el.inner_text().strip()
                    if val and "@" in val:
                        logger.info(f"Captured checkout customer email via locator '{sel}': '{val}'")
                        return val
            except Exception:
                pass

        # 3. Fallback to regex across full page HTML/text
        try:
            content = self.page.content()
            email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", content)
            if email_match:
                email_val = email_match.group(0)
                logger.info(f"Captured email via content inspection: '{email_val}'")
                return email_val
        except Exception:
            pass

        return ""

    def fill_customer_details(self, first_name: str = "AI", last_name: str = "Automation", phone: str = "898989999") -> None:
        """Fill First Name, Last Name, and Phone into the billing/customer form if editable."""
        logger.info(f"Entering customer details: first_name='{first_name}', last_name='{last_name}', phone='{phone}'")
        fn = self.page.locator(OrderPurchaseLocators.BILLING_FIRST_NAME).first
        if fn.is_visible(timeout=3000):
            fn.fill(first_name)
            logger.info(f"Filled First Name: '{first_name}'")

        ln = self.page.locator(OrderPurchaseLocators.BILLING_LAST_NAME).first
        if ln.is_visible(timeout=3000):
            ln.fill(last_name)
            logger.info(f"Filled Last Name: '{last_name}'")

        phone_inp = self.page.locator(OrderPurchaseLocators.BILLING_PHONE).first
        if phone_inp.is_visible(timeout=2000):
            phone_inp.fill(phone)
            logger.info(f"Filled Phone: '{phone}'")

    def use_address_finder(self, zip_code: str = "51570") -> Dict[str, Any]:
        """Use Address Finder to search for ZIP code 51570, inspect suggestions, select valid address,
        and click 'Use this address' and 'Continue to Billing' if present.
        """
        logger.info(f"Using Address Finder for postcode/ZIP: '{zip_code}'")
        af_input = self.page.locator(OrderPurchaseLocators.ADDRESS_FINDER_INPUT).first
        suggestions_found: List[str] = []
        selected_address = ""

        # Only interact with address finder if it is visible on the current step
        if af_input.is_visible(timeout=2000):
            af_input.click()
            af_input.fill("")
            af_input.type(zip_code, delay=120)
            self.wait_for_timeout(2500)

            # Inspect returned suggestions
            sugg_locator = self.page.locator(OrderPurchaseLocators.ADDRESS_FINDER_SUGGESTIONS)
            sugg_count = sugg_locator.count()
            logger.info(f"Address Finder returned {sugg_count} suggestion elements.")

            for i in range(min(sugg_count, 10)):
                try:
                    s_text = sugg_locator.nth(i).inner_text().strip().replace("\n", ", ")
                    if s_text and s_text not in suggestions_found:
                        suggestions_found.append(s_text)
                except Exception:
                    pass

            logger.info(f"Address suggestions: {suggestions_found}")

            # Select a valid returned test address (prefer USA or first matching item)
            target_sugg = self.page.locator("button.shipperhq-autocomplete__action:has-text('USA')").first
            if not target_sugg.is_visible():
                target_sugg = sugg_locator.first

            if target_sugg.is_visible(timeout=3000):
                selected_address = target_sugg.inner_text().strip().replace("\n", ", ")
                logger.info(f"Selecting address suggestion: '{selected_address}'")
                target_sugg.click()
                self.wait_for_timeout(1500)

            # Click 'Use this address' if visible
            use_btn = self.page.locator(OrderPurchaseLocators.USE_THIS_ADDRESS_BUTTON).first
            if use_btn.is_visible(timeout=3000):
                logger.info(f"Clicking '{use_btn.inner_text().strip()}' button...")
                use_btn.click()
                self.wait_for_timeout(2000)

        # Check for 'Continue to Billing' or 'Continue' button only if shipping step is active
        curr_url = self.get_current_url()
        has_payment_on_screen = self.page.locator(OrderPurchaseLocators.FREE_PAYMENT_RADIO_LABEL).is_visible(timeout=1000)
        if "payment" not in curr_url and not has_payment_on_screen:
            try:
                self.page.wait_for_selector(".loading-mask", state="hidden", timeout=5000)
            except Exception:
                pass
            cont_btn = self.page.locator(OrderPurchaseLocators.CONTINUE_TO_BILLING_BUTTON).first
            if cont_btn.is_visible(timeout=2000):
                logger.info(f"Clicking '{cont_btn.inner_text().strip()}' button...")
                try:
                    cont_btn.click(timeout=3000, force=True)
                except Exception:
                    cont_btn.evaluate("el => el.click()")
                self.wait_for_timeout(3000)

        return {
            "zip_code": zip_code,
            "suggestions": suggestions_found,
            "selected_address": selected_address,
        }

    # =========================================================================
    # Coupon & Order Summary
    # =========================================================================

    def apply_coupon(self, coupon_code: str = "Gajanan100") -> Dict[str, Any]:
        """Apply coupon code Gajanan100 and verify the actual coupon response and discount."""
        logger.info(f"Checking coupon status for: '{coupon_code}'")

        cancel_btn = self.page.locator(OrderPurchaseLocators.CANCEL_COUPON_BUTTON).first
        coupon_inp = self.page.locator(OrderPurchaseLocators.COUPON_INPUT).first

        # Check if already applied (Cancel Coupon is visible or input is disabled)
        if cancel_btn.is_visible(timeout=2000) or (coupon_inp.count() > 0 and coupon_inp.is_disabled()):
            logger.info(f"Coupon '{coupon_code}' is already applied (input disabled or cancel button visible).")
            return {
                "coupon_code": coupon_code,
                "is_applied": True,
                "response_message": f'Code "{coupon_code}" is active',
            }

        # Open coupon trigger if collapsed
        trigger = self.page.locator(OrderPurchaseLocators.COUPON_TRIGGER).first
        if trigger.is_visible(timeout=3000):
            trigger.click()
            self.wait_for_timeout(1000)

        # Check again after expanding trigger
        if cancel_btn.is_visible(timeout=1000) or (coupon_inp.count() > 0 and coupon_inp.is_disabled()):
            logger.info(f"Coupon '{coupon_code}' is already applied (input disabled or cancel button visible).")
            return {
                "coupon_code": coupon_code,
                "is_applied": True,
                "response_message": f'Code "{coupon_code}" is active',
            }

        assert coupon_inp.is_visible(timeout=5000), "Coupon input field not visible"

        logger.info(f"Entering coupon code: '{coupon_code}'")
        coupon_inp.fill(coupon_code)

        apply_btn = self.page.locator(OrderPurchaseLocators.APPLY_COUPON_BUTTON).first
        assert apply_btn.is_visible(timeout=3000), "Apply Coupon button not visible"
        logger.info("Clicking 'Apply Coupon'...")
        apply_btn.click()
        self.wait_for_timeout(5000)

        # Check response message
        success_elem = self.page.locator(OrderPurchaseLocators.COUPON_SUCCESS_MESSAGE).first
        error_elem = self.page.locator(OrderPurchaseLocators.COUPON_ERROR_MESSAGE).first

        response_message = ""
        is_applied = False

        if success_elem.is_visible(timeout=4000):
            response_message = success_elem.inner_text().strip()
            is_applied = True
            logger.info(f"Coupon application successful: '{response_message}'")
        elif error_elem.is_visible(timeout=2000):
            response_message = error_elem.inner_text().strip()
            is_applied = False
            logger.warning(f"Coupon application rejected: '{response_message}'")
        elif cancel_btn.is_visible(timeout=2000):
            is_applied = True
            response_message = f'Code "{coupon_code}" applied'
            logger.info("Coupon verified applied via active Cancel Coupon state.")

        return {
            "coupon_code": coupon_code,
            "is_applied": is_applied,
            "response_message": response_message,
        }

    def get_order_summary_totals(self) -> Dict[str, Any]:
        """Extract order summary details: product name, subtotal, discount, and grand total."""
        self.wait_for_timeout(1000)
        p_name = self.page.locator(OrderPurchaseLocators.SUMMARY_PRODUCT_NAME).first
        product_name = p_name.inner_text().strip() if p_name.is_visible(timeout=3000) else ""

        sub_elem = self.page.locator(OrderPurchaseLocators.SUMMARY_SUBTOTAL).first
        subtotal = sub_elem.inner_text().strip() if sub_elem.is_visible(timeout=3000) else ""

        disc_elem = self.page.locator(OrderPurchaseLocators.SUMMARY_DISCOUNT).first
        discount = disc_elem.inner_text().strip() if disc_elem.is_visible(timeout=3000) else ""

        total_elem = self.page.locator(OrderPurchaseLocators.SUMMARY_GRAND_TOTAL).first
        grand_total = total_elem.inner_text().strip() if total_elem.is_visible(timeout=3000) else ""

        # Fallback to body parsing if specific locators not hydrated
        if not grand_total or not subtotal:
            body_text = self.page.locator("body").inner_text()
            for line in body_text.split("\n"):
                line = line.strip()
                if "sub total" in line.lower() or "subtotal" in line.lower():
                    if not subtotal:
                        subtotal = line
                elif "discount" in line.lower():
                    if not discount:
                        discount = line
                elif "order total" in line.lower():
                    if not grand_total:
                        grand_total = line

        logger.info(
            f"Order Summary totals: product_name='{product_name}', subtotal='{subtotal}', "
            f"discount='{discount}', grand_total='{grand_total}'"
        )
        return {
            "product_name": product_name,
            "subtotal": subtotal,
            "discount": discount,
            "grand_total": grand_total,
        }

    # =========================================================================
    # Payment Safety & Order Submission
    # =========================================================================

    def verify_safe_payment_condition(self) -> Dict[str, Any]:
        """Verify that the payable amount is 0.00 and select 'No Payment Information Required'."""
        totals = self.get_order_summary_totals()
        grand_total_str = totals["grand_total"]

        # Parse numeric amount
        matches = re.findall(r"\d+\.\d{2}", grand_total_str)
        numeric_total = float(matches[0]) if matches else 999.0

        is_zero_dollar = (numeric_total == 0.0) or ("$0.00" in grand_total_str) or ("0.00" in grand_total_str)
        logger.info(f"Payment safety check: grand_total='{grand_total_str}', is_zero_dollar={is_zero_dollar}")

        # Select 'No Payment Information Required' radio
        radio_label = self.page.locator(OrderPurchaseLocators.FREE_PAYMENT_RADIO_LABEL).first
        radio_visible = radio_label.is_visible(timeout=4000)
        if radio_visible:
            logger.info("Selecting 'No Payment Information Required' radio option...")
            radio_label.scroll_into_view_if_needed()
            try:
                radio_label.click(timeout=3000)
            except Exception:
                radio_label.evaluate("el => el.click()")
            self.wait_for_timeout(1500)

        pay_now_btn = self.page.locator(OrderPurchaseLocators.PAY_NOW_BUTTON).first
        pay_now_visible = pay_now_btn.is_visible(timeout=3000)
        if not pay_now_visible:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.wait_for_timeout(1000)
            pay_now_visible = pay_now_btn.is_visible(timeout=3000)

        is_safe = is_zero_dollar and radio_visible and pay_now_visible
        logger.info(f"Safe zero-dollar payment verification: is_safe={is_safe}, pay_now_visible={pay_now_visible}")

        return {
            "is_zero_dollar": is_zero_dollar,
            "numeric_total": numeric_total,
            "radio_visible": radio_visible,
            "pay_now_visible": pay_now_visible,
            "is_safe": is_safe,
        }

    def submit_order_and_capture_confirmation(self) -> Dict[str, Any]:
        """Submit the zero-dollar safe order, handle the review popup, and capture the order number."""
        pay_now_btn = self.page.locator(OrderPurchaseLocators.PAY_NOW_BUTTON).first
        assert pay_now_btn.is_visible(timeout=5000), "Pay Now button is not visible"

        btn_text = pay_now_btn.inner_text().strip()
        logger.info(f"Submitting order via button: '{btn_text}'...")
        pay_now_btn.click()

        # Wait for navigation to success page
        logger.info("Waiting for order confirmation page...")
        try:
            self.page.wait_for_url("**/checkout/onepage/success**", timeout=20000)
        except Exception:
            pass

        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(4000)

        curr_url = self.get_current_url()
        page_title = self.get_title()
        logger.info(f"Confirmation loaded: URL='{curr_url}', Title='{page_title}'")

        # Handle 'Please Write a Review' popup if it appears
        self.close_review_popup_if_present()

        # Capture order number dynamically
        order_number = self.extract_order_number()
        logger.info(f"Dynamically captured order number: '{order_number}'")

        return {
            "order_number": order_number,
            "confirmation_url": curr_url,
            "page_title": page_title,
        }

    def close_review_popup_if_present(self, timeout: int = 4000) -> bool:
        """Close the 'Please Write a Review' modal popup if visible."""
        try:
            review_close = self.page.locator(OrderPurchaseLocators.REVIEW_POPUP_CLOSE).first
            if review_close.is_visible(timeout=timeout):
                logger.info("Detected 'Please Write a Review' popup. Closing it...")
                review_close.click()
                self.wait_for_timeout(1000)
                logger.info("Review popup successfully closed.")
                return True
        except Exception as e:
            logger.debug(f"Review popup check: {e}")
        return False

    def extract_order_number(self) -> str:
        """Extract the numeric order number from confirmation page links, paragraphs, or title."""
        # 1. From order number link (a.order-number)
        link = self.page.locator(OrderPurchaseLocators.CONFIRMATION_ORDER_NUMBER_LINK).first
        if link.is_visible(timeout=3000):
            num = link.inner_text().strip()
            if num:
                return num

        # 2. From page title ("Order # 000545060")
        title = self.get_title()
        match = re.search(r"(\d{6,12})", title)
        if match:
            return match.group(1)

        # 3. From page text ("Your order number is: 000545060")
        body_text = self.page.locator("body").inner_text()
        match = re.search(r"order\s+(?:number\s+is:\s*|#\s*)(\d{6,12})", body_text, re.IGNORECASE)
        if match:
            return match.group(1)

        return ""

    # =========================================================================
    # My Orders & Order Details
    # =========================================================================

    def navigate_to_my_orders(self) -> str:
        """Navigate to My Account -> My Orders (/sales/order/history/)."""
        logger.info("Navigating to My Orders: /sales/order/history/")
        self.goto("sales/order/history/", wait_until="domcontentloaded")
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()
        self.wait_for_timeout(3000)
        curr_url = self.get_current_url()
        logger.info(f"My Orders page loaded at: '{curr_url}'")
        return curr_url

    def find_order_in_history(self, order_number: str) -> Dict[str, Any]:
        """Locate the row in My Orders corresponding to order_number and extract its metadata."""
        logger.info(f"Locating order '{order_number}' in order history table...")
        self.page.wait_for_selector(OrderPurchaseLocators.MY_ORDERS_TABLE, state="visible", timeout=15000)

        rows = self.page.locator(OrderPurchaseLocators.MY_ORDERS_ROWS).all()
        matched_row: Optional[Locator] = None
        order_meta: Dict[str, Any] = {
            "found": False,
            "order_number": order_number,
            "date": "",
            "total": "",
            "status": "",
        }

        for r in rows:
            try:
                row_text = r.inner_text().strip()
                if order_number in row_text:
                    matched_row = r
                    order_meta["found"] = True

                    cols = r.locator("td").all()
                    if len(cols) >= 4:
                        order_meta["date"] = cols[1].inner_text().strip()
                        order_meta["total"] = cols[2].inner_text().strip()
                        order_meta["status"] = cols[3].inner_text().strip()

                    logger.info(f"Order '{order_number}' located in My Orders: {order_meta}")
                    break
            except Exception:
                pass

        return order_meta

    def view_order_details(self, order_number: str) -> Dict[str, Any]:
        """Open the details for the specified order and verify order number, products, totals, and status."""
        logger.info(f"Opening order details for order: '{order_number}'")
        # Find row and click View Order
        rows = self.page.locator(OrderPurchaseLocators.MY_ORDERS_ROWS).all()
        view_clicked = False
        for r in rows:
            if order_number in r.inner_text():
                view_link = r.locator("a:has-text('View Order'), a[href*='order_id']").first
                if view_link.is_visible(timeout=3000):
                    view_link.click()
                    view_clicked = True
                    break

        if not view_clicked:
            # Direct link fallback
            logger.info("Attempting direct link search for view order...")
            direct_link = self.page.locator(f"a[href*='order_id']:has-text('{order_number}')").first
            if direct_link.is_visible(timeout=3000):
                direct_link.click()

        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(3000)

        curr_url = self.get_current_url()
        title = self.get_title()
        logger.info(f"Order details loaded: URL='{curr_url}', Title='{title}'")

        # Extract status dynamically
        status = ""
        for loc_str in [
            OrderPurchaseLocators.ORDER_DETAILS_STATUS,
            ".order-status",
            "[class*='status']",
            "span:has-text('Complete')",
            "span:has-text('Processing')",
            "span:has-text('Pending')",
        ]:
            try:
                elem = self.page.locator(loc_str).first
                if elem.is_visible(timeout=500):
                    txt = elem.inner_text().strip()
                    if txt and len(txt) < 30 and any(s in txt.lower() for s in ["complete", "processing", "pending", "closed", "canceled"]):
                        status = txt
                        break
            except Exception:
                pass

        if not status:
            try:
                body_text = self.page.locator("body").inner_text()
                match = re.search(r"Status\s*[:\n\r\t]+\s*([A-Za-z]+)", body_text, re.IGNORECASE)
                if match:
                    status = match.group(1).strip()
            except Exception:
                pass

        # Extract product names from table
        product_names = []
        for p in self.page.locator(OrderPurchaseLocators.ORDER_DETAILS_PRODUCT_NAME).all():
            try:
                txt = p.inner_text().strip()
                if txt and txt not in product_names:
                    product_names.append(txt)
            except Exception:
                pass

        subtotal_elem = self.page.locator(OrderPurchaseLocators.ORDER_DETAILS_SUBTOTAL).first
        subtotal = subtotal_elem.inner_text().strip() if subtotal_elem.is_visible(timeout=2000) else ""

        disc_elem = self.page.locator(OrderPurchaseLocators.ORDER_DETAILS_DISCOUNT).first
        discount = disc_elem.inner_text().strip() if disc_elem.is_visible(timeout=2000) else ""

        total_elem = self.page.locator(OrderPurchaseLocators.ORDER_DETAILS_GRAND_TOTAL).first
        grand_total = ""
        if total_elem.is_visible(timeout=2000):
            raw_t = total_elem.inner_text().strip()
            if "$" in raw_t or re.search(r"\d+\.\d{2}", raw_t):
                grand_total = raw_t
        if not grand_total:
            try:
                body_text = self.page.locator("body").inner_text()
                match = re.search(r"Order\s+total\s*[:\n\r\t]+\s*(\$[0-9\.]+)", body_text, re.IGNORECASE)
                if match:
                    grand_total = match.group(1).strip()
            except Exception:
                pass

        date_elem = self.page.locator(OrderPurchaseLocators.ORDER_DETAILS_DATE).first
        order_date = date_elem.inner_text().strip() if date_elem.is_visible(timeout=2000) else ""

        logger.info(
            f"Parsed Order Details: order_number='{order_number}', status='{status}', "
            f"products={product_names}, subtotal='{subtotal}', discount='{discount}', "
            f"grand_total='{grand_total}', date='{order_date}'"
        )

        return {
            "order_number": order_number,
            "url": curr_url,
            "title": title,
            "status": status,
            "product_names": product_names,
            "subtotal": subtotal,
            "discount": discount,
            "grand_total": grand_total,
            "order_date": order_date,
        }

