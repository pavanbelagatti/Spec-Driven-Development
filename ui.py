
import os
import re
import json
from datetime import datetime
from urllib.parse import urlparse

import requests
import streamlit as st

# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="LinkForge | Feature Studio",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_URL = os.getenv(
    "SHORTENER_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

ALIAS_PATTERN = re.compile(r"^[a-z0-9-]+$")


# --------------------------------------------------
# STYLING
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, .stApp {
    font-family: 'DM Sans', sans-serif;
    background: #0b111b;
    color: #eef3f9;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 70% 50% at 70% -10%,
        #172b40 0%, transparent 75%), #0b111b !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background: transparent !important;
}

.block-container {
    max-width: 1100px;
    padding-top: 1.2rem !important;
    padding-bottom: 3rem !important;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.6px;
}

.brand {
    font: 700 26px 'Space Grotesk', sans-serif;
    letter-spacing: -1px;
}

.brand b {
    color: #61e7c5;
}

.hero {
    font: 700 clamp(38px, 5vw, 60px)/1.1
        'Space Grotesk', sans-serif;
    letter-spacing: -2px;
    margin: 15px 0;
}

.hero em {
    color: #61e7c5;
    font-style: normal;
}

.sub {
    color: #b3c3d4;
    font-size: 17px;
    line-height: 1.7;
    margin-bottom: 25px;
}

.eyebrow {
    color: #61e7c5;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 35px;
}

.stagebar {
    background: #142131;
    border: 1px solid #304258;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 15px 0;
    color: #eaf2fa;
}

.stagebar b {
    color: #75edcf;
}

.pill {
    display: inline-block;
    background: #193b36;
    color: #79f3d4;
    border: 1px solid #2b6a5b;
    border-radius: 30px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}

[data-testid="stWidgetLabel"] p,
[data-testid="stCaptionContainer"] p {
    color: #dce8f5 !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background: #eef2f7 !important;
    color: #182431 !important;
    border-radius: 10px !important;
    -webkit-text-fill-color: #182431 !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #718095 !important;
    opacity: 1 !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #eef2f7 !important;
    color: #182431 !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] * {
    color: #182431 !important;
}

.stButton > button,
.stFormSubmitButton > button {
    background: #172738 !important;
    color: #f0f6fc !important;
    border: 1px solid #496078 !important;
    border-radius: 10px !important;
    min-height: 48px !important;
    font-weight: 700 !important;
}

.stButton > button *,
.stFormSubmitButton > button * {
    color: inherit !important;
}

.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
    background: #61e7c5 !important;
    color: #092b27 !important;
    border-color: #61e7c5 !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #244457 !important;
    color: #ffffff !important;
    border-color: #61e7c5 !important;
}

.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {
    background: #78efd3 !important;
    color: #092b27 !important;
}

.stButton > button:disabled,
.stFormSubmitButton > button:disabled {
    opacity: 0.55 !important;
}

[data-testid="stTabs"] button,
[data-testid="stTabs"] button:hover,
[data-testid="stTabs"] button:focus {
    background: #142131 !important;
    color: #eaf2fa !important;
    border-radius: 10px 10px 0 0 !important;
}

[data-testid="stTabs"] button *,
[data-testid="stTabs"] button:hover * {
    color: #eaf2fa !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    background: #193b36 !important;
}

[data-testid="stTabs"] button[aria-selected="true"] * {
    color: #77f1d3 !important;
}

[data-testid="stExpander"],
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary:hover,
[data-testid="stExpander"] summary:focus {
    background: #142131 !important;
    color: #f1f6fc !important;
    border-radius: 10px !important;
}

[data-testid="stExpander"] summary *,
[data-testid="stExpander"] summary:hover * {
    color: #f1f6fc !important;
}

[data-testid="stExpanderDetails"] {
    background: #0e1927 !important;
    color: #eaf2fa !important;
}

[data-testid="stTextArea"] textarea:disabled {
    background: #142131 !important;
    color: #f1f6fc !important;
    -webkit-text-fill-color: #f1f6fc !important;
}

[data-testid="stAlert"] {
    background: #132438 !important;
    border: 1px solid #30465d !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: #e3eef9 !important;
}

[data-testid="stMetric"] {
    background: #131f2d;
    border: 1px solid #293849;
    border-radius: 14px;
    padding: 16px 18px;
}

[data-testid="stMetric"] * {
    color: #dce8f5 !important;
}

