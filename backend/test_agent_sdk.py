"""
Simple test suite to verify Claude SDK integration and continuous conversations
Run with: python test_agent_sdk.py
"""
import asyncio
import os
from typing import Dict, Any
import pandas as pd

# Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.base import ContinuousAgent
from app.agents.data_ingestion import DataIngestionAgent
from app.core.config import settings


class TestAgent(ContinuousAgent):
    """Simple test agent for verifying SDK functionality"""

    def __init__(self):
        super().__init__(
            name="TestAgent",
            description="Test agent for SDK verification"
        )


async def test_basic_conversation():
    """Test 1: Basic single query with ClaudeSDKClient"""
    print("\n" + "="*50)
    print("TEST 1: Basic Single Query")
    print("="*50)

    agent = TestAgent()

    # Test single query without context manager
    response = await agent.query_single(
        "What is 2+2? Give me just the number.",
        context={"test": "basic_math"}
    )

    print(f"Query: What is 2+2?")
    print(f"Response: {response}")

    # Verify we got a response
    assert response and len(response) > 0, "No response received"
    assert "4" in response or "four" in response.lower(), "Incorrect answer"
    print("✅ Basic query test passed")

    return True


async def test_continuous_conversation():
    """Test 2: Continuous conversation with context retention"""
    print("\n" + "="*50)
    print("TEST 2: Continuous Conversation")
    print("="*50)

    agent = TestAgent()

    async with agent:
        # First query
        print("\nFirst query: Remember the number 42")
        response1 = await agent.follow_up("Remember the number 42. Just acknowledge you'll remember it.")
        print(f"Response 1: {response1}")

        # Second query - should remember context
        print("\nSecond query: What number did I ask you to remember?")
        response2 = await agent.follow_up("What number did I ask you to remember?")
        print(f"Response 2: {response2}")

        # Verify context retention
        assert "42" in response2, "Agent didn't remember the number from previous message"
        print("✅ Continuous conversation test passed")

        # Get conversation history
        history = agent.get_conversation_history()
        print(f"\nConversation history length: {len(history)} exchanges")

    return True


async def test_data_analysis_agent():
    """Test 3: DataIngestionAgent with real data analysis"""
    print("\n" + "="*50)
    print("TEST 3: Data Analysis Agent")
    print("="*50)

    # Create sample data
    sample_data = pd.DataFrame({
        'deal_id': ['D001', 'D002', 'D003'],
        'amount': [10000, 25000, 15000],
        'stage': ['Proposal', 'Negotiation', 'Closed Won'],
        'owner': ['Alice', 'Bob', 'Alice']
    })

    agent = DataIngestionAgent()

    async with agent:
        # Process data
        print("\nAnalyzing sample sales data...")
        result = await agent.process(
            sample_data,
            context={"query": "Analyze this sales data"}
        )

        print(f"\nAnalysis Status: {result.get('status')}")

        # Check for AI-generated insights
        insights = result.get('insights', [])
        print(f"Number of insights generated: {len(insights)}")

        if insights:
            print("\nFirst insight:")
            print(f"- {insights[0].get('description', 'No description')[:200]}")

        # Verify we got meaningful analysis
        assert result.get('status') == 'success', "Processing failed"
        assert len(insights) > 0, "No insights generated"
        assert result.get('schema'), "No schema detected"

        print("✅ Data analysis agent test passed")

    return True


async def test_multi_turn_analysis():
    """Test 4: Multi-turn conversation with follow-up questions"""
    print("\n" + "="*50)
    print("TEST 4: Multi-turn Analysis")
    print("="*50)

    agent = TestAgent()

    async with agent:
        # Initial context
        print("\nSetting context about a sales team...")
        await agent.follow_up(
            "I have a sales team with 3 reps: Alice, Bob, and Charlie. "
            "Alice closed $100K, Bob closed $75K, and Charlie closed $50K last quarter."
        )

        # Ask analysis question
        print("\nAsking: Who was the top performer?")
        response1 = await agent.follow_up("Who was the top performer?")
        print(f"Response: {response1}")
        assert "Alice" in response1 or "100" in response1, "Didn't identify Alice as top performer"

        # Ask follow-up calculation
        print("\nAsking: What was the total revenue?")
        response2 = await agent.follow_up("What was the total revenue from all three reps?")
        print(f"Response: {response2}")
        assert "225" in response2 or "225K" in response2 or "225,000" in response2, "Incorrect total calculation"

        # Ask comparative question
        print("\nAsking: What's the performance gap?")
        response3 = await agent.follow_up("What's the difference between the top and bottom performer?")
        print(f"Response: {response3}")
        assert "50" in response3 or "50K" in response3 or "50,000" in response3, "Incorrect difference calculation"

        print("✅ Multi-turn analysis test passed")

    return True


async def test_streaming_responses():
    """Test 5: Streaming responses from agent"""
    print("\n" + "="*50)
    print("TEST 5: Streaming Responses")
    print("="*50)

    agent = TestAgent()

    async with agent:
        print("\nStreaming query: Explain sales pipeline in 3 sentences")

        response_parts = []
        async for message in agent.query_continuous(
            "Explain what a sales pipeline is in exactly 3 sentences."
        ):
            if message.get("type") == "assistant":
                content = message.get("content", "")
                if content:
                    response_parts.append(content)
                    print(f"Received: {content[:50]}...")

        full_response = "".join(response_parts)
        print(f"\nFull response length: {len(full_response)} characters")

        # Verify we got a meaningful response
        assert len(full_response) > 50, "Response too short"
        assert any(word in full_response.lower() for word in ["sales", "pipeline", "process", "stage"]), \
            "Response doesn't seem to be about sales pipeline"

        print("✅ Streaming test passed")

    return True


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("CLAUDE SDK INTEGRATION TEST SUITE")
    print("="*60)

    # Check for API key
    if not settings.ANTHROPIC_API_KEY:
        print("\n❌ ERROR: ANTHROPIC_API_KEY not set in environment")
        print("Please set your API key in backend/.env file")
        return False

    print(f"\n✓ API Key configured")
    print(f"✓ Using model: {settings.CLAUDE_MODEL}")

    tests = [
        ("Basic Conversation", test_basic_conversation),
        ("Continuous Conversation", test_continuous_conversation),
        ("Data Analysis Agent", test_data_analysis_agent),
        ("Multi-turn Analysis", test_multi_turn_analysis),
        ("Streaming Responses", test_streaming_responses),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} failed: {str(e)}")
            failed += 1

    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 All tests passed! The Claude SDK integration is working correctly.")
        print("The agents can:")
        print("  • Make single queries to Claude")
        print("  • Maintain continuous conversations with context")
        print("  • Process and analyze data with AI")
        print("  • Handle multi-turn interactions")
        print("  • Stream responses in real-time")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please check the errors above.")

    return failed == 0


if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)