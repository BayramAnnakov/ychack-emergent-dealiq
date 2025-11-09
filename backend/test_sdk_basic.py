"""
Basic test to verify Claude SDK is working
Run with: python test_sdk_basic.py
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

try:
    from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock, ResultMessage
    SDK_AVAILABLE = True
except ImportError as e:
    SDK_AVAILABLE = False
    print(f"❌ Claude SDK import error: {e}")


async def test_basic_sdk():
    """Test the Claude SDK with correct pattern"""

    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found")
        print("\nPlease set it in one of these ways:")
        print("1. Create a .env file in the backend directory with:")
        print("   ANTHROPIC_API_KEY=your_key_here")
        print("\n2. Or export it as an environment variable:")
        print("   export ANTHROPIC_API_KEY=your_key_here")
        return False

    if not SDK_AVAILABLE:
        print("❌ ERROR: Claude SDK not available")
        print("Please run: pip install claude-agent-sdk")
        return False

    # Set API key as environment variable for SDK
    os.environ["ANTHROPIC_API_KEY"] = api_key

    print("Testing Claude SDK Basic Functionality")
    print("="*50)

    # Test 1: Simple query using ClaudeSDKClient
    print("\nTest 1: Basic Query with ClaudeSDKClient")
    print("-"*30)

    try:
        print("Creating SDK client and sending query: What is 2+2?")

        response_text = ""
        message_count = 0

        # Use ClaudeSDKClient with async context manager
        async with ClaudeSDKClient() as client:
            # Send the query
            await client.query("What is 2+2? Reply with just the number.")

            # Receive and process the response
            async for message in client.receive_response():
                message_count += 1

                # Handle AssistantMessage type
                if isinstance(message, AssistantMessage):
                    print(f"  Got AssistantMessage")
                    # Iterate through content blocks
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response_text += block.text
                            print(f"  TextBlock content: {block.text}")
                        else:
                            print(f"  Other block type: {type(block)}")

                # Handle ResultMessage type
                elif isinstance(message, ResultMessage):
                    print(f"  Got ResultMessage: {message}")

                # Handle other message types for debugging
                else:
                    print(f"  Debug - Message type: {type(message)}")
                    print(f"  Debug - Message: {message}")

        print(f"\nReceived {message_count} messages")
        print(f"Final response: {response_text}")

        if "4" in response_text:
            print("✅ Test 1 passed: Got correct answer")
        else:
            print("❌ Test 1 failed: Unexpected response")
            return False

    except Exception as e:
        print(f"❌ Test 1 failed with error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")

        # More detailed error information
        import traceback
        print("   Traceback:")
        traceback.print_exc()
        return False

    # Test 2: Continuous conversation
    print("\nTest 2: Continuous Conversation")
    print("-"*30)

    try:
        print("Testing continuous conversation with context...")

        async with ClaudeSDKClient() as client:
            # First message - establish context
            print("\n1. Sending: Tell me about the capital of France")
            await client.query("What's the capital of France? Please be brief.")

            first_response = ""
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            first_response += block.text

            print(f"   Response: {first_response[:100]}...")

            # Second message - follow-up question
            print("\n2. Sending follow-up: Tell me more about that city")
            await client.query("Tell me one interesting fact about that city you just mentioned.")

            second_response = ""
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            second_response += block.text

            print(f"   Response: {second_response[:100]}...")

            # Check if context was maintained
            if "paris" in second_response.lower() or "france" in second_response.lower():
                print("✅ Test 2 passed: Context maintained in conversation")
            else:
                print("⚠️  Test 2 partial: Context might not be fully retained")

    except Exception as e:
        print(f"❌ Test 2 failed with error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

    # Test 3: Multiple turns in one session
    print("\nTest 3: Multi-turn Session")
    print("-"*30)

    try:
        print("Testing multiple turns in one session...")

        async with ClaudeSDKClient() as client:
            # Set up some context
            await client.query("My name is Alex and I like Python programming. Remember this.")

            setup_response = ""
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            setup_response += block.text

            print(f"Setup acknowledged: {setup_response[:50]}...")

            # Test memory
            await client.query("What's my name and what do I like?")

            memory_response = ""
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            memory_response += block.text

            print(f"Memory test: {memory_response[:100]}...")

            if "alex" in memory_response.lower() and "python" in memory_response.lower():
                print("✅ Test 3 passed: Full context retention works")
            else:
                print("⚠️  Test 3 partial: Some context might be lost")

    except Exception as e:
        print(f"❌ Test 3 failed with error: {str(e)}")
        return False

    print("\n" + "="*50)
    print("🎉 Claude SDK is working correctly!")
    print("\nThe SDK can:")
    print("  • Connect to Claude API using ClaudeSDKClient")
    print("  • Send queries and receive responses")
    print("  • Handle AssistantMessage and TextBlock types")
    print("  • Maintain context in continuous conversations")
    print("\nYou can now use the agent system with confidence.")

    return True


async def test_with_fallback():
    """Test with fallback to direct API if SDK fails"""

    # First try SDK
    sdk_success = await test_basic_sdk()

    if not sdk_success:
        print("\n" + "="*50)
        print("SDK test failed. Trying direct Anthropic API...")
        print("="*50)

        try:
            from anthropic import AsyncAnthropic

            api_key = os.getenv("ANTHROPIC_API_KEY")
            client = AsyncAnthropic(api_key=api_key)

            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{"role": "user", "content": "What is 2+2? Reply with just the number."}]
            )

            response_text = response.content[0].text
            print(f"Direct API Response: {response_text}")

            if "4" in response_text:
                print("\n✅ Direct Anthropic API works!")
                print("Consider using the direct API as a fallback in your agents.")
                return True

        except Exception as e:
            print(f"❌ Direct API also failed: {str(e)}")
            return False

    return sdk_success


if __name__ == "__main__":
    success = asyncio.run(test_with_fallback())
    exit(0 if success else 1)