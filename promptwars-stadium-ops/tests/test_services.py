"""Unit tests for operations services, crowd controls, and sustainability parameters.

This module validates that sector densities are simulated correctly, volunteer
recommenders assign appropriate matching roles, incidents parse successfully,
and carbon offsets map to correct badges.
"""

from unittest.mock import patch
from stadium_ops.services.crowd_management import CrowdManagementService, VOLUNTEER_ROSTER
from stadium_ops.services.sustainability import SustainabilityService
from stadium_ops.core.exceptions import LLMRequestError


def test_get_simulated_sectors() -> None:
    """Verifies that simulated sector lists contain name, density, and status tags."""
    sectors = CrowdManagementService.get_simulated_sectors("MetLife Stadium")
    assert len(sectors) > 0
    for sector in sectors:
        assert "name" in sector
        assert "density" in sector
        assert "status" in sector


@patch('random.randint')
def test_get_simulated_sectors_branches(mock_randint) -> None:
    """Verifies that random density rolls map to correct crowd status values.

    Args:
        mock_randint: Mocked random value generator.
    """
    mock_randint.return_value = 50
    sectors = CrowdManagementService.get_simulated_sectors("MetLife Stadium")
    assert sectors[0]["status"] == "Normal"

    mock_randint.return_value = 75
    sectors = CrowdManagementService.get_simulated_sectors("MetLife Stadium")
    assert sectors[0]["status"] == "Crowded"

    mock_randint.return_value = 90
    sectors = CrowdManagementService.get_simulated_sectors("MetLife Stadium")
    assert sectors[0]["status"] == "Critical"


def test_get_crowd_recommendations() -> None:
    """Verifies crowd rerouting plans generated based on occupancy levels."""
    normal_sectors = [
        {"name": "Gate A", "density": 40, "status": "Normal", "color": "green"}
    ]
    recs = CrowdManagementService.get_crowd_recommendations(normal_sectors)
    assert len(recs) == 1
    assert "Operations Smooth" in recs[0]

    critical_sectors = [
        {"name": "Gate A", "density": 90, "status": "Critical", "color": "red"},
        {"name": "Gate B", "density": 70, "status": "Crowded", "color": "orange"}
    ]
    recs = CrowdManagementService.get_crowd_recommendations(critical_sectors)
    assert len(recs) == 2
    assert "Urgent Rerouting" in recs[0]


def test_volunteer_roster_queries() -> None:
    """Verifies that the active volunteer lists are returned successfully."""
    roster = CrowdManagementService.get_active_volunteers()
    assert len(roster) == len(VOLUNTEER_ROSTER)
    assert roster[0]["name"] == "Marta Silva"


def test_volunteer_recommendation_matching() -> None:
    """Verifies that incident types match available volunteer specialty roles."""
    # Test medical category (Marta Silva or Luis Gomez)
    v = CrowdManagementService.recommend_volunteer_dispatch("Medical", "Zone 100 Seats")
    assert v is not None
    assert v["name"] == "Marta Silva"
    
    # Test security category (John Smith)
    v_sec = CrowdManagementService.recommend_volunteer_dispatch("Security", "VIP Lounge")
    assert v_sec is not None
    assert v_sec["name"] == "John Smith"
    
    # Test facilities category (Pierre Dupont)
    v_fac = CrowdManagementService.recommend_volunteer_dispatch("Facilities / Maintenance", "Food court East")
    assert v_fac is not None
    assert v_fac["name"] == "Pierre Dupont"
    
    # Test matching default fallback when specialty matches are busy/Unavailable
    for volunteer in VOLUNTEER_ROSTER:
        if volunteer["name"] == "John Smith":
            volunteer["status"] = "Dispatched"
            
    v_fallback = CrowdManagementService.recommend_volunteer_dispatch("Security")
    assert v_fallback is not None
    assert v_fallback["role"] in ["General Support", "Navigational Guide"]
    
    # Restore John Smith status
    for volunteer in VOLUNTEER_ROSTER:
        if volunteer["name"] == "John Smith":
            volunteer["status"] = "Available"


def test_volunteer_recommendation_empty_roster() -> None:
    """Verifies that dispatch recommenders return None when all volunteers are busy."""
    orig_statuses = [v["status"] for v in VOLUNTEER_ROSTER]
    for v in VOLUNTEER_ROSTER:
        v["status"] = "Dispatched"
        
    v_none = CrowdManagementService.recommend_volunteer_dispatch("Medical")
    assert v_none is None
    
    # Restore statuses
    for idx, v in enumerate(VOLUNTEER_ROSTER):
        v["status"] = orig_statuses[idx]


def test_analyze_and_dispatch_incident_fallback() -> None:
    """Verifies rules-based mock classification for incident text inputs."""
    med_report = "A spectator fainted at Section 102."
    analysis = CrowdManagementService.analyze_and_dispatch_incident(med_report)
    assert analysis["severity"] == "High"
    assert analysis["category"] == "Medical"

    empty_analysis = CrowdManagementService.analyze_and_dispatch_incident("")
    assert empty_analysis == {}


