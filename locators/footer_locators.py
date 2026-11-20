"""Footer Locators Module.

Encapsulates selectors for all Silhouette America website Footer components,
including newsletter subscription, Need Help section, Legal links, Support links,
Headquarters regional links, Social media icons, Reviews.io badge, and Floating Chat/Help widget.
"""


class FooterLocators:
    """Centralized locators for footer components."""

    # Main Footer Container & Sections
    FOOTER_CONTAINER = "footer.page-footer"
    NEWSLETTER_SECTION = "section.safoot-newsletter"
    HELP_SECTION = "footer.page-footer .safoot-col--help"
    LEGAL_SECTION = "footer.page-footer .safoot-col--legal"
    SUPPORT_SECTION = "footer.page-footer .safoot-col--support"
    HEADQUARTERS_SECTION = "footer.page-footer .safoot-col--hq"
    SOCIAL_SECTION = "footer.page-footer .safoot-social"

    # Newsletter Form Elements
    NEWSLETTER_SECTION = "section.safoot-newsletter"
    NEWSLETTER_HEADING = "#safoot-newsletter-title, section.safoot-newsletter .safoot-newsletter__title, section.safoot-newsletter h2"
    NEWSLETTER_DESC = "section.safoot-newsletter .safoot-newsletter__desc, section.safoot-newsletter p"
    NEWSLETTER_FORM = "#newsletter-validate-detail"
    NEWSLETTER_EMAIL_INPUT = "#newsletter"
    NEWSLETTER_SUBSCRIBE_BUTTON = "#newsletter-validate-detail button[type='submit'], section.safoot-newsletter button"
    NEWSLETTER_SUCCESS_MESSAGE = "#newsletter_success, .newsletter_success, .message-success, .messages .message-success, div[data-bind*='prepareMessageForHtml']"
    NEWSLETTER_ERROR_MESSAGE = "#newsletter_error, .newsletter_error, .message-error, .messages .message-error, #newsletter-error"

    # Need Help / Support Email
    SUPPORT_EMAIL_LINK = "footer.page-footer .safoot-col--help a.mail"
    HELP_TITLE = "footer.page-footer .safoot-col--help .safoot-col__title"
    HELP_ADDRESS = "footer.page-footer .safoot-col--help p.loc"

    # Legal Links
    LEGAL_LINKS = "footer.page-footer .safoot-col--legal .flisting a"
    LEGAL_TERMS_OF_USE = "footer.page-footer a[href*='legal#terms-of-use']"
    LEGAL_PRIVACY_POLICY = "footer.page-footer a[href*='legal#privacy-policy']"
    LEGAL_SILHOUETTE_POLICIES = "footer.page-footer a[href$='/legal']"

    # Support Links
    SUPPORT_LINKS = "footer.page-footer .safoot-col--support .flisting a"
    SUPPORT_MACHINE_SETUP = "footer.page-footer a[href*='machine-setup']"
    SUPPORT_CREATOR_REWARDS = "footer.page-footer a[href*='creator-rewards']"
    SUPPORT_UPDATE_SOFTWARE = "footer.page-footer a[href*='/software']"
    SUPPORT_BLOG = "footer.page-footer a[href*='/blog']"
    SUPPORT_PRESS_RELEASE = "footer.page-footer a[href*='press-release']"
    SUPPORT_FAQ = "footer.page-footer a[href*='freshdesk.com']"
    SUPPORT_EDUCATION = "footer.page-footer a[href*='education']"
    SUPPORT_SITEMAP = "footer.page-footer a[href*='htmlsitemap']"
    SUPPORT_REVIEWS = "footer.page-footer .safoot-col--support a[href*='reviews']"

    # Headquarters Regional Links
    HQ_LINKS = "footer.page-footer .safoot-col--hq .place a"
    HQ_AMERICA = "footer.page-footer .safoot-col--hq a[href='https://www.silhouetteamerica.com/']"
    HQ_EUROPE = "footer.page-footer .safoot-col--hq a[href*='silhouetteeurope.eu']"
    HQ_JAPAN = "footer.page-footer .safoot-col--hq a[href*='silhouettejapan.co.jp']"

    # Social Media Links
    SOCIAL_LINKS = "footer.page-footer .safoot-social a"
    SOCIAL_INSTAGRAM = "footer.page-footer .safoot-social a.insta"
    SOCIAL_FACEBOOK = "footer.page-footer .safoot-social a.fb"
    SOCIAL_YOUTUBE = "footer.page-footer .safoot-social a.ytube"
    SOCIAL_X_TWITTER = "footer.page-footer .safoot-social a.tw"
    SOCIAL_PINTEREST = "footer.page-footer .safoot-social a.pi"

    # Reviews Badge
    REVIEWS_RIBBON_LINK = "footer.page-footer a.sa-footer-reviews-ribbon"
    REVIEWS_RIBBON_LOGO = "footer.page-footer .sa-footer-reviews-ribbon__logo img"
    REVIEWS_RIBBON_COUNT = "footer.page-footer .sa-footer-reviews-ribbon__count"

    # Floating Help / Chatbot Widget
    CHATBOT_ICON = ".chatbot-icon"
    CHATBOT_CONTAINER = "#chatbot"
    CHATBOT_ACTIVE = "#chatbot.active, .chatbot-container.active"
    CHATBOT_TITLE = "#chatbot .chatbot-title"
    CHATBOT_CLOSE_BUTTON = "#chatbot .close-btn"
    CHATBOT_OPTIONS_LIST = "#chatbot .chat-options"
    CHATBOT_OPTIONS_LINKS = "#chatbot .chat-options a"

