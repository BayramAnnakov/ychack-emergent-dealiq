#!/usr/bin/env python3
"""
Prepare GDPval submission package for HuggingFace dataset upload

This script:
1. Validates the submission.csv format
2. Verifies all deliverable files exist
3. Creates a submission package ready for HuggingFace upload
4. Generates submission instructions
"""
import os
import csv
import json
import shutil
from pathlib import Path
from datetime import datetime


def validate_submission_csv(csv_path: str) -> dict:
    """
    Validate the submission.csv file format and content

    Returns:
        dict with validation results
    """
    print("🔍 Validating submission.csv...")

    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'stats': {}
    }

    if not os.path.exists(csv_path):
        results['valid'] = False
        results['errors'].append(f"File not found: {csv_path}")
        return results

    # Read and parse CSV
    tasks = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        # Check required columns
        required_columns = ['task_id', 'deliverable_text', 'deliverable_files', 'status']
        missing_columns = [col for col in required_columns if col not in reader.fieldnames]

        if missing_columns:
            results['valid'] = False
            results['errors'].append(f"Missing required columns: {missing_columns}")
            return results

        for row_idx, row in enumerate(reader, start=2):
            tasks.append(row)

            # Validate task_id
            if not row['task_id']:
                results['errors'].append(f"Row {row_idx}: Missing task_id")
                results['valid'] = False

            # Validate deliverable_text
            if not row['deliverable_text']:
                results['warnings'].append(f"Row {row_idx}: Empty deliverable_text")
            elif len(row['deliverable_text']) < 100:
                results['warnings'].append(f"Row {row_idx}: deliverable_text seems too short ({len(row['deliverable_text'])} chars)")

            # Validate deliverable_files
            if not row['deliverable_files']:
                results['errors'].append(f"Row {row_idx}: Missing deliverable_files")
                results['valid'] = False
            else:
                # Parse the file list (should be a list in the CSV)
                try:
                    # Handle both string and list formats
                    files_str = row['deliverable_files']
                    if files_str.startswith('[') and files_str.endswith(']'):
                        # It's formatted as a list string
                        import ast
                        files_list = ast.literal_eval(files_str)
                    else:
                        files_list = [files_str]

                    # Check if files exist
                    for file_path in files_list:
                        # Convert to actual path (remove 'deliverable_files/' prefix if needed)
                        actual_path = file_path.replace('deliverable_files/', 'data/gdpval/deliverable_files/')
                        if not os.path.exists(actual_path):
                            results['errors'].append(f"Row {row_idx}: File not found: {actual_path}")
                            results['valid'] = False
                        else:
                            # Check file size
                            file_size = os.path.getsize(actual_path)
                            if file_size == 0:
                                results['errors'].append(f"Row {row_idx}: File is empty: {actual_path}")
                                results['valid'] = False
                            elif file_size < 1024:
                                results['warnings'].append(f"Row {row_idx}: File seems small ({file_size} bytes): {actual_path}")

                except Exception as e:
                    results['errors'].append(f"Row {row_idx}: Error parsing deliverable_files: {str(e)}")
                    results['valid'] = False

            # Validate status
            if row['status'] not in ['completed', 'pending', 'failed']:
                results['warnings'].append(f"Row {row_idx}: Unusual status: {row['status']}")

    # Calculate stats
    results['stats'] = {
        'total_tasks': len(tasks),
        'completed': sum(1 for t in tasks if t['status'] == 'completed'),
        'pending': sum(1 for t in tasks if t['status'] == 'pending'),
        'failed': sum(1 for t in tasks if t['status'] == 'failed'),
    }

    return results


