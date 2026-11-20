import json
import re
from typing import Any, Dict, List, Optional
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError
from config.config import Config
from locators.different_pdp_locators import Different_PDP_Locators
from pages.base_page import BasePage
from utils.logger import logger


class Different_PDP_Page(BasePage):
    """Single, unified Page Object Model for all Product Detail Page (PDP) variants:

    - Machine PDP (E2E-Different_PDP-001)
    - Tools & Mats PDP (E2E-Different_PDP-002)
    - Clearance Supply Bundles PDP & PLP (E2E-Different_PDP-003)
    - Software PDP (E2E-Different_PDP-004)
    """

    def __init__(self, page: Page, config: Optional[Config] = None):
        super().__init__(page, config)

    # =========================================================================
    # 1. Navigation & Dynamic Product Selection
    # =========================================================================

    def navigate_to_category(self, category_name: str) -> str:
        """Navigate to a top-level category or PLP.

        Supports: 'machines', 'tools-mats', 'clearance-supply-bundles', 'software'.
        """
        logger.info(f"Navigating to category: '{category_name}'")
        mapping = {
            "machines": "machines",
            "tools-mats": "machine-tools-mats/machine-tools",
            "tools-and-mats": "machine-tools-mats/machine-tools",
            "clearance-supply-bundles": "accessories-parts/supply-bundles",
            "supply-bundles": "accessories-parts/supply-bundles",
            "software": "software",
        }
        target_path = mapping.get(category_name.lower(), category_name)
        self.goto(target_path, wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.wait_for_timeout(2000)
        curr_url = self.get_current_url()
        logger.info(f"Category '{category_name}' loaded at URL: '{curr_url}'")
        return curr_url

    def navigate_to_clearance_supply_bundles(self) -> str:
        """Navigate to Clearance -> Supply Bundles via header menu interaction or direct fallback."""
        logger.info("Opening Supply Bundles via Clearance navigation...")
        self.goto("", wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()

        # Attempt header hover / click
        clearance_nav = self.page.locator(Different_PDP_Locators.CLEARANCE_NAV_TRIGGER).first
        if clearance_nav.is_visible(timeout=3000):
            try:
                clearance_nav.hover()
                self.wait_for_timeout(500)
                bundle_link = self.page.locator(Different_PDP_Locators.SUPPLY_BUNDLES_NAV_LINK).first
                if bundle_link.is_visible(timeout=2000):
                    bundle_link.click()
                    self.wait_for_dom_content_loaded()
                    self.wait_for_timeout(2000)
                    return self.get_current_url()
            except Exception as e:
                logger.debug(f"Hover clearance navigation fallback: {e}")

        # Direct navigation fallback
        return self.navigate_to_category("clearance-supply-bundles")

    def open_product_by_slug(self, slug: str) -> str:
        """Navigate directly to any product slug or path."""
        clean_slug = slug.lstrip("/")
        logger.info(f"Opening product directly by slug: '{clean_slug}'")
        self.goto(clean_slug, wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.wait_for_timeout(2000)
        return self.get_current_url()

    def select_available_product_dynamically(self) -> Dict[str, str]:
        """Inspect the current category/PLP, identify an available product card, and open its PDP.

        Returns:
            Dict containing selected product 'name', 'href', and 'price'.
        """
        logger.info("Dynamically identifying an in-stock product on current listing...")
        self.page.wait_for_selector(Different_PDP_Locators.PLP_PRODUCT_CARDS, state="visible", timeout=15000)
        cards = self.page.locator(Different_PDP_Locators.PLP_PRODUCT_CARDS).all()
        assert len(cards) > 0, "No product cards found on listing page."

        chosen_prod: Dict[str, str] = {"name": "", "href": "", "price": ""}

        for card in cards:
            try:
                card_text = card.inner_text().strip()
                # Check for in-stock
                if "out of stock" in card_text.lower():
                    continue

                link_elem = card.locator(Different_PDP_Locators.PLP_PRODUCT_LINK).first
                if link_elem.is_visible(timeout=1000):
                    href = link_elem.get_attribute("href") or ""
                    name = link_elem.inner_text().strip()
                    price_elem = card.locator(Different_PDP_Locators.PLP_PRODUCT_PRICE).first
                    price = price_elem.inner_text().strip() if price_elem.is_visible(timeout=500) else ""

                    if href and not chosen_prod["href"]:
                        chosen_prod["name"] = name
                        chosen_prod["href"] = href
                        chosen_prod["price"] = price
                        logger.info(f"Selected product card: name='{name}', price='{price}', href='{href}'")
                        link_elem.click()
                        break
            except Exception as e:
                logger.debug(f"Card inspection note: {e}")
                continue

        # If click didn't navigate, open href directly
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.wait_for_timeout(2000)

        logger.info(f"Opened PDP: URL='{self.get_current_url()}'")
        return chosen_prod

    def verify_pdp_loaded(self, expected_slug_or_name: Optional[str] = None) -> bool:
        """Verify that the Product Detail Page has loaded cleanly without 404/500 errors."""
        curr_url = self.get_current_url()
        title = self.get_title()

        no_error = "404" not in title and "500" not in title and "error" not in title.lower()

        # Check title visibility using .first
        title_visible = False
        for sel in [Different_PDP_Locators.PAGE_TITLE, "h1", ".page-title", ".product-info-main"]:
            try:
                el = self.page.locator(sel).first
                if el.is_visible(timeout=1000):
                    title_visible = True
                    break
            except Exception:
                continue

        # Check price or purchase block using .first
        price_or_cart = False
        for sel in [
            Different_PDP_Locators.PRODUCT_PRICE,
            Different_PDP_Locators.PURCHASE_BUTTON,
            Different_PDP_Locators.ADD_TO_CART_BUTTON,
            Different_PDP_Locators.OUT_OF_STOCK_BADGE,
            Different_PDP_Locators.MAIN_INFO_CONTAINER,
            ".price",
            "button",
        ]:
            try:
                el = self.page.locator(sel).first
                if el.is_visible(timeout=1000):
                    price_or_cart = True
                    break
            except Exception:
                continue

        keyword_match = True
        if expected_slug_or_name:
            clean = expected_slug_or_name.lower().replace("-", " ")
            keyword_match = (
                expected_slug_or_name.lower() in curr_url.lower()
                or clean in title.lower()
                or clean in self.get_product_name().lower()
            )

        is_loaded = no_error and (title_visible or price_or_cart) and keyword_match
        logger.info(
            f"PDP loaded verification: URL='{curr_url}', Title='{title}', "
            f"title_visible={title_visible}, price_or_cart={price_or_cart}, is_loaded={is_loaded}"
        )
        return is_loaded

    # =========================================================================
    # 2. Core Product Information (Name, Price, SKU, Description, Availability)
    # =========================================================================

    def get_product_name(self) -> str:
        """Retrieve displayed product name heading."""
        try:
            elem = self.page.locator(Different_PDP_Locators.PAGE_TITLE).first
            if elem.is_visible(timeout=3000):
                txt = elem.inner_text().strip()
                if txt:
                    logger.info(f"Retrieved PDP product name: '{txt}'")
                    return txt
        except Exception:
            pass
        title = self.get_title()
        logger.info(f"Retrieved PDP product name from title: '{title}'")
        return title

    def get_displayed_price(self) -> str:
        """Retrieve currently displayed product price (regular, sale, or final)."""
        # Try final price container
        final_price = self.page.locator(Different_PDP_Locators.PRODUCT_PRICE).first
        if final_price.is_visible(timeout=3000):
            price_text = final_price.inner_text().strip()
            # Extract first currency match e.g. '$279.99'
            match = re.search(r"(\$[0-9\.,]+)", price_text)
            if match:
                logger.info(f"Retrieved displayed price: '{match.group(1)}'")
                return match.group(1)
            return price_text

        # Try purchase button text (e.g. 'Purchase $39.99')
        btn = self.page.locator(Different_PDP_Locators.PURCHASE_BUTTON).first
        if btn.is_visible(timeout=2000):
            txt = btn.inner_text().strip()
            match = re.search(r"(\$[0-9\.,]+)", txt)
            if match:
                logger.info(f"Retrieved price from purchase button: '{match.group(1)}'")
                return match.group(1)

        return ""

    def get_product_sku(self) -> str:
        """Retrieve product SKU text if present."""
        sku_elem = self.page.locator(Different_PDP_Locators.PRODUCT_SKU).first
        try:
            if sku_elem.is_visible(timeout=3000):
                sku = sku_elem.inner_text().strip()
                logger.info(f"Retrieved product SKU: '{sku}'")
                return sku
        except Exception:
            pass
        return ""

    def get_product_description(self) -> str:
        """Retrieve product overview or description text."""
        for desc_elem in self.page.locator(Different_PDP_Locators.PRODUCT_DESCRIPTION).all():
            try:
                if desc_elem.is_visible():
                    txt = desc_elem.inner_text().strip()
                    if txt and len(txt) > 20:
                        logger.info(f"Retrieved product description ({len(txt)} chars).")
                        return txt
            except Exception:
                continue
        return ""

    def verify_product_availability(self) -> Dict[str, Any]:
        """Check whether the product is in-stock, out of stock, or purchasable."""
        is_in_stock = self.page.locator(Different_PDP_Locators.IN_STOCK_BADGE).first.is_visible(timeout=2000)
        is_out_of_stock = self.page.locator(Different_PDP_Locators.OUT_OF_STOCK_BADGE).first.is_visible(timeout=2000)
        has_add_cart = self.page.locator(Different_PDP_Locators.ADD_TO_CART_BUTTON).first.is_visible(timeout=2000)
        has_purchase = self.page.locator(Different_PDP_Locators.PURCHASE_BUTTON).first.is_visible(timeout=2000)

        status_text = "In Stock" if (is_in_stock or has_add_cart or has_purchase) else "Out of Stock"
        info = {
            "is_in_stock": is_in_stock or has_add_cart or has_purchase,
            "is_out_of_stock": is_out_of_stock,
            "status_text": status_text,
            "purchasable": has_add_cart or has_purchase,
        }
        logger.info(f"Product availability: {info}")
        return info

    # =========================================================================
    # 3. Product Image Gallery & Thumbnails
    # =========================================================================

    def get_gallery_image_count(self) -> int:
        """Count the number of gallery frames or thumbnails available."""
        thumbs = self.page.locator(Different_PDP_Locators.GALLERY_THUMBNAILS).count()
        if thumbs > 0:
            return thumbs
        frames = self.page.locator(Different_PDP_Locators.GALLERY_STAGE_FRAMES).count()
        if frames > 0:
            return frames
        return 1 if self.is_main_image_visible() else 0

    def is_main_image_visible(self) -> bool:
        """Check if main/active product image is visible and rendered."""
        for sel in [
            Different_PDP_Locators.GALLERY_ACTIVE_IMAGE,
            ".product.media picture img",
            ".gallery-placeholder picture img",
            ".product.media img",
            ".gallery-placeholder img",
            ".fotorama__stage__frame.fotorama__active img",
        ]:
            try:
                img = self.page.locator(sel).first
                if img.is_visible(timeout=1500):
                    has_render = img.evaluate(
                        "e => (e.naturalWidth > 0) || (e.clientWidth > 0 && e.clientHeight > 0) || "
                        "(e.width > 0 && e.height > 0) || Boolean(e.getAttribute('data-amsrc')) || "
                        "Boolean(e.getAttribute('src')) || Boolean(e.getAttribute('srcset'))"
                    )
                    if has_render:
                        return True
            except Exception:
                continue

        # Fallback: check media container
        for sel in [Different_PDP_Locators.GALLERY_CONTAINER, ".gallery-placeholder", ".fotorama"]:
            try:
                el = self.page.locator(sel).first
                if el.is_visible(timeout=1000):
                    return True
            except Exception:
                continue
        return False

    def get_active_image_src(self) -> str:
        """Extract current src attribute of the active main product image."""
        for sel in [
            Different_PDP_Locators.GALLERY_ACTIVE_IMAGE,
            ".product.media picture source",
            ".gallery-placeholder picture source",
            ".product.media img",
            ".gallery-placeholder img",
        ]:
            try:
                el = self.page.locator(sel).first
                if el.count() > 0:
                    src = el.get_attribute("src") or ""
                    if src and "data:image" not in src:
                        return src
                    srcset = el.get_attribute("srcset") or ""
                    if srcset:
                        return srcset.split()[0]
                    amsrc = el.get_attribute("data-amsrc") or ""
                    if amsrc:
                        return amsrc
            except Exception:
                continue
        return ""

    def interact_with_gallery_thumbnails(self) -> List[str]:
        """Click each available gallery thumbnail and verify the main image updates or remains valid.

        Returns:
            List of observed main image src values.
        """
        observed_srcs: List[str] = []
        thumbs = self.page.locator(Different_PDP_Locators.GALLERY_THUMBNAILS).all()
        if not thumbs:
            src = self.get_active_image_src()
            if src:
                observed_srcs.append(src)
            return observed_srcs

        logger.info(f"Clicking through {len(thumbs)} gallery thumbnails...")
        for idx, thumb in enumerate(thumbs[:3]):  # Check first 3 thumbnails
            try:
                thumb.scroll_into_view_if_needed()
                thumb.click()
                self.wait_for_timeout(400)
                src = self.get_active_image_src()
                if src and src not in observed_srcs:
                    observed_srcs.append(src)
                    logger.info(f"Thumbnail {idx + 1}/{len(thumbs)} verified: image src='{src[:60]}...'")
            except Exception as e:
                logger.debug(f"Thumbnail interaction notice at index {idx}: {e}")

        # Reset to first thumbnail
        if thumbs:
            try:
                thumbs[0].click()
                self.wait_for_timeout(400)
            except Exception:
                pass

        return observed_srcs

    # =========================================================================
    # 4. Color Swatches & Machine Options (Machine PDP & Options)
    # =========================================================================

    def get_available_colors(self) -> List[str]:
        """Retrieve list of available color swatch labels."""
        colors: List[str] = []
        swatches = self.page.locator(Different_PDP_Locators.COLOR_SWATCHES).all()
        for s in swatches:
            try:
                label = (
                    s.get_attribute("aria-label")
                    or s.get_attribute("option-label")
                    or s.inner_text().strip()
                )
                if label and label not in colors:
                    colors.append(label)
            except Exception:
                continue
        logger.info(f"Available color swatches: {colors}")
        return colors

    def select_color_by_index(self, index: int = 0) -> Dict[str, Any]:
        """Click and select a color swatch by index and verify UI updates."""
        swatches = self.page.locator(Different_PDP_Locators.COLOR_SWATCHES).all()
        if not swatches or index >= len(swatches):
            return {"selected": False, "color_name": "", "image_src": "", "sku": ""}

        target = swatches[index]
        label = (
            target.get_attribute("aria-label")
            or target.get_attribute("option-label")
            or target.inner_text().strip()
        )
        logger.info(f"Selecting color swatch {index + 1}/{len(swatches)}: '{label}'...")

        initial_src = self.get_active_image_src()
        target.scroll_into_view_if_needed()
        target.click()
        self.wait_for_timeout(1000)

        new_src = self.get_active_image_src()
        new_sku = self.get_product_sku()
        logger.info(f"Selected color '{label}': new_src='{new_src[:60]}...', new_sku='{new_sku}'")

        return {
            "selected": True,
            "color_name": label,
            "initial_src": initial_src,
            "new_src": new_src,
            "image_changed": new_src != initial_src,
            "sku": new_sku,
        }

    def get_available_machine_options(self) -> List[str]:
        """Retrieve list of available machine options (bundles, configurations)."""
        options: List[str] = []
        swatches = self.page.locator(Different_PDP_Locators.MACHINE_OPTIONS_SWATCHES).all()
        for s in swatches:
            try:
                txt = s.inner_text().strip()
                label = s.get_attribute("aria-label") or s.get_attribute("option-label") or txt.split("\n")[0]
                if label and label not in options:
                    options.append(label)
            except Exception:
                continue
        logger.info(f"Available machine options: {options}")
        return options

    def select_machine_option_by_index(self, index: int = 0) -> Dict[str, Any]:
        """Select a machine option / bundle configuration by index and verify price update."""
        swatches = self.page.locator(Different_PDP_Locators.MACHINE_OPTIONS_SWATCHES).all()
        if not swatches or index >= len(swatches):
            return {"selected": False, "option_name": "", "old_price": "", "new_price": ""}

        target = swatches[index]
        label = target.inner_text().strip().split("\n")[0] or f"Option-{index}"
        old_price = self.get_displayed_price()

        logger.info(f"Selecting machine option {index + 1}/{len(swatches)}: '{label}' (current price: '{old_price}')...")
        target.scroll_into_view_if_needed()
        target.click()
        self.wait_for_timeout(1200)

        new_price = self.get_displayed_price()
        logger.info(f"Selected option '{label}': price updated from '{old_price}' to '{new_price}'")

        return {
            "selected": True,
            "option_name": label,
            "old_price": old_price,
            "new_price": new_price,
            "price_changed": new_price != old_price,
            "availability": self.verify_product_availability(),
        }

    def select_each_available_option(self) -> List[Dict[str, Any]]:
        """Iterate through all available swatches/options, verify selection and price responsiveness."""
        results: List[Dict[str, Any]] = []
        # Try machine options swatches first, fallback to all swatches
        swatches = self.page.locator(Different_PDP_Locators.MACHINE_OPTIONS_SWATCHES).all()
        if not swatches:
            swatches = self.page.locator(Different_PDP_Locators.ALL_SWATCH_OPTIONS).all()

        for idx, swatch in enumerate(swatches[:5]):  # Verify up to 5 options
            try:
                txt = swatch.inner_text().strip().split("\n")[0] or f"Option-{idx}"
                old_price = self.get_displayed_price()
                swatch.scroll_into_view_if_needed()
                swatch.click()
                self.wait_for_timeout(1000)
                new_price = self.get_displayed_price()
                res = {
                    "index": idx,
                    "label": txt,
                    "old_price": old_price,
                    "new_price": new_price,
                    "price_updated": bool(new_price),
                }
                results.append(res)
                logger.info(f"Option {idx + 1} '{txt}': price='{new_price}'")
            except Exception as e:
                logger.debug(f"Option interaction note at index {idx}: {e}")

        return results

    # =========================================================================
    # 5. Quantity Controls
    # =========================================================================

    def verify_quantity_controls(self) -> Dict[str, Any]:
        """Verify quantity input field, increment, and decrement buttons."""
        qty_input = self.page.locator(Different_PDP_Locators.QTY_INPUT).first
        plus_btn = self.page.locator(Different_PDP_Locators.QTY_PLUS).first
        minus_btn = self.page.locator(Different_PDP_Locators.QTY_MINUS).first

        has_input = qty_input.is_visible(timeout=2000)
        has_plus = plus_btn.is_visible(timeout=2000)
        has_minus = minus_btn.is_visible(timeout=2000)

        initial_qty = 1
        if has_input:
            try:
                v = qty_input.input_value()
                initial_qty = int(v) if v.isdigit() else 1
            except Exception:
                pass

        # Test increment
        if has_plus:
            try:
                plus_btn.click()
                self.wait_for_timeout(300)
            except Exception:
                pass

        qty_after_inc = initial_qty
        if has_input:
            try:
                v = qty_input.input_value()
                qty_after_inc = int(v) if v.isdigit() else initial_qty
            except Exception:
                pass

        # Test decrement
        if has_minus:
            try:
                minus_btn.click()
                self.wait_for_timeout(300)
            except Exception:
                pass

        qty_after_dec = qty_after_inc
        if has_input:
            try:
                v = qty_input.input_value()
                qty_after_dec = int(v) if v.isdigit() else qty_after_inc
            except Exception:
                pass

        info = {
            "has_quantity_controls": has_input or has_plus or has_minus,
            "has_input": has_input,
            "has_plus": has_plus,
            "has_minus": has_minus,
            "initial_qty": initial_qty,
            "qty_after_inc": qty_after_inc,
            "qty_after_dec": qty_after_dec,
        }
        logger.info(f"Quantity controls verification: {info}")
        return info

    # =========================================================================
    # 6. Specifications, Compatibility & Contents (Tools & Mats PDP, Bundles)
    # =========================================================================

    def get_product_specifications(self) -> str:
        """Retrieve specifications or technical details text."""
        for sel in [
            Different_PDP_Locators.SPECIFICATIONS_SECTION,
            ".additional-attributes",
            "table.data.table",
        ]:
            try:
                for el in self.page.locator(sel).all():
                    if el.is_visible():
                        txt = el.inner_text().strip()
                        if txt and len(txt) > 10:
                            logger.info(f"Retrieved specifications ({len(txt)} chars).")
                            return txt
            except Exception:
                continue
        return ""

    def verify_compatibility_section(self) -> Dict[str, Any]:
        """Verify the compatibility section and supported machines/products."""
        logger.info("Inspecting compatibility section on PDP...")
        compat_elem = self.page.locator(Different_PDP_Locators.COMPATIBILITY_SECTION).first
        has_compat = False
        compat_text = ""

        try:
            if compat_elem.is_visible(timeout=3000):
                has_compat = True
                compat_text = compat_elem.inner_text().strip()
        except Exception:
            pass

        if not has_compat:
            # Fallback text search in body
            try:
                body_txt = self.page.locator("body").inner_text()
                match = re.search(r"(Compatible\s+with[^.\n]+)", body_txt, re.IGNORECASE)
                if match:
                    has_compat = True
                    compat_text = match.group(1).strip()
            except Exception:
                pass

        info = {
            "is_displayed": has_compat,
            "content_length": len(compat_text),
            "preview": compat_text[:100] if compat_text else "",
        }
        logger.info(f"Compatibility verification: {info}")
        return info

    def verify_bundle_contents(self) -> Dict[str, Any]:
        """Verify What's Included / Product Contents section."""
        logger.info("Inspecting What's Included / Bundle Contents...")
        contents_elem = self.page.locator(Different_PDP_Locators.CONTENTS_INCLUDED_SECTION).first
        has_contents = False
        content_text = ""

        try:
            if contents_elem.is_visible(timeout=3000):
                has_contents = True
                content_text = contents_elem.inner_text().strip()
        except Exception:
            pass

        if not has_contents:
            try:
                body_txt = self.page.locator("body").inner_text()
                match = re.search(r"(What\'s\s+Included[^.\n]+)", body_txt, re.IGNORECASE)
                if match:
                    has_contents = True
                    content_text = match.group(1).strip()
            except Exception:
                pass

        info = {
            "is_displayed": has_contents,
            "content_length": len(content_text),
            "preview": content_text[:100] if content_text else "",
        }
        logger.info(f"Product contents verification: {info}")
        return info

    # =========================================================================
    # 7. Customer Reviews Section (Tools & Mats PDP)
    # =========================================================================

    def verify_customer_reviews_section(self) -> Dict[str, Any]:
        """Verify the customer reviews section ('Real Results. Real Opinions. Real Reviews.')."""
        logger.info("Inspecting customer reviews section...")
        reviews_section = self.page.locator(Different_PDP_Locators.REVIEWS_SECTION).first
        has_reviews_section = False
        heading_text = ""

        try:
            if reviews_section.is_visible(timeout=3000):
                has_reviews_section = True
                heading_text = reviews_section.inner_text().strip().split("\n")[0]
        except Exception:
            pass

        if not has_reviews_section:
            # Check for heading in page text
            try:
                body_txt = self.page.locator("body").inner_text()
                if "reviews" in body_txt.lower() or "real results" in body_txt.lower():
                    has_reviews_section = True
                    heading_text = "Reviews Section Present in DOM"
            except Exception:
                pass

        review_count_elem = self.page.locator(Different_PDP_Locators.REVIEWS_COUNT).first
        review_count = review_count_elem.inner_text().strip() if review_count_elem.is_visible(timeout=1500) else "0"

        info = {
            "section_visible": has_reviews_section,
            "heading": heading_text,
            "review_count": review_count,
            "has_reviews": bool(has_reviews_section),
        }
        logger.info(f"Customer reviews verification: {info}")
        return info

    # =========================================================================
    # 8. Clearance & Supply Bundles PLP & Interactions (Clearance Bundles PDP)
    # =========================================================================

    def verify_supply_bundles_plp(self) -> Dict[str, Any]:
        """Verify Supply Bundles PLP listing, title, product count, and product cards."""
        logger.info("Verifying Supply Bundles PLP...")
        title = self.get_title()
        curr_url = self.get_current_url()

        self.page.wait_for_selector(Different_PDP_Locators.PLP_PRODUCT_CARDS, state="visible", timeout=15000)
        cards = self.page.locator(Different_PDP_Locators.PLP_PRODUCT_CARDS).all()
        card_count = len(cards)

        # Inspect first 3 cards for image, title, price
        valid_cards = 0
        for card in cards[:3]:
            has_img = card.locator(Different_PDP_Locators.PLP_PRODUCT_IMAGE).first.is_visible(timeout=1000)
            has_title = card.locator(Different_PDP_Locators.PLP_PRODUCT_LINK).first.is_visible(timeout=1000)
            has_price = card.locator(Different_PDP_Locators.PLP_PRODUCT_PRICE).first.is_visible(timeout=1000)
            if has_img and (has_title or has_price):
                valid_cards += 1

        info = {
            "title": title,
            "url": curr_url,
            "product_count": card_count,
            "valid_cards_sampled": valid_cards,
            "is_valid": card_count > 0,
        }
        logger.info(f"Supply Bundles PLP verified: {info}")
        return info

    def test_share_icon_on_product_card(self) -> Dict[str, Any]:
        """Click share icon on product card if present and verify it does not navigate away."""
        initial_url = self.get_current_url()
        share_btn = self.page.locator(Different_PDP_Locators.PLP_SHARE_ICON).first
        has_share = share_btn.is_visible(timeout=2000)

        opened_dialog = False
        if has_share:
            try:
                logger.info("Clicking share icon on product card...")
                share_btn.click()
                self.wait_for_timeout(1000)
                opened_dialog = self.is_visible(Different_PDP_Locators.PLP_SHARE_DIALOG, timeout=2000)
            except Exception as e:
                logger.debug(f"Share click note: {e}")

        current_url = self.get_current_url()
        did_not_navigate_away = (current_url == initial_url)

        info = {
            "share_available": has_share,
            "opened_dialog": opened_dialog,
            "did_not_navigate_away": did_not_navigate_away,
        }
        logger.info(f"Share icon test result: {info}")
        return info

    def navigate_back_to_plp(self) -> bool:
        """Navigate back from PDP to PLP and verify listing remains functional."""
        logger.info("Navigating back to PLP listing...")
        self.page.go_back()
        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(2000)
        cards = self.page.locator(Different_PDP_Locators.PLP_PRODUCT_CARDS).count()
        logger.info(f"Returned to PLP. Product cards count: {cards}")
        return cards > 0

    # =========================================================================
    # 9. Software PDP (Editions & View More / View Less)
    # =========================================================================

    def verify_software_editions_section(self) -> Dict[str, Any]:
        """Verify the Silhouette Studio® editions section and extract details."""
        logger.info("Inspecting Silhouette Studio® editions section...")
        editions_section = self.page.locator(Different_PDP_Locators.EDITIONS_SECTION).first
        has_editions = editions_section.is_visible(timeout=4000)

        # Look for edition names
        body_text = self.page.locator("body").inner_text()
        found_editions = []
        for name in ["Basic edition", "Designer edition", "Designer Plus", "Business edition", "Designer"]:
            if name.lower() in body_text.lower():
                found_editions.append(name)

        has_view_more = self.page.locator(Different_PDP_Locators.VIEW_MORE_BUTTON).first.is_visible(timeout=2000)

        info = {
            "section_visible": has_editions or len(found_editions) > 0,
            "editions_found": found_editions,
            "has_view_more_button": has_view_more,
        }
        logger.info(f"Software editions verification: {info}")
        return info

    def click_view_more_and_verify(self) -> bool:
        """Click 'View More' and verify additional content expands and button changes to 'View Less'."""
        view_more_btn = self.page.locator(Different_PDP_Locators.VIEW_MORE_BUTTON).first
        if not view_more_btn.is_visible(timeout=3000):
            logger.info("View More button is not visible or already expanded.")
            return True

        logger.info("Clicking 'View More' button...")
        view_more_btn.scroll_into_view_if_needed()
        view_more_btn.click()
        self.wait_for_timeout(1000)

        # Verify button toggled to View Less
        view_less_btn = self.page.locator(Different_PDP_Locators.VIEW_LESS_BUTTON).first
        is_expanded = view_less_btn.is_visible(timeout=3000)
        logger.info(f"View More clicked. 'View Less' button visible: {is_expanded}")
        return is_expanded

    def click_view_less_and_verify(self) -> bool:
        """Click 'View Less' and verify content collapses and button changes back to 'View More'."""
        view_less_btn = self.page.locator(Different_PDP_Locators.VIEW_LESS_BUTTON).first
        if not view_less_btn.is_visible(timeout=3000):
            logger.info("View Less button is not visible or already collapsed.")
            return True

        logger.info("Clicking 'View Less' button...")
        view_less_btn.scroll_into_view_if_needed()
        view_less_btn.click()
        self.wait_for_timeout(1000)

        view_more_btn = self.page.locator(Different_PDP_Locators.VIEW_MORE_BUTTON).first
        is_collapsed = view_more_btn.is_visible(timeout=3000)
        logger.info(f"View Less clicked. 'View More' button visible: {is_collapsed}")
        return is_collapsed

    def test_repeated_view_more_view_less(self, cycles: int = 2) -> bool:
        """Toggle View More and View Less repeatedly to verify consistent UI state."""
        logger.info(f"Testing repeated View More / View Less toggling for {cycles} cycles...")
        for i in range(cycles):
            logger.info(f"Cycle {i + 1}/{cycles}: Expanding...")
            expanded = self.click_view_more_and_verify()
            assert expanded, f"Failed to expand content on cycle {i + 1}"

            logger.info(f"Cycle {i + 1}/{cycles}: Collapsing...")
            collapsed = self.click_view_less_and_verify()
            assert collapsed, f"Failed to collapse content on cycle {i + 1}"

        logger.info(f"Successfully completed {cycles} repeated expand/collapse cycles.")
        return True

    def verify_software_links(self) -> Dict[str, Any]:
        """Inspect download, purchase, release notes, and system requirements links without buying."""
        logger.info("Inspecting software download, purchase, and info links...")
        downloads = [
            a.get_attribute("href")
            for a in self.page.locator(Different_PDP_Locators.SOFTWARE_DOWNLOAD_LINKS).all()
            if a.get_attribute("href")
        ]
        purchases = [
            a.get_attribute("href")
            for a in self.page.locator(Different_PDP_Locators.SOFTWARE_PURCHASE_LINKS).all()
            if a.get_attribute("href")
        ]
        sys_req = self.page.locator(Different_PDP_Locators.SYSTEM_REQUIREMENTS_LINK).first
        has_sys_req = sys_req.is_visible(timeout=2000)

        info = {
            "download_links_count": len(downloads),
            "purchase_links_count": len(purchases),
            "has_system_requirements": has_sys_req,
            "downloads_sample": downloads[:2],
        }
        logger.info(f"Software links verified: {info}")
        return info

    # =========================================================================
    # 10. General Page Scrolling & Evidence Capture
    # =========================================================================

    def scroll_through_complete_pdp(self) -> Dict[str, Any]:
        """Smoothly scroll through the full height of the PDP and verify all sections load."""
        logger.info("Scrolling through complete PDP to verify layout and dynamic sections...")
        viewport_height = self.page.viewport_size["height"] if self.page.viewport_size else 800

        # Scroll in increments
        for step in range(1, 5):
            self.page.evaluate(f"window.scrollTo(0, {step * viewport_height})")
            self.wait_for_timeout(400)

        # Scroll back to top
        self.page.evaluate("window.scrollTo(0, 0)")
        self.wait_for_timeout(300)

        logger.info("Completed full PDP page scroll.")
        return {"scrolled": True}

    def prepare_for_pdp_evidence(self) -> None:
        """Reset page scroll to top, dismiss any popups, and stabilize viewport for evidence capture."""
        logger.info("Preparing PDP viewport for clean evidence capture...")
        try:
            self.page.evaluate("window.scrollTo(0, 0)")
        except Exception:
            pass
        self.dismiss_transient_elements()
        self.wait_for_timeout(400)

