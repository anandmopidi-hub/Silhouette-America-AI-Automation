import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from config.config import Config
from locators.my_account_locators import MyAccountLocators
from pages.base_page import BasePage
from utils.logger import logger


class MyAccountPage(BasePage):
    """Page Object Model representing Silhouette America My Account module,
    covering Account Dashboard, Profile / Account Information, Address Book,
    My Orders, Software Licenses, Club Membership, Privacy & Data Rights,
    and My Wishlist.
    """

    def __init__(self, page: Page, config: Optional[Config] = None) -> None:
        super().__init__(page, config)

    # =========================================================================
    # Navigation & Section Access
    # =========================================================================

    def open_my_account(self) -> str:
        """Navigate to the main My Account Dashboard (/customer/account/)."""
        logger.info("Opening My Account dashboard: /customer/account/")
        self.goto("customer/account/", wait_until="domcontentloaded")
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()
        self.wait_for_dom_content_loaded()
        url = self.get_current_url()
        logger.info(f"My Account URL: {url}")
        return url

    def navigate_to_section(self, section_name: str) -> str:
        """Navigate to a specified My Account section using sidebar or direct route."""
        sec = section_name.strip().lower()
        logger.info(f"Navigating to My Account section: '{section_name}'")

        route_map = {
            "dashboard": "customer/account/",
            "profile": "customer/account/edit/",
            "edit": "customer/account/edit/",
            "address": "customer/address/",
            "address_book": "customer/address/",
            "orders": "sales/order/history/",
            "order_history": "sales/order/history/",
            "licenses": "downloadable/customer/products/",
            "software_licenses": "downloadable/customer/products/",
            "club": "clubsilhouette/customer/",
            "club_silhouette": "clubsilhouette/customer/",
            "privacy": "customer/account/",
            "wishlist": "wishlist/",
        }

        target_path = route_map.get(sec, "customer/account/")

        # Try clicking sidebar link first if visible on current page
        selector_map = {
            "dashboard": MyAccountLocators.NAV_DASHBOARD,
            "profile": MyAccountLocators.NAV_PROFILE,
            "edit": MyAccountLocators.NAV_PROFILE,
            "address": MyAccountLocators.NAV_ADDRESS_BOOK,
            "address_book": MyAccountLocators.NAV_ADDRESS_BOOK,
            "orders": MyAccountLocators.NAV_MY_ORDERS,
            "order_history": MyAccountLocators.NAV_MY_ORDERS,
            "licenses": MyAccountLocators.NAV_SOFTWARE_LICENSES,
            "software_licenses": MyAccountLocators.NAV_SOFTWARE_LICENSES,
            "club": MyAccountLocators.NAV_CLUB_MEMBERSHIP,
            "club_silhouette": MyAccountLocators.NAV_CLUB_MEMBERSHIP,
            "privacy": MyAccountLocators.NAV_PRIVACY_DATA,
            "wishlist": MyAccountLocators.NAV_WISHLIST,
        }

        nav_sel = selector_map.get(sec)
        clicked = False
        if nav_sel:
            try:
                link = self.page.locator(nav_sel).first
                if link.is_visible(timeout=2000):
                    link.click()
                    self.wait_for_dom_content_loaded()
                    self.dismiss_cookie_consent_if_present()
                    clicked = True
            except Exception as e:
                logger.debug(f"Sidebar click notice: {e}, falling back to direct route")

        if not clicked:
            self.goto(target_path, wait_until="domcontentloaded")
            self.handle_cloudflare_if_present()
            self.dismiss_cookie_consent_if_present()
            self.ensure_minicart_closed()
            self.wait_for_dom_content_loaded()

        return self.get_current_url()

    # =========================================================================
    # 1. Account Dashboard (E2E-ACC-001)
    # =========================================================================

    def is_dashboard_loaded(self, timeout_ms: int = 10000) -> bool:
        """Verify if the My Account dashboard has successfully loaded."""
        try:
            heading = self.page.locator(MyAccountLocators.DASHBOARD_PAGE_TITLE).first
            heading.wait_for(state="visible", timeout=timeout_ms)
            title_text = heading.inner_text().strip()
            logger.info(f"Dashboard heading text: '{title_text}'")
            return "account" in title_text.lower() or "silhouette" in self.get_title().lower()
        except Exception as e:
            logger.debug(f"Dashboard heading wait notice: {e}")
            return "/customer/account" in self.get_current_url()

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Extract summary information from the account dashboard blocks."""
        summary = {
            "title": self.get_title(),
            "url": self.get_current_url(),
            "has_account_info": False,
            "has_address_book": False,
            "has_recent_orders": False,
            "contact_info_text": "",
        }

        try:
            info_block = self.page.locator(MyAccountLocators.DASHBOARD_INFO_BLOCK).first
            if info_block.is_visible(timeout=2000):
                summary["has_account_info"] = True
                summary["contact_info_text"] = info_block.inner_text().strip().replace("\n", " ")
        except Exception:
            pass

        try:
            addr_block = self.page.locator(MyAccountLocators.DASHBOARD_ADDRESSES_BLOCK).first
            if addr_block.is_visible(timeout=2000):
                summary["has_address_book"] = True
        except Exception:
            pass

        try:
            orders_block = self.page.locator(MyAccountLocators.DASHBOARD_ORDERS_BLOCK).first
            if orders_block.is_visible(timeout=2000):
                summary["has_recent_orders"] = True
        except Exception:
            pass

        logger.info(f"Dashboard summary: {summary}")
        return summary

    # =========================================================================
    # 2. Profile & Account Information (E2E-ACC-002, E2E-ACC-003)
    # =========================================================================

    def navigate_to_profile(self) -> str:
        """Navigate to Edit Profile / Account Information page."""
        return self.navigate_to_section("profile")

    def get_profile_data(self) -> Dict[str, str]:
        """Read and return current profile form input values."""
        if "customer/account/edit" not in self.page.url:
            self.navigate_to_profile()
        self.page.wait_for_selector(MyAccountLocators.PROFILE_FIRSTNAME_INPUT, state="visible", timeout=10000)
        fn_val = self.page.locator(MyAccountLocators.PROFILE_FIRSTNAME_INPUT).first.input_value().strip()
        ln_val = self.page.locator(MyAccountLocators.PROFILE_LASTNAME_INPUT).first.input_value().strip()
        em_val = ""
        em_inp = self.page.locator(MyAccountLocators.PROFILE_EMAIL_INPUT).first
        if em_inp.is_visible(timeout=1000):
            em_val = em_inp.input_value().strip()

        data = {"firstname": fn_val, "lastname": ln_val, "email": em_val}
        logger.info(f"Captured current profile values: {data}")
        return data

    def update_profile(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        save: bool = True,
    ) -> None:
        """Update profile fields with specified values and submit."""
        logger.info(f"Updating profile: first_name='{first_name}', last_name='{last_name}'")
        self.page.wait_for_selector(MyAccountLocators.PROFILE_FIRSTNAME_INPUT, state="visible", timeout=10000)

        if first_name is not None:
            fn = self.page.locator(MyAccountLocators.PROFILE_FIRSTNAME_INPUT).first
            fn.click()
            fn.fill(first_name)

        if last_name is not None:
            ln = self.page.locator(MyAccountLocators.PROFILE_LASTNAME_INPUT).first
            ln.click()
            ln.fill(last_name)

        if save:
            save_btn = self.page.locator(MyAccountLocators.PROFILE_SAVE_BUTTON).first
            save_btn.click()
            self.wait_for_dom_content_loaded()
            self.wait_for_timeout(2000)

    def get_profile_success_message(self, timeout_ms: int = 5000) -> str:
        """Retrieve profile update success message."""
        try:
            msg_loc = self.page.locator(MyAccountLocators.PROFILE_SUCCESS_MESSAGE).first
            msg_loc.wait_for(state="visible", timeout=timeout_ms)
            return msg_loc.inner_text().strip()
        except Exception:
            return ""

    def get_profile_validation_errors(self) -> List[str]:
        """Retrieve all visible client-side or server-side validation error messages."""
        errors: List[str] = []
        loc = self.page.locator(MyAccountLocators.ALL_FIELD_ERRORS)
        try:
            count = loc.count()
            for i in range(count):
                txt = loc.nth(i).inner_text().strip()
                if txt and txt not in errors:
                    errors.append(txt)
        except Exception:
            pass
        logger.info(f"Profile validation errors found: {errors}")
        return errors

    # =========================================================================
    # 3. Address Book (E2E-ACC-004 to E2E-ACC-008)
    # =========================================================================

    def navigate_to_address_book(self) -> str:
        """Navigate to Address Book page."""
        logger.info("Navigating directly to Address Book...")
        self.goto("customer/address/", wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.dismiss_cookie_consent_if_present()
        return self.get_current_url()

    def open_add_address_form(self) -> None:
        """Click the 'Add new address' button to open the form."""
        logger.info("Opening Add New Address form...")
        btn = self.page.locator(MyAccountLocators.ADD_NEW_ADDRESS_BUTTON).first
        if btn.is_visible(timeout=5000):
            btn.click()
            self.wait_for_dom_content_loaded()
            self.wait_for_timeout(1000)
        else:
            self.goto("customer/address/new/", wait_until="domcontentloaded")
            self.wait_for_dom_content_loaded()

    def fill_address_form(
        self,
        address_data: Dict[str, Any],
        set_default_shipping: bool = False,
        set_default_billing: bool = False,
    ) -> None:
        """Fill address form fields using verified DOM locators.
        Handles First Name, Last Name, Phone, Street Line 1, Street Line 2,
        City, State/Province, ZIP/Postal Code, Country, and default address flags.
        """
        logger.info(f"Filling address form: {address_data}")
        self.page.wait_for_selector(MyAccountLocators.ADDRESS_FORM, state="visible", timeout=10000)

        # 1. First Name & Last Name
        if "firstname" in address_data:
            fn = self.page.locator(MyAccountLocators.ADDR_FIRSTNAME).first
            if fn.is_visible(timeout=2000):
                fn.fill(address_data["firstname"])
        if "lastname" in address_data:
            ln = self.page.locator(MyAccountLocators.ADDR_LASTNAME).first
            if ln.is_visible(timeout=2000):
                ln.fill(address_data["lastname"])

        # 2. Telephone
        if "telephone" in address_data:
            phone = self.page.locator(MyAccountLocators.ADDR_TELEPHONE).first
            if phone.is_visible(timeout=2000):
                phone.fill(address_data["telephone"])

        # 3. Street Address Line 1 & Line 2
        if "street_0" in address_data:
            s0 = self.page.locator(MyAccountLocators.ADDR_STREET_0).first
            if s0.is_visible(timeout=2000):
                s0.fill(address_data["street_0"])
        if "street_1" in address_data:
            s1 = self.page.locator(MyAccountLocators.ADDR_STREET_1).first
            if s1.is_visible(timeout=2000):
                s1.fill(address_data["street_1"])

        # 4. Country (select dropdown)
        country_name = address_data.get("country", "United States")
        country_sel = self.page.locator(MyAccountLocators.ADDR_COUNTRY).first
        if country_sel.is_visible(timeout=2000):
            current_val = country_sel.input_value()
            if current_val != "US" and "united states" not in current_val.lower():
                try:
                    country_sel.select_option(label=country_name)
                except Exception:
                    try:
                        country_sel.select_option(value="US")
                    except Exception:
                        pass
                self.wait_for_timeout(800)

        # 5. State / Province (select dropdown or text input)
        if "region" in address_data:
            reg_val = address_data["region"]
            reg_sel = self.page.locator(MyAccountLocators.ADDR_REGION_SELECT).first
            if reg_sel.is_visible(timeout=2000):
                try:
                    reg_sel.select_option(label=reg_val)
                except Exception:
                    options = reg_sel.locator("option").all()
                    for opt in options:
                        if reg_val.lower() in opt.inner_text().lower():
                            opt_val = opt.get_attribute("value")
                            if opt_val:
                                reg_sel.select_option(value=opt_val)
                                break
            else:
                reg_inp = self.page.locator(MyAccountLocators.ADDR_REGION_INPUT).first
                if reg_inp.is_visible(timeout=1000):
                    reg_inp.fill(reg_val)

        # 6. City
        if "city" in address_data:
            city = self.page.locator(MyAccountLocators.ADDR_CITY).first
            if city.is_visible(timeout=2000):
                city.fill(address_data["city"])

        # 7. ZIP / Postcode
        if "postcode" in address_data:
            zip_el = self.page.locator(MyAccountLocators.ADDR_POSTCODE).first
            if zip_el.is_visible(timeout=2000):
                zip_el.fill(address_data["postcode"])

        # 8. Default shipping checkbox
        should_default_ship = set_default_shipping or bool(address_data.get("default_shipping"))
        if should_default_ship:
            self.set_default_shipping_checkbox(True)

        # 9. Default billing checkbox
        should_default_bill = set_default_billing or bool(address_data.get("default_billing"))
        if should_default_bill:
            cb_bill = self.page.locator(MyAccountLocators.ADDR_DEFAULT_BILLING).first
            if cb_bill.is_visible(timeout=2000):
                try:
                    if not cb_bill.is_checked():
                        cb_bill.check()
                except Exception:
                    cb_bill.click()

    def is_default_shipping_selected(self) -> bool:
        """Check if 'Use as my default shipping address' checkbox is currently selected."""
        cb = self.page.locator(MyAccountLocators.ADDR_DEFAULT_SHIPPING).first
        if cb.is_visible(timeout=2000):
            return cb.is_checked()
        # Fallback input query
        inp = self.page.locator("input#primary_shipping, input[name='default_shipping']").first
        if inp.count() > 0:
            return inp.is_checked()
        return False

    def set_default_shipping_checkbox(self, check: bool = True) -> bool:
        """Set the 'Use as my default shipping address' checkbox state."""
        logger.info(f"Setting default shipping checkbox to: {check}")
        cb = self.page.locator(MyAccountLocators.ADDR_DEFAULT_SHIPPING).first
        if cb.is_visible(timeout=2000):
            if cb.is_checked() != check:
                try:
                    cb.set_checked(check)
                except Exception:
                    cb.click()
            return cb.is_checked()

        # Try clicking associated label
        ship_label = self.page.locator("label[for='primary_shipping'], label:has-text('default shipping')").first
        if ship_label.is_visible(timeout=2000):
            ship_label.click()
            self.wait_for_timeout(300)
        return self.is_default_shipping_selected()

    def submit_address_form(self) -> str:
        """Submit the address form, wait for save to complete, and return success message."""
        logger.info("Submitting address form...")
        save_btn = self.page.locator(MyAccountLocators.ADDR_SAVE_BUTTON).first
        assert save_btn.is_visible(timeout=5000), "Save Address button not visible on form."
        save_btn.click()

        # Wait for save operation to complete (success alert appears or URL redirects)
        success_msg = ""
        try:
            msg_loc = self.page.locator(MyAccountLocators.ADDRESS_SUCCESS_MESSAGE).first
            msg_loc.wait_for(state="visible", timeout=12000)
            success_msg = msg_loc.inner_text().strip()
            logger.info(f"Address save confirmed with message: '{success_msg}'")
        except Exception:
            pass

        # Ensure redirect completes away from /new/ or /edit/ to listing page
        try:
            self.page.wait_for_function(
                "() => !window.location.href.includes('/new') && !window.location.href.includes('/edit')",
                timeout=10000,
            )
        except Exception:
            pass

        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(1000)
        return success_msg

    def get_address_success_message(self, timeout_ms: int = 5000) -> str:
        """Retrieve the address save/delete success message."""
        try:
            msg_loc = self.page.locator(MyAccountLocators.ADDRESS_SUCCESS_MESSAGE).first
            msg_loc.wait_for(state="visible", timeout=timeout_ms)
            return msg_loc.inner_text().strip()
        except Exception:
            return ""

    def get_all_addresses(self) -> List[str]:
        """Return text representation of all addresses listed in Address Book
        including Default Billing, Default Shipping, and Additional Addresses.
        """
        addresses: List[str] = []

        # 1. Default Billing
        billing = self.page.locator(MyAccountLocators.DEFAULT_BILLING_BOX).first
        if billing.is_visible(timeout=1000):
            addresses.append(billing.inner_text().strip().replace("\n", " "))

        # 2. Default Shipping
        shipping = self.page.locator(MyAccountLocators.DEFAULT_SHIPPING_BOX).first
        if shipping.is_visible(timeout=1000):
            addresses.append(shipping.inner_text().strip().replace("\n", " "))

        # 3. Additional Address cards
        cards = self.page.locator(MyAccountLocators.ADDITIONAL_ADDRESS_CARDS)
        count = cards.count()
        for i in range(count):
            txt = cards.nth(i).inner_text().strip().replace("\n", " ")
            if txt and txt not in addresses:
                addresses.append(txt)

        # 4. Fallback: also include main address container text
        main_content = self.page.locator(".column.main, #maincontent").first
        if main_content.is_visible(timeout=1000):
            full_txt = main_content.inner_text().strip().replace("\n", " ")
            if full_txt and full_txt not in addresses:
                addresses.append(full_txt)

        logger.info(f"Discovered {len(addresses)} address blocks in Address Book.")
        return addresses

    def is_address_present_in_book(self, keyword: str) -> bool:
        """Check whether an address matching keyword is present anywhere in Address Book."""
        curr_url = self.get_current_url()
        if "/customer/address/" not in curr_url or "/new" in curr_url or "/edit" in curr_url:
            self.navigate_to_address_book()

        addresses = self.get_all_addresses()
        kw = keyword.strip().lower()
        if any(kw in a.lower() for a in addresses):
            return True
        try:
            return kw in self.page.locator("#maincontent, .column.main, body").first.inner_text().lower()
        except Exception:
            return False

    def get_default_shipping_address(self) -> str:
        """Retrieve the text of the default shipping address block."""
        box = self.page.locator(MyAccountLocators.DEFAULT_SHIPPING_BOX).first
        if box.is_visible(timeout=3000):
            return box.inner_text().strip().replace("\n", " ")
        return ""

    def get_address_validation_errors(self) -> List[str]:
        """Return all visible validation errors on the address form."""
        errors: List[str] = []
        loc = self.page.locator(MyAccountLocators.ADDR_REQUIRED_ERRORS)
        try:
            count = loc.count()
            for i in range(count):
                txt = loc.nth(i).inner_text().strip()
                if txt and txt not in errors:
                    errors.append(txt)
        except Exception:
            pass
        return errors

    def edit_address_by_keyword(self, keyword: str, updated_data: Dict[str, Any]) -> bool:
        """Locate an address card containing keyword, click Edit, update fields, and save."""
        logger.info(f"Editing address matching keyword: '{keyword}'")
        cards = self.page.locator(MyAccountLocators.ADDITIONAL_ADDRESS_CARDS)
        count = cards.count()
        target_card: Optional[Locator] = None
        initial_match_count = 0

        for i in range(count):
            c = cards.nth(i)
            if keyword.lower() in c.inner_text().lower():
                initial_match_count += 1
                if not target_card:
                    target_card = c

        if not target_card:
            for box_loc in [MyAccountLocators.DEFAULT_SHIPPING_BOX, MyAccountLocators.DEFAULT_BILLING_BOX]:
                box = self.page.locator(box_loc).first
                if box.is_visible(timeout=1000) and keyword.lower() in box.inner_text().lower():
                    target_card = box
                    break

        if not target_card:
            fallback = self.page.locator(f".add-entry:has-text('{keyword}')").first
            if fallback.is_visible(timeout=1000):
                target_card = fallback

        if not target_card:
            logger.warning(f"Address matching keyword '{keyword}' not found for editing.")
            return False

        edit_link = target_card.locator(MyAccountLocators.ADDRESS_EDIT_LINK).first
        if not edit_link.is_visible(timeout=3000):
            logger.warning(f"Edit link not found on address card for '{keyword}'.")
            return False

        edit_link.click()
        try:
            self.page.wait_for_url("**/customer/address/edit/**", timeout=10000)
        except Exception:
            pass
        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(1000)

        self.fill_address_form(updated_data)
        self.submit_address_form()
        return True

    def delete_additional_address(self, keyword: str) -> Dict[str, Any]:
        """Delete an automation-created address from the Additional Addresses section.
        Flow:
        1. Locate the card under Additional Addresses matching keyword.
        2. Click the Delete icon (✕) on that card.
        3. Verify the delete confirmation popup appears.
        4. Click the confirmation popup's OK button.
        5. Wait for deletion to complete and capture the success message.
        6. Verify the address is no longer displayed in Additional Addresses.
        """
        logger.info(f"Deleting additional test address matching keyword: '{keyword}'")
        assert "[TEST_AUTO]" in keyword, "Safety check: only automation test addresses can be deleted."

        cards = self.page.locator(MyAccountLocators.ADDITIONAL_ADDRESS_CARDS)
        count = cards.count()
        target_card: Optional[Locator] = None
        initial_match_count = 0

        for i in range(count):
            c = cards.nth(i)
            if keyword.lower() in c.inner_text().lower():
                initial_match_count += 1
                if not target_card:
                    target_card = c

        if not target_card:
            fallback = self.page.locator(f".add-entry:has-text('{keyword}')").first
            if fallback.is_visible(timeout=2000):
                target_card = fallback

        if not target_card:
            logger.warning(f"No additional address found matching '{keyword}'.")
            return {"deleted": False, "message": "Address not found", "still_present": True}

        # Click the delete button / icon on that card
        del_btn = target_card.locator(MyAccountLocators.ADDRESS_DELETE_BUTTON).first
        assert del_btn.is_visible(timeout=3000), f"Delete icon not visible on card for '{keyword}'."
        del_btn.click()
        self.wait_for_timeout(800)

        # Verify confirmation popup appears and click OK
        ok_btn = self.page.locator(MyAccountLocators.DELETE_CONFIRM_OK).first
        if ok_btn.is_visible(timeout=5000):
            ok_btn.click()
            logger.info("Clicked OK on delete confirmation modal.")
        else:
            modal = self.page.locator(MyAccountLocators.DELETE_CONFIRM_MODAL).first
            if modal.is_visible(timeout=2000):
                modal_ok = modal.locator("button:has-text('OK'), button.action-accept").first
                if modal_ok.is_visible(timeout=2000):
                    modal_ok.click()

        # Wait for deletion operation to complete
        try:
            self.page.wait_for_url("**/customer/address/**", timeout=10000)
        except Exception:
            pass

        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(2000)

        success_msg = self.get_address_success_message()
        try:
            msg_loc = self.page.locator(MyAccountLocators.ADDRESS_SUCCESS_MESSAGE).first
            msg_loc.wait_for(state="visible", timeout=10000)
            success_msg = msg_loc.inner_text().strip()
            logger.info(f"Deletion confirmed with success message: '{success_msg}'")
        except Exception:
            pass

        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(1500)

        # Verify deletion via success message and reduced card count
        new_cards = self.page.locator(MyAccountLocators.ADDITIONAL_ADDRESS_CARDS)
        final_match_count = sum(1 for i in range(new_cards.count()) if keyword.lower() in new_cards.nth(i).inner_text().lower())
        has_delete_msg = "deleted" in success_msg.lower() or "saved" in success_msg.lower()
        deleted = has_delete_msg or (final_match_count < initial_match_count)
        still_present = (final_match_count >= initial_match_count) and not has_delete_msg
        logger.info(f"Post-deletion check: initial={initial_match_count}, final={final_match_count}, has_msg={has_delete_msg}, still_present={still_present}")

        return {
            "deleted": deleted,
            "success_message": success_msg,
            "still_present": still_present,
        }

    def is_address_present_in_additional(self, keyword: str) -> bool:
        """Check whether keyword exists inside any Additional Address card."""
        cards = self.page.locator(MyAccountLocators.ADDITIONAL_ADDRESS_CARDS)
        count = cards.count()
        for i in range(count):
            if keyword.lower() in cards.nth(i).inner_text().lower():
                return True
        return False

    # =========================================================================
    # 4. My Orders & Order Details (E2E-ACC-009, E2E-ACC-010)
    # =========================================================================

    def navigate_to_orders(self) -> str:
        """Navigate to My Orders (/sales/order/history/)."""
        return self.navigate_to_section("orders")

    def get_order_history_rows(self) -> List[Dict[str, Any]]:
        """Extract all visible order records from the orders history table."""
        logger.info("Extracting orders history from table...")
        orders: List[Dict[str, Any]] = []

        try:
            self.page.wait_for_selector(MyAccountLocators.ORDERS_TABLE, state="visible", timeout=8000)
        except Exception:
            logger.info("Orders table not visible or customer has no orders yet.")
            return orders

        rows = self.page.locator(MyAccountLocators.ORDERS_ROWS)
        count = rows.count()
        for i in range(count):
            r = rows.nth(i)
            try:
                order_id_el = r.locator(MyAccountLocators.ORDER_COL_ID).first
                date_el = r.locator(MyAccountLocators.ORDER_COL_DATE).first
                total_el = r.locator(MyAccountLocators.ORDER_COL_TOTAL).first
                status_el = r.locator(MyAccountLocators.ORDER_COL_STATUS).first
                view_link = r.locator(MyAccountLocators.ORDER_VIEW_LINK).first

                order_id = order_id_el.inner_text().strip() if order_id_el.is_visible(timeout=500) else ""
                order_date = date_el.inner_text().strip() if date_el.is_visible(timeout=500) else ""
                order_total = total_el.inner_text().strip() if total_el.is_visible(timeout=500) else ""
                order_status = status_el.inner_text().strip() if status_el.is_visible(timeout=500) else ""
                view_url = view_link.get_attribute("href") if view_link.is_visible(timeout=500) else ""

                if order_id or order_total:
                    orders.append({
                        "index": i,
                        "order_id": order_id,
                        "date": order_date,
                        "total": order_total,
                        "status": order_status,
                        "view_url": view_url,
                    })
            except Exception as e:
                logger.debug(f"Row {i} extract notice: {e}")

        logger.info(f"Retrieved {len(orders)} orders from history.")
        return orders

    def open_order_details(self, order_index: int = 0) -> Dict[str, Any]:
        """Open order details by clicking 'View Order' on the specified row."""
        logger.info(f"Opening order details for order row index: {order_index}")
        orders = self.get_order_history_rows()
        if not orders or order_index >= len(orders):
            raise IndexError(f"Order index {order_index} out of range (found {len(orders)} orders).")

        target_order = orders[order_index]
        rows = self.page.locator(MyAccountLocators.ORDERS_ROWS)
        view_link = rows.nth(order_index).locator(MyAccountLocators.ORDER_VIEW_LINK).first

        if view_link.is_visible(timeout=3000):
            view_link.click()
        elif target_order.get("view_url"):
            self.goto(target_order["view_url"], wait_until="domcontentloaded")
        else:
            raise RuntimeError(f"Could not open view link for order {target_order}")

        self.wait_for_dom_content_loaded()
        self.wait_for_timeout(2000)
        return target_order

    def get_order_details_info(self) -> Dict[str, Any]:
        """Extract details from the currently opened Order Details page."""
        details: Dict[str, Any] = {
            "title": self.get_title(),
            "url": self.get_current_url(),
            "status": "",
            "date": "",
            "items": [],
            "grand_total": "",
        }

        # Status
        status_loc = self.page.locator(MyAccountLocators.ORDER_DETAILS_STATUS).first
        if status_loc.is_visible(timeout=2000):
            details["status"] = status_loc.inner_text().strip()

        # Date
        date_loc = self.page.locator(MyAccountLocators.ORDER_DETAILS_DATE).first
        if date_loc.is_visible(timeout=2000):
            details["date"] = date_loc.inner_text().strip()

        # Grand Total
        total_loc = self.page.locator(MyAccountLocators.ORDER_DETAILS_GRAND_TOTAL).first
        if total_loc.is_visible(timeout=2000):
            details["grand_total"] = total_loc.inner_text().strip()

        # Ordered items
        item_rows = self.page.locator(MyAccountLocators.ORDER_DETAILS_ITEMS_ROWS)
        count = item_rows.count()
        for i in range(count):
            r = item_rows.nth(i)
            name_el = r.locator(MyAccountLocators.ORDER_DETAILS_PRODUCT_NAME).first
            if name_el.is_visible(timeout=500):
                details["items"].append(name_el.inner_text().strip())

        logger.info(f"Captured Order Details: {details}")
        return details

    # =========================================================================
    # 5. Software Licenses (E2E-ACC-011)
    # =========================================================================

    def navigate_to_software_licenses(self) -> str:
        """Navigate to Software Licenses section."""
        return self.navigate_to_section("software_licenses")

    def get_software_licenses(self) -> List[Dict[str, str]]:
        """Retrieve software licenses/downloadable products, masking sensitive keys."""
        licenses: List[Dict[str, str]] = []
        try:
            self.page.wait_for_selector(MyAccountLocators.LICENSES_TABLE, state="visible", timeout=6000)
        except Exception:
            logger.info("Software licenses table not visible or no downloadable items exist.")
            return licenses

        rows = self.page.locator(MyAccountLocators.LICENSES_ROWS)
        count = rows.count()
        for i in range(count):
            r = rows.nth(i)
            title_el = r.locator(MyAccountLocators.LICENSES_COL_TITLE).first
            status_el = r.locator(MyAccountLocators.LICENSES_COL_STATUS).first

            title = title_el.inner_text().strip() if title_el.is_visible(timeout=500) else ""
            status = status_el.inner_text().strip() if status_el.is_visible(timeout=500) else ""

            if title:
                masked_title = re.sub(r"([A-Z0-9]{4}-){3}[A-Z0-9]{4}", "****-****-****-****", title)
                licenses.append({"product": masked_title, "status": status})

        logger.info(f"Found {len(licenses)} software license entries.")
        return licenses

    # =========================================================================
    # 6. Club Membership (E2E-ACC-012)
    # =========================================================================

    def navigate_to_club_membership(self) -> str:
        """Navigate to Club Silhouette membership section."""
        return self.navigate_to_section("club_silhouette")

    def get_club_membership_details(self) -> Dict[str, Any]:
        """Extract membership status, benefits, and banner details."""
        info: Dict[str, Any] = {
            "title": self.get_title(),
            "url": self.get_current_url(),
            "has_banner": False,
            "benefits": [],
            "status_text": "",
        }

        banner = self.page.locator(MyAccountLocators.CLUB_BANNER).first
        if banner.is_visible(timeout=3000):
            info["has_banner"] = True
            info["status_text"] = banner.inner_text().strip().replace("\n", " ")

        benefits = self.page.locator(MyAccountLocators.CLUB_BENEFITS_LIST)
        count = benefits.count()
        for i in range(count):
            b_text = benefits.nth(i).inner_text().strip()
            if b_text and b_text not in info["benefits"]:
                info["benefits"].append(b_text)

        logger.info(f"Captured Club Membership info: {info}")
        return info

    def is_club_silhouette_title_visible(self) -> bool:
        """Verify whether the 'Club Silhouette' title is visible on the page."""
        title_loc = self.page.locator(MyAccountLocators.CLUB_PAGE_TITLE).first
        if title_loc.is_visible(timeout=5000):
            txt = title_loc.inner_text().strip()
            logger.info(f"Club Membership heading: '{txt}'")
            return "club silhouette" in txt.lower()

        # Fallback to page title or content check
        page_title = self.get_title().lower()
        if "club silhouette" in page_title:
            return True
        try:
            h_elements = self.page.locator("h1, h2, h3, .page-title, .title, strong").all()
            for h in h_elements:
                if "club silhouette" in h.inner_text().lower():
                    return True
        except Exception:
            pass
        return False

    # =========================================================================
    # 7. Privacy & Data Rights (E2E-ACC-013, E2E-ACC-014)
    # =========================================================================

    def navigate_to_privacy(self) -> str:
        """Navigate to Privacy & Data Rights section."""
        return self.navigate_to_section("privacy")

    def download_personal_data(self, password: str, download_dir: Optional[Path] = None) -> Optional[Path]:
        """Trigger Personal Data download with password verification via Playwright download event."""
        logger.info("Attempting Personal Data download...")
        pwd_inp = self.page.locator(MyAccountLocators.PRIVACY_PASSWORD_INPUT).first
        if pwd_inp.is_visible(timeout=3000):
            pwd_inp.fill(password)

        dl_btn = self.page.locator(MyAccountLocators.DOWNLOAD_DATA_BUTTON).first
        if not dl_btn.is_visible(timeout=3000):
            logger.warning("Download Personal Data button not visible.")
            return None

        with self.page.expect_download(timeout=15000) as download_info:
            dl_btn.click()

        download = download_info.value
        dest_dir = download_dir or Path(self.config.artifacts_dir if hasattr(self.config, "artifacts_dir") else "artifacts")
        dest_path = dest_dir / download.suggested_filename
        download.save_as(str(dest_path))
        logger.info(f"Successfully downloaded personal data to: {dest_path}")
        return dest_path

    def get_privacy_preference_state(self) -> Dict[str, Any]:
        """Inspect 'Don't Sell or Share My Personal Information' preference state."""
        state = {"is_visible": False, "is_checked": False}
        cb = self.page.locator(MyAccountLocators.DONT_SELL_SHARE_CHECKBOX).first
        if cb.is_visible(timeout=2000):
            state["is_visible"] = True
            state["is_checked"] = cb.is_checked()
        return state

    def save_privacy_preference(self, checked: bool = True, password: Optional[str] = None) -> str:
        """Save the 'Don't Sell or Share My Personal Information' preference."""
        logger.info(f"Setting privacy preference to {checked}...")
        cb = self.page.locator(MyAccountLocators.DONT_SELL_SHARE_CHECKBOX).first
        if cb.is_visible(timeout=2000):
            if cb.is_checked() != checked:
                cb.set_checked(checked)

        if password:
            pwd_inp = self.page.locator(MyAccountLocators.PRIVACY_PASSWORD_INPUT).first
            if pwd_inp.is_visible(timeout=1000):
                pwd_inp.fill(password)

        save_btn = self.page.locator(MyAccountLocators.SAVE_PRIVACY_BUTTON).first
        if save_btn.is_visible(timeout=2000):
            save_btn.click()
            self.wait_for_dom_content_loaded()
            self.wait_for_timeout(2000)

        conf_msg = self.page.locator(MyAccountLocators.PRIVACY_CONFIRMATION_MESSAGE).first
        return conf_msg.inner_text().strip() if conf_msg.is_visible(timeout=3000) else ""

    # =========================================================================
    # 8. My Wishlist (E2E-ACC-015)
    # =========================================================================

    def navigate_to_wishlist(self) -> str:
        """Navigate to My Wishlist (/wishlist/)."""
        return self.navigate_to_section("wishlist")

    def get_wishlist_items(self) -> List[Dict[str, str]]:
        """Retrieve all items currently in customer Wishlist."""
        items: List[Dict[str, str]] = []
        item_loc = self.page.locator(MyAccountLocators.WISHLIST_ITEMS)
        try:
            count = item_loc.count()
            for i in range(count):
                it = item_loc.nth(i)
                name_el = it.locator(MyAccountLocators.WISHLIST_ITEM_NAME).first
                price_el = it.locator(MyAccountLocators.WISHLIST_ITEM_PRICE).first
                name = name_el.inner_text().strip() if name_el.is_visible(timeout=500) else ""
                url = name_el.get_attribute("href") or ""
                price = price_el.inner_text().strip() if price_el.is_visible(timeout=500) else ""
                if name:
                    items.append({"name": name, "price": price, "url": url})
        except Exception:
            pass
        logger.info(f"Retrieved {len(items)} wishlist items: {items}")
        return items

    def open_product_pdp(self, shop_url: str = "accessories", product_index: int = 0) -> Dict[str, str]:
        """Navigate to shop/catalog page, dynamically select the product at product_index,
        open its PDP, and return captured product metadata (name, price, url).
        """
        logger.info(f"Navigating to shop/catalog page: '{shop_url}'")
        self.goto(shop_url, wait_until="domcontentloaded")
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.ensure_minicart_closed()

        product_links = self.page.locator(MyAccountLocators.CATALOG_PRODUCT_LINKS)
        if product_links.count() == 0:
            logger.info("No direct product links on current page; falling back to 'accessories' listing...")
            self.goto("accessories", wait_until="domcontentloaded")
            self.handle_cloudflare_if_present()
            self.dismiss_cookie_consent_if_present()
            product_links = self.page.locator(MyAccountLocators.CATALOG_PRODUCT_LINKS)

        count = product_links.count()
        assert count > 0, "No products found on shop/catalog page."

        # Collect distinct visible product link elements to ensure distinct product selection
        distinct_links = []
        seen_hrefs = set()
        for i in range(count):
            pl = product_links.nth(i)
            if pl.is_visible(timeout=500):
                href = pl.get_attribute("href") or ""
                if href and href not in seen_hrefs and not any(k in href for k in ["#", "javascript", "checkout", "cart", "customer"]):
                    seen_hrefs.add(href)
                    distinct_links.append(pl)

        assert len(distinct_links) > 0, "No visible distinct product links found."
        target_idx = product_index if product_index < len(distinct_links) else 0
        target_link = distinct_links[target_idx]
        target_href = target_link.get_attribute("href") or ""
        catalog_name = target_link.inner_text().strip()
        logger.info(f"Opening product PDP index {target_idx}: '{target_href}' (catalog title: '{catalog_name}')")

        target_link.click()
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()

        # Wait for PDP to load and capture actual product name
        self.page.wait_for_selector(MyAccountLocators.PDP_TITLE, state="visible", timeout=12000)
        product_title_el = self.page.locator(MyAccountLocators.PDP_TITLE).first
        pdp_name = product_title_el.inner_text().strip()
        product_name = catalog_name if catalog_name else pdp_name
        logger.info(f"Captured product name: '{product_name}' (PDP: '{pdp_name}')")
        assert product_name, "Failed to capture product name from PDP."

        # Capture price if visible
        price_el = self.page.locator(MyAccountLocators.PDP_PRICE).first
        product_price = price_el.inner_text().strip() if price_el.is_visible(timeout=1500) else ""

        return {
            "name": product_name,
            "catalog_name": catalog_name,
            "pdp_name": pdp_name,
            "price": product_price,
            "url": self.get_current_url(),
        }

    def click_pdp_wishlist_button(self, ensure_added: bool = False) -> None:
        """Locate and click the Wishlist heart icon on the active PDP.
        If ensure_added is True and the product already has 'already-in-wishlist' class,
        skips click to prevent untoggling/removing the item.
        """
        self.page.wait_for_selector(MyAccountLocators.PDP_WISHLIST_BUTTON, state="visible", timeout=12000)
        wishlist_btn = self.page.locator(MyAccountLocators.PDP_WISHLIST_BUTTON).first
        assert wishlist_btn.is_visible(timeout=8000), "Wishlist button not found on PDP."
        btn_class = wishlist_btn.get_attribute("class") or ""

        if ensure_added and "already-in-wishlist" in btn_class:
            logger.info("Product already has 'already-in-wishlist' class; preserving wishlist state.")
            return

        logger.info("Clicking Wishlist button on PDP...")
        wishlist_btn.click()

    def add_pdp_product_to_wishlist(
        self, shop_url: str = "accessories", product_index: int = 0, ensure_added: bool = True
    ) -> Dict[str, str]:
        """Navigate to shop/catalog/category, dynamically select an in-stock product,
        open its PDP, capture its details, click the PDP Wishlist button, and wait
        for the wishlist action to complete.
        """
        product_info = self.open_product_pdp(shop_url=shop_url, product_index=product_index)
        self.click_pdp_wishlist_button(ensure_added=ensure_added)

        # Wait for the Wishlist action to complete (redirect to /wishlist/ or AJAX confirmation)
        try:
            self.page.wait_for_url("**/wishlist/**", timeout=6000)
            self.wait_for_dom_content_loaded()
            logger.info("Redirected to Wishlist page after clicking Add to Wishlist.")
        except Exception:
            self.wait_for_timeout(2500)

        return product_info

    def is_wishlist_auth_popup_visible(self, timeout_ms: int = 5000) -> bool:
        """Verify if the Sign In authentication popup is displayed (e.g. after guest clicks wishlist)."""
        modal = self.page.locator(MyAccountLocators.WISHLIST_AUTH_MODAL).first
        try:
            return modal.is_visible(timeout=timeout_ms)
        except Exception:
            return False

    def is_product_in_wishlist(self, product_name: str) -> bool:
        """Check whether a product with given name or URL is present in current Wishlist items."""
        items = self.get_wishlist_items()
        kw = product_name.strip().lower()
        clean_kw = re.sub(r"[^a-zA-Z0-9\s]", "", kw)
        nospace_kw = re.sub(r"[^a-zA-Z0-9]", "", kw)
        kw_words = [w for w in clean_kw.split() if len(w) > 3]

        for item in items:
            it_name = item.get("name", "").strip().lower()
            it_url = item.get("url", "").strip().lower()
            clean_it = re.sub(r"[^a-zA-Z0-9\s]", "", it_name)
            nospace_it = re.sub(r"[^a-zA-Z0-9]", "", it_name)

            if (
                kw in it_name
                or it_name in kw
                or clean_kw in clean_it
                or clean_it in clean_kw
            ):
                return True

            if (
                (nospace_kw and nospace_kw in nospace_it)
                or (nospace_it and nospace_it in nospace_kw)
            ):
                return True

            if it_url and (
                any(w in it_url for w in kw_words)
                or (nospace_kw and nospace_kw in it_url)
            ):
                return True

            it_words = [w for w in clean_it.split() if len(w) > 3]
            if kw_words and any(w in it_words for w in kw_words):
                return True

            # Plural/singular word stem match (e.g. crosscutter vs crosscutters)
            if any(w.rstrip("s") in it_name.rstrip("s") or it_name.rstrip("s") in w.rstrip("s") for w in kw_words):
                return True
            if any(w.rstrip("s") in it_w.rstrip("s") or it_w.rstrip("s") in w.rstrip("s") for w in kw_words for it_w in it_words):
                return True

        return False

    def remove_wishlist_item_by_name(self, product_name: str) -> bool:
        """Locate the specific Wishlist product card matching product_name, click its
        individual Remove button, handle any confirm popup, and wait for UI update.
        """
        logger.info(f"Removing product '{product_name}' from Wishlist...")
        curr_url = self.get_current_url()
        if "/wishlist" not in curr_url:
            self.navigate_to_wishlist()
            self.wait_for_dom_content_loaded()

        items = self.page.locator(MyAccountLocators.WISHLIST_ITEMS)
        count = items.count()
        target_card = None
        kw = product_name.strip().lower()
        clean_kw = re.sub(r"[^a-zA-Z0-9\s]", "", kw)
        nospace_kw = re.sub(r"[^a-zA-Z0-9]", "", kw)
        kw_words = [w for w in clean_kw.split() if len(w) > 3]

        for i in range(count):
            card = items.nth(i)
            card_text = card.inner_text().lower()
            clean_card_text = re.sub(r"[^a-zA-Z0-9\s]", "", card_text)
            nospace_card_text = re.sub(r"[^a-zA-Z0-9]", "", card_text)
            card_link = card.locator(MyAccountLocators.WISHLIST_ITEM_NAME).first
            card_url = card_link.get_attribute("href") or "" if card_link.is_visible(timeout=500) else ""

            if (
                kw in card_text
                or clean_kw in clean_card_text
                or (nospace_kw and nospace_kw in nospace_card_text)
                or (card_url and any(w in card_url.lower() for w in kw_words))
                or (kw_words and any(w in clean_card_text for w in kw_words))
            ):
                target_card = card
                break

        if not target_card:
            logger.warning(f"Wishlist item '{product_name}' not found for removal.")
            return False

        remove_btn = target_card.locator(MyAccountLocators.WISHLIST_REMOVE_BUTTON).first
        assert remove_btn.is_visible(timeout=5000), f"Remove button not visible for product '{product_name}'"

        # Register one-shot dialog handler for native confirmation alert
        self.page.once("dialog", lambda dialog: dialog.accept())

        # Click remove button
        remove_btn.click()

        # Handle modal confirmation button if present
        try:
            confirm_btn = self.page.locator(MyAccountLocators.WISHLIST_CONFIRM_OK_BUTTON).first
            if confirm_btn.is_visible(timeout=2000):
                confirm_btn.click()
        except Exception:
            pass

        # Wait for loading mask to disappear or DOM update
        try:
            self.page.locator(".loading-mask, .loader").first.wait_for(state="hidden", timeout=8000)
        except Exception:
            pass
        self.wait_for_timeout(2000)

        # Verify product is no longer present
        is_still_present = self.is_product_in_wishlist(product_name)
        return not is_still_present

    def clear_all_wishlist_items(self) -> bool:
        """Click Clear Wishlist button, handle any confirmation, and verify empty state."""
        logger.info("Executing Clear All Wishlist Items...")
        curr_url = self.get_current_url()
        if "/wishlist" not in curr_url:
            self.navigate_to_wishlist()
            self.wait_for_dom_content_loaded()

        clear_btn = self.page.locator(MyAccountLocators.WISHLIST_CLEAR_BUTTON).first
        if not clear_btn.is_visible(timeout=3000):
            # If clear button is not visible, check if wishlist is already empty
            empty_msg = self.page.locator(MyAccountLocators.WISHLIST_EMPTY_MESSAGE).first
            if empty_msg.is_visible(timeout=2000) or len(self.get_wishlist_items()) == 0:
                logger.info("Wishlist is already empty; clear action not required.")
                return True
            logger.warning("Clear Wishlist button not visible and items exist.")
            return False

        # Register dialog handler if browser dialog pops up
        self.page.once("dialog", lambda dialog: dialog.accept())

        clear_btn.click()

        # Handle modal confirmation button if present
        try:
            confirm_btn = self.page.locator(MyAccountLocators.WISHLIST_CONFIRM_OK_BUTTON).first
            if confirm_btn.is_visible(timeout=2000):
                confirm_btn.click()
        except Exception:
            pass

        # Wait for loading mask to disappear
        try:
            self.page.locator(".loading-mask, .loader").first.wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.wait_for_timeout(2500)

        # Verify empty state
        remaining_count = len(self.get_wishlist_items())
        logger.info(f"Remaining wishlist items after clear: {remaining_count}")
        return remaining_count == 0

    def get_cart_badge_count(self) -> int:
        """Extract numeric value from the header shopping cart counter badge."""
        badge = self.page.locator(MyAccountLocators.CART_BADGE_COUNTER).first
        try:
            if badge.is_visible(timeout=3000):
                text = badge.inner_text().strip()
                digits = re.findall(r"\d+", text)
                if digits:
                    return int(digits[0])
        except Exception:
            pass
        return 0

    def add_all_wishlist_items_to_cart(self) -> Dict[str, Any]:
        """Click 'Add All to Cart' button from Wishlist and return initial and updated status."""
        logger.info("Adding all Wishlist items to cart...")
        curr_url = self.get_current_url()
        if "/wishlist" not in curr_url:
            self.navigate_to_wishlist()
            self.wait_for_dom_content_loaded()

        initial_cart_count = self.get_cart_badge_count()
        initial_wishlist_count = len(self.get_wishlist_items())
        logger.info(f"Initial state -> Cart count: {initial_cart_count}, Wishlist items: {initial_wishlist_count}")

        add_all_btn = self.page.locator(MyAccountLocators.WISHLIST_ADD_ALL_TO_CART_BUTTON).first
        assert add_all_btn.is_visible(timeout=5000), "Add All to Cart button is not visible on Wishlist page."

        add_all_btn.click()

        # Wait for redirect or cart update (often redirects to /checkout/cart/)
        try:
            self.page.wait_for_url("**/checkout/cart/**", timeout=8000)
            self.wait_for_dom_content_loaded()
        except Exception:
            self.wait_for_timeout(3000)

        # Wait for loading mask to disappear if present
        try:
            self.page.locator(".loading-mask, .loader").first.wait_for(state="hidden", timeout=8000)
        except Exception:
            pass

        updated_cart_count = self.get_cart_badge_count()
        success_msg_el = self.page.locator(MyAccountLocators.WISHLIST_SUCCESS_MESSAGE).first
        success_message = success_msg_el.inner_text().strip() if success_msg_el.is_visible(timeout=3000) else ""

        logger.info(
            f"After Add All to Cart -> Cart count: {updated_cart_count}, "
            f"Success message: '{success_message}', Current URL: '{self.get_current_url()}'"
        )

        return {
            "initial_cart_count": initial_cart_count,
            "initial_wishlist_count": initial_wishlist_count,
            "updated_cart_count": updated_cart_count,
            "success_message": success_message,
            "current_url": self.get_current_url(),
        }

