import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import pytest
from config.config import get_config

# Import centralized fixtures
from fixtures.browser_fixtures import app_config, browser, playwright_instance
from fixtures.page_fixtures import (
    authenticated_account_page,
    browser_context,
    catalog_page,
    clearance_page,
    club_silhouette_page,
    creator_rewards_page,
    different_pdp_page,
    exclusive_classes_page,
    footer_page,
    header_page,
    home_page,
    login_page,
    machine_registration_page,
    my_account_page,
    order_purchase_page,
    page,
    pdp_page,
    product_user_manuals_page,
    registration_page,
    search_page,
    software_page,
)
from fixtures.test_fixtures import test_lifecycle
from utils.custom_reporter import CustomReporter


PROJECT_ROOT = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_ROOT / "reports" / "html"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Central Custom Reporter Instance
custom_reporter: Optional[CustomReporter] = None


class TestLogCollector(logging.Handler):
    """In-memory logging handler capturing logs for individual test cases."""

    def __init__(self) -> None:
        super().__init__()
        self.records: List[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        try:
            formatted = self.format(record)
            # Prevent duplicate records if captured across logger hierarchies
            if not self.records or self.records[-1] != formatted:
                self.records.append(formatted)
        except Exception:
            pass

    def get_text(self) -> str:
        return "\n".join(self.records)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom command-line options for environment, browser, and execution control."""
    group = parser.getgroup("Silhouette America Framework Options")

    group.addoption(
        "--env",
        action="store",
        default="production",
        help="Target test environment: 'production' or 'staging' (default: production)",
    )
    group.addoption(
        "--browser-name",
        action="store",
        default=None,
        choices=["chromium", "firefox", "webkit"],
        help="Browser type to execute tests on: chromium, firefox, or webkit",
    )
    group.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser in headed (visible) mode instead of headless",
    )
    group.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Explicitly run browser in headless mode",
    )
    group.addoption(
        "--slowmo",
        action="store",
        type=int,
        default=None,
        help="Slow down Playwright operations by specified milliseconds",
    )
    group.addoption(
        "--base-url",
        action="store",
        default=None,
        help="Override base application URL",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest session and initialize centralized custom HTML reporter."""
    global custom_reporter
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    cfg = get_config(env=config.getoption("--env", default="production"))
    cfg.update_from_pytest_options(config)

    # Initialize Custom HTML Reporter
    report_file = REPORTS_DIR / "report.html"
    custom_reporter = CustomReporter(output_path=report_file)
    custom_reporter.environment = config.getoption("--env", default="production")
    browser_opt = config.getoption("--browser-name", default=None)
    custom_reporter.browser = browser_opt.capitalize() if browser_opt else "Chromium"
    custom_reporter.is_headless = config.getoption("--headless", default=False) or not config.getoption(
        "--headed", default=True
    )
    custom_reporter.base_url = cfg.base_url


def pytest_collection_finish(session: pytest.Session) -> None:
    """Record total discovered tests dynamically across all modules."""
    global custom_reporter
    if custom_reporter:
        custom_reporter.discovered_tests_count = len(session.items)
        custom_reporter.discovered_tests = [
            {
                "nodeid": item.nodeid,
                "name": item.name,
                "file": str(getattr(item, "path", getattr(item, "fspath", ""))),
            }
            for item in session.items
        ]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: Optional[pytest.Item]) -> Any:
    """Attach in-memory log collector around test execution to capture all technical logs."""
    handler = TestLogCollector()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    item.log_handler = handler

    try:
        yield
    finally:
        root_logger.removeHandler(handler)
        setattr(item, "captured_test_logs", handler.get_text())


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Any:
    """Pytest hook to track test outcomes, associate Test Case IDs, and capture evidence paths."""
    global custom_reporter
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    # Extract test case ID (e.g., E2E-HOME-001, E2E-LOGIN-001, E2E-ORDER_Purchase-001, E2E-Different_PDP-001)
    diff_pdp_match = re.search(r"E2E[-_]DIFFERENT[-_]PDP[-_](\d+)", item.name, re.IGNORECASE)
    order_tc_match = re.search(r"E2E[-_]ORDER[-_]PURCHASE[-_](\d+)", item.name, re.IGNORECASE)
    tc_match = re.search(r"(E2E[-_][A-Za-z0-9_]+[-_]\d+)", item.name, re.IGNORECASE)
    if diff_pdp_match:
        report.test_case_id = f"E2E-Different_PDP-{diff_pdp_match.group(1)}"
    elif order_tc_match:
        report.test_case_id = f"E2E-ORDER_Purchase-{order_tc_match.group(1)}"
    elif tc_match:
        report.test_case_id = tc_match.group(1).upper().replace("_", "-")
    else:
        report.test_case_id = item.name

    if report.when == "call" or (report.when == "setup" and report.failed):
        # Look for artifacts attached by test_lifecycle
        for prop_name, prop_val in getattr(item, "user_properties", []):
            if prop_name == "screenshot_path":
                report.screenshot_path = prop_val
            elif prop_name == "video_path":
                report.video_path = prop_val
            elif prop_name == "safety_status":
                report.safety_status = prop_val
            elif prop_name == "order_id":
                report.order_id = prop_val

    elif report.when == "teardown":
        # Propagate properties attached during fixture teardowns (page_fixtures) to rep_call
        rep_call = getattr(item, "rep_call", None)
        screenshot_path = None
        video_path = None
        for prop_name, prop_val in getattr(item, "user_properties", []):
            if prop_name == "screenshot_path":
                screenshot_path = prop_val
                if rep_call:
                    rep_call.screenshot_path = prop_val
            elif prop_name == "video_path":
                video_path = prop_val
                if rep_call:
                    rep_call.video_path = prop_val

        # Determine outcome, duration, and error details across setup, call, teardown
        rep_setup = getattr(item, "rep_setup", None)
        rep_call = getattr(item, "rep_call", None)
        rep_teardown = report

        final_outcome = "passed"
        duration = 0.0
        error_msg = None
        traceback_str = None

        if rep_setup and rep_setup.failed:
            final_outcome = "failed"
            duration = rep_setup.duration
            error_msg = str(rep_setup.longrepr)
            traceback_str = getattr(rep_setup, "longreprtext", str(rep_setup.longrepr))
        elif rep_setup and rep_setup.skipped:
            final_outcome = "skipped"
            duration = rep_setup.duration
            if rep_setup.longrepr:
                error_msg = str(rep_setup.longrepr)
        elif rep_call:
            duration = rep_call.duration
            if rep_call.failed:
                final_outcome = "failed"
                error_msg = str(rep_call.longrepr)
                traceback_str = getattr(rep_call, "longreprtext", str(rep_call.longrepr))
            elif rep_call.skipped:
                final_outcome = "skipped"
            else:
                final_outcome = "passed"
        else:
            final_outcome = "skipped"

        # Check for teardown failures
        if rep_teardown and rep_teardown.failed:
            final_outcome = "failed"
            duration += rep_teardown.duration
            td_err = str(rep_teardown.longrepr)
            td_tb = getattr(rep_teardown, "longreprtext", str(rep_teardown.longrepr))
            error_msg = f"{error_msg}\nTeardown Error: {td_err}" if error_msg else td_err
            traceback_str = f"{traceback_str}\nTeardown Traceback:\n{td_tb}" if traceback_str else td_tb

        # Capture technical logs
        captured_logs = getattr(item, "captured_test_logs", "")
        if not captured_logs and hasattr(item, "log_handler") and item.log_handler:
            captured_logs = item.log_handler.get_text()

        # Fallback to deterministic artifact paths if not in user_properties
        tc_id = getattr(report, "test_case_id", "")
        if not screenshot_path and tc_id:
            try:
                from utils.screenshot_helper import PASSED_DIR as S_PASSED, FAILED_DIR as S_FAILED, SKIPPED_DIR as S_SKIPPED
                s_target = S_PASSED if final_outcome == "passed" else (S_SKIPPED if final_outcome == "skipped" else S_FAILED)
                candidate_s = s_target / f"{tc_id}_{final_outcome}.png"
                if candidate_s.exists():
                    screenshot_path = str(candidate_s)
                else:
                    matches_s = list(s_target.glob(f"*{tc_id}*"))
                    if matches_s:
                        screenshot_path = str(matches_s[-1])
            except Exception:
                pass

        if not video_path and tc_id:
            try:
                from utils.video_helper import PASSED_VIDEOS_DIR as V_PASSED, FAILED_VIDEOS_DIR as V_FAILED, SKIPPED_VIDEOS_DIR as V_SKIPPED
                v_target = V_PASSED if final_outcome == "passed" else (V_SKIPPED if final_outcome == "skipped" else V_FAILED)
                candidate_v = v_target / f"{tc_id}_{final_outcome}.webm"
                if candidate_v.exists():
                    video_path = str(candidate_v)
                else:
                    matches_v = list(v_target.glob(f"*{tc_id}*"))
                    if matches_v:
                        video_path = str(matches_v[-1])
            except Exception:
                pass

        # Record test run in custom reporter
        if custom_reporter:
            file_path = str(getattr(item, "path", getattr(item, "fspath", "")))
            docstring = getattr(item.obj, "__doc__", None) if hasattr(item, "obj") else None
            custom_reporter.record_test_run(
                nodeid=item.nodeid,
                test_name=item.name,
                file_path=file_path,
                docstring=docstring,
                outcome=final_outcome,
                duration=duration,
                logs=captured_logs,
                screenshot_path=screenshot_path,
                video_path=video_path,
                error_msg=error_msg,
                traceback_str=traceback_str,
            )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Generate professional custom HTML report automatically upon test session completion."""
    global custom_reporter
    if getattr(session.config.option, "collectonly", False):
        return
    if custom_reporter and len(custom_reporter.test_records) > 0:
        report_path = custom_reporter.generate_html_report()
        print(f"\n================================================================================")
        print(f"[REPORTER] AI Test Automation Execution Report automatically generated at:")
        print(f"file:///{str(report_path).replace(chr(92), '/')}")
        print(f"================================================================================\n")
