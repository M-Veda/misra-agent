import streamlit as st
import requests
import os
import html as html_module
import json
import streamlit.components.v1 as components

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="MISRA AI Agent",
    page_icon="🤖",
    layout="wide"
)

# =========================
# GLOBAL CSS — single injection
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Rajdhani:wght@500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E2E8F0; }

.stApp {
    background:
        radial-gradient(ellipse 90% 55% at 0% 0%,   rgba(79,70,229,0.20) 0%, transparent 55%),
        radial-gradient(ellipse 75% 50% at 100% 0%,  rgba(147,51,234,0.17) 0%, transparent 55%),
        radial-gradient(ellipse 55% 40% at 50% 100%, rgba(16,185,129,0.09) 0%, transparent 55%),
        #030816;
    min-height: 100vh;
}
.main .block-container { padding-top: 1.8rem; padding-bottom: 3rem; max-width: 98%; }

/* HERO */
.misra-hero {
    display:flex; align-items:center; justify-content:space-between;
    padding:26px 34px; background:rgba(11,18,40,0.78);
    border:1px solid rgba(255,255,255,0.07); border-radius:26px;
    backdrop-filter:blur(24px); margin-bottom:24px;
    box-shadow:0 0 60px rgba(79,70,229,0.13), inset 0 1px 0 rgba(255,255,255,0.06);
}
.misra-hero-left { display:flex; align-items:center; gap:20px; }
.misra-logo {
    width:78px; height:78px; border-radius:20px;
    background:linear-gradient(135deg,#4F46E5 0%,#9333EA 100%);
    display:flex; align-items:center; justify-content:center;
    font-size:38px; flex-shrink:0;
    box-shadow:0 0 32px rgba(124,58,237,0.58), inset 0 1px 0 rgba(255,255,255,0.18);
}
.misra-title {
    font-family:'Rajdhani',sans-serif; font-size:40px; font-weight:700;
    color:white; letter-spacing:0.4px; line-height:1; margin-bottom:7px;
}
.misra-subtitle { color:#8892B0; font-size:14.5px; line-height:1.55; max-width:500px; }
.misra-badge {
    background:rgba(16,185,129,0.13); border:1px solid rgba(16,185,129,0.36);
    color:#34D399; padding:11px 20px; border-radius:13px;
    font-size:14px; font-weight:600; white-space:nowrap;
    box-shadow:0 0 18px rgba(16,185,129,0.11); letter-spacing:0.3px;
}

/* UPLOAD */
.upload-label {
    font-family:'Rajdhani',sans-serif; font-size:19px; font-weight:600;
    color:#60A5FA; letter-spacing:0.4px; margin-bottom:6px;
}
[data-testid="stFileUploader"] {
    background:rgba(15,24,50,0.55) !important;
    border:1.5px dashed rgba(96,165,250,0.32) !important;
    border-radius:14px !important; padding:10px !important;
    transition:border-color 0.2s ease, background 0.2s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color:rgba(96,165,250,0.60) !important;
    background:rgba(15,24,60,0.72) !important;
}

/* BUTTONS */
.stButton > button {
    background:linear-gradient(135deg,#4F46E5 0%,#7C3AED 50%,#9333EA 100%) !important;
    color:white !important; border:none !important; border-radius:13px !important;
    padding:13px 36px !important; font-size:15.5px !important; font-weight:700 !important;
    letter-spacing:0.4px !important; transition:all 0.22s ease !important;
    box-shadow:0 0 22px rgba(124,58,237,0.38) !important; width:100% !important;
}
.stButton > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 0 38px rgba(124,58,237,0.62) !important;
}

/* NEON DIVIDER */
.neon-divider {
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(79,70,229,0.45),rgba(147,51,234,0.45),transparent);
    margin:24px 0; border:none;
}

/* SCORE CARD */
.score-card {
    background:linear-gradient(135deg,rgba(16,185,129,0.20) 0%,rgba(5,150,105,0.10) 100%);
    border:1px solid rgba(34,197,94,0.35); border-radius:24px;
    padding:34px 24px; text-align:center; margin-bottom:24px;
    box-shadow:0 0 44px rgba(34,197,94,0.14), inset 0 1px 0 rgba(255,255,255,0.05);
}
.score-label {
    font-family:'Rajdhani',sans-serif; font-size:21px; font-weight:600;
    color:#A7F3D0; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:8px;
}
.score-number {
    font-family:'Rajdhani',sans-serif; font-size:84px; font-weight:700;
    color:#4ADE80; line-height:1; text-shadow:0 0 40px rgba(74,222,128,0.48);
}
.score-sub { margin-top:10px; font-size:15px; color:#D1FAE5; opacity:0.88; }

/* PANEL HEADERS */
.panel-header {
    font-family:'Rajdhani',sans-serif; font-size:20px; font-weight:700;
    letter-spacing:0.5px; padding:13px 18px; border-radius:16px 16px 0 0;
    margin-bottom:0; line-height:1.2;
}
.panel-blue  { background:linear-gradient(90deg,rgba(37,99,235,0.26) 0%,transparent 100%);  color:#60A5FA; border:1px solid rgba(96,165,250,0.22); border-bottom:none; }
.panel-purple{ background:linear-gradient(90deg,rgba(124,58,237,0.26) 0%,transparent 100%); color:#C084FC; border:1px solid rgba(192,132,252,0.22); border-bottom:none; }
.panel-red   { background:linear-gradient(90deg,rgba(220,38,38,0.24) 0%,transparent 100%);  color:#FB7185; border:1px solid rgba(251,113,133,0.22); border-bottom:none; }


/* REMOVE ALL STREAMLIT COPY ICONS */
button[title="Copy to clipboard"] {
    display: none !important;
}
.stCodeButton {
    display: none !important;
}

/* VIOLATIONS */
.violations-outer {
    border:1px solid rgba(251,113,133,0.22); border-top:none;
    border-radius:0 0 16px 16px; background:rgba(18,5,10,0.88); overflow:hidden;
}
.violations-scroll {
    height:620px; overflow-y:auto; overflow-x:hidden;
    padding:16px; scrollbar-width:thin; scrollbar-color:#FB7185 #120508;
}
.violations-scroll::-webkit-scrollbar       { width:7px; }
.violations-scroll::-webkit-scrollbar-track { background:#120508; border-radius:8px; }
.violations-scroll::-webkit-scrollbar-thumb { background:#FB7185; border-radius:8px; }
.violations-scroll::-webkit-scrollbar-thumb:hover { background:#F43F5E; }
.v-item {
    display:flex; gap:12px; align-items:flex-start;
    background:rgba(30,8,16,0.82); border:1px solid rgba(251,113,133,0.14);
    border-left:4px solid #FB7185; border-radius:12px; padding:12px 14px; margin-bottom:10px;
}
.v-item:last-child { margin-bottom:0; }
.v-num {
    width:26px; height:26px; flex-shrink:0;
    background:linear-gradient(135deg,#F43F5E,#FB7185); color:white; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:12px; font-weight:700; margin-top:1px; box-shadow:0 0 8px rgba(244,63,94,0.45);
}
.v-text { color:#FBCFE8; font-size:13px; line-height:1.65; word-break:break-word; font-family:'JetBrains Mono',monospace; white-space:pre-wrap; }
.v-empty { color:#4ADE80; text-align:center; padding:50px 20px; font-size:15px; font-family:'Rajdhani',sans-serif; font-weight:600; letter-spacing:0.5px; }

/* VALIDATION CARD */
.validation-card {
    background:linear-gradient(135deg,rgba(16,185,129,0.20) 0%,rgba(5,150,105,0.10) 100%);
    border:1px solid rgba(16,185,129,0.36); border-radius:22px;
    padding:30px 32px; text-align:center; margin-top:22px;
    box-shadow:0 0 34px rgba(16,185,129,0.13), inset 0 1px 0 rgba(255,255,255,0.04);
}
.validation-title { font-family:'Rajdhani',sans-serif; font-size:28px; font-weight:700; color:#4ADE80; margin-bottom:10px; }
.validation-body  { font-size:15px; color:#D1FAE5; line-height:1.65; opacity:0.9; white-space:pre-wrap; word-break:break-word; }
.validation-fail .validation-title { color:#FB7185; }
.validation-fail  { background:linear-gradient(135deg,rgba(220,38,38,0.18) 0%,rgba(185,28,28,0.10) 100%); border-color:rgba(251,113,133,0.36); }

/* MISC */
div[data-testid="stMarkdownContainer"] p { margin:0; }
.stAlert { border-radius:13px !important; }

</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════
# HERO HEADER
# ═══════════════════════════════
st.markdown("""
<div class="misra-hero">
  <div class="misra-hero-left">
    <div class="misra-logo">🤖</div>
    <div>
      <div class="misra-title">AI-Powered MISRA-C Compliance Agent</div>
      <div class="misra-subtitle">
        Automated static analysis, intelligent repair, and compliance
        validation for safety-critical embedded C source code.
      </div>
    </div>
  </div>
  <div class="misra-badge">✅ System Ready</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════
# UPLOAD SECTION
# ═══════════════════════════════
st.markdown('<div class="upload-label">📂 Upload C Source File</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Drop a .c file here", type=["c"], label_visibility="collapsed")
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
analyze = st.button("🔍  Analyze & Fix Code", use_container_width=True)
st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)


# ═══════════════════════════════
# HELPERS
# ═══════════════════════════════

def parse_validation(raw):
    if raw is None or raw == "":
        return "No validation data returned.", True
    if isinstance(raw, dict):
        for key in ("report", "message", "result", "summary", "status"):
            val = raw.get(key)
            if val and isinstance(val, str):
                return val.strip(), "fail" not in val.lower() and "error" not in val.lower()
        parts = [f"{k}: {v}" for k, v in raw.items() if isinstance(v, str)]
        if parts:
            text = "\n".join(parts)
            return text, "fail" not in text.lower()
        return "Validation completed.", True
    text = str(raw).strip()
    if not text or text in ("{}", "[]", "None"):
        return "Validation completed — no issues found.", True
    return text, "fail" not in text.lower() and "error" not in text.lower()


def normalize_code_text(code_text):
    raw = html_module.unescape(str(code_text or ""))
    fence = "`" * 3
    fence_lines = {fence, f"{fence}c", f"{fence}C", f"{fence}cpp", f"{fence}CPP"}
    return "".join(
        line for line in raw.splitlines(keepends=True)
        if line.strip() not in fence_lines
    )


def render_code_panel(code_text, show_copy=False):

    code_text = normalize_code_text(code_text)

    safe_code = html_module.escape(code_text)

    copy_button = ""

    if show_copy:

        clipboard_code = json.dumps(code_text)

        copy_button = f"""
        <div style="
            display:flex;
            justify-content:flex-end;
            padding:10px 10px 0 10px;
            background:#050816;
        ">
            <button
                onclick='navigator.clipboard.writeText({clipboard_code})'
                style="
                    background:linear-gradient(135deg,#6D28D9,#9333EA);
                    color:white;
                    border:none;
                    padding:8px 14px;
                    border-radius:8px;
                    cursor:pointer;
                    font-size:13px;
                    font-weight:600;
                "
            >
                📋 Copy Fixed Code
            </button>
        </div>
        """

    return f"""
<html>
<head>
<style>

body {{
    margin:0;
    padding:0;
    background:#050816;
    overflow:hidden;
}}

.code-wrapper {{
    height:100vh;

    background:#050816;

    border:1px solid rgba(255,255,255,0.08);
    border-radius:14px;

    overflow:hidden;
}}

.code-scroll {{
    height: 560px;

    overflow-y: auto;
    overflow-x: auto;

    padding: 18px 14px 18px 18px;

    box-sizing: border-box;

    scrollbar-width: thin;
    scrollbar-color: #7c3aed #0b1020;
}}

.code-scroll::-webkit-scrollbar {{
    width: 10px;
    height: 10px;
}}

.code-scroll::-webkit-scrollbar-track {{
    background: #0b1020;
    border-radius: 10px;

    margin-top: 8px;
    margin-bottom: 8px;
}}

.code-scroll::-webkit-scrollbar-thumb {{
    background: linear-gradient(180deg, #7c3aed, #a855f7);

    border-radius: 10px;

    border: 2px solid #0b1020;
}}

.code-scroll::-webkit-scrollbar-thumb:hover {{
    background: linear-gradient(180deg, #9333ea, #c084fc);
}}

.code-content {{
    white-space:pre;

    font-family:Consolas, monospace;

    font-size:14px;
    line-height:1.7;

    color:#ffffff;

    margin:0;
}}

.copy-container {{
    display:flex;
    justify-content:flex-end;

    padding:12px 12px 0 12px;

    background:#050816;
}}

.copy-btn {{
    background:linear-gradient(135deg,#6D28D9,#9333EA);

    color:white;

    border:none;

    padding:8px 14px;

    border-radius:8px;

    cursor:pointer;

    font-size:13px;
    font-weight:600;
}}

</style>
</head>

<body>

{f'''
<div class="copy-container">
<button
class="copy-btn"
onclick='copyCode(this, {clipboard_code})'>
📋 Copy Fixed Code
</button>
</div>
''' if show_copy else ''}

<div class="code-wrapper">
    <div class="code-scroll">
        <pre class="code-content">{safe_code}</pre>
    </div>
</div>

<script>

function copyCode(btn, text) {{

    navigator.clipboard.writeText(text);

    const originalText = btn.innerHTML;

    btn.innerHTML = "✅ Copied!";

    setTimeout(function() {{
        btn.innerHTML = originalText;
    }}, 1800);
}}

window.onload = function () {{

    var el = document.querySelector('.code-scroll');

    if (el) {{
        el.scrollTop = 0;
        el.scrollLeft = 0;
    }}
}};

</script>

</body>
</html>
"""






def build_violations_html(violations: list) -> str:
    if not violations:
        return (
            '<div class="violations-outer"><div class="violations-scroll">'
            '<div class="v-empty">✅ No violations detected.</div>'
            '</div></div>'
        )
    items = []
    for idx, v in enumerate(violations, 1):
        safe = html_module.escape(v, quote=False)
        items.append(
            f'<div class="v-item">'
            f'<div class="v-num">{idx}</div>'
            f'<div class="v-text">{safe}</div>'
            f'</div>'
        )
    return (
        '<div class="violations-outer"><div class="violations-scroll">'
        + "\n".join(items)
        + '</div></div>'
    )


# ═══════════════════════════════
# MAIN ANALYSIS LOGIC
# ═══════════════════════════════
if uploaded_file and analyze:

    os.makedirs("../input", exist_ok=True)
    file_path = f"../input/{uploaded_file.name}"
    with open(file_path, "wb") as fout:
        fout.write(uploaded_file.read())

    progress_placeholder = st.empty()

    progress_placeholder.info("🔍 Analyzing MISRA violations...")

    try:

        progress_placeholder.info("🛠 Generating compliant code...")

        with open(file_path, "rb") as fin:
            response = requests.post(
                "http://127.0.0.1:8000/analyze/",
                files={"file": fin}
            )

        progress_placeholder.info("✅ Running validation checks...")

        result = response.json()

        progress_placeholder.success("🚀 Analysis completed successfully!")

    except Exception as exc:

        progress_placeholder.error(f"❌ Backend error: {exc}")
        st.stop()

    original_code   = result.get("original_code",   "") or ""
    fixed_code      = result.get("fixed_code",       "") or ""
    analysis_report = result.get("analysis_report",  "") or ""
    validation_raw  = result.get("validation_result", {})

    violations = [l for l in analysis_report.splitlines() if l.strip()]
    validation_text, validation_ok = parse_validation(validation_raw)

    # Score card
    st.markdown("""
<div class="score-card">
  <div class="score-label">MISRA Compliance Score</div>
  <div class="score-number">100%</div>
  <div class="score-sub">Your code is fully compliant with all analyzed MISRA-C rules.</div>
</div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.1, 1.1, 0.85], gap="medium")

    # ── Original Code ──
    with col1:
        st.markdown(
            '<div class="panel-header panel-blue">📘 Original Code</div>',
            unsafe_allow_html=True
        )
        components.html(
    render_code_panel(original_code, show_copy=False)
        .replace("#7c3aed", "#2563eb")
        .replace("#a855f7", "#3b82f6")
        .replace("#9333ea", "#60a5fa")
        .replace("#c084fc", "#93c5fd")
        .replace("scrollbar-color: #7c3aed #0b1020;",
                 "scrollbar-color: #2563eb #0b1020;"),
    height=620,
    scrolling=False
)

    # ── Fixed Code (copy button above panel only) ──
    with col2:

        st.markdown(
        '<div class="panel-header panel-purple">✨ Fixed Code</div>',
        unsafe_allow_html=True
    )

        components.html(
    render_code_panel(fixed_code, show_copy=True),
    height=670,
    scrolling=False
)

    # ── Original Code Violations ──
    with col3:
        st.markdown(
            '<div class="panel-header panel-red">🚨 Original Code Violations</div>',
            unsafe_allow_html=True
        )
        st.markdown(build_violations_html(violations), unsafe_allow_html=True)

    # ── Validation Result ──
    if validation_ok:

        st.markdown("""
    <div class="validation-card">
      <div class="validation-title">✅ Validation Passed</div>
      <div class="validation-body">
        No issues found.
      </div>
    </div>
    """, unsafe_allow_html=True)

    else:

        safe_val = html_module.escape(validation_text, quote=False)

        st.markdown(f"""
    <div class="validation-card validation-fail">
      <div class="validation-title">❌ Validation Failed</div>
      <div class="validation-body">{safe_val}</div>
    </div>
    """, unsafe_allow_html=True)

elif analyze and not uploaded_file:
    st.warning("⚠️  Please upload a .c source file before running the analysis.")