@patch('stadium_ops.core.llm.GeminiLLMService.generate_response')
@patch('stadium_ops.core.llm.get_gemini_api_key')
def test_analyze_and_dispatch_incident_live_llm(mock_key, mock_generate) -> None:
    """Verifies live LLM parsing of emergency reports and JSON formatting.

    Args:
        mock_key: Mocked API key getter.
        mock_generate: Mocked Gemini estrategia responder.
    """
    mock_key.return_value = "dummy-key"
    mock_generate.return_value = '{"severity": "High", "category": "Medical", "department": "First Aid", "checklist": ["Check pulse"]}'
    analysis = CrowdManagementService.analyze_and_dispatch_incident("He fell down")
    assert analysis["severity"] == "High"
    assert analysis["category"] == "Medical"

    # Test Markdown wrapped JSON response
    mock_generate.return_value = '```json\n{"severity": "Medium", "category": "Security", "department": "Patrol Team", "checklist": ["Check ID"]}\n```'
    analysis = CrowdManagementService.analyze_and_dispatch_incident("Lost badge")
    assert analysis["severity"] == "Medium"
    assert analysis["category"] == "Security"

    # Test bad JSON format triggers fallback
    mock_generate.return_value = 'this is not valid json'
    analysis = CrowdManagementService.analyze_and_dispatch_incident("A spectator fainted")
    assert analysis["severity"] == "High"  # Fallback triggered


@patch('stadium_ops.core.llm.GeminiLLMService.generate_response')
@patch('stadium_ops.core.llm.get_gemini_api_key')
def test_analyze_and_dispatch_incident_live_llm_error(mock_key, mock_generate) -> None:
    """Verifies fallback classification is triggered on Gemini API request failure.

    Args:
        mock_key: Mocked API key getter.
        mock_generate: Mocked Gemini strategy responder.
    """
    mock_key.return_value = "dummy-key"
    mock_generate.side_effect = LLMRequestError("Gemini Server Error")
    analysis = CrowdManagementService.analyze_and_dispatch_incident("A spectator fainted")
    # Verify fallback is triggered gracefully
    assert analysis["severity"] == "High"
    assert analysis["category"] == "Medical"


def test_sustainability_calculate_impact_badges() -> None:
    """Verifies carbon calculators map points to correct green badges."""
    res = SustainabilityService.calculate_impact([])
    assert res["badge"] == "Green Fan Recruit"

    res = SustainabilityService.calculate_impact(["recycle_cup"])
    assert res["badge"] == "Eco Supporter (Bronze)"

    res = SustainabilityService.calculate_impact(["light_rail"])
    assert res["badge"] == "Green Advocate (Silver)"

    res = SustainabilityService.calculate_impact(["light_rail", "plant_based_meal"])
    assert res["badge"] == "Sustainability Leader (Gold)"

    res = SustainabilityService.calculate_impact(["walk_cycle", "light_rail"])
    assert res["badge"] == "Eco Champion (Platinum)"


def test_sustainability_get_eco_tip_fallback() -> None:
    """Verifies that heuristic eco recommendations are returned for logged habits."""
    assert "SkyTrain" in SustainabilityService.get_eco_tip([])
    assert "hydration" in SustainabilityService.get_eco_tip(["light_rail"])
    assert "scorecard" in SustainabilityService.get_eco_tip(["light_rail", "refill_bottle"])


@patch('stadium_ops.core.llm.GeminiLLMService.generate_response')
@patch('stadium_ops.core.llm.get_gemini_api_key')
def test_sustainability_get_eco_tip_live(mock_key, mock_generate) -> None:
    """Verifies live LLM eco tips are returned when API keys exist.

    Args:
        mock_key: Mocked API key getter.
        mock_generate: Mocked Gemini strategy responder.
    """
    mock_key.return_value = "dummy-key"
    mock_generate.return_value = "Always bring a canvas bag."
    tip = SustainabilityService.get_eco_tip(["recycle_cup"])
    assert tip == "Always bring a canvas bag."


@patch('stadium_ops.core.llm.GeminiLLMService.generate_response')
@patch('stadium_ops.core.llm.get_gemini_api_key')
def test_sustainability_get_eco_tip_live_error(mock_key, mock_generate) -> None:
    """Verifies that fallback recommendations are returned on eco generation failure.

    Args:
        mock_key: Mocked API key getter.
        mock_generate: Mocked Gemini strategy responder.
    """
    mock_key.return_value = "dummy-key"
    mock_generate.side_effect = LLMRequestError("Gemini Server Error")
    tip = SustainabilityService.get_eco_tip(["recycle_cup"])
    assert "hydration" in tip
