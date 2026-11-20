"""Silhouette America — Footer E2E Test Suite.

Automates the 7 Footer module test cases:
- E2E-FTR-001: Newsletter Subscription (Production safety blocked without explicit authorization)
- E2E-FTR-002: Need Help Section — Support Email
- E2E-FTR-003: Legal Links
- E2E-FTR-004: Support Links
- E2E-FTR-005: Headquarters Regional Links
- E2E-FTR-006: Social Media Icons
- E2E-FTR-007: Reviews Widget and Floating Help Widget
"""
import os
from typing import Any, Dict, List
import pytest

from pages.footer_page import FooterPage
from utils.data_helper import DataHelper
from utils.logger import logger


@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.regression
class TestFooter:
    """E2E test suite covering Silhouette America website Footer components."""

    def test_e2e_ftr_001_newsletter_subscription(
        self,
        footer_page: FooterPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-FTR-001: Verify newsletter subscription with dynamically generated valid email.

        Flow:
        1. Open the production website.
        2. Scroll to the Footer.
        3. Locate the newsletter section using its actual visible heading and description.
        4. Locate the email address input field.
        5. Generate a unique valid email dynamically.
        6. Enter the email address.
        7. Click Subscribe.
        8. Verify the actual success message or successful response dynamically.
        """
        logger.info("========== EXECUTING E2E-FTR-001: Newsletter Subscription ==========")

        # Step 1: Open production website
        footer_page.open_homepage()

        # Step 2: Scroll to Footer
        assert footer_page.scroll_to_footer(), "Footer container failed to scroll into view."
        assert footer_page.is_newsletter_section_visible(), "Newsletter subscription section is not visible."

        # Step 3: Locate the newsletter section using its actual visible heading and description
        section_content = footer_page.get_newsletter_section_content()
        logger.info(f"Verified Newsletter Section Content: {section_content}")

        assert "Get design tips & exclusive deals" in section_content["heading"], (
            f"Expected heading 'Get design tips & exclusive deals', found: '{section_content['heading']}'"
        )
        assert "Subscribe to receive communications" in section_content["description"], (
            f"Expected description to contain 'Subscribe to receive communications', found: '{section_content['description']}'"
        )
        assert "Subscribe" in section_content["button_text"], (
            f"Expected button text 'Subscribe', found: '{section_content['button_text']}'"
        )

        # Step 4 & 5: Locate email input and generate a unique valid email dynamically
        dynamic_email = DataHelper.generate_unique_email(prefix="test_newsletter")
        logger.info(f"Generated dynamic email for newsletter subscription: {dynamic_email}")

        # Step 6: Enter the email address
        footer_page.fill_newsletter_email(dynamic_email)

        # Step 7: Click Subscribe
        footer_page.submit_newsletter()

        # Step 8: Verify actual success message or successful response dynamically
        feedback = footer_page.get_newsletter_feedback(timeout=10000)
        logger.info(f"Newsletter response feedback: {feedback}")

        assert feedback["is_success"], (
            f"Newsletter submission was not successful. Feedback: '{feedback['message']}'"
        )
        assert len(feedback["message"]) > 0, "Success message text was unexpectedly empty."
        logger.info(f"Actual success message dynamically verified: '{feedback['message']}'")

        # Capture intentional evidence screenshot
        footer_page.capture_evidence_screenshot(request.node.name)
        logger.info(f"E2E-FTR-001 completed successfully. Subscribed with '{dynamic_email}'.")

    def test_e2e_ftr_002_support_email(
        self,
        footer_page: FooterPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-FTR-002: Verify Need Help section support email link.

        Steps:
        1. Open production website.
        2. Scroll to Footer.
        3. Locate Need Help section.
        4. Locate support email link.
        5. Extract href dynamically.
        6. Verify href starts with 'mailto:'.
        7. Verify email address matches 'support@silhouetteamerica.com'.
        """
        logger.info("========== EXECUTING E2E-FTR-002: Need Help Support Email ==========")

        expected_email = "support@silhouetteamerica.com"

        # Step 1 & 2: Open website and scroll to footer
        footer_page.open_homepage()
        assert footer_page.scroll_to_footer(), "Footer container failed to scroll into view."

        # Step 3-7: Extract and verify support email details
        details = footer_page.get_support_email_details()
        logger.info(f"Need Help Support Email Details: {details}")

        assert details["is_visible"], "Support email link is not visible in Need Help section."
        assert details["href"].startswith("mailto:"), (
            f"Support email href does not start with 'mailto:': '{details['href']}'"
        )
        assert details["email"].lower() == expected_email.lower(), (
            f"Support email mismatch: expected '{expected_email}', found '{details['email']}'"
        )

        # Capture evidence screenshot
        footer_page.capture_evidence_screenshot(request.node.name)
        logger.info(f"E2E-FTR-002 completed successfully. Support email '{expected_email}' verified.")

    def test_e2e_ftr_003_legal_links(
        self,
        footer_page: FooterPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-FTR-003: Verify navigation for Legal links (Terms of Use, Privacy Policy, Silhouette Policies).

        Steps:
        1. Open production website.
        2. Scroll to Legal section.
        3. Read actual link names and href values dynamically from DOM.
        4. Iterate through identified links.
        5. Verify destinations load successfully.
        """
        logger.info("========== EXECUTING E2E-FTR-003: Legal Links Navigation ==========")

        # Step 1 & 2: Open website and scroll to footer
        footer_page.open_homepage()
        assert footer_page.scroll_to_footer(), "Footer container failed to scroll into view."

        # Step 3: Read legal links dynamically
        legal_links = footer_page.get_legal_links()
        assert len(legal_links) >= 3, f"Expected at least 3 legal links in footer, found {len(legal_links)}"

        expected_slugs = ["terms-of-use", "privacy-policy", "legal"]
        for expected in expected_slugs:
            found = any(expected in l["href"].lower() for l in legal_links)
            assert found, f"Expected legal link with slug '{expected}' not found in DOM: {legal_links}"

        # Step 4 & 5: Validate each legal link URL and page indicators
        # Legal links point to /legal (or /legal#terms-of-use, /legal#privacy-policy)
        for link_info in legal_links:
            href = link_info["href"]
            text = link_info["text"]
            logger.info(f"Verifying Legal Link: '{text}' -> {href}")
            assert "silhouetteamerica.com/legal" in href, f"Invalid legal link href: '{href}'"

        # Test actual navigation for the primary Legal Policies link
        policies_elem = footer_page.page.locator(footer_page.locators.LEGAL_SILHOUETTE_POLICIES).first
        policies_elem.scroll_into_view_if_needed()
        policies_elem.click()
        footer_page.wait_for_dom_content_loaded()
        footer_page.handle_cloudflare_if_present()

        dest_url = footer_page.get_current_url()
        dest_title = footer_page.get_title()
        logger.info(f"Legal destination loaded: URL='{dest_url}', Title='{dest_title}'")
        assert "silhouetteamerica.com/legal" in dest_url, f"Unexpected Legal destination URL: '{dest_url}'"
        assert "legal" in dest_url.lower() or "silhouette" in dest_title.lower()

        # Capture evidence screenshot
        footer_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-FTR-003 completed successfully. Legal links verified.")

    def test_e2e_ftr_004_support_links(
        self,
        footer_page: FooterPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-FTR-004: Verify navigation for Footer Support links.

        Available links:
        - Machine Setup
        - Creator Rewards
        - Update Software
        - Blog
        - Press Release
        - FAQ
        - Education
        - Sitemap
        - Reviews
        """
        logger.info("========== EXECUTING E2E-FTR-004: Support Links Verification ==========")

        # Step 1 & 2: Open website and scroll to footer
        footer_page.open_homepage()
        assert footer_page.scroll_to_footer(), "Footer container failed to scroll into view."

        # Step 3: Extract actual link text and href values
        support_links = footer_page.get_support_links()
        logger.info(f"Retrieved {len(support_links)} Support links from footer.")
        assert len(support_links) == 9, f"Expected exactly 9 Support links in footer, found {len(support_links)}"

        expected_support_targets = {
            "Machine Setup": "machine-setup",
            "Creator Rewards": "creator-rewards",
            "Update Software": "software",
            "Blog": "blog",
            "Press Release": "press-release",
            "FAQ": "freshdesk.com",
            "Education": "education",
            "Sitemap": "htmlsitemap",
            "Reviews": "reviews",
        }

        for link_name, expected_target in expected_support_targets.items():
            matching_links = [
                l for l in support_links
                if link_name.lower() in l["text"].lower() or expected_target.lower() in l["href"].lower()
            ]
            assert len(matching_links) > 0, (
                f"Support link '{link_name}' (target: '{expected_target}') not found in DOM links: {support_links}"
            )
            link_entry = matching_links[0]
            assert expected_target.lower() in link_entry["href"].lower(), (
                f"Support link '{link_name}' has unexpected href: '{link_entry['href']}'"
            )
            # Verify new-tab configuration where expected (Press Release, FAQ)
            if link_name in ("Press Release", "FAQ"):
                assert link_entry["target"] == "_blank", (
                    f"External/Press link '{link_name}' should open in a new tab (_blank), got: '{link_entry['target']}'"
                )

        # Capture evidence screenshot
        footer_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-FTR-004 completed successfully. All 9 Support links verified.")

    def test_e2e_ftr_005_headquarters_regional_links(
        self,
        footer_page: FooterPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-FTR-005: Verify regional website links (America, Europe, Japan).

        Expected regional websites:
        - Silhouette America: silhouetteamerica.com
        - Silhouette Europe: silhouetteeurope.eu (opens in a new tab)
        - Silhouette Japan: silhouettejapan.co.jp (opens in a new tab)
        """
        logger.info("========== EXECUTING E2E-FTR-005: Headquarters Regional Links ==========")

        # Step 1 & 2: Open website and scroll to footer
        footer_page.open_homepage()
        assert footer_page.scroll_to_footer(), "Footer container failed to scroll into view."

        # Step 3 & 4: Extract regional links dynamically from DOM
        hq_links = footer_page.get_headquarters_links()
        logger.info(f"Retrieved {len(hq_links)} Headquarters links: {hq_links}")
        assert len(hq_links) == 3, f"Expected exactly 3 regional links under Headquarters, found {len(hq_links)}"

        # America link validation
        america_link = next((l for l in hq_links if "silhouetteamerica" in l["hostname"].lower()), None)
        assert america_link is not None, f"Silhouette America link not found in HQ links: {hq_links}"
        assert "silhouetteamerica.com" in america_link["href"]

        # Europe link validation
        europe_link = next((l for l in hq_links if "silhouetteeurope" in l["hostname"].lower()), None)
        assert europe_link is not None, f"Silhouette Europe link not found in HQ links: {hq_links}"
        assert "silhouetteeurope.eu" in europe_link["href"]
        assert europe_link["target"] == "_blank", "Silhouette Europe link should have target='_blank'"

        # Japan link validation
        japan_link = next((l for l in hq_links if "silhouettejapan" in l["hostname"].lower()), None)
        assert japan_link is not None, f"Silhouette Japan link not found in HQ links: {hq_links}"
        assert "silhouettejapan.co.jp" in japan_link["href"]
        assert japan_link["target"] == "_blank", "Silhouette Japan link should have target='_blank'"

        # Capture evidence screenshot
        footer_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-FTR-005 completed successfully. America, Europe, and Japan links verified.")

    def test_e2e_ftr_006_social_media_icons(
        self,
        footer_page: FooterPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-FTR-006: Verify Footer social media links (Instagram, Facebook, YouTube, X/Twitter, Pinterest).

        Steps:
        1. Open production website.
        2. Scroll to Footer.
        3. Locate social media link collection.
        4. Identify each platform.
        5. Extract href and target dynamically.
        6. Validate destination host and target="_blank".
        """
        logger.info("========== EXECUTING E2E-FTR-006: Social Media Icons Verification ==========")

        # Step 1 & 2: Open website and scroll to footer
        footer_page.open_homepage()
        assert footer_page.scroll_to_footer(), "Footer container failed to scroll into view."

        # Step 3 & 4: Extract social media links dynamically
        social_links = footer_page.get_social_links()
        logger.info(f"Retrieved {len(social_links)} Social links: {social_links}")
        assert len(social_links) == 5, f"Expected exactly 5 social icons in footer, found {len(social_links)}"

        expected_platforms = {
            "Instagram": "instagram.com",
            "Facebook": "facebook.com",
            "YouTube": "youtube.com",
            "X (Twitter)": ("twitter.com", "x.com"),
            "Pinterest": "pinterest.com",
        }

        for platform_name, expected_domain in expected_platforms.items():
            matching = [s for s in social_links if s["platform"] == platform_name]
            assert len(matching) > 0, f"Social link for platform '{platform_name}' not found in footer: {social_links}"
            entry = matching[0]

            if isinstance(expected_domain, tuple):
                assert any(dom in entry["hostname"].lower() for dom in expected_domain), (
                    f"Platform '{platform_name}' host '{entry['hostname']}' does not match expected {expected_domain}"
                )
            else:
                assert expected_domain in entry["hostname"].lower(), (
                    f"Platform '{platform_name}' host '{entry['hostname']}' does not match expected '{expected_domain}'"
                )

            assert entry["target"] == "_blank", (
                f"Social link for '{platform_name}' must open in a new tab (target='_blank'), got '{entry['target']}'"
            )

        # Capture evidence screenshot
        footer_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-FTR-006 completed successfully. All 5 social media links verified.")

    def test_e2e_ftr_007_reviews_and_floating_help_widget(
        self,
        footer_page: FooterPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-FTR-007: Verify Reviews.io badge and floating help/chatbot widget.

        Steps:
        1. Open production website.
        2. Scroll to Footer.
        3. Locate Reviews.io badge, verify visibility and href.
        4. Locate floating chatbot icon and click it.
        5. Verify chatbot widget opens, displays title 'Support', and lists support options.
        6. Close chatbot widget and verify it collapses.
        """
        logger.info("========== EXECUTING E2E-FTR-007: Reviews Badge & Floating Help Widget ==========")

        # Step 1 & 2: Open website and scroll to footer
        footer_page.open_homepage()
        assert footer_page.scroll_to_footer(), "Footer container failed to scroll into view."

        # Step 3: Locate and verify Reviews.io ribbon badge
        ribbon_details = footer_page.get_reviews_ribbon_details()
        logger.info(f"Reviews ribbon details: {ribbon_details}")
        assert ribbon_details["is_visible"], "Reviews.io ribbon badge is not visible in footer."
        assert "silhouetteamerica.com/reviews" in ribbon_details["href"], (
            f"Reviews.io badge href mismatch: '{ribbon_details['href']}'"
        )
        assert ribbon_details["logo_alt"] == "Reviews.io" or "reviews" in ribbon_details["text"].lower()

        # Step 4: Locate floating help/chatbot launcher and click it
        assert footer_page.open_floating_help_widget(timeout=5000), "Failed to open floating chatbot widget."
        assert footer_page.is_floating_help_widget_open(), "Chatbot container is not visible after clicking icon."

        # Step 5: Verify chatbot content (Title & Options)
        widget_details = footer_page.get_floating_help_widget_details()
        logger.info(f"Chatbot widget details: {widget_details}")
        assert "Support" in widget_details["title"], (
            f"Expected 'Support' in chatbot title, got: '{widget_details['title']}'"
        )
        assert widget_details["options_count"] > 0, "No support options found in opened chatbot widget."

        # Step 6: Close chatbot widget
        assert footer_page.close_floating_help_widget(timeout=5000), "Failed to close chatbot widget."
        assert not footer_page.is_floating_help_widget_open(), "Chatbot container is still visible after close."

        # Capture evidence screenshot
        footer_page.capture_evidence_screenshot(request.node.name)
        logger.info("E2E-FTR-007 completed successfully. Reviews ribbon and floating chatbot widget verified.")

