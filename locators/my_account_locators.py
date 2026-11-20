class MyAccountLocators:
    """Encapsulated locators for Silhouette America My Account module,
    covering Account Dashboard, Profile / Account Information, Address Book,
    My Orders, Software Licenses, Club Membership, Privacy & Data Rights,
    and My Wishlist.
    """

    # -------------------------------------------------------------------------
    # Account Navigation & Header Triggers
    # -------------------------------------------------------------------------
    ACCOUNT_MENU_TRIGGER = ".user-link-dropdown, .user-icon, span.user-link-dropdown"
    ACCOUNT_DROPDOWN_LINKS = ".user-link-items a, .header-links a, a[href*='customer/account']"
    HEADER_MY_ACCOUNT_LINK = "a[href*='customer/account/'], a:has-text('My Account'), a:has-text('My account')"
    SIDEBAR_NAV = ".block-collapsible-nav, .sidebar.sidebar-main, .account-nav"
    SIDEBAR_NAV_ITEMS = ".block-collapsible-nav ul li, .account-nav ul li"

    # Sidebar Navigation Links
    NAV_DASHBOARD = ".sidebar a[href*='customer/account/'], a:has-text('Account Dashboard'), a:has-text('My account')"
    NAV_PROFILE = ".sidebar a[href*='customer/account/edit'], a:has-text('Account Information'), a:has-text('Edit Profile')"
    NAV_ADDRESS_BOOK = ".sidebar a:has-text('Address book'), .account-nav a:has-text('Address book'), a:has-text('Address book'), .block-collapsible-nav a[href$='customer/address/'], .block-collapsible-nav a[href$='customer/address']"
    NAV_MY_ORDERS = ".sidebar a:has-text('My orders'), .account-nav a:has-text('My orders'), a:has-text('My orders')"
    NAV_SOFTWARE_LICENSES = ".sidebar a:has-text('License keys'), .account-nav a:has-text('License keys'), a:has-text('License keys')"
    NAV_CLUB_MEMBERSHIP = ".sidebar a:has-text('Club silhouette'), .account-nav a:has-text('Club silhouette'), a:has-text('Club silhouette')"
    NAV_PRIVACY_DATA = ".sidebar a:has-text('Privacy & data rights'), a:has-text('Privacy & data rights')"
    NAV_WISHLIST = ".sidebar a:has-text('My wishlist'), .account-nav a:has-text('My wishlist'), a:has-text('My wishlist')"

    # -------------------------------------------------------------------------
    # My Account Dashboard (/customer/account/)
    # -------------------------------------------------------------------------
    DASHBOARD_PAGE_TITLE = "h1.page-title, h1"
    DASHBOARD_WELCOME_TXT = ".box-information .box-content, .block-dashboard-info .box-content, .greet.welcome"
    DASHBOARD_INFO_BLOCK = ".block-dashboard-info, .box-information"
    DASHBOARD_ADDRESSES_BLOCK = ".block-dashboard-addresses, .box-address-billing, .box-address-shipping"
    DASHBOARD_ORDERS_BLOCK = ".block-dashboard-orders, .block-recent-orders"
    DASHBOARD_EDIT_PROFILE_LINK = "a[href*='customer/account/edit'], .box-information a.action.edit"
    DASHBOARD_MANAGE_ADDRESSES_LINK = "a[href*='customer/address'], .block-dashboard-addresses a.action.edit"

    # -------------------------------------------------------------------------
    # Profile & Account Information (/customer/account/edit/)
    # -------------------------------------------------------------------------
    PROFILE_PAGE_TITLE = "h1.page-title, h1"
    PROFILE_FORM = "form.form-edit-account, form#form-validate, form[action*='editPost']"
    PROFILE_FIRSTNAME_INPUT = "#firstname, input[name='firstname']"
    PROFILE_LASTNAME_INPUT = "#lastname, input[name='lastname']"
    PROFILE_EMAIL_INPUT = "#email, input[name='email']"
    PROFILE_CHANGE_EMAIL_CHECKBOX = "#change-email, input[name='change_email']"
    PROFILE_CHANGE_PASSWORD_CHECKBOX = "#change-password, input[name='change_password']"
    PROFILE_CURRENT_PASSWORD_INPUT = "#current-password, input[name='current_password']"
    PROFILE_NEW_PASSWORD_INPUT = "#password, input[name='password']"
    PROFILE_CONFIRM_PASSWORD_INPUT = "#password-confirmation, input[name='password_confirmation']"
    PROFILE_SAVE_BUTTON = "form.form-edit-account button[type='submit'], form#form-validate button[type='submit'], button.action.save.primary, button:has-text('Save')"
    PROFILE_SUCCESS_MESSAGE = ".messages .message-success, .message.success, [data-ui-id='message-success']"
    PROFILE_ERROR_MESSAGE = ".messages .message-error, .message.error, [data-ui-id='message-error']"
    PROFILE_FIRSTNAME_ERROR = "#firstname-error, div.mage-error[for='firstname']"
    PROFILE_LASTNAME_ERROR = "#lastname-error, div.mage-error[for='lastname']"
    PROFILE_EMAIL_ERROR = "#email-error, div.mage-error[for='email']"
    ALL_FIELD_ERRORS = ".mage-error:visible, div.mage-error:visible, label.mage-error:visible"

    # -------------------------------------------------------------------------
    # Address Book (/customer/address/)
    # -------------------------------------------------------------------------
    ADDRESS_BOOK_TITLE = "h1.page-title, h1:has-text('My address'), h1:has-text('Address Book'), h1"
    ADD_NEW_ADDRESS_BUTTON = "button:has-text('Add new address'), a:has-text('Add new address'), button:has-text('Add New Address'), a:has-text('Add New Address'), a[href*='customer/address/new'], button.action.add, a.action.add"
    
    # Address Blocks & Cards
    DEFAULT_BILLING_BOX = ".box-address-billing, .box-billing-address, div:has-text('Billing'):has-text('Zip code')"
    DEFAULT_SHIPPING_BOX = ".box-address-shipping, .box-shipping-address, div:has-text('Shipping'):has-text('Zip code')"
    ADDITIONAL_ADDRESSES_SECTION = ".additional-addresses, .addresses-additional, .block-addresses-list"
    ADDITIONAL_ADDRESS_CARDS = ".add-entry"
    ALL_ADDRESS_CARDS = ".box-address-billing, .box-address-shipping, .add-entry"

    # Address Card Actions & Deletion Confirmation
    ADDRESS_EDIT_LINK = ".actions-section a:has-text('Edit'), a:has-text('Edit'), button:has-text('Edit'), a[href*='address/edit']"
    ADDRESS_DELETE_BUTTON = ".actions-section a:has-text('Delete'), a:has-text('Delete'), button:has-text('Delete'), a:has-text('✕'), button:has-text('✕')"
    DELETE_CONFIRM_MODAL = ".modal-popup._show, div[role='dialog']._show"
    DELETE_CONFIRM_OK = ".modal-popup._show button.action-accept, .modal-popup._show button.action-primary.action-accept, .modal-popup._show button:has-text('OK')"
    ADDRESS_SUCCESS_MESSAGE = ".messages .message-success, .message.success, [data-ui-id='message-success'], div:has-text('You saved the address.'), div:has-text('You deleted the address.')"
    ADDRESS_ERROR_MESSAGE = ".messages .message-error, .message.error, [data-ui-id='message-error']"

    # Add / Edit Address Form (/customer/address/new/ or /customer/address/edit/...)
    ADDRESS_FORM = "form#form-validate, form.form-address-edit"
    ADDR_FIRSTNAME = "#firstname, input[name='firstname']"
    ADDR_LASTNAME = "#lastname, input[name='lastname']"
    ADDR_TELEPHONE = "#mobile_number, input[name='telephone'], #telephone, input[placeholder*='Phone']"
    ADDR_STREET_0 = "#street_1, input[name='street[0]'], input[name='street[]']:first-of-type"
    ADDR_STREET_1 = "#street_2, input[name='street[1]']"
    ADDR_CITY = "#city, input[name='city']"
    ADDR_REGION_SELECT = "select#region_id, select[name='region_id']"
    ADDR_REGION_INPUT = "input#region, input[name='region']"
    ADDR_POSTCODE = "#zip, #postcode, input[name='postcode']"
    ADDR_COUNTRY = "select#country, select[name='country_id']"
    ADDR_DEFAULT_BILLING = "#primary_billing, input[name='default_billing']"
    ADDR_DEFAULT_SHIPPING = "#primary_shipping, input[name='default_shipping']"
    ADDR_SAVE_BUTTON = "form#form-validate button[type='submit'], form.form-address-edit button[type='submit'], button.action.save.primary, button:has-text('Save Address'), button:has-text('Save address')"
    ADDR_REQUIRED_ERRORS = ".mage-error:visible, div.mage-error:visible, #street_1-error, #city-error, #telephone-error, #zip-error"

    # -------------------------------------------------------------------------
    # My Orders (/sales/order/history/) & Order Details
    # -------------------------------------------------------------------------
    ORDERS_PAGE_TITLE = "h1.page-title, h1"
    ORDERS_TABLE = "table#my-orders-table, table.orders-history, .table-order-items"
    ORDERS_ROWS = "table#my-orders-table tbody tr, table.orders-history tbody tr"
    ORDER_COL_ID = "td.col.id, .col.id"
    ORDER_COL_DATE = "td.col.date, .col.date"
    ORDER_COL_TOTAL = "td.col.total, .col.total"
    ORDER_COL_STATUS = "td.col.status, .col.status"
    ORDER_COL_ACTIONS = "td.col.actions, .col.actions"
    ORDER_VIEW_LINK = "a.action.view, a[href*='sales/order/view']"
    ORDERS_EMPTY_MESSAGE = ".message.info.empty, .empty"

    # Order Details View (/sales/order/view/order_id/...)
    ORDER_DETAILS_TITLE = "h1.page-title, h1"
    ORDER_DETAILS_STATUS = ".order-status, [class*='order-status'], span.status"
    ORDER_DETAILS_DATE = ".order-date"
    ORDER_DETAILS_ITEMS_TABLE = "table#my-orders-table, table.order-details-items, .table-order-items"
    ORDER_DETAILS_ITEMS_ROWS = "table#my-orders-table tbody tr, table.order-details-items tbody tr, .table-order-items tbody tr"
    ORDER_DETAILS_PRODUCT_NAME = ".col.name .product-item-name, .product-item-name"
    ORDER_DETAILS_GRAND_TOTAL = "tr.grand_total td.amount, .grand_total .price, tr.order-total .price"
    ORDER_DETAILS_BILLING_ADDRESS = ".box-order-billing-address, .box-billing-address"
    ORDER_DETAILS_SHIPPING_ADDRESS = ".box-order-shipping-address, .box-shipping-address"

    # -------------------------------------------------------------------------
    # Software Licenses (/downloadable/customer/products/ or /customer/account/)
    # -------------------------------------------------------------------------
    LICENSES_PAGE_TITLE = "h1.page-title, h1"
    LICENSES_TABLE = "table#my-downloadable-products-table, .products-downloadable, .downloadable-products-table, table.data.table"
    LICENSES_ROWS = "table#my-downloadable-products-table tbody tr, .products-downloadable tbody tr, table.data.table tbody tr"
    LICENSES_COL_TITLE = ".col.title, .product-name"
    LICENSES_COL_DATE = ".col.date"
    LICENSES_COL_STATUS = ".col.status, .col.remaining"
    LICENSES_COL_DOWNLOAD = "a[href*='downloadable/download'], .col.actions a"
    LICENSES_EMPTY_MESSAGE = ".message.info.empty, .empty, .downloadable-empty"

    # -------------------------------------------------------------------------
    # Club Silhouette Membership (/clubsilhouette/customer/ or /club-silhouette)
    # -------------------------------------------------------------------------
    CLUB_PAGE_TITLE = "h1.page-title, h1:has-text('Club Silhouette'), h1:has-text('Club silhouette'), h1"
    CLUB_BANNER = ".member-ships, .membership-information, .club-banner"
    CLUB_BENEFITS_LIST = ".member-ships ul li, .membership-benefits li, .benefits-list li"
    CLUB_STATUS_INFO = ".membership-information, .club-status, #maincontent:has-text('Club')"
    CLUB_JOIN_BUTTON = "a.joinbtn, a[href*='clubsilhouette/plan']"

    # -------------------------------------------------------------------------
    # Privacy & Data Rights
    # -------------------------------------------------------------------------
    PRIVACY_PAGE_TITLE = "h1.page-title, h1"
    PRIVACY_PASSWORD_INPUT = "input#password, input[name='current_password'], input[name='password'], input[type='password']"
    DOWNLOAD_DATA_BUTTON = "button:has-text('Download Personal Data'), a:has-text('Download Personal Data'), button:has-text('Download'), #download-personal-data, [data-action='download-data']"
    DONT_SELL_SHARE_CHECKBOX = "input#dont_sell_share, input[name*='do_not_sell'], input[type='checkbox'][name*='privacy'], input#privacy_preference"
    DONT_SELL_SHARE_LABEL = "label:has-text('Don\'t Sell'), label:has-text('Do Not Sell'), label[for='dont_sell_share']"
    SAVE_PRIVACY_BUTTON = "button:has-text('Save Preference'), button:has-text('Save Settings'), button.action.save, form.form-privacy button[type='submit']"
    PRIVACY_CONFIRMATION_MESSAGE = ".messages .message-success, .message.success, .confirmation-msg"

    # -------------------------------------------------------------------------
    # My Wishlist (/wishlist/) & PDP Wishlist Button
    # -------------------------------------------------------------------------
    WISHLIST_PAGE_TITLE = "h1.page-title, h1:has-text('My wishlist'), h1:has-text('My Wishlist'), h1"
    WISHLIST_CONTAINER = "#wishlist-view-form, .products-grid.wishlist, .wishlist-index-index"
    WISHLIST_ITEMS = ".products-grid.wishlist .product-item, #wishlist-view-form .product-item, .wishlist.item, .product-item"
    WISHLIST_ITEM_NAME = ".product-item-name a, .product-item-name, strong.product-name a, a.product-item-link"
    WISHLIST_ITEM_PRICE = ".price-box .price, .price"
    WISHLIST_ITEM_IMAGE = ".product-image-photo, img"
    WISHLIST_REMOVE_BUTTON = "a.btn-remove.action.delete, a[data-role='remove'], a[title*='Remove'], .action.delete"
    WISHLIST_EMPTY_MESSAGE = ".message.info.empty, .empty, .wishlist-empty"
    WISHLIST_CLEAR_BUTTON = "#clearwishlist, a.clearwishlist, [title*='Clear Wishlist']"
    WISHLIST_ADD_ALL_TO_CART_BUTTON = "button[data-role='all-tocart'], button.action.tocart, button:has-text('Add All to Cart')"
    CART_BADGE_COUNTER = ".action.showcart .counter-number, .counter-number, .cart-counter, .minicart-wrapper .counter"
    WISHLIST_SUCCESS_MESSAGE = ".message-success, .messages .message-success, div[data-bind*='prepareMessageForHtml']"
    WISHLIST_CONFIRM_OK_BUTTON = "button.action-primary.action-accept, .action-primary:has-text('OK'), button:has-text('OK')"
    WISHLIST_AUTH_MODAL = ".login-container, #customer-popup-login, form.popup-login-form"

    # PDP Locators
    PDP_TITLE = "h1.page-title, h1, .product-info-main h1"
    PDP_PRICE = ".product-info-main .price-box .price, .product-info-price .price, .price"
    PDP_WISHLIST_BUTTON = ".pdp-wishlist a, .comparewish a, a.towishlist, .share-wishlist a, a[aria-label='wishlist'], [data-action='add-to-wishlist'], a.action.towishlist, button.action.towishlist"
    CATALOG_PRODUCT_LINKS = "a.product-item-link, .product-item-name a"
