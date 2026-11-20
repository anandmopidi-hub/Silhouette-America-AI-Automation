import json
from pathlib import Path
from typing import Any, Dict, List, Union
from utils.logger import logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_DATA_DIR = PROJECT_ROOT / "test_data"


class DataHelper:
    """Reusable loader for test data stored in the test_data/ directory."""

    @staticmethod
    def load_json(relative_or_absolute_path: Union[str, Path]) -> Any:
        """Load and return data from a JSON file.

        Args:
            relative_or_absolute_path: Path relative to test_data/ or absolute path.
        """
        path = Path(relative_or_absolute_path)
        if not path.is_absolute():
            path = TEST_DATA_DIR / path

        if not path.exists():
            raise FileNotFoundError(f"Test data file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            logger.error(f"Failed to read test data from {path}: {e}")
            raise

    @classmethod
    def load_user_data(cls, file_name: str = "users.json") -> Any:
        """Load user credentials / profiles from test_data/users/."""
        if not file_name.endswith(".json"):
            file_name += ".json"
        return cls.load_json(Path("users") / file_name)

    @classmethod
    def load_product_data(cls, file_name: str = "products.json") -> Any:
        """Load product catalog data from test_data/products/."""
        if not file_name.endswith(".json"):
            file_name += ".json"
        return cls.load_json(Path("products") / file_name)

    @classmethod
    def load_checkout_data(cls, file_name: str = "checkout.json") -> Any:
        """Load checkout / shipping / billing data from test_data/checkout/."""
        if not file_name.endswith(".json"):
            file_name += ".json"
        return cls.load_json(Path("checkout") / file_name)

    @classmethod
    def load_machine_data(cls, file_name: str = "machine_registration.json") -> Any:
        """Load machine registration test data from test_data/machines/."""
        if not file_name.endswith(".json"):
            file_name += ".json"
        return cls.load_json(Path("machines") / file_name)

    @staticmethod
    def generate_unique_email(prefix: str = "testuser", domain: str = "example.com") -> str:
        """Generate a unique email address using CommonHelper."""
        from utils.common_helper import CommonHelper
        return CommonHelper.generate_unique_email(prefix=prefix, domain=domain)

    @classmethod
    def load_software_data(cls, file_name: str = "software.json") -> Any:
        """Load software test data from test_data/software/."""
        if not file_name.endswith(".json"):
            file_name += ".json"
        return cls.load_json(Path("software") / file_name)

    @classmethod
    def load_club_data(cls, file_name: str = "club_silhouette.json") -> Any:
        """Load Club Silhouette test data from test_data/club/."""
        if not file_name.endswith(".json"):
            file_name += ".json"
        club_file = TEST_DATA_DIR / "club" / file_name
        if not club_file.exists():
            return {}
        return cls.load_json(Path("club") / file_name)

    @classmethod
    def load_account_data(cls, file_name: str = "account.json") -> Any:
        """Load My Account test data from test_data/account/."""
        if not file_name.endswith(".json"):
            file_name += ".json"
        return cls.load_json(Path("account") / file_name)




