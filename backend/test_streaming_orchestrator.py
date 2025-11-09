#!/usr/bin/env python3
"""
Test the StreamingOrchestrator (that works with frontend) to compare with BenchmarkOrchestrator
"""
import asyncio
from app.agents.orchestrator_streaming import StreamingOrchestrator


async def test_working_orchestrator():
    """Test the working StreamingOrchestrator with a simple file"""
    print("="*80)
    print("Testing WORKING StreamingOrchestrator")
    print("="*80)

    # Create orchestrator
    orchestrator = StreamingOrchestrator(verbose=True)

    # Use an existing CSV file
    file_path = "data/uploads/09ae3726-4b37-413c-9894-bcc5d7da283e.csv"

    print(f"\n📂 Testing with file: {file_path}")
    print("🚀 Starting analysis...\n")

    # Try to analyze the file
    try:
        message_count = 0
        async for update in orchestrator.analyze_file_streaming(
            file_path=file_path,
            analysis_type="pipeline_analysis",
            description="Quick test to verify SDK works"
        ):
            message_count += 1

            if update.get("type") == "assistant":
                content = update.get("content", "")
                if content:
                    print(f"✅ Message {message_count}: Got {len(content)} chars of content")

            if update.get("type") == "result":
                print(f"\n✅ COMPLETED!")
                print(f"   Duration: {update.get('duration_ms', 0)}ms")
                print(f"   Cost: ${update.get('cost_usd', 0):.4f}")
                print(f"   Turns: {update.get('num_turns', 0)}")
                break

        print(f"\n✅ StreamingOrchestrator works! Received {message_count} messages")
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Testing if StreamingOrchestrator works...\n")
    result = asyncio.run(test_working_orchestrator())

    if result:
        print("\n" + "="*80)
        print("✅ StreamingOrchestrator WORKS - SDK connection is OK")
        print("="*80)
        print("\nNow we can compare to see what's different in BenchmarkOrchestrator")
    else:
        print("\n" + "="*80)
        print("❌ StreamingOrchestrator ALSO FAILS - SDK issue is system-wide")
        print("="*80)
