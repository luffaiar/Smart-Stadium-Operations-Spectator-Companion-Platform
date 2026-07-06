import logging
from typing import Dict, Any, List
from stadium_ops.core.llm import generate_llm_response

logger = logging.getLogger(__name__)

class SustainabilityService:
    # CO2 offsets in kilograms
    CO2_SAVINGS = {
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
        total_co2 = 0.0
        points = 0
        
        for action in actions:
            if action in cls.CO2_SAVINGS:
                savings = cls.CO2_SAVINGS[action]
                total_co2 += savings
                # Map savings directly to points: 10 points per 0.1 kg saved (i.e. 100 points per kg)
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
        # Prompt LLM to write a personalized eco tip
        actions_str = ", ".join(actions) if actions else "no actions yet"
        
        system_instruction = (
            "You are the ArenaFlow Eco-Advisor. Write a short, motivating, one-sentence suggestion "
            "for a football fan to reduce their carbon footprint at the stadium today."
        )
        
        prompt = f"The fan has logged these green actions today: {actions_str}. Give them a direct tip."
        
        tip = generate_llm_response(prompt, system_instruction=system_instruction)
        
        if not tip:
            # Fallback tips
            if not actions:
                return "Taking the SkyTrain or light rail to the stadium is the single biggest way to cut carbon emissions today!"
            elif "refill_bottle" not in actions:
                return "Great job! Try using the hydration stations next to Gate D to keep your bottle topped up plastic-free."
            else:
                return "Fantastic effort! Share your green scorecard with friends to build eco-momentum around the tournament!"
                
        return tip
