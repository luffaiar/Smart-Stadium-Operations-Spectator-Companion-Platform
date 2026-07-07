from unittest.mock import patch
from stadium_ops.services.crowd_management import CrowdManagementService
from stadium_ops.services.sustainability import SustainabilityService

def test_get_simulated_sectors():
    sectors = CrowdManagementService.get_simulated_sectors("MetLife Stadium")
    assert len(sectors) > 0
    for sector in sectors:
        assert "name" in sector
        assert "density" in sector
        assert "status" in sector
        assert 0 <= sector["density"] <= 100


@patch('random.randint')
def test_get_simulated_sectors_branches(mock_randint):
    # Test Normal path (density = 50)
    mock_randint.return_value = 50
    sectors = CrowdManagementService.get_simulated_sectors("MetLife Stadium")
    assert sectors[0]["status"] == "Normal"
    assert sectors[0]["color"] == "#00c853"

    # Test Crowded path (density = 75)
    mock_randint.return_value = 75
    sectors = CrowdManagementService.get_simulated_sectors("MetLife Stadium")
    assert sectors[0]["status"] == "Crowded"
    assert sectors[0]["color"] == "#ffa500"

    # Test Critical path (density = 90)
    mock_randint.return_value = 90
    sectors = CrowdManagementService.get_simulated_sectors("MetLife Stadium")
    assert sectors[0]["status"] == "Critical"
    assert sectors[0]["color"] == "#ff4b4b"


def test_get_crowd_recommendations():
    # Test normal sectors
    normal_sectors = [
        {"name": "Gate A", "density": 40, "status": "Normal", "color": "green"},
        {"name": "Gate B", "density": 50, "status": "Normal", "color": "green"}
    ]
    recs = CrowdManagementService.get_crowd_recommendations(normal_sectors)
    assert len(recs) == 1
    assert "Operations Smooth" in recs[0]

    # Test critical sectors
    critical_sectors = [
        {"name": "Gate A", "density": 90, "status": "Critical", "color": "red"},
        {"name": "Gate B", "density": 70, "status": "Crowded", "color": "orange"}
    ]
    recs = CrowdManagementService.get_crowd_recommendations(critical_sectors)
    assert len(recs) == 2
    assert "Urgent Rerouting Needed" in recs[0]
    assert "Pre-emptive Crowd Shift" in recs[1]


def test_analyze_and_dispatch_incident_fallback():
    # Test fallback classification on different reports
    med_report = "A spectator fainted and is unconscious at Section 102."
    analysis = CrowdManagementService.analyze_and_dispatch_incident(med_report)
    assert analysis["severity"] == "High"
    assert analysis["category"] == "Medical"
    assert "AED" in analysis["checklist"][0] or "EMT" in analysis["checklist"][1]

    leak_report = "There is a water leak and puddle near Section 120."
    analysis = CrowdManagementService.analyze_and_dispatch_incident(leak_report)
    assert analysis["severity"] == "Medium"
    assert analysis["category"] == "Facilities / Maintenance"
    
    sec_report = "There is a rowdy fight breaking out near the concession stands."
    analysis = CrowdManagementService.analyze_and_dispatch_incident(sec_report)
    assert analysis["category"] == "Security"
    assert "security officers" in analysis["checklist"][0]

    empty_analysis = CrowdManagementService.analyze_and_dispatch_incident("")
    assert empty_analysis == {}


@patch('stadium_ops.services.crowd_management.generate_llm_response')
def test_analyze_and_dispatch_incident_live_llm(mock_llm):
    # Test raw JSON response
    mock_llm.return_value = '{"severity": "High", "category": "Medical", "department": "First Aid Team", "checklist": ["Check pulse", "Apply ice"]}'
    analysis = CrowdManagementService.analyze_and_dispatch_incident("He fell down")
    assert analysis["severity"] == "High"
    assert analysis["category"] == "Medical"
    assert analysis["department"] == "First Aid Team"
    assert "Check pulse" in analysis["checklist"]

    # Test Markdown wrapped JSON response
    mock_llm.return_value = '```json\n{"severity": "Medium", "category": "Security", "department": "Patrol Team", "checklist": ["Check ID"]}\n```'
    analysis = CrowdManagementService.analyze_and_dispatch_incident("Lost badge")
    assert analysis["severity"] == "Medium"
    assert analysis["category"] == "Security"

    # Test bad JSON format triggers fallback
    mock_llm.return_value = 'this is not valid json'
    analysis = CrowdManagementService.analyze_and_dispatch_incident("A spectator fainted")
    assert analysis["severity"] == "High"  # Fallback triggered


def test_sustainability_calculate_impact_badges():
    # Test Recruit badge (0 pts)
    res = SustainabilityService.calculate_impact([])
    assert res["badge"] == "Green Fan Recruit"

    # Test Bronze badge (points < 150)
    res = SustainabilityService.calculate_impact(["recycle_cup"])
    assert res["badge"] == "Eco Supporter (Bronze)"

    # Test Silver badge (points >= 150 and < 300)
    res = SustainabilityService.calculate_impact(["light_rail"])
    assert res["badge"] == "Green Advocate (Silver)"

    # Test Gold badge (points >= 300 and < 500)
    res = SustainabilityService.calculate_impact(["light_rail", "plant_based_meal"])
    assert res["badge"] == "Sustainability Leader (Gold)"

    # Test Platinum badge (points >= 500)
    res = SustainabilityService.calculate_impact(["walk_cycle", "light_rail"])
    assert res["badge"] == "Eco Champion (Platinum)"


def test_sustainability_get_eco_tip_fallback():
    # Test fallback eco tip responses
    assert "SkyTrain" in SustainabilityService.get_eco_tip([])
    assert "hydration" in SustainabilityService.get_eco_tip(["light_rail"])
    assert "scorecard" in SustainabilityService.get_eco_tip(["light_rail", "refill_bottle"])


@patch('stadium_ops.services.sustainability.generate_llm_response')
def test_sustainability_get_eco_tip_live(mock_llm):
    mock_llm.return_value = "Always bring a canvas bag."
    tip = SustainabilityService.get_eco_tip(["recycle_cup"])
    assert tip == "Always bring a canvas bag."


@patch('stadium_ops.services.crowd_management.generate_llm_response')
def test_analyze_and_dispatch_incident_live_llm_error(mock_llm):
    from stadium_ops.core.exceptions import LLMRequestError
    mock_llm.side_effect = LLMRequestError("Gemini Server Error")
    analysis = CrowdManagementService.analyze_and_dispatch_incident("A spectator fainted")
    assert analysis["severity"] == "High"
    assert analysis["category"] == "Medical"


@patch('stadium_ops.services.sustainability.generate_llm_response')
def test_sustainability_get_eco_tip_live_error(mock_llm):
    from stadium_ops.core.exceptions import LLMRequestError
    mock_llm.side_effect = LLMRequestError("Gemini Server Error")
    tip = SustainabilityService.get_eco_tip(["recycle_cup"])
    assert "hydration" in tip

