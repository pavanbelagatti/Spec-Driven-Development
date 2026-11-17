"""Approval-first feature builder for the existing spec-coding-assistant.
WARNING: approved local tests execute untrusted AI code; not a security sandbox.
"""
import ast
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
APP = ROOT / 'workspace' / 'app.py'
BASE_SPEC = ROOT / 'specs' / 'url_shortener.md'
JOBS = ROOT / 'feature_jobs'
JOBS.mkdir(exist_ok=True)


def job_path(job):
    if not re.fullmatch(r'[0-9a-f]{32}', job):
        raise ValueError('Invalid job identifier')
    return JOBS / job


def read(job):
    return json.loads((job_path(job) / 'state.json').read_text())


def update(job, **changes):
    data = read(job)
    data.update(changes)
    (job_path(job) / 'state.json').write_text(json.dumps(data, indent=2))
    return data


def ask(system, user):
    load_dotenv(ROOT / '.env')
    if not os.getenv('OPENAI_API_KEY'):
        raise RuntimeError('OPENAI_API_KEY missing from .env')
    result = OpenAI().chat.completions.create(
        model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'),
        messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
        response_format={'type': 'json_object'}, temperature=0,
    )
    return json.loads(result.choices[0].message.content)



def normalize_testclient_redirects(source):
    """Correct a known httpx/TestClient API mismatch, not test expectations."""
    return re.sub(r'\ballow_redirects\s*=', 'follow_redirects=', source)


