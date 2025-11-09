#!/usr/bin/env python3
"""
Test the Excel Validator on the generated GDPval output
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.excel_validator import validate_excel_file, ExcelValidator


def main():
    """Test validator on the generated output file"""

    # Path to the generated output
    output_file = "19403010-3e5c-494e-a6d3-13594e99f6af_output.xlsx"

    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        sys.exit(1)

    print("🔍 Validating Excel output file...")
    print(f"📁 File: {output_file}")
    print()

    # Run validation
    validator = ExcelValidator(verbose=True)
    report = validator.validate_file(output_file)

    # Print the report
    report.print_report(verbose=True)

    # Save report to JSON
    report_file = output_file.replace('.xlsx', '_validation_report.json')
    with open(report_file, 'w') as f:
        json.dump(report.to_dict(), f, indent=2)

    print(f"\n💾 Validation report saved to: {report_file}")

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
    sys.exit(main())
