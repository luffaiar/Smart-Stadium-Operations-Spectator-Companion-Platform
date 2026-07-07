from stadium_ops.services.transport_service import TransportService

def test_get_transit_status():
    # Test valid stadium
    routes = TransportService.get_transit_status("MetLife Stadium")
    assert len(routes) == 3
    for r in routes:
        assert "route" in r
        assert "status" in r
        assert "delay" in r
        assert "color" in r
        
    # Test BC Place routes
    routes_bc = TransportService.get_transit_status("BC Place")
    assert len(routes_bc) == 3
    assert any("SkyTrain" in r["type"] for r in routes_bc)
    
    # Test invalid stadium
    routes_invalid = TransportService.get_transit_status("NonExistent Stadium")
    assert routes_invalid == []


from unittest.mock import patch

@patch('random.random')
def test_get_transit_status_congested_delayed(mock_random):
    # Test congested branch (0.5 < status_roll <= 0.8)
    mock_random.return_value = 0.6
    routes = TransportService.get_transit_status("MetLife Stadium")
    assert routes[0]["status"] == "Congested"
    
    # Test delayed branch (status_roll > 0.8)
    mock_random.return_value = 0.9
    routes_del = TransportService.get_transit_status("MetLife Stadium")
    assert routes_del[0]["status"] == "Delayed"
