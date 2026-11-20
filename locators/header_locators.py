"""Encapsulated locators for Silhouette America Header Navigation components.

Covers top-level header navigation items, mega-menu dropdown panels,
and destination page verification elements.
"""


class HeaderLocators:
    """Locators for Silhouette America Header Navigation."""

    # -------------------------------------------------------------------------
    # Header Branding & Navigation Structure
    # -------------------------------------------------------------------------
    HEADER = "header, .page-header"
    LOGO = "a.logo, header .hlog a.logo"
    NAV_CONTAINER = "nav, .navigation, .header-navigation, header ul.header-menu"
    COOKIE_ACCEPT_BUTTON = "button[data-amgdprcookie-js='accept'], button:has-text('I Agree'), button:has-text('I agree'), .amgdprcookie-button.-allow"

    # -------------------------------------------------------------------------
    # Top-Level Navigation Menu Items (data-menu based)
    # -------------------------------------------------------------------------
    TOP_LEVEL_ITEMS = "header li[data-menu], nav li[data-menu]"
    SHOP_ITEM = "li[data-menu='shopmenu']"
    SHOP_LINK = "li[data-menu='shopmenu'] a"
    SOFTWARE_ITEM = "li[data-menu='softwaremenu']"
    MACHINE_ITEM = "li[data-menu='machinemenu']"
    TOOLS_MATS_ITEM = "li[data-menu='toolmatmmenu']"
    MATERIALS_ITEM = "li[data-menu='materialmenu']"
    ACCESSORIES_ITEM = "li[data-menu='accemenu']"
    CLUB_SILHOUETTE_ITEM = "li[data-menu='clubsilmenu']"
    CLUB_SILHOUETTE_LINK = "li[data-menu='clubsilmenu'] a"
    CLEARANCE_ITEM = "li[data-menu='clearmenu']"
    RESOURCES_ITEM = "li[data-menu='resourcemenu']"

    # -------------------------------------------------------------------------
    # Mega-Menu Dropdown Panels
    # -------------------------------------------------------------------------
    SOFTWARE_PANEL = "#softwaremenu-panel"
    MACHINE_PANEL = "#machinemenu-panel"
    TOOLS_MATS_PANEL = "#toolmatmmenu-panel"
    MATERIALS_PANEL = "#materialmenu-panel"
    ACCESSORIES_PANEL = "#accemenu-panel"
    CLEARANCE_PANEL = "#clearmenu-panel"
    RESOURCES_PANEL = "#resourcemenu-panel"

    # -------------------------------------------------------------------------
    # Category Landing / Primary Destination Links in Mega-Menus
    # -------------------------------------------------------------------------
    SOFTWARE_PRIMARY_LINK = "#softwaremenu-panel a[href$='/software'], #softwaremenu-panel a:has-text('View All')"
    MACHINE_PRIMARY_LINK = "#machinemenu-panel a[href$='/machines'], #machinemenu-panel a:has-text('View All')"
    TOOLS_MATS_PRIMARY_LINK = "#toolmatmmenu-panel a[href*='machine-tools-mats'], #toolmatmmenu-panel a:has-text('Shop All')"
    MATERIALS_PRIMARY_LINK = "#materialmenu-panel a[href$='/material'], #materialmenu-panel a:has-text('Shop All')"
    ACCESSORIES_PRIMARY_LINK = "#accemenu-panel a[href$='/accessories-parts'], #accemenu-panel a:has-text('Shop All')"
    CLEARANCE_PRIMARY_LINK = "#clearmenu-panel a[href$='/clearance'], #clearmenu-panel a:has-text('Sale Items')"

    # -------------------------------------------------------------------------
    # Dropdown Child Links Selector
    # -------------------------------------------------------------------------
    PANEL_CHILD_LINKS = "a"

    # -------------------------------------------------------------------------
    # Destination Page Verification
    # -------------------------------------------------------------------------
    PAGE_HEADING = "h1, .page-title, h1.page-title, .base"
    PAGE_SUBTITLE = ".page-title-wrapper, .category-description"
    NOT_FOUND_INDICATORS = ".page-title:has-text('404'), h1:has-text('404'), text='Whoops, our bad', text='Page Not Found', .error-404"
    CLEARANCE_PRODUCT_ITEMS = ".products.list .product-item, .products.grid .product-item, .product-item"

