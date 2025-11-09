"""
GDPval Task Executor
Runs benchmark tasks and collects results for submission
"""
import os
import shutil
import asyncio
from typing import Dict, List, Optional
from pathlib import Path
from .loader import GDPvalTask
from app.agents.benchmark_orchestrator import BenchmarkOrchestrator


class GDPvalExecutor:
    """Executes GDPval tasks and prepares submissions"""

    def __init__(
        self,
        output_dir: str = "data/gdpval/outputs",
        verbose: bool = True
    ):
        """
        Initialize executor

        Args:
            output_dir: Directory to save task outputs
            verbose: Enable verbose logging
        """
        self.output_dir = output_dir
        self.verbose = verbose
        self.orchestrator = BenchmarkOrchestrator(verbose=verbose)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Track task results
        self.results: List[Dict] = []

    async def execute_task(
        self,
        task: GDPvalTask,
        reference_files: List[str]
    ) -> Dict:
        """
        Execute a single GDPval task

        Args:
            task: The GDPvalTask to execute
            reference_files: List of local paths to reference files

        Returns:
            Dictionary with task result including output file path
        """
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"🎯 EXECUTING TASK: {task.task_id}")
            print(f"{'='*70}")
            print(f"Description: {task.description[:200]}...")
            print(f"Reference files: {reference_files}")

        # Generate output filename
        output_filename = f"{task.task_id}_output.xlsx"
        output_path = os.path.join(self.output_dir, output_filename)

        # Track execution metadata
        result = {
            "task_id": task.task_id,
            "status": "running",
            "output_file": None,
            "deliverable_text": "",
            "error": None
        }

        try:
            # Execute task with streaming
            deliverable_text_parts = []

            async for update in self.orchestrator.execute_gpteval_task_streaming(
                task_description=task.description,
                reference_file_paths=reference_files,
                output_filename=output_filename
            ):
                # Collect any text output for deliverable_text
                if update.get("type") == "assistant" and update.get("content"):
                    content = update["content"]
                    deliverable_text_parts.append(content)

                    if self.verbose:
                        # Show preview of content
                        preview = content[:100] + "..." if len(content) > 100 else content
                        print(f"   💬 {preview}")

                # Check for completion
                if update.get("type") == "result":
                    if update.get("is_error"):
                        result["status"] = "error"
                        result["error"] = "Task execution failed"
                    else:
                        result["status"] = "completed"

                    if self.verbose:
                        print(f"\n   ✅ Execution complete")
                        print(f"   Duration: {update.get('duration_ms', 0)}ms")
                        print(f"   Cost: ${update.get('cost_usd', 0):.4f}")

            # Combine deliverable text
            result["deliverable_text"] = "\n".join(deliverable_text_parts)

            # Verify output file was created
            if os.path.exists(output_path):
                result["output_file"] = output_filename
                if self.verbose:
                    file_size = os.path.getsize(output_path)
                    print(f"   📄 Output file: {output_filename} ({file_size} bytes)")
            else:
                if self.verbose:
                    print(f"   ⚠️  Output file not found at: {output_path}")
                # File might be in different location, search for it
                result["output_file"] = self._find_output_file(output_filename)

            # Store result
            self.results.append(result)

        except Exception as e:
            if self.verbose:
                print(f"   ❌ ERROR: {str(e)}")
                import traceback
                traceback.print_exc()

            result["status"] = "error"
            result["error"] = str(e)
            self.results.append(result)

        return result

    def _find_output_file(self, filename: str) -> Optional[str]:
        """
        Search for output file in common locations

        Args:
            filename: Name of the file to find

        Returns:
            Relative path to file if found, None otherwise
        """
        # Search locations
        search_paths = [
            os.path.join(".", filename),
            os.path.join("data", filename),
            os.path.join("data/uploads", filename),
            os.path.join(self.output_dir, filename),
        ]

        for path in search_paths:
            if os.path.exists(path):
                # Copy to output directory
                shutil.copy(path, os.path.join(self.output_dir, filename))
                return filename

        return None

    def prepare_submission(self, output_csv: str = "data/gdpval/submission.csv") -> str:
        """
        Prepare results for GDPval submission

        Creates a CSV file with task_id, deliverable_text, deliverable_files columns
        that can be added to the HuggingFace dataset

        Args:
            output_csv: Path to save submission CSV

        Returns:
            Path to the submission CSV file
        """
        if self.verbose:
            print(f"\n{'='*70}")
            print("📦 PREPARING SUBMISSION")
            print(f"{'='*70}")

        import csv

        # Create submissions directory
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)

        # Write CSV
        with open(output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'task_id',
                'deliverable_text',
                'deliverable_files',
                'status'
            ])
            writer.writeheader()

            for result in self.results:
                # Format deliverable_files as list
                deliverable_files = []
                if result.get('output_file'):
                    deliverable_files.append(f"deliverable_files/{result['output_file']}")

                writer.writerow({
                    'task_id': result['task_id'],
                    'deliverable_text': result.get('deliverable_text', ''),
                    'deliverable_files': str(deliverable_files),  # Will be parsed by HF
                    'status': result['status']
                })

        if self.verbose:
            print(f"✅ Submission CSV created: {output_csv}")
            print(f"   Tasks: {len(self.results)}")
            completed = sum(1 for r in self.results if r['status'] == 'completed')
            print(f"   Completed: {completed}/{len(self.results)}")
            print(f"\nNext steps:")
            print(f"1. Copy files from {self.output_dir}/ to deliverable_files/")
            print(f"2. Upload to HuggingFace dataset")
            print(f"3. Submit dataset URL at https://evals.openai.com/gdpval/grading")

        return output_csv

    def get_summary(self) -> Dict:
        """Get execution summary statistics"""
        completed = sum(1 for r in self.results if r['status'] == 'completed')
        errors = sum(1 for r in self.results if r['status'] == 'error')

        return {
            'total_tasks': len(self.results),
            'completed': completed,
            'errors': errors,
            'success_rate': completed / len(self.results) if self.results else 0,
            'results': self.results
        }


async def test_executor():
    """Test the GDPval executor"""
    from .loader import load_sales_tasks

    print("🧪 Testing GDPval Executor")
    print("="*70)

    # Load first task
    tasks = load_sales_tasks(limit=1, verbose=True)

    if not tasks:
        print("❌ No tasks loaded")
        return

    # Create executor
    executor = GDPvalExecutor(verbose=True)

    # Execute first task (mocked reference files for now)
    first_task = tasks[0]
    reference_files = ["data/uploads/sample_crm_data.csv"]  # Mock

    result = await executor.execute_task(first_task, reference_files)

    print(f"\n{'='*70}")
    print("📊 EXECUTION RESULT:")
    print(f"{'='*70}")
    print(f"Task ID: {result['task_id']}")
    print(f"Status: {result['status']}")
    print(f"Output file: {result.get('output_file', 'N/A')}")
    print(f"Text length: {len(result.get('deliverable_text', ''))}")

    # Prepare submission
    submission_path = executor.prepare_submission()
    print(f"\n✅ Submission prepared: {submission_path}")

    # Show summary
    summary = executor.get_summary()
    print(f"\n📈 SUMMARY:")
    print(f"   Total: {summary['total_tasks']}")
    print(f"   Completed: {summary['completed']}")
    print(f"   Success rate: {summary['success_rate']*100:.1f}%")


if __name__ == "__main__":
    asyncio.run(test_executor())
