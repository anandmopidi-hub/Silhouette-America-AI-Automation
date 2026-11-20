import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Ensure standard output can handle utf-8 characters like 'α' on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_LOG_FILE = LOGS_DIR / "automation.log"

LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class AutomationLogger:
    """Centralized framework logger supporting console and file outputs

    with structured formatting for Timestamp, Test name, Action, Result, and Error.
    """

    _logger: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "SilhouetteAmerica") -> logging.Logger:
        if cls._logger is None:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)

            # When running under pytest, pytest.ini configures log_cli and log_file
            # on the root logger. Adding redundant handlers here causes duplicate terminal
            # and file logs. Only attach standalone handlers when not running under pytest.
            is_pytest = "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST")

            if not is_pytest and not logger.handlers:
                # Console Handler
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.INFO)
                console_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
                console_handler.setFormatter(console_formatter)
                logger.addHandler(console_handler)

                # File Handler
                file_handler = logging.FileHandler(DEFAULT_LOG_FILE, mode="a", encoding="utf-8")
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

            cls._logger = logger

        return cls._logger

    @classmethod
    def log_action(
        cls,
        action: str,
        result: str,
        test_name: Optional[str] = None,
        error: Optional[str] = None,
        level: int = logging.INFO,
    ) -> None:
        """Log a structured automation action.

        Format: [Test: <name>] Action: <action> | Result: <result> [ | Error: <error>]
        """
        logger = cls.get_logger()
        test_part = f"[Test: {test_name}] " if test_name else ""
        msg = f"{test_part}Action: {action} | Result: {result}"
        if error:
            msg += f" | Error: {error}"
            level = logging.ERROR
        logger.log(level, msg)


# Module-level convenience instance and methods
logger = AutomationLogger.get_logger()
log_action = AutomationLogger.log_action
