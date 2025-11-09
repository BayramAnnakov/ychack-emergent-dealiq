#!/usr/bin/env python3
"""
Download and explore the GDPval dataset
This script downloads the dataset and saves sales-related tasks locally
"""
import os
import json
from datasets import load_dataset
from pathlib import Path


def download_gdpval_dataset(save_dir: str = "data/gdpval/dataset"):
    """
    Download the full GDPval dataset and save sales-related tasks

    Args:
        save_dir: Directory to save the dataset files
    """
    print("="*80)
    print("📥 DOWNLOADING GDPVAL DATASET FROM HUGGINGFACE")
    print("="*80)

    # Create directory
    os.makedirs(save_dir, exist_ok=True)

    try:
        # Load the dataset
        print("\n⏳ Loading dataset from HuggingFace...")
        print("   Dataset: openai/gdpval")
        print("   This may take a minute on first download...")

        dataset = load_dataset("openai/gdpval", split="train")

        print(f"\n✅ Dataset loaded successfully!")
        print(f"   Total tasks: {len(dataset)}")

        # Explore dataset structure
        print("\n📊 Dataset Structure:")
        if len(dataset) > 0:
            first_task = dataset[0]
            print("   Columns:")
            for key in first_task.keys():
                value_type = type(first_task[key]).__name__
                preview = str(first_task[key])[:50] if first_task[key] else "None"
                print(f"   - {key}: {value_type} (e.g., {preview}...)")

        # Filter for sales-related tasks
        print("\n🔍 Filtering for sales-related tasks...")

        sales_keywords = [
            'sales', 'crm', 'revenue', 'account', 'retailer',
            'makeup', 'cosmetics', 'customer', 'deal', 'pipeline',
            'forecast', 'quota', 'territory', 'account executive',
            'opportunity', 'lead', 'conversion', 'close rate',
            'business development', 'retail', 'commerce'
        ]

        sales_tasks = []
        for idx, task in enumerate(dataset):
            # Get task description (may be in different fields)
            description = (
                task.get('task', '') + ' ' +
                task.get('description', '') + ' ' +
                task.get('prompt', '')
            ).lower()

            # Check if any keyword matches
            if any(keyword in description for keyword in sales_keywords):
                sales_tasks.append({
                    'index': idx,
                    'task': task
                })

                # Show first few matches
                if len(sales_tasks) <= 5:
                    print(f"\n   ✓ Task {idx}: {task.get('task', task.get('description', ''))[:80]}...")

        print(f"\n📈 Found {len(sales_tasks)} sales-related tasks out of {len(dataset)} total")

        # Save sales tasks to JSON
        sales_json_path = os.path.join(save_dir, "sales_tasks.json")
        with open(sales_json_path, 'w') as f:
            json.dump(sales_tasks, f, indent=2, default=str)
        print(f"\n💾 Saved sales tasks to: {sales_json_path}")

        # Save first 10 sales tasks individually
        print("\n📁 Saving individual task files...")
        tasks_dir = os.path.join(save_dir, "tasks")
        os.makedirs(tasks_dir, exist_ok=True)

        for i, item in enumerate(sales_tasks[:10]):
            task = item['task']
            task_id = f"task_{item['index']:04d}"

            # Save task metadata
            task_file = os.path.join(tasks_dir, f"{task_id}.json")
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2, default=str)

            print(f"   💾 {task_id}: {task.get('task', '')[:60]}...")

            # Check if task has reference files
            reference_files = (
                task.get('reference_files', []) or
                task.get('files', []) or
                task.get('data_files', [])
            )

            if reference_files:
                print(f"      📎 Has {len(reference_files)} reference file(s)")
                for rf in reference_files[:3]:
                    print(f"         - {rf}")

        # Create a summary
        print("\n" + "="*80)
        print("📊 DOWNLOAD SUMMARY")
        print("="*80)
        print(f"✅ Total tasks downloaded: {len(dataset)}")
        print(f"✅ Sales-related tasks: {len(sales_tasks)}")
        print(f"✅ Saved to: {save_dir}")
        print("\n📋 Next Steps:")
        print("1. Review sales_tasks.json for all sales tasks")
        print("2. Check individual task files in tasks/ directory")
        print("3. Download reference files if URLs are provided")
        print("4. Run test_gdpval.py to execute tasks")

        return sales_tasks

    except Exception as e:
        print(f"\n❌ Error downloading dataset: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Try: pip install --upgrade datasets")
        print("3. Clear HuggingFace cache: rm -rf ~/.cache/huggingface")
        return []


def analyze_task_structure(sales_tasks):
    """
    Analyze the structure of sales tasks to understand the data format
    """
    if not sales_tasks:
        print("No tasks to analyze")
        return

    print("\n" + "="*80)
    print("🔬 ANALYZING TASK STRUCTURE")
    print("="*80)

    # Collect all unique keys across tasks
    all_keys = set()
    for item in sales_tasks:
        all_keys.update(item['task'].keys())

    print(f"\n📊 Unique fields across {len(sales_tasks)} sales tasks:")
    for key in sorted(all_keys):
        # Count how many tasks have this field
        count = sum(1 for item in sales_tasks if key in item['task'])
        percentage = (count / len(sales_tasks)) * 100
        print(f"   - {key}: {count}/{len(sales_tasks)} tasks ({percentage:.1f}%)")

    # Show example of most complete task
    print("\n📝 Example of a complete task:")
    most_complete_task = max(sales_tasks, key=lambda x: len(x['task'].keys()))
    task = most_complete_task['task']

    for key, value in task.items():
        if value:
            value_str = str(value)[:100] if len(str(value)) > 100 else str(value)
            print(f"\n   {key}:")
            print(f"      {value_str}")


if __name__ == "__main__":
    print("🚀 Starting GDPval Dataset Download")
    print("-" * 80)

    # Download dataset
    sales_tasks = download_gdpval_dataset()

    # Analyze structure
    if sales_tasks:
        analyze_task_structure(sales_tasks)

    print("\n✅ Download script complete!")