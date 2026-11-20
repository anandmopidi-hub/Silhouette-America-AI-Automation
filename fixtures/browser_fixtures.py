from typing import Generator
import pytest
from playwright.sync_api import Browser, Playwright, sync_playwright
from config.config import Config, get_config
from utils.logger import logger


@pytest.fixture(scope="session")
def app_config(request: pytest.FixtureRequest) -> Config:
    """Session-level configuration fixture with CLI option overrides applied."""
    cfg = get_config()
    cfg.update_from_pytest_options(request.config)
    logger.info(
        f"Initialized test suite configuration: Environment={cfg.environment}, "
        f"Browser={cfg.browser}, Headless={cfg.headless}, BaseURL={cfg.base_url}"
    )
    return cfg


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """Session-scoped Playwright engine instance."""
    logger.info("Starting Playwright driver session")
    with sync_playwright() as playwright:
        yield playwright
    logger.info("Stopped Playwright driver session")


@pytest.fixture(scope="session")
def browser(
    playwright_instance: Playwright,
    app_config: Config,
) -> Generator[Browser, None, None]:
    """Session-scoped Browser instance launched according to configuration.

    Supports: chromium, firefox, webkit.
    """
    browser_type = app_config.browser.lower()
    headless = app_config.headless
    slow_mo = app_config.slow_mo

    logger.info(
        f"Launching browser: '{browser_type}' (headless={headless}, slow_mo={slow_mo}ms)"
    )

    if browser_type == "firefox":
        launcher = playwright_instance.firefox
    elif browser_type in ("webkit", "safari"):
        launcher = playwright_instance.webkit
    else:
        launcher = playwright_instance.chromium

    launch_args = ["--disable-blink-features=AutomationControlled"]
    if not headless:
        launch_args.append("--start-maximized")

    browser_instance = launcher.launch(
        headless=headless,
        slow_mo=slow_mo,
        args=launch_args,
    )

    yield browser_instance

    logger.info(f"Closing browser: '{browser_type}'")
    browser_instance.close()
