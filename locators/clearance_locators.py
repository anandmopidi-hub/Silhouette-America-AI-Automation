"""Encapsulated locators for Silhouette America Clearance / Sale Items module."""


class ClearanceLocators:
    """Encapsulates all selectors for the Clearance / Sale Items page and promotional navigation."""

    # -------------------------------------------------------------------------
    # Header Navigation
    # -------------------------------------------------------------------------
    CLEARANCE_MENU_ITEM = "li[data-menu='clearmenu'], nav.desktop-menu li:has-text('Clearance')"
    CLEARANCE_PANEL = "#clearmenu-panel, [data-menu-panel='clearmenu']"
    SALE_ITEMS_LINK = "#clearmenu-panel a[href$='/clearance'], #clearmenu-panel a:has-text('Sale Items')"
    COOKIE_ACCEPT_BUTTON = "#btn-cookie-allow, button:has-text('I Agree'), .cookie-btn"

    # -------------------------------------------------------------------------
    # Hero Banner & Page Headings
    # -------------------------------------------------------------------------
    HERO_SECTION = ".silhouette-banner, .banner-container, .banner-content"
    HERO_HEADING = ".banner-content h2, .silhouette-banner h2, h2:has-text('Real Deals'), h1.banner-subtitle, .banner-container h2"
    PAGE_H1_TITLE = "h1.banner-subtitle, h1.page-title, h1"

    # -------------------------------------------------------------------------
    # Layered Navigation / Filters Sidebar
    # -------------------------------------------------------------------------
    FILTER_SIDEBAR = "#layered-filter-block, .block.filter, .sidebar-main"
    FILTER_GROUPS = ".filter-options-item"
    FILTER_GROUP_TITLE = ".filter-options-title"
    FILTER_GROUP_CONTENT = ".filter-options-content"
    FILTER_OPTION_LINKS = ".filter-options-content a"
    FILTER_OPTION_ITEMS = ".filter-options-content li"
    ACTIVE_FILTER_BLOCK = ".filter-current, .block-actions.filter-actions, .filter-value"
    ACTIVE_FILTER_ITEMS = ".filter-current .item, .filter-current li, .amshopby-item"
    FILTER_CLEAR_ALL_BTN = (
        ".sa-filter-clear-all-desktop, .filter-clear, a.action.clear, .filter-actions a, a:has-text('Clear All')"
    )

    # -------------------------------------------------------------------------
    # Product Grid & Product Cards
    # -------------------------------------------------------------------------
    PRODUCT_GRID = ".products.grid, .products-grid, .products.list"
    PRODUCT_CARDS = ".products.grid .product-item, .product-item"
    PRODUCT_CARD_IMAGE = "img.product-image-photo, .product-image-container img"
    PRODUCT_CARD_TITLE = ".product-item-name a, a.product-item-link, strong.product-name a"
    PRODUCT_CARD_PRICE_BOX = ".price-box"
    PRODUCT_CARD_OLD_PRICE = ".old-price .price, [data-price-type='oldPrice'] .price"
    PRODUCT_CARD_SPECIAL_PRICE = ".special-price .price, [data-price-type='finalPrice'] .price"
    PRODUCT_CARD_PRICE_REGULAR = ".price-container .price, span.price"
    PRODUCT_CARD_DISCOUNT_BADGE = ".badge:has-text('Off'), [class*='discount'], .product-label:has-text('Off'), span:has-text('Off')"
    PRODUCT_CARD_CLEARANCE_BADGE = ".badge:has-text('Clearance'), [class*='clearance'], .product-label:has-text('Clearance'), span:has-text('Clearance')"
    PRODUCT_CARD_EXPLORE_CTA = "a:has-text('Explore Options'), button:has-text('Explore Options'), .action:has-text('Explore Options')"
    PRODUCT_CARD_ALL_CTAS = ".actions-primary a, .actions-primary button, a.action.tocart, .action"

    # -------------------------------------------------------------------------
    # Sorter Dropdown & Ordering
    # -------------------------------------------------------------------------
    SORTER_DROPDOWN = "#sorter, select[data-role='sorter']"
    SORTER_OPTIONS = "#sorter option, select[data-role='sorter'] option"
    SORTER_DIRECTION_SWITCHER = ".action.sorter-action, a[data-role='direction-switcher']"

    # -------------------------------------------------------------------------
    # Editorial Sections & Customer Reviews
    # -------------------------------------------------------------------------
    CUSTOMER_REVIEWS_HEADING = "h2:has-text('Why our customers love Silhouette')"
    EDITORIAL_QUALITY_HEADING = (
        "h2:has-text('The Same Silhouette Quality — at Genuine Clearance Prices'), "
        "h2:has-text('The Same Silhouette Quality')"
    )
    EDITORIAL_FIND_HEADING = (
        "h2:has-text(\"What You'll Find in the Silhouette Clearance Section\"), "
        "h2:has-text('What You\\'ll Find')"
    )
    EDITORIAL_TIPS_HEADING = (
        "h2:has-text('Smart Tips for Shopping the Silhouette Clearance Section'), "
        "h2:has-text('Smart Tips')"
    )

    # -------------------------------------------------------------------------
    # Common Questions FAQ Accordion
    # -------------------------------------------------------------------------
    FAQ_COMMON_QUESTIONS_HEADING = "h2:has-text('Common Questions')"
    FAQ_ITEMS = ".faq_wrapper"
    FAQ_QUESTION = ".faq_product_question, [data-role='trigger'], [data-role='title'], h3, .title"
    FAQ_ANSWER = ".faq_product_answer, [data-role='content']"

