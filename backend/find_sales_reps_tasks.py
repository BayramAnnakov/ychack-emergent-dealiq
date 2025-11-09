#!/usr/bin/env python3
"""
Find and prepare GDPval tasks for the specific occupation:
'Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products'
"""
import json
import os
from pathlib import Path


def find_sales_reps_tasks():
    """Find tasks for Sales Representatives occupation"""

    target_occupation = "Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products"

    print("="*80)
    print("🔍 FINDING SALES REPRESENTATIVES TASKS")
    print("="*80)
    print(f"\nTarget Occupation: {target_occupation}")

    # Load all sales tasks
    sales_file = "data/gdpval/dataset/sales_tasks.json"

    if not os.path.exists(sales_file):
        print(f"\n❌ File not found: {sales_file}")
        print("   Run download_gdpval.py first")
        return []

    with open(sales_file, 'r') as f:
        all_sales_tasks = json.load(f)

    print(f"\n📊 Searching through {len(all_sales_tasks)} sales-related tasks...")

    # Filter for the specific occupation
    sales_reps_tasks = []

    for item in all_sales_tasks:
        task = item['task']
        occupation = task.get('occupation', '')

        if occupation == target_occupation:
            sales_reps_tasks.append(task)

    print(f"\n✅ Found {len(sales_reps_tasks)} tasks for Sales Representatives")

    if not sales_reps_tasks:
        print("\n⚠️  No tasks found for this specific occupation")
        print("\n📋 Available occupations with 'Sales' in name:")

        # Show other sales-related occupations
        sales_occupations = set()
        for item in all_sales_tasks:
            occupation = item['task'].get('occupation', '')
            if 'sales' in occupation.lower():
                sales_occupations.add(occupation)

        for occ in sorted(sales_occupations):
            print(f"   - {occ}")

        return []

    # Save the Sales Representatives tasks
    output_dir = "data/gdpval/sales_reps"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "sales_reps_tasks.json")
    with open(output_file, 'w') as f:
        json.dump(sales_reps_tasks, f, indent=2)

    print(f"\n💾 Saved {len(sales_reps_tasks)} tasks to: {output_file}")

    # Show task details
    print("\n📋 TASK DETAILS:")
    print("="*80)

    for i, task in enumerate(sales_reps_tasks, 1):
        task_id = task.get('task_id', 'unknown')
        sector = task.get('sector', 'Unknown')
        prompt_preview = task.get('prompt', '')[:150]
        reference_files = task.get('reference_files', [])

        print(f"\nTask {i}: {task_id}")
        print(f"  Sector: {sector}")
        print(f"  Prompt: {prompt_preview}...")
        print(f"  Reference files: {len(reference_files)}")

        if reference_files:
            for rf in reference_files[:3]:
                filename = os.path.basename(rf)
                print(f"    - {filename}")

    return sales_reps_tasks


def prepare_test_task(task_index: int = 0):
    """Prepare a specific task for testing"""

    print("\n" + "="*80)
    print("🎯 PREPARING TEST TASK")
    print("="*80)

    # Load sales reps tasks
    tasks_file = "data/gdpval/sales_reps/sales_reps_tasks.json"

    if not os.path.exists(tasks_file):
        print("❌ No sales reps tasks found. Running search first...")
        tasks = find_sales_reps_tasks()
        if not tasks:
            return None
    else:
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)

    if not tasks:
        print("❌ No tasks available")
        return None

    if task_index >= len(tasks):
        print(f"❌ Task index {task_index} out of range (have {len(tasks)} tasks)")
        return None

    task = tasks[task_index]
    task_id = task.get('task_id', 'unknown')

    print(f"\n📋 Selected Task: {task_id}")
    print(f"   Occupation: {task.get('occupation', 'Unknown')}")
    print(f"   Sector: {task.get('sector', 'Unknown')}")

    # Save as the active test task
    test_file = "data/gdpval/sales_reps/active_test_task.json"
    with open(test_file, 'w') as f:
        json.dump(task, f, indent=2)

    print(f"\n✅ Task prepared for testing: {test_file}")

    # Show full prompt
    print("\n📝 FULL PROMPT:")
    print("-"*80)
    print(task.get('prompt', 'No prompt'))

    print("\n📎 REFERENCE FILES:")
    print("-"*80)
    for rf in task.get('reference_files', []):
        print(f"  - {rf}")

    print("\n🔗 DOWNLOAD URLs:")
    print("-"*80)
    for url in task.get('reference_file_urls', [])[:3]:
        print(f"  - {url[:100]}...")

    return task


if __name__ == "__main__":
    # Find all Sales Representatives tasks
    tasks = find_sales_reps_tasks()

    if tasks:
        # Prepare the first task for testing
        prepare_test_task(0)