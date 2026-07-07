"""Google Gemini API connector and offline heuristic fallback engines.

This module provides structural interfaces to prompt the Gemini models using system
instructions, and houses rules-based fallback engines to parse user queries
locally when offline or when credentials are not configured.
"""

import json
import logging
from typing import Dict, Any, Optional
from stadium_ops.core.config import get_gemini_api_key
from stadium_ops.core.exceptions import LLMRequestError

logger = logging.getLogger(__name__)


class MockLLMEngine:
    """Rules-based text processing engine acting as an offline fallback model."""

    @staticmethod
    def answer_navigation(query: str, stadium: str, guide_data: Dict[str, Any]) -> str:
        """Heuristically answers fan questions about stadium amenities and transit.

        Args:
            query: The user's text question.
            stadium: Selected target stadium name.
            guide_data: Grounding JSON dictionary representing stadium layouts.

        Returns:
            The heuristic text answer.
        """
        query_lower = query.lower()
        stadium_info = guide_data.get(stadium, {})
        
        if "wheelchair" in query_lower or "handicap" in query_lower or "accessible" in query_lower or "fauteuil" in query_lower:
            return (
                f"[Offline AI Fallback for {stadium} Accessibility]\n"
                + stadium_info.get("accessibility", "Elevator and ramp access is available at Gate 3.")
            )
        elif "nursing" in query_lower or "baby" in query_lower or "diaper" in query_lower or "enfant" in query_lower:
            return (
                f"[Offline AI Fallback for {stadium} Amenities]\n"
                + stadium_info.get("family_services", "Diaper tables are located in family restrooms.")
            )
        elif "eat" in query_lower or "food" in query_lower or "nourriture" in query_lower or "restaurant" in query_lower:
            return (
                f"[Offline AI Fallback for {stadium} Dining]\n"
                + stadium_info.get("dining", "Hot dogs and vegan options are available at concessions.")
            )
        elif any(w in query_lower for w in ["parking", "bus", "station", "gare", "train", "sky", "metro", "transit", "rail", "transport"]):
            return (
                f"[Offline AI Fallback for {stadium} Transit]\n"
                + stadium_info.get("transit", "Light rail connections stop at Gate A.")
            )
        
        return (
            f"[Offline AI Fallback for {stadium}]\n"
            "Welcome! For gate and transit assistance, let us know what specific area you seek."
        )

    @staticmethod
    def classify_incident(report: str) -> Dict[str, Any]:
        """Categorizes and formats checklists for reported stadium incidents.

        Args:
            report: Plain text incident narrative.

        Returns:
            Dictionary detailing severity, category, department, and checklist.
        """
        report_lower = report.lower()
        
        # Heuristics for Severity
        severity = "Low"
        if any(w in report_lower for w in ["unconscious", "blood", "fire", "fight", "heart", "critical", "danger", "hurt", "faint", "fainted", "collapse", "collapsing", "emergency"]):
            severity = "High"
        elif any(w in report_lower for w in ["slip", "fall", "leak", "break", "stolen", "lost"]):
            severity = "Medium"
            
        # Heuristics for Category and Department
        category = "General"
        department = "Fan Services"
        checklist = ["Assess the situation.", "Dispatch nearest volunteer."]
        
        if any(w in report_lower for w in ["hurt", "injured", "medical", "faint", "heart", "ambulance"]):
            category = "Medical"
            department = "Medical Response Team"
            checklist = [
                "Locate AED/medical kit and carry it to the scene.",
                "Send 2 EMTs to evaluate the patient.",
                "Clear direct pathway for ambulance access if necessary."
            ]
        elif any(w in report_lower for w in ["water", "leak", "pipe", "spill", "light", "facilities", "trash"]):
            category = "Facilities / Maintenance"
            department = "Facilities & Operations"
            checklist = [
                "Locate the sector shutoff valve if water leak.",
                "Dispatch maintenance crew with mops and 'Wet Floor' signs.",
                "Clean and dry the surface to prevent slips."
            ]
        elif any(w in report_lower for w in ["fight", "security", "stolen", "threat", "rowdy", "trespass"]):
            category = "Security"
            department = "Venue Security"
            checklist = [
                "Dispatch 2 security officers to the location.",
                "Diffuse the situation and separate conflicting parties.",
                "Document IDs and escort individuals if necessary."
            ]
            
        return {
            "severity": severity,
            "category": category,
            "department": department,
            "checklist": checklist
        }


def generate_llm_response(prompt: str, system_instruction: Optional[str] = None) -> str:
    """Queries the Google Gemini API to generate content text.

    Args:
        prompt: Main query guidelines or grounding context.
        system_instruction: Static operational instruction system directives.

    Returns:
        Generated text response, or empty string if API key is not configured.

    Raises:
        LLMRequestError: If the remote model query fails during execution.
    """
    api_key = get_gemini_api_key()
    
    if not api_key:
        logger.warning("No Gemini API Key found. Falling back to simple heuristic responses.")
        return ""
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model_args = {}
        if system_instruction:
            model_args["system_instruction"] = system_instruction
            
        model = genai.GenerativeModel("gemini-1.5-flash", **model_args)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}. Raising custom LLMRequestError.")
        raise LLMRequestError(f"Failed to fetch response from Gemini model: {e}") from e
