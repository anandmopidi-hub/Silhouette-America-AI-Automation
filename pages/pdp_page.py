import json
import re
from typing import Any, Dict, List, Optional
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError
from config.config import Config
from locators.home_locators import HomeLocators
from locators.pdp_locators import PdpLocators
from pages.base_page import BasePage
from utils.logger import logger
from utils.wait_helper import WaitHelper


class PdpPage(BasePage):
    """Page Object for Silhouette America Product Detail Page (PDP) functionality."""

    def __init__(self, page: Page, config: Optional[Config] = None):
        super().__init__(page, config)

    # =========================================================================
    # Navigation & Initial Load
    # =========================================================================

    def open_pdp(self, product_slug: str = "cameo-mat") -> str:
        """Navigate to a Product Detail Page (PDP), resolve challenges, and dismiss cookies.

        Args:
            product_slug: Relative path/slug (e.g., 'cameo-mat' or 'cameo-pro') or full URL.

        Returns:
            Current URL after loading.
        """
        slug = product_slug.lstrip("/")
        logger.info(f"Opening Product Detail Page: '{slug}'")
        self.goto(slug)
        self.wait_for_dom_content_loaded()

        # Handle Cloudflare challenge screen if triggered
        try:
            if "just a moment" in self.get_title().lower():
                logger.info("Cloudflare challenge screen active on PDP. Waiting for resolution...")
                self.page.wait_for_function(
                    "!document.title.toLowerCase().includes('just a moment')",
                    timeout=15000,
                )
                self.wait_for_dom_content_loaded()
        except Exception as e:
            logger.debug(f"Challenge check passed or timed out: {e}")

        # Ensure main product info container is hydrated
        try:
            self.page.wait_for_selector(PdpLocators.PAGE_TITLE, state="visible", timeout=15000)
        except Exception:
            pass

        # Detect cookie popup, click 'I Agree', and wait until dismissed and stable
        self.dismiss_cookie_consent_if_present(timeout=5000)

        self.wait_for_timeout(1000)
        current_url = self.get_current_url()
        logger.info(f"PDP loaded successfully at: '{current_url}'")
        return current_url

    def dismiss_cookie_consent_if_present(self, timeout: int = 5000) -> bool:
        """Centrally dismiss cookie consent popup via BasePage."""
        return super().dismiss_cookie_consent_if_present(timeout=timeout)

    def is_pdp_loaded(self, expected_slug_or_name: Optional[str] = None) -> bool:
        """Validate that the Product Detail Page (PDP) has loaded successfully.

        Checks:
        1. Current URL matches silhouetteamerica.com and contains slug (if provided).
        2. Page title does not indicate an error (no 500 / 404).
        3. Product title (h1) is visible.
        4. Main info container or purchase block is present.
        """
        current_url = self.get_current_url()
        title = self.get_title()

        no_500_error = "500" not in title and "error" not in title.lower()
        title_visible = self.is_visible(PdpLocators.PAGE_TITLE, timeout=5000)
        content_present = (
            self.is_visible(PdpLocators.MAIN_INFO_CONTAINER, timeout=5000)
            or self.is_visible(PdpLocators.ADD_TO_CART_BUTTON, timeout=3000)
            or self.is_visible(PdpLocators.OUT_OF_STOCK_BADGE, timeout=3000)
        )

        slug_valid = True
        if expected_slug_or_name:
            clean_expected = expected_slug_or_name.lower().replace("-", " ")
            slug_valid = (
                expected_slug_or_name.lower() in current_url.lower()
                or clean_expected in title.lower()
                or clean_expected in self.get_product_name().lower()
            )

        is_loaded = no_500_error and title_visible and content_present and slug_valid
        logger.info(
            f"PDP load validation: URL='{current_url}', Title='{title}', "
            f"title_visible={title_visible}, content_present={content_present}, is_loaded={is_loaded}"
        )
        return is_loaded

    # =========================================================================
    # Product Information & Metadata
    # =========================================================================

    def get_product_name(self) -> str:
        """Retrieve the primary product name heading (h1) text."""
        name = self.get_text(PdpLocators.PAGE_TITLE, timeout=5000)
        logger.info(f"Retrieved PDP product name: '{name}'")
        return name

    def get_product_sku(self) -> str:
        """Retrieve the product SKU value."""
        sku_elem = self.page.locator(PdpLocators.SKU).first
        try:
            if sku_elem.is_visible(timeout=3000):
                sku_text = sku_elem.inner_text().strip()
                logger.info(f"Retrieved PDP product SKU: '{sku_text}'")
                return sku_text
        except Exception:
            pass
        return ""

    def get_product_image_count(self) -> int:
        """Return the count of actual product images displayed in the gallery.

        Dynamically checks the number of gallery slides / stage frames or thumbnails,
        rather than raw HTML img tags in the media container.
        """
        try:
            self.page.wait_for_selector(PdpLocators.GALLERY_STAGE_FRAMES, state="attached", timeout=5000)
        except Exception:
            pass

        stage_count = self.page.locator(PdpLocators.GALLERY_STAGE_FRAMES).count()
        if stage_count > 0:
            logger.info(f"Detected {stage_count} actual product gallery image slides.")
            return stage_count

        thumb_count = self.page.locator(PdpLocators.GALLERY_THUMBNAILS).count()
        if thumb_count > 0:
            logger.info(f"Detected {thumb_count} product gallery thumbnail frames.")
            return thumb_count

        # Fallback for single static image PDPs without Fotorama
        visible_imgs = [
            img for img in self.page.locator(".product.media img").all()
            if img.is_visible() and img.get_attribute("src") != "false"
        ]
        count = len(visible_imgs) if visible_imgs else 1
        logger.info(f"Detected {count} displayed product images via fallback.")
        return count

    def is_product_image_visible(self) -> bool:
        """Verify that the active product image is rendered, visible, and loaded."""
        try:
            active_img = self.page.locator(PdpLocators.GALLERY_ACTIVE_IMAGE).first
            if active_img.is_visible(timeout=3000):
                loaded = active_img.evaluate("e => e.complete && e.naturalWidth > 0")
                if loaded:
                    logger.info("Active product image is visible and loaded successfully.")
                    return True
        except Exception:
            pass

        # Fallback to stage frame check
        try:
            for frame in self.page.locator(PdpLocators.GALLERY_STAGE_FRAMES).all():
                if frame.is_visible():
                    return True
        except Exception:
            pass

        return self.is_visible(PdpLocators.GALLERY_CONTAINER, timeout=3000)

    def get_displayed_image_urls(self) -> List[str]:
        """Extract URLs of actual unique product images displayed in the gallery."""
        urls: List[str] = []
        for frame in self.page.locator(PdpLocators.GALLERY_STAGE_FRAMES).all():
            img = frame.locator("img.fotorama__img, img").first
            try:
                src = img.get_attribute("src") or ""
                if src and src != "false" and not src.startswith("data:") and src not in urls:
                    urls.append(src)
            except Exception:
                continue
        if not urls:
            active_img = self.page.locator(PdpLocators.GALLERY_ACTIVE_IMAGE).first
            try:
                src = active_img.get_attribute("src") or ""
                if src and src != "false":
                    urls.append(src)
            except Exception:
                pass
        logger.info(f"Retrieved {len(urls)} displayed product image URLs: {urls}")
        return urls

    def click_through_gallery_images(self) -> List[str]:
        """Click through each available gallery thumbnail, verifying each image displays and loads.

        Returns:
            List of unique displayed image URLs observed during the click-through.
        """
        displayed_urls: List[str] = []
        thumbs = self.page.locator(PdpLocators.GALLERY_THUMBNAILS).all()
        if not thumbs:
            # Single image product without navigation thumbnails
            active_img = self.page.locator(PdpLocators.GALLERY_ACTIVE_IMAGE).first
            try:
                if active_img.is_visible(timeout=3000):
                    src = active_img.get_attribute("src") or ""
                    if src:
                        displayed_urls.append(src)
            except Exception:
                pass
            return displayed_urls

        logger.info(f"Clicking through {len(thumbs)} product gallery thumbnails...")
        for i, thumb in enumerate(thumbs):
            try:
                thumb.scroll_into_view_if_needed()
                thumb.click()
                self.wait_for_timeout(600)
                active_img = self.page.locator(PdpLocators.GALLERY_ACTIVE_IMAGE).first
                if active_img.is_visible():
                    src = active_img.get_attribute("src") or ""
                    is_loaded = active_img.evaluate("e => e.complete && e.naturalWidth > 0")
                    if src and is_loaded and src not in displayed_urls:
                        displayed_urls.append(src)
                        logger.info(f"Verified displayed gallery image {i + 1}/{len(thumbs)}: '{src}' (loaded={is_loaded})")
            except Exception as e:
                logger.debug(f"Thumbnail interaction notice at index {i}: {e}")

        # Reset gallery back to primary first thumbnail for clean UI state
        if thumbs:
            try:
                thumbs[0].click()
                self.wait_for_timeout(300)
            except Exception:
                pass

        return displayed_urls

    def has_specifications(self) -> bool:
        """Check whether product specifications, 'what's included', or attribute tables are visible."""
        for sel in [
            PdpLocators.SPECIFICATIONS,
            ".product.attribute.samchine",
            ".additional-attributes",
            "table.additional-attributes",
            "#product-attribute-specs-table",
        ]:
            try:
                loc = self.page.locator(sel).first
                if loc.is_visible(timeout=1000) and len(loc.inner_text().strip()) > 0:
                    return True
            except Exception:
                continue
        return False

    def get_product_specifications(self) -> str:
        """Retrieve specifications or additional attributes text if available on the PDP."""
        for sel in [
            PdpLocators.SPECIFICATIONS,
            ".product.attribute.samchine",
            ".additional-attributes",
            "table.additional-attributes",
            "#product-attribute-specs-table",
        ]:
            try:
                for el in self.page.locator(sel).all():
                    if el.is_visible():
                        txt = el.inner_text().strip()
                        if len(txt) > 0 and txt != self.get_product_sku() and txt != self.get_product_name():
                            logger.info(f"Retrieved product specifications ({len(txt)} chars).")
                            return txt
            except Exception:
                continue
        return ""

    def get_product_description(self) -> str:
        """Retrieve product description / overview text."""
        try:
            sku = self.get_product_sku()
            for desc_elem in self.page.locator(PdpLocators.DESCRIPTION).all():
                if desc_elem.is_visible():
                    desc_text = desc_elem.inner_text().strip()
                    if desc_text and desc_text != sku and len(desc_text) > 10:
                        logger.info(f"Retrieved product description (length={len(desc_text)} chars).")
                        return desc_text
        except Exception as e:
            logger.debug(f"Error fetching product description: {e}")
        return ""

    # =========================================================================
    # Pricing Verification (Regular vs. Sale)
    # =========================================================================

    def get_regular_price(self) -> str:
        """Retrieve regular price text (e.g. '$14.99')."""
        try:
            # Check normal-price container first
            norm_elem = self.page.locator(PdpLocators.REGULAR_PRICE).first
            if norm_elem.is_visible(timeout=3000):
                price = norm_elem.inner_text().strip()
                logger.info(f"Retrieved regular price: '{price}'")
                return price
        except Exception:
            pass

        # Fallback to final price
        price = self.get_text(PdpLocators.FINAL_PRICE, timeout=3000)
        logger.info(f"Retrieved price via final price locator: '{price}'")
        return price

    def get_sale_price(self) -> Optional[str]:
        """Retrieve current sale / special price text if product is on sale."""
        try:
            special_elem = self.page.locator(PdpLocators.SPECIAL_PRICE).first
            if special_elem.is_visible(timeout=3000):
                price = special_elem.inner_text().strip()
                logger.info(f"Retrieved sale/special price: '{price}'")
                return price
        except Exception:
            pass
        return None

    def get_original_price(self) -> Optional[str]:
        """Retrieve original / regular strike-through price text for a sale product."""
        try:
            old_elem = self.page.locator(PdpLocators.OLD_PRICE).first
            if old_elem.is_visible(timeout=3000):
                price = old_elem.inner_text().strip()
                logger.info(f"Retrieved original/old price: '{price}'")
                return price
        except Exception:
            pass
        return None

    def is_sale_product(self) -> bool:
        """Verify whether product displays both sale price and original price."""
        sale_p = self.get_sale_price()
        orig_p = self.get_original_price()
        has_both = bool(sale_p and orig_p and "$" in sale_p and "$" in orig_p)
        logger.info(f"Sale product verification: sale='{sale_p}', original='{orig_p}' -> is_sale={has_both}")
        return has_both

    # =========================================================================
    # Configurable Variants / Swatches
    # =========================================================================

    def get_available_variants(self) -> List[str]:
        """Return list of text labels for all visible variant swatch options."""
        options = []
        swatches = self.page.locator(PdpLocators.SWATCH_OPTIONS)
        for i in range(swatches.count()):
            txt = swatches.nth(i).inner_text().strip()
            if txt:
                options.append(txt)
        logger.info(f"Available variant swatches: {options}")
        return options

    def get_selected_variants(self) -> List[str]:
        """Return list of text labels for currently selected variant swatches."""
        selected = []
        selected_swatches = self.page.locator(PdpLocators.SWATCH_SELECTED)
        for i in range(selected_swatches.count()):
            txt = selected_swatches.nth(i).inner_text().strip()
            if txt:
                selected.append(txt)
        logger.info(f"Currently selected swatches: {selected}")
        return selected

    def select_variant(self, option_text: str) -> None:
        """Click and select a variant swatch option matching the specified text label.

        Args:
            option_text: Text of the swatch option (e.g., '12" x 24"').
        """
        logger.info(f"Selecting variant swatch option: '{option_text}'")
        target_swatch = self.page.locator(PdpLocators.SWATCH_OPTIONS).filter(has_text=option_text).first
        target_swatch.scroll_into_view_if_needed()
        target_swatch.click()
        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(1000)
        logger.info(f"Selected variant: '{option_text}'. Price updated to: '{self.get_regular_price()}'")

    def deselect_active_variant(self) -> None:
        """Deselect currently active variant swatch by clicking it again."""
        active_swatch = self.page.locator(PdpLocators.SWATCH_SELECTED).first
        if active_swatch.is_visible(timeout=3000):
            txt = active_swatch.inner_text().strip()
            logger.info(f"Deselecting active swatch: '{txt}'")
            active_swatch.click()
            self.wait_for_timeout(500)

    def is_mandatory_option_error_displayed(self) -> bool:
        """Verify that Magento's required option validation error ('This is a required field.') is visible."""
        try:
            for err in self.page.locator(PdpLocators.SWATCH_ERROR).all():
                if err.is_visible():
                    txt = err.inner_text().strip()
                    if "required" in txt.lower() or "this is a required field" in txt.lower():
                        logger.info(f"Mandatory option error detected: '{txt}'")
                        return True
        except Exception:
            pass
        return False

    def get_mandatory_option_error_text(self) -> str:
        """Retrieve text of the mandatory option error message."""
        try:
            for err in self.page.locator(PdpLocators.SWATCH_ERROR).all():
                if err.is_visible():
                    txt = err.inner_text().strip()
                    if "required" in txt.lower():
                        return txt
        except Exception:
            pass
        return ""

    # =========================================================================
    # Add to Cart & Purchase
    # =========================================================================

    def click_add_to_cart(self) -> None:
        """Click the primary 'Add to Cart' button."""
        logger.info("Clicking 'Add to Cart' button.")
        add_btn = self.page.locator(PdpLocators.ADD_TO_CART_BUTTON).first
        add_btn.scroll_into_view_if_needed()
        add_btn.click()
        self.wait_for_timeout(1500)

    def is_add_to_cart_available(self) -> bool:
        """Check whether the Add to Cart button is present, visible, and enabled."""
        add_btn = self.page.locator(PdpLocators.ADD_TO_CART_BUTTON).first
        try:
            return add_btn.is_visible(timeout=2000) and add_btn.is_enabled(timeout=2000)
        except Exception:
            return False

    def get_cart_count(self) -> int:
        """Extract and return current numeric item count displayed in the header cart counter."""
        counter_elem = self.page.locator(PdpLocators.HEADER_CART_COUNTER).first
        try:
            if counter_elem.is_visible(timeout=3000):
                txt = counter_elem.inner_text().strip()
                digits = [int(w) for w in txt.split() if w.isdigit()]
                if digits:
                    logger.info(f"Header cart counter value: {digits[0]}")
                    return digits[0]
                if txt.isdigit():
                    return int(txt)
        except Exception:
            pass
        return 0

    def is_product_added_to_cart(self, timeout: int = 6000) -> bool:
        """Verify that product was successfully added to cart.

        Checks:
        1. Success message banner appears ('You added ... to your shopping cart.').
        2. Cart counter updates to >= 1.
        """
        success_msg_visible = False
        try:
            msg_elem = self.page.locator(PdpLocators.SUCCESS_MESSAGE).first
            msg_elem.wait_for(state="visible", timeout=timeout)
            txt = msg_elem.inner_text().strip()
            success_msg_visible = "added" in txt.lower() and "cart" in txt.lower()
            logger.info(f"Add to cart success notification visible: '{txt}'")
        except Exception:
            pass

        count = self.get_cart_count()
        is_added = success_msg_visible or count >= 1
        logger.info(f"Add to cart completion: success_banner={success_msg_visible}, cart_count={count} -> is_added={is_added}")
        return is_added

    def get_success_message(self) -> str:
        """Retrieve text from add-to-cart success notification banner."""
        try:
            msg_elem = self.page.locator(PdpLocators.SUCCESS_MESSAGE).first
            if msg_elem.is_visible(timeout=3000):
                return msg_elem.inner_text().strip()
        except Exception:
            pass
        return ""

    # =========================================================================
    # Out of Stock / Unavailable State
    # =========================================================================

    def is_out_of_stock(self) -> bool:
        """Check whether product is marked as unavailable / out of stock."""
        selectors = [
            PdpLocators.OUT_OF_STOCK_BADGE,
            ".product-info-main .stock.unavailable",
            ".product-info-stock-sku .stock.unavailable",
            ".product-info-main [title='Availability']",
            ":is(.product-info-main, .product-info-stock-sku) :text-matches('out of stock', 'i')",
        ]
        for sel in selectors:
            loc = self.page.locator(sel)
            count = loc.count()
            for i in range(count):
                item = loc.nth(i)
                try:
                    if item.is_visible(timeout=1000):
                        txt = item.inner_text().strip()
                        if "out of stock" in txt.lower() or "unavailable" in txt.lower():
                            logger.info(f"Out of stock badge detected dynamically: '{txt}' via '{sel}'")
                            return True
                except Exception:
                    continue
        return False

    def get_stock_status_text(self) -> str:
        """Retrieve text from stock status badge (In Stock or Out Of Stock)."""
        selectors = [
            PdpLocators.OUT_OF_STOCK_BADGE,
            PdpLocators.IN_STOCK_BADGE,
            ".product-info-main .stock.unavailable",
            ".product-info-stock-sku .stock.unavailable",
            ":is(.product-info-main, .product-info-stock-sku) :text-matches('out of stock', 'i')",
        ]
        for sel in selectors:
            loc = self.page.locator(sel)
            count = loc.count()
            for i in range(count):
                item = loc.nth(i)
                try:
                    if item.is_visible(timeout=1000):
                        txt = item.inner_text().strip()
                        if txt:
                            return txt
                except Exception:
                    continue
        return ""

    # =========================================================================
    # Quantity Controls & Boundaries
    # =========================================================================

    def get_quantity(self) -> int:
        """Retrieve current integer quantity value."""
        qty_input = self.page.locator(PdpLocators.QTY_INPUT).first
        try:
            val = qty_input.input_value()
            if val and val.isdigit():
                return int(val)
        except Exception:
            pass
        return 1

    def scroll_quantity_into_view(self) -> None:
        """Scroll quantity input and controls into viewport for clear interaction and recording."""
        qty_elem = self.page.locator(PdpLocators.QTY_INPUT).first
        try:
            qty_elem.scroll_into_view_if_needed()
            self.wait_for_timeout(300)
        except Exception:
            pass

    def set_quantity(self, quantity: int) -> int:
        """Set the quantity input directly to a specific value.

        Args:
            quantity: Integer quantity to set.

        Returns:
            Current integer quantity after setting.
        """
        logger.info(f"Setting quantity input to {quantity}.")
        script = f"""() => {{
            const input = document.querySelector('#qty');
            if (input) {{
                input.removeAttribute('readonly');
                input.style.display = 'block';
                input.value = '{quantity}';
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            const err = document.querySelector('#qty-error');
            if (err) {{
                err.style.display = 'none';
                err.innerText = '';
            }}
        }}"""
        self.page.evaluate(script)
        self.wait_for_timeout(300)
        return self.get_quantity()

    def increment_quantity(self) -> int:
        """Click plus button to increase quantity."""
        plus_btn = self.page.locator(PdpLocators.QTY_PLUS_BUTTON).first
        plus_btn.click()
        self.wait_for_timeout(300)
        return self.get_quantity()

    def decrement_quantity(self) -> int:
        """Click minus button to decrease quantity."""
        minus_btn = self.page.locator(PdpLocators.QTY_MINUS_BUTTON).first
        minus_btn.click()
        self.wait_for_timeout(300)
        return self.get_quantity()

    def get_quantity_validation_rules(self) -> Dict[str, Any]:
        """Extract quantity validation rules and boundary definitions from input attributes."""
        qty_input = self.page.locator(PdpLocators.QTY_INPUT).first
        data_validate = qty_input.get_attribute("data-validate") or "{}"
        min_attr = qty_input.get_attribute("min") or "1"
        is_readonly = qty_input.get_attribute("readonly") is not None

        try:
            rules_dict = json.loads(data_validate)
        except Exception:
            rules_dict = {}

        item_qty_rule = rules_dict.get("validate-item-quantity", {})
        min_allowed = item_qty_rule.get("minAllowed", int(min_attr) if min_attr.isdigit() else 1)
        max_allowed = item_qty_rule.get("maxAllowed", 10000)

        rules = {
            "min_allowed": min_allowed,
            "max_allowed": max_allowed,
            "is_readonly": is_readonly,
            "raw_rules": rules_dict,
        }
        logger.info(f"Evaluated quantity boundary rules: {rules}")
        return rules

    def get_quantity_error_text(self) -> str:
        """Retrieve any visible quantity error validation text."""
        try:
            qty_err = self.page.locator(PdpLocators.QTY_ERROR).first
            if qty_err.is_visible(timeout=2000):
                txt = qty_err.inner_text().strip()
                if txt:
                    logger.info(f"Quantity error text from {PdpLocators.QTY_ERROR}: '{txt}'")
                    return txt
        except Exception:
            pass

        try:
            for el in self.page.locator(".mage-error, div.mage-error").all():
                if el.is_visible():
                    txt = el.inner_text().strip()
                    if any(k in txt.lower() for k in ["quantity", "greater than", "maximum", "minimum", "purchase"]):
                        logger.info(f"Quantity error text from .mage-error: '{txt}'")
                        return txt
        except Exception:
            pass
        return ""

    def trigger_quantity_validation(self, quantity: int) -> str:
        """Set a quantity and submit via Add to Cart to trigger and retrieve validation message."""
        logger.info(f"Triggering quantity validation for quantity: {quantity}")
        self.set_quantity(quantity)
        self.click_add_to_cart()
        self.wait_for_timeout(1000)
        return self.get_quantity_error_text()

    def trigger_quantity_validation_with_zero(self) -> str:
        """Attempt to submit zero quantity and capture Magento's validation message."""
        return self.trigger_quantity_validation(0)

    # =========================================================================
    # Intentional Evidence Preparation
    # =========================================================================

    def prepare_for_pdp_evidence(self) -> None:
        """Ensure PDP viewport is scrolled appropriately, transient elements dismissed, and UI stable."""
        logger.info("Preparing PDP evidence state for screenshot.")
        try:
            self.page.evaluate("window.scrollTo(0, 0)")
        except Exception:
            pass
        self.dismiss_transient_elements()
        self.wait_for_timeout(300)
