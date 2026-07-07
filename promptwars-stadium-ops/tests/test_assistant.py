import pytest
from unittest.mock import patch
from stadium_ops.services.assistant import StadiumAssistant
from stadium_ops.services.stadium_repository import StadiumRepository
from stadium_ops.core.exceptions import DataLoadError, LLMRequestError

def test_stadium_repository_cache():
    repo = StadiumRepository()
    assert "MetLife Stadium" in repo.get_all_guides()
    assert repo.get_stadium_facts("MetLife Stadium") != {}
    assert repo.get_stadium_facts("NonExistent Stadium") == {}


def test_stadium_repository_load_error():
    import os
    package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bad_path = os.path.join(package_root, "stadium_ops", "data", "non_existent_guides.json")
    with pytest.raises(DataLoadError) as excinfo:
        StadiumRepository(data_path=bad_path)
    assert "Could not load stadium specifications" in str(excinfo.value)


def test_stadium_repository_path_traversal_warning():
    repo = StadiumRepository(data_path="../../invalid_path.json")
    assert "MetLife Stadium" in repo.get_all_guides()


def test_assistant_init_repository():
    assistant = StadiumAssistant()
    assert isinstance(assistant.repo, StadiumRepository)


def test_assistant_get_answer_invalid_stadium():
    assistant = StadiumAssistant()
    res = assistant.get_answer("Where is gate A?", "NonExistent Stadium")
    assert "unavailable" in res


def test_assistant_get_answer_fallback_keywords():
    assistant = StadiumAssistant()
    
    # Test accessibility keyword
    res_acc = assistant.get_answer("Is there wheelchair access?", "MetLife Stadium")
    assert "Accessibility" in res_acc or "accessibility" in res_acc
    
    # Test transit keyword
    res_transit = assistant.get_answer("How to go by train?", "BC Place")
    assert "Transit" in res_transit
    
    # Test dining keyword
    res_dining = assistant.get_answer("Where to eat food?", "Estadio Azteca")
    assert "Dining" in res_dining
    
    # Test nursing/baby keyword
    res_baby = assistant.get_answer("Do you have diaper changing stations?", "MetLife Stadium")
    assert "Amenities" in res_baby


@patch('stadium_ops.core.llm.GeminiLLMService.generate_response')
@patch('stadium_ops.core.llm.get_gemini_api_key')
def test_assistant_get_answer_live_llm(mock_key, mock_generate):
    mock_key.return_value = "dummy-key"
    mock_generate.return_value = "Grounded response for section 102 from live Gemini."
    
    assistant = StadiumAssistant()
    res = assistant.get_answer("Where is section 102?", "MetLife Stadium")
    assert res == "Grounded response for section 102 from live Gemini."


@patch('stadium_ops.core.llm.GeminiLLMService.generate_response')
@patch('stadium_ops.core.llm.get_gemini_api_key')
def test_assistant_get_answer_live_llm_failure(mock_key, mock_generate):
    mock_key.return_value = "dummy-key"
    mock_generate.side_effect = LLMRequestError("Service Unavailable")
    
    assistant = StadiumAssistant()
    res = assistant.get_answer("Where is wheelchair access?", "MetLife Stadium")
    # Verify fallback strategy is triggered on error
    assert "Accessibility" in res
