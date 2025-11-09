#!/usr/bin/env python3
"""
Clean up the submission.csv to extract only the final analysis text
and remove intermediate conversation steps
"""
import csv
import re


def extract_final_analysis(full_text: str) -> str:
    """
    Extract the final analysis from the agent conversation
    Keep only the substantive analysis, remove intermediate steps
    """
    # Look for the final summary section (starts with ## 📊)
    if '## 📊 **XR Retailer 2023 Sales Performance Analysis - Complete**' in full_text:
        # Extract everything from this marker onwards
        parts = full_text.split('## 📊 **XR Retailer 2023 Sales Performance Analysis - Complete**')
        if len(parts) > 1:
            return '## 📊 **XR Retailer 2023 Sales Performance Analysis - Complete**' + parts[1]

    # Fallback: return the full text
    return full_text


def clean_submission_csv(input_path: str, output_path: str):
    """Clean up the submission CSV"""
    print(f"🧹 Cleaning submission.csv...")
    print(f"  Input: {input_path}")
    print(f"  Output: {output_path}")

    rows_cleaned = 0

    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                # Clean the deliverable_text
                if row['deliverable_text']:
                    original_length = len(row['deliverable_text'])
                    row['deliverable_text'] = extract_final_analysis(row['deliverable_text'])
                    new_length = len(row['deliverable_text'])

                    if new_length < original_length:
                        rows_cleaned += 1
                        print(f"  ✅ Task {row['task_id']}: Reduced from {original_length} to {new_length} chars")

                writer.writerow(row)

    print(f"\n✨ Cleaned {rows_cleaned} rows")
    print(f"📝 Output saved to: {output_path}")


if __name__ == "__main__":
    clean_submission_csv(
        'data/gpteval/submission.csv',
        'data/gpteval/submission_cleaned.csv'
    )

    # Also create a cleaned version in the submission package
    clean_submission_csv(
        'submission_package/submission.csv',
        'submission_package/submission_cleaned.csv'
    )
