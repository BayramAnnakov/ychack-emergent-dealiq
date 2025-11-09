"""
BenchmarkOrchestrator - Execute GPTEVAL tasks using Agent Skills
Extends StreamingOrchestrator with Skills support for Excel generation
"""
import os
from typing import Optional, AsyncIterator, Dict, Any
from claude_agent_sdk import ClaudeAgentOptions
from .orchestrator_streaming import StreamingOrchestrator


class BenchmarkOrchestrator(StreamingOrchestrator):
    """Execute GPTEVAL benchmark tasks using Agent Skills"""

    def __init__(self, verbose: bool = True):
        """
        Initialize BenchmarkOrchestrator with Skills enabled

        Args:
            verbose: Enable verbose logging
        """
        # Initialize parent first
        super().__init__(verbose)

        # Override system prompt for benchmark tasks
        self.system_prompt = """You are DealIQ, an AI-powered sales analytics expert.

Your role is to execute professional sales analysis tasks that involve:
1. Reading and analyzing CRM/sales data from Excel files
2. Performing advanced analytics (calculations, trends, forecasts)
3. Creating professionally formatted Excel output files with:
   - Multiple sheets for different analysis sections
   - Excel FORMULAS (not hardcoded values) for all calculations
   - Proper formatting, headers, and structure
   - Clear insights and recommendations

When creating Excel files:
- Use the xlsx Skill to ensure proper formatting and formulas
- Include formulas like SUM(), AVERAGE(), growth calculations, etc.
- Format numbers, percentages, and currency appropriately
- Add clear section headers and explanations
- Create multiple sheets when organizing complex analyses

Be specific, data-driven, and provide professional-grade outputs."""

        # Get backend directory (where .claude/skills is located)
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

        if self.verbose:
            print(f"📂 Backend dir: {backend_dir}")
            print(f"🔧 Skills dir: {os.path.join(backend_dir, '.claude/skills/xlsx')}")

        # Configure options WITHOUT Skills tool (SDK bug causes hanging)
        # Instead, xlsx Skill guidance is in system_prompt and Claude uses it via Python/openpyxl
        # NOTE: xlsx Skill exists at backend/.claude/skills/xlsx/SKILL.md for reference
        self.options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            model="sonnet",  # Use latest Sonnet for best performance
            max_turns=30,    # More turns for complex Excel tasks with data analysis
            permission_mode="bypassPermissions",
            cwd=backend_dir,
            setting_sources=["user", "project"],
            allowed_tools=["Skill", "Read", "Write", "Bash"]
            # NOT including setting_sources or Skill in allowed_tools due to SDK hanging bug
        )

        if self.verbose:
            print("✅ BenchmarkOrchestrator initialized")
            print(f"   max_turns: {self.options.max_turns}")
            print(f"   cwd: {backend_dir}")
            print(f"   xlsx Skill: Available via Python/openpyxl (system prompt guidance)")

    async def execute_gpteval_task_streaming(
        self,
        task_description: str,
        reference_file_paths: list[str],
        output_filename: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a GPTEVAL task with streaming updates

        Args:
            task_description: The task description from GPTEVAL
            reference_file_paths: List of paths to reference data files
            output_filename: Name for the output Excel file

        Yields:
            Streaming updates with type and content
        """
        if self.verbose:
            print("\n" + "="*60)
            print("🎯 EXECUTING GPTEVAL TASK")
            print("="*60)
            print(f"📋 Task: {task_description[:100]}...")
            print(f"📂 Reference files: {len(reference_file_paths)}")
            print(f"📄 Output file: {output_filename}")

        # Build additional instructions for GDPval task
        # Get absolute path for the reference file
        import os
        reference_file = reference_file_paths[0] if reference_file_paths else ""
        if not os.path.isabs(reference_file):
            # Make it absolute relative to backend_dir
            backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
            reference_file = os.path.join(backend_dir, reference_file)

        additional_instructions = f"""
The reference data file is located at: {reference_file}

TASK DESCRIPTION:
{task_description}

OUTPUT REQUIREMENTS:
Create an Excel file named {output_filename} with:
- Multiple sheets if the task requires different sections
- Excel FORMULAS (not hardcoded values) for ALL calculations
- Proper formatting (numbers, percentages, currency)
- Clear section headers and structure
- Professional appearance suitable for executive review

Use formulas like:
- For totals: =SUM(B2:B10)
- For averages: =AVERAGE(C2:C10)
- For growth: =(B2-C2)/C2
- For percentages: =B2/SUM($B$2:$B$10)

Save the output as: {output_filename}"""

        if self.verbose:
            print(f"\n📝 Instructions length: {len(additional_instructions)} chars")
            print(f"\n📂 Using absolute path: {reference_file}")
            print("\n🚀 Starting execution with Skills enabled...")

        # Use parent's analyze_file_streaming method which is working
        # Pass the absolute file path
        async for update in self.analyze_file_streaming(
            file_path=reference_file,
            analysis_type="gdpval_task",
            description=additional_instructions
        ):
            # Output all updates for visibility
            if self.verbose:
                update_type = update.get("type", "unknown")

                if update_type == "assistant":
                    content = update.get("content", "")
                    tools = update.get("tool_uses", [])
                    if content:
                        preview = content[:100] + "..." if len(content) > 100 else content
                        print(f"\n💬 Assistant: {preview}")
                    if tools:
                        for tool in tools:
                            tool_name = tool.get("name", "unknown")
                            print(f"\n🔧 Tool: {tool_name}")
                            if tool_name == "Skill":
                                print(f"   🎯 xlsx Skill invoked!")

                elif update_type == "system":
                    subtype = update.get("subtype", "")
                    print(f"\n⚙️  System: {subtype}")

                elif update_type == "result":
                    duration = update.get("duration_ms", 0)
                    cost = update.get("cost_usd", 0)
                    turns = update.get("num_turns", 0)
                    print(f"\n✅ Result: {duration}ms, ${cost:.4f}, {turns} turns")

                elif update_type == "error":
                    error = update.get("error", "")
                    print(f"\n❌ Error: {error}")

            yield update

    def _build_gpteval_prompt(
        self,
        task_description: str,
        reference_file_paths: list[str],
        output_filename: str
    ) -> str:
        """
        Build prompt that triggers Claude to use xlsx Skill

        Args:
            task_description: The GPTEVAL task description
            reference_file_paths: Paths to reference data files
            output_filename: Desired output filename

        Returns:
            Formatted prompt string
        """
        # Format reference files list
        files_list = "\n".join(f"- {path}" for path in reference_file_paths)

        prompt = f"""You are executing a professional sales analysis task.

TASK DESCRIPTION:
{task_description}

REFERENCE DATA FILES:
{files_list}

REQUIRED OUTPUT FORMAT: Excel (.xlsx)

INSTRUCTIONS:
1. Read the reference Excel file(s) using the Read tool
2. Analyze the data as specified in the task description
3. Use the xlsx Skill to create a professional Excel file with:
   - Multiple sheets if the task requires different sections
   - Excel FORMULAS (not hardcoded values) for ALL calculations
   - Proper formatting (numbers, percentages, currency)
   - Clear section headers and structure
   - Professional appearance suitable for executive review
4. Save the output as: {output_filename}

CRITICAL: Use FORMULAS for calculations. For example:
- For totals: =SUM(B2:B10)
- For averages: =AVERAGE(C2:C10)
- For growth: =(B2-C2)/C2
- For percentages: =B2/SUM($B$2:$B$10)

The xlsx Skill will help you create properly formatted Excel files with validated formulas.

Begin your analysis now."""

        return prompt


async def test_benchmark():
    """Test the BenchmarkOrchestrator"""
    print("🚀 Testing BenchmarkOrchestrator with Skills")

    # Create orchestrator
    orchestrator = BenchmarkOrchestrator(verbose=True)

    # Simulate a simple GPTEVAL-style task
    task_description = """Analyze the sales data and create an Excel report with:
    1. Overall Business Metrics (Revenue, Units, Growth %)
    2. Top 5 Products by Revenue
    3. Bottom 5 Products by Performance
    Include formulas for all calculations."""

    reference_files = ["data/uploads/sample_crm_data.csv"]
    output_file = "test_benchmark_output.xlsx"

    print("\n📊 Executing test task...")
    async for update in orchestrator.execute_gpteval_task_streaming(
        task_description,
        reference_files,
        output_file
    ):
        # Updates already logged in verbose mode
        pass

    print("\n✅ Test complete!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_benchmark())
