# LinkForge — AI-Assisted Spec-Driven Development

LinkForge is a beginner-friendly, hands-on project that demonstrates how **Spec-Driven Development (SDD)** works using OpenAI, Python, FastAPI, pytest, and Streamlit.

Instead of asking AI to write code immediately, we start with a clear feature request, generate a specification and acceptance tests, and then use AI to implement and validate the feature.

The goal is to demonstrate how developers can combine AI-generated code with structured specifications, automated testing, and human approvals.

## How It Works

1. **Feature Request:** Describe the feature you want to build in plain English.
2. **Generate Specification & Tests:** OpenAI generates the feature specification and acceptance tests.
3. **Human Approval:** Review and approve the proposed specification before proceeding.
4. **Generate Implementation:** OpenAI generates the Python code required to implement the feature.
5. **Review & Run Tests:** Review the proposed changes and authorize local test execution using pytest.
6. **Diagnose & Fix:** If tests fail, AI analyzes the failures and proposes corrections to the implementation or tests. Test changes require explicit approval.
7. **Apply Feature:** Once the tests pass, review and approve applying the implementation to the application.
8. **Try & Verify:** Test the newly implemented feature directly from the LinkForge interface.

## Tech Stack

- **OpenAI API:** Specification generation, acceptance-test generation, code generation, and failure diagnosis.
- **Python:** Core application and workflow orchestration.
- **FastAPI:** Backend application for the URL shortener.
- **Streamlit:** Interactive LinkForge interface.
- **pytest:** Acceptance and regression testing.

## Project Structure

| File / Folder | Description |
|---|---|
| `specs/` | Project specifications and requirements |
| `tests/` | Acceptance and regression tests |
| `workspace/` | FastAPI application and implemented features |
| `feature_jobs/` | Local generated feature jobs and workflow history |
| `templates/` | Project templates |
| `feature_builder.py` | AI-assisted feature generation and validation workflow |
| `assistant.py` | Original specification-based coding assistant |
| `ui.py` | Streamlit interface |
| `port_integration.py` | Optional Port integration |
| `.env` | Local environment variables and API credentials |
| `.env.example` | Example environment configuration |
| `requirements.txt` | Python dependencies |

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/pavanbelagatti/Spec-Driven-Development.git
cd Spec-Driven-Development
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure OpenAI

Create a `.env` file in the project root and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Keep this file private. Never commit API keys or other credentials to GitHub.

### 5. Start the FastAPI Backend

Open a terminal and run:

```bash
source .venv/bin/activate
uvicorn workspace.app:app --reload --port 8000
```

FastAPI will run at:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

### 6. Start LinkForge

Open another terminal in the same project directory and run:

```bash
source .venv/bin/activate
streamlit run ui.py
```

Open LinkForge in your browser:

http://localhost:8501

## Try the Spec-Driven Development Workflow

Once LinkForge is running:

1. Open the **Feature Studio**.
2. Select an example feature or enter your own feature request.
3. Generate and review the specification and acceptance tests.
4. Approve the specification and generate the implementation.
5. Review the proposed changes and authorize test execution.
6. Inspect the results and review any AI-proposed fixes.
7. Approve applying the feature once validation succeeds.
8. Open **Try Your Feature** to verify the new functionality.

### Example: URL Click Statistics

Suppose you want to add a feature that tracks how many times a shortened URL has been visited.

You can request:

> Add an API endpoint that returns the original URL and the number of times a short URL has been visited. Checking the statistics should not increase the click count.

LinkForge generates the specification, tests, and implementation for the feature.

After validation and approval, you can test the endpoint:

```http
GET /api/stats/{code}
```

The response includes the short URL code, original URL, and click count.

## Human-in-the-Loop Development

LinkForge is not designed to blindly accept AI-generated code.

Developers remain responsible for reviewing specifications, approving implementation changes, authorizing tests, and deciding when a feature should be applied.

The workflow also distinguishes between failures caused by incorrect application code and failures caused by incorrect generated tests.

**The specification guides the implementation, tests validate the requirements, and humans control critical decisions.**

## Important Security Notes

This project is intended for local learning and demonstration.

- Generated Python tests run locally with your user account's permissions.
- Test execution is not isolated in a secure sandbox.
- Do not run untrusted generated code in an environment containing sensitive files or credentials.
- Do not expose the Streamlit interface publicly.
- Review AI-generated changes carefully, particularly modifications to acceptance tests.
- Passing tests does not guarantee that generated code is correct or secure.

For safer experimentation, use a disposable, isolated development environment.

## About This Project

This tutorial demonstrates how Spec-Driven Development can bring more structure to AI-assisted software engineering.

Rather than relying entirely on repeated prompting, developers can define requirements, validate generated implementations against acceptance tests, and maintain human oversight throughout the development lifecycle.

**Built as a hands-on educational project for developers exploring AI-assisted software development and Spec-Driven Development.**