[data-testid="stCodeBlock"] {
    border: 1px solid #304258;
    border-radius: 10px;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "links" not in st.session_state:
    st.session_state.links = []

if "lf_job" not in st.session_state:
    st.session_state.lf_job = None


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def valid_url(value):
    parsed = urlparse(value)
    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.hostname)
    )


def get_expiration_seconds(duration):
    return {
        "1 hour": 3600,
        "1 day": 86400,
        "7 days": 604800,
        "30 days": 2592000,
    }[duration]


def friendly_api_error(response):
    if response.status_code == 409:
        return (
            "This custom alias is already taken. "
            "Please choose another one."
        )

    if response.status_code == 422:
        return (
            "The URL or alias was rejected. "
            "Check that the URL is valid and the alias "
            "contains only lowercase letters, numbers, "
            "and hyphens."
        )

    try:
        detail = response.json().get("detail")
        if detail:
            return f"HTTP {response.status_code}: {detail}"
    except (ValueError, AttributeError):
        pass

    return f"API returned HTTP {response.status_code}."


# --------------------------------------------------
# HEADER
# --------------------------------------------------

left, right = st.columns([4, 1])

with left:
    st.markdown(
        '<div class="brand">◈ Link<b>Forge</b></div>',
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        '<div style="text-align:right">'
        '<span class="pill">● Local demo</span>'
        '</div>',
        unsafe_allow_html=True,
    )


shortener_tab, builder_tab, try_tab = st.tabs([
    "🔗 URL Shortener",
    "✦ Feature Studio",
    "◉ Try Your Feature",
])


# ==================================================
# TAB 1: URL SHORTENER
# ==================================================