def list_jobs(limit=25):
    """Explicitly opt in to resuming a previous job; never auto-restore it."""
    jobs = []
    for state_file in sorted(JOBS.glob('*/state.json'), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            state = json.loads(state_file.read_text())
            if state.get('status') not in ('rejected',):
                jobs.append(state)
        except (OSError, ValueError, KeyError):
            pass
        if len(jobs) >= limit:
            break
    return jobs


def result_summary(job):
    output_path = job_path(job) / 'test_output.txt'
    output = output_path.read_text(errors='replace') if output_path.exists() else ''
    matches = re.findall(r'(?:(\d+) passed|(?:\d+) failed|(?:\d+) error)', output)
    summary = next((line.strip() for line in reversed(output.splitlines())
                    if re.search(r'\b(?:passed|failed|error|errors)\b', line)
                    and (' in ' in line or '===' in line)), 'No test summary available')
    failures = [line.strip() for line in output.splitlines() if line.startswith('FAILED ') or line.startswith('ERROR ')]
    return {'summary': summary, 'failures': failures, 'output': output}


def _propose_test_fix(job, revised, explanation, kind):
    """Stage a test correction for human approval; never silently change approved tests."""
    folder = job_path(job)
    original = (folder / 'test_feature.py').read_text()
    ast.parse(revised)
    if revised == original:
        raise ValueError('No test correction was proposed')
    if len(revised) > 50000:
        raise ValueError('Proposed tests are too large')
    # The correction must retain the same test functions and parameterization.
    def tests_in(source):
        tree = ast.parse(source)
        return sorted(node.name for node in ast.walk(tree)
                      if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and node.name.startswith('test_'))
    if tests_in(revised) != tests_in(original):
        raise ValueError('The proposed correction adds or removes test functions')
    (folder / 'proposed_tests.py').write_text(revised)
    diff = ''.join(difflib.unified_diff(original.splitlines(True), revised.splitlines(True),
                    fromfile='approved_tests.py', tofile='proposed_tests.py'))
    (folder / 'test_fix.diff').write_text(diff)
    update(job, status='test_fix_review', repair_kind=kind, repair_note=explanation,
           repair_attempts=read(job).get('repair_attempts', 0) + 1)
    return 'test_fix_review'


def approve_test_fix(job):
    if read(job)['status'] != 'test_fix_review':
        raise ValueError('There is no proposed test correction to approve')
    folder = job_path(job)
    revised = (folder / 'proposed_tests.py').read_text()
    ast.parse(revised)
    (folder / 'test_feature.py').write_text(revised)
    update(job, status='code_review', repair_note=(
        'You approved a correction to the generated tests. The application code has not changed. '
        'Authorize another test run to verify the result.'), repair_kind='test_fix_approved')


def reject_test_fix(job):
    if read(job)['status'] != 'test_fix_review':
        raise ValueError('No test correction is awaiting review')
    update(job, status='failed', repair_note='Proposed test correction rejected; no tests were changed.')


def prepare_repair(job):
    """Diagnose failures and stage a test fix OR revised code; never run or apply automatically."""
    state = read(job)
    if state['status'] != 'failed':
        raise ValueError('Only failed validations can be diagnosed')
    folder = job_path(job)
    output = result_summary(job)['output']
    tests = (folder / 'test_feature.py').read_text()
    corrected = normalize_testclient_redirects(tests)
    if corrected != tests:
        return _propose_test_fix(job, corrected,
            'The generated tests used allow_redirects, which is not supported by this HTTPX version. '
            'The proposed correction uses follow_redirects. No assertions are changed.',
            'test_compatibility')

    # A missing URL path segment cannot match /{alias}; 404 is the correct route-level response.
    empty_alias_failure = (re.search(r'test_alias_invalid_format_returns_422\[\]', output)
                           and re.search(r'assert 404 == 422', output))
    if empty_alias_failure and 'invalid_alias == ""' not in tests:
        # Only touch the assertion inside the exact affected test function.
        pattern = (r'(def test_alias_invalid_format_returns_422\(self, invalid_alias\):'
                   r'(?:(?!\n    def |\nclass ).)*?)'
                   r'assert response\.status_code == 422')
        revised, count = re.subn(pattern,
            lambda m: m.group(1) + 'assert response.status_code == (404 if invalid_alias == "" else 422)',
            tests, count=1, flags=re.S)
        if count:
            return _propose_test_fix(job, revised,
                'The test sends an empty alias as /api/alias-available/. That URL is missing '
                'the required path segment, so FastAPI returns 404 before alias validation. '
                'The proposed correction expects 404 only for the empty path, while keeping '
                '422 for nonempty invalid aliases. All other tests remain unchanged.',
                'missing_path_segment')

    # Use the reviewer to explain the failure. If it identifies a test problem,
    # propose a reviewable correction instead of repeatedly rewriting application code.
    diagnosis = ask(
        'You are a test-failure investigator. Respond with JSON keys category '
        '(one of "test" or "implementation"), cause, explanation, suggested_fix. '
        'Explain in everyday English. Identify invalid test assumptions distinctly '
        'from actual application defects. Do not weaken legitimate requirements.',
        'Approved specification:\n' + (folder / 'feature.md').read_text()[:10000] +
        '\nApproved tests:\n' + tests[:18000] +
        '\nCandidate implementation:\n' + (folder / 'candidate.py').read_text()[:24000] +
        '\nFailure output:\n' + output[-12000:])
    explanation = str(diagnosis.get('explanation') or diagnosis.get('cause') or 'The tests failed.')[:1400]
    suggestion = str(diagnosis.get('suggested_fix') or '')[:1200]
    if diagnosis.get('category') == 'test':
        payload = ask(
            'Return JSON with key tests containing the COMPLETE corrected pytest source. '
            'Fix only the demonstrably incorrect test assumption described. Preserve all '
            'test functions, valid assertions, requirements, and coverage. Do not delete tests. '
            'No filesystem/network access or shell commands.',
            'Original approved tests:\n' + tests[:24000] +
            '\nFailure output:\n' + output[-12000:] +
            '\nDiagnosis:\n' + explanation + '\nSuggested correction:\n' + suggestion)
        return _propose_test_fix(job, payload['tests'],
            explanation + '\nSuggested test correction: ' + suggestion,
            'ai_test_correction')
    feedback = ('Validation failed. Root cause: ' + explanation +
                '\nFix required: ' + suggestion +
                '\nDo not change the approved tests. Preserve existing features. '
                'Register specific FastAPI routes before dynamic /{code} routes.')
    generate_code(job, feedback)
    update(job, repair_note=(explanation + '\nProposed implementation fix: ' + suggestion +
                             '\nReview the revised code, then authorize a new test run.'),
           repair_kind='implementation',
           repair_attempts=state.get('repair_attempts', 0) + 1)
    return 'implementation'

def create(request):
    request = request.strip()
    if len(request) < 20 or len(request) > 3000:
        raise ValueError('Enter a feature request between 20 and 3000 characters')
    job = uuid.uuid4().hex
    folder = job_path(job)
    folder.mkdir()
    (folder / 'state.json').write_text(json.dumps({
        'job': job, 'request': request, 'status': 'generating_spec',
        'created': datetime.now(timezone.utc).isoformat(), 'revision': 0,
    }, indent=2))
    try:
        payload = ask(
            'You are a specification engineer. Return JSON with exactly two strings: '
            'spec (Markdown requirements, API behavior, compatibility and edge cases) and '
            'tests (complete pytest Python source with FastAPI TestClient tests). '
            'Tests must import `from workspace.app import app`. No shell, file writes, '
            'network calls or external services in generated tests. Keep baseline behavior.',
            'Existing specification:\n' + BASE_SPEC.read_text()[:16000] +
            '\nCurrent application:\n' + APP.read_text()[:24000] +
            '\nRequested change:\n' + request,
        )
        spec, tests = payload['spec'], payload['tests']
        if not isinstance(spec, str) or not isinstance(tests, str):
            raise ValueError('Invalid OpenAI response')
        tests = normalize_testclient_redirects(tests)
        ast.parse(tests)
        (folder / 'feature.md').write_text(spec)
        (folder / 'test_feature.py').write_text(tests)
        update(job, status='spec_review')
    except Exception as exc:
        update(job, status='error', error=str(exc))
        raise
    return job


def save_spec(job, spec, tests):
    if read(job)['status'] != 'spec_review':
        raise ValueError('Specification is not awaiting review')
    tests = normalize_testclient_redirects(tests)
    ast.parse(tests)
    folder = job_path(job)
    (folder / 'feature.md').write_text(spec)
    (folder / 'test_feature.py').write_text(tests)


def generate_code(job, feedback=None):
    """Generate or revise a candidate without changing approved specs/tests.

    Regeneration is allowed at code review or after failed tests. Existing
    candidate files are retained if the model request fails.
    """
    state = read(job)
    current_status = state['status']
    if current_status not in ('spec_review', 'code_review', 'failed'):
        raise ValueError('Code generation is not available at this stage')
    feedback = (feedback or '').strip()
    if current_status != 'spec_review' and not feedback:
        raise ValueError('Please enter feedback describing what to improve')
    if len(feedback) > 5000:
        raise ValueError('Feedback must be 5000 characters or fewer')

    folder = job_path(job)
    original = (folder / 'original.py').read_text() if (folder / 'original.py').exists() else APP.read_text()
    previous_code = (folder / 'candidate.py').read_text() if (folder / 'candidate.py').exists() else None
    if not (folder / 'original.py').exists():
        (folder / 'original.py').write_text(original)

    update(job, status='generating_code')
    try:
        prompt = (
            'Existing specification:\n' + BASE_SPEC.read_text()[:16000] +
            '\nApproved new specification:\n' + (folder / 'feature.md').read_text() +
            '\nApproved new tests:\n' + (folder / 'test_feature.py').read_text()[:18000] +
            '\nOriginal application (the replacement must preserve its behavior):\n' + original[:28000]
        )
        if previous_code is not None and feedback:
            prompt += (
                '\nPREVIOUS PROPOSED IMPLEMENTATION (revise this, do not merely repeat it):\n' +
                previous_code[:28000] +
                '\nHUMAN REVIEWER FEEDBACK (address every issue):\n' + feedback
            )
            if (folder / 'test_output.txt').exists() and current_status == 'failed':
                prompt += '\nPREVIOUS TEST FAILURES:\n' + (folder / 'test_output.txt').read_text()[-10000:]
        payload = ask(
            'You are a careful FastAPI developer. Return a JSON object with keys '
            '`plan` and `code`, both strings. `code` must be the COMPLETE replacement '
            'workspace/app.py, not a diff. Preserve baseline behavior and satisfy new '
            'requirements and reviewer feedback. Use only FastAPI, Pydantic and standard '
            'library. No filesystem access, subprocesses, network calls, eval, exec or '
            'dynamic imports. Keep duplicate checking, short-code allocation and store '
            'insertion atomic under the same lock; never use placeholder entries.',
            prompt,
        )
        code = payload['code']
        if not isinstance(code, str) or not 0 < len(code) <= 50000:
            raise ValueError('Invalid generated code')
        ast.parse(code)
        diff = ''.join(difflib.unified_diff(
            original.splitlines(keepends=True), code.splitlines(keepends=True),
            fromfile='current/app.py', tofile='proposed/app.py'))
        # Write only after a complete, syntactically valid response is available.
        (folder / 'candidate.py').write_text(code)
        (folder / 'plan.md').write_text(str(payload.get('plan', '')))
        (folder / 'changes.diff').write_text(diff)
        if feedback:
            history = state.get('feedback_history', [])
            history.append({'feedback': feedback, 'at': datetime.now(timezone.utc).isoformat()})
            update(job, feedback_history=history, revision=len(history), status='code_review', error=None, repair_note=None)
        else:
            update(job, status='code_review', error=None, repair_note=None)
    except Exception as exc:
        # Keep the previous proposal available for review if regeneration fails.
        fallback = current_status if current_status in ('code_review', 'failed') else 'error'
        update(job, status=fallback, error=str(exc))
        raise


def latest_unfinished_job():
    """Restore the latest in-progress review after Streamlit restarts."""
    candidates = sorted(JOBS.glob('*/state.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    for state_file in candidates:
        try:
            state = json.loads(state_file.read_text())
            if state.get('status') in ('spec_review', 'code_review', 'failed', 'validated'):
                return state['job']
        except (OSError, ValueError, KeyError):
            continue
    return None


def validate(job):
    """Only call after user has explicitly reviewed and authorized execution."""
    if read(job)['status'] != 'code_review':
        raise ValueError('Review and authorize generated code first')
    folder = job_path(job)
    update(job, status='testing')
    try:
        with tempfile.TemporaryDirectory(prefix='linkforge-review-') as tmp:
            staging = Path(tmp)
            (staging / 'workspace').mkdir()
            (staging / 'workspace' / '__init__.py').write_text('')
            (staging / 'workspace' / 'app.py').write_text((folder / 'candidate.py').read_text())
            (staging / 'tests').mkdir()
            (staging / 'tests' / 'test_feature.py').write_text((folder / 'test_feature.py').read_text())
            shutil.copy2(ROOT / 'tests' / 'test_acceptance.py', staging / 'tests' / 'test_acceptance.py')
            for previous in sorted((ROOT / 'tests').glob('test_feature_*.py')):
                shutil.copy2(previous, staging / 'tests' / previous.name)
            # Removes common secrets from child environment, but is NOT an isolation boundary.
            env = {k: v for k, v in os.environ.items() if not any(
                marker in k.upper() for marker in ('KEY', 'TOKEN', 'SECRET', 'PASSWORD', 'PORT_', 'OPENAI'))}
            env.update({'PYTHONPATH': str(staging), 'PYTHONDONTWRITEBYTECODE': '1',
                        'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1'})
            process = subprocess.run(
                [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'tests'],
                cwd=staging, env=env, capture_output=True, text=True, timeout=90,
            )
            output = (process.stdout + '\n' + process.stderr)[-16000:]
            (folder / 'test_output.txt').write_text(output)
            update(job, status='validated' if process.returncode == 0 else 'failed', repair_note=None)
    except subprocess.TimeoutExpired:
        (folder / 'test_output.txt').write_text('Tests timed out after 90 seconds')
        update(job, status='failed')
    except Exception as exc:
        update(job, status='error', error=str(exc))
        raise


def apply(job):
    if read(job)['status'] != 'validated':
        raise ValueError('Tests must pass before applying')
    folder = job_path(job)
    original = (folder / 'original.py').read_text()
    if APP.read_text() != original:
        raise RuntimeError('Application changed since generation; refusing to overwrite')
    backup = folder / 'app_before_apply.py'
    backup.write_text(original)
    APP.write_text((folder / 'candidate.py').read_text())
    # Store approved spec and tests for future reference, without overwriting baseline.
    (ROOT / 'specs' / ('feature_' + job[:8] + '.md')).write_text((folder / 'feature.md').read_text())
    (ROOT / 'tests' / ('test_feature_' + job[:8] + '.py')).write_text((folder / 'test_feature.py').read_text())
    update(job, status='applied')


def reject(job):
    if read(job)['status'] == 'applied':
        raise ValueError('Already applied')
    update(job, status='rejected')