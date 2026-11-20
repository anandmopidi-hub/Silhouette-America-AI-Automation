class MachineRegistrationLocators:
    """Encapsulated locators for Silhouette America Machine Registration flow."""

    # -------------------------------------------------------------------------
    # Header & Authentication
    # -------------------------------------------------------------------------
    ACCOUNT_TRIGGER = ".user-link-dropdown, .user-icon"
    SIGN_IN_LINK = "a.signin_link, .signin-link a, a:has-text('Sign In')"
    LOGIN_OVERLAY = ".login-overlay"
    LOGIN_FORM = "form.popup-login-form"
    LOGIN_USERNAME_INPUT = "form.popup-login-form input[name='username']"
    LOGIN_PASSWORD_INPUT = "form.popup-login-form input[name='popup-password'], #popup-password"
    LOGIN_SUBMIT_BUTTON = "form.popup-login-form button[type='submit']"
    LOGGED_IN_WELCOME = ".customer-welcome, span.logged-in, .user-name, .greet.welcome"

    # -------------------------------------------------------------------------
    # Header Machine Menu Navigation
    # -------------------------------------------------------------------------
    MACHINE_MENU_TAB = "li[data-menu='machinemenu']"
    MACHINE_MENU_PANEL = "#machinemenu-panel"
    REGISTER_MACHINE_SUBMENU = "#machinemenu-panel a:has-text('Register Machine'), a[href*='machine-setup']"
    FOOTER_MACHINE_SETUP = "footer a[href*='machine-setup']"

    # -------------------------------------------------------------------------
    # Machine Setup Form (/machine-setup)
    # -------------------------------------------------------------------------
    SETUP_PAGE_TITLE = "h1:has-text('Silhouette Machine Setup'), h1"
    REGISTER_NEW_MACHINE_HEADING = "h2:has-text('Register a NEW Machine')"
    SERIAL_NUMBER_INPUT = "input#serial-number, input[name='serial_number']"
    PURCHASE_DATE_INPUT = "input#purchase-date, input[name='purchase_date']"
    STORE_NAME_INPUT = "input#store-name, input[name='store_name']"
    STORE_COUNTRY_SELECT = "select#store-country, select[name='store_country']"
    CONTINUE_BUTTON = "button#submit-register-machine-form"

    # -------------------------------------------------------------------------
    # Validation & Alert Messages
    # -------------------------------------------------------------------------
    SERIAL_NUMBER_ERROR = "#serial-number-error"
    PURCHASE_DATE_ERROR = "#purchase-date-error"
    STORE_NAME_ERROR = "#store-name-error"
    ALL_FIELD_ERRORS = ".mage-error:visible"
    MODAL_DIALOG = ".modal-popup._show, div[role='dialog'], .setup-box, .modal-inner-wrap"
    MODAL_CONTENT = ".modal-popup._show .modal-content, .modal-content"
    MODAL_CLOSE_BUTTON = ".modal-popup._show button.action-close, button.action-close"

    # -------------------------------------------------------------------------
    # Machine Model Selection Dialog (Step 1)
    # -------------------------------------------------------------------------
    SETUP_MODAL_TITLE = ".modal-popup._show .modal-title, .modal-popup._show h1, .modal-popup._show h2, .modal-popup._show:has-text('Silhouette Machine Setup')"
    RADIO_MACHINE_OPTIONS = ".modal-popup._show input[type='radio'][name='detected_machine_selected'], .modal-popup._show input[type='radio']"
    DETECTED_MODEL_NAME = ".modal-popup._show .list-detected-machines .detected_machine_name, .modal-popup._show .machine-box"
    CAMEO_5_PLUS_OPTION = ".modal-popup._show label:has-text('CAMEO 5 PLUS'), .modal-popup._show div:has-text('CAMEO 5 PLUS')"
    REGISTER_MY_MACHINE_BUTTON = ".modal-popup._show #register_my_machine, #register_my_machine, button:has-text('Register My Machine')"

    # -------------------------------------------------------------------------
    # Address Verification Step (if requested)
    # -------------------------------------------------------------------------
    ADDRESS_STREET_INPUT = "#street"
    ADDRESS_CITY_INPUT = "#city"
    ADDRESS_STATE_INPUT = "#states"
    ADDRESS_ZIP_INPUT = "#zip"
    ADDRESS_SAVE_BUTTON = "#save_address"

    # -------------------------------------------------------------------------
    # Free Trial / Benefit Activation Dialog (Step 2)
    # -------------------------------------------------------------------------
    ACTIVATE_TRIAL_TITLE = ".modal-popup._show:has-text('Activate Your Free Trial'), .modal-popup._show:has(#free_trial)"
    CLAIM_FREE_TRIAL_BUTTON = ".modal-popup._show #free_trial, #free_trial, button:has-text('Claim Free Trial')"
    SKIP_TRIAL_BUTTON = ".modal-popup._show #skip_move_to_next, #skip_move_to_next, button:has-text('Skip')"
    FINAL_REGISTER_BUTTON = ".modal-popup._show #final_register_machine, #final_register_machine, button:has-text('Register Machine')"

    # -------------------------------------------------------------------------
    # Success Confirmation & Warranty Information
    # -------------------------------------------------------------------------
    SUCCESS_CONFIRMATION_CONTAINER = ".modal-popup._show:has-text('Congratulations'), :has-text('is now registered'), .registration-success, .success-msg"
    CONGRATULATIONS_MESSAGE = ":has-text('Congratulations!'), :has-text('is now registered'), .modal-popup._show:has-text('Congratulations')"
    CONFIRMATION_PAGE_TITLE = "h1.page-title, h1:has-text('Congratulations'), .page-title:has-text('Congratulations')"
    CONFIRMATION_CONTINUE_BUTTON = "button.action.primary:has-text('Continue'), button:has-text('Continue'), a.action.primary:has-text('Continue'), a:has-text('Continue'), .action.primary.continue, button.continue"
    WARRANTY_INFORMATION_SECTION = ":has-text('Warranty Information'), .warranty-info, .warranty-section, :has-text('Warranty')"

    # -------------------------------------------------------------------------
    # Guided Onboarding / Machine Setup Walkthrough (Steps 1 to 4)
    # -------------------------------------------------------------------------
    SETUP_GUIDE_TITLE = "h1.page-title, h1:has-text('Silhouette machine setup'), h1:has-text('Silhouette Machine Setup')"
    NEXT_STEP_BUTTON = "button:has-text('Next Step'), a:has-text('Next Step'), button:has-text('Next'), .btn-next-step, a.next-step"
    STEP_1_HEADING = ":has-text('Step 1: Check box contents & setup machine'), :has-text('Step 1: Check box contents')"
    STEP_2_HEADING = ":has-text('Step 2: Download & install software'), :has-text('Step 2: Download')"
    STEP_3_HEADING = ":has-text('Step 3: Get your free designs & 1 month Design Store subscription'), :has-text('Step 3: Get your free designs')"
    STEP_4_HEADING = ":has-text('Step 4: Learn to use your Silhouette machine and software'), :has-text('Step 4: Learn to use')"
    STEP_4_SUBTITLE_1 = ":has-text('4.1 Learn to use your Silhouette CAMEO'), :has-text('4.1')"
    STEP_4_SUBTITLE_2 = ":has-text('4.2 Learn to use the Silhouette Studio'), :has-text('4.2')"
    MANUAL_PDF_LINK = "a:has-text('manual (PDF)'), a:has-text('manual'), a[href*='.pdf'], button:has-text('manual (PDF)')"

    # -------------------------------------------------------------------------
    # Customer Account Area (/machine-setup/account/)
    # -------------------------------------------------------------------------
    ACCOUNT_URL_PATH = "/customer/account/"
    MACHINE_ACCOUNT_URL_PATH = "/machine-setup/account/"
    ACCOUNT_NAV_REGISTERED_MACHINES = ".block-collapsible-nav a[href*='machine-setup/account'], a:has-text('Machine registration')"
    REGISTERED_MACHINES_PAGE_TITLE = "h1.page-title, h1:has-text('Machines'), h1:has-text('Machine registration')"
    REGISTERED_MACHINES_MAIN_CONTENT = "#maincontent"

    # -------------------------------------------------------------------------
    # Library / Design Store Free Content
    # -------------------------------------------------------------------------
    DESIGN_STORE_HEADER_LINK = ".sa-hlogo a, header a[href*='silhouettedesignstore.com']"
    DESIGN_STORE_CREDIT_INFO = ".credit-balance, .user-credits, .account-credit, .subscription-badge"
