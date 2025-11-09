"""
Real CRM Data Analysis Test
Tests the orchestrator with actual sample_crm_data.csv
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import json

# Fix PATH for Node.js
if '/usr/local/bin' not in os.environ['PATH']:
    os.environ['PATH'] = '/usr/local/bin:' + os.environ['PATH']

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

from app.agents.orchestrator_streaming import StreamingOrchestrator


async def analyze_real_crm_data():
    """Test with real CRM data"""
    print("="*70)
    print("REAL CRM DATA ANALYSIS TEST")
    print("="*70)

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found")
        sys.exit(1)

    print(f"✅ API Key: {api_key[:20]}...\n")

    # Load real CRM data
    csv_path = Path(__file__).parent.parent / 'data' / 'sample_crm_data.csv'
    print(f"📂 Loading CRM data from: {csv_path}")

    if not csv_path.exists():
        print(f"❌ ERROR: File not found: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} deals\n")

    # Convert to dict for analysis
    data = {
        "deals": df.to_dict('records'),
        "summary": {
            "total_deals": len(df),
            "total_pipeline_value": df['amount'].sum(),
            "avg_deal_size": df['amount'].mean(),
            "stages": df['stage'].value_counts().to_dict(),
            "owners": df['owner'].value_counts().to_dict()
        }
    }

    print(f"📊 Data Summary:")
    print(f"   Total Deals: {data['summary']['total_deals']}")
    print(f"   Total Pipeline: ${data['summary']['total_pipeline_value']:,.0f}")
    print(f"   Avg Deal Size: ${data['summary']['avg_deal_size']:,.0f}")
    print(f"   Stages: {list(data['summary']['stages'].keys())}")
    print(f"   Sales Reps: {list(data['summary']['owners'].keys())}")

    # Create orchestrator
    orchestrator = StreamingOrchestrator(verbose=True)

    # Test different analysis types
    analysis_types = [
        ("general", "General pipeline analysis"),
        ("pipeline_analysis", "Detailed pipeline health analysis"),
        ("deal_scoring", "Deal prioritization and scoring"),
    ]

    for analysis_type, description in analysis_types:
        print(f"\n{'='*70}")
        print(f"🔍 Analysis Type: {analysis_type}")
        print(f"📋 Description: {description}")
        print(f"{'='*70}\n")

        results = {
            "analysis_type": analysis_type,
            "content": "",
            "metrics": {}
        }

        start_time = asyncio.get_event_loop().time()

        # Stream analysis
        async for update in orchestrator.analyze_streaming(data, analysis_type):
            if update["type"] == "assistant":
                results["content"] += update["content"]
            elif update["type"] == "result":
                results["metrics"] = {
                    "duration_ms": update["duration_ms"],
                    "cost_usd": update["cost_usd"],
                    "is_error": update["is_error"]
                }

        elapsed = asyncio.get_event_loop().time() - start_time

        # Show results
        print(f"\n{'='*70}")
        print(f"✅ ANALYSIS COMPLETE")
        print(f"{'='*70}")
        print(f"⏱️  Time: {elapsed:.1f}s")
        print(f"💰 Cost: ${results['metrics'].get('cost_usd', 0):.4f}")
        print(f"📝 Content length: {len(results['content'])} chars")
        print(f"\n--- First 500 characters of analysis ---")
        print(results['content'][:500])
        print("...\n")

        # Ask if user wants to continue
        if analysis_type != analysis_types[-1][0]:
            print("Press Enter to continue to next analysis type, or Ctrl+C to stop...")
            try:
                input()
            except KeyboardInterrupt:
                print("\n\n⚠️  Stopped by user")
                break

    print(f"\n{'='*70}")
    print("🎉 ALL TESTS COMPLETE!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    try:
        asyncio.run(analyze_real_crm_data())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