with shortener_tab:

    st.markdown(
        '<div class="eyebrow">A smarter way to share</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero">'
        'Long links, <em>short stories.</em>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sub">'
        'Create clean, shareable links in seconds. '
        'Choose your own custom alias, set expiration '
        'dates, and control click limits.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Create a short link")

    with st.form("shorten_form", clear_on_submit=False):

        url = st.text_input(
            "Destination URL",
            placeholder="https://example.com/my-article",
        )

        # NEW: CUSTOM ALIAS FIELD
        alias = st.text_input(
            "Custom alias (optional)",
            placeholder="e.g. my-article",
            help=(
                "Use lowercase letters, numbers, and hyphens. "
                "Leave empty for an automatically generated code."
            ),
        )

        st.caption(
            "Example: `my-article` creates "
            "`http://127.0.0.1:8000/my-article`"
        )

        a, b = st.columns(2)

        with a:
            duration = st.selectbox(
                "Expires after",
                ["1 hour", "1 day", "7 days", "30 days"],
                index=3,
            )

        with b:
            limit_mode = st.selectbox(
                "Click limit",
                [
                    "Unlimited",
                    "1 click",
                    "3 clicks",
                    "5 clicks",
                    "10 clicks",
                    "Custom",
                ],
                index=0,
            )

            custom_limit = None

            if limit_mode == "Custom":
                custom_limit = st.number_input(
                    "Maximum clicks",
                    min_value=1,
                    value=20,
                    step=1,
                )

        submitted = st.form_submit_button(
            "✦  Shorten URL",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        clean_url = url.strip()
        clean_alias = alias.strip()

        if not valid_url(clean_url):

            st.error(
                "Please enter a valid HTTP or HTTPS URL."
            )

        elif clean_alias and not ALIAS_PATTERN.fullmatch(
            clean_alias
        ):

            st.error(
                "Invalid custom alias. Use only lowercase "
                "letters, numbers, and hyphens. "
                "Spaces and uppercase letters are not allowed."
            )

        else:

            seconds = get_expiration_seconds(duration)

            if limit_mode == "Unlimited":
                max_clicks = None

            elif limit_mode == "Custom":
                max_clicks = int(custom_limit)

            else:
                max_clicks = int(limit_mode.split()[0])

            payload = {
                "url": clean_url,
                "expires_in_seconds": seconds,
            }

            if max_clicks is not None:
                payload["max_clicks"] = max_clicks

            # Include alias only when the user entered one.
            if clean_alias:
                payload["alias"] = clean_alias

            try:

                resp = requests.post(
                    f"{API_URL}/shorten",
                    json=payload,
                    timeout=8,
                )

                if resp.status_code == 201:

                    result = resp.json()
                    code = result.get("code")

                    if not code:

                        st.error(
                            "The API did not return a short code."
                        )

                    else:

                        short_url = f"{API_URL}/{code}"

                        st.session_state.links.insert(
                            0,
                            {
                                "code": code,
                                "original": clean_url,
                                "short": short_url,
                                "alias": clean_alias or None,
                                "created": datetime.now().strftime(
                                    "%d %b %Y, %H:%M"
                                ),
                                "expires": duration,
                                "limit": max_clicks,
                            },
                        )

                        st.session_state.latest_code = code

                        st.success(
                            "Your short link is ready!"
                        )

                        st.code(
                            short_url,
                            language=None,
                        )

                        if clean_alias:
                            st.caption(
                                f"Custom alias: `{clean_alias}`"
                            )
                        else:
                            st.caption(
                                "An automatic short code was generated."
                            )

                        st.caption(
                            "Use the copy icon to copy your link."
                        )

                else:

                    st.error(friendly_api_error(resp))

            except requests.RequestException:

                st.error(
                    "Cannot connect to the FastAPI backend. "
                    "Make sure it is running on port 8000."
                )

    st.markdown("---")

    # DASHBOARD METRICS

    items = st.session_state.links

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Links created this session",
        len(items),
    )

    c2.metric(
        "Custom aliases",
        sum(
            bool(item.get("alias"))
            for item in items
        ),
    )

    c3.metric(
        "Backend",
        "FastAPI",
    )

    st.markdown("### Your recent links")

    st.caption(
        "Links created in this browser session. "
        "This list is not persistent storage."
    )

    if not items:

        st.info(
            "Your shortened links will appear here."
        )

    else:

        for item in items[:15]:

            with st.container(border=True):

                st.markdown(
                    f"**{item['short']}**"
                )

                st.caption(
                    f"Destination: {item['original']}"
                )

                if item.get("alias"):
                    st.caption(
                        f"Custom alias: {item['alias']}"
                    )

                st.caption(
                    f"Created {item['created']} · "
                    f"Expires after {item['expires']} · "
                    f"Click limit: "
                    f"{item['limit'] if item['limit'] is not None else 'Unlimited'}"
                )


# ==================================================
# TAB 2: FEATURE STUDIO
# ==================================================

with builder_tab:

    import feature_builder as fb

    st.markdown(
        "## Build software features with AI"
    )

    st.markdown(
        '<div class="sub">'
        'Choose a feature, approve the plan, '
        'and let LinkForge generate, test, '
        'diagnose, and improve the code.'
        '</div>',
        unsafe_allow_html=True,
    )

    EXAMPLES = {

        "API Version":
            'Add GET /api/version returning HTTP 200 '
            'and exactly {"version":"1.0.0"}. '
            'Register before /{code}. '
            'Generate two tests for status and JSON response. '
            'Preserve existing functionality.',

        "Application Information":
            'Add GET /api/info returning HTTP 200 '
            'and exactly {"name":"LinkForge",'
            '"type":"URL Shortener"}. '
            'Register before /{code}. '
            'Generate two tests. Preserve existing behavior.',

        "API Capabilities":
            'Add GET /api/capabilities returning HTTP 200 '
            'and exactly {"features":["shorten",'
            '"redirect","custom-alias"]}. '
            'Register before /{code}. '
            'Generate two tests. Preserve existing behavior.',

        "Service Status":
            'Add GET /api/status returning HTTP 200 '
            'and exactly {"service":"LinkForge",'
            '"status":"running"}. '
            'Register before /{code}. '
            'Generate two tests.',

        "API Welcome Message":
            'Add GET /api/welcome returning HTTP 200 '
            'and exactly {"message":"Welcome to LinkForge"}. '
            'Register before /{code}. Generate two tests.',

        "Short URL Count":
            'Add GET /api/count returning HTTP 200 '
            'with {"total_urls":N}, where N is the number '
            'of stored short URLs. Test before and after '
            'creating a URL without assuming an empty store. '
            'Register before /{code}. Preserve existing behavior.',

        "Alias Availability":
            'Add GET /api/alias-available/{alias}. '
            'Return {"available":true} for unused valid aliases '
            'and {"available":false} for existing aliases. '
            'Return 422 for nonempty invalid aliases and '
            '404 when the path segment is missing. '
            'Register before /{code}. Generate tests.',

        "Delete Short URL":
            'Add DELETE /api/urls/{code}. '
            'Return HTTP 204 with an empty body for successful '
            'deletion and 404 for unknown codes. '
            'Test that other URLs are unaffected. '
            'For redirects use follow_redirects=False, '
            'never allow_redirects=False. '
            'Preserve existing functionality.',

        "URL Preview":
            'Add GET /api/preview/{code} returning HTTP 200 '
            'with code and original URL without redirecting '
            'or incrementing click_count. '
            'Return 404 for unknown codes. '
            'Register before /{code}. Generate tests.',

        "URL Click Statistics":
            'Add GET /api/stats/{code} returning HTTP 200 '
            'with code, url, and click_count for a stored URL. '
            'Reading stats must not increase the count. '
            'Return 404 for unknown codes. '
            'Test before and after a successful redirect using '
            'follow_redirects=False, never allow_redirects=False. '
            'Register before /{code}. Preserve existing behavior.',
    }

    # ----------------------------------------------
    # START NEW FEATURE
    # ----------------------------------------------

    if st.session_state.lf_job is None:

        st.markdown("### 01 · Choose a feature")

        st.caption(
            "Choose a feature below or write your own request."
        )

        example = st.selectbox(
            "Feature examples",
            ["Write my own request"] + list(EXAMPLES),
            key="lf_example",
        )

        request = st.text_area(
            "Feature request",
            value=EXAMPLES.get(example, ""),
            height=150,
            placeholder=(
                "Describe the feature you want to build..."
            ),
            key=f"lf_request_{example}",
        )

        if st.button(
            "Generate specification and acceptance tests",
            type="primary",
            use_container_width=True,
            disabled=not request.strip(),
        ):

            try:

                with st.spinner(
                    "Generating specification and tests..."
                ):

                    st.session_state.lf_job = fb.create(
                        request
                    )

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Could not generate feature: {exc}"
                )

        previous = fb.list_jobs()

        if previous:

            with st.expander(
                "Resume an earlier feature (optional)"
            ):

                choices = {
                    (
                        f"{item.get('request', 'Feature')[:65]}"
                        f" · {item['status'].replace('_', ' ')}"
                        f" · {item['job'][:6]}"
                    ): item["job"]
                    for item in previous
                }

                selection = st.selectbox(
                    "Saved work",
                    list(choices),
                    key="lf_resume_select",
                )

                if st.button(
                    "Resume selected feature"
                ):

                    st.session_state.lf_job = (
                        choices[selection]
                    )

                    st.rerun()

    # ----------------------------------------------
    # EXISTING FEATURE WORKFLOW
    # ----------------------------------------------

    else:

        job = st.session_state.lf_job

        state = fb.read(job)
        status = state["status"]
        folder = fb.job_path(job)

        labels = {
            "spec_review": "Review specification",
            "code_review": "Review generated code",
            "failed": "Investigate test failure",
            "test_fix_review": "Approve test correction",
            "validated": "Ready for approval",
            "applied": "Feature applied",
            "generating_spec": "Generating specification",
            "generating_code": "Generating code",
            "testing": "Running tests",
            "error": "Error",
            "rejected": "Rejected",
        }

        heading, reset = st.columns([5, 1])

        with heading:

            st.markdown("### Current feature")
            st.write(state.get("request", ""))

        with reset:

            if st.button(
                "＋ New",
                key="lf_new",
                help="Start another feature.",
            ):

                st.session_state.lf_job = None
                st.rerun()

        stage_label = labels.get(status, status)

        st.markdown(
            '<div class="stagebar">'
            f'<b>Current step: {stage_label}</b>'
            f' · Revisions: {state.get("revision", 0)}'
            f' · Repair attempts: '
            f'{state.get("repair_attempts", 0)}'
            '</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "01 Specify → 02 Generate → 03 Test → "
            "04 Diagnose & retry → 05 Apply → 06 Try it"
        )

        # SPEC REVIEW

        if status == "spec_review":

            st.markdown("### 02 · Review the plan")

            st.info(
                "LinkForge generated the specification and tests. "
                "No application changes have been applied."
            )

            spec_text = st.text_area(
                "Feature specification",
                value=(
                    folder / "feature.md"
                ).read_text(),
                height=230,
                key=f"lf_spec_{job}",
            )

            with st.expander("Acceptance tests"):

                test_text = st.text_area(
                    "Generated tests",
                    value=(
                        folder / "test_feature.py"
                    ).read_text(),
                    height=250,
                    key=f"lf_tests_{job}",
                )

            a, b = st.columns(2)

            if a.button(
                "Approve plan and generate code",
                type="primary",
                use_container_width=True,
            ):

                try:

                    fb.save_spec(
                        job,
                        spec_text,
                        test_text,
                    )

                    with st.spinner(
                        "Generating implementation..."
                    ):
                        fb.generate_code(job)

                    st.rerun()

                except Exception as exc:
                    st.error(str(exc))

            if b.button(
                "Reject feature",
                use_container_width=True,
            ):

                fb.reject(job)
                st.session_state.lf_job = None
                st.rerun()

        # CODE REVIEW

        elif status == "code_review":

            st.markdown(
                "### 03 · Review proposed changes"
            )

            note = state.get("repair_note")

            if note:
                st.info(note)

            st.markdown(
                (folder / "plan.md").read_text()
            )

            with st.expander("Show code changes"):

                st.code(
                    (folder / "changes.diff").read_text(),
                    language="diff",
                )

            with st.expander(
                "Show full generated Python"
            ):

                st.code(
                    (folder / "candidate.py").read_text(),
                    language="python",
                )

            with st.expander(
                "Show approved tests"
            ):

                st.code(
                    (folder / "test_feature.py").read_text(),
                    language="python",
                )

            with st.expander(
                "Request another revision (optional)"
            ):

                feedback = st.text_area(
                    "What should the AI improve?",
                    placeholder=(
                        "Describe what needs fixing..."
                    ),
                    key=f"lf_feedback_{job}",
                )

                if st.button(
                    "Revise implementation",
                    disabled=not feedback.strip(),
                ):

                    try:

                        with st.spinner(
                            "Revising implementation..."
                        ):
                            fb.generate_code(
                                job,
                                feedback,
                            )

                        st.rerun()

                    except Exception as exc:
                        st.error(str(exc))

            st.warning(
                "Local tests execute generated Python "
                "on your computer without a sandbox. "
                "Use a disposable environment without "
                "sensitive files or credentials."
            )

            a, b = st.columns(2)

            if a.button(
                "Authorize local tests",
                type="primary",
                use_container_width=True,
            ):

                try:

                    with st.spinner(
                        "Running tests..."
                    ):
                        fb.validate(job)

                    st.rerun()

                except Exception as exc:
                    st.error(str(exc))

            if b.button(
                "Reject proposed code",
                use_container_width=True,
            ):

                fb.reject(job)
                st.session_state.lf_job = None
                st.rerun()

        # TEST RESULTS

        elif status in ("validated", "failed"):

            result = fb.result_summary(job)

            st.markdown("### 04 · Test results")

            if status == "validated":

                st.success(
                    "All tests passed. "
                    "Ready for final approval."
                )

            else:

                st.error(
                    "Some tests failed. "
                    "Nothing has been applied."
                )

            st.markdown(
                "**Result:** " + result["summary"]
            )

            if result["failures"]:

                st.markdown("**Tests that failed:**")

                for failure in result["failures"][:10]:
                    st.write("• " + failure)

            with st.expander(
                "View complete pytest output (advanced)"
            ):

                st.code(
                    result["output"][-16000:],
                    language="text",
                )

            if status == "validated":

                st.markdown("### 05 · Final approval")

                if st.button(
                    "Approve and apply feature",
                    type="primary",
                    use_container_width=True,
                ):

                    try:

                        fb.apply(job)
                        st.rerun()

                    except Exception as exc:
                        st.error(str(exc))

            else:

                st.markdown(
                    "### Automatic diagnosis and repair"
                )

                st.write(
                    "LinkForge will examine the failed tests "
                    "and prepare a targeted correction. "
                    "Proposed test changes require approval."
                )

                if state.get("repair_attempts", 0) >= 2:

                    st.warning(
                        "Multiple repair attempts have been made. "
                        "Review the diagnosis before retrying."
                    )

                if st.button(
                    "Diagnose and prepare a fix",
                    type="primary",
                    use_container_width=True,
                ):

                    try:

                        with st.spinner(
                            "Diagnosing failures..."
                        ):
                            fb.prepare_repair(job)

                        st.rerun()

                    except Exception as exc:

                        st.error(
                            f"Could not prepare fix: {exc}"
                        )

        # TEST CORRECTION REVIEW

        elif status == "test_fix_review":

            st.markdown(
                "### 04 · Review test correction"
            )

            st.info(
                state.get(
                    "repair_note",
                    "LinkForge found a possible test issue.",
                )
            )

            st.write(
                "The proposed correction changes generated "
                "tests, not your existing application."
            )

            with st.expander(
                "See exact changes to tests",
                expanded=True,
            ):

                st.code(
                    (folder / "test_fix.diff").read_text(),
                    language="diff",
                )

            a, b = st.columns(2)

            if a.button(
                "Approve test correction",
                type="primary",
                use_container_width=True,
            ):

                try:

                    fb.approve_test_fix(job)
                    st.rerun()

                except Exception as exc:
                    st.error(str(exc))

            if b.button(
                "Reject test correction",
                use_container_width=True,
            ):

                fb.reject_test_fix(job)
                st.rerun()

        # FEATURE APPLIED

        elif status == "applied":

            st.success(
                "Feature successfully applied "
                "to workspace/app.py."
            )

            st.markdown(
                "### 06 · Try your feature"
            )

            st.write(
                "Open the **Try Your Feature** tab "
                "to call the new endpoint and see "
                "the response."
            )

            if st.button(
                "Start another feature",
                type="primary",
            ):

                st.session_state.lf_job = None
                st.rerun()

        elif status == "error":

            st.error(
                state.get(
                    "error",
                    "Unexpected error",
                )
            )

        elif status == "rejected":

            st.info(
                "Feature rejected. "
                "Start a new feature when ready."
            )

        else:

            st.info(
                "Current step: " + stage_label
            )


