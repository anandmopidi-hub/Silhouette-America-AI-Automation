"""Encapsulated locators for Silhouette America Club Silhouette module.

Discovered dynamically from live application DOM.
"""


class ClubSilhouetteLocators:
    """Locators for Silhouette America Club Silhouette module."""

    # -------------------------------------------------------------------------
    # Club Silhouette Landing Page (/club-silhouette)
    # -------------------------------------------------------------------------
    CLUB_PAGE_HEADING = "h1:has-text('Club Silhouette'), h1"
    LANDING_SUBHEADING = "p:has-text('Everything you need to know before you start'), :has-text('Everything you need to know before you start')"
    NAV_CLUB_LINK = "nav a.fmlink[href*='club-silhouette'], header a[href*='club-silhouette']"

    # Plan Comparison Table
    PLAN_COMPARE_CONTAINER = ".maintbclub, .plan-compare-table"
    PLAN_COMPARE_TABLE = ".plan-compare-table table, .maintbclub table, table"
    PLAN_TABLE_HEADERS = ".plan-compare-table thead th, .maintbclub thead th, table thead th"
    PLAN_TABLE_ROWS = ".plan-compare-table tbody tr, .maintbclub tbody tr, table tbody tr"

    # Plan CTA Buttons
    ANNUAL_PLAN_JOIN_BUTTON = "a.joinbtn[href*='clubsilhouette/plan/annually'], a[href*='clubsilhouette/plan/annually']"
    MONTHLY_PLAN_JOIN_BUTTON = "a.joinbtn[href*='clubsilhouette/plan/monthly'], a[href*='clubsilhouette/plan/monthly'], a:has-text('Join monthly')"
    ALL_JOIN_BUTTONS = "a.joinbtn, .plan-compare-table a.joinbtn"

    # Reviews Section
    REVIEWS_SECTION = ".club-review, .review-sec, :has(> h2:has-text('Why our customers love Silhouette'))"
    REVIEWS_HEADING = "h2:has-text('Why our customers love Silhouette'), :has-text('Why our customers love Silhouette')"
    REVIEWS_SWIPER = ".myreview.swiper, .club-review .swiper"

    # Frequently Asked Questions Section
    FAQ_SECTION = ".club-faq, .faq-sec, :has(> h2:has-text('Frequently Asked Questions'))"
    FAQ_HEADING = "h2:has-text('Frequently Asked Questions'), :has-text('Frequently Asked Questions')"
    FAQ_ITEMS = ".faq-item"
    FAQ_QUESTIONS = ".faq-question"
    FAQ_ANSWERS = ".faq-answer, .answer"

    # Regional Restriction Notice Modal
    NOTICE_MODAL = ".modal-popup._show:has-text('Notice'), .modal-popup._show:has-text('Club Silhouette is not available')"
    NOTICE_CONTENT = ".modal-popup._show .modal-content, .modal-popup._show:has-text('not available in your area')"
    NOTICE_OK_BUTTON = ".modal-popup._show button.action-primary, .modal-popup._show button.action-accept"

    # -------------------------------------------------------------------------
    # Membership Selection & Refill Checkout Flow (/clubsilhouette/plan/...)
    # -------------------------------------------------------------------------
    PLAN_SELECTION_TITLE = "h1:has-text('Select your free refill items'), h1:has-text('Select your membership type'), h2:has-text('Select your free refill items'), .page-title"
    REFILL_HEADING = "h1:has-text('Select your free refill items'), h2:has-text('Select your free refill items'), h2:has-text('Choose Your Items')"
    CHOOSE_ITEMS_HEADING = "h2:has-text('Choose Your Items')"

    # Machine and Category Selection Dropdowns
    MACHINES_SELECT = "select#machines-select"
    CATEGORY_SELECT = "select#category-select"

    # Product Refill Cards & Selection
    REFILL_ITEMS = ".refillmat, .refill-item, .mat-item, .product-item"
    REFILL_SELECT_BUTTONS = ".refillmat .selectbtn, .selectbtn"
    REFILL_SELECTED_HIDDEN = "input#selected_refills"

    # Step 1 Continue Button
    CONTINUE_TO_SHIPPING_BUTTON = "button#club-continue-checkout, #club-continue-checkout"

    # Step 2 Details & Shipping Section
    SHIPPING_PAYMENT_DETAILS_HEADING = ":has-text('Select your shipping address and payment details'), h2:has-text('Select your shipping address')"
    SHIPPING_ADDRESS_SELECT = "select#shippingaddress, select[name='shippingaddress']"
    BILLING_ADDRESS_SELECT = "select#billingaddressbook, select[name='billingaddressbook']"
    SHIPPING_FORM = "form:has(#street_1), form:has(#firstname)"
    ORDER_SUMMARY_CONTAINER = "#order-summary, .order-summary, .cart-summary, .block-summary, .club-order-summary"
    FREE_REFILL_SUMMARY = ".selected-refill-items, .refill-summary, .refillmat"

    # Payment Gateway Form & Card
    CARD_SELECT = "select#card_id, select[name='card_id']"
    CARD_MODAL = "#modal-content-card"
    PAYMENT_SUBMIT_BUTTON = "button#submit_card_data"
    PAYMENT_ERROR_MESSAGE = ".message-error, .messages .error, [data-ui-id='message-error']"

    # Checkout Continuation & Terms
    TERMS_CHECKBOX = "input#terms, input[name='terms']"
    JOIN_CLUB_BUTTON = "button#continue-btn, #continue-btn"
    CONTINUE_BUTTON = "button#continue-btn, .continue-btn"

    # Post-Purchase Review / Success
    REVIEW_PAGE_HEADING = "h1:has-text('Thank you for your purchase'), .page-main:has-text('Thank you for your purchase'), h2:has-text('Payment Review'), :has-text('Thank you for your purchase!')"
    REVIEW_PAGE_BODY = "#maincontent"
    SHOP_NOW_BUTTON = "a:has-text('Shop now'), button:has-text('Shop now'), .action.primary:has-text('Shop now')"

    # -------------------------------------------------------------------------
    # Customer Account & Membership Status
    # -------------------------------------------------------------------------
    ACCOUNT_TRIGGER = ".user-link-dropdown, .user-icon"
    SIGN_IN_LINK = "a.signin_link, .signin-link a, a:has-text('Sign In')"
    LOGGED_IN_WELCOME = ".customer-welcome, span.logged-in, .user-name, .greet.welcome"
    ACCOUNT_SIDEBAR_CLUB_LINK = "a[href*='clubsilhouette/customer'], a:has-text('Club silhouette'), .block-collapsible-nav a[href*='clubsilhouette'], .sidebar a[href*='clubsilhouette'], .block-collapsible-nav a[href*='club-silhouette'], .sidebar a[href*='club-silhouette']"
    ACCOUNT_SIDEBAR_NAV = ".block-collapsible-nav, .sidebar.sidebar-main"
    ACCOUNT_DASHBOARD_MAIN = ".column.main, #maincontent"
    PAYMENTS_TAB = "button#club-tab-payments, button:has-text('Payments'), a:has-text('Payments'), li:has-text('Payments') a, .nav-tabs a:has-text('Payments')"
    PAYMENTS_PANEL = "#club-panel-payments, .club-account-info-panel.payment-container, #club-content-payments"
    PAYMENTS_TABLE = "#club-payments-table, .table-order-items, .table-payments"
    PAYMENTS_ROWS = "#club-payments-table tbody tr, .table-order-items tbody tr"
    PAYMENTS_NO_RECORDS = ":has-text('No any record'), :has-text('No records')"
    MEMBER_SHIPS_BANNER = ".member-ships"
    MEMBER_BENEFITS_LIST = ".member-ships ul li"
    MEMBER_DASHBOARD_HEADING = ".clubsilhouette-customer-index h1, h1:has-text('Club silhouette'), .page-title:has-text('Club')"
    MEMBER_INFO_STATUS = ".membership-information, #maincontent:has-text('Active')"
    MEMBER_TYPE_MONTHLY = ":has-text('Club Silhouette - Monthly Subscription')"
    MEMBER_TYPE_ANNUAL = ":has-text('Club Silhouette - Annual Subscription')"

    # Popup / Full-Page Login Form
    POPUP_LOGIN_FORM = "form.popup-login-form"
    POPUP_USERNAME_INPUT = "form.popup-login-form input[name='username']"
    POPUP_PASSWORD_INPUT = "form.popup-login-form input[name='popup-password'], #popup-password"
    POPUP_SUBMIT_BUTTON = "form.popup-login-form button[type='submit']"
    LOGIN_OVERLAY = ".login-overlay"

    # Cookie Consent
    COOKIE_ACCEPT_BUTTON = "button[data-amgdprcookie-js='accept'], button:has-text('I Agree'), button:has-text('I agree'), .amgdprcookie-button.-allow"
    COOKIE_BANNER = "[data-amcookie-js='bar'], .amgdprcookie-bar-container, .modal-popup._show.amgdprcookie-bar-container"

    # QA Purge
    QA_PURGE_PATH = "clubsilhouette/qa/purge"
    QA_PURGEMEAS_PATH = "clubsilhouette/qa/purgemeas"
