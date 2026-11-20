class Different_PDP_Locators:
    """Centralized, encapsulated locators for all Silhouette America Product Detail Pages (PDP).

    Supports:
    - E2E-Different_PDP-001 (Machine PDP)
    - E2E-Different_PDP-002 (Tools & Mats PDP)
    - E2E-Different_PDP-003 (Clearance Supply Bundles PDP & PLP)
    - E2E-Different_PDP-004 (Software PDP)
    """

    # =========================================================================
    # 1. Core PDP Information & Metadata
    # =========================================================================
    PAGE_TITLE = "h1.page-title, h1"
    PRODUCT_SKU = "[itemprop='sku'], .sku .value, .product.attribute.sku .value, .product-info-stock-sku .value"
    PRODUCT_PRICE = (
        ".price-box .price-container.price-final_price .price, "
        "[data-price-type='finalPrice'] .price, "
        ".price-box .price, "
        ".product-info-price .price"
    )
    REGULAR_PRICE = ".price-box .normal-price .price, .price-box .price"
    SPECIAL_PRICE = ".price-box .special-price .price, .special-price [data-price-type='finalPrice'] .price"
    OLD_PRICE = ".price-box .old-price .price, .old-price [data-price-type='oldPrice'] .price"
    PRODUCT_DESCRIPTION = (
        ".product.attribute.description, "
        ".product.attribute.description .value, "
        ".description .value, "
        "#description, "
        ".product-info-main .overview"
    )
    MAIN_INFO_CONTAINER = ".product-info-main, #maincontent"
    IN_STOCK_BADGE = ".stock.available, [title='Availability'] span, .in-stock"
    OUT_OF_STOCK_BADGE = ".stock.unavailable, .unavailable, .out-of-stock"

    # Add to Cart & Purchase
    ADD_TO_CART_BUTTON = "#product-addtocart-button, button[title='Add to Cart'], button:has-text('Add to Cart')"
    PURCHASE_BUTTON = "button:has-text('Purchase'), a:has-text('Purchase'), .purchase-button"

    # Quantity Controls
    QTY_CONTAINER = ".field.qty, .qty-wrapper, [class*='qty']"
    QTY_INPUT = "#qty, input.qty, input[name='qty']"
    QTY_PLUS = ".field.qty .qty-plus, [aria-label='Increase quantity'], .plus, .quantity-plus"
    QTY_MINUS = ".field.qty .qty-minus, [aria-label='Decrease quantity'], .minus, .quantity-minus"

    # =========================================================================
    # 2. Product Image Gallery & Thumbnails
    # =========================================================================
    GALLERY_CONTAINER = ".product.media"
    GALLERY_ACTIVE_IMAGE = (
        ".fotorama__stage__frame.fotorama__active img.fotorama__img, "
        ".fotorama__stage__frame.fotorama__active img, "
        ".product.media picture img, "
        ".gallery-placeholder picture img, "
        ".product.media img, "
        ".gallery-placeholder img"
    )
    GALLERY_STAGE_FRAMES = ".fotorama__stage__frame"
    GALLERY_THUMBNAILS = (
        ".fotorama__nav__frame--thumb, "
        ".fotorama__thumb, "
        ".gallery-placeholder .fotorama__nav__shaft .fotorama__nav__frame, "
        ".product-thumbnails .thumbnail"
    )

    # =========================================================================
    # 3. Variants, Color Swatches & Machine Options (Machine PDP)
    # =========================================================================
    SWATCH_CONTAINER = ".swatch-opt, .swatch-attribute"
    COLOR_SWATCH_CONTAINER = (
        ".swatch-attribute.color, "
        ".swatch-attribute[data-attribute-code='color'], "
        "[aria-label*='Color' i]"
    )
    COLOR_SWATCHES = (
        ".swatch-attribute.color .swatch-option, "
        ".swatch-attribute[data-attribute-code='color'] .swatch-option, "
        ".swatch-option.color, "
        ".swatch-option[data-option-type='1'], "
        ".swatch-option[data-option-type='2']"
    )
    MACHINE_OPTIONS_CONTAINER = (
        ".swatch-attribute.machine_option, "
        ".swatch-attribute[data-attribute-code*='machine'], "
        ".product-custom-option, "
        ".bundle-options-container"
    )
    MACHINE_OPTIONS_SWATCHES = (
        ".swatch-attribute.machine_option .swatch-option, "
        ".swatch-attribute[data-attribute-code*='machine'] .swatch-option, "
        ".swatch-attribute:not(.color) .swatch-option, "
        ".bundle-option-item"
    )
    ALL_SWATCH_OPTIONS = ".swatch-option"
    SWATCH_SELECTED = ".swatch-option.selected, .swatch-option[aria-checked='true']"
    SWATCH_LABEL = ".swatch-attribute-label"
    SWATCH_SELECTED_LABEL = ".swatch-attribute-selected-option"

    # =========================================================================
    # 4. Specifications, Compatibility & Contents (Tools & Mats PDP, Bundles)
    # =========================================================================
    SPECIFICATIONS_SECTION = (
        ".product.attribute.samchine, "
        ".additional-attributes, "
        "table.additional-attributes, "
        "#product-attribute-specs-table, "
        ".data.table.additional-attributes, "
        ".specs, "
        ".specifications, "
        "#specifications"
    )
    COMPATIBILITY_SECTION = (
        ".compatibility, "
        ".product-compatibility, "
        "[class*='compatib'], "
        "div:has-text('Compatibility'), "
        "section:has-text('Compatible with'), "
        "p:has-text('Compatible with')"
    )
    CONTENTS_INCLUDED_SECTION = (
        ".whats-included, "
        ".product-contents, "
        ".bundle-items, "
        "[class*='included'], "
        "[class*='contents'], "
        "div:has-text('What\'s Included'), "
        "section:has-text('What\'s Included')"
    )

    # Customer Reviews
    REVIEWS_SECTION = (
        "#customer-reviews, "
        ".reviews-actions, "
        ".product-reviews-summary, "
        ".sa-reviews, "
        "div:has-text('Real Results'), "
        "[class*='review']"
    )
    REVIEWS_COUNT = ".reviews-actions .action.view span, .review-count, .rating-summary .rating-result"
    REVIEWS_ITEMS = ".review-item, .customer-review, .block-reviews .item"
    REVIEWS_CONTROLS = ".reviews-actions a, .review-control, .review-pagination"

    # =========================================================================
    # 5. Clearance & Supply Bundles Navigation & PLP (Clearance Bundles PDP)
    # =========================================================================
    CLEARANCE_NAV_TRIGGER = (
        "header a:has-text('Clearance'), "
        "nav a:has-text('Clearance'), "
        ".navigation a:has-text('Clearance'), "
        "[class*='clearance']"
    )
    CLEARANCE_DROPDOWN_MENU = (
        ".clearance-menu, "
        "li:has(a:has-text('Clearance')) ul, "
        ".navigation .submenu, "
        ".dropdown-menu"
    )
    SUPPLY_BUNDLES_NAV_LINK = (
        "a:has-text('Supply Bundles'), "
        "a[href*='supply-bundles'], "
        ".navigation a[href*='supply-bundles']"
    )
    PLP_PAGE_TITLE = "h1.page-title, h1, .category-title"
    PLP_PRODUCT_COUNT = ".toolbar-amount, .toolbar-number, .total-products, span[data-ui-id='page-title-wrapper']"
    PLP_PRODUCT_CARDS = ".product-item, .product-card, li.product-item"
    PLP_PRODUCT_LINK = "a.product-item-link, a.product-item-photo"
    PLP_PRODUCT_IMAGE = ".product-image-photo, img.product-image-photo"
    PLP_PRODUCT_PRICE = ".price-box .price, .price"
    PLP_DISCOUNT_BADGE = ".discount-percent, .badge-sale, .sale-badge, [class*='discount'], .special-price"
    PLP_SHARE_ICON = (
        ".share, "
        "[class*='share'], "
        "button[aria-label*='share' i], "
        ".action.share, "
        "a.share-btn"
    )
    PLP_SHARE_DIALOG = ".share-dialog, .share-popup, .share-modal, [class*='share-modal']"

    # =========================================================================
    # 6. Software PDP (Silhouette Studio® Editions & View More/View Less)
    # =========================================================================
    SOFTWARE_NAV_LINK = "header a:has-text('Software'), a[href*='/software'], .navigation a:has-text('Software')"
    EDITIONS_SECTION = (
        "#editions, "
        ".editions-section, "
        ".software-editions, "
        "div:has-text('Silhouette Studio® editions'), "
        "table.editions-table, "
        ".pricing-table"
    )
    EDITIONS_CARDS = ".edition-card, .edition-column, tr.edition-row, .pricing-plan, [class*='edition']"
    VIEW_MORE_BUTTON = (
        "button:has-text('View More'), "
        "a:has-text('View More'), "
        "span:has-text('View More'), "
        "[class*='view-more']"
    )
    VIEW_LESS_BUTTON = (
        "button:has-text('View Less'), "
        "a:has-text('View Less'), "
        "span:has-text('View Less'), "
        "[class*='view-less']"
    )
    EXPANDED_CONTENT_CONTAINER = (
        ".view-more-container, "
        ".expanded-content, "
        ".more-features, "
        "[class*='features-table'], "
        "tr.hidden-feature"
    )
    SOFTWARE_DOWNLOAD_LINKS = (
        "a[href*='.dmg'], "
        "a[href*='.exe'], "
        "a:has-text('MAC 64'), "
        "a:has-text('Win 64'), "
        "a:has-text('Download')"
    )
    SOFTWARE_PURCHASE_LINKS = (
        "a:has-text('Buy upgrade'), "
        "a:has-text('Buy Now'), "
        "button:has-text('Purchase')"
    )
    SYSTEM_REQUIREMENTS_LINK = (
        "a:has-text('System requirements'), "
        "a[href*='solutions/articles'], "
        "a[href*='system-requirements']"
    )

