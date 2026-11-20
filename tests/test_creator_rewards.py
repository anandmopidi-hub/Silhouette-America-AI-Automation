"""Silhouette America — Creator Rewards E2E Test Suite.

Automates all 4 Creator Rewards module test cases:
- E2E-CRW-001: Navigation & Hero Section
- E2E-CRW-002: How It Works & User Guide
- E2E-CRW-003: What Happens Next & Video Gallery
- E2E-CRW-004: Guidelines, Terms & Common Questions
"""
import re
from typing import List
import pytest
from playwright.sync_api import expect

from pages.creator_rewards_page import CreatorRewardsPage
from utils.logger import logger


@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.regression
class TestCreatorRewards:
    """E2E test suite covering Silhouette America Creator Rewards module."""

    def test_e2e_crw_001_navigation_and_hero_section(
        self,
        creator_rewards_page: CreatorRewardsPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CRW-001: Navigation & Hero Section.

        1. Open Silhouette America homepage and wait for header/navigation.
        2. Handle cookie consent popup if displayed.
        3. Identify Resources menu dynamically and expand it.
        4. Identify Creator Rewards link dynamically and extract actual href.
        5. Click link and verify URL resolves to Creator Rewards page & HTTP status.
        6. Assert hero heading 'Make it. Share it. Get Rewarded.' is visible in hero section.
        """
        logger.info("========== EXECUTING E2E-CRW-001: Navigation & Hero Section ==========")

        # Steps 1-3: Open homepage, handle cookies, wait for header nav
        creator_rewards_page.open_homepage_and_wait_for_nav()

        # Steps 4-5: Open Resources menu dynamically
        panel = creator_rewards_page.open_resources_menu()
        expect(panel).to_be_visible()

        # Steps 6-8: Identify Creator Rewards nav link, verify href before click, and navigate
        nav_link = creator_rewards_page.get_creator_rewards_nav_link()
        expect(nav_link).to_be_visible()
        extracted_href = nav_link.get_attribute("href") or ""
        assert "creator-rewards" in extracted_href.lower(), (
            f"Expected 'creator-rewards' in extracted nav href, got: '{extracted_href}'"
        )
        logger.info(f"Extracted Creator Rewards nav href dynamically: '{extracted_href}'")

        nav_result = creator_rewards_page.navigate_to_creator_rewards()

        # Steps 9-10: Verify destination URL and HTTP status
        expect(creator_rewards_page.page).to_have_url(re.compile(r".*creator-rewards.*", re.IGNORECASE))
        if nav_result["status"] is not None:
            assert nav_result["status"] < 400, (
                f"Expected successful navigation HTTP status, got {nav_result['status']}"
            )
            logger.info(f"Verified navigation HTTP status: {nav_result['status']}")

        # Steps 11-12: Verify hero heading inside actual hero section
        hero_section = creator_rewards_page.get_hero_section()
        hero_heading = creator_rewards_page.get_hero_heading()
        expect(hero_section).to_be_visible()
        expect(hero_heading).to_be_visible()
        expect(hero_heading).to_contain_text("Make it. Share it. Get Rewarded.")

        actual_heading = hero_heading.inner_text().strip()
        logger.info(f"Verified hero heading inside hero section: '{actual_heading}'")

        request.node.user_properties.append(("nav_href", extracted_href))
        request.node.user_properties.append(("hero_heading", actual_heading))

        creator_rewards_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-CRW-001 PASSED: Navigation & Hero Section Verified ==========")

    def test_e2e_crw_002_how_it_works_and_user_guide(
        self,
        creator_rewards_page: CreatorRewardsPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CRW-002: How It Works & User Guide.

        1. Navigate to Creator Rewards page.
        2. Locate 'How It Works' section, scroll into view, verify heading visible.
        3. Count step cards dynamically and assert 5 cards displayed with visible content.
        4. Locate Step 2 'User Guide' link, verify valid href & HTTP response, return cleanly.
        5. Locate 'Submit Your Creation' CTA, verify visible/enabled, click, and verify
           resulting submission form interface without performing real submission.
        """
        logger.info("========== EXECUTING E2E-CRW-002: How It Works & User Guide ==========")

        creator_rewards_page.open_creator_rewards()

        # Steps 2-4: How It Works section & heading
        how_sec = creator_rewards_page.get_how_it_works_section()
        how_heading = creator_rewards_page.get_how_it_works_heading()
        how_sec.scroll_into_view_if_needed()
        expect(how_sec).to_be_visible()
        expect(how_heading).to_be_visible()
        expect(how_heading).to_contain_text("How It Works")

        # Steps 5-8: Dynamically count and verify all 5 step cards have meaningful visible content
        step_cards = creator_rewards_page.get_step_cards()
        expect(step_cards).to_have_count(5)
        cards_info = creator_rewards_page.get_step_cards_content()
        for card_meta in cards_info:
            assert len(card_meta["title"]) > 0, f"Step card {card_meta['index']} title is empty."
            assert len(card_meta["text"]) > len(card_meta["title"]), (
                f"Step card {card_meta['index']} lacks body content: {card_meta}"
            )
        logger.info(f"Verified 5 'How It Works' cards: {[c['title'] for c in cards_info]}")

        # Steps 9-14: Step 2 User Guide link extraction & verification
        ug_result = creator_rewards_page.open_user_guide_and_verify()
        assert ug_result["href"], "Step 2 User Guide href was empty."
        assert ug_result["final_url"] and ug_result["final_url"] != "about:blank", (
            f"User Guide failed to open valid destination: {ug_result}"
        )
        if ug_result["http_status"] is not None:
            assert ug_result["http_status"] < 400, (
                f"User Guide destination returned HTTP {ug_result['http_status']}: {ug_result['href']}"
            )
        logger.info(
            f"Verified Step 2 User Guide link: href='{ug_result['href']}', "
            f"status={ug_result['http_status']} ({ug_result['response_source']})"
        )

        # Ensure we are on Creator Rewards page
        expect(creator_rewards_page.page).to_have_url(re.compile(r".*creator-rewards.*", re.IGNORECASE))

        # Steps 15-19: Submit Your Creation CTA inspection (no real form submission)
        submit_info = creator_rewards_page.click_submit_creation()
        assert submit_info["form_visible"], "Submit Your Creation form did not become visible."
        assert submit_info["field_count"] > 0, "Submission form rendered zero interactive fields."
        assert submit_info["submit_button_visible"] and submit_info["submit_button_enabled"], (
            "Form submit button is not visible and enabled."
        )
        logger.info(
            f"Verified 'Submit Your Creation' interface: heading='{submit_info['submit_heading']}', "
            f"fields={submit_info['field_count']}, url='{submit_info['current_url']}'"
        )

        request.node.user_properties.append(("step_count", len(cards_info)))
        request.node.user_properties.append(("user_guide_status", ug_result["http_status"]))
        request.node.user_properties.append(("submit_form_fields", submit_info["field_count"]))

        creator_rewards_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-CRW-002 PASSED: How It Works, User Guide & Submission UI Verified ==========")

    def test_e2e_crw_003_what_happens_next_and_video_gallery(
        self,
        creator_rewards_page: CreatorRewardsPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CRW-003: What Happens Next & Video Gallery.

        1. Navigate to Creator Rewards page.
        2. Locate 'What Happens Next' section, scroll into view, verify heading and steps.
        3. Locate 'Made With Silhouette' gallery section and verify heading.
        4. Inspect all video cards dynamically and verify video references.
        5. Select first video card, hover, click, verify controls, expand fullscreen,
           restore player cleanly, and verify page remains usable & capture video console errors.
        """
        logger.info("========== EXECUTING E2E-CRW-003: What Happens Next & Video Gallery ==========")

        creator_rewards_page.open_creator_rewards()

        # Steps 2-4: What Happens Next section
        next_sec = creator_rewards_page.get_what_happens_next_section()
        next_heading = creator_rewards_page.get_what_happens_next_heading()
        next_steps = creator_rewards_page.get_what_happens_next_steps()
        next_sec.scroll_into_view_if_needed()
        expect(next_sec).to_be_visible()
        expect(next_heading).to_be_visible()
        expect(next_heading).to_contain_text("What Happens Next")
        assert next_steps.count() > 0, "No step items rendered in 'What Happens Next' section."
        for idx in range(next_steps.count()):
            step_el = next_steps.nth(idx)
            expect(step_el).to_be_visible()
            assert step_el.inner_text().strip(), f"What Happens Next step {idx} has empty content."
        logger.info(f"Verified 'What Happens Next' section with {next_steps.count()} steps.")

        # Steps 5-8: Made With Silhouette heading and dynamic video card extraction
        made_sec = creator_rewards_page.get_made_with_silhouette_section()
        made_heading = creator_rewards_page.get_made_with_silhouette_heading()
        made_sec.scroll_into_view_if_needed()
        expect(made_heading).to_be_visible()
        expect(made_heading).to_contain_text("Made With Silhouette")

        video_cards = creator_rewards_page.get_video_cards()
        total_cards = video_cards.count()
        assert total_cards > 0, "Expected video cards in 'Made With Silhouette' gallery, found 0."

        cards_meta = creator_rewards_page.extract_video_cards_metadata()
        assert all(c["has_video_ref"] for c in cards_meta), (
            f"Some video cards lack valid video src/data-src references: {cards_meta}"
        )
        visible_cards_count = sum(1 for c in cards_meta if c["visible"])
        assert visible_cards_count > 0, "No video cards are visible in the carousel."
        logger.info(
            f"Verified {total_cards} video cards ({visible_cards_count} currently visible in viewport); "
            f"all carry valid media references."
        )

        # Capture browser console errors specifically during video interaction
        video_console_errors: List[str] = []

        def _on_console(msg) -> None:
            if msg.type == "error":
                video_console_errors.append(msg.text)

        creator_rewards_page.page.on("console", _on_console)
        try:
            # Steps 9-18: Hover, click, controls & fullscreen expand/restore on first card
            player_info = creator_rewards_page.inspect_first_video_card_interactions()
        finally:
            try:
                creator_rewards_page.page.remove_listener("console", _on_console)
            except Exception:
                pass

        assert player_info["playpause_visible"], "Video player Play/Pause control not visible on hover."
        assert player_info["fullscreen_btn_visible"], "Video player Fullscreen control not visible."

        # Verify expand/restore fullscreen behavior
        assert player_info["expanded_fullscreen_class"] or player_info["expanded_dom_fullscreen"], (
            f"Clicking fullscreen button did not enter expanded/fullscreen state: {player_info}"
        )
        assert player_info["restored_cleanly"], (
            f"Video player did not cleanly exit fullscreen/restore state: {player_info}"
        )

        # Verify page remains usable after restoring player
        expect(made_heading).to_be_visible()
        expect(creator_rewards_page.get_submit_creation_cta()).to_be_enabled()

        # Log any captured console errors (note unrelated third-party telemetry if any)
        logger.info(f"Console errors observed during video interaction: {video_console_errors}")
        video_specific_errors = [e for e in video_console_errors if "ugc_video" in e.lower()]
        assert not video_specific_errors, f"Video asset console errors encountered: {video_specific_errors}"

        request.node.user_properties.append(("video_cards_count", total_cards))
        request.node.user_properties.append(("video_console_errors", video_console_errors))

        creator_rewards_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-CRW-003 PASSED: What Happens Next & Video Gallery Verified ==========")

    def test_e2e_crw_004_guidelines_terms_and_common_questions(
        self,
        creator_rewards_page: CreatorRewardsPage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-CRW-004: Guidelines, Terms & Common Questions.

        1. Navigate to Creator Rewards page.
        2. Locate 'Creator Guidelines' section, scroll into view, verify heading & content.
        3. Locate 'Terms & Conditions' section, verify heading & content.
        4. Locate 'Common Questions' FAQ section, verify heading & accordion items count > 0.
        5. Iterate through every FAQ item dynamically: verify question visible, click, verify
           answer panel visible with non-empty text, verify ARIA expanded state, and record
           whether accordion allows single or multiple open items simultaneously.
        """
        logger.info("========== EXECUTING E2E-CRW-004: Guidelines, Terms & Common Questions ==========")

        creator_rewards_page.open_creator_rewards()

        # Steps 2-4: Creator Guidelines section
        guide_sec = creator_rewards_page.get_creator_guidelines_section()
        guide_heading = creator_rewards_page.get_creator_guidelines_heading()
        guide_items = creator_rewards_page.get_creator_guidelines_items()
        guide_sec.scroll_into_view_if_needed()
        expect(guide_sec).to_be_visible()
        expect(guide_heading).to_be_visible()
        expect(guide_heading).to_contain_text("Creator Guidelines")
        assert guide_items.count() > 0, "Creator Guidelines contains no rule items."
        assert len(guide_sec.inner_text().strip()) > 0, "Creator Guidelines section text is empty."
        logger.info(f"Verified 'Creator Guidelines' section with {guide_items.count()} items.")

        # Steps 5-6: Terms & Conditions section
        terms_sec = creator_rewards_page.get_terms_section()
        terms_heading = creator_rewards_page.get_terms_heading()
        terms_content = creator_rewards_page.get_terms_content()
        terms_sec.scroll_into_view_if_needed()
        expect(terms_sec).to_be_visible()
        expect(terms_heading).to_be_visible()
        expect(terms_heading).to_contain_text("Terms & Conditions")
        expect(terms_content).to_be_visible()
        assert len(terms_content.inner_text().strip()) > 0, "Terms & Conditions content is empty."
        logger.info("Verified 'Terms & Conditions' section heading and content.")

        # Steps 7-15: Common Questions FAQ accordion
        faq_sec = creator_rewards_page.get_faq_section()
        faq_heading = creator_rewards_page.get_faq_heading()
        faq_items = creator_rewards_page.get_faq_items()

        faq_sec.scroll_into_view_if_needed()
        expect(faq_heading).to_be_visible()
        expect(faq_heading).to_contain_text("Common Questions")
        faq_count = faq_items.count()
        assert faq_count > 0, "Expected FAQ accordion items > 0, found 0."

        faq_summary = creator_rewards_page.expand_and_verify_all_faqs()
        assert len(faq_summary["items"]) == faq_count, (
            f"Expected all {faq_count} FAQs to expand, expanded {len(faq_summary['items'])}"
        )
        logger.info(
            f"Verified all {faq_count} FAQ items expanded cleanly | "
            f"Accordion behavior observed: {faq_summary['accordion_mode']}"
        )

        request.node.user_properties.append(("guidelines_items", guide_items.count()))
        request.node.user_properties.append(("faq_count", faq_count))
        request.node.user_properties.append(("faq_accordion_mode", faq_summary["accordion_mode"]))

        creator_rewards_page.capture_evidence_screenshot(request.node.name)
        logger.info("========== E2E-CRW-004 PASSED: Guidelines, Terms & Common Questions Verified ==========")

