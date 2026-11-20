"""Encapsulated locators for Silhouette America Product User Manuals module.

Discovered and verified dynamically from live production application DOM.
Target URL: https://www.silhouetteamerica.com/product-user-manual
"""


class ProductUserManualsLocators:
    """Encapsulated locators for Silhouette America Product User Manuals."""

    # -------------------------------------------------------------------------
    # Page Headings & Static Sections
    # -------------------------------------------------------------------------
    MAIN_HEADING = "h1.user-manuals__title"
    CUSTOMER_SECTION_HEADING = "h2.sa-reviews-slider-sidebar__title"

    # -------------------------------------------------------------------------
    # Navigation Tabs (role='tablist')
    # -------------------------------------------------------------------------
    TABS_CONTAINER = "nav.user-manuals__tabs[role='tablist']"
    ALL_TABS = "nav.user-manuals__tabs button.user-manuals__tab[role='tab']"
    TAB_MACHINE = "button#user-manuals-tab-machine"
    TAB_SOFTWARE = "button#user-manuals-tab-software"
    TAB_SUPPLY = "button#user-manuals-tab-supply"
    TAB_LEGACY = "button#user-manuals-tab-legacy"

    # -------------------------------------------------------------------------
    # Tab Panels
    # -------------------------------------------------------------------------
    PANEL_MACHINE = "#user-manuals-panel-machine"
    PANEL_SOFTWARE = "#user-manuals-panel-software"
    PANEL_SUPPLY = "#user-manuals-panel-supply"
    PANEL_LEGACY = "#user-manuals-panel-legacy"
    PANEL_SECTION_TITLE = ".user-manuals__section-title"

    # -------------------------------------------------------------------------
    # Product Manual Cards & Actions
    # -------------------------------------------------------------------------
    MANUAL_CARDS = "article.manual-card"
    CARD_TITLE = "h3.manual-card__name"
    CARD_ACTIONS = ".manual-card__actions"
    USER_MANUAL_LINK = "a.manual-card__btn:has-text('User Manual')"
    SAFETY_MANUAL_LINK = "a.manual-card__btn:has-text('Safety Manual')"
    VIEW_PRODUCT_LINK = "a.manual-card__btn--product, a.manual-card__btn:has-text('View Product')"

    # -------------------------------------------------------------------------
    # Destination PDP Verification
    # -------------------------------------------------------------------------
    PDP_HEADING = "h1.page-title span, h1.page-title, main h1, h1"
    PDP_SUBHEADINGS = "main h2, h2"
    NOT_FOUND_INDICATORS = "h1:has-text('404'), h1:has-text('Not Found'), h1:has-text('Whoops'), .error-404"

