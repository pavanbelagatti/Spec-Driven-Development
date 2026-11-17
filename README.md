LinkForge Feature Studio — beginner-friendly demo update

REPLACE THESE TWO FILES in your existing spec-coding-assistant project:
  ui.py
  feature_builder.py

Keep your existing workspace/app.py, .env, specs/, tests/, and feature_jobs/.
Do NOT delete or overwrite any of those folders or files.

INSTALL
1. Stop Streamlit with Control+C in its terminal.
2. Back up your current ui.py and feature_builder.py.
3. Extract this ZIP and copy the two replacement Python files to your project root.
4. Restart Streamlit:
   source .venv/bin/activate
   streamlit run ui.py
5. In a separate terminal, if FastAPI is not already running:
   source .venv/bin/activate
   uvicorn workspace.app:app --reload --port 8000
6. Open http://localhost:8501

WHAT CHANGED
- Cleaner Feature Studio, larger headings, guided progress, and dark hover/expander styling.
- Removed the expandable Safety information section; a brief warning remains at the local test authorization step.
- Removed technical/non-technical labels from expandable sections.
- Fresh feature selection by default, with optional Resume earlier feature.
- Ten feature examples, with neutral labels and no success/failure promises.
- Readable failure summaries; technical logs in expandable code block.
- Diagnosis distinguishes incorrect generated tests from incorrect application code.
- Known 404-vs-422 empty-path case proposes a focused test correction.
- Generated test corrections are shown as a diff and REQUIRE explicit approval.
- AI can propose other test corrections or code revisions. Approval is required.
- Tests are rerun only after you authorize local execution; applying code also requires approval.
- Regression testing includes the baseline and earlier applied feature tests.
- New Try Your Feature tab lists API endpoints from local FastAPI and shows responses.

IMPORTANT
This is NOT an isolated sandbox. Generated Python tests run with your Mac account permissions.
Use only in a disposable environment without private files or credentials.
Never expose this UI publicly. Do not blindly approve AI changes to tests.
AI diagnosis and generated code can still be wrong; tests cannot guarantee correctness.
This update was syntax checked and the known test-correction workflow was smoke-tested;
not end-to-end tested on your Mac.