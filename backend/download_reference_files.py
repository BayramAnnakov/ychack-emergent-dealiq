#!/usr/bin/env python3
"""
Download reference files for GDPval tasks
Downloads the actual Excel/PDF files referenced in the tasks
"""
import os
import json
import requests
from pathlib import Path
from typing import List, Dict


def download_file(url: str, destination: str, verbose: bool = True) -> bool:
    """
    Download a file from URL to destination

    Args:
        url: URL to download from
        destination: Local path to save file
        verbose: Print progress

    Returns:
        True if successful, False otherwise
    """
    try:
        if verbose:
            print(f"   📥 Downloading: {os.path.basename(destination)}")

        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        # Create directory if needed
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        # Write file
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = os.path.getsize(destination)
        if verbose:
            print(f"      ✅ Saved ({file_size:,} bytes)")

        return True

    except Exception as e:
        if verbose:
            print(f"      ❌ Error: {e}")
        return False


def download_task_references(
    task_file: str,
    output_dir: str = "data/gdpval/reference_files",
    verbose: bool = True
) -> List[str]:
    """
    Download all reference files for a single task

    Args:
        task_file: Path to task JSON file
        output_dir: Directory to save reference files
        verbose: Print progress

    Returns:
        List of local file paths
    """
    # Load task
    with open(task_file, 'r') as f:
        task = json.load(f)

    task_id = task.get('task_id', 'unknown')
    reference_urls = task.get('reference_file_urls', [])
    reference_files = task.get('reference_files', [])

    if not reference_urls:
        if verbose:
            print(f"   ⚠️  No reference files for task {task_id}")
        return []

    local_files = []

    for url, ref_path in zip(reference_urls, reference_files):
        # Extract filename
        filename = os.path.basename(ref_path)

        # Create local path (organize by task_id)
        local_path = os.path.join(output_dir, task_id, filename)

        # Download
        if download_file(url, local_path, verbose):
            local_files.append(local_path)

    return local_files


def download_all_references(
    limit: int = 5,
    verbose: bool = True
):
    """
    Download reference files for the first N tasks

    Args:
        limit: Number of tasks to process
        verbose: Print progress
    """
    print("="*80)
    print("📥 DOWNLOADING REFERENCE FILES FOR GDPVAL TASKS")
    print("="*80)

    # Find task files
    tasks_dir = "data/gdpval/dataset/tasks"
    if not os.path.exists(tasks_dir):
        print(f"❌ Tasks directory not found: {tasks_dir}")
        print("   Run download_gdpval.py first")
        return

    task_files = sorted([f for f in os.listdir(tasks_dir) if f.endswith('.json')])[:limit]

    print(f"\n📋 Processing {len(task_files)} tasks...")

    all_local_files = []

    for task_file in task_files:
        task_path = os.path.join(tasks_dir, task_file)

        # Load task to get description
        with open(task_path, 'r') as f:
            task = json.load(f)

        task_id = task.get('task_id', 'unknown')
        prompt_preview = task.get('prompt', '')[:80]

        print(f"\n📁 Task: {task_id}")
        print(f"   {prompt_preview}...")

        # Download reference files
        local_files = download_task_references(
            task_path,
            output_dir="data/gdpval/reference_files",
            verbose=verbose
        )

        all_local_files.extend(local_files)

    # Summary
    print("\n" + "="*80)
    print("📊 DOWNLOAD SUMMARY")
    print("="*80)
    print(f"✅ Downloaded {len(all_local_files)} reference files")
    print(f"✅ Saved to: data/gdpval/reference_files/")

    # Save mapping
    mapping_file = "data/gdpval/reference_files_mapping.json"
    with open(mapping_file, 'w') as f:
        json.dump({
            "files": all_local_files,
            "count": len(all_local_files)
        }, f, indent=2)

    print(f"✅ Mapping saved to: {mapping_file}")

    print("\n📋 Next Steps:")
    print("1. Review downloaded files in data/gdpval/reference_files/")
    print("2. Run test_gdpval.py to execute tasks with real data")
    print("3. Submit results to OpenAI autograder")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download GDPval reference files")
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of tasks to download files for"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Print verbose output"
    )

    args = parser.parse_args()

    # Install requests if needed
    try:
        import requests
    except ImportError:
        print("Installing requests library...")
        import subprocess
        subprocess.check_call(["pip", "install", "requests"])
        import requests

    download_all_references(
        limit=args.limit,
        verbose=args.verbose
    )