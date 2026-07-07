"""Stadium navigation assistant and RAG (Retrieval-Augmented Generation) coordinator.

This module provides tools to answer fan queries using layout details loaded from
local json databases, integrating live GenAI with rule-based heuristics backups.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from stadium_ops.core.llm import generate_llm_response, MockLLMEngine
from stadium_ops.core.exceptions import DataLoadError, LLMRequestError

logger = logging.getLogger(__name__)


class StadiumAssistant:
    """Manages stadium guides and provides grounded RAG Q&A responses."""

    def __init__(self, data_path: Optional[str] = None) -> None:
        """Initializes the assistant and loads the stadium grounding database.

        Args:
            data_path: Optional custom path to stadium_guides.json.

        Raises:
            DataLoadError: If loading the JSON grounding data fails.
        """
        self.data_path = data_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "stadium_guides.json"
        )
        self.guides = self._load_guides()

    def _load_guides(self) -> Dict[str, Any]:
        """Reads and parses the stadium guides JSON database file.

        Returns:
            The parsed grounding data dictionary.

        Raises:
            DataLoadError: If the file is missing or contains invalid JSON.
        """
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load stadium guides JSON: {e}")
            raise DataLoadError(f"Could not load stadium specifications: {e}") from e

    def get_answer(self, query: str, stadium: str, language: str = "English") -> str:
        """Answers a user question grounded in stadium-specific guidelines.

        Args:
            query: The user's search query.
            stadium: Target venue name.
            language: The response output language (e.g. English, French).

        Returns:
            The final answer string.
        """
        # Grounding data
        stadium_facts = self.guides.get(stadium, {})
        if not stadium_facts:
            return f"Sorry, stadium guides for '{stadium}' are currently unavailable."
            
        facts_str = json.dumps(stadium_facts, indent=2)
        
        # System instructions to keep Gemini grounded and force the language
        system_instruction = (
            "You are the ArenaFlow Smart Stadium Fan Companion for the FIFA World Cup 2026.\n"
            "Answer the fan's question using ONLY the provided stadium facts.\n"
            "If the guide details do not contain the answer, politely state that you do not have that specific information.\n"
            "You MUST respond in the requested language."
        )
        
        prompt = (
            f"Stadium Facts:\n{facts_str}\n\n"
            f"Requested Response Language: {language}\n"
            f"Fan Question: {query}"
        )
        
        # Attempt LLM generation
        try:
            answer = generate_llm_response(prompt, system_instruction=system_instruction)
        except LLMRequestError as e:
            logger.warning(f"Live Gemini API request failed: {e}. Switching to heuristic fallback.")
            answer = ""
        
        # If live LLM failed or API key was absent, use heuristic fallback
        if not answer:
            answer = MockLLMEngine.answer_navigation(query, stadium, self.guides)
            
        return answer
