import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
ENVIRONMENTS_DIR = CONFIG_DIR / "environments"


class Config:
    """Central configuration class supporting environment-based settings

    and runtime CLI/Environment variable overrides.
    """

    _instance: Optional["Config"] = None
    _config_data: Dict[str, Any] = {}

    def __init__(self, env: Optional[str] = None):
        """Initialize configuration for the specified or detected environment.

        Args:
            env: Target environment name ('production' or 'staging'). If not supplied,
                 it is read from ENV environment variable or defaults to 'production'.
        """
        self.environment_name = (
            env
            or os.getenv("ENV")
            or os.getenv("ENVIRONMENT")
            or "production"
        ).strip().lower()

        self._load_environment_config()
        self._apply_env_var_overrides()

    def _load_environment_config(self) -> None:
        """Load JSON configuration for the active environment."""
        env_file = ENVIRONMENTS_DIR / f"{self.environment_name}.json"
        if not env_file.exists():
            raise FileNotFoundError(
                f"Configuration file for environment '{self.environment_name}' "
                f"not found at: {env_file}"
            )

        with open(env_file, "r", encoding="utf-8") as f:
            self._config_data = json.load(f)

    def _apply_env_var_overrides(self) -> None:
        """Allow runtime system environment variables to override JSON settings."""
        if os.getenv("BASE_URL"):
            self._config_data["BASE_URL"] = os.getenv("BASE_URL")
        if os.getenv("BROWSER"):
            self._config_data["BROWSER"] = os.getenv("BROWSER").lower()
        if os.getenv("HEADLESS") is not None:
            self._config_data["HEADLESS"] = os.getenv("HEADLESS").lower() in ("true", "1", "yes")
        if os.getenv("SLOW_MO"):
            self._config_data["SLOW_MO"] = int(os.getenv("SLOW_MO"))
        if os.getenv("TIMEOUT"):
            self._config_data["TIMEOUT"] = int(os.getenv("TIMEOUT"))
        if os.getenv("VIDEO"):
            self._config_data["VIDEO"] = os.getenv("VIDEO")
        if os.getenv("SCREENSHOT"):
            self._config_data["SCREENSHOT"] = os.getenv("SCREENSHOT")
        if os.getenv("TRACE"):
            self._config_data["TRACE"] = os.getenv("TRACE")

    def update_from_pytest_options(self, pytest_config: Any) -> None:
        """Update configuration dynamically from Pytest command line options."""
        env_opt = pytest_config.getoption("--env", default=None)
        if env_opt and env_opt.strip().lower() != self.environment_name:
            self.environment_name = env_opt.strip().lower()
            self._load_environment_config()
            self._apply_env_var_overrides()

        browser_opt = pytest_config.getoption("--browser-name", default=None)
        if browser_opt:
            self._config_data["BROWSER"] = browser_opt.lower()

        headed_opt = pytest_config.getoption("--headed", default=False)
        if headed_opt:
            self._config_data["HEADLESS"] = False

        headless_opt = pytest_config.getoption("--headless", default=False)
        if headless_opt:
            self._config_data["HEADLESS"] = True

        slowmo_opt = pytest_config.getoption("--slowmo", default=None)
        if slowmo_opt is not None:
            self._config_data["SLOW_MO"] = int(slowmo_opt)

        base_url_opt = pytest_config.getoption("--base-url", default=None)
        if base_url_opt:
            self._config_data["BASE_URL"] = base_url_opt

    @property
    def base_url(self) -> str:
        return self._config_data.get("BASE_URL", "https://www.silhouetteamerica.com/")

    @property
    def environment(self) -> str:
        return self._config_data.get("ENVIRONMENT", self.environment_name)

    @property
    def browser(self) -> str:
        return self._config_data.get("BROWSER", "chromium").lower()

    @property
    def headless(self) -> bool:
        return bool(self._config_data.get("HEADLESS", True))

    @property
    def slow_mo(self) -> int:
        return int(self._config_data.get("SLOW_MO", 0))

    @property
    def timeout(self) -> int:
        return int(self._config_data.get("TIMEOUT", 30000))

    @property
    def video(self) -> str:
        # Options: 'on', 'off', 'retain-on-failure'
        return self._config_data.get("VIDEO", "retain-on-failure")

    @property
    def screenshot(self) -> str:
        # Options: 'on', 'off', 'only-on-failure'
        return self._config_data.get("SCREENSHOT", "only-on-failure")

    @property
    def trace(self) -> str:
        # Options: 'on', 'off', 'retain-on-failure'
        return self._config_data.get("TRACE", "retain-on-failure")

    def get(self, key: str, default: Any = None) -> Any:
        return self._config_data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._config_data)


_active_config: Optional[Config] = None


def get_config(env: Optional[str] = None) -> Config:
    """Singleton-style accessor for the framework configuration."""
    global _active_config
    if _active_config is None or (env and _active_config.environment_name != env.strip().lower()):
        _active_config = Config(env=env)
    return _active_config
