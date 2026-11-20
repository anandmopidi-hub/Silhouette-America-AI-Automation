class LoginLocators:
    """Encapsulated locators for Silhouette America Login flow (popup modal & standalone page)."""

    # -------------------------------------------------------------------------
    # Header Account Navigation & Session State
    # -------------------------------------------------------------------------
    ACCOUNT_MENU_TRIGGER = ".user-link-dropdown, .user-icon, span.user-link-dropdown"
    SIGN_IN_DROPDOWN_LINK = "a.signin_link, .signin-link a, a:has-text('Sign In')"
    LOGGED_IN_WELCOME = ".customer-welcome, span.logged-in, .user-name, .greet.welcome, span.user-name.bs"
    LOGGED_IN_USER_NAME = "span.user-name, .user-name.bs, span.user-link-dropdown:not(:has-text('Account'))"
    ACCOUNT_DROPDOWN_ITEMS = ".user-link-items, .header-links"
    ACCOUNT_DROPDOWN_LINKS = ".user-link-items a, .header-links a, a[href*='customer/account']"
    SIGN_OUT_LINK = "a:has-text('Sign Out'), a[href*='logout']"
    MY_ACCOUNT_LINK = "a[href*='customer/account/'], a:has-text('My Account')"

    # -------------------------------------------------------------------------
    # Popup Login Modal Elements
    # -------------------------------------------------------------------------
    LOGIN_OVERLAY = ".login-overlay"
    POPUP_LOGIN_CONTAINER = ".login-container"
    POPUP_LOGIN_FORM = "form.popup-login-form"
    POPUP_USERNAME_INPUT = "form.popup-login-form input[name='username'], form.popup-login-form #username"
    POPUP_PASSWORD_INPUT = "form.popup-login-form input[name='popup-password'], form.popup-login-form #popup-password"
    POPUP_REMEMBER_ME_CHECKBOX = "form.popup-login-form input#remember_me, form.popup-login-form input[name='remember_me']"
    POPUP_REMEMBER_ME_LABEL = "form.popup-login-form label[for='remember_me']"
    POPUP_FORGOT_PASSWORD_LINK = "form.popup-login-form a[href*='forgotpassword'], form.popup-login-form .forgot-password"
    POPUP_SUBMIT_BUTTON = "form.popup-login-form button[type='submit']"
    POPUP_CLOSE_BUTTON = ".login-overlay .cancelbtn, form.popup-login-form .cancelbtn"
    SHOW_PASSWORD_TOGGLE = "form.popup-login-form .show-password"

    # Field-Level Client Validation Errors (Popup Modal)
    POPUP_USERNAME_ERROR = "#username-error, div.mage-error[for='username']"
    POPUP_PASSWORD_ERROR = "#popup-password-error, div.mage-error[for='popup-password']"
    RECAPTCHA_LOGIN_ERROR = "#recaptcha-login-error, .recaptcha-field-error"
    ALL_FIELD_ERRORS = "form.popup-login-form .mage-error:visible, form.popup-login-form div.mage-error:visible, form.popup-login-form label.mage-error:visible"

    # Server Response Messages (AJAX Banner in Popup)
    RESPONSE_MSG_CONTAINER = ".login-overlay .response-msg"
    RESPONSE_ERROR_MSG = ".login-overlay .response-msg .error, .login-overlay .response-msg div.error, .login-overlay .error"
    RESPONSE_SUCCESS_MSG = ".login-overlay .response-msg .success, .login-overlay .response-msg div.success"

    # -------------------------------------------------------------------------
    # Standalone Login Page (/customer/account/login)
    # -------------------------------------------------------------------------
    STANDALONE_LOGIN_FORM = "form#login-form, form.form-login"
    STANDALONE_USERNAME_INPUT = "form#login-form input#email, form#login-form input[name='login[username]']"
    STANDALONE_PASSWORD_INPUT = "form#login-form input#pass, form#login-form input[name='login[password]']"
    STANDALONE_REMEMBER_ME = "input[name='persistent_remember_me'], #remember-me-box input[type='checkbox']"
    STANDALONE_SUBMIT_BUTTON = "form#login-form button#send2, form#login-form button[type='submit']"
    STANDALONE_EMAIL_ERROR = "#email-error"
    STANDALONE_PASSWORD_ERROR = "#pass-error"

    # -------------------------------------------------------------------------
    # Customer Account Area & Protected Routes
    # -------------------------------------------------------------------------
    ACCOUNT_PAGE_TITLE = "h1.page-title, h1"
    ACCOUNT_PAGE_HEADING = ".column.main h1, h1:has-text('My Account')"
    ACCOUNT_URL_PATH = "/customer/account"
    ACCOUNT_LOGIN_PATH = "/customer/account/login"

