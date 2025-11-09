#!/usr/bin/env python3
"""
Test GDPval Integration End-to-End

This script:
1. Loads sales tasks from GDPval dataset
2. Executes tasks using BenchmarkOrchestrator with xlsx Skill
3. Prepares submission for HuggingFace upload
"""
import asyncio
import sys
import logging
from datetime import datetime
from app.benchmarks.gdpval.loader import load_sales_tasks
from app.benchmarks.gdpval.executor import GDPvalExecutor


def setup_logging(log_dir="data/gdpval/logs"):
    """Setup detailed logging to file"""
    import os
    os.makedirs(log_dir, exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"gdpval_execution_{timestamp}.log")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("GDPval Execution Log Started")
    logger.info(f"Log file: {log_file}")
    logger.info("="*80)

    return logger, log_file


async def test_single_task():
    """Test execution of a single GDPval task"""
    # Setup logging
    logger, log_file = setup_logging()

    print("\n" + "="*80)
    print("🧪 GDPval END-TO-END TEST - SINGLE TASK")
    print("="*80)
    print(f"📝 Detailed log: {log_file}\n")

    logger.info("Starting GDPval END-TO-END TEST - SINGLE TASK")

    # Step 1: Use the XR retailer task we already have
    print("\n📥 STEP 1: Using XR Retailer Makeup 2023 task...")
    logger.info("STEP 1: Loading XR Retailer Makeup 2023 task")

    # Load the saved Sales Representatives tasks
    import json
    import os

    tasks_file = "data/gdpval/sales_reps/sales_reps_tasks.json"
    if os.path.exists(tasks_file):
        with open(tasks_file, 'r') as f:
            sales_reps_tasks = json.load(f)

        # Use task index 2 (XR retailer task)
        xr_task_data = sales_reps_tasks[2]

        # Create GDPvalTask object
        from app.benchmarks.gdpval.loader import GDPvalTask
        first_task = GDPvalTask(
            task_id=xr_task_data['task_id'],
            description=xr_task_data['prompt'],
            reference_files=xr_task_data['reference_files'],
            expected_output_format='Excel (.xlsx)',
            additional_context={
                'sector': xr_task_data['sector'],
                'occupation': xr_task_data['occupation']
            }
        )
        print(f"\n✅ Task ID: {first_task.task_id}")
        print(f"   Sector: Wholesale Trade")
        print(f"   Role: Sales Representatives")
        print(f"   Description: XR retailer makeup sales analysis for 2023")

        logger.info(f"Task loaded: {first_task.task_id}")
        logger.info(f"  Sector: Wholesale Trade")
        logger.info(f"  Occupation: Sales Representatives")
        logger.info(f"  Description length: {len(first_task.description)} chars")
    else:
        # Fallback: load from HuggingFace
        tasks = load_sales_tasks(limit=1, verbose=True)
        if not tasks:
            print("❌ No tasks found")
            return
        first_task = tasks[0]
        print(f"\n✅ Loaded task: {first_task.task_id}")
        print(f"   Description: {first_task.description[:150]}...")

    # Step 2: Use the downloaded reference file
    print("\n📂 STEP 2: Using downloaded reference file...")
    reference_files = ["data/gdpval/reference_files/DATA_XR_MU_2023.xlsx"]

    print(f"   Using {len(reference_files)} reference file(s)")
    for rf in reference_files:
        print(f"   - {rf}")

    # Step 3: Execute task with BenchmarkOrchestrator
    print("\n🚀 STEP 3: Executing task with Claude Agent SDK + xlsx Skill...")
    print("   (This will take 30-60 seconds...)")
    logger.info("STEP 3: Starting task execution")

    executor = GDPvalExecutor(
        output_dir="data/gdpval/outputs",
        verbose=True
    )

    logger.info(f"  Output directory: data/gdpval/outputs")
    logger.info(f"  Reference files: {reference_files}")

    result = await executor.execute_task(first_task, reference_files)

    # Step 4: Check results
    print("\n📊 STEP 4: Results")
    print("="*80)
    print(f"Task ID: {result['task_id']}")
    print(f"Status: {result['status']}")
    print(f"Output file: {result.get('output_file', 'N/A')}")
    print(f"Deliverable text length: {len(result.get('deliverable_text', ''))} chars")

    logger.info("STEP 4: Execution results")
    logger.info(f"  Task ID: {result['task_id']}")
    logger.info(f"  Status: {result['status']}")
    logger.info(f"  Output file: {result.get('output_file', 'N/A')}")
    logger.info(f"  Deliverable text length: {len(result.get('deliverable_text', ''))} chars")
    logger.info(f"  Deliverable text: {result.get('deliverable_text', '')}")

    if result.get('error'):
        print(f"❌ Error: {result['error']}")
        logger.error(f"Task failed: {result['error']}")
    else:
        print("✅ Task completed successfully!")
        logger.info("Task completed successfully")

    # Step 5: Prepare submission
    print("\n📦 STEP 5: Preparing HuggingFace submission...")
    submission_path = executor.prepare_submission(
        output_csv="data/gpteval/submission.csv"
    )

    print(f"\n{'='*80}")
    print("✅ END-TO-END TEST COMPLETE!")
    print(f"{'='*80}")

    # Print summary
    summary = executor.get_summary()
    print(f"\n📈 SUMMARY:")
    print(f"   Tasks executed: {summary['total_tasks']}")
    print(f"   Completed: {summary['completed']}")
    print(f"   Errors: {summary['errors']}")
    print(f"   Success rate: {summary['success_rate']*100:.1f}%")

    print(f"\n📋 NEXT STEPS:")
    print(f"   1. Review output: data/gdpval/outputs/")
    print(f"   2. Review submission CSV: {submission_path}")
    print(f"   3. Upload to HuggingFace (see GDPVAL_INTEGRATION_PLAN.md)")
    print(f"   4. Submit at: https://evals.openai.com/gdpval/grading")

    return result


