import json
from pathlib import Path
from typing import Any, Dict, Optional
from utils.common_helper import CommonHelper
from utils.logger import logger

ORDER_DATA_FILE = CommonHelper.get_project_root() / "test_data" / "checkout" / "last_order.json"


class OrderContext:
    """Shared state container for order details across test execution."""

    _current_order: Dict[str, Any] = {}

    @classmethod
    def set_order(cls, order_details: Dict[str, Any]) -> None:
        """Store the created order details in memory and persist to disk for cross-test dependency."""
        cls._current_order = order_details
        try:
            ORDER_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(ORDER_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(order_details, f, indent=2)
            logger.info(f"Persisted created order details to: {ORDER_DATA_FILE}")
        except Exception as e:
            logger.warning(f"Could not persist order context to disk: {e}")

    @classmethod
    def get_order(cls) -> Dict[str, Any]:
        """Retrieve the latest created order details from memory or persisted file."""
        if cls._current_order:
            return cls._current_order
        if ORDER_DATA_FILE.exists():
            try:
                with open(ORDER_DATA_FILE, "r", encoding="utf-8") as f:
                    cls._current_order = json.load(f)
                    return cls._current_order
            except Exception as e:
                logger.warning(f"Failed to read persisted order context: {e}")
        return {}

    @classmethod
    def get_order_number(cls) -> str:
        """Return the captured order number, or empty string if not found."""
        order = cls.get_order()
        return order.get("order_number", "")

