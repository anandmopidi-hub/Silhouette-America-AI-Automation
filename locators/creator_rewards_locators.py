"""Encapsulated locators for Silhouette America Creator Rewards module.

Discovered and verified dynamically from live production application DOM.
Target URL: https://www.silhouetteamerica.com/creator-rewards
"""


class CreatorRewardsLocators:
    """Encapsulated locators for Silhouette America Creator Rewards."""

    # -------------------------------------------------------------------------
    # Homepage Navigation -> Resources -> Creators Rewards
    # -------------------------------------------------------------------------
    DESKTOP_NAV = "nav.desktop-menu"
    NAV_RESOURCES_MENU = "nav.desktop-menu li[data-menu='resourcemenu']"
    NAV_RESOURCES_PANEL = "#resourcemenu-panel"
    NAV_CREATOR_REWARDS_LINK = "#resourcemenu-panel a[href*='creator-rewards']"

    # -------------------------------------------------------------------------
    # Hero Section
    # -------------------------------------------------------------------------
    HERO_SECTION = "section.ugc-hero"
    HERO_HEADING = "section.ugc-hero h1#ugc-hero-heading"
    HERO_CTA_SUBMIT = "section.ugc-hero a.ugc-cta"

    # -------------------------------------------------------------------------
    # How It Works Section & Step Cards
    # -------------------------------------------------------------------------
    HOW_IT_WORKS_SECTION = "section.ugc-how"
    HOW_IT_WORKS_HEADING = "h2#ugc-how-heading"
    HOW_IT_WORKS_CARDS = "section.ugc-how .ugc-how-grid article.ugc-how-card"
    STEP_CARD_TITLE = ".ugc-how-card-title"
    STEP_USER_GUIDE_LINK = "a.ugc-how-link"

    # -------------------------------------------------------------------------
    # Submit Your Creation Section & Form
    # -------------------------------------------------------------------------
    SUBMIT_SECTION = "section#ugc-submit"
    SUBMIT_HEADING = "h2#ugc-submit-heading"
    SUBMIT_FORM = "form#ugc-creator-rewards-form"
    SUBMIT_FORM_FIELDS = "form#ugc-creator-rewards-form input, form#ugc-creator-rewards-form select, form#ugc-creator-rewards-form textarea"
    SUBMIT_FORM_BUTTON = "form#ugc-creator-rewards-form button[type='submit'], form#ugc-creator-rewards-form button"

    # -------------------------------------------------------------------------
    # What Happens Next Section
    # -------------------------------------------------------------------------
    WHAT_HAPPENS_NEXT_SECTION = "section.ugc-next"
    WHAT_HAPPENS_NEXT_HEADING = "h2#ugc-next-heading"
    WHAT_HAPPENS_NEXT_STEPS = "section.ugc-next ol.ugc-next-steps li.ugc-next-step"

    # -------------------------------------------------------------------------
    # Made With Silhouette Video Gallery
    # -------------------------------------------------------------------------
    MADE_SECTION = "section.ugc-made"
    MADE_HEADING = "h2#ugc-made-heading"
    VIDEO_CARDS = "section.ugc-made figure.ugc-made-card"
    VIDEO_ELEMENT = "video.ugc-made-video"
    VIDEO_CONTROLS = ".ugc-made-controls"
    VIDEO_PLAYPAUSE_BTN = "button.ugc-made-btn--playpause"
    VIDEO_MUTE_BTN = "button.ugc-made-btn--mute"
    VIDEO_FULLSCREEN_BTN = "button.ugc-made-btn--fullscreen"

    # -------------------------------------------------------------------------
    # Creator Guidelines Section
    # -------------------------------------------------------------------------
    GUIDELINES_SECTION = "section.ugc-guide"
    GUIDELINES_HEADING = "h2#ugc-guide-heading"
    GUIDELINES_CARDS = "section.ugc-guide .ugc-guide-card"
    GUIDELINES_LIST_ITEMS = "section.ugc-guide .ugc-guide-item"

    # -------------------------------------------------------------------------
    # Terms & Conditions Section
    # -------------------------------------------------------------------------
    TERMS_SECTION = "section#ugc-terms-and-conditions"
    TERMS_HEADING = "h2#ugc-privacy-heading"
    TERMS_CONTENT = "section#ugc-terms-and-conditions .ugc-privacy-content"

    # -------------------------------------------------------------------------
    # Common Questions (FAQ Accordion)
    # -------------------------------------------------------------------------
    FAQ_SECTION = ".faq-split-layout-wrapper"
    FAQ_HEADING = ".faq-split-left h2"
    FAQ_ITEMS = ".faq_product_main-wrapper .faq_wrapper[data-role='collapsible']"
    FAQ_QUESTION = "h3.faq_product_question[data-role='trigger']"
    FAQ_ANSWER = "div.faq_product_answer[data-role='content']"