# ==================================================
# TAB 3: TRY YOUR FEATURE
# ==================================================

with try_tab:

    st.markdown("## Try your feature")

    st.markdown(
        '<div class="sub">'
        'Test your applied API features directly '
        'from LinkForge. View the request, '
        'response status, and JSON output.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Connects to your local FastAPI server "
        "on port 8000."
    )

    available = []

    try:

        spec_resp = requests.get(
            f"{API_URL}/openapi.json",
            timeout=3,
        )

        spec_resp.raise_for_status()

        for route, methods in (
            spec_resp.json().get("paths", {}).items()
        ):

            for method in ("get", "post", "delete"):

                if method in methods:
                    available.append(
                        (method.upper(), route)
                    )

    except requests.RequestException:

        st.warning(
            "FastAPI is not responding. "
            "Start the backend and refresh."
        )

    if available:

        options = [
            f"{method}  {path}"
            for method, path in available
        ]

        chosen = st.selectbox(
            "Choose an API endpoint",
            options,
            key="lf_try_endpoint",
        )

        method, route = available[
            options.index(chosen)
        ]

        st.caption(
            "Replace {code} or {alias} "
            "with a real value."
        )

        latest_code = st.session_state.get(
            "latest_code"
        )

        default_path = route

        if latest_code:
            default_path = default_path.replace(
                "{code}",
                str(latest_code),
            )

        path = st.text_input(
            "Request path",
            value=default_path,
            key=f"lf_try_path_{chosen}",
        )

        body = ""

        if method == "POST":

            body = st.text_area(
                "JSON request body",
                value=(
                    '{"url":"https://example.com"}'
                ),
                height=120,
                key=f"lf_try_body_{chosen}",
            )

        confirmed = True

        if method == "DELETE":

            confirmed = st.checkbox(
                "I understand this will delete a URL "
                "from my running demo application."
            )

        if st.button(
            "Send request and show result",
            type="primary",
            disabled=not confirmed,
            use_container_width=True,
        ):

            if (
                not path.startswith("/")
                or "://" in path
                or "?" in path
                or "#" in path
                or "{" in path
                or "}" in path
            ):

                st.error(
                    "Enter only the API path, "
                    "such as /api/stats/5."
                )

            else:

                try:

                    payload = None

                    if method == "POST":
                        payload = json.loads(body)

                    response = requests.request(
                        method,
                        f"{API_URL}{path}",
                        json=payload,
                        timeout=8,
                        allow_redirects=False,
                    )

                    st.markdown("### API response")

                    st.metric(
                        "HTTP status",
                        response.status_code,
                    )

                    if response.status_code >= 400:

                        st.warning(
                            "The API returned an error. "
                            "Check the path or request data."
                        )

                    try:
                        st.json(response.json())

                    except ValueError:
                        st.code(
                            response.text
                            or "(empty response body)",
                            language="text",
                        )

                    if "location" in response.headers:

                        st.caption(
                            "Redirect destination: "
                            + response.headers["location"]
                        )

                except ValueError as exc:

                    st.error(
                        "Invalid JSON request body: "
                        + str(exc)
                    )

                except requests.RequestException as exc:

                    st.error(
                        "Could not contact FastAPI: "
                        + str(exc)
                    )

    else:

        st.info(
            "Available API endpoints will appear "
            "once FastAPI is running."
        )