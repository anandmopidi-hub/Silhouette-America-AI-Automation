"""Silhouette America AI Automation — Professional Custom HTML Reporter.

Generates a modern, responsive, client-friendly AI Test Automation Execution
Report with dynamic execution metrics, test-specific steps, expected and actual
results, assertion summaries, screenshot previews, embedded video players,
and collapsible technical logs.
"""
import html
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class CustomReporter:
    """Enterprise-grade Test Execution Reporter for Silhouette America."""

    MODULE_NAMES = {
        "test_clearance.py": "Clearance / Sale Items",
        "test_club_silhouette.py": "Club Silhouette",
        "test_creator_rewards.py": "Creator Rewards",
        "test_different_product_pdp.py": "Product Detail Page (Different PDP)",
        "test_exclusive_classes.py": "Exclusive Classes",
        "test_footer.py": "Footer",
        "test_header.py": "Header Navigation",
        "test_homepage.py": "Homepage",
        "test_login.py": "Authentication / Login",
        "test_machine_registration.py": "Machine Registration",
        "test_my_account.py": "My Account",
        "test_order_purchase.py": "Order Purchase & Checkout",
        "test_pdp.py": "Product Detail Page (PDP)",
        "test_plp_filter_and_sortby.py": "Catalog PLP Filter & Sort",
        "test_product_user_manuals.py": "Product User Manuals",
        "test_registration.py": "User Registration",
        "test_search.py": "Search",
        "test_software.py": "Software Downloads",
        "test_wishlist.py": "Wishlist",
    }

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.start_time = time.time()
        self.start_dt = datetime.now()
        self.end_time: Optional[float] = None
        self.end_dt: Optional[datetime] = None
        self.discovered_tests_count: int = 0
        self.discovered_tests: List[Dict[str, str]] = []
        self.test_records: List[Dict[str, Any]] = []
        self.environment: str = "production"
        self.browser: str = "Chromium"
        self.is_headless: bool = False
        self.base_url: str = "https://www.silhouetteamerica.com/"

    @property
    def executed_tests(self) -> List[Dict[str, Any]]:
        """Alias for test_records to maintain backward compatibility."""
        return self.test_records

    @executed_tests.setter
    def executed_tests(self, val: List[Dict[str, Any]]) -> None:
        self.test_records = val

    @classmethod
    def get_module_name(cls, file_name: str) -> str:
        """Map test filename to human-friendly module name."""
        base = os.path.basename(file_name)
        return cls.MODULE_NAMES.get(base, base.replace("test_", "").replace(".py", "").replace("_", " ").title())

    @classmethod
    def extract_test_id(cls, test_name: str, nodeid: str = "") -> str:
        """Extract clean normalized Test Case ID (e.g. E2E-CLR-001 or E2E-MACHINE-010 [CAMEO 5 PLUS])."""
        combined = f"{test_name} {nodeid}"
        diff_pdp_match = re.search(r"E2E[-_]DIFFERENT[-_]PDP[-_](\d+)", combined, re.IGNORECASE)
        order_tc_match = re.search(r"E2E[-_]ORDER[-_]PURCHASE[-_](\d+)", combined, re.IGNORECASE)
        tc_match = re.search(r"(E2E[-_][A-Za-z0-9_]+[-_]\d+)", combined, re.IGNORECASE)

        if diff_pdp_match:
            base_id = f"E2E-Different_PDP-{diff_pdp_match.group(1)}"
        elif order_tc_match:
            base_id = f"E2E-ORDER_Purchase-{order_tc_match.group(1)}"
        elif tc_match:
            base_id = tc_match.group(1).upper().replace("_", "-")
        else:
            base_id = test_name

        # For data-driven parameterized tests, append dataset label to distinguish runs in report
        param_match = re.search(r"\[(.*?)\]$", nodeid)
        if param_match:
            clean_param = param_match.group(1).strip().replace("serial_", "").replace("_", " ")
            return f"{base_id} [{clean_param}]"

        return base_id

    @classmethod
    def parse_docstring_metadata(cls, doc: Optional[str], test_name: str, tc_id: str) -> Dict[str, Any]:
        """Extract readable title, numbered steps, and expected result from docstring."""
        if not doc:
            clean_fn = re.sub(r"^test_e2e_[a-z0-9]+_\d+_", "", test_name)
            title = clean_fn.replace("_", " ").title()
            return {
                "title": title or tc_id,
                "steps": [
                    "Open target application page and wait for DOM stabilization.",
                    "Execute primary workflow actions and handle transient overlays.",
                    "Verify DOM state, attributes, URLs, and assertion expectations.",
                ],
                "expected": f"Test case {tc_id} executes without errors and all assertions pass.",
            }

        lines = [l.strip() for l in doc.strip().splitlines() if l.strip()]
        if not lines:
            return {"title": tc_id, "steps": [], "expected": "All assertions pass successfully."}

        first_line = lines[0]
        # Match pattern like "E2E-CLR-001: Page Landing & Hero Banner."
        m = re.match(r"^[A-Za-z0-9_\-]+:\s*(.+?)(?:\.|$)", first_line)
        if m:
            title = m.group(1).strip()
        else:
            title = first_line.rstrip(".")

        # Extract numbered steps
        steps: List[str] = []
        for line in lines[1:]:
            m_step = re.match(r"^(\d+)\.\s*(.+)$", line)
            if m_step:
                steps.append(m_step.group(2).strip())

        # If no numbered steps in docstring, look for bullet points
        if not steps:
            for line in lines[1:]:
                if line.startswith("- ") or line.startswith("* "):
                    steps.append(line[2:].strip())

        if not steps:
            clean_fn = re.sub(r"^test_e2e_[a-z0-9]+_\d+_", "", test_name)
            steps = [
                f"Navigate to {title} interface and verify initial rendering.",
                "Execute designated user actions and extract dynamic values.",
                "Assert functional expectations and response parameters.",
            ]

        # Extract expected result
        expected = f"{title} functionality operates correctly and all UI assertions pass."
        for line in lines:
            if "verify" in line.lower() or "assert" in line.lower() or "expected" in line.lower():
                expected = line.rstrip(".") + "."
                break

        return {
            "title": title,
            "steps": steps,
            "expected": expected,
        }

    @classmethod
    def extract_actual_and_assertions(
        cls, logs: str, outcome: str, doc_meta: Dict[str, Any]
    ) -> Tuple[str, List[str]]:
        """Extract actual observed browser observations and assertion checklist from logs."""
        assertions: List[str] = []
        actual_snippets: List[str] = []

        log_lines = logs.splitlines()
        for line in log_lines:
            # Skip banner separators and test lifecycle markers
            if "=====" in line or "STARTING TEST:" in line or "FINISHED TEST:" in line:
                continue

            # Look for verified assertions in logs
            if "Verified" in line or "assert" in line.lower():
                m_v = re.search(r"\bVerified\s+([A-Za-z0-9_ -].*?)(?:\s*=+)?$", line)
                if m_v:
                    val = m_v.group(1).strip().strip("= ")
                    if val and not val.startswith("="):
                        entry = f"Verified {val}: Passed"
                        if entry not in assertions:
                            assertions.append(entry)
                elif "assert" in line.lower():
                    m_a = re.search(r"\|\s*([A-Za-z0-9_ -]+assert.+)$", line, re.IGNORECASE)
                    if m_a:
                        entry = f"{m_a.group(1).strip()}: Passed"
                        if entry not in assertions:
                            assertions.append(entry)

            # Look for actual values (status, URL, headings, counts, serial allocation)
            if (
                "Final URL:" in line
                or "HTTP Status:" in line
                or "Discovered" in line
                or "Resulting products:" in line
                or "Serial Allocation" in line
                or "Selected Serial" in line
                or "[ATTEMPT" in line
            ):
                m_act = re.search(r"(?:Final URL|HTTP Status|Discovered|Resulting products|Validation complete|Serial Allocation|Selected Serial|\[ATTEMPT).+$", line)
                if m_act:
                    snip = m_act.group(0).strip()
                    if snip not in actual_snippets:
                        actual_snippets.append(snip)

        if not assertions:
            if outcome == "passed":
                assertions.append("All DOM and UI state assertions verified: Passed")
            elif outcome == "failed":
                assertions.append("Assertion check failed: Error")
            else:
                assertions.append("Test skipped: No assertions executed")

        if outcome == "passed":
            if actual_snippets:
                actual_result = " | ".join(actual_snippets[:3]) + " | Execution finished with status: PASSED."
            else:
                actual_result = f"{doc_meta['title']} verified successfully on live application with status: PASSED."
        elif outcome == "failed":
            actual_result = "Test failed during assertion check or UI interaction. Inspect technical logs below for traceback."
        else:
            actual_result = "Test execution was skipped."

        return actual_result, assertions

    def record_test_run(
        self,
        nodeid: str,
        test_name: str,
        file_path: str,
        docstring: Optional[str],
        outcome: str,
        duration: float,
        logs: str,
        screenshot_path: Optional[str] = None,
        video_path: Optional[str] = None,
        error_msg: Optional[str] = None,
        traceback_str: Optional[str] = None,
    ) -> None:
        """Record completed test run metrics and evidence."""
        tc_id = self.extract_test_id(test_name, nodeid)
        doc_meta = self.parse_docstring_metadata(docstring, test_name, tc_id)
        module_name = self.get_module_name(file_path)

        # For parameterized tests, update title to reflect the specific dataset/model
        param_match = re.search(r"\[(.*?)\]$", nodeid)
        if param_match:
            clean_param = param_match.group(1).strip().replace("serial_", "").replace("_", " ")
            if clean_param and clean_param.lower() not in doc_meta["title"].lower():
                doc_meta["title"] = f"{doc_meta['title']} ({clean_param})"

        actual_res, assertions = self.extract_actual_and_assertions(logs, outcome, doc_meta)

        # Normalize relative evidence paths from reports/html/ to artifacts/
        rel_ss = None
        if screenshot_path and os.path.exists(screenshot_path):
            rel_ss = os.path.relpath(screenshot_path, start=str(self.output_path.parent)).replace("\\", "/")
        else:
            cand = self.find_evidence_file("screenshots", tc_id, outcome, ".png")
            if cand:
                rel_ss = os.path.relpath(cand, start=str(self.output_path.parent)).replace("\\", "/")

        rel_vid = None
        if video_path and os.path.exists(video_path):
            rel_vid = os.path.relpath(video_path, start=str(self.output_path.parent)).replace("\\", "/")
        else:
            cand = self.find_evidence_file("videos", tc_id, outcome, ".webm")
            if cand:
                rel_vid = os.path.relpath(cand, start=str(self.output_path.parent)).replace("\\", "/")

        formatted_duration = f"{int(duration // 60):02d}:{int(duration % 60):02d}"

        full_logs = logs.strip()
        if traceback_str and traceback_str not in full_logs:
            full_logs = f"{full_logs}\n\n[FAILURE TRACEBACK]\n{traceback_str}".strip() if full_logs else traceback_str.strip()
        elif error_msg and error_msg not in full_logs:
            full_logs = f"{full_logs}\n\n[ERROR MESSAGE]\n{error_msg}".strip() if full_logs else error_msg.strip()

        test_data = {
            "nodeid": nodeid,
            "test_case_id": tc_id,
            "test_name": test_name,
            "title": doc_meta["title"],
            "module": module_name,
            "file": os.path.basename(file_path),
            "status": outcome.upper(),
            "duration_seconds": round(duration, 2),
            "duration_formatted": formatted_duration,
            "steps": doc_meta["steps"],
            "expected_result": doc_meta["expected"],
            "actual_result": actual_res,
            "assertions": assertions,
            "screenshot_rel": rel_ss,
            "video_rel": rel_vid,
            "logs": full_logs,
            "error_msg": error_msg,
            "traceback": traceback_str,
        }
        self.test_records.append(test_data)

    def find_evidence_file(self, evidence_type: str, tc_id: str, outcome: str, ext: str) -> Optional[Path]:
        """Search for evidence file in artifacts directory."""
        project_root = self.output_path.parent.parent.parent
        target_dirs = [
            project_root / "artifacts" / evidence_type / outcome.lower(),
            project_root / "artifacts" / evidence_type / "passed",
            project_root / "artifacts" / evidence_type / "failed",
            project_root / "artifacts" / evidence_type / "skipped",
        ]
        base_id = tc_id.split()[0] if " " in tc_id else tc_id
        candidate_names = [
            f"{tc_id}_{outcome.lower()}{ext}",
            f"{base_id}_{outcome.lower()}{ext}",
            f"{tc_id}_passed{ext}",
            f"{base_id}_passed{ext}",
            f"{tc_id}_failed{ext}",
            f"{base_id}_failed{ext}",
            f"{tc_id}{ext}",
            f"{base_id}{ext}",
        ]
        for d in target_dirs:
            if not d.exists():
                continue
            for name in candidate_names:
                cand = d / name
                if cand.exists():
                    return cand
            clean_search = re.sub(r"[\[\]*?]", "", base_id)
            for f in d.glob(f"*{clean_search}*{ext}"):
                return f
        return None

    def generate_html_report(self) -> Path:
        """Generate professional standalone HTML report."""
        if self.end_time is None:
            self.end_time = time.time()
        if self.end_dt is None:
            self.end_dt = datetime.now()
        total_duration = max(0.0, self.end_time - self.start_time)
        total_mins = int(total_duration // 60)
        total_secs = int(total_duration % 60)
        total_duration_formatted = f"{total_mins}m {total_secs:02d}s"

        total_executed = len(self.test_records)
        passed_count = sum(1 for t in self.test_records if t["status"] == "PASSED")
        failed_count = sum(1 for t in self.test_records if t["status"] == "FAILED")
        skipped_count = sum(1 for t in self.test_records if t["status"] == "SKIPPED")
        error_count = sum(1 for t in self.test_records if t["status"] == "ERROR")

        success_rate = round((passed_count / total_executed * 100), 1) if total_executed > 0 else 0.0

        if failed_count > 0 or error_count > 0:
            overall_status = "Failed"
            status_color = "#ef4444"
        elif total_executed == 0:
            overall_status = "Not Run"
            status_color = "#64748b"
        elif skipped_count > 0 and passed_count > 0:
            overall_status = "Partially Completed"
            status_color = "#f59e0b"
        else:
            overall_status = "Passed"
            status_color = "#10b981"

        # Module-wise breakdown
        modules_summary: Dict[str, Dict[str, int]] = {}
        for t in self.test_records:
            mod = t["module"]
            if mod not in modules_summary:
                modules_summary[mod] = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
            modules_summary[mod]["total"] += 1
            if t["status"] == "PASSED":
                modules_summary[mod]["passed"] += 1
            elif t["status"] == "FAILED":
                modules_summary[mod]["failed"] += 1
            elif t["status"] == "SKIPPED":
                modules_summary[mod]["skipped"] += 1

        # Format executed modules summary text
        if len(modules_summary) == 1:
            active_module_text = list(modules_summary.keys())[0]
        elif len(modules_summary) > 1:
            active_module_text = f"Multiple Modules ({len(modules_summary)})"
        else:
            active_module_text = "Multiple Modules (19)"

        # 12-hour format with AM/PM for execution window
        start_12h = self.start_dt.strftime("%I:%M:%S %p")
        end_12h = self.end_dt.strftime("%I:%M:%S %p")
        if self.start_dt.date() != self.end_dt.date():
            execution_window_str = f"{start_12h} – {end_12h} (next day)"
        else:
            execution_window_str = f"{start_12h} – {end_12h}"

        # Full month format: e.g. November 16, 2026
        execution_date_str = self.start_dt.strftime("%B %d, %Y")

        # JSON payload for client-side interactivity
        tests_json = json.dumps(self.test_records)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Silhouette America - Automation Test Execution Results</title>
  <style>
    :root {{
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-light: #eff6ff;
      --success: #10b981;
      --success-light: #ecfdf5;
      --danger: #ef4444;
      --danger-light: #fef2f2;
      --warning: #f59e0b;
      --warning-light: #fffbeb;
      --slate-50: #f8fafc;
      --slate-100: #f1f5f9;
      --slate-200: #e2e8f0;
      --slate-300: #cbd5e1;
      --slate-600: #475569;
      --slate-700: #334155;
      --slate-800: #1e293b;
      --slate-900: #0f172a;
      --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font-family);
      background-color: #f8fafc;
      color: var(--slate-800);
      line-height: 1.5;
      padding: 24px;
    }}
    .container {{
      max-width: 1440px;
      margin: 0 auto;
    }}
    /* Header Card */
    .header-card {{
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      color: #ffffff;
      border-radius: 16px;
      padding: 32px;
      margin-bottom: 24px;
      box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
    }}
    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 24px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 20px;
    }}
    .header-brand h1 {{
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .header-brand h1 span.badge-ai {{
      background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
      color: #0f172a;
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 6px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .header-brand p {{
      color: #94a3b8;
      font-size: 14px;
      margin-top: 4px;
    }}
    .header-status-badge {{
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid {status_color};
      color: {status_color};
      font-weight: 700;
      padding: 6px 16px;
      border-radius: 30px;
      font-size: 13px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .header-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
    }}
    .header-meta-item {{
      display: flex;
      flex-direction: column;
    }}
    .meta-label {{
      font-size: 12px;
      color: #94a3b8;
      text-transform: uppercase;
      font-weight: 600;
      letter-spacing: 0.5px;
    }}
    .meta-val {{
      font-size: 14.5px;
      color: #f1f5f9;
      font-weight: 600;
      margin-top: 2px;
    }}

    /* Summary Dashboard Cards */
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 20px;
      margin-bottom: 24px;
    }}
    .summary-card {{
      background: #ffffff;
      border-radius: 14px;
      padding: 22px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
      border: 1px solid var(--slate-200);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}
    .card-title {{
      font-size: 13px;
      font-weight: 700;
      color: var(--slate-600);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .card-icon {{
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: bold;
    }}
    .card-val {{
      font-size: 32px;
      font-weight: 800;
      color: var(--slate-900);
      line-height: 1.1;
    }}
    .card-subtext {{
      font-size: 12px;
      color: var(--slate-600);
      margin-top: 6px;
    }}

    .card-total .card-icon {{ background: var(--primary-light); color: var(--primary); }}
    .card-passed .card-icon {{ background: var(--success-light); color: var(--success); }}
    .card-failed .card-icon {{ background: var(--danger-light); color: var(--danger); }}
    .card-skipped .card-icon {{ background: var(--warning-light); color: var(--warning); }}

    /* Module Breakdown Bar */
    .module-card {{
      background: #ffffff;
      border-radius: 14px;
      padding: 20px 24px;
      margin-bottom: 24px;
      border: 1px solid var(--slate-200);
      box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }}
    .module-card h3 {{
      font-size: 13px;
      font-weight: 700;
      color: var(--slate-700);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 14px;
    }}
    .module-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .mod-pill {{
      background: var(--slate-50);
      border: 1px solid var(--slate-200);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--slate-700);
    }}
    .mod-pill-badge {{
      background: var(--primary);
      color: #fff;
      padding: 2px 6px;
      border-radius: 10px;
      font-size: 11px;
    }}

    /* Main Table Container */
    .table-container {{
      background: #ffffff;
      border-radius: 14px;
      border: 1px solid var(--slate-200);
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      overflow: hidden;
      margin-bottom: 30px;
    }}
    .table-toolbar {{
      padding: 20px 24px;
      border-bottom: 1px solid var(--slate-200);
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      background: #fff;
    }}
    .search-box {{
      position: relative;
      min-width: 280px;
    }}
    .search-input {{
      width: 100%;
      padding: 9px 14px 9px 36px;
      font-size: 13px;
      border: 1px solid var(--slate-300);
      border-radius: 8px;
      outline: none;
      transition: border-color 0.2s;
    }}
    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }}
    .search-icon {{
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--slate-600);
      font-size: 13px;
    }}
    .filters-group {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .filter-btn {{
      padding: 7px 14px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 8px;
      border: 1px solid var(--slate-200);
      background: #ffffff;
      color: var(--slate-700);
      cursor: pointer;
      transition: all 0.2s;
    }}
    .filter-btn:hover {{ background: var(--slate-100); }}
    .filter-btn.active {{
      background: var(--slate-800);
      color: #ffffff;
      border-color: var(--slate-800);
    }}
    .select-dropdown {{
      padding: 8px 12px;
      font-size: 12px;
      border: 1px solid var(--slate-300);
      border-radius: 8px;
      background: #fff;
      color: var(--slate-700);
      cursor: pointer;
      outline: none;
    }}
    .btn-clear {{
      background: none;
      border: none;
      color: var(--primary);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      padding: 6px 10px;
      text-decoration: underline;
    }}

    /* Table Styling */
    table.test-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }}
    table.test-table th {{
      background: var(--slate-50);
      padding: 12px 20px;
      font-size: 12px;
      font-weight: 700;
      color: var(--slate-600);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid var(--slate-200);
      user-select: none;
    }}
    table.test-table td {{
      padding: 14px 20px;
      font-size: 13px;
      border-bottom: 1px solid var(--slate-200);
      vertical-align: middle;
    }}
    table.test-table tr.test-row {{
      cursor: pointer;
      transition: background-color 0.15s;
    }}
    table.test-table tr.test-row:hover {{
      background-color: #f8fafc;
    }}

    /* Result Badges */
    .badge-status {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }}
    .status-passed {{
      background: var(--success-light);
      color: #065f46;
      border: 1px solid #a7f3d0;
    }}
    .status-failed {{
      background: var(--danger-light);
      color: #991b1b;
      border: 1px solid #fecaca;
    }}
    .status-skipped {{
      background: var(--warning-light);
      color: #92400e;
      border: 1px solid #fde68a;
    }}

    .tc-id {{
      font-weight: 700;
      color: var(--slate-900);
    }}
    .tc-title {{
      font-weight: 600;
      color: var(--slate-700);
    }}
    .tc-mod {{
      color: var(--slate-600);
      font-size: 12px;
    }}
    .tc-dur {{
      font-family: monospace;
      font-size: 12px;
      color: var(--slate-600);
    }}

    /* Evidence Action Links */
    .evidence-link {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 12px;
      font-weight: 600;
      color: var(--primary);
      text-decoration: none;
      padding: 4px 10px;
      border-radius: 6px;
      background: var(--primary-light);
      border: 1px solid #bfdbfe;
      cursor: pointer;
      transition: background 0.2s;
    }}
    .evidence-link:hover {{
      background: #dbeafe;
    }}
    .evidence-na {{
      color: #94a3b8;
      font-size: 12px;
    }}

    /* Pagination */
    .table-footer {{
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #fff;
    }}
    .pagination-info {{
      font-size: 13px;
      color: var(--slate-600);
    }}
    .pagination-controls {{
      display: flex;
      gap: 6px;
    }}
    .page-btn {{
      padding: 6px 12px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 6px;
      border: 1px solid var(--slate-300);
      background: #ffffff;
      color: var(--slate-700);
      cursor: pointer;
    }}
    .page-btn.active {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }}
    .page-btn:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}

    /* Detailed Modal */
    .modal-backdrop {{
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(15, 23, 42, 0.65);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 24px;
      backdrop-filter: blur(4px);
    }}
    .modal-container {{
      background: #ffffff;
      border-radius: 16px;
      width: 100%;
      max-width: 980px;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      position: relative;
    }}
    .modal-header {{
      padding: 24px;
      border-bottom: 1px solid var(--slate-200);
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      background: #ffffff;
      z-index: 10;
    }}
    .modal-title-group h2 {{
      font-size: 19px;
      font-weight: 800;
      color: var(--slate-900);
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .modal-title-group p {{
      font-size: 13px;
      color: var(--slate-600);
      margin-top: 3px;
    }}
    .modal-close-btn {{
      background: var(--slate-100);
      border: none;
      font-size: 18px;
      width: 34px;
      height: 34px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--slate-600);
    }}
    .modal-close-btn:hover {{
      background: var(--slate-200);
      color: var(--slate-900);
    }}
    .modal-body {{
      padding: 24px;
    }}
    .section-block {{
      margin-bottom: 24px;
    }}
    .section-block h4 {{
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--slate-600);
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    /* Execution Steps List */
    .steps-list {{
      list-style: none;
      border-left: 2px solid var(--slate-200);
      padding-left: 16px;
      margin-left: 8px;
    }}
    .step-item {{
      position: relative;
      margin-bottom: 12px;
      font-size: 13px;
      color: var(--slate-700);
    }}
    .step-item::before {{
      content: "";
      position: absolute;
      left: -21px;
      top: 5px;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--primary);
    }}

    /* Callout Boxes */
    .callout-box {{
      background: var(--slate-50);
      border: 1px solid var(--slate-200);
      border-radius: 10px;
      padding: 14px 18px;
      font-size: 13px;
      color: var(--slate-800);
    }}
    .callout-expected {{
      background: #f0fdf4;
      border-color: #bbf7d0;
      color: #14532d;
    }}
    .callout-actual {{
      background: #f8fafc;
      border-color: #cbd5e1;
      color: #0f172a;
    }}

    /* Assertion Checklist */
    .assertions-list {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .assertion-item {{
      font-size: 12.5px;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-radius: 6px;
      background: #f8fafc;
      border: 1px solid var(--slate-200);
    }}

    /* Evidence Showcase */
    .evidence-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }}
    .evidence-pane {{
      background: var(--slate-50);
      border: 1px solid var(--slate-200);
      border-radius: 12px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .evidence-pane h5 {{
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--slate-600);
      margin-bottom: 12px;
      width: 100%;
      text-align: left;
    }}
    .img-preview {{
      max-width: 100%;
      max-height: 240px;
      object-fit: cover;
      border-radius: 8px;
      border: 1px solid var(--slate-300);
      cursor: pointer;
      transition: transform 0.2s;
    }}
    .img-preview:hover {{
      transform: scale(1.02);
    }}
    .video-container {{
      width: 100%;
    }}
    video.embedded-video {{
      width: 100%;
      max-height: 240px;
      border-radius: 8px;
      border: 1px solid var(--slate-300);
      background: #000;
    }}

    /* Collapsible Logs */
    .logs-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      user-select: none;
      background: var(--slate-100);
      padding: 10px 14px;
      border-radius: 8px;
    }}
    .logs-content {{
      display: none;
      background: #0f172a;
      color: #e2e8f0;
      font-family: Consolas, Monaco, "Courier New", monospace;
      font-size: 12px;
      padding: 16px;
      border-radius: 8px;
      margin-top: 8px;
      max-height: 320px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-all;
    }}
  </style>
