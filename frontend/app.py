import json
import os
from typing import Any, Dict, Optional

import requests
import streamlit as st


API_BASE_URL = os.getenv("MISRA_API_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="MISRA C:2012 Compliance Platform",
    page_icon="MISRA",
    layout="wide",
)

st.markdown(
    """
<style>
.main .block-container { padding-top: 1.5rem; max-width: 1400px; }
[data-testid="stMetricValue"] { font-size: 1.6rem; }
.misra-header {
    border-bottom: 1px solid #d7dde8;
    margin-bottom: 1rem;
    padding-bottom: 0.8rem;
}
.misra-title {
    font-size: 1.85rem;
    font-weight: 760;
    letter-spacing: 0;
    color: #111827;
}
.misra-subtitle { color: #4b5563; font-size: 0.95rem; margin-top: 0.2rem; }
.review-panel {
    border: 1px solid #d7dde8;
    border-radius: 8px;
    padding: 1rem;
    background: #ffffff;
}
.rule-chip {
    display: inline-block;
    border: 1px solid #bfd4ee;
    background: #f3f8ff;
    color: #174b7a;
    border-radius: 6px;
    padding: 0.16rem 0.45rem;
    margin-right: 0.35rem;
    font-size: 0.78rem;
    font-weight: 650;
}
.status-ready { color: #116b45; font-weight: 650; }
.status-blocked { color: #9f1239; font-weight: 650; }
.small-muted { color: #6b7280; font-size: 0.86rem; }
</style>
""",
    unsafe_allow_html=True,
)


