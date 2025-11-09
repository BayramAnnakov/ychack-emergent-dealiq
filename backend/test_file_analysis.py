"""
Test file-based CRM analysis - Claude reads CSV directly using Read tool
This is the SIMPLEST way to analyze CRM data with Claude Agent SDK
"""
import os
import asyncio
from app.agents.orchestrator_streaming import StreamingOrchestrator
from app.core.config import settings

# Ensure Node.js is in PATH for Claude SDK
if '/usr/local/bin' not in os.environ['PATH']:
    os.environ['PATH'] = '/usr/local/bin:' + os.environ['PATH']


async def test_file_based_analysis():
    """Test analyzing CSV file directly - Claude uses Read tool"""

    print("="*70)
    print("FILE-BASED CRM ANALYSIS TEST")
    print("Claude will use the Read tool to load and analyze the CSV")
    print("="*70)

    # Ensure API key
    if not settings.ANTHROPIC_API_KEY:
        print("❌ ERROR: ANTHROPIC_API_KEY not set")
        return

    print(f"✅ API Key: {settings.ANTHROPIC_API_KEY[:15]}...")

    # Create orchestrator
    orchestrator = StreamingOrchestrator(verbose=True)

    # Path to CSV file (relative to project root, which is set as cwd)
    csv_file = "data/sample_crm_data.csv"

    print(f"\n📂 CSV File: {csv_file}")
    print(f"📊 Claude will read this file using the Read tool")

    # Run file-based analysis
    print("\n" + "="*70)
    print("🚀 STARTING FILE-BASED ANALYSIS")
    print("="*70)

    start_time = asyncio.get_event_loop().time()
    full_content = ""

    async for update in orchestrator.analyze_file_streaming(
        file_path=csv_file,
        analysis_type="pipeline_analysis",
        description="Analyze sales pipeline health and identify opportunities"
    ):
        if update["type"] == "assistant":
            full_content += update["content"]
        elif update["type"] == "result":
            elapsed = asyncio.get_event_loop().time() - start_time

            print("\n" + "="*70)
            print("✅ ANALYSIS COMPLETE")
            print("="*70)
            print(f"⏱️  Time: {elapsed:.1f}s")
            print(f"💰 Cost: ${update['cost_usd']:.4f}")
            print(f"📝 Content length: {len(full_content)} chars")
            print(f"🔄 Turns: {update.get('num_turns', 'N/A')}")

            print("\n" + "-"*70)
            print("ANALYSIS RESULT:")
            print("-"*70)
            print(full_content[:1000] + "..." if len(full_content) > 1000 else full_content)
            print("-"*70)

    print("\n✅ Test complete!")


if __name__ == "__main__":
    asyncio.run(test_file_based_analysis())
