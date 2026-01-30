import pytest
from unittest.mock import AsyncMock, patch
from src.infrastructure.llm.openai_client import OpenAIClient
from src.core.schemas.models import AgentState, Action

@pytest.mark.asyncio
async def test_ask_returns_valid_action():
    # Mock de la respuesta de OpenAI
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(message=AsyncMock(content='{"type": "skill", "name": "web-research", "args": {"q": "test"}, "reason": "test reasoning"}'))
    ]
    
    with patch("src.infrastructure.llm.openai_client.AsyncOpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
        
        client = OpenAIClient()
        state = AgentState(session_id="test")
        action = await client.ask(state)
        
        assert isinstance(action, Action)
        assert action.type == "skill"
        assert action.name == "web-research"
        assert action.args["q"] == "test"

@pytest.mark.asyncio
async def test_ask_error_fallback():
    with patch("src.infrastructure.llm.openai_client.AsyncOpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        client = OpenAIClient()
        state = AgentState(session_id="test")
        action = await client.ask(state)
        
        assert action.type == "respond"
        assert "Error en el Router LLM" in action.args["response"]
        assert action.stop is True
