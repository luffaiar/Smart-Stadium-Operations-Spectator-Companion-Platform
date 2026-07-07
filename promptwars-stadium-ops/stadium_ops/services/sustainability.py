"""Sustainability calculator and carbon offset monitoring utilities.

This module provides tools to estimate carbon footprint reductions (in kilograms of CO2)
earned by green fan practices, and generates AI-driven environmental advice.
"""

import logging
from typing import Dict, Any, List
from stadium_ops.core.llm import LLMServiceFactory
from stadium_ops.core.exceptions import LLMRequestError

logger = logging.getLogger(__name__)


class SustainabilityService:
    """Manages carbon calculation systems and eco-badge awards."""

    # CO2 offsets in kilograms
    CO2_SAVINGS: Dict[str, float] = {
        "light_rail": 2.5,        # savings per trip compared to single-passenger driving
        "bus": 1.8,
        "carpool": 1.2,
        "walk_cycle": 3.5,
        "refill_bottle": 0.15,    # savings per bottle refilled instead of buying single-use plastic
        "recycle_cup": 0.08,      # savings per cup recycled
        "plant_based_meal": 0.9   # savings per meal vs beef/meat option
    }
    
    @classmethod
    def calculate_impact(cls, actions: List[str]) -> Dict[str, Any]:
        """Calculates carbon savings and maps them to a reward badge tier.

        Args:
            actions: List of checked sustainable actions.

        Returns:
            A dictionary containing total CO2 saved (kg), points, and badge name.
        """
        total_co2 = 0.0
        points = 0
        
        for action in actions:
            if action in cls.CO2_SAVINGS:
                savings = cls.CO2_SAVINGS[action]
                total_co2 += savings
                # Map savings directly to points: 100 points per kg saved
                points += int(savings * 100)
                
        # Determine badges
        badge = "Green Fan Recruit"
        if points >= 500:
            badge = "Eco Champion (Platinum)"
        elif points >= 300:
            badge = "Sustainability Leader (Gold)"
        elif points >= 150:
            badge = "Green Advocate (Silver)"
        elif points > 0:
            badge = "Eco Supporter (Bronze)"
            
        return {
            "total_co2_saved_kg": round(total_co2, 2),
            "points": points,
            "badge": badge
        }

    @staticmethod
    def get_eco_tip(actions: List[str]) -> str:
        """Generates a motivating tip using live GenAI or offline static lists.

        Args:
            actions: List of checked actions logged by the user.

        Returns:
            A string recommendation tip.
        """
        # Prompt LLM to write a personalized eco tip
        actions_str = ", ".join(actions) if actions else "no actions yet"
        
        system_instruction = (
            "You are the ArenaFlow Eco-Advisor. Write a short, motivating, one-sentence suggestion "
            "for a football fan to reduce their carbon footprint at the stadium today."
        )
        
        prompt = f"The fan has logged these green actions today: {actions_str}. Give them a direct tip."
        
        # Load the active LLM strategy from the Factory
        llm_service = LLMServiceFactory.get_service()
        
        try:
            tip = llm_service.generate_response(prompt, system_instruction=system_instruction)
        except LLMRequestError as e:
            logger.warning(f"Live Gemini strategy failed: {e}. Switching to heuristic strategy.")
            from stadium_ops.core.llm import HeuristicLLMService
            fallback_strategy = HeuristicLLMService()
            tip = fallback_strategy.generate_response(prompt, system_instruction=system_instruction)
            
        return tip
