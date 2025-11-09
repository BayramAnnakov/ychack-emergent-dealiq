# GDPval Benchmark Integration - Implementation Plan

## Goal
Transform DealIQ into a dual-mode AI sales analyst that can:
1. **Ad-Hoc Mode** (DONE): Answer natural language CRM queries
2. **Benchmark Mode** (IN PROGRESS): Execute GDPval sales analytics tasks and beat SOTA

---

## ✅ Completed: Phase 1.1 - Setup Excel Skill

**What was done:**
- Downloaded official Anthropic skills repository
- Copied xlsx skill to `backend/.claude/skills/xlsx/`
- Skill includes:
  - `SKILL.md` - Comprehensive Excel creation/editing instructions
  - `recalc.py` - Formula validation script
  - Best practices for formulas, formatting, error handling

**Files created:**
```
backend/.claude/skills/xlsx/
├── SKILL.md       # Skill definition
├── recalc.py      # Formula validator
└── LICENSE.txt
```

---

## 🚧 Next Steps

### Phase 1.2: Enable Skills in BenchmarkOrchestrator (30 min)

**Create new orchestrator with Skills enabled:**

```python
# backend/app/agents/benchmark_orchestrator.py
from claude_agent_sdk import ClaudeAgentOptions
from .orchestrator_streaming import StreamingOrchestrator

class BenchmarkOrchestrator(StreamingOrchestrator):
    """Execute GDPval tasks using Agent Skills"""

    def __init__(self, verbose=False):
        super().__init__(verbose)

        # Override options to include Skill tool
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

        self.options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            model="sonnet",
            max_turns=15,  # More turns for complex Excel tasks
            permission_mode="bypassPermissions",
            cwd=backend_dir,
            setting_sources=["project"],  # Load from .claude/skills
            allowed_tools=["Read", "Write", "Bash", "Skill", "Grep", "Glob"]
        )
```

---

### Phase 2: Load GDPval Tasks (30 min)

**2.1 Install HuggingFace datasets:**
```bash
cd backend
source venv/bin/activate
pip install datasets
```

**2.2 Create task loader:**
```python
# backend/app/benchmarks/gdpval/loader.py
from datasets import load_dataset
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class GDPvalTask:
    task_id: str
    description: str
    reference_files: List[str]
    expected_output_format: str
    sections: List[str]

def load_sales_tasks() -> List[GDPvalTask]:
    """Load GDPval sales analytics tasks from HuggingFace"""
    dataset = load_dataset("openai/gdpval", split="train")

    # Filter for sales-related tasks
    sales_keywords = ['sales', 'crm', 'revenue', 'account', 'retailer', 'makeup', 'cosmetics']
    sales_tasks = [
        task for task in dataset
        if any(kw in task['description'].lower() for kw in sales_keywords)
    ]

    return sales_tasks[:10]  # Start with 10 tasks
```

---

### Phase 3: Build Task Execution Pipeline (45 min)

**3.1 Task prompt template:**
```python
def build_task_prompt(task: GDPvalTask, reference_paths: List[str]) -> str:
    """
    Build prompt that triggers Claude to use xlsx Skill
    """
    return f\"\"\"
You are a national account director executing a sales analysis task.

TASK DESCRIPTION:
{task.description}

REFERENCE DATA FILES:
{chr(10).join(f'- {path}' for path in reference_paths)}

REQUIRED OUTPUT FORMAT: Excel (.xlsx)

INSTRUCTIONS:
1. Read the reference Excel files using the Read tool
2. Analyze the data as specified in the task description
3. Use the xlsx Skill to create a professional Excel file with:
   - Multiple sheets if needed
   - Excel FORMULAS (not hardcoded values) for all calculations
   - Proper formatting and structure
   - Clear section headers
4. Save as "task_{task.task_id}_output.xlsx"

The xlsx Skill will help you create properly formatted Excel files.
Begin analysis now.
\"\"\"
```

