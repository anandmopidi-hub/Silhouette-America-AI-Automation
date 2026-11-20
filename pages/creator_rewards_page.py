"""Page Object for Silhouette America Creator Rewards module.

Target URL: https://www.silhouetteamerica.com/creator-rewards
"""
from typing import Any, Dict, List, Optional
from urllib.parse import unquote
from playwright.sync_api import Locator, Page, Response, expect

from locators.creator_rewards_locators import CreatorRewardsLocators
from pages.base_page import BasePage
from utils.logger import logger


class CreatorRewardsPage(BasePage):
    """Page Object covering Silhouette America Creator Rewards (/creator-rewards)."""

    def __init__(self, page: Page, config: Optional[Any] = None) -> None:
        super().__init__(page=page, config=config)
        self.creator_rewards_path = "creator-rewards"

    # =========================================================================
    # E2E-CRW-001: Homepage Navigation & Hero Section
    # =========================================================================

    def open_homepage_and_wait_for_nav(self) -> None:
        """Open homepage, resolve Cloudflare/cookies, and wait for desktop navigation."""
        logger.info("Opening Silhouette America homepage...")
        self.goto("", wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()

        nav = self.page.locator(CreatorRewardsLocators.DESKTOP_NAV).first
        expect(nav).to_be_visible(timeout=10000)

    def open_creator_rewards(self) -> Optional[Response]:
        """Navigate directly to the Creator Rewards page."""
        logger.info(f"Navigating directly to Creator Rewards: {self.creator_rewards_path}")
        response = self.goto(self.creator_rewards_path, wait_until="domcontentloaded")
        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()
        expect(self.get_hero_heading()).to_be_visible(timeout=10000)
        return response

    def get_resources_menu(self) -> Locator:
        """Return locator for the Resources top-level navigation menu item."""
        return self.page.locator(CreatorRewardsLocators.NAV_RESOURCES_MENU).first

    def open_resources_menu(self) -> Locator:
        """Hover or click Resources menu so its mega-menu panel opens, and return panel locator."""
        res_menu = self.get_resources_menu()
        expect(res_menu).to_be_visible(timeout=5000)

        logger.info("Hovering over 'Resources' navigation menu...")
        res_menu.hover()
        panel = self.page.locator(CreatorRewardsLocators.NAV_RESOURCES_PANEL).first
        try:
            expect(panel).to_be_visible(timeout=3000)
        except AssertionError:
            logger.info("Hover did not expand Resources panel; clicking Resources trigger...")
            res_menu.locator("button, a").first.click()
            expect(panel).to_be_visible(timeout=5000)
        return panel

    def get_creator_rewards_nav_link(self) -> Locator:
        """Return locator for the Creator Rewards link inside Resources panel."""
        return self.page.locator(CreatorRewardsLocators.NAV_CREATOR_REWARDS_LINK).first

    def navigate_to_creator_rewards(self) -> Dict[str, Any]:
        """Extract href, click Creator Rewards nav link, and return navigation details."""
        link = self.get_creator_rewards_nav_link()
        expect(link).to_be_visible(timeout=5000)

        actual_href = link.get_attribute("href") or ""
        link_text = link.inner_text().strip()
        logger.info(f"Clicking Creator Rewards link '{link_text}' (href='{actual_href}')...")

        nav_status: Optional[int] = None
        with self.page.expect_navigation(wait_until="domcontentloaded", timeout=15000) as nav_info:
            link.click()
        resp = nav_info.value
        if resp:
            nav_status = resp.status

        self.wait_for_dom_content_loaded()
        self.handle_cloudflare_if_present()
        self.dismiss_cookie_consent_if_present()

        return {
            "link_text": link_text,
            "href": actual_href,
            "final_url": self.get_current_url(),
            "status": nav_status,
        }

    def get_hero_section(self) -> Locator:
        """Return locator for the Hero section."""
        return self.page.locator(CreatorRewardsLocators.HERO_SECTION).first

    def get_hero_heading(self) -> Locator:
        """Return locator for Hero heading rendered inside the Hero section."""
        return self.page.locator(CreatorRewardsLocators.HERO_HEADING).first

    # =========================================================================
    # E2E-CRW-002: How It Works, User Guide & Submit Your Creation CTA
    # =========================================================================

    def get_how_it_works_section(self) -> Locator:
        """Return locator for How It Works section."""
        return self.page.locator(CreatorRewardsLocators.HOW_IT_WORKS_SECTION).first

    def get_how_it_works_heading(self) -> Locator:
        """Return locator for How It Works heading."""
        return self.page.locator(CreatorRewardsLocators.HOW_IT_WORKS_HEADING).first

    def get_step_cards(self) -> Locator:
        """Return locator matching all How It Works step cards."""
        return self.page.locator(CreatorRewardsLocators.HOW_IT_WORKS_CARDS)

    def get_step_cards_content(self) -> List[Dict[str, str]]:
        """Extract title and full visible text for each step card dynamically."""
        cards = self.get_step_cards()
        results: List[Dict[str, str]] = []
        for idx in range(cards.count()):
            card = cards.nth(idx)
            expect(card).to_be_visible()
            title = card.locator(CreatorRewardsLocators.STEP_CARD_TITLE).first.inner_text().strip()
            body_text = card.inner_text().strip()
            results.append({"index": str(idx + 1), "title": title, "text": body_text})
        return results

    def get_step2_user_guide_link(self) -> Locator:
        """Locate the User Guide link dynamically within Step 2 card only."""
        step2_card = self.get_step_cards().nth(1)
        return step2_card.locator(CreatorRewardsLocators.STEP_USER_GUIDE_LINK).first

    def open_user_guide_and_verify(self) -> Dict[str, Any]:
        """Click Step 2 User Guide link, handle new tab/same tab, inspect response, and return."""
        link = self.get_step2_user_guide_link()
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        target = link.get_attribute("target") or ""
        link_text = link.inner_text().strip()
        logger.info(f"Opening Step 2 '{link_text}' (target='{target}', href='{href}')...")

        captured_responses: List[Dict[str, Any]] = []

        def _on_response(resp: Response) -> None:
            try:
                captured_responses.append({
                    "url": resp.url,
                    "status": resp.status,
                    "content_type": resp.headers.get("content-type", ""),
                })
            except Exception:
                pass

        self.page.context.on("response", _on_response)

        opened_new_tab = False
        final_url = ""
        http_status: Optional[int] = None
        content_type = ""
        response_source = "unavailable"

        try:
            if target == "_blank":
                opened_new_tab = True
                with self.page.context.expect_page(timeout=10000) as new_pg_info:
                    link.click()
                new_pg = new_pg_info.value
                try:
                    new_pg.wait_for_load_state("domcontentloaded", timeout=10000)
                except Exception as e:
                    logger.debug(f"User Guide tab load notice: {e}")

                final_url = new_pg.url or href
                norm_href = unquote(href).lower()
                for r in captured_responses:
                    if norm_href in unquote(r["url"]).lower():
                        http_status = r["status"]
                        content_type = r["content_type"]
                        response_source = "browser_response"
                        break

                if not new_pg.is_closed():
                    new_pg.close()
                self.page.bring_to_front()
            else:
                with self.page.expect_navigation(wait_until="domcontentloaded", timeout=12000) as nav_info:
                    link.click()
                resp = nav_info.value
                final_url = self.page.url
                if resp:
                    http_status = resp.status
                    content_type = resp.headers.get("content-type", "")
                    response_source = "browser_navigation_response"
                self.go_back(wait_until="domcontentloaded")
                self.wait_for_dom_content_loaded()
        finally:
            try:
                self.page.context.remove_listener("response", _on_response)
            except Exception:
                pass

        if http_status is None and href:
            try:
                head_resp = self.page.context.request.head(href, timeout=10000)
                http_status = head_resp.status
                content_type = content_type or head_resp.headers.get("content-type", "")
                response_source = "context_request_head"
            except Exception as e:
                logger.warning(f"HEAD verification unavailable for '{href}': {e}")

        return {
            "text": link_text,
            "href": href,
            "final_url": final_url,
            "opened_in_new_tab": opened_new_tab,
            "http_status": http_status,
            "content_type": content_type,
            "response_source": response_source,
        }

    def get_submit_creation_cta(self) -> Locator:
        """Return locator for the primary 'Submit Your Creation' CTA in Hero section."""
        return self.page.locator(CreatorRewardsLocators.HERO_CTA_SUBMIT).first

    def click_submit_creation(self) -> Dict[str, Any]:
        """Click Submit Your Creation CTA and inspect resulting submission interface."""
        cta = self.get_submit_creation_cta()
        expect(cta).to_be_visible()
        expect(cta).to_be_enabled()
        cta_href = cta.get_attribute("href") or ""

        logger.info(f"Clicking 'Submit Your Creation' CTA (href='{cta_href}')...")
        cta.click()

        submit_section = self.page.locator(CreatorRewardsLocators.SUBMIT_SECTION).first
        submit_heading = self.page.locator(CreatorRewardsLocators.SUBMIT_HEADING).first
        submit_form = self.page.locator(CreatorRewardsLocators.SUBMIT_FORM).first
        form_fields = self.page.locator(CreatorRewardsLocators.SUBMIT_FORM_FIELDS)
        form_btn = self.page.locator(CreatorRewardsLocators.SUBMIT_FORM_BUTTON).first

        expect(submit_section).to_be_visible(timeout=5000)
        expect(submit_heading).to_be_visible(timeout=5000)
        expect(submit_form).to_be_visible(timeout=5000)

        return {
            "cta_href": cta_href,
            "current_url": self.get_current_url(),
            "submit_heading": submit_heading.inner_text().strip(),
            "form_visible": submit_form.is_visible(),
            "field_count": form_fields.count(),
            "submit_button_visible": form_btn.is_visible(),
            "submit_button_enabled": form_btn.is_enabled(),
        }

    # =========================================================================
    # E2E-CRW-003: What Happens Next & Video Gallery
    # =========================================================================

    def get_what_happens_next_section(self) -> Locator:
        """Return locator for What Happens Next section."""
        return self.page.locator(CreatorRewardsLocators.WHAT_HAPPENS_NEXT_SECTION).first

    def get_what_happens_next_heading(self) -> Locator:
        """Return locator for What Happens Next heading."""
        return self.page.locator(CreatorRewardsLocators.WHAT_HAPPENS_NEXT_HEADING).first

    def get_what_happens_next_steps(self) -> Locator:
        """Return locator for steps inside What Happens Next section."""
        return self.page.locator(CreatorRewardsLocators.WHAT_HAPPENS_NEXT_STEPS)

    def get_made_with_silhouette_section(self) -> Locator:
        """Return locator for Made With Silhouette gallery section."""
        return self.page.locator(CreatorRewardsLocators.MADE_SECTION).first

    def get_made_with_silhouette_heading(self) -> Locator:
        """Return locator for Made With Silhouette heading."""
        return self.page.locator(CreatorRewardsLocators.MADE_HEADING).first

    def get_video_cards(self) -> Locator:
        """Return locator matching all video cards in the gallery."""
        return self.page.locator(CreatorRewardsLocators.VIDEO_CARDS)

    def extract_video_cards_metadata(self) -> List[Dict[str, Any]]:
        """Inspect all video cards dynamically and collect src/data-src/aria-label attributes."""
        cards = self.get_video_cards()
        metadata: List[Dict[str, Any]] = []
        for idx in range(cards.count()):
            card = cards.nth(idx)
            video = card.locator(CreatorRewardsLocators.VIDEO_ELEMENT).first
            data_src = video.get_attribute("data-src") or ""
            src = video.get_attribute("src") or ""
            label = video.get_attribute("aria-label") or ""
            metadata.append({
                "index": idx,
                "visible": card.is_visible(),
                "label": label,
                "data_src": data_src,
                "src": src,
                "has_video_ref": bool(data_src or src),
            })
        return metadata

    def inspect_first_video_card_interactions(self) -> Dict[str, Any]:
        """Hover, click, expand fullscreen, and restore the first video card; inspect real states."""
        card = self.get_video_cards().first
        video = card.locator(CreatorRewardsLocators.VIDEO_ELEMENT).first
        controls = card.locator(CreatorRewardsLocators.VIDEO_CONTROLS).first
        playpause_btn = card.locator(CreatorRewardsLocators.VIDEO_PLAYPAUSE_BTN).first
        fullscreen_btn = card.locator(CreatorRewardsLocators.VIDEO_FULLSCREEN_BTN).first

        card.scroll_into_view_if_needed()
        expect(card).to_be_visible()

        # Hover over video card and inspect controls/playback state
        card.hover()
        expect(controls).to_be_visible(timeout=5000)

        # Wait briefly for lazy-load src assignment or playback readiness (non-blocking)
        try:
            self.page.wait_for_function(
                "(el) => Boolean(el.getAttribute('src') || el.getAttribute('data-src'))",
                arg=video.element_handle(),
                timeout=4000,
            )
        except Exception:
            pass

        hover_state = video.evaluate(
            "v => ({ src: v.getAttribute('src') || v.currentSrc || '', "
            "dataSrc: v.getAttribute('data-src') || '', "
            "paused: v.paused, readyState: v.readyState, currentTime: v.currentTime })"
        )
        logger.info(f"Video card hover state: {hover_state}")

        # Click video card and inspect resulting playback/modal state
        paused_before_click = bool(video.evaluate("v => v.paused"))
        card.click()
        paused_after_click = bool(video.evaluate("v => v.paused"))
        logger.info(f"Video card click: paused {paused_before_click} -> {paused_after_click}")

        # Inspect controls visibility
        play_btn_visible = playpause_btn.is_visible()
        fs_btn_visible = fullscreen_btn.is_visible()
        fs_label_before = fullscreen_btn.get_attribute("aria-label") or ""

        # Expand / Fullscreen control check
        expanded_fullscreen_class = False
        expanded_dom_fullscreen = False
        fs_label_expanded = ""
        restored_cleanly = False

        if fs_btn_visible and fullscreen_btn.is_enabled():
            logger.info("Clicking fullscreen expand control...")
            fullscreen_btn.click()
            try:
                self.page.wait_for_function(
                    "() => Boolean(document.fullscreenElement) || Boolean(document.querySelector('.ugc-made-card--fullscreen'))",
                    timeout=3000,
                )
            except Exception:
                pass

            card_cls_expanded = card.get_attribute("class") or ""
            expanded_fullscreen_class = "ugc-made-card--fullscreen" in card_cls_expanded
            expanded_dom_fullscreen = bool(self.page.evaluate("() => Boolean(document.fullscreenElement)"))
            fs_label_expanded = fullscreen_btn.get_attribute("aria-label") or ""
            logger.info(
                f"Expanded state -> class={expanded_fullscreen_class}, "
                f"domFullscreen={expanded_dom_fullscreen}, aria-label='{fs_label_expanded}'"
            )

            # Minimize / Exit fullscreen control
            logger.info("Restoring player from fullscreen...")
            if fullscreen_btn.is_visible():
                fullscreen_btn.click()
            else:
                self.page.evaluate("() => document.exitFullscreen && document.exitFullscreen()")

            try:
                self.page.wait_for_function(
                    "() => !document.fullscreenElement && !document.querySelector('.ugc-made-card--fullscreen')",
                    timeout=3000,
                )
            except Exception:
                pass

            card_cls_restored = card.get_attribute("class") or ""
            dom_fs_after = bool(self.page.evaluate("() => Boolean(document.fullscreenElement)"))
            restored_cleanly = ("ugc-made-card--fullscreen" not in card_cls_restored) and not dom_fs_after
            logger.info(f"Restored cleanly: {restored_cleanly}")

        return {
            "hover_state": hover_state,
            "paused_before_click": paused_before_click,
            "paused_after_click": paused_after_click,
            "playpause_visible": play_btn_visible,
            "fullscreen_btn_visible": fs_btn_visible,
            "fs_label_before": fs_label_before,
            "expanded_fullscreen_class": expanded_fullscreen_class,
            "expanded_dom_fullscreen": expanded_dom_fullscreen,
            "fs_label_expanded": fs_label_expanded,
            "restored_cleanly": restored_cleanly,
        }

    # =========================================================================
    # E2E-CRW-004: Guidelines, Terms & Common Questions (FAQ)
    # =========================================================================

    def get_creator_guidelines_section(self) -> Locator:
        """Return locator for Creator Guidelines section."""
        return self.page.locator(CreatorRewardsLocators.GUIDELINES_SECTION).first

    def get_creator_guidelines_heading(self) -> Locator:
        """Return locator for Creator Guidelines heading."""
        return self.page.locator(CreatorRewardsLocators.GUIDELINES_HEADING).first

    def get_creator_guidelines_items(self) -> Locator:
        """Return locator matching Do's/Don'ts guideline list items."""
        return self.page.locator(CreatorRewardsLocators.GUIDELINES_LIST_ITEMS)

    def get_terms_section(self) -> Locator:
        """Return locator for Terms & Conditions section."""
        return self.page.locator(CreatorRewardsLocators.TERMS_SECTION).first

    def get_terms_heading(self) -> Locator:
        """Return locator for Terms & Conditions heading."""
        return self.page.locator(CreatorRewardsLocators.TERMS_HEADING).first

    def get_terms_content(self) -> Locator:
        """Return locator for Terms & Conditions text block."""
        return self.page.locator(CreatorRewardsLocators.TERMS_CONTENT).first

    def get_faq_section(self) -> Locator:
        """Return locator for Common Questions FAQ section."""
        return self.page.locator(CreatorRewardsLocators.FAQ_SECTION).first

    def get_faq_heading(self) -> Locator:
        """Return locator for Common Questions heading."""
        return self.page.locator(CreatorRewardsLocators.FAQ_HEADING).first

    def get_faq_items(self) -> Locator:
        """Return locator matching all FAQ accordion items."""
        return self.page.locator(CreatorRewardsLocators.FAQ_ITEMS)

    def expand_and_verify_all_faqs(self) -> Dict[str, Any]:
        """Iterate through all FAQ items, expand each dynamically, and verify behavior."""
        items = self.get_faq_items()
        total = items.count()
        logger.info(f"Inspecting {total} FAQ accordion items dynamically...")

        faq_results: List[Dict[str, Any]] = []
        single_open_observed = True

        for idx in range(total):
            item = items.nth(idx)
            question = item.locator(CreatorRewardsLocators.FAQ_QUESTION).first
            answer = item.locator(CreatorRewardsLocators.FAQ_ANSWER).first

            question.scroll_into_view_if_needed()
            expect(question).to_be_visible()
            q_text = question.inner_text().strip()
            assert q_text, f"FAQ item {idx} has empty question text."

            question.click()
            expect(answer).to_be_visible(timeout=5000)
            expect(item).to_have_attribute("aria-expanded", "true")

            a_text = answer.inner_text().strip()
            assert len(a_text) > 0, f"FAQ item {idx} ('{q_text}') answer panel is empty."

            # Verify whether opening this item collapsed the previous item (single-open accordion)
            prev_still_expanded = None
            if idx > 0:
                prev_item = items.nth(idx - 1)
                prev_expanded_attr = prev_item.get_attribute("aria-expanded")
                prev_still_expanded = prev_expanded_attr == "true"
                if prev_still_expanded:
                    single_open_observed = False

            faq_results.append({
                "index": idx,
                "question": q_text,
                "answer_length": len(a_text),
                "aria_expanded": item.get_attribute("aria-expanded"),
                "prev_still_expanded": prev_still_expanded,
            })

        return {
            "total_faqs": total,
            "accordion_mode": "single-open" if single_open_observed else "multi-open",
            "items": faq_results,
        }

