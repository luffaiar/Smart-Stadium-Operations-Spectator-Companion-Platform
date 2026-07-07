"""Crowd monitoring simulator and GenAI operations incident dispatcher.

This module provides systems to model sector occupancy percentages in real-time
and classify reports of facilities, medical, or security incidents to output
volunteer checklists and recommend nearby volunteer dispatch assignments.
"""

import json
import logging
import random  # nosec
from typing import Dict, Any, List, Optional
from stadium_ops.core.llm import LLMServiceFactory
from stadium_ops.core.exceptions import LLMRequestError

logger = logging.getLogger(__name__)


# Roster representing active volunteers on-duty at the stadium gates and sections
VOLUNTEER_ROSTER: List[Dict[str, str]] = [
    {"name": "Marta Silva", "sector": "Zone 100 Seats", "role": "Medical Assistant", "status": "Available"},
    {"name": "Ahmed Khan", "sector": "Gate A Entrance", "role": "Navigational Guide", "status": "Available"},
    {"name": "Pierre Dupont", "sector": "Food court East", "role": "Facilities support", "status": "Available"},
    {"name": "John Smith", "sector": "VIP Lounge", "role": "Venue Security Assistant", "status": "Available"},
    {"name": "Sarah Connor", "sector": "Zone 200 Seats", "role": "General Support", "status": "Available"},
    {"name": "Luis Gomez", "sector": "Gate B Concourse", "role": "Medical Assistant", "status": "Available"}
]