def init_state() -> None:
    defaults = {
        "session_id": "",
        "review": None,
        "final": None,
        "explanation": None,
        "uploaded_name": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def api_request(method: str, path: str, **kwargs) -> Optional[Dict[str, Any]]:
    try:
        response = requests.request(
            method,
            f"{API_BASE_URL}{path}",
            timeout=90,
            **kwargs,
        )
    except requests.RequestException as exc:
        st.error(f"Backend request failed: {exc}")
        return None

    if response.status_code >= 400:
        detail = response.text
        try:
            detail = response.json().get("detail", detail)
        except ValueError:
            pass
        st.error(f"Backend returned {response.status_code}: {detail}")
        return None

    return response.json()


def start_review(uploaded_file) -> None:
    file_bytes = uploaded_file.getvalue()
    files = {"file": (uploaded_file.name, file_bytes, "text/x-csrc")}
    result = api_request("POST", "/upload", files=files)
    if result is None:
        return

    st.session_state.session_id = result["session_id"]
    st.session_state.review = result
    st.session_state.final = None
    st.session_state.explanation = None
    st.session_state.uploaded_name = uploaded_file.name


def submit_decision(action: str, edited_code: str = "", comment: str = "") -> None:
    payload = {
        "session_id": st.session_state.session_id,
        "action": action,
        "edited_code": edited_code,
        "comment": comment,
    }
    result = api_request("POST", "/decision", json=payload)
    if result is None:
        return

    st.session_state.review = result
    st.session_state.explanation = None


def explain_rule() -> None:
    session_id = st.session_state.session_id
    result = api_request("GET", f"/review/{session_id}/explain")
    if result is not None:
        st.session_state.explanation = result


def finalize_review() -> None:
    session_id = st.session_state.session_id
    result = api_request("POST", f"/finalize/{session_id}")
    if result is None:
        return

    st.session_state.final = result
    st.session_state.review = result


def render_progress(review: Dict[str, Any]) -> None:
    progress = review.get("progress", {})
    total = review.get("total_violations", 0)
    reviewed = progress.get("reviewed", 0)
    ratio = reviewed / total if total else 1

    st.progress(ratio)
    cols = st.columns(5)
    cols[0].metric("Reviewed", reviewed)
    cols[1].metric("Remaining", progress.get("remaining", 0))
    cols[2].metric("Accepted", progress.get("accepted", 0))
    cols[3].metric("Rejected", progress.get("rejected", 0))
    cols[4].metric("Skipped", progress.get("skipped", 0))


def render_violation(review: Dict[str, Any]) -> None:
    violation = review.get("current_violation")
    if violation is None:
        st.success("Review complete.")
        if st.button("Apply approved patches", type="primary", use_container_width=True):
            finalize_review()
        return

    st.markdown(
        f"""
<div class="review-panel">
  <span class="rule-chip">Rule {violation.get('rule_id', '')}</span>
  <span class="rule-chip">{violation.get('severity', '')}</span>
  <span class="rule-chip">Line {violation.get('line_number', '')}</span>
  <h3>{violation.get('title', 'Violation')}</h3>
  <p class="small-muted">{violation.get('description', '')}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        st.caption("Original code")
        st.code(violation.get("original_code", ""), language="c")
    with right:
        st.caption("Suggested replacement")
        suggested = violation.get("suggested_code") or "No automatic replacement is available."
        st.code(suggested, language="c")

    actions = st.columns([1, 1, 1, 1])
    if actions[0].button("Accept", use_container_width=True):
        submit_decision("accept")
        st.rerun()
    if actions[1].button("Reject", use_container_width=True):
        submit_decision("reject")
        st.rerun()
    if actions[2].button("Skip", use_container_width=True):
        submit_decision("skip")
        st.rerun()
    if actions[3].button("Explain Rule", use_container_width=True):
        explain_rule()

    explanation = st.session_state.explanation
    if explanation is not None:
        with st.expander("Rule explanation", expanded=True):
            st.write(explanation.get("explanation", ""))
            st.json(
                {
                    "rule_id": explanation.get("rule_id"),
                    "category": explanation.get("category"),
                    "severity": explanation.get("severity"),
                    "auto_fixable": explanation.get("auto_fixable"),
                }
            )

    with st.form("edit_decision_form", clear_on_submit=False):
        replacement = st.text_area(
            "Edited replacement",
            value=violation.get("suggested_code") or violation.get("original_code", ""),
            height=130,
        )
        comment = st.text_input("Review note", value="")
        submitted = st.form_submit_button("Submit edit", use_container_width=True)
        if submitted:
            submit_decision("edit", replacement, comment)
            st.rerun()


def render_final(final_result: Dict[str, Any]) -> None:
    validation = final_result.get("validation_result") or {}
    report = final_result.get("compliance_report") or {}
    passed = validation.get("is_valid", False)

    st.subheader("Final corrected code")
    original, corrected = st.columns(2)
    with original:
        st.caption("Original")
        st.code(final_result.get("original_code", ""), language="c")
    with corrected:
        st.caption("Corrected")
        st.code(final_result.get("final_code", ""), language="c")

    if passed:
        st.markdown('<p class="status-ready">Validation passed.</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-blocked">Validation needs attention.</p>', unsafe_allow_html=True)
        st.code(validation.get("report", ""), language="text")

    downloads = st.columns(2)
    downloads[0].download_button(
        "Download corrected code",
        data=final_result.get("final_code", ""),
        file_name=f"{final_result.get('session_id', 'session')}_fixed.c",
        mime="text/x-csrc",
        use_container_width=True,
    )
    downloads[1].download_button(
        "Download compliance report",
        data=json.dumps(report, indent=2),
        file_name=f"{final_result.get('session_id', 'session')}_report.json",
        mime="application/json",
        use_container_width=True,
    )

    with st.expander("Compliance report", expanded=False):
        st.json(report)


init_state()

st.markdown(
    """
<div class="misra-header">
  <div class="misra-title">MISRA C:2012 Compliance Platform</div>
  <div class="misra-subtitle">Interactive review workflow</div>
</div>
""",
    unsafe_allow_html=True,
)

upload_col, state_col = st.columns([2, 1])
with upload_col:
    uploaded_file = st.file_uploader("Upload C source", type=["c"])
with state_col:
    st.caption("Backend")
    st.code(API_BASE_URL, language="text")

if uploaded_file is not None:
    if st.button("Analyze", type="primary", use_container_width=True):
        start_review(uploaded_file)
        st.rerun()

review = st.session_state.review
final_result = st.session_state.final

if review is not None:
    st.divider()
    st.subheader(st.session_state.uploaded_name or "Review session")
    render_progress(review)
    render_violation(review)

if final_result is not None:
    st.divider()
    render_final(final_result)
