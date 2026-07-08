"""Concrete strategy implementations for LLM services and LLM Service Factory.

This module houses the concrete strategies for Gemini and heuristic fallback engines,
orchestrating them under a unified LLMService interface using the Strategy and Factory patterns.
It also includes translations to satisfy multilingual requirements offline.
"""

import json
import logging
from typing import Dict, Any, Optional
from stadium_ops.core.config import get_gemini_api_key
from stadium_ops.core.exceptions import LLMRequestError
from stadium_ops.core.llm_interface import LLMService

logger = logging.getLogger(__name__)

# Complete translation mapping to support multilingual requirements offline
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "English": {
        "accessibility": "Elevator and ramp access is available at Gate 3.",
        "amenities": "Diaper tables are located in family restrooms.",
        "dining": "Hot dogs and vegan options are available at concessions.",
        "transit": "Light rail connections stop at Gate A.",
        "welcome": "Welcome! For gate and transit assistance, let us know what specific area you seek."
    },
    "Español": {
        "accessibility": "El acceso por elevador y rampa está disponible en la Puerta 3.",
        "amenities": "Las mesas para cambiar pañales se encuentran en los baños familiares.",
        "dining": "Los perritos calientes y las opciones veganas están disponibles en las concesiones.",
        "transit": "Las conexiones de tren ligero paran en la Puerta A.",
        "welcome": "¡Bienvenido! Para asistencia de puertas y tránsito, háganos saber qué área específica busca."
    },
    "Français": {
        "accessibility": "L'accès par ascenseur et rampe est disponible à la Porte 3.",
        "amenities": "Les tables à langer sont situées dans les toilettes familiales.",
        "dining": "Des hot-dogs et des options végétaliennes sont disponibles aux concessions.",
        "transit": "Les liaisons par métro léger s'arrêtent à la Porte A.",
        "welcome": "Bienvenue! Pour obtenir de l'aide concernant les portes et le transport, veuillez nous indiquer la zone spécifique que vous recherchez."
    },
    "Português": {
        "accessibility": "O acesso por elevador e rampa está disponível no Portão 3.",
        "amenities": "As mesas para trocar fraldas estão localizadas nos banheiros familiares.",
        "dining": "Cachorros-quentes e opções veganas estão disponíveis nas concessões.",
        "transit": "As conexões de veículo leve sobre trilhos param no Portão A.",
        "welcome": "Bem-vindo! Para assistência com portões e trânsito, informe-nos qual área específica você procura."
    },
    "Deutsch": {
        "accessibility": "Aufzug- und Rampenzugang ist an Tor 3 verfügbar.",
        "amenities": "Wickeltische befinden sich in den Familien-WCs.",
        "dining": "Hot Dogs und vegane Optionen sind an den Ständen erhältlich.",
        "transit": "Stadtbahnverbindungen halten an Tor A.",
        "welcome": "Willkommen! Für Hilfe zu Toren und Nahverkehr teilen Sie uns bitte mit, welchen Bereich Sie suchen."
    },
    "العربية": {
        "accessibility": "يتوفر مدخل للمصعد والمنحدر عند البوابة 3.",
        "amenities": "توجد طاولات تغيير الحفاضات في حمامات العائلة.",
        "dining": "تتوفر الهوت دوغ والخيارات النباتية في أكشاك البيع.",
        "transit": "تتوقف خطوط السكك الحديدية الخفيفة عند البوابة A.",
        "welcome": "مرحباً! للحصول على مساعدة بشأن البوابات والنقل، أخبرنا بالمنطقة المحددة التي تبحث عنها."
    }
}


class MockLLMEngine:
    """Helper engine providing raw rules-based text completions and incident checks."""

    @staticmethod
    def answer_navigation(query: str, stadium: str, guide_data: Dict[str, Any], language: str = "English") -> str:
        """Heuristically parses navigation queries to return matched guide text.

        Args:
            query: The user query string.
            stadium: Target venue name.
            guide_data: Stadium database dictionary.
            language: Target output language name.

        Returns:
            The heuristic answer.
        """
        query_lower = query.lower()
        stadium_info = guide_data.get(stadium, {})
        lang_dict = TRANSLATIONS.get(language, TRANSLATIONS["English"])
        
        # If language is not English, return translated fallback texts to simulate AI translation
        if language != "English":
            if "wheelchair" in query_lower or "handicap" in query_lower or "accessible" in query_lower or "fauteuil" in query_lower:
                return f"[Offline AI Fallback for {stadium} Accessibility]\n" + lang_dict["accessibility"]
            elif "nursing" in query_lower or "baby" in query_lower or "diaper" in query_lower or "enfant" in query_lower:
                return f"[Offline AI Fallback for {stadium} Amenities]\n" + lang_dict["amenities"]
            elif "eat" in query_lower or "food" in query_lower or "nourriture" in query_lower or "restaurant" in query_lower:
                return f"[Offline AI Fallback for {stadium} Dining]\n" + lang_dict["dining"]
            elif any(w in query_lower for w in ["parking", "bus", "station", "gare", "train", "sky", "metro", "transit", "rail", "transport"]):
                return f"[Offline AI Fallback for {stadium} Transit]\n" + lang_dict["transit"]
            return f"[Offline AI Fallback for {stadium}]\n" + lang_dict["welcome"]
            
        if "wheelchair" in query_lower or "handicap" in query_lower or "accessible" in query_lower or "fauteuil" in query_lower:
            return (
                f"[Offline AI Fallback for {stadium} Accessibility]\n"
                + stadium_info.get("accessibility", lang_dict["accessibility"])
            )
        elif "nursing" in query_lower or "baby" in query_lower or "diaper" in query_lower or "enfant" in query_lower:
            return (
                f"[Offline AI Fallback for {stadium} Amenities]\n"
                + stadium_info.get("family_services", lang_dict["amenities"])
            )
        elif "eat" in query_lower or "food" in query_lower or "nourriture" in query_lower or "restaurant" in query_lower:
            return (
                f"[Offline AI Fallback for {stadium} Dining]\n"
                + stadium_info.get("dining", lang_dict["dining"])
            )
        elif any(w in query_lower for w in ["parking", "bus", "station", "gare", "train", "sky", "metro", "transit", "rail", "transport"]):
            return (
                f"[Offline AI Fallback for {stadium} Transit]\n"
                + stadium_info.get("transit", lang_dict["transit"])
            )
        
        return (
            f"[Offline AI Fallback for {stadium}]\n"
            + lang_dict["welcome"]
        )

    @staticmethod
    def classify_incident(report: str) -> Dict[str, Any]:
        """Classifies the severity and category of reported incidents.

        Args:
            report: Plain text report.

        Returns:
            Dictionary format incident classification.
        """
        report_lower = report.lower()
        severity = "Low"
        if any(w in report_lower for w in ["unconscious", "blood", "fire", "fight", "heart", "critical", "danger", "hurt", "faint", "fainted", "collapse", "collapsing", "emergency"]):
            severity = "High"
        elif any(w in report_lower for w in ["slip", "fall", "leak", "break", "stolen", "lost"]):
            severity = "Medium"
            
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