**3.2 Execution method:**
```python
async def execute_gdpval_task(self, task: GDPvalTask):
    """Execute a GDPval task and return output file path"""

    # 1. Download reference data
    reference_paths = await self.download_reference_data(task)

    # 2. Build prompt
    prompt = self.build_task_prompt(task, reference_paths)

    # 3. Execute with Claude (will auto-invoke xlsx Skill)
    output_file = None
    async for message in self.agent.query(prompt, self.options):
        # Track file creation
        if message.type == "result" and ".xlsx" in str(message):
            output_file = self.extract_file_path(message)
        yield message

    return output_file
```

---

### Phase 4: Testing (1 hour)

**Test script:**
```python
# backend/test_gdpval.py
import asyncio
from app.benchmarks.gdpval.loader import load_sales_tasks
from app.agents.benchmark_orchestrator import BenchmarkOrchestrator

async def test_first_task():
    # Load tasks
    tasks = load_sales_tasks()
    first_task = tasks[0]

    print(f"Testing: {first_task.task_id}")
    print(f"Description: {first_task.description[:200]}...")

    # Execute
    orchestrator = BenchmarkOrchestrator(verbose=True)
    output_file = await orchestrator.execute_gdpval_task(first_task)

    print(f"\\nOutput file: {output_file}")
    print("✅ Task completed!")

if __name__ == "__main__":
    asyncio.run(test_first_task())
```

---

## File Structure (Target)

```
backend/
├── .claude/
│   └── skills/
│       └── xlsx/           ✅ DONE
│           ├── SKILL.md
│           └── recalc.py
├── app/
│   ├── agents/
│   │   ├── orchestrator_streaming.py  (existing)
│   │   └── benchmark_orchestrator.py  (TODO)
│   └── benchmarks/
│       └── gdpval/
│           ├── __init__.py
│           ├── loader.py              (TODO)
│           ├── executor.py            (TODO)
│           ├── validator.py           (TODO)
│           ├── tasks/                 (auto-created)
│           └── reference_data/        (auto-created)
└── test_gdpval.py                    (TODO)
```

---

## Example: XR Retailer Makeup 2023 Task

**Input:**
- Task ID: `sales_xr_makeup_2023`
- Data: `Data XR MU 2023 Final.xlsx`
- Required Sections:
  1. Overall Business (TY, LY, % Change, $ Change)
  2. Discontinued SKUs Risk
  3. Function-level Analysis
  4. Top Functions
  5. Bottom Functions

**Expected Output:**
Excel file with 5 sections, formulas for calculations, professional formatting.

**How it will work:**
1. Load task from GDPval
2. Download reference Excel file
3. Claude reads Excel using Read tool
4. Claude autonomously invokes xlsx Skill
5. xlsx Skill creates output with formulas
6. recalc.py validates formulas
7. Output saved and validated

---

## Success Metrics

- ✅ Execute 5 GDPval sales tasks
- ✅ Generate valid Excel outputs
- ✅ Beat SOTA baseline scores
- ✅ Ad-hoc mode still works (no regression)

---

## Current Status

**✅ Completed:**
- Excel skill setup (`backend/.claude/skills/xlsx/`)
- BenchmarkOrchestrator with Skills enabled (`backend/app/agents/benchmark_orchestrator.py`)
- GDPval task loader from HuggingFace (`backend/app/benchmarks/gdpval/loader.py`)
- Task executor with streaming support (`backend/app/benchmarks/gdpval/executor.py`)
- HuggingFace submission formatter (CSV + deliverable_files format)
- End-to-end test script (`backend/test_gdpval.py`)

**🚧 In Progress:**
- Testing first GDPval task execution

**📋 TODO:**
- Run multiple sales analytics tasks
- Validate Excel outputs with recalc.py
- Create HuggingFace dataset for submission
- Submit to OpenAI autograder

---

## Time Estimate

- Remaining Phase 1: 30 min
- Phase 2: 30 min
- Phase 3: 45 min
- Phase 4: 1 hour

**Total remaining: ~2.5 hours**
