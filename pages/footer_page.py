"""Footer Page Object Model.

Encapsulates all actions and verifications for the Silhouette America website Footer,
including newsletter subscription, Need Help section, Legal links, Support links,
Headquarters regional links, Social media icons, Reviews.io badge, and Floating Chat/Help widget.
"""
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from playwright.sync_api import Locator, Page, Response, TimeoutError as PlaywrightTimeoutError

from config.config import Config
from locators.footer_locators import FooterLocators
from pages.base_page import BasePage
from utils.logger import logger
from utils.wait_helper import WaitHelper


class FooterPage(BasePage):
    """Page Object for Silhouette America Footer interactions and validations."""

    def __init__(self, page: Page, config: Optional[Config] = None) -> None:
        super().__init__(page=page, config=config)
        self.locators = FooterLocators

    # =========================================================================
    # Navigation & Footer Container
    # =========================================================================

    def open_homepage(self) -> str:
        """Navigate to the production homepage, handle security challenges, and dismiss popups."""
        logger.info("Opening homepage for Footer automation...")
        self.goto("", wait_until="domcontentloaded")
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        self.wait_for_dom_content_loaded()
        return self.get_current_url()

    def scroll_to_footer(self, timeout: int = 10000) -> bool:
        """Scroll down to make the footer container fully visible in the viewport."""
        logger.info("Scrolling down to the footer...")
        try:
            footer_elem = self.page.locator(FooterLocators.FOOTER_CONTAINER).first
            footer_elem.wait_for(state="attached", timeout=timeout)
            footer_elem.scroll_into_view_if_needed(timeout=timeout)
            self.dismiss_cookie_consent_if_present()
            self.wait_for_timeout(500)
            return footer_elem.is_visible()
        except Exception as e:
            logger.error(f"Failed to scroll to footer: {e}")
            return False

    def is_footer_visible(self) -> bool:
        """Check whether the main footer container is visible."""
        return self.is_visible(FooterLocators.FOOTER_CONTAINER, timeout=3000)

    # =========================================================================
    # E2E-FTR-001: Newsletter Subscription
    # =========================================================================

    def is_newsletter_section_visible(self) -> bool:
        """Check whether the newsletter subscription section is visible."""
        return self.is_visible(FooterLocators.NEWSLETTER_SECTION, timeout=3000)

    def get_newsletter_section_content(self) -> Dict[str, str]:
        """Extract visible heading, description, and button text from the newsletter section."""
        logger.info("Extracting newsletter section content...")
        heading_elem = self.page.locator(FooterLocators.NEWSLETTER_HEADING).first
        heading_elem.scroll_into_view_if_needed()
        heading_text = heading_elem.inner_text().strip() if heading_elem.is_visible(timeout=3000) else ""

        desc_elem = self.page.locator(FooterLocators.NEWSLETTER_DESC).first
        desc_text = desc_elem.inner_text().strip() if desc_elem.is_visible(timeout=3000) else ""

        btn_elem = self.page.locator(FooterLocators.NEWSLETTER_SUBSCRIBE_BUTTON).first
        btn_text = btn_elem.inner_text().strip() if btn_elem.is_visible(timeout=3000) else ""

        return {
            "heading": heading_text,
            "description": desc_text,
            "button_text": btn_text,
        }

    def fill_newsletter_email(self, email: str) -> None:
        """Enter the specified email address into the newsletter input field."""
        logger.info(f"Filling newsletter email: '{email}'")
        input_elem = self.page.locator(FooterLocators.NEWSLETTER_EMAIL_INPUT).first
        input_elem.scroll_into_view_if_needed()
        input_elem.fill(email)

    def submit_newsletter(self) -> None:
        """Click the newsletter Subscribe button."""
        logger.info("Submitting newsletter subscription form...")
        btn = self.page.locator(FooterLocators.NEWSLETTER_SUBSCRIBE_BUTTON).first
        btn.scroll_into_view_if_needed()
        btn.click()

    def get_newsletter_feedback(self, timeout: int = 8000) -> Dict[str, Any]:
        """Wait for and retrieve feedback (success or error message) after newsletter submission."""
        logger.info("Waiting for newsletter subscription feedback...")
        success_loc = self.page.locator(FooterLocators.NEWSLETTER_SUCCESS_MESSAGE).first
        error_loc = self.page.locator(FooterLocators.NEWSLETTER_ERROR_MESSAGE).first

        try:
            # Check for either success or error message
            self.page.wait_for_selector(
                f"{FooterLocators.NEWSLETTER_SUCCESS_MESSAGE}, {FooterLocators.NEWSLETTER_ERROR_MESSAGE}",
                state="visible",
                timeout=timeout,
            )
        except Exception as e:
            logger.debug(f"Newsletter feedback wait timed out: {e}")

        is_success = success_loc.is_visible(timeout=500)
        is_error = error_loc.is_visible(timeout=500)
        feedback_text = ""
        if is_success:
            feedback_text = success_loc.inner_text().strip()
        elif is_error:
            feedback_text = error_loc.inner_text().strip()

        return {
            "is_success": is_success,
            "is_error": is_error,
            "message": feedback_text,
        }

    # =========================================================================
    # E2E-FTR-002: Need Help / Support Email
    # =========================================================================

    def get_support_email_details(self) -> Dict[str, Any]:
        """Extract and return details of the support email link in the Need Help section."""
        logger.info("Extracting Need Help support email link details...")
        email_elem = self.page.locator(FooterLocators.SUPPORT_EMAIL_LINK).first
        email_elem.scroll_into_view_if_needed()

        is_visible = email_elem.is_visible(timeout=3000)
        href = email_elem.get_attribute("href") or ""
        raw_text = email_elem.inner_text().strip()

        # Extract email address without 'mailto:'
        email_address = href.replace("mailto:", "").strip() if href.startswith("mailto:") else ""

        return {
            "is_visible": is_visible,
            "href": href,
            "email": email_address,
            "text": raw_text,
        }

    # =========================================================================
    # E2E-FTR-003: Legal Links
    # =========================================================================

    def get_legal_links(self) -> List[Dict[str, str]]:
        """Extract all legal links from the actual Footer DOM."""
        logger.info("Extracting Legal links from footer...")
        links_loc = self.page.locator(FooterLocators.LEGAL_LINKS)
        count = links_loc.count()
        links_data: List[Dict[str, str]] = []

        for i in range(count):
            item = links_loc.nth(i)
            text = item.inner_text().strip()
            href = item.get_attribute("href") or ""
            target = item.get_attribute("target") or ""
            links_data.append({
                "index": i,
                "text": text,
                "href": href,
                "target": target,
            })
            logger.info(f"Found Legal Link [{i}]: '{text}' -> {href} (target='{target}')")

        return links_data

    # =========================================================================
    # E2E-FTR-004: Support Links
    # =========================================================================

    def get_support_links(self) -> List[Dict[str, str]]:
        """Extract all support links from the actual Footer DOM."""
        logger.info("Extracting Support links from footer...")
        links_loc = self.page.locator(FooterLocators.SUPPORT_LINKS)
        count = links_loc.count()
        links_data: List[Dict[str, str]] = []

        for i in range(count):
            item = links_loc.nth(i)
            text = item.inner_text().strip()
            # Clean up newlines or hidden text
            clean_text = " ".join(text.split())
            href = item.get_attribute("href") or ""
            target = item.get_attribute("target") or ""
            links_data.append({
                "index": i,
                "text": clean_text,
                "href": href,
                "target": target,
            })
            logger.info(f"Found Support Link [{i}]: '{clean_text}' -> {href} (target='{target}')")

        return links_data

    # =========================================================================
    # E2E-FTR-005: Headquarters Regional Links
    # =========================================================================

    def get_headquarters_links(self) -> List[Dict[str, str]]:
        """Extract all regional headquarters links from the actual Footer DOM."""
        logger.info("Extracting Headquarters regional links from footer...")
        places_loc = self.page.locator(FooterLocators.HQ_LINKS)
        count = places_loc.count()
        links_data: List[Dict[str, str]] = []

        for i in range(count):
            item = places_loc.nth(i)
            text = item.inner_text().strip()
            clean_text = " ".join(text.split())
            href = item.get_attribute("href") or ""
            target = item.get_attribute("target") or ""
            parsed = urlparse(href)
            hostname = parsed.hostname or ""

            links_data.append({
                "index": i,
                "text": clean_text,
                "href": href,
                "target": target,
                "hostname": hostname,
            })
            logger.info(f"Found HQ Link [{i}]: '{clean_text}' -> {href} (host='{hostname}', target='{target}')")

        return links_data

    # =========================================================================
    # E2E-FTR-006: Social Media Icons
    # =========================================================================

    def get_social_links(self) -> List[Dict[str, str]]:
        """Extract all social media links from the actual Footer DOM."""
        logger.info("Extracting Social Media links from footer...")
        social_loc = self.page.locator(FooterLocators.SOCIAL_LINKS)
        count = social_loc.count()
        links_data: List[Dict[str, str]] = []

        for i in range(count):
            item = social_loc.nth(i)
            cls = item.get_attribute("class") or ""
            href = item.get_attribute("href") or ""
            aria = item.get_attribute("aria-label") or ""
            target = item.get_attribute("target") or ""
            parsed = urlparse(href)
            hostname = parsed.hostname or ""

            # Determine platform name
            platform = "unknown"
            if "insta" in cls or "instagram" in href.lower():
                platform = "Instagram"
            elif "fb" in cls or "facebook" in href.lower():
                platform = "Facebook"
            elif "ytube" in cls or "youtube" in href.lower():
                platform = "YouTube"
            elif "tw" in cls or "twitter" in href.lower() or "x.com" in href.lower():
                platform = "X (Twitter)"
            elif "pi" in cls or "pinterest" in href.lower():
                platform = "Pinterest"

            links_data.append({
                "index": i,
                "platform": platform,
                "class": cls,
                "href": href,
                "target": target,
                "aria_label": aria,
                "hostname": hostname,
            })
            logger.info(
                f"Found Social Icon [{i}]: Platform='{platform}', Host='{hostname}', Target='{target}', Class='{cls}'"
            )

        return links_data

    # =========================================================================
    # E2E-FTR-007: Reviews Badge & Floating Chat Widget
    # =========================================================================

    def get_reviews_ribbon_details(self) -> Dict[str, Any]:
        """Extract details of the Reviews.io badge in the footer."""
        logger.info("Extracting Reviews.io ribbon details from footer...")
        ribbon_elem = self.page.locator(FooterLocators.REVIEWS_RIBBON_LINK).first
        ribbon_elem.scroll_into_view_if_needed()

        is_visible = ribbon_elem.is_visible(timeout=3000)
        href = ribbon_elem.get_attribute("href") or ""
        aria_label = ribbon_elem.get_attribute("aria-label") or ""
        raw_text = ribbon_elem.inner_text().strip()

        # Extract review count
        count_elem = ribbon_elem.locator(".sa-footer-reviews-ribbon__count").first
        count_text = count_elem.inner_text().strip() if count_elem.is_visible(timeout=1000) else ""

        # Logo image check
        logo_elem = ribbon_elem.locator("img").first
        logo_alt = logo_elem.get_attribute("alt") or "" if logo_elem.is_visible(timeout=1000) else ""

        return {
            "is_visible": is_visible,
            "href": href,
            "aria_label": aria_label,
            "text": raw_text,
            "count": count_text,
            "logo_alt": logo_alt,
        }

    def open_floating_help_widget(self, timeout: int = 5000) -> bool:
        """Click the floating chatbot icon to expand the help/support widget."""
        logger.info("Opening floating chatbot/help widget...")
        icon_elem = self.page.locator(FooterLocators.CHATBOT_ICON).first
        if not icon_elem.is_visible(timeout=timeout):
            logger.error("Chatbot launcher icon is not visible.")
            return False

        icon_elem.click()
        try:
            bot_elem = self.page.locator(FooterLocators.CHATBOT_CONTAINER).first
            bot_elem.wait_for(state="visible", timeout=timeout)
            logger.info("Chatbot widget opened successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to open chatbot widget: {e}")
            return False

    def is_floating_help_widget_open(self) -> bool:
        """Check whether the floating chatbot widget is currently visible/open."""
        bot_elem = self.page.locator(FooterLocators.CHATBOT_CONTAINER).first
        return bot_elem.is_visible()

    def get_floating_help_widget_details(self) -> Dict[str, Any]:
        """Extract title and options from the expanded chatbot widget."""
        logger.info("Extracting floating chatbot widget details...")
        title_elem = self.page.locator(FooterLocators.CHATBOT_TITLE).first
        title_text = title_elem.inner_text().strip() if title_elem.is_visible(timeout=2000) else ""

        options_loc = self.page.locator(FooterLocators.CHATBOT_OPTIONS_LINKS)
        options_count = options_loc.count()
        options: List[Dict[str, str]] = []

        for i in range(options_count):
            opt = options_loc.nth(i)
            options.append({
                "text": opt.inner_text().strip(),
                "href": opt.get_attribute("href") or "",
            })

        return {
            "title": title_text,
            "options_count": options_count,
            "options": options,
        }

    def close_floating_help_widget(self, timeout: int = 5000) -> bool:
        """Click the close button to collapse the chatbot widget."""
        logger.info("Closing floating chatbot widget...")
        close_btn = self.page.locator(FooterLocators.CHATBOT_CLOSE_BUTTON).first
        if not close_btn.is_visible(timeout=timeout):
            logger.warning("Chatbot close button is not visible.")
            return False

        close_btn.click()
        try:
            bot_elem = self.page.locator(FooterLocators.CHATBOT_CONTAINER).first
            bot_elem.wait_for(state="hidden", timeout=timeout)
            logger.info("Chatbot widget closed successfully.")
            return True
        except Exception as e:
            logger.debug(f"Chatbot widget hidden wait notice: {e}")
            return not bot_elem.is_visible()

    # =========================================================================
    # Reusable Navigation Validator
    # =========================================================================

    def navigate_and_validate_link(
        self,
        link_locator: Locator,
        expected_url_part: str,
        is_new_tab: bool = False,
        timeout: int = 15000,
    ) -> Dict[str, Any]:
        """Reusable method to navigate to a footer link (same-tab or new-tab),

        validate destination URL and indicator, and return cleanly to homepage.
        """
        link_locator.scroll_into_view_if_needed()

        if is_new_tab:
            logger.info(f"Opening link in new tab (expecting '{expected_url_part}')...")
            with self.page.context.expect_page(timeout=timeout) as new_page_info:
                link_locator.click()
            dest_page = new_page_info.value
            dest_page.wait_for_load_state("domcontentloaded", timeout=timeout)
            actual_url = dest_page.url
            actual_title = dest_page.title()
            logger.info(f"New tab loaded: URL='{actual_url}', Title='{actual_title}'")
            dest_page.close()
            return {
                "success": expected_url_part.lower() in actual_url.lower(),
                "actual_url": actual_url,
                "actual_title": actual_title,
                "is_new_tab": True,
            }
        else:
            logger.info(f"Navigating in same tab (expecting '{expected_url_part}')...")
            link_locator.click()
            self.wait_for_dom_content_loaded()
            self.handle_cloudflare_if_present()
            actual_url = self.get_current_url()
            actual_title = self.get_title()
            logger.info(f"Same tab loaded: URL='{actual_url}', Title='{actual_title}'")

            # Return to homepage and scroll back to footer for subsequent links
            self.open_homepage()
            self.scroll_to_footer()

            return {
                "success": expected_url_part.lower() in actual_url.lower(),
                "actual_url": actual_url,
                "actual_title": actual_title,
                "is_new_tab": False,
            }

