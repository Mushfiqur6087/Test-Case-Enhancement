"""
Parser for test_cases.md files.
"""

import re
from typing import Dict, List, Tuple
from test_case_enhancement.core.models import TestCase, TestCaseStep

def parse_test_cases(file_path: str) -> Dict[str, List[TestCase]]:
    """
    Parse a test cases markdown file and return a dictionary mapping
    module names to their list of TestCase objects.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading test cases file: {e}")
        return {}

    modules_dict: Dict[str, List[TestCase]] = {}
    current_module = ""
    current_tc = None

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        
        # Match Module Header: ## 1. Login
        module_match = re.match(r"^##\s+(?:\d+\.\s+)?(.+)$", line)
        if module_match and not line.lower().startswith("## summary"):
            current_module = module_match.group(1).strip()
            if current_module not in modules_dict:
                modules_dict[current_module] = []
            current_tc = None
            continue

        # Match TC Header: ### TC-001 — Title ✅ Type | Priority
        tc_match = re.match(r"^###\s+([A-Z0-9-]+)\s*[—\-]\s*(.*?)(?:[✅❌⚡]\s*([^|]+)\|\s*(.+))?$", line)
        if tc_match and current_module:
            tc_id = tc_match.group(1).strip()
            title = tc_match.group(2).strip()
            tc_type = tc_match.group(3).strip() if tc_match.group(3) else "Unknown"
            priority = tc_match.group(4).strip() if tc_match.group(4) else "Unknown"
            
            current_tc = TestCase(
                tc_id=tc_id,
                title=title,
                tc_type=tc_type,
                priority=priority,
                module_name=current_module,
                preconditions="",
                steps=[],
                expected_result=""
            )
            modules_dict[current_module].append(current_tc)
            continue

        # Match Table Rows if we have an active TC
        if current_tc and line.startswith("|") and "**" in line:
            # e.g. | **Preconditions** | User is unauthenticated... |
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                key = parts[0].replace("*", "").strip()
                val = parts[1].strip()
                
                if key.lower() == "preconditions":
                    current_tc.preconditions = val
                elif key.lower() == "expected result":
                    current_tc.expected_result = val
                elif key.lower() == "steps":
                    # Steps are separated by <br>
                    step_strings = val.split("<br>")
                    for s in step_strings:
                        s = s.strip()
                        if not s:
                            continue
                        # Match "1. Enter something"
                        step_match = re.match(r"^(\d+)\.\s+(.+)$", s)
                        if step_match:
                            num = int(step_match.group(1))
                            desc = step_match.group(2).strip()
                            current_tc.steps.append(TestCaseStep(number=num, description=desc))
                        else:
                            # If no number, just append as a step
                            current_tc.steps.append(TestCaseStep(number=len(current_tc.steps) + 1, description=s))

    return modules_dict