class CrowdManagementService:
    """Handles venue occupancy calculations and incident log classifications."""

    @staticmethod
    def get_simulated_sectors(stadium: str, seed_value: int = 42) -> List[Dict[str, Any]]:
        """Generates mock crowd volume indicators for various stadium zones.

        Args:
            stadium: The name of the venue.
            seed_value: Random seed integer to guarantee deterministic data.

        Returns:
            A list of dictionary objects representing stadium sectors.
        """
        random.seed(hash(stadium) + seed_value)
        
        sectors = [
            {"name": "Gate A Entrance", "description": "Main public transit drop-off"},
            {"name": "Gate B Concourse", "description": "Secondary plaza and concessions"},
            {"name": "Gate C Entrance", "description": "Rail Link entry point"},
            {"name": "Zone 100 Seats", "description": "Lower bowl seating area"},
            {"name": "Zone 200 Seats", "description": "Club level suites and restrooms"},
            {"name": "Food court East", "description": "Primary concessions court"},
            {"name": "VIP Lounge", "description": "Hospitality & media suite"}
        ]
        
        for s in sectors:
            # Generate simulated densities (20% to 95%)
            density = random.randint(20, 95)
            s["density"] = density
            if density >= 85:
                s["status"] = "Critical"
                s["color"] = "#ff4b4b"  # Streamlit Red
            elif density >= 65:
                s["status"] = "Crowded"
                s["color"] = "#ffa500"  # Orange
            else:
                s["status"] = "Normal"
                s["color"] = "#00c853"  # Green
                
        return sectors

    @staticmethod
    def get_active_volunteers() -> List[Dict[str, str]]:
        """Returns the roster of active on-duty World Cup volunteers.

        Returns:
            List of volunteer dictionaries.
        """
        return VOLUNTEER_ROSTER

    @staticmethod
    def recommend_volunteer_dispatch(category: str, incident_sector: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Finds the best available volunteer based on specialty and proximity.

        Args:
            category: Classified category (e.g. Medical, Security).
            incident_sector: Optional reported location to optimize proximity.

        Returns:
            The matched volunteer dictionary, or None if none are available.
        """
        # Map incident categories to volunteer roles
        role_map = {
            "Medical": "Medical Assistant",
            "Security": "Venue Security Assistant",
            "Facilities / Maintenance": "Facilities support"
        }
        target_role = role_map.get(category, "General Support")
        
        # Filter available volunteers with matching skills
        candidates = [v for v in VOLUNTEER_ROSTER if v["role"] == target_role and v["status"] == "Available"]
        if not candidates:
            # Fallback to general support volunteers
            candidates = [v for v in VOLUNTEER_ROSTER if v["role"] in ["General Support", "Navigational Guide"] and v["status"] == "Available"]
            
        if not candidates:
            return None
            
        # Optimize by proximity if sector is reported
        if incident_sector:
            for cand in candidates:
                if cand["sector"].lower() in incident_sector.lower():
                    return cand
                    
        # Otherwise, return the first matching volunteer
        return candidates[0]

    @staticmethod
    def analyze_and_dispatch_incident(report: str, data_path: Optional[str] = None) -> Dict[str, Any]:
        """Analyzes a safety report and dispatches a structured action checklist.

        Uses the Factory LLM strategy, falling back to heuristics on connection errors.

        Args:
            report: The text incident report.
            data_path: Optional custom path to data.

        Returns:
            A dictionary containing category, severity, department, and checklist.
        """
        report = report.strip()
        if not report:
            return {}
            
        system_instruction = (
            "You are the ArenaFlow AI Operations Dispatcher. Analyze the user's stadium incident report.\n"
            "Respond ONLY with a valid JSON block of the format:\n"
            "{\n"
            "  \"severity\": \"Low\" | \"Medium\" | \"High\",\n"
            "  \"category\": \"Medical\" | \"Facilities / Maintenance\" | \"Security\" | \"Fan Services\",\n"
            "  \"department\": \"string naming the response unit\",\n"
            "  \"checklist\": [\"string step 1\", \"string step 2\", \"string step 3\"]\n"
            "}\n"
            "Do not include any formatting markdown like ```json, just output raw JSON."
        )
        
        prompt = f"Analyze this incident: '{report}'"
        
        # Fetch service from Factory
        llm_service = LLMServiceFactory.get_service(data_path)
        
        try:
            response_text = llm_service.generate_response(prompt, system_instruction=system_instruction)
        except LLMRequestError as e:
            logger.warning(f"Live Gemini strategy failed: {e}. Switching to heuristic strategy.")
            from stadium_ops.core.llm import HeuristicLLMService
            fallback_strategy = HeuristicLLMService(data_path)
            response_text = fallback_strategy.generate_response(prompt, system_instruction=system_instruction)
        
        if response_text:
            try:
                cleaned_text = response_text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()
                
                parsed = json.loads(cleaned_text)
                if all(k in parsed for k in ["severity", "category", "department", "checklist"]):
                    return parsed
            except Exception as e:
                logger.error(f"Failed to parse LLM response JSON: {response_text}. Error: {e}")
                
        # If parsing fails, use standard heuristics
        from stadium_ops.core.llm import MockLLMEngine
        return MockLLMEngine.classify_incident(report)
        
    @staticmethod
    def get_crowd_recommendations(sectors: List[Dict[str, Any]]) -> List[str]:
        """Formulates redistribution advice based on active sector occupancies.

        Args:
            sectors: List of active sectors data dictionaries.

        Returns:
            A list of recommended operational directive strings.
        """
        recommendations = []
        critical_sectors = [s["name"] for s in sectors if s["status"] == "Critical"]
        crowded_sectors = [s["name"] for s in sectors if s["status"] == "Crowded"]
        
        if critical_sectors:
            recommendations.append(
                f"🚨 **Urgent Rerouting Needed**: The density at {', '.join(critical_sectors)} is above 85%. "
                "Instruct volunteer stewards to deploy mobile signage and guide incoming flows to alternative entrances."
            )
        if crowded_sectors:
            recommendations.append(
                f"⚠️ **Pre-emptive Crowd Shift**: {', '.join(crowded_sectors)} is experiencing high volumes. "
                "Open additional service lanes or concession checkouts to reduce queue stagnation."
            )
        if not critical_sectors and not crowded_sectors:
            recommendations.append(
                "🟢 **Operations Smooth**: All stadium zones are operating within safe density margins. Continue standard security sweeps."
            )
            
        return recommendations
