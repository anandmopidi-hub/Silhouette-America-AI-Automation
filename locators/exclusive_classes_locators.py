"""Encapsulated locators for Silhouette America Exclusive Classes module.

Discovered and verified dynamically from live production application DOM.
Target URL: https://www.silhouetteamerica.com/exclusive-class
"""


class ExclusiveClassesLocators:
    """Encapsulated locators for Silhouette America Exclusive Classes module."""

    # -------------------------------------------------------------------------
    # Navigation from Homepage Header
    # -------------------------------------------------------------------------
    NAV_RESOURCES_MENU = (
        "nav.desktop-menu li[data-menu='resourcemenu'], "
        "nav.desktop-menu li.menu-component:has(#resourcemenu-panel), "
        "nav.desktop-menu a.fmlink:has-text('Resources')"
    )
    NAV_RESOURCES_PANEL = "#resourcemenu-panel"
    NAV_EXCLUSIVE_CLASSES_LINK = (
        "nav.desktop-menu #resourcemenu-panel a[href*='exclusive-class'], "
        "#resourcemenu-panel a[href*='exclusive-class']"
    )

    # -------------------------------------------------------------------------
    # Hero Banner & Page Section Headings
    # -------------------------------------------------------------------------
    PAGE_HERO_SECTION = "section.exclusive-classes-hero"
    PAGE_HERO_TITLE_LINES = ".exclusive-classes-hero-title-line"
    PAGE_HERO_HEADING = (
        ".exclusive-classes-hero-title-line, "
        ".exclusive-classes-hero h1, "
        ".exclusive-classes-hero"
    )
    PAGE_HERO_BADGE = ".exclusive-classes-hero-badge-text"
    PAGE_HERO_DESCRIPTION = ".exclusive-classes-hero-description"

    # Archive / Past Classes Section
    ARCHIVE_SECTION = "section.exclusive-classes-archive"
    ARCHIVE_SECTION_TITLE = "#past-classes-title, .exclusive-classes-archive-title"
    ARCHIVE_SECTION_DESCRIPTION = ".exclusive-classes-archive-description"
    ARCHIVE_CONTAINER = "#extraclass-listing, .past-classes-archive"

    # -------------------------------------------------------------------------
    # Search Toolbar
    # -------------------------------------------------------------------------
    SEARCH_INPUT = "input#classes-search-input, .past-classes-archive-search-input"
    SEARCH_ICON = ".past-classes-archive-search-icon"
    SEARCH_LABEL = "label[for='classes-search-input']"

    # -------------------------------------------------------------------------
    # Class Cards Grid & Elements
    # -------------------------------------------------------------------------
    GRID_CONTAINER = "ul.past-classes-archive-grid, [data-role='grid']"
    CLASS_CARDS = "li.past-classes-archive-card"
    CARD_TITLE = ".past-classes-archive-card-title"
    CARD_DATE = ".past-classes-archive-card-date"
    CARD_DURATION = ".past-classes-archive-card-duration"
    CARD_IMAGE = ".past-classes-archive-card-image img"
    CARD_VIDEO_WRAPPER = ".past-classes-archive-card-video"
    LOADING_SPINNER = ".past-classes-archive-loading:not(.past-classes-archive-loading-hidden)"
    SKELETON_GRID = ".past-classes-archive-skeleton-grid"

    # -------------------------------------------------------------------------
    # Empty State (No Search Results)
    # -------------------------------------------------------------------------
    EMPTY_STATE_ITEM = "li.past-classes-archive-empty, [data-role='empty']"
    EMPTY_STATE_MESSAGE = "li.past-classes-archive-empty p, [data-role='empty'] p"

    # -------------------------------------------------------------------------
    # Sorting Dropdown
    # -------------------------------------------------------------------------
    SORT_WRAPPER = ".custom-sort-dropdown, [data-role='custom-sort']"
    SORT_TOGGLE_BUTTON = "button#classes-sort-toggle, .custom-sort-toggle"
    SORT_CURRENT_LABEL = ".custom-sort-label, [data-role='custom-sort-label']"
    SORT_LISTBOX = "ul#classes-sort-listbox, .custom-sort-menu"
    SORT_OPTIONS = "#classes-sort-listbox li.custom-sort-option, .custom-sort-option"
    SORT_HIDDEN_INPUT = "input#classes-sort-select"

