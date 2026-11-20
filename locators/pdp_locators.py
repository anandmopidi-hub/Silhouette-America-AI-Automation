class PdpLocators:
    """Encapsulated locators for Silhouette America Product Detail Page (PDP)."""

    # Product Header & Core Information
    PAGE_TITLE = "h1.page-title, h1"
    SKU = "[itemprop='sku'], .sku .value, .product.attribute.sku .value, .product-info-stock-sku .value"
    DESCRIPTION = ".product.attribute.description, .product.attribute.description .value, .description .value, .description, #description"
    MAIN_INFO_CONTAINER = ".product-info-main, #maincontent"

    # Product Media / Gallery
    GALLERY_CONTAINER = ".product.media, .gallery-placeholder"
    GALLERY_STAGE_FRAMES = ".fotorama__stage__frame"
    GALLERY_ACTIVE_IMAGE = ".fotorama__stage__frame.fotorama__active img.fotorama__img, .fotorama__stage__frame.fotorama__active img"
    GALLERY_THUMBNAILS = ".fotorama__nav__frame--thumb"
    GALLERY_IMAGES = ".fotorama__stage__frame"

    # Specifications / Technical Details
    SPECIFICATIONS = ".product.attribute.samchine, .additional-attributes, table.additional-attributes, #product-attribute-specs-table, .data.table.additional-attributes, .specs, .specifications"

    # Pricing Elements
    FINAL_PRICE = ".price-box .price-container.price-final_price .price, [data-price-type='finalPrice'] .price, .price-box .price"
    REGULAR_PRICE = ".price-box .normal-price .price, .price-box .price"
    SPECIAL_PRICE = ".price-box .special-price .price, .special-price [data-price-type='finalPrice'] .price"
    OLD_PRICE = ".price-box .old-price .price, .old-price [data-price-type='oldPrice'] .price"

    # Configurable Variants / Swatches
    SWATCH_CONTAINER = ".swatch-opt, .swatch-attribute"
    SWATCH_OPTIONS = ".swatch-option"
    SWATCH_SELECTED = ".swatch-option.selected"
    SWATCH_LABEL = ".swatch-attribute-label"
    SWATCH_SELECTED_LABEL = ".swatch-attribute-selected-option"
    SWATCH_ERROR = "div.mage-error:not(.recaptcha-field-error):not(#qty-error), div.mage-error[generated='true']"

    # Add to Cart & Purchase Controls
    ADD_TO_CART_BUTTON = "#product-addtocart-button"
    ADD_TO_CART_FORM = "#product_addtocart_form"
    SUCCESS_MESSAGE = ".message.success, .message-success, [data-ui-id='message-success']"
    HEADER_CART_COUNTER = ".counter-number, .minicart-wrapper .counter.qty"

    # Stock Status Badges
    IN_STOCK_BADGE = (
        ".product-info-main .stock.available, "
        ".product-info-stock-sku .stock.available, "
        ".product-info-main [title='Availability'] span, "
        ".stock.available, [title='Availability'] span"
    )
    OUT_OF_STOCK_BADGE = (
        ".product-info-main .stock.unavailable, "
        ".product-info-stock-sku .stock.unavailable, "
        ".product-info-main [title='Availability'], "
        ".product-info-main .stock.unavailable span, "
        ".stock.unavailable, "
        ".product-info-main .unavailable"
    )

    # Quantity Controls
    QTY_INPUT = "#qty, input.qty"
    QTY_MINUS_BUTTON = ".field.qty .qty-minus, [aria-label='Decrease quantity']"
    QTY_PLUS_BUTTON = ".field.qty .qty-plus, [aria-label='Increase quantity']"
    QTY_ERROR = "#qty-error, div.mage-error#qty-error, div.mage-error[for='qty']"
