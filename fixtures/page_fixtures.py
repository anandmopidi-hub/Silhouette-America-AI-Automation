from typing import Generator
import pytest
from playwright.sync_api import Browser, BrowserContext, Page
from config.config import Config
from utils.logger import logger
from utils.video_helper import VideoHelper


@pytest.fixture(scope="function")
def browser_context(
    browser: Browser,
    app_config: Config,
) -> Generator[BrowserContext, None, None]:
    """Function-scoped BrowserContext providing clean isolation per test case,

    with viewport settings, video recording, and tracing support.
    """
    context_options = {
        "base_url": app_config.base_url,
        "viewport": {"width": 1280, "height": 585},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "ignore_https_errors": True,
    }

    if app_config.video != "off":
        context_options["record_video_dir"] = str(VideoHelper.get_temp_video_dir())
        context_options["record_video_size"] = {"width": 1280, "height": 585}

    context = browser.new_context(**context_options)

    if app_config.trace != "off":
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    if app_config.trace != "off":
        try:
            # Stop tracing if context is still active
            context.tracing.stop()
        except Exception:
            pass

    context.close()


@pytest.fixture(scope="function")
def page(
    browser_context: BrowserContext,
    app_config: Config,
    request: pytest.FixtureRequest,
) -> Generator[Page, None, None]:
    """Function-scoped Page fixture."""
    page_instance = browser_context.new_page()
    page_instance.set_default_timeout(app_config.timeout)

    # Track all pages created in context (primary page and any popups/new tabs)
    context_pages = [page_instance]
    browser_context.on("page", lambda new_p: context_pages.append(new_p) if new_p not in context_pages else None)

    # Attach the active page instance to the test node for hooks and reports
    request.node.user_properties.append(("page", page_instance))

    yield page_instance

    # Post-test artifact handling before closing page instance
    test_name = request.node.name
    rep_call = getattr(request.node, "rep_call", None)
    status = "passed"
    if rep_call:
        if rep_call.failed:
            status = "failed"
        elif rep_call.skipped:
            status = "skipped"
    elif getattr(request.node, "rep_setup", None) and request.node.rep_setup.failed:
        status = "failed"

    # Capture screenshot according to config policy
    should_screenshot = (app_config.screenshot == "on") or (
        app_config.screenshot == "only-on-failure" and status == "failed"
    )
    # Target the active page for screenshot: if a popup/new tab was opened, capture the active destination page
    target_page = page_instance
    if context_pages:
        latest_page = context_pages[-1]
        if not latest_page.is_closed():
            target_page = latest_page

    evidence_path = getattr(target_page, "_evidence_screenshot_path", None)
    if evidence_path:
        request.node.user_properties.append(("screenshot_path", str(evidence_path)))
    elif should_screenshot and not target_page.is_closed():
        from utils.screenshot_helper import ScreenshotHelper
        screenshot_path = ScreenshotHelper.capture_screenshot(
            page=target_page,
            test_name=test_name,
            status=status,
            handle_popups=True,
        )
        if screenshot_path:
            request.node.user_properties.append(("screenshot_path", str(screenshot_path)))

    # Safely close any auxiliary pages opened during test (e.g. popups / new tabs) to finalize their videos
    for p in context_pages:
        if p != page_instance and not p.is_closed():
            try:
                p.close()
            except Exception:
                pass

    if not page_instance.is_closed():
        page_instance.close()

    # Process recorded video after all pages are closed and file locks are released
    video_path = VideoHelper.process_test_video(
        page=page_instance,
        pages=context_pages,
        test_name=test_name,
        status=status,
        video_mode=app_config.video,
    )
    if video_path:
        request.node.user_properties.append(("video_path", str(video_path)))


@pytest.fixture(scope="function")
def home_page(page: Page, app_config: Config) -> "HomePage":
    """Function-scoped fixture providing an initialized HomePage Page Object."""
    from pages.home_page import HomePage

    return HomePage(page=page, config=app_config)


@pytest.fixture(scope="function")
def search_page(page: Page, app_config: Config) -> "SearchPage":
    """Function-scoped fixture providing an initialized SearchPage Page Object."""
    from pages.search_page import SearchPage

    return SearchPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def catalog_page(page: Page, app_config: Config) -> "CatalogPage":
    """Function-scoped fixture providing an initialized CatalogPage Page Object."""
    from pages.catalog_page import CatalogPage

    return CatalogPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def pdp_page(page: Page, app_config: Config) -> "PdpPage":
    """Function-scoped fixture providing an initialized PdpPage Page Object."""
    from pages.pdp_page import PdpPage

    return PdpPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def registration_page(page: Page, app_config: Config) -> "RegistrationPage":
    """Function-scoped fixture providing an initialized RegistrationPage Page Object."""
    from pages.registration_page import RegistrationPage

    return RegistrationPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def machine_registration_page(page: Page, app_config: Config) -> "MachineRegistrationPage":
    """Function-scoped fixture providing an initialized MachineRegistrationPage Page Object."""
    from pages.machine_registration_page import MachineRegistrationPage

    return MachineRegistrationPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def software_page(page: Page, app_config: Config) -> "SoftwarePage":
    """Function-scoped fixture providing an initialized SoftwarePage Page Object."""
    from pages.software_page import SoftwarePage

    return SoftwarePage(page=page, config=app_config)


