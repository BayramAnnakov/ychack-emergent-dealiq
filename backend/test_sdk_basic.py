"""
Basic test to verify Claude SDK is working
Run with: python test_sdk_basic.py
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from claude_agent_sdk import ClaudeSDKClient

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Simple test without any app dependencies
async def test_basic_sdk():
    """Test the Claude SDK directly without our agent framework"""

    # Get API key from environment (now loaded from .env)
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found")
        print("\nPlease set it in one of these ways:")
        print("1. Create a .env file in the backend directory with:")
        print("   ANTHROPIC_API_KEY=your_key_here")
        print("\n2. Or export it as an environment variable:")
        print("   export ANTHROPIC_API_KEY=your_key_here")
        return False

    print("Testing Claude SDK Basic Functionality")
    print("="*50)

    # Configure SDK options
    options = {
        "api_key": api_key,
        "model": "claude-3-5-sonnet-20241022",
        "max_turns": 1,
        "system_prompt": {
            "type": "preset",
            "preset": "claude_code",
            "append": "You are a helpful assistant. Be concise."
        }
    }

    try:
        # Test 1: Single response
        print("\nTest 1: Single Query")
        print("-"*30)

        async with ClaudeSDKClient(options) as client:
            # Send a simple query
            await client.query("What is 2+2? Reply with just the number.")

            # Get response
            response_text = ""
            async for message in client.receive_response():
                if hasattr(message, 'content'):
                    response_text += message.content
                elif isinstance(message, dict) and 'content' in message:
                    response_text += message['content']
                else:
                    response_text += str(message)

            print(f"Query: What is 2+2?")
            print(f"Response: {response_text}")

            if "4" in response_text:
                print("✅ Test 1 passed: Got correct answer")
            else:
                print("❌ Test 1 failed: Unexpected response")
                return False

        # Test 2: Continuous conversation
        print("\nTest 2: Continuous Conversation")
        print("-"*30)

        async with ClaudeSDKClient(options) as client:
            # First message
            await client.query("My favorite color is blue. Remember that.")

            response1 = ""
            async for message in client.receive_response():
                if hasattr(message, 'content'):
                    response1 += message.content
                elif isinstance(message, dict) and 'content' in message:
                    response1 += message['content']

            print(f"Message 1: Set favorite color to blue")
            print(f"Response 1: {response1[:100]}...")

            # Second message - test context retention
            await client.query("What's my favorite color?")

            response2 = ""
            async for message in client.receive_response():
                if hasattr(message, 'content'):
                    response2 += message.content
                elif isinstance(message, dict) and 'content' in message:
                    response2 += message['content']

            print(f"\nMessage 2: What's my favorite color?")
            print(f"Response 2: {response2}")

            if "blue" in response2.lower():
                print("✅ Test 2 passed: Context retained across messages")
            else:
                print("❌ Test 2 failed: Context not retained")
                return False

        print("\n" + "="*50)
        print("🎉 All tests passed! Claude SDK is working correctly.")
        print("\nThe SDK can:")
        print("  • Connect to Claude API")
        print("  • Send queries and receive responses")
        print("  • Maintain conversation context")
        print("\nYou can now use the full agent system with confidence.")

        return True

    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        print("\nPossible issues:")
        print("  • Invalid API key")
        print("  • Network connection problem")
        print("  • SDK installation issue")
        print("\nTry: pip install claude-agent-sdk")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_basic_sdk())
    exit(0 if success else 1)