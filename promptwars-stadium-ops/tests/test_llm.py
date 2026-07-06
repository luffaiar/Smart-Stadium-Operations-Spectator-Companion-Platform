import os
from unittest.mock import patch, MagicMock
from stadium_ops.core.config import get_gemini_api_key
from stadium_ops.core.llm import generate_llm_response

def test_get_gemini_api_key_from_env():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-env-key"}):
        assert get_gemini_api_key() == "test-env-key"


def test_get_gemini_api_key_from_secrets():
    # Clear environment variable to ensure it checks secrets
    with patch.dict(os.environ, {}, clear=True):
        # Mock streamlit secrets and file existence check
        mock_secrets = {"GEMINI_API_KEY": "test-secrets-key"}
        with patch('streamlit.secrets', mock_secrets), \
             patch('os.path.exists', return_value=True):
            assert get_gemini_api_key() == "test-secrets-key"


def test_get_gemini_api_key_missing():
    with patch.dict(os.environ, {}, clear=True):
        with patch('streamlit.secrets', {}):
            assert get_gemini_api_key() == ""


@patch('stadium_ops.core.llm.get_gemini_api_key')
def test_generate_llm_response_no_key(mock_key):
    mock_key.return_value = ""
    # Should exit early and return empty string
    res = generate_llm_response("Hello")
    assert res == ""


@patch('stadium_ops.core.llm.get_gemini_api_key')
@patch('google.generativeai.GenerativeModel')
def test_generate_llm_response_success(mock_model_class, mock_key):
    mock_key.return_value = "dummy-key"
    mock_model = mock_model_class.return_value
    mock_model.generate_content.return_value.text = "Hello there!"
    
    res = generate_llm_response("Test prompt", system_instruction="system inst")
    assert res == "Hello there!"
    mock_model_class.assert_called_with("gemini-1.5-flash", system_instruction="system inst")


@patch('stadium_ops.core.llm.get_gemini_api_key')
@patch('google.generativeai.GenerativeModel')
def test_generate_llm_response_error(mock_model_class, mock_key):
    mock_key.return_value = "dummy-key"
    mock_model = mock_model_class.return_value
    mock_model.generate_content.side_effect = Exception("API connection failure")
    
    res = generate_llm_response("Test prompt")
    assert res == ""
