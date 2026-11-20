class RegistrationLocators:
    """Encapsulated locators for Silhouette America Customer Registration modal and flow."""

    # Header Triggers & Navigation
    ACCOUNT_MENU_TRIGGER = ".user-link-items, .user-link-dropdown, .user-icon, span.user-link-dropdown"
    REGISTER_DROPDOWN_LINK = ".register-link a, a[title='Register'], a[href*='customer/account/create/'].blue-link, a[href*='customer/account/create/']"
    SIGN_IN_DROPDOWN_LINK = ".signin-link a, a.signin_link, a[title='Sign In'], a[href*='customer/account/login/']"

    # Registration Modal & Form
    REGISTRATION_OVERLAY = ".login-overlay"
    REGISTRATION_CONTAINER = ".register-container"
    REGISTRATION_FORM = "form.popup-register-form"
    MODAL_TITLE = "form.popup-register-form p.popup-label"
    CLOSE_BUTTON = ".register-container .cancelbtn, form.popup-register-form .cancelbtn"

    # Form Input Fields
    FIRST_NAME_INPUT = "form.popup-register-form input[name='firstname']"
    LAST_NAME_INPUT = "form.popup-register-form input[name='lastname']"
    DOB_INPUT = "form.popup-register-form #register-dob, form.popup-register-form input[name='dob']"
    GENDER_SELECT = "form.popup-register-form #register-gender, form.popup-register-form select[name='gender']"
    EMAIL_INPUT = "form.popup-register-form input[name='email']"
    MOBILE_INPUT = "form.popup-register-form #register-mobile, form.popup-register-form input[name='mobile_number']"
    COUNTRY_CODE_SELECT = "form.popup-register-form #mobile-country-code"
    PASSWORD_INPUT = "form.popup-register-form #reg-password, form.popup-register-form input[name='password']"
    CONFIRM_PASSWORD_INPUT = "form.popup-register-form input[name='confirm-password'], form.popup-register-form input[name='password_confirmation'], form.popup-register-form #confirm-password"
    SHOW_PASSWORD_TOGGLE = "form.popup-register-form .show-password"

    # Checkboxes & Terms
    TERMS_CHECKBOX = "form.popup-register-form #termscondition, form.popup-register-form input[name='terms_agreed']"
    TERMS_LABEL = "form.popup-register-form label[for='termscondition']"
    MARKETING_CHECKBOX = "form.popup-register-form #marketingmessages, form.popup-register-form input[name='marketing_messages_agreed']"
    MARKETING_LABEL = "form.popup-register-form label[for='marketingmessages']"

    # Form Submission
    SUBMIT_BUTTON = "form.popup-register-form button[type='submit'], form.popup-register-form button.action.login.primary"

    # Server Response Messages (AJAX Banner)
    SERVER_RESPONSE_CONTAINER = ".login-overlay .response-msg"
    SERVER_ERROR_MESSAGE = ".login-overlay .response-msg .error"
    SERVER_SUCCESS_MESSAGE = ".login-overlay .response-msg .success"

    # Field-Level Client Validation Error Labels (Mage Error)
    ALL_FIELD_ERRORS = "form.popup-register-form .mage-error, form.popup-register-form div.mage-error, form.popup-register-form label.mage-error"
    FIRST_NAME_ERROR = "#firstname-error, [for='firstname'].mage-error"
    LAST_NAME_ERROR = "#lastname-error, [for='lastname'].mage-error"
    DOB_ERROR = "#register-dob-error, [for='register-dob'].mage-error, [for='dob'].mage-error"
    EMAIL_ERROR = "#email-error, [for='email'].mage-error"
    MOBILE_ERROR = "#register-mobile-error, [for='register-mobile'].mage-error, div.mage-error[for='mobile_number'], [for='mobile_number'].mage-error"
    PASSWORD_ERROR = "#reg-password-error, [for='reg-password'].mage-error, [for='password'].mage-error"
    TERMS_ERROR = "#terms_agreed-error, #termscondition-error, div.mage-error[for='terms_agreed'], [for='terms_agreed'].mage-error, [for='termscondition'].mage-error, label.mage-error[for='termscondition'], label.mage-error[for='terms_agreed']"

    # OTP Verification (Post-Registration Flow)
    LOGIN_BOX = ".login-box"
    OTP_CONTAINER = "#login-otp-combine"
    OTP_INPUT = "input[name='otp'], input.login-otp"
    OTP_RESEND_LINK = ".resend-login-otp"
    OTP_TIMER = "#otp-timer"
    OTP_SUBMIT_BUTTON = "form.popup-login-form button[type='submit'], form.popup-login-form button.action.login.primary, #login-otp-combine button[type='submit']"

    # Customer Account Area
    ACCOUNT_URL_PATH = "/customer/account/"
    ACCOUNT_PAGE_TITLE = "h1.page-title, h1"
    CUSTOMER_WELCOME = ".customer-welcome, span.logged-in"
    MY_ACCOUNT_LINK = "a[href*='customer/account/']"
