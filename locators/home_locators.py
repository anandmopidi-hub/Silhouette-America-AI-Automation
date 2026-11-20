class HomeLocators:
    """Encapsulated locators for Silhouette America Homepage."""

    # Cookie Consent
    COOKIE_ACCEPT_BUTTON = "button[data-amgdprcookie-js='accept'], button:has-text('I Agree'), button:has-text('I agree'), .amgdprcookie-button.-allow"
    COOKIE_BANNER = "[data-amcookie-js='bar'], .amgdprcookie-bar-container, .modal-popup._show.amgdprcookie-bar-container, .amgdprcookie-bar-template, [data-amcookie-js='banner']"

    # Logo
    LOGO = "a.logo, header .hlog a.logo"

    # Main Navigation Tabs / Buttons
    SHOP_MENU = "li[data-menu='shopmenu']"
    MACHINE_TAB = "li[data-menu='machinemenu']"
    ACCESSORIES_TAB = "li[data-menu='accemenu']"
    MATERIALS_TAB = "li[data-menu='materialmenu']"
    SOFTWARE_TAB = "li[data-menu='softwaremenu']"
    CLUB_SILHOUETTE_LINK = "nav a.fmlink[href*='club-silhouette']"
    DESIGN_STORE_LINK = ".sa-hlogo a, header .header-rightside a[href*='silhouettedesignstore.com']"
    DESIGN_STORE_LOGO = "a.logo-white img.desktop-white, img[alt*='design store logo' i]"
    DESIGN_STORE_SEARCH = "#search, input#search, input[placeholder*='search' i]"
    RESOURCES_TAB = "li[data-menu='resourcemenu']"

    # Sub-Menu Panels
    MACHINE_PANEL = "#machinemenu-panel"
    ACCESSORIES_PANEL = "#accemenu-panel"
    MATERIALS_PANEL = "#materialmenu-panel"
    SOFTWARE_PANEL = "#softwaremenu-panel"
    RESOURCES_PANEL = "#resourcemenu-panel"

    # Sub-Menu Destinations / Shop All links
    MACHINE_SHOP_ALL = "#cameo a[href$='/machines'], #cameo a:has-text('Shop All')"
    MACHINE_CUTTING_TAB = "#machinemenu-panel button.tablinks"
    ACCESSORIES_SHOP_ALL = "#accemenu-panel a[href$='/accessories-parts']"
    MATERIALS_SHOP_ALL = "#materialmenu-panel a[href$='/material']"
    SOFTWARE_SHOP_ALL = "#softwaremenu-panel a[href$='/software']"
    SUPPORT_FAQ_LINK = "#resourcemenu-panel a[href*='freshdesk.com'], #resourcemenu-panel a:has-text('FAQ')"

    # Footer Container & Critical Links
    FOOTER = "footer, .page-footer"
    FOOTER_MACHINE_SETUP = "footer a[href*='machine-setup']"
    FOOTER_CREATOR_REWARDS = "footer a[href*='creator-rewards']"
    FOOTER_UPDATE_SOFTWARE = "footer a[href*='/software']"
    FOOTER_BLOG = "footer a[href*='/blog']"
    FOOTER_TERMS_OF_USE = "footer a[href*='legal#terms-of-use']"
    FOOTER_PRIVACY_POLICY = "footer a[href*='legal#privacy-policy']"
    FOOTER_SILHOUETTE_POLICIES = "footer a[href$='/legal']"
    FOOTER_FAQ = "footer a[href*='freshdesk.com']"

    # Hero / Promotional Banners
    HERO_BANNER_CONTAINER = ".hero-banner-slider, .main-banner, .slider-wrapper"
    HERO_ACTIVE_BANNER = ".hero-banner-slider:not(.banner-loading) .swiper-slide:not(.swiper-slide-duplicate).swiper-slide-active a, .hero-banner-slider:not(.banner-loading) .swiper-slide-active a, .main-banner a"
    PROMO_BANNERS = ".hero-banner-slider a, .main-banner a, [class*='promo'] a, .slider-wrapper a"

    # Mobile & Responsive Elements
    MOBILE_MENU_TOGGLE = ".toggle-menu, .menu__icon__mobile, .mobile-menu"
    MOBILE_MENU_CATALOGUE = ".menu-catalogue"
    MAIN_CONTENT = "#maincontent, main, .page-main"

    # Customer Reviews Section & Carousel (E2E-HOME-016 & E2E-HOME-017)
    REVIEWS_SECTION = ".sa-reviews-slider-layout, section:has(.sa-reviews-slider-sidebar)"
    REVIEWS_HEADING = ".sa-reviews-slider-sidebar__title, h2:has-text('Why our customers love Silhouette')"
    REVIEWS_DESC = ".sa-reviews-slider-sidebar__desc"
    REVIEWS_RIBBON_BADGE = "a.sa-footer-reviews-ribbon, a[href*='reviews']:has-text('Read our')"
    REVIEWS_RIBBON_COUNT = ".sa-footer-reviews-ribbon__count"
    REVIEWS_SWIPER_CONTAINER = ".sa-reviews-swiper"
    REVIEWS_ACTIVE_SLIDE = ".sa-reviews-swiper .swiper-slide-active"
    REVIEWS_ALL_SLIDES = ".sa-reviews-swiper .sa-reviews-slide"
    REVIEWS_CARD = ".sa-review-card"
    REVIEWS_CARD_COMMENT = ".sa-review-card__comment"
    REVIEWS_CARD_AUTHOR = ".sa-review-card__author-name"
    REVIEWS_CARD_STARS = ".sa-review-card__stars"
    REVIEWS_CARD_VERIFIED = ".sa-review-card__verified"
    REVIEWS_ARROW_NEXT = "button.sa-reviews-slider__arrow.swiper-button-next, button[aria-label='Next review']"
    REVIEWS_ARROW_PREV = "button.sa-reviews-slider__arrow.swiper-button-prev, button[aria-label='Previous review']"
    REVIEWS_FOOTER_LINK = "footer a[href$='/reviews'], .safoot-col a:has-text('Reviews')"
    REVIEWS_DESTINATION_HEADING = "h1:has-text('Trusted by Thousands of Makers Worldwide'), .page-title:has-text('Trusted by Thousands of Makers Worldwide'), h1"