def create_submission_package(output_dir: str = "submission_package"):
    """
    Create a submission package ready for HuggingFace upload
    """
    print(f"\n📦 Creating submission package in {output_dir}/...")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Copy submission.csv
    shutil.copy('data/gpteval/submission.csv', f'{output_dir}/submission.csv')
    print(f"  ✅ Copied submission.csv")

    # Copy deliverable files
    deliverable_dir = f'{output_dir}/deliverable_files'
    os.makedirs(deliverable_dir, exist_ok=True)

    # Copy all files from data/gdpval/deliverable_files/
    src_dir = 'data/gdpval/deliverable_files'
    if os.path.exists(src_dir):
        for file in os.listdir(src_dir):
            if file.endswith('.xlsx'):
                shutil.copy(f'{src_dir}/{file}', f'{deliverable_dir}/{file}')
                print(f"  ✅ Copied {file}")

    # Create README
    readme_content = f"""# GDPval Submission - DealIQ

## Submission Information

- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Model**: dealiq-claude-sonnet-4-5-20250929
- **System**: DealIQ AI-powered CRM intelligence using Claude Agent SDK

## Files

- `submission.csv`: Main submission file with task results
- `deliverable_files/`: Excel output files for each task

## Model Details

- **Base Model**: claude-sonnet-4-5-20250929
- **SDK**: Claude Agent SDK (Python)
- **Skills**: xlsx Skill from Anthropic (enables Excel formula generation)
- **Orchestrator**: BenchmarkOrchestrator with streaming capabilities

## Key Features

1. **Formula-based Calculations**: All Excel outputs use formulas, not hardcoded values
2. **Professional Formatting**: Executive-ready reports with proper styling
3. **Comprehensive Analysis**: Detailed insights and recommendations for each task
4. **Sales Domain Expertise**: Specialized prompting for sales analytics

## Submission Instructions

1. Upload this entire folder structure to HuggingFace
2. Ensure the dataset is public
3. Submit to: https://evals.openai.com/gdpval/grading
4. Use dataset URL: https://huggingface.co/datasets/YOUR_USERNAME/gdpval-dealiq-submission

## Contact

For questions about this submission, please contact the team.
"""

    with open(f'{output_dir}/README.md', 'w') as f:
        f.write(readme_content)
    print(f"  ✅ Created README.md")

    return output_dir


def generate_submission_report(validation_results: dict, package_dir: str):
    """Generate a submission report"""
    print(f"\n{'='*80}")
    print(f"📋 SUBMISSION VALIDATION REPORT")
    print(f"{'='*80}")

    if validation_results['valid']:
        print(f"Status: ✅ VALID - Ready for submission")
    else:
        print(f"Status: ❌ INVALID - Please fix errors before submitting")

    print(f"\n📊 Statistics:")
    for key, value in validation_results['stats'].items():
        print(f"  {key}: {value}")

    if validation_results['errors']:
        print(f"\n🔴 ERRORS ({len(validation_results['errors'])}):")
        for error in validation_results['errors']:
            print(f"  - {error}")

    if validation_results['warnings']:
        print(f"\n🟡 WARNINGS ({len(validation_results['warnings'])}):")
        for warning in validation_results['warnings']:
            print(f"  - {warning}")

    if validation_results['valid']:
        print(f"\n📦 Submission Package:")
        print(f"  Location: {package_dir}/")
        print(f"\n📤 Next Steps:")
        print(f"  1. Review the package contents in {package_dir}/")
        print(f"  2. Go to https://huggingface.co/spaces/huggingface/repo_duplicator")
        print(f"  3. Duplicate openai/gdpval to your HuggingFace account")
        print(f"  4. Upload the contents of {package_dir}/ to your duplicated dataset")
        print(f"  5. Make the dataset public")
        print(f"  6. Submit at https://evals.openai.com/gdpval/grading")

    print(f"\n{'='*80}")


def main():
    """Main submission preparation workflow"""
    print("🚀 GDPval Submission Preparation Tool")
    print("="*80)

    # Change to backend directory
    os.chdir('/Users/bayramannakov/GH/ychack-emergent-dealiq/backend')

    # Validate submission.csv
    validation_results = validate_submission_csv('data/gpteval/submission.csv')

    # Create submission package if valid
    package_dir = None
    if validation_results['valid'] or (validation_results['errors'] and not any('File not found' in e for e in validation_results['errors'])):
        package_dir = create_submission_package('submission_package')

    # Generate report
    generate_submission_report(validation_results, package_dir or 'submission_package')

    # Save validation results to JSON
    with open('submission_validation.json', 'w') as f:
        json.dump(validation_results, f, indent=2)
    print(f"\n💾 Validation results saved to submission_validation.json")

    return 0 if validation_results['valid'] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
