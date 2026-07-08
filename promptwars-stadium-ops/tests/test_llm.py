"""Unit and integration tests for the LLM Services.

This module validates that credentials getters check environment settings and Streamlit
secrets, Heuristic strategy parsers mimic Gemini responses offline, and mock Gemini
connections handle generation success and failure modes correctly.
"""

import os
import json
import pytest
from unittest.mock import patch
from stadium_ops.core.config import get_gemini_api_key
from stadium_ops.core.llm import GeminiLLMService, HeuristicLLMService, LLMServiceFactory
from stadium_ops.core.exceptions import LLMRequestError


def test_get_gemini_api_key_from_env() -> None:
    """Verifies that API keys are retrieved correctly from environment variables."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-env-key"}):
        assert get_gemini_api_key() == "test-env-key"


def test_get_gemini_api_key_from_secrets() -> None:
    """Verifies that API keys are retrieved correctly from Streamlit secrets."""
    with patch.dict(os.environ, {}, clear=True):
        mock_secrets = {"GEMINI_API_KEY": "test-secrets-key"}
        with patch('streamlit.secrets', mock_secrets), \
             patch('os.path.exists', return_value=True):
            assert get_gemini_api_key() == "test-secrets-key"


def test_get_gemini_api_key_missing() -> None:
    """Verifies that empty strings are returned when credentials are missing."""
    with patch.dict(os.environ, {}, clear=True):
        with patch('streamlit.secrets', {}):
            assert get_gemini_api_key() == ""


@patch('stadium_ops.core.llm.get_gemini_api_key')
def test_llm_service_factory(mock_key) -> None:
    """Verifies that the factory builds correct strategy objects based on keys.

    Args:
        mock_key: Mocked key retrieval getter.
    """
    # Test fallback factory when no key exists
    mock_key.return_value = ""
    service = LLMServiceFactory.get_service()
    assert isinstance(service, HeuristicLLMService)

    # Test live factory when key is present
    mock_key.return_value = "dummy-key"
    service_live = LLMServiceFactory.get_service()
    assert isinstance(service_live, GeminiLLMService)


def test_heuristic_llm_strategy_incident() -> None:
    """Verifies that heuristic incident prompts are classified correctly."""
    service = HeuristicLLMService()
    prompt = "Analyze this incident: 'A fan fainted'"
    res = service.generate_response(prompt)
    parsed = json.loads(res)
    assert parsed["severity"] == "High"
    assert parsed["category"] == "Medical"


def test_heuristic_llm_strategy_navigation() -> None:
    """Verifies that heuristic RAG queries return accessibility answers."""
    service = HeuristicLLMService()
    prompt_qa = "Fan Question: Is there wheelchair access? MetLife Stadium"
    res_qa = service.generate_response(prompt_qa)
    assert "Gate" in res_qa or "Transit" in res_qa or "Puerta" in res_qa or "elevador" in res_qa


def test_heuristic_llm_strategy_sustainability() -> None:
    """Verifies that heuristic green logs produce motivated tips."""
    service = HeuristicLLMService()
    prompt_eco = "Green Actions today logged: refill_bottle, recycle_cup"
    res_eco = service.generate_response(prompt_eco)
    assert "scorecard" in res_eco


def test_heuristic_llm_strategy_default() -> None:
    """Verifies that unrecognized heuristic prompts fall back to default welcomes."""
    service = HeuristicLLMService()
    res = service.generate_response("Some unrecognized request")
    assert "Welcome" in res


@patch('stadium_ops.core.llm.get_gemini_api_key')
@patch('google.generativeai.GenerativeModel')
def test_gemini_llm_strategy_success(mock_model_class, mock_key) -> None:
    """Verifies successful live response generation from the Gemini API.

    Args:
        mock_model_class: Mocked GenerativeModel type class.
        mock_key: Mocked API key retriever.
    """
    mock_key.return_value = "dummy-key"
    service = GeminiLLMService("dummy-key")
    mock_model = mock_model_class.return_value
    mock_model.generate_content.return_value.text = "Grounded reply"
    
    res = service.generate_response("User query", system_instruction="instruction")
    assert res == "Grounded reply"
    mock_model_class.assert_called_with("gemini-1.5-flash", system_instruction="instruction")


def test_gemini_llm_strategy_error() -> None:
    """Verifies that failures inside the Gemini connection raise request errors."""
    service = GeminiLLMService("dummy-key")
    with patch('google.generativeai.GenerativeModel') as mock_model_class:
        mock_model = mock_model_class.return_value
        mock_model.generate_content.side_effect = Exception("API connection failure")
        
        with pytest.raises(LLMRequestError) as excinfo:
            service.generate_response("Test prompt")
        assert "Failed to fetch response" in str(excinfo.value)
