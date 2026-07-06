import os
import json
import logging
from typing import Dict, Any
from stadium_ops.core.llm import generate_llm_response, MockLLMEngine

logger = logging.getLogger(__name__)

class StadiumAssistant:
    def __init__(self):
        self.data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "stadium_guides.json"
        )
        self.guides = self._load_guides()

    def _load_guides(self) -> Dict[str, Any]:
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load stadium guides JSON: {e}")
            return {}

    def get_answer(self, query: str, stadium: str, language: str = "English") -> str:
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
        answer = generate_llm_response(prompt, system_instruction=system_instruction)
        
        # If live LLM failed or API key was absent, use heuristic fallback
        if not answer:
            answer = MockLLMEngine.answer_navigation(query, stadium, self.guides)
            
        return answer