class GeminiLLMService(LLMService):
    """Google Gemini model connection strategy."""

    def __init__(self, api_key: str) -> None:
        """Initializes the service with active api key.

        Args:
            api_key: The Google Gemini credentials.
        """
        self.api_key = api_key

    def generate_response(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generates content completions using live Gemini API.

        Args:
            prompt: User-supplied context or question.
            system_instruction: Operational rules for model.

        Returns:
            Completed text string response.

        Raises:
            LLMRequestError: If Gemini API throws an exception.
        """
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model_args = {}
            if system_instruction:
                model_args["system_instruction"] = system_instruction
                
            model = genai.GenerativeModel("gemini-1.5-flash", **model_args)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API execution failure: {e}")
            raise LLMRequestError(f"Failed to fetch response from Gemini model: {e}") from e


class HeuristicLLMService(LLMService):
    """Rules-based local text processor strategy."""

    def __init__(self, data_path: Optional[str] = None) -> None:
        """Initializes the local service and loads the stadium guides.

        Args:
            data_path: Optional custom path to stadium_guides.json.
        """
        from stadium_ops.services.stadium_repository import StadiumRepository
        self.repo = StadiumRepository(data_path)

    def generate_response(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Parses the prompt and selects matching heuristics to mimic model completions.

        Args:
            prompt: User query containing metadata tags.
            system_instruction: Optional system context.

        Returns:
            Heuristic completion text.
        """
        prompt_lower = prompt.lower()
        
        # 1. Incident Dispatcher request matching
        if "analyze this incident:" in prompt_lower:
            import re
            match = re.search(r"incident:\s*'(.*?)'", prompt)
            report = match.group(1) if match else prompt
            res = MockLLMEngine.classify_incident(report)
            return json.dumps(res)
            
        # 2. Fan RAG Chatbot request matching
        elif "fan question:" in prompt_lower:
            stadium = "MetLife Stadium"
            for s in ["MetLife Stadium", "Estadio Azteca", "BC Place"]:
                if s.lower() in prompt_lower:
                    stadium = s
                    break
            
            # Retrieve language from prompt context
            language = "English"
            for l in ["English", "Español", "Français", "Português", "Deutsch", "العربية"]:
                if f"requested response language: {l.lower()}" in prompt_lower:
                    language = l
                    break
                    
            import re
            match = re.search(r"fan question:\s*(.*)", prompt, re.IGNORECASE)
            query = match.group(1) if match else prompt
            return MockLLMEngine.answer_navigation(query, stadium, self.repo.get_all_guides(), language)
            
        # 3. Sustainability Eco Tip request matching
        elif "green actions" in prompt_lower:
            if "no actions yet" in prompt_lower:
                return "Taking the SkyTrain or light rail to the stadium is the single biggest way to cut carbon emissions today!"
            elif "refill_bottle" not in prompt_lower:
                return "Great job! Try using the hydration stations next to Gate D to keep your bottle topped up plastic-free."
            else:
                return "Fantastic effort! Share your green scorecard with friends to build eco-momentum around the tournament!"
                
        return "Welcome! How can we help you at the stadium today?"


class LLMServiceFactory:
    """Factory builder initializing active LLM Strategy classes."""

    @staticmethod
    def get_service(data_path: Optional[str] = None) -> LLMService:
        """Returns the appropriate LLMService strategy based on key presence.

        Args:
            data_path: Optional custom path to stadium specifications.

        Returns:
            An active LLMService strategy class.
        """
        api_key = get_gemini_api_key()
        if api_key:
            return GeminiLLMService(api_key)
        else:
            return HeuristicLLMService(data_path)
