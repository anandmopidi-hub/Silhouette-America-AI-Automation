import time
from typing import Generator
import pytest
from playwright.sync_api import Page
from config.config import Config
from utils.logger import AutomationLogger, logger
from utils.screenshot_helper import ScreenshotHelper
from utils.video_helper import VideoHelper


@pytest.fixture(scope="function", autouse=True)
def test_lifecycle(
    request: pytest.FixtureRequest,
    app_config: Config,
) -> Generator[None, None, None]:
    """Test lifecycle fixture logging test execution and managing

    post-test artifacts (screenshots and videos) cleanly.
    """
    test_name = request.node.name
    start_time = time.time()
    logger.info(f"========== STARTING TEST: {test_name} ==========")
    AutomationLogger.log_action("Test Start", "Initiated", test_name=test_name)

    yield

    duration = time.time() - start_time
    rep_call = getattr(request.node, "rep_call", None)
    status = "passed"
    if rep_call:
        if rep_call.failed:
            status = "failed"
        elif rep_call.skipped:
            status = "skipped"
    elif getattr(request.node, "rep_setup", None) and request.node.rep_setup.failed:
        status = "failed"

    result_msg = f"Completed with status: {status.upper()} in {duration:.2f}s"
    AutomationLogger.log_action("Test Finish", result_msg, test_name=test_name)
    logger.info(f"========== FINISHED TEST: {test_name} [{status.upper()}] ==========\n")
