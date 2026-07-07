"""Data repository for stadium layout and specification guides.

This module encapsulates access to the local JSON specifications database,
providing caching and error containment.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from stadium_ops.core.exceptions import DataLoadError

logger = logging.getLogger(__name__)


class StadiumRepository:
    """Repository managing loading and retrieval of stadium specification details."""

    def __init__(self, data_path: Optional[str] = None) -> None:
        """Initializes the repository and caches the guide specifications.

        Args:
            data_path: Optional custom path to stadium_guides.json.

        Raises:
            DataLoadError: If loading the JSON grounding data fails.
        """
        self.data_path = data_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "stadium_guides.json"
        )
        self._cache: Dict[str, Any] = self._load_guides()

    def _load_guides(self) -> Dict[str, Any]:
        """Loads and parses the json guide database from disk.

        Returns:
            The parsed guide dictionary data.

        Raises:
            DataLoadError: If the file is missing or contains invalid JSON formats.
        """
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load stadium guides file at {self.data_path}: {e}")
            raise DataLoadError(f"Could not load stadium specifications: {e}") from e

    def get_stadium_facts(self, stadium: str) -> Dict[str, Any]:
        """Retrieves layout and operations facts for a given stadium.

        Args:
            stadium: Target venue name.

        Returns:
            A dictionary containing transit, accessibility, and dining specifications.
        """
        return self._cache.get(stadium, {})

    def get_all_guides(self) -> Dict[str, Any]:
        """Returns the entire cached guides dictionary.

        Returns:
            The full guide specifications database.
        """
        return self._cache
