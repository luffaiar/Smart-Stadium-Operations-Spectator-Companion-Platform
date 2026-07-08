"""Stadium navigation assistant and RAG (Retrieval-Augmented Generation) coordinator.

This module provides tools to answer fan queries using layout details loaded from
local json databases, integrating live GenAI with rule-based heuristics backups.
"""

import json
import logging
from typing import Dict, Any, Optional
from stadium_ops.core.llm import LLMServiceFactory
from stadium_ops.services.stadium_repository import StadiumRepository
from stadium_ops.core.exceptions import LLMRequestError

logger = logging.getLogger(__name__)


class StadiumAssistant:
    """Manages stadium guides and provides grounded RAG Q&A responses."""

    def __init__(self, data_path: Optional[str] = None) -> None:
        """Initializes the assistant using a StadiumRepository and LLM strategy.

        Args:
            data_path: Optional custom path to stadium_guides.json.
        """
        self.repo = StadiumRepository(data_path)
        # Load the appropriate LLM strategy from the Factory
        self.llm_service = LLMServiceFactory.get_service(data_path)

    def get_answer(self, query: str, stadium: str, language: str = "English") -> str:
        """Answers a user question grounded in stadium-specific guidelines.

        Args:
            query: The user's search query.
            stadium: Target venue name.
            language: The response output language (e.g. English, French).

        Returns:
            The final answer string.
        """
        # Grounding data retrieved from the Repository
        stadium_facts = self.repo.get_stadium_facts(stadium)
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
        
        # Query LLM Strategy
        try:
            answer = self.llm_service.generate_response(prompt, system_instruction=system_instruction)
        except LLMRequestError as e:
            logger.warning(f"Live Gemini strategy failed: {e}. Falling back to heuristic strategy.")
            # Explicit fallback strategy instanced dynamically on failure
            from stadium_ops.core.llm import HeuristicLLMService
            fallback_strategy = HeuristicLLMService(self.repo.data_path)
            answer = fallback_strategy.generate_response(prompt, system_instruction=system_instruction)
            
        return answer