@pytest.fixture(scope="function")
def club_silhouette_page(page: Page, app_config: Config) -> "ClubSilhouettePage":
    """Function-scoped fixture providing an initialized ClubSilhouettePage Page Object."""
    from pages.club_silhouette_page import ClubSilhouettePage

    return ClubSilhouettePage(page=page, config=app_config)


@pytest.fixture(scope="function")
def login_page(page: Page, app_config: Config) -> "LoginPage":
    """Function-scoped fixture providing an initialized LoginPage Page Object."""
    from pages.login_page import LoginPage

    return LoginPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def order_purchase_page(page: Page, app_config: Config) -> "OrderPurchasePage":
    """Function-scoped fixture providing an initialized OrderPurchasePage Page Object."""
    from pages.order_purchase_page import OrderPurchasePage

    return OrderPurchasePage(page=page, config=app_config)


@pytest.fixture(scope="function")
def different_pdp_page(page: Page, app_config: Config) -> "Different_PDP_Page":
    """Function-scoped fixture providing an initialized Different_PDP_Page Page Object."""
    from pages.different_pdp_page import Different_PDP_Page

    return Different_PDP_Page(page=page, config=app_config)


@pytest.fixture(scope="function")
def my_account_page(page: Page, app_config: Config) -> "MyAccountPage":
    """Function-scoped fixture providing an initialized MyAccountPage Page Object."""
    from pages.my_account_page import MyAccountPage

    return MyAccountPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def footer_page(page: Page, app_config: Config) -> "FooterPage":
    """Function-scoped fixture providing an initialized FooterPage Page Object."""
    from pages.footer_page import FooterPage

    return FooterPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def header_page(page: Page, app_config: Config) -> "HeaderPage":
    """Function-scoped fixture providing an initialized HeaderPage Page Object."""
    from pages.header_page import HeaderPage

    return HeaderPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def exclusive_classes_page(page: Page, app_config: Config) -> "ExclusiveClassesPage":
    """Function-scoped fixture providing an initialized ExclusiveClassesPage Page Object."""
    from pages.exclusive_classes_page import ExclusiveClassesPage

    return ExclusiveClassesPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def product_user_manuals_page(page: Page, app_config: Config) -> "ProductUserManualsPage":
    """Function-scoped fixture providing an initialized ProductUserManualsPage Page Object."""
    from pages.product_user_manuals_page import ProductUserManualsPage

    return ProductUserManualsPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def creator_rewards_page(page: Page, app_config: Config) -> "CreatorRewardsPage":
    """Function-scoped fixture providing an initialized CreatorRewardsPage Page Object."""
    from pages.creator_rewards_page import CreatorRewardsPage

    return CreatorRewardsPage(page=page, config=app_config)


@pytest.fixture(scope="function")
def clearance_page(page: Page, app_config: Config) -> "ClearancePage":
    """Function-scoped fixture providing an initialized ClearancePage Page Object."""
    from pages.clearance_page import ClearancePage

    return ClearancePage(page=page, config=app_config)


@pytest.fixture(scope="function")
def authenticated_account_page(
    login_page: "LoginPage",
    my_account_page: "MyAccountPage",
) -> "MyAccountPage":
    """Centralized authenticated-user fixture ensuring a valid customer session
    before executing authenticated test cases.
    """
    from utils.data_helper import DataHelper

    user_data = DataHelper.load_user_data().get("valid_user", {})
    email = user_data.get("email")
    password = user_data.get("password")
    assert email and password, "Valid user credentials missing from external test data."

    # Verify if already authenticated; if not, log in
    if not login_page.is_customer_authenticated(timeout_ms=3000):
        logger.info("Session not authenticated. Performing login via Login modal...")
        login_page.open_login_modal()
        login_page.fill_credentials(email=email, password=password)
        login_page.submit_login()
        assert login_page.is_customer_authenticated(timeout_ms=12000), (
            "Authentication failed: customer session could not be established."
        )

    return my_account_page











