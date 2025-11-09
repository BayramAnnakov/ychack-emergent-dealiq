"""
GDPval Dataset Loader for Sales Analytics Tasks
Loads tasks from HuggingFace and filters for sales-related analyses
"""
import os
from dataclasses import dataclass
from typing import List, Dict, Optional
from datasets import load_dataset


@dataclass
class GDPvalTask:
    """Represents a single GDPval benchmark task"""
    task_id: str
    description: str
    reference_files: List[str]
    expected_output_format: str
    sections: Optional[List[str]] = None
    additional_context: Optional[Dict] = None

    def __str__(self):
        return f"Task {self.task_id}: {self.description[:100]}..."


def load_sales_tasks(limit: int = 10, verbose: bool = False) -> List[GDPvalTask]:
    """
    Load GDPval sales analytics tasks from HuggingFace
    Specifically targets: Sales Representatives, Wholesale and Manufacturing

    Args:
        limit: Maximum number of tasks to return
        verbose: Print debug information

    Returns:
        List of GDPvalTask objects for Sales Representatives
    """
    if verbose:
        print("📥 Loading GDPval dataset from HuggingFace...")

    try:
        # Load the full GDPval dataset
        dataset = load_dataset("openai/gdpval", split="train")

        if verbose:
            print(f"✅ Loaded {len(dataset)} total tasks")
            print("🔍 Filtering for Sales Representatives tasks...")

        # Target specific occupation
        target_occupation = "Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products"

        sales_tasks = []
        for idx, task in enumerate(dataset):
            # Check if task matches our target occupation
            occupation = task.get('occupation', '')

            if occupation == target_occupation:
                # Parse the task into our GDPvalTask format
                gdpval_task = _parse_task(task, idx)
                sales_tasks.append(gdpval_task)

                if verbose:
                    print(f"  ✓ Found: {gdpval_task.task_id}")
                    print(f"    Sector: {task.get('sector', 'Unknown')}")

                # Stop if we've reached the limit
                if len(sales_tasks) >= limit:
                    break

        if verbose:
            print(f"\n✅ Filtered to {len(sales_tasks)} Sales Representatives tasks")

        return sales_tasks

    except Exception as e:
        print(f"❌ Error loading GDPval dataset: {e}")
        print("Note: This requires internet connection to download from HuggingFace")
        return []


def _parse_task(task: Dict, index: int) -> GDPvalTask:
    """
    Parse a raw GDPval task dictionary into a GDPvalTask object

    Args:
        task: Raw task dictionary from dataset
        index: Index of the task in the dataset

    Returns:
        GDPvalTask object
    """
    # Extract task components
    # The GDPval format has standardized fields

    task_id = task.get('task_id', f"task_{index:03d}")
    # Use 'prompt' field which contains the actual task description
    description = task.get('prompt', task.get('description', ''))

    # Reference files are in 'reference_files' field
    reference_files = task.get('reference_files', [])

    # Expected output format
    output_format = task.get('output_format', 'Excel (.xlsx)')

    # Sections (if specified)
    sections = task.get('sections', None)

    # Additional context
    additional_context = {
        'sector': task.get('sector', ''),
        'occupation': task.get('occupation', ''),
        'reference_file_urls': task.get('reference_file_urls', []),
        'original_index': index
    }

    return GDPvalTask(
        task_id=task_id,
        description=description,
        reference_files=reference_files,
        expected_output_format=output_format,
        sections=sections,
        additional_context=additional_context
    )


def download_reference_files(task: GDPvalTask, output_dir: str = "data/gdpval") -> List[str]:
    """
    Download reference files for a task to local storage

    Args:
        task: The GDPvalTask to download files for
        output_dir: Directory to save files (relative to backend/)

    Returns:
        List of local file paths
    """
    os.makedirs(output_dir, exist_ok=True)

    local_paths = []
    for file_url in task.reference_files:
        # Extract filename from URL
        filename = os.path.basename(file_url)
        local_path = os.path.join(output_dir, filename)

        # Download file (simplified - in production use requests)
        # For now, we'll assume files are already present or mock them
        local_paths.append(local_path)

    return local_paths


# Test function
if __name__ == "__main__":
    print("🧪 Testing GDPval Loader")
    print("="*60)

    # Load first 5 sales tasks
    tasks = load_sales_tasks(limit=5, verbose=True)

    print("\n📋 LOADED TASKS:")
    print("="*60)
    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. {task.task_id}")
        print(f"   Description: {task.description[:150]}...")
        print(f"   Reference files: {len(task.reference_files)}")
        print(f"   Output format: {task.expected_output_format}")
        if task.sections:
            print(f"   Sections: {', '.join(task.sections[:3])}...")

    print("\n✅ Test complete!")
