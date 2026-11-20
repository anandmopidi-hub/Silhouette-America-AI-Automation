import os
import random
import re
import string
from datetime import datetime
from pathlib import Path
from typing import Optional


class CommonHelper:
    """Reusable generic utility methods (file paths, timestamping, unique strings)."""

    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """Ensure a directory exists, creating parent directories if needed."""
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def get_timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
        """Return the current timestamp as a formatted string."""
        return datetime.now().strftime(fmt)

    @staticmethod
    def sanitize_filename(name: str, max_length: int = 120) -> str:
        """Sanitize a string to be safely used as a filename."""
        sanitized = re.sub(r'[\\/*?:"<>| \t\n\r]', "_", name)
        sanitized = re.sub(r"_+", "_", sanitized).strip("_")
        return sanitized[:max_length]

    @staticmethod
    def generate_random_string(length: int = 8, prefix: str = "") -> str:
        """Generate a random alphanumeric string with an optional prefix."""
        chars = string.ascii_letters + string.digits
        random_part = "".join(random.choices(chars, k=length))
        return f"{prefix}{random_part}"

    @staticmethod
    def generate_unique_email(prefix: str = "testuser", domain: str = "example.com") -> str:
        """Generate a unique email address using timestamp and random characters."""
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        return f"{prefix}_{ts}_{rand}@{domain}"

    @staticmethod
    def get_project_root() -> Path:
        """Return the root path of the automation project."""
        return Path(__file__).resolve().parent.parent
