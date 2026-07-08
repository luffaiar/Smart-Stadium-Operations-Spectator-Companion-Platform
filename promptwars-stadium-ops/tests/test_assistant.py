"""Unit and integration tests for the StadiumAssistant and StadiumRepository.

This module validates that guides are loaded securely, RAG heuristics routing
takes place, path boundary rules are checked, and LLM connection errors
seamlessly trigger local fallback strategies.
"""

from unittest.mock import patch
import pytest
from stadium_ops.services.assistant import StadiumAssistant
from stadium_ops.services.stadium_repository import StadiumRepository
from stadium_ops.core.exceptions import DataLoadError, LLMRequestError


def test_stadium_repository_cache() -> None:
    """Verifies that the stadium guides specifications cache is loaded successfully."""
    repo = StadiumRepository()
    assert "MetLife Stadium" in repo.get_all_guides()
    assert repo.get_stadium_facts("MetLife Stadium") != {}
    assert repo.get_stadium_facts("NonExistent Stadium") == {}


def test_stadium_repository_load_error() -> None:
    """Verifies that non-existent paths raise standard DataLoadError exceptions."""
    import os
    package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bad_path = os.path.join(package_root, "stadium_ops", "data", "non_existent_guides.json")
    with pytest.raises(DataLoadError) as excinfo:
        StadiumRepository(data_path=bad_path)
    assert "Could not load stadium specifications" in str(excinfo.value)


def test_stadium_repository_path_traversal_warning() -> None:
    """Verifies that path traversal attempts are blocked and fallback to default."""
    repo = StadiumRepository(data_path="../../invalid_path.json")
    assert "MetLife Stadium" in repo.get_all_guides()


def test_assistant_init_repository() -> None:
    """Verifies that the StadiumAssistant links StadiumRepository successfully."""
    assistant = StadiumAssistant()
    assert isinstance(assistant.repo, StadiumRepository)


def test_assistant_get_answer_invalid_stadium() -> None:
    """Verifies that queries to unregistered stadiums return warning details."""
    assistant = StadiumAssistant()
    res = assistant.get_answer("Where is gate A?", "NonExistent Stadium")
    assert "unavailable" in res


def test_assistant_get_answer_fallback_keywords() -> None:
    """Verifies that navigation, dining, and accessibility keywords route to local fallbacks."""
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

    # Test Spanish translation fallback
    res_es = assistant.get_answer("Is there wheelchair access?", "MetLife Stadium", language="Español")
    assert "elevador" in res_es or "Puerta" in res_es


@patch('stadium_ops.core.llm.GeminiLLMService.generate_response')
@patch('stadium_ops.core.llm.get_gemini_api_key')
def test_assistant_get_answer_live_llm(mock_key, mock_generate) -> None:
    """Verifies that the RAG assistant uses the live Gemini service when API keys exist.

    Args:
        mock_key: Mocked API key getter.
        mock_generate: Mocked Gemini strategy responder.
    """
    mock_key.return_value = "dummy-key"
    mock_generate.return_value = "Grounded response for section 102 from live Gemini."
    
    assistant = StadiumAssistant()
    res = assistant.get_answer("Where is section 102?", "MetLife Stadium")
    assert res == "Grounded response for section 102 from live Gemini."


@patch('stadium_ops.core.llm.GeminiLLMService.generate_response')
@patch('stadium_ops.core.llm.get_gemini_api_key')
def test_assistant_get_answer_live_llm_failure(mock_key, mock_generate) -> None:
    """Verifies that the RAG assistant falls back to mock strategies on connection error.

    Args:
        mock_key: Mocked API key getter.
        mock_generate: Mocked Gemini strategy responder.
    """
    mock_key.return_value = "dummy-key"
    mock_generate.side_effect = LLMRequestError("Service Unavailable")
    
    assistant = StadiumAssistant()
    res = assistant.get_answer("Where is wheelchair access?", "MetLife Stadium")
    # Verify fallback strategy is triggered on error
    assert "Accessibility" in res
