import pytest
from app.services.ai_service import AIService

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

@pytest.mark.real_request
async def test_ai_service_default_model():
    """
    Tests the AIService with the default model specified in ai_config.json.
    This is an integration test and makes a real API call.
    """
    try:
        # Initialize with default model
        ai_service = AIService()
        
        prompt = "Hello, world! Give me a short, two-sentence reply."
        
        print(f"\n[Default Model Test] Using model strategy: {ai_service._config.use_model}")
        print(f"Model name: {ai_service.strategy_config.model}")
        print(f"Prompt: {prompt}")

        response = await ai_service.generate_response(prompt)

        print(f"Response: {response}")

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0

    except Exception as e:
        pytest.fail(f"AIService with default model failed with an exception: {e}")

@pytest.mark.real_request
async def test_ai_service_specific_model():
    """
    Tests the AIService with a specifically chosen model ('gpt-4-1').
    This is an integration test and makes a real API call.
    """
    try:
        strategy_key = "gpt-4-1"
        # Initialize with a specific model strategy
        ai_service = AIService(strategy_key=strategy_key)

        prompt = "What is the capital of France? Answer in one word."

        print(f"\n[Specific Model Test] Using model strategy: {strategy_key}")
        print(f"Model name: {ai_service.strategy_config.model}")
        print(f"Prompt: {prompt}")

        response = await ai_service.generate_response(prompt)

        print(f"Response: {response}")

        assert response is not None
        assert isinstance(response, str)
        assert "Paris" in response

    except Exception as e:
        pytest.fail(f"AIService with specific model '{strategy_key}' failed with an exception: {e}")
