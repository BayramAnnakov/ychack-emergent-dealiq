#!/usr/bin/env python3
"""
Test the AI-powered Excel Validator Agent
"""
import os
import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.excel_validator_agent import validate_excel_with_ai


async def main():
    """Test AI validator on the generated output file"""

    # Path to the generated output
    output_file = "19403010-3e5c-494e-a6d3-13594e99f6af_output.xlsx"

    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return 1

    print("🔍 Validating Excel output file with AI analysis...")
    print(f"📁 File: {output_file}")
    print()

    # Run AI-powered validation
    report = await validate_excel_with_ai(output_file, verbose=True)

    # Save report to JSON
    report_file = output_file.replace('.xlsx', '_ai_validation_report.json')
    with open(report_file, 'w') as f:
        json.dump(report.to_dict(), f, indent=2)

    print(f"\n💾 AI validation report saved to: {report_file}")

    # Return exit code based on validation result
    if report.critical_issues > 0:
        print(f"\n❌ VALIDATION FAILED: {report.critical_issues} critical issues found")
        return 1
    elif report.warnings > 0:
        print(f"\n⚠️  VALIDATION PASSED WITH WARNINGS: {report.warnings} warnings found")
        return 0
    else:
        print(f"\n✅ VALIDATION PASSED: No issues found")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