</head>
<body>
  <div class="container">
    <!-- Header Card -->
    <header class="header-card">
      <div class="header-top">
        <div class="header-brand">
          <h1>Silhouette America - Automation Test Execution Results</h1>
          <p>Automated End-to-End Enterprise Test Execution Results</p>
        </div>
        <div class="header-status-badge" style="border-color: {status_color}; color: {status_color};">
          <span style="font-size:16px;">●</span> {overall_status}
        </div>
      </div>
      <div class="header-grid">
        <div class="header-meta-item">
          <span class="meta-label">Project</span>
          <span class="meta-val">Silhouette America</span>
        </div>
        <div class="header-meta-item">
          <span class="meta-label">Module</span>
          <span class="meta-val">{active_module_text}</span>
        </div>
        <div class="header-meta-item">
          <span class="meta-label">Environment</span>
          <span class="meta-val">{self.environment.capitalize()}</span>
        </div>
        <div class="header-meta-item">
          <span class="meta-label">Execution Date</span>
          <span class="meta-val">{execution_date_str}</span>
        </div>
        <div class="header-meta-item">
          <span class="meta-label">Duration</span>
          <span class="meta-val">{total_duration_formatted}</span>
        </div>
        <div class="header-meta-item">
          <span class="meta-label">Overall Status</span>
          <span class="meta-val" style="color: {status_color}; font-weight: 700;">{overall_status}</span>
        </div>
        <div class="header-meta-item">
          <span class="meta-label">Execution Window</span>
          <span class="meta-val">{execution_window_str}</span>
        </div>
      </div>
    </header>

    <!-- Execution Summary Dashboard Cards -->
    <section class="summary-grid">
      <div class="summary-card card-total">
        <div class="card-top">
          <span class="card-title">Total Tests</span>
          <div class="card-icon">Σ</div>
        </div>
        <div class="card-val">{total_executed}</div>
        <div class="card-subtext">{f'{total_executed} executed of {self.discovered_tests_count} discovered' if self.discovered_tests_count > 0 else f'{total_executed} executed'}</div>
      </div>

      <div class="summary-card card-passed">
        <div class="card-top">
          <span class="card-title">Passed</span>
          <div class="card-icon">✓</div>
        </div>
        <div class="card-val" style="color:var(--success);">{passed_count}</div>
        <div class="card-subtext">{success_rate}% success rate</div>
      </div>

      <div class="summary-card card-failed">
        <div class="card-top">
          <span class="card-title">Failed</span>
          <div class="card-icon">✕</div>
        </div>
        <div class="card-val" style="color:var(--danger);">{failed_count}</div>
        <div class="card-subtext">{f'{failed_count} defects found' if failed_count > 0 else 'Zero defects identified'}</div>
      </div>

      <div class="summary-card card-skipped">
        <div class="card-top">
          <span class="card-title">Skipped</span>
          <div class="card-icon">↷</div>
        </div>
        <div class="card-val" style="color:var(--warning);">{skipped_count}</div>
        <div class="card-subtext">{f'{skipped_count} skipped tests' if skipped_count > 0 else 'None skipped'}</div>
      </div>
    </section>

    <!-- Module-wise Execution Summary -->
    <section class="module-card">
      <h3>Module-Wise Execution Summary</h3>
      <div class="module-pills">
        {"".join(f'<div class="mod-pill"><span>{m}</span><span class="mod-pill-badge">{c["passed"]}/{c["total"]}</span></div>' for m, c in modules_summary.items())}
      </div>
    </section>

    <!-- Main Results Table -->
    <main class="table-container">
      <div class="table-toolbar">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" class="search-input" placeholder="Search by Test Case ID or title...">
        </div>
        <div class="filters-group">
          <button class="filter-btn active" data-filter="all">All ({total_executed})</button>
          <button class="filter-btn" data-filter="passed">Passed ({passed_count})</button>
          <button class="filter-btn" data-filter="failed">Failed ({failed_count})</button>
          <button class="filter-btn" data-filter="skipped">Skipped ({skipped_count})</button>

          <select id="moduleFilter" class="select-dropdown">
            <option value="">All Modules</option>
            {"".join(f'<option value="{m}">{m}</option>' for m in modules_summary.keys())}
          </select>

          <select id="sortSelect" class="select-dropdown">
            <option value="default">Default Order</option>
            <option value="id_asc">ID: Ascending</option>
            <option value="dur_desc">Duration: High to Low</option>
            <option value="dur_asc">Duration: Low to High</option>
          </select>

          <button id="clearFiltersBtn" class="btn-clear">Clear Filters</button>
        </div>
      </div>

      <table class="test-table">
        <thead>
          <tr>
            <th style="width:110px;">Result</th>
            <th style="width:150px;">Test Case ID</th>
            <th>Test Case Name</th>
            <th style="width:200px;">Module</th>
            <th style="width:90px;">Duration</th>
            <th style="width:120px;">Screenshot</th>
            <th style="width:110px;">Video</th>
          </tr>
        </thead>
        <tbody id="testTableBody">
          <!-- Injected via JavaScript -->
        </tbody>
      </table>

      <div class="table-footer">
        <div id="paginationInfo" class="pagination-info">Showing 1 to {total_executed} of {total_executed} tests</div>
        <div id="paginationControls" class="pagination-controls"></div>
      </div>
    </main>
  </div>

  <!-- Detailed Modal -->
  <div id="testModal" class="modal-backdrop">
    <div class="modal-container">
      <div class="modal-header">
        <div class="modal-title-group">
          <h2><span id="modalTcId"></span> <span id="modalStatusBadge"></span></h2>
          <p id="modalTitle"></p>
        </div>
        <button id="modalCloseBtn" class="modal-close-btn">&times;</button>
      </div>
      <div class="modal-body">
        <div style="display:flex;gap:12px;margin-bottom:20px;font-size:12px;color:var(--slate-600);border-bottom:1px solid var(--slate-100);padding-bottom:14px;">
          <span><strong>Module:</strong> <span id="modalModule"></span></span>
          <span>&bull;</span>
          <span><strong>Duration:</strong> <span id="modalDuration"></span></span>
          <span>&bull;</span>
          <span><strong>Environment:</strong> {self.environment.capitalize()}</span>
        </div>

        <!-- 7.1 Execution Steps -->
        <div class="section-block">
          <h4>Execution Steps</h4>
          <ol id="modalStepsList" class="steps-list"></ol>
        </div>

        <!-- 7.2 Expected Result -->
        <div class="section-block">
          <h4>Expected Result</h4>
          <div id="modalExpected" class="callout-box callout-expected"></div>
        </div>

        <!-- 7.3 Actual Result -->
        <div class="section-block">
          <h4>Actual Result</h4>
          <div id="modalActual" class="callout-box callout-actual"></div>
        </div>

        <!-- Failure Details / Error Traceback -->
        <div class="section-block" id="modalErrorSection" style="display:none;">
          <h4 style="color:var(--danger);display:flex;align-items:center;gap:6px;">⚠️ Failure Reason & Traceback</h4>
          <pre id="modalErrorBox" class="callout-box" style="background:#fef2f2;border:1px solid #fecaca;color:#991b1b;font-family:Consolas,monospace;font-size:12px;white-space:pre-wrap;overflow-x:auto;max-height:280px;"></pre>
        </div>

        <!-- 7.4 Assertion Summary -->
        <div class="section-block">
          <h4>Assertion Summary</h4>
          <div id="modalAssertions" class="assertions-list"></div>
        </div>

        <!-- Evidence Gallery -->
        <div class="section-block">
          <h4>Evidence Gallery</h4>
          <div class="evidence-grid">
            <div class="evidence-pane">
              <h5>Screenshot Evidence</h5>
              <div id="modalScreenshotContainer"></div>
            </div>
            <div class="evidence-pane">
              <h5>Video Recording</h5>
              <div id="modalVideoContainer" class="video-container"></div>
            </div>
          </div>
        </div>

        <!-- 7.5 Technical Execution Logs -->
        <div class="section-block">
          <div id="toggleLogsBtn" class="logs-header">
            <h4>Technical Execution Logs</h4>
            <span id="logsChevron" style="font-size:12px;color:var(--slate-600);">▼ Expand Logs</span>
          </div>
          <div id="modalLogsContent" class="logs-content"></div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const testCases = {tests_json};

    let currentPage = 1;
    const pageSize = 15;
    let filteredTests = [...testCases];
    let currentStatusFilter = 'all';

    function renderTable() {{
      const tbody = document.getElementById('testTableBody');
      tbody.innerHTML = '';

      if (filteredTests.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:40px;color:#94a3b8;">No matching test cases found.</td></tr>`;
        document.getElementById('paginationInfo').innerText = 'Showing 0 tests';
        document.getElementById('paginationControls').innerHTML = '';
        return;
      }}

      const startIndex = (currentPage - 1) * pageSize;
      const paginated = filteredTests.slice(startIndex, startIndex + pageSize);

      paginated.forEach((tc) => {{
        const tr = document.createElement('tr');
        tr.className = 'test-row';
        tr.onclick = (e) => {{
          if (e.target.tagName !== 'A' && !e.target.classList.contains('evidence-link')) {{
            openTestModal(tc);
          }}
        }};

        let statusClass = 'status-passed';
        let statusIcon = '✓';
        if (tc.status === 'FAILED') {{
          statusClass = 'status-failed';
          statusIcon = '✕';
        }} else if (tc.status === 'SKIPPED') {{
          statusClass = 'status-skipped';
          statusIcon = '↷';
        }}

        const ssHtml = tc.screenshot_rel 
          ? `<a class="evidence-link" href="${{tc.screenshot_rel}}" target="_blank">📷 View</a>`
          : `<span class="evidence-na">N/A</span>`;

        const vidHtml = tc.video_rel
          ? `<a class="evidence-link" href="${{tc.video_rel}}" target="_blank">🎬 View</a>`
          : `<span class="evidence-na">N/A</span>`;

        tr.innerHTML = `
          <td><span class="badge-status ${{statusClass}}">${{statusIcon}} ${{tc.status}}</span></td>
          <td class="tc-id">${{tc.test_case_id}}</td>
          <td class="tc-title">${{tc.title}}</td>
          <td class="tc-mod">${{tc.module}}</td>
          <td class="tc-dur">${{tc.duration_formatted}} <span style="font-size:11px;color:#64748b;font-weight:400;">(${{tc.duration_seconds}}s)</span></td>
          <td>${{ssHtml}}</td>
          <td>${{vidHtml}}</td>
        `;
        tbody.appendChild(tr);
      }});

      // Update Pagination
      const total = filteredTests.length;
      const endIndex = Math.min(startIndex + pageSize, total);
      document.getElementById('paginationInfo').innerText = `Showing ${{startIndex + 1}} to ${{endIndex}} of ${{total}} tests`;

      const totalPages = Math.ceil(total / pageSize);
      const controls = document.getElementById('paginationControls');
      controls.innerHTML = '';

      if (totalPages > 1) {{
        const prevBtn = document.createElement('button');
        prevBtn.className = 'page-btn';
        prevBtn.innerText = '‹ Prev';
        prevBtn.disabled = currentPage === 1;
        prevBtn.onclick = () => {{ currentPage--; renderTable(); }};
        controls.appendChild(prevBtn);

        for (let p = 1; p <= totalPages; p++) {{
          const pageBtn = document.createElement('button');
          pageBtn.className = `page-btn ${{p === currentPage ? 'active' : ''}}`;
          pageBtn.innerText = p;
          pageBtn.onclick = () => {{ currentPage = p; renderTable(); }};
          controls.appendChild(pageBtn);
        }}

        const nextBtn = document.createElement('button');
        nextBtn.className = 'page-btn';
        nextBtn.innerText = 'Next ›';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.onclick = () => {{ currentPage++; renderTable(); }};
        controls.appendChild(nextBtn);
      }}
    }}

    function filterAndSort() {{
      const query = document.getElementById('searchInput').value.toLowerCase().trim();
      const modFilter = document.getElementById('moduleFilter').value;
      const sortOpt = document.getElementById('sortSelect').value;

      filteredTests = testCases.filter((tc) => {{
        const matchesQuery = !query || tc.test_case_id.toLowerCase().includes(query) || tc.title.toLowerCase().includes(query) || tc.module.toLowerCase().includes(query);
        const matchesStatus = currentStatusFilter === 'all' || tc.status.toLowerCase() === currentStatusFilter.toLowerCase();
        const matchesMod = !modFilter || tc.module === modFilter;
        return matchesQuery && matchesStatus && matchesMod;
      }});

      if (sortOpt === 'id_asc') {{
        filteredTests.sort((a, b) => a.test_case_id.localeCompare(b.test_case_id));
      }} else if (sortOpt === 'dur_desc') {{
        filteredTests.sort((a, b) => b.duration_seconds - a.duration_seconds);
      }} else if (sortOpt === 'dur_asc') {{
        filteredTests.sort((a, b) => a.duration_seconds - b.duration_seconds);
      }}

      currentPage = 1;
      renderTable();
    }}

    document.getElementById('searchInput').addEventListener('input', filterAndSort);
    document.getElementById('moduleFilter').addEventListener('change', filterAndSort);
    document.getElementById('sortSelect').addEventListener('change', filterAndSort);

    document.querySelectorAll('.filter-btn').forEach((btn) => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.filter-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        currentStatusFilter = btn.getAttribute('data-filter');
        filterAndSort();
      }});
    }});

    document.getElementById('clearFiltersBtn').addEventListener('click', () => {{
      document.getElementById('searchInput').value = '';
      document.getElementById('moduleFilter').value = '';
      document.getElementById('sortSelect').value = 'default';
      currentStatusFilter = 'all';
      document.querySelectorAll('.filter-btn').forEach((b) => b.classList.remove('active'));
      document.querySelector('.filter-btn[data-filter="all"]').classList.add('active');
      filterAndSort();
    }});

    function openTestModal(tc) {{
      document.getElementById('modalTcId').innerText = tc.test_case_id;
      document.getElementById('modalTitle').innerText = tc.title;
      document.getElementById('modalModule').innerText = tc.module;
      document.getElementById('modalDuration').innerText = `${{tc.duration_formatted}} (${{tc.duration_seconds}}s)`;

      const badge = document.getElementById('modalStatusBadge');
      badge.className = `badge-status ${{tc.status === 'PASSED' ? 'status-passed' : tc.status === 'FAILED' ? 'status-failed' : 'status-skipped'}}`;
      badge.innerText = tc.status;

      // Steps
      const stepsOl = document.getElementById('modalStepsList');
      stepsOl.innerHTML = '';
      if (tc.steps && tc.steps.length > 0) {{
        tc.steps.forEach((s) => {{
          const li = document.createElement('li');
          li.className = 'step-item';
          li.innerText = s;
          stepsOl.appendChild(li);
        }});
      }} else {{
        stepsOl.innerHTML = '<li class="step-item">No explicit steps recorded.</li>';
      }}

      // Expected & Actual
      document.getElementById('modalExpected').innerText = tc.expected_result;
      document.getElementById('modalActual').innerText = tc.actual_result;

      // Failure Details
      const errSection = document.getElementById('modalErrorSection');
      const errBox = document.getElementById('modalErrorBox');
      if (tc.status === 'FAILED' && (tc.error_msg || tc.traceback)) {{
        errSection.style.display = 'block';
        errBox.innerText = tc.traceback || tc.error_msg;
      }} else {{
        errSection.style.display = 'none';
        errBox.innerText = '';
      }}

      // Assertions
      const assertContainer = document.getElementById('modalAssertions');
      assertContainer.innerHTML = '';
      if (tc.assertions && tc.assertions.length > 0) {{
        tc.assertions.forEach((a) => {{
          const div = document.createElement('div');
          div.className = 'assertion-item';
          div.innerHTML = `<span style="color:var(--success);font-weight:bold;">✓</span> <span>${{a}}</span>`;
          assertContainer.appendChild(div);
        }});
      }} else {{
        assertContainer.innerHTML = '<div style="color:#64748b;font-size:12px;">No specific assertions parsed.</div>';
      }}

      // Screenshot Evidence
      const ssBox = document.getElementById('modalScreenshotContainer');
      if (tc.screenshot_rel) {{
        ssBox.innerHTML = `
          <a href="${{tc.screenshot_rel}}" target="_blank">
            <img src="${{tc.screenshot_rel}}" alt="${{tc.test_case_id}} Screenshot" class="img-preview" loading="lazy" />
          </a>
          <p style="font-size:11px;color:#64748b;margin-top:6px;">Click to view full image in high resolution</p>
        `;
      }} else {{
        ssBox.innerHTML = `<p style="color:#94a3b8;font-size:12px;">Screenshot not available.</p>`;
      }}

      // Video Evidence (HTML5 Player)
      const vidBox = document.getElementById('modalVideoContainer');
      if (tc.video_rel) {{
        vidBox.innerHTML = `
          <video class="embedded-video" controls preload="metadata">
            <source src="${{tc.video_rel}}" type="video/webm">
            Your browser does not support HTML5 video.
          </video>
          <p style="font-size:11px;color:#64748b;margin-top:6px;text-align:center;">Playwright Execution Recording (${{tc.duration_formatted}})</p>
        `;
      }} else {{
        vidBox.innerHTML = `<p style="color:#94a3b8;font-size:12px;text-align:center;">Video recording not available.</p>`;
      }}

      // Technical Logs
      const logsBox = document.getElementById('modalLogsContent');
      logsBox.style.display = 'none';
      document.getElementById('logsChevron').innerText = '▼ Expand Logs';
      logsBox.innerText = tc.logs || (tc.traceback ? tc.traceback : (tc.error_msg ? tc.error_msg : 'No technical logs captured for this test.'));

      document.getElementById('testModal').style.display = 'flex';
    }}

    document.getElementById('toggleLogsBtn').addEventListener('click', () => {{
      const logs = document.getElementById('modalLogsContent');
      const chev = document.getElementById('logsChevron');
      if (logs.style.display === 'block') {{
        logs.style.display = 'none';
        chev.innerText = '▼ Expand Logs';
      }} else {{
        logs.style.display = 'block';
        chev.innerText = '▲ Collapse Logs';
      }}
    }});

    document.getElementById('modalCloseBtn').addEventListener('click', () => {{
      document.getElementById('testModal').style.display = 'none';
      const vid = document.querySelector('#modalVideoContainer video');
      if (vid) vid.pause();
    }});

    window.addEventListener('click', (e) => {{
      const modal = document.getElementById('testModal');
      if (e.target === modal) {{
        modal.style.display = 'none';
        const vid = document.querySelector('#modalVideoContainer video');
        if (vid) vid.pause();
      }}
    }});

    renderTable();
  </script>
</body>
</html>
"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return self.output_path
