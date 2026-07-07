"""Crowd monitoring simulator and GenAI operations incident dispatcher.

This module provides systems to model sector occupancy percentages in real-time
and classify reports of facilities, medical, or security incidents to output
volunteer checklists.
"""

import json
import logging
import random
from typing import Dict, Any, List
from stadium_ops.core.llm import generate_llm_response, MockLLMEngine
from stadium_ops.core.exceptions import LLMRequestError

logger = logging.getLogger(__name__)


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
        # Seeded generation so it is stable per render, but varies by stadium
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
    def analyze_and_dispatch_incident(report: str) -> Dict[str, Any]:
        """Analyzes a safety report and dispatches a structured action checklist.

        Uses Gemini API when available, falling back to heuristics on connection errors.

        Args:
            report: The text incident report.

        Returns:
            A dictionary of parsed parameters containing category, severity,
            department, and volunteer tasks.
        """
        # Clean text
        report = report.strip()
        if not report:
            return {}
            
        system_instruction = (
            "You are the ArenaFlow AI Operations Dispatcher. Analyze the user's stadium incident report.\n"
            "Respond ONLY with a valid JSON block of the format:\n"
            "{\n"
            "  \"severity\": \"Low\" | \"Medium\" | \"High\",\n"
            "  \"category\": \"Medical\" | \"Facilities\" | \"Security\" | \"Fan Services\",\n"
            "  \"department\": \"string naming the response unit\",\n"
            "  \"checklist\": [\"string step 1\", \"string step 2\", \"string step 3\"]\n"
            "}\n"
            "Do not include any formatting markdown like ```json, just output raw JSON."
        )
        
        prompt = f"Analyze this incident: '{report}'"
        
        try:
            response_text = generate_llm_response(prompt, system_instruction=system_instruction)
        except LLMRequestError as e:
            logger.warning(f"Live Gemini API call failed: {e}. Falling back to offline heuristics.")
            response_text = ""
        
        # If response is generated, try to parse it
        if response_text:
            try:
                # Clean up any potential markdown wrapper if LLM outputs it anyway
                cleaned_text = response_text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()
                
                parsed = json.loads(cleaned_text)
                # Quick verification of fields
                if all(k in parsed for k in ["severity", "category", "department", "checklist"]):
                    return parsed
            except Exception as e:
                logger.error(f"Failed to parse LLM incident response JSON: {response_text}. Error: {e}")
                
        # If parsing fails or LLM fails, use robust offline heuristics
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
