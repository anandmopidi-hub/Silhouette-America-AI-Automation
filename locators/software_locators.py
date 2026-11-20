class SoftwareLocators:
    """Encapsulated locators for Silhouette America Software and License Keys flow."""

    # -------------------------------------------------------------------------
    # Software Page Elements (/software)
    # -------------------------------------------------------------------------
    SOFTWARE_PAGE_HEADING = "h1:has-text('Empower Your Creativity with Silhouette Software'), h1"
    SOFTWARE_SECTION_STUDIO = "h2:has-text('Silhouette Studio'), h2:has-text('Silhouette Studio®')"
    SOFTWARE_SECTION_CONNECT = "h2:has-text('Silhouette Connect')"
    SOFTWARE_CARDS = ".software-box, .software-block, .product-item, #maincontent section"

    # Supported OS Download Buttons
    DOWNLOAD_WINDOWS_BUTTON = "a.btn.windows.dldbtn, a[href*='_W6R.exe'], a:has-text('Win 64')"
    DOWNLOAD_MAC_BUTTON = "a.btn.mac.dldbtn, a[href*='_M6R.dmg'], a:has-text('MAC 64')"
    ALL_DOWNLOAD_BUTTONS = "a.dldbtn, a[class*='dldbtn']"

    # Compatibility & Documentation Links
    SYSTEM_REQUIREMENTS_LINK = "a.link:has-text('System requirements'), a:has-text('System requirements')"
    LEGACY_VERSIONS_LINK = "a.link:has-text('Legacy versions'), a:has-text('Legacy versions')"
    RELEASE_NOTES_LINK = "a.link:has-text('Release Notes'), a:has-text('Release Notes')"

    # -------------------------------------------------------------------------
    # Header & Account Navigation
    # -------------------------------------------------------------------------
    ACCOUNT_TRIGGER = ".user-link-dropdown, .user-icon"
    SIGN_IN_LINK = "a.signin_link, .signin-link a, a:has-text('Sign In')"
    LOGIN_OVERLAY = ".login-overlay"
    LOGGED_IN_WELCOME = ".customer-welcome, span.logged-in, .user-name, .greet.welcome"
    ACCOUNT_SIDEBAR_LICENSE_LINK = ".block-collapsible-nav a[href*='license/apply'], .block-collapsible-nav a:has-text('License keys')"
    USER_DROPDOWN_LICENSE_LINK = "a.account-sub[href*='license/apply'], a:has-text('Software License Keys')"

    # Popup / Full-Page Login Form
    POPUP_LOGIN_FORM = "form.popup-login-form"
    POPUP_USERNAME_INPUT = "form.popup-login-form input[name='username']"
    POPUP_PASSWORD_INPUT = "form.popup-login-form input[name='popup-password'], #popup-password"
    POPUP_SUBMIT_BUTTON = "form.popup-login-form button[type='submit']"

    FULL_LOGIN_FORM = "form#login-form, form[action*='loginPost'], .login-container"
    FULL_USERNAME_INPUT = "input#email, input[name='login[username]']"
    FULL_PASSWORD_INPUT = "input#pass, input[name='login[password]']"
    FULL_SUBMIT_BUTTON = "button#send2, button[type='submit']"

    # -------------------------------------------------------------------------
    # Software License Keys Management (/license/apply/)
    # -------------------------------------------------------------------------
    LICENSE_PAGE_HEADING = "h1:has-text('License keys'), h1, .page-title"
    LICENSE_KEY_INPUT = "input#license_key, input[name='license_key'], .license-key-form"
    LICENSE_APPLY_BUTTON = "button.submit:has-text('Apply'), .license-key-inner button.submit, button.submit"
    LICENSE_TABLES = "table.license"
    LICENSE_TABLE_ROWS = "table.license tbody tr, table.license tr"
    LICENSE_TABLE_HEADERS = "table.license th"
    PURCHASED_LICENSES_WRAPPER = ".software-licenses-wrapper"

    # Notifications & Alert Messages
    ALERT_MESSAGES = ".message, .messages, [class*='message'], .error-msg, .success-msg"
    SUCCESS_MESSAGE = ".message-success, .success.message, .messages:has-text('Applied')"
    COOKIE_ACCEPT_BUTTON = "button[data-amgdprcookie-js='accept'], button:has-text('I Agree'), button:has-text('I agree'), .amgdprcookie-button.-allow"