async def test_multiple_tasks(num_tasks: int = 3):
    """Test execution of multiple GDPval tasks"""
    print("\n" + "="*80)
    print(f"🧪 GDPval END-TO-END TEST - {num_tasks} TASKS")
    print("="*80)

    # Load tasks
    print(f"\n📥 Loading {num_tasks} sales tasks...")
    tasks = load_sales_tasks(limit=num_tasks, verbose=True)

    if not tasks:
        print("❌ No tasks loaded")
        return

    print(f"\n✅ Loaded {len(tasks)} tasks")

    # Create executor
    executor = GDPvalExecutor(verbose=True)

    # Execute each task
    import glob
    csv_files = glob.glob("data/uploads/*.csv")
    reference_files = csv_files[:1] if csv_files else ["data/uploads/sample_crm_data.csv"]

    for i, task in enumerate(tasks, 1):
        print(f"\n{'='*80}")
        print(f"📋 TASK {i}/{len(tasks)}: {task.task_id}")
        print(f"{'='*80}")

        result = await executor.execute_task(task, reference_files)

        print(f"\n   Status: {result['status']}")
        if result.get('output_file'):
            print(f"   ✅ Output: {result['output_file']}")
        else:
            print(f"   ⚠️  No output file")

    # Prepare submission
    print(f"\n{'='*80}")
    print("📦 PREPARING SUBMISSION")
    print(f"{'='*80}")

    submission_path = executor.prepare_submission()

    # Show summary
    summary = executor.get_summary()
    print(f"\n📈 FINAL SUMMARY:")
    print(f"   Total tasks: {summary['total_tasks']}")
    print(f"   Completed: {summary['completed']}")
    print(f"   Errors: {summary['errors']}")
    print(f"   Success rate: {summary['success_rate']*100:.1f}%")

    print(f"\n✅ Batch test complete!")
    print(f"   Submission ready: {submission_path}")


def main():
    """Main test runner"""
    import argparse

    parser = argparse.ArgumentParser(description="Test GDPval integration")
    parser.add_argument(
        "--mode",
        choices=["single", "batch"],
        default="single",
        help="Test mode: single task or batch"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Number of tasks for batch mode"
    )

    args = parser.parse_args()

    if args.mode == "single":
        asyncio.run(test_single_task())
    else:
        asyncio.run(test_multiple_tasks(args.count))


if __name__ == "__main__":
    main()
