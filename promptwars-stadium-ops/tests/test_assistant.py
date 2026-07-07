import pytest
from unittest.mock import patch
from stadium_ops.services.assistant import StadiumAssistant
from stadium_ops.core.exceptions import DataLoadError, LLMRequestError

def test_assistant_load_guides():
    assistant = StadiumAssistant()
    assert len(assistant.guides) > 0
    assert "MetLife Stadium" in assistant.guides
    assert "Estadio Azteca" in assistant.guides
    assert "BC Place" in assistant.guides


def test_assistant_load_error():
    # Pass an invalid file path to trigger file load exception
    with pytest.raises(DataLoadError) as excinfo:
        StadiumAssistant(data_path="non_existent_guides_file.json")
    assert "Could not load stadium specifications" in str(excinfo.value)


def test_assistant_get_answer_invalid_stadium():
    assistant = StadiumAssistant()
    res = assistant.get_answer("Where is gate A?", "NonExistent Stadium")
    assert "unavailable" in res


def test_assistant_get_answer_fallback_keywords():
    assistant = StadiumAssistant()
    
    # Test accessibility keyword
    res_acc = assistant.get_answer("Is there wheelchair access?", "MetLife Stadium")
    assert "Accessibility" in res_acc or "accessibility" in res_acc
    assert "Gate C" in res_acc or "Gate D" in res_acc or "elevator" in res_acc
    
    # Test transit keyword (using train/station keywords)
    res_transit = assistant.get_answer("How to go by train?", "BC Place")
    assert "Transit" in res_transit
    assert "Expo Line SkyTrain" in res_transit
    
    # Test dining keyword
    res_dining = assistant.get_answer("Where to eat food?", "Estadio Azteca")
    assert "Dining" in res_dining
    assert "concessions" in res_dining
    
    # Test nursing/baby keyword
    res_baby = assistant.get_answer("Do you have diaper changing stations?", "MetLife Stadium")
    assert "Amenities" in res_baby
    assert "diaper-changing" in res_baby or "restrooms" in res_baby
    
    # Test generic query with no match
    res_generic = assistant.get_answer("Tell me about the matches", "MetLife Stadium")
    assert "Welcome!" in res_generic


@patch('stadium_ops.services.assistant.generate_llm_response')
def test_assistant_get_answer_live_llm(mock_llm):
    mock_llm.return_value = "Grounded response for section 102 from live Gemini."
    assistant = StadiumAssistant()
    res = assistant.get_answer("Where is section 102?", "MetLife Stadium")
    assert res == "Grounded response for section 102 from live Gemini."


@patch('stadium_ops.services.assistant.generate_llm_response')
def test_assistant_get_answer_live_llm_failure(mock_llm):
    # Mock live API throwing an exception to ensure graceful fallback
    mock_llm.side_effect = LLMRequestError("Service Unavailable")
    assistant = StadiumAssistant()
    res = assistant.get_answer("Where is wheelchair access?", "MetLife Stadium")
    # Verify fallback is triggered rather than raising error
    assert "Accessibility" in res
