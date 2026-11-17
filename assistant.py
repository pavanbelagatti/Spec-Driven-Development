
"""Spec-driven mini coding assistant.

Reads specs/url_shortener.md, generates workspace/app.py,
runs acceptance tests, and retries failed implementations.

WARNING: Generated code is executed during testing.
Use only in an isolated, disposable development environment.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from dotenv import load_dotenv
from openai import OpenAI
from port_integration import report_to_port


ROOT = Path(__file__).resolve().parent

SPEC = ROOT / "specs" / "url_shortener.md"
TARGET = ROOT / "workspace" / "app.py"
REPORT = ROOT / "workspace" / "validation_report.json"
PLAN = ROOT / "workspace" / "implementation_plan.md"

MAX_OUTPUT = 14000


SYSTEM = """
You are a careful Python software engineer implementing a specification.

Return a JSON object only, with exactly two keys:
- "plan": implementation plan as a string
- "code": complete Python source code as a string

The code must be runnable Python for workspace/app.py.

Rules:
- Use FastAPI and the Python standard library.
- Follow every requirement in the specification.
- Preserve existing behavior when adding new features.
- Do not modify acceptance tests.
- Do not write to other files.
- Do not use subprocesses, shell calls, network requests,
  eval, or exec.
- Prefer simple, maintainable implementations.
"""


def generate(client, model, spec, previous_code="", failure=""):
    """Generate or repair code using OpenAI."""

    user = f"SPECIFICATION:\n{spec}\n"

    if previous_code:
        user += (
            "\nCURRENT IMPLEMENTATION:\n"
            f"{previous_code[:MAX_OUTPUT]}\n"
        )

    if failure:
        user += (
            "\nTEST FAILURES:\n"
            f"{failure[-MAX_OUTPUT:]}\n"
            "Fix the implementation while preserving passing behavior."
        )
    elif previous_code:
        user += (
            "\nUpdate the existing implementation to satisfy the "
            "specification while preserving working functionality."
        )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    payload = json.loads(response.choices[0].message.content)

    if not isinstance(payload.get("plan"), str):
        raise ValueError("Model did not return a valid plan")

    if not isinstance(payload.get("code"), str):
        raise ValueError("Model did not return valid code")

    return payload


def test():
    """Execute the human-authored acceptance tests."""

    try:
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_acceptance.py",
                "-q",
                "--tb=short",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=45,
            env={
                **os.environ,
                "PYTHONDONTWRITEBYTECODE": "1",
            },
        )

        output = (
            process.stdout + "\n" + process.stderr
        )[-MAX_OUTPUT:]

        return process.returncode == 0, output

    except subprocess.TimeoutExpired:
        return False, "pytest timed out after 45 seconds"


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--report-port",
        action="store_true",
        help="Update Port if configured",
    )

    args = parser.parse_args()

    if not 1 <= args.max_attempts <= 5:
        parser.error("--max-attempts must be between 1 and 5")

    load_dotenv(ROOT / ".env")

    if not os.getenv("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY in .env")

    client = OpenAI()

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-4.1-mini",
    )

    spec = SPEC.read_text(encoding="utf-8")

    TARGET.parent.mkdir(parents=True, exist_ok=True)

    # Read the existing application before making changes.
    code = (
        TARGET.read_text(encoding="utf-8")
        if TARGET.exists()
        else ""
    )

    failure = ""
    passed = False

    for attempt in range(1, args.max_attempts + 1):
        print(
            f"\n=== Attempt {attempt}/{args.max_attempts} ===",
            flush=True,
        )

        print("Reading specification and generating code...")

        result = generate(
            client,
            model,
            spec,
            previous_code=code,
            failure=failure,
        )

        new_code = result["code"]

        if new_code.startswith("```"):
            new_code = (
                new_code.split("\n", 1)[1]
                .rsplit("```", 1)[0]
            )

        # Syntax check only, not a security sandbox.
        compile(new_code, str(TARGET), "exec")

        code = new_code

        TARGET.write_text(code, encoding="utf-8")

        PLAN.write_text(
            result["plan"] + "\n",
            encoding="utf-8",
        )

        print("Generated workspace/app.py")
        print("Running acceptance tests...")

        passed, failure = test()

        print(failure, flush=True)

        if passed:
            print("All acceptance tests passed!")
            break

        print("Tests failed. Asking OpenAI to repair the code...")

    status = "PASS" if passed else "FAIL"

    report = {
        "status": status,
        "attempts": attempt,
        "model": model,
        "spec": str(SPEC.relative_to(ROOT)),
        "test_output": failure,
    }

    REPORT.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(
        f"\nFinal result: {status}\n"
        "Report: workspace/validation_report.json"
    )

    if args.report_port:
        try:
            report_to_port(status, failure)
        except Exception as exc:
            print(
                "Port reporting failed "
                f"(local result retained): {exc}"
            )

    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()