class OrderPurchaseLocators:
    """Encapsulated locators for Silhouette America Order Purchase & Checkout module,

    covering software PDP, mini cart, checkout, payment, confirmation, and My Orders flows.
    """

    # -------------------------------------------------------------------------
    # Software Product Details Page (PDP)
    # -------------------------------------------------------------------------
    PDP_TITLE = "h1.page-title, h1, .product-info-main h1"
    PDP_PRICE = ".price-box .price, [data-price-type='finalPrice'] .price, .product-info-price .price"
    PDP_PURCHASE_BUTTON = "button:has-text('Purchase'), button.action.primary.tocart, #product-addtocart-button"
    PDP_SUCCESS_MESSAGE = ".message.success, .message-success, [data-ui-id='message-success']"

    # -------------------------------------------------------------------------
    # Header Cart & Mini Cart
    # -------------------------------------------------------------------------
    HEADER_CART_LINK = "a.action.showcart, .minicart-wrapper a.showcart, .minicart-wrapper a"
    HEADER_CART_COUNTER = ".counter-number, .minicart-wrapper .counter.qty"
    MINICART_WRAPPER = "#minicart-content-wrapper, .block-minicart"
    MINICART_ITEMS = ".minicart-items .product-item, .minicart-items li"
    MINICART_ITEM_NAME = ".minicart-items .product-item-name a, .minicart-items .product-item-name"
    MINICART_ITEM_PRICE = ".minicart-items .price-container .price, .minicart-items .price"
    MINICART_ITEM_QTY = ".minicart-items input.item-qty, .minicart-items input.cart-item-qty, .minicart-items .details-qty input"
    MINICART_SUBTOTAL = ".subtotal .price, .amount.price-container .price"
    MINICART_CHECKOUT_BUTTON = "button#top-cart-btn-checkout, .action.checkout, button:has-text('Checkout'), a:has-text('Checkout')"

    # -------------------------------------------------------------------------
    # Checkout Page Layout & Sections
    # -------------------------------------------------------------------------
    CHECKOUT_PAGE_CONTAINER = "#checkout, .checkout-container, .checkout-index-index, .opc-wrapper"
    CHECKOUT_PAGE_TITLE = "h1.title, .page-title, h1"
    PROGRESS_BAR_PAYMENT = "[data-cy='progress-bar-payment-trigger'], .opc-progress-bar"
    LOGGED_IN_EMAIL_TEXT = "[data-cy='logged-in-email'], #email, input[type='email']"

    # Customer & Billing Address Form
    BILLING_FIRST_NAME = "#billing-first-name, input[name='firstname']"
    BILLING_LAST_NAME = "#billing-last-name, input[name='lastname']"
    BILLING_PHONE = "input[name='telephone'], input[placeholder*='phone' i], input[type='tel']"
    ADDRESS_FINDER_INPUT = "input[placeholder*='Search by street name or postcode' i], input[placeholder*='postcode' i]"
    ADDRESS_FINDER_SUGGESTIONS = "button.shipperhq-autocomplete__action, .pca-item, div.pca div, [class*='suggestion']"
    USE_THIS_ADDRESS_BUTTON = "button:has-text('Use this address'), .select-address-btn, button[class*='select-address']"
    CONTINUE_TO_BILLING_BUTTON = "button:has-text('Continue to Billing'), button.continue-btn, button:has-text('Continue'), [data-cy='continue-button']"
    EDIT_DETAILS_BUTTON = "[data-cy='completed-step-details-edit-button'], .edit-details-button"

    # -------------------------------------------------------------------------
    # Coupon & Discount Section
    # -------------------------------------------------------------------------
    COUPON_TRIGGER = ".coupon-discount-trigger, [data-cy='coupon-discount-trigger-desktop'], .coupon-discount-title:has-text('Enter Discount Code')"
    COUPON_INPUT = "input[name='coupon-code'], input[placeholder*='Discount Code' i], [data-cy='coupon-discount-input-desktop']"
    APPLY_COUPON_BUTTON = "button:has-text('Apply Coupon'), [data-cy='coupon-discount-apply-desktop']"
    CANCEL_COUPON_BUTTON = "button:has-text('Cancel Coupon'), [data-cy='coupon-discount-remove-desktop'], p:has-text('Cancel Coupon'), span:has-text('Cancel Coupon')"
    COUPON_SUCCESS_MESSAGE = "[data-cy='coupon-discount-success-desktop-text'], .message-success, .success.message, .messages .message-success"
    COUPON_ERROR_MESSAGE = ".messages .message-error, .error.message, [data-cy*='coupon-discount-error']"

    # -------------------------------------------------------------------------
    # Order Summary on Checkout
    # -------------------------------------------------------------------------
    ORDER_SUMMARY_CONTAINER = ".order-summary, .opc-block-summary, .order-review-form"
    SUMMARY_PRODUCT_NAME = "[data-cy='product-name-desktop'], .product-item-name"
    SUMMARY_SUBTOTAL = "[data-cy='subtotal-ex-tax-desktop'], .subtotal .price, .totals.sub .price"
    SUMMARY_DISCOUNT = "[data-cy='discount-price-desktop'], .discount .price"
    SUMMARY_GRAND_TOTAL = "[data-cy='grand-total-price-desktop'], .grand.totals .price, .order-total-grand .price, .order-total .price"

    # -------------------------------------------------------------------------
    # Payment Method & Place Order
    # -------------------------------------------------------------------------
    FREE_PAYMENT_RADIO = "#fastlane-select, input[data-cy='free-mo-payment-radio']"
    FREE_PAYMENT_RADIO_LABEL = "label:has-text('No Payment Information Required'), label[for='fastlane-select']"
    PAY_NOW_BUTTON = "button.free-payment-button, button[data-cy='free-mo-pay-button'], button:has-text('Pay Now'), button:has-text('Pay $0.00')"

    # -------------------------------------------------------------------------
    # Order Confirmation (/checkout/onepage/success)
    # -------------------------------------------------------------------------
    CONFIRMATION_TITLE = "h1, .page-title, .checkout-success"
    CONFIRMATION_ORDER_NUMBER_LINK = "a.order-number, a[href*='sales/order/view']"
    CONFIRMATION_ORDER_NUMBER_TEXT = ".order-number, p:has-text('Your order number is:')"
    REVIEW_POPUP = ".sa-write-review, .modal-popup, [class*='review']"
    REVIEW_POPUP_CLOSE = ".sa-write-review__close, button[aria-label='Close'], .close-modal"

    # -------------------------------------------------------------------------
    # Customer Account & My Orders (/sales/order/history/)
    # -------------------------------------------------------------------------
    ACCOUNT_MENU_TRIGGER = ".user-link-dropdown, .user-icon"
    MY_ORDERS_NAV_LINK = "a.account-order, a[href*='sales/order/history/'], a:has-text('My orders')"
    MY_ORDERS_TABLE = "table#my-orders-table, table.orders-history, .table-order-items"
    MY_ORDERS_ROWS = "table#my-orders-table tbody tr, table.orders-history tbody tr"

    # -------------------------------------------------------------------------
    # Order Details View (/sales/order/view/order_id/...)
    # -------------------------------------------------------------------------
    ORDER_DETAILS_TITLE = "h1, .page-title"
    ORDER_DETAILS_STATUS = ".order-status, [class*='order-status'], span.status"
    ORDER_DETAILS_DATE = ".order-date"
    ORDER_DETAILS_ITEMS_ROWS = "table#my-orders-table tbody tr, table.order-details-items tbody tr, .table-order-items tbody tr"
    ORDER_DETAILS_PRODUCT_NAME = ".col.name .product-item-name, .product-item-name"
    ORDER_DETAILS_SUBTOTAL = "tr.subtotal td.amount, .subtotal .price"
    ORDER_DETAILS_DISCOUNT = "tr.discount td.amount, .discount .price"
    ORDER_DETAILS_GRAND_TOTAL = "tr.grand_total td.amount, .grand_total .price"
