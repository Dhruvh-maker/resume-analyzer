"""
Streamlit Frontend — AI Resume Analyzer
Premium light-themed UI with glassmorphism, animations, and rich visualizations.
"""

import requests
import streamlit as st
import plotly.graph_objects as go
import time

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Backend URL ───────────────────────────────────────────────────────
API_URL = "http://localhost:8000"

# ── Premium Light CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Global Dark Theme ── */
    .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: #050505;
        color: #e2e8f0;
    }

    .stApp > header { background: transparent !important; }
    .block-container { padding-top: 2rem !important; max-width: 1100px !important; }

    /* ── Deep Background Glow ── */
    .bg-glow {
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 25% 30%, rgba(255, 75, 43, 0.05) 0%, transparent 50%),
                    radial-gradient(circle at 75% 50%, rgba(255, 65, 108, 0.03) 0%, transparent 50%),
                    radial-gradient(circle at 50% 80%, rgba(220, 38, 38, 0.02) 0%, transparent 40%);
        pointer-events: none;
        z-index: 0;
        animation: bgPulse 10s ease-in-out infinite alternate;
    }
    @keyframes bgPulse {
        0% { opacity: 0.5; transform: scale(1); }
        100% { opacity: 0.8; transform: scale(1.05); }
    }

    /* ── Hero ── */
    .hero-container {
        text-align: center;
        padding: 2rem 0 3rem;
        position: relative;
    }
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF4B2B 0%, #FF416C 50%, #9013FE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
        letter-spacing: -2px;
        margin-bottom: 1rem;
        animation: fadeInUp 0.8s ease-out;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ── Upload Area ── */
    .upload-wrapper {
        background: rgba(15, 15, 18, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 2rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        animation: fadeInUp 0.8s ease-out 0.4s both;
    }

    /* ── Glowing Flowing Cards ── */
    .glass-card {
        background: #0f0f12;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        position: relative;
        z-index: 1;
        overflow: hidden;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .glass-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(
            transparent, 
            transparent, 
            transparent, 
            #FF4B2B, 
            #FF416C, 
            transparent
        );
        animation: rotateGlow 4s linear infinite;
        z-index: -1;
    }
    .glass-card::after {
        content: '';
        position: absolute;
        inset: 1.5px;
        background: #0f1014;
        border-radius: 19px;
        z-index: -1;
    }
    @keyframes rotateGlow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(255, 75, 43, 0.15);
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.2rem;
    }
    .card-icon {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        background: rgba(255, 75, 43, 0.1);
    }
    .card-label {
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #f8fafc;
    }

    .card-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        font-size: 0.95rem;
        line-height: 1.6;
        color: #cbd5e1;
    }
    .card-item:last-child { border-bottom: none; }
    .card-bullet {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
        margin-top: 8px;
        box-shadow: 0 0 10px currentColor;
    }

    /* ── Score Ring ── */
    .score-section {
        text-align: center;
        padding: 2.5rem 0 1.5rem;
    }
    .score-ring-wrapper {
        position: relative;
        width: 220px;
        height: 220px;
        margin: 0 auto;
    }
    .score-ring-bg {
        position: absolute;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.03);
    }
    .score-ring-fill {
        position: absolute;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        animation: scoreReveal 1.5s ease-out forwards;
    }
    .score-inner {
        position: absolute;
        inset: 15px;
        border-radius: 50%;
        background: #050505;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5);
    }
    .score-number {
        font-size: 4rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -3px;
        line-height: 1;
        background: linear-gradient(135deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .score-max {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        margin-top: 5px;
    }
    .score-verdict {
        display: inline-block;
        margin-top: 1.5rem;
        padding: 8px 24px;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* ── Summary Card ── */
    .summary-card {
        background: rgba(255, 75, 43, 0.03);
        border: 1px solid rgba(255, 75, 43, 0.1);
        border-radius: 20px;
        padding: 1.5rem 2.5rem;
        margin: 2rem 0;
        text-align: center;
    }
    .summary-text {
        font-size: 1.1rem;
        color: #94a3b8;
        line-height: 1.8;
        font-weight: 400;
    }

    /* ── Skills ── */
    .skills-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 0.8rem;
    }
    .skill-chip {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 8px 16px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #f1f5f9;
        font-family: 'JetBrains Mono', monospace;
        transition: all 0.3s ease;
    }
    .skill-chip:hover {
        background: rgba(255, 75, 43, 0.1);
        border-color: rgba(255, 75, 43, 0.3);
        color: #FF4B2B;
        transform: translateY(-2px);
    }

    /* ── Section Headers ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin: 3rem 0 1.5rem;
    }
    .section-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(to right, rgba(255, 75, 43, 0.3), transparent);
    }
    .section-title {
        font-size: 0.85rem;
        font-weight: 800;
        color: #FF4B2B;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* ── Stats Row ── */
    .stat-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stat-card:hover {
        background: rgba(255, 75, 43, 0.05);
        border-color: rgba(255, 75, 43, 0.2);
        transform: translateY(-3px);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        background: linear-gradient(135deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 6px;
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        padding: 4rem 0 2rem;
        color: #475569;
        font-size: 0.9rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 3rem;
    }

    /* ── Hide Streamlit defaults ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Hide labels */
    [data-testid="stFileUploader"] > label,
    [data-testid="stTextInput"] > label,
    [data-testid="stTextArea"] > label {
        display: none !important;
    }

    /* Style file uploader */
    [data-testid="stFileUploader"] { background: transparent; }
    [data-testid="stFileUploader"] section {
        background: rgba(255, 75, 43, 0.02);
        border: 1px dashed rgba(255, 75, 43, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: rgba(255, 75, 43, 0.5);
        background: rgba(255, 75, 43, 0.04);
    }
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #FF4B2B, #FF416C) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.5rem !important;
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.3) !important;
    }
    /* Black/White text logic for dark theme */
    [data-testid="stFileUploader"] * { color: #94a3b8 !important; }
    [data-testid="stFileUploader"] button * { color: white !important; }
    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] { color: #f8fafc !important; }

    /* Style text inputs */
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
        background: #121214 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        padding: 12px 16px !important;
    }
    [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
        border-color: #FF4B2B !important;
        box-shadow: 0 0 0 3px rgba(255, 75, 43, 0.1) !important;
    }

    /* Style primary button */
    .stButton > button {
        background: linear-gradient(135deg, #FF4B2B, #FF416C) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.8rem 2.5rem !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 30px rgba(255, 75, 43, 0.4) !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 40px rgba(255, 75, 43, 0.5) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        color: #64748b !important;
        font-weight: 700 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: #1a1a1e !important;
        color: #FF4B2B !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

</style>
""", unsafe_allow_html=True)

# Background glow
st.markdown('<div class="bg-glow"></div>', unsafe_allow_html=True)


# ── Helper functions ──────────────────────────────────────────────────
def get_score_gradient(score: int) -> str:
    if score >= 90:
        return "linear-gradient(135deg, #10b981, #059669)"
    elif score >= 75:
        return "linear-gradient(135deg, #FF4B2B, #FF416C)"
    elif score >= 60:
        return "linear-gradient(135deg, #f59e0b, #d97706)"
    elif score >= 40:
        return "linear-gradient(135deg, #ea580c, #dc2626)"
    else:
        return "linear-gradient(135deg, #dc2626, #b91c1c)"


def get_score_color(score: int) -> str:
    if score >= 90: return "#10b981"
    elif score >= 75: return "#FF4B2B"
    elif score >= 60: return "#f59e0b"
    elif score >= 40: return "#ea580c"
    else: return "#ef4444"


def get_verdict(score: int) -> tuple[str, str, str]:
    if score >= 90:
        return "Elite Profile", "rgba(16,185,129,0.1)", "#10b981"
    elif score >= 75:
        return "Strong Core", "rgba(255,75,43,0.1)", "#FF4B2B"
    elif score >= 60:
        return "Solid Base", "rgba(245,158,11,0.1)", "#f59e0b"
    elif score >= 40:
        return "Needs Polish", "rgba(234,88,12,0.1)", "#ea580c"
    else:
        return "At Risk", "rgba(239,68,68,0.1)", "#ef4444"


def create_radar_chart(scores: dict) -> go.Figure:
    labels = ["Skills", "Experience", "Education", "Formatting", "Impact"]
    values = [
        scores["skills_relevance"], scores["experience_quality"],
        scores["education"], scores["formatting"], scores["impact_metrics"],
    ]
    values.append(values[0])
    labels.append(labels[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=labels, fill="toself",
        fillcolor="rgba(255, 75, 43, 0.15)",
        line=dict(color="#FF4B2B", width=3),
        marker=dict(size=10, color="#FF416C"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100],
                            tickfont=dict(size=10, color="#64748b"),
                            gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.05)"),
            angularaxis=dict(tickfont=dict(size=12, color="#94a3b8", family="Plus Jakarta Sans"),
                             gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.05)")),
        showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=60, t=30, b=30), height=320,
    )
    return fig


def create_bar_chart(scores: dict) -> go.Figure:
    categories = {
        "Impact & Metrics": scores["impact_metrics"],
        "Formatting": scores["formatting"],
        "Education": scores["education"],
        "Experience": scores["experience_quality"],
        "Skills": scores["skills_relevance"],
    }
    colors = []
    for v in categories.values():
        if v >= 75: colors.append("#FF4B2B")
        elif v >= 60: colors.append("#f59e0b")
        elif v >= 40: colors.append("#ea580c")
        else: colors.append("#ef4444")

    fig = go.Figure(go.Bar(
        x=list(categories.values()), y=list(categories.keys()), orientation="h",
        marker=dict(color=colors, line=dict(width=0), cornerradius=8),
        text=[f"  {v}" for v in categories.values()], textposition="outside",
        textfont=dict(size=14, color="#f8fafc", family="JetBrains Mono"),
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 115], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(tickfont=dict(size=13, color="#94a3b8", family="Plus Jakarta Sans"), showgrid=False),
        margin=dict(l=10, r=40, t=10, b=10), height=230,
    )
    return fig


def render_card(title: str, emoji: str, items: list[str], color: str, icon_bg: str):
    items_html = ""
    for item in items:
        items_html += f'''<div class="card-item">
            <div class="card-bullet" style="background: {color};"></div>
            <div>{item}</div>
        </div>'''
    st.markdown(f"""
    <div class="glass-card">
        <div class="card-header">
            <div class="card-icon" style="background: {icon_bg};">{emoji}</div>
            <div class="card-label" style="color: {color};">{title}</div>
        </div>
        {items_html}
    </div>""", unsafe_allow_html=True)


def render_skills(skills: list[str]):
    chips = "".join(f'<span class="skill-chip">{s}</span>' for s in skills)
    st.markdown(f"""
    <div class="glass-card">
        <div class="card-header">
            <div class="card-icon" style="background: rgba(255, 75, 43, 0.1);">⚡</div>
            <div class="card-label">Identified Expertise</div>
        </div>
        <div class="skills-grid">{chips}</div>
    </div>""", unsafe_allow_html=True)


def section_divider(title: str):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-line"></div>
        <div class="section-title">{title}</div>
        <div class="section-line" style="background: linear-gradient(to left, rgba(255, 75, 43, 0.3), transparent);"></div>
    </div>""", unsafe_allow_html=True)


# ── Main UI ───────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Resume Intelligence</div>
    <div class="hero-subtitle">Premium resume audit, competitive benchmarking, and precision JD matching</div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📄 Analyze", "⚖️ Compare", "🎯 JD Match", "✍️ AI Rewrite"])


# ═════════════════════════════════════════════════════════════════════
# TAB 1: ANALYZE (existing feature)
# ═════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="upload-wrapper">', unsafe_allow_html=True)
    col_upload, col_role = st.columns([2.5, 1.5])
    with col_upload:
        uploaded_file = st.file_uploader(
            "📄 Upload Resume", type=["pdf"], key="analyze_file",
            help="Text-based PDF only, up to 10MB", label_visibility="collapsed",
        )
    with col_role:
        job_role = st.text_input(
            "🎯 Target Role", placeholder="e.g. Backend Engineer", key="analyze_role",
            help="Optional — get tailored feedback", label_visibility="collapsed",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        if st.button("✨  Analyze Resume", use_container_width=True, type="primary", key="btn_analyze"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            for pct, msg in [(15, "📄 Parsing PDF..."), (35, "🔍 Extracting..."), (55, "🧠 AI analyzing..."), (75, "📊 Scoring..."), (90, "✨ Generating...")]:
                progress_bar.progress(pct)
                status_text.markdown(f"<p style='text-align:center; color:#94a3b8; font-size:0.9rem;'>{msg}</p>", unsafe_allow_html=True)
                time.sleep(0.3)

            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {}
                if job_role.strip():
                    data["job_role"] = job_role.strip()
                response = requests.post(f"{API_URL}/analyze", files=files, data=data, timeout=60)
                progress_bar.progress(100); status_text.empty(); progress_bar.empty()
                if response.status_code != 200:
                    st.error(f"❌ {response.json().get('detail', 'Unknown error')}"); st.stop()
                result = response.json()
            except requests.ConnectionError:
                progress_bar.empty(); status_text.empty()
                st.error("❌ Cannot connect to backend. Is the server running?"); st.stop()
            except Exception as e:
                progress_bar.empty(); status_text.empty()
                st.error(f"❌ {str(e)}"); st.stop()

            # Results
            score = result["overall_score"]
            score_color = get_score_color(score)
            verdict, verdict_bg, verdict_color = get_verdict(score)
            pct = score * 3.6

            section_divider("ANALYSIS RESULTS")

            st.markdown(f"""
            <div class="score-section">
                <div class="score-ring-wrapper">
                    <div class="score-ring-bg"></div>
                    <div class="score-ring-fill" style="background: conic-gradient(from 0deg, {score_color} 0deg, {score_color} {pct}deg, rgba(0,0,0,0.03) {pct}deg);"></div>
                    <div class="score-inner">
                        <div class="score-number" style="color: {score_color};">{score}</div>
                        <div class="score-max">/ 100</div>
                    </div>
                </div>
                <div class="score-verdict" style="background: {verdict_bg}; color: {verdict_color}; border: 1px solid {verdict_color}22;">{verdict}</div>
            </div>""", unsafe_allow_html=True)

            st.markdown(f'<div class="summary-card"><div class="summary-text">{result["summary"]}</div></div>', unsafe_allow_html=True)

            cat = result["category_scores"]
            stat_cols = st.columns(5)
            for col, (label, val, icon) in zip(stat_cols, [("Skills", cat["skills_relevance"], "🛠️"), ("Experience", cat["experience_quality"], "💼"), ("Education", cat["education"], "🎓"), ("Formatting", cat["formatting"], "📐"), ("Impact", cat["impact_metrics"], "📈")]):
                c = get_score_color(val)
                col.markdown(f'<div class="stat-card"><div style="font-size:1.2rem;margin-bottom:4px;">{icon}</div><div class="stat-value" style="color:{c};">{val}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

            section_divider("CATEGORY BREAKDOWN")
            ch1, ch2 = st.columns(2)
            with ch1: st.plotly_chart(create_radar_chart(result["category_scores"]), use_container_width=True, config={"displayModeBar": False})
            with ch2: st.plotly_chart(create_bar_chart(result["category_scores"]), use_container_width=True, config={"displayModeBar": False})

            section_divider("SKILLS DETECTED")
            render_skills(result["extracted_skills"])

            section_divider("DETAILED FEEDBACK")
            c1, c2 = st.columns(2)
            with c1:
                render_card("Strengths", "💪", result["strengths"], "#16a34a", "rgba(34,197,94,0.08)")
                render_card("ATS Tips", "🤖", result["ats_tips"], "#d97706", "rgba(217,119,6,0.08)")
            with c2:
                render_card("Weaknesses", "⚠️", result["weaknesses"], "#ea580c", "rgba(234,88,12,0.08)")
                render_card("Suggestions", "💡", result["suggestions"], "#4f46e5", "rgba(99,102,241,0.08)")
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📄</div>
            <div class="empty-title">Upload a resume to analyze</div>
            <div class="empty-desc">Get scores, feedback, and ATS tips in seconds</div>
        </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# TAB 2: COMPARE
# ═════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="upload-wrapper">', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Resume A**")
        file_a = st.file_uploader("Upload Resume A", type=["pdf"], key="compare_a", label_visibility="collapsed")
    with col_b:
        st.markdown("**Resume B**")
        file_b = st.file_uploader("Upload Resume B", type=["pdf"], key="compare_b", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if file_a and file_b:
        if st.button("⚖️  Compare Resumes", use_container_width=True, type="primary", key="btn_compare"):
            with st.spinner("🧠 Comparing resumes with AI..."):
                try:
                    files = {
                        "file_a": (file_a.name, file_a.getvalue(), "application/pdf"),
                        "file_b": (file_b.name, file_b.getvalue(), "application/pdf"),
                    }
                    response = requests.post(f"{API_URL}/compare", files=files, timeout=60)
                    if response.status_code != 200:
                        st.error(f"❌ {response.json().get('detail', 'Error')}"); st.stop()
                    result = response.json()
                except requests.ConnectionError:
                    st.error("❌ Backend not running."); st.stop()
                except Exception as e:
                    st.error(f"❌ {str(e)}"); st.stop()

            section_divider("COMPARISON RESULTS")

            # Winner banner
            winner = result["winner"]
            st.markdown(f"""
            <div class="summary-card" style="border-color: rgba(34,197,94,0.2);">
                <div style="font-size:1.5rem; margin-bottom:0.5rem;">🏆 Winner: <strong>Resume {winner}</strong></div>
                <div class="summary-text">{result['summary']}</div>
            </div>""", unsafe_allow_html=True)

            # Side-by-side profiles
            p1, p2 = st.columns(2)
            for col, profile, label, is_winner in [(p1, result["resume_a"], "A", winner == "A"), (p2, result["resume_b"], "B", winner == "B")]:
                border = "border-color: rgba(34,197,94,0.3);" if is_winner else ""
                badge = " 🏆" if is_winner else ""
                sc = get_score_color(profile["overall_score"])
                skills_html = "".join(f'<span class="skill-chip">{s}</span>' for s in profile["top_skills"])
                col.markdown(f"""
                <div class="glass-card" style="{border}">
                    <div class="card-header">
                        <div class="card-label" style="color: #4f46e5;">Resume {label}{badge} — {profile['name']}</div>
                    </div>
                    <div style="text-align:center; margin: 0.5rem 0;">
                        <div class="stat-value" style="color:{sc}; font-size:2.5rem;">{profile['overall_score']}</div>
                        <div class="stat-label">Overall Score</div>
                    </div>
                    <div class="card-item">📅 Experience: {profile['experience_years']}</div>
                    <div class="card-item">✅ Strongest: {profile['strongest_area']}</div>
                    <div class="card-item">⚠️ Weakest: {profile['weakest_area']}</div>
                    <div style="margin-top: 0.8rem;">
                        <div class="skills-grid">{skills_html}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # Detailed comparison
            render_card("Detailed Comparison", "📋", result["detailed_comparison"], "#4f46e5", "rgba(99,102,241,0.08)")

            st.markdown(f"""
            <div class="summary-card">
                <div class="card-label" style="color: #16a34a; margin-bottom: 0.5rem;">💼 Recommendation</div>
                <div class="summary-text">{result['recommendation']}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">⚖️</div>
            <div class="empty-title">Upload two resumes to compare</div>
            <div class="empty-desc">Side-by-side AI comparison with winner recommendation</div>
        </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# TAB 3: JD MATCH
# ═════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="upload-wrapper">', unsafe_allow_html=True)
    col_resume, col_jd = st.columns([1, 1.5])
    with col_resume:
        jd_file = st.file_uploader("Upload Resume", type=["pdf"], key="match_file", label_visibility="collapsed")
    with col_jd:
        jd_text = st.text_area(
            "Job Description", placeholder="Paste the job description here...",
            height=150, key="match_jd", label_visibility="collapsed",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    if jd_file and jd_text.strip():
        if st.button("🎯  Check Match", use_container_width=True, type="primary", key="btn_match"):
            with st.spinner("🧠 Analyzing resume vs job description..."):
                try:
                    files = {"file": (jd_file.name, jd_file.getvalue(), "application/pdf")}
                    data = {"job_description": jd_text.strip()}
                    response = requests.post(f"{API_URL}/match", files=files, data=data, timeout=60)
                    if response.status_code != 200:
                        st.error(f"❌ {response.json().get('detail', 'Error')}"); st.stop()
                    result = response.json()
                except requests.ConnectionError:
                    st.error("❌ Backend not running."); st.stop()
                except Exception as e:
                    st.error(f"❌ {str(e)}"); st.stop()

            section_divider("MATCH RESULTS")

            # Match percentage gauge
            match_pct = result["match_percentage"]
            match_color = get_score_color(match_pct)
            pct_deg = match_pct * 3.6

            st.markdown(f"""
            <div class="score-section">
                <div class="score-ring-wrapper">
                    <div class="score-ring-bg"></div>
                    <div class="score-ring-fill" style="background: conic-gradient(from 0deg, {match_color} 0deg, {match_color} {pct_deg}deg, rgba(0,0,0,0.03) {pct_deg}deg);"></div>
                    <div class="score-inner">
                        <div class="score-number" style="color: {match_color};">{match_pct}%</div>
                        <div class="score-max">match</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown(f'<div class="summary-card"><div class="summary-text">{result["fit_summary"]}</div></div>', unsafe_allow_html=True)

            # Matched vs Missing skills
            m1, m2 = st.columns(2)
            with m1:
                matched_chips = "".join(f'<span class="skill-chip" style="border-color: rgba(34,197,94,0.3); color: #16a34a;">{s}</span>' for s in result["matched_skills"])
                st.markdown(f"""
                <div class="glass-card">
                    <div class="card-header"><div class="card-label" style="color: #16a34a;">✅ Matched Skills</div></div>
                    <div class="skills-grid">{matched_chips}</div>
                </div>""", unsafe_allow_html=True)

                render_card("Requirements Met", "✅", result["matched_requirements"], "#16a34a", "rgba(34,197,94,0.08)")

            with m2:
                missing_chips = "".join(f'<span class="skill-chip" style="border-color: rgba(239,68,68,0.3); color: #dc2626;">{s}</span>' for s in result["missing_skills"])
                st.markdown(f"""
                <div class="glass-card">
                    <div class="card-header"><div class="card-label" style="color: #dc2626;">❌ Missing Skills</div></div>
                    <div class="skills-grid">{missing_chips}</div>
                </div>""", unsafe_allow_html=True)

                render_card("Gaps", "⚠️", result["gaps"], "#ea580c", "rgba(234,88,12,0.08)")

            render_card("How to Improve", "💡", result["suggestions_to_improve"], "#4f46e5", "rgba(99,102,241,0.08)")
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🎯</div>
            <div class="empty-title">Upload resume + paste job description</div>
            <div class="empty-desc">See match percentage, skill gaps, and how to improve</div>
        </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# TAB 4: AI REWRITE
# ═════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="upload-wrapper">', unsafe_allow_html=True)
    bullet_input = st.text_area(
        "Bullet Points", height=180, key="rewrite_bullets",
        placeholder="Paste your weak resume bullet points here, one per line...\n\nExample:\n- Worked on backend stuff\n- Helped with team projects\n- Did some testing",
        label_visibility="collapsed",
    )
    rewrite_context = st.text_input(
        "Context", placeholder="Optional: your role/industry (e.g. 'Senior Software Engineer at a fintech startup')",
        key="rewrite_context", label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if bullet_input.strip():
        if st.button("✍️  Rewrite with AI", use_container_width=True, type="primary", key="btn_rewrite"):
            with st.spinner("🧠 Transforming your bullet points..."):
                try:
                    payload = {"bullet_text": bullet_input.strip()}
                    if rewrite_context.strip():
                        payload["context"] = rewrite_context.strip()
                    response = requests.post(f"{API_URL}/rewrite", json=payload, timeout=60)
                    if response.status_code != 200:
                        st.error(f"❌ {response.json().get('detail', 'Error')}"); st.stop()
                    result = response.json()
                except requests.ConnectionError:
                    st.error("❌ Backend not running."); st.stop()
                except Exception as e:
                    st.error(f"❌ {str(e)}"); st.stop()

            section_divider("REWRITTEN BULLET POINTS")

            for i, rw in enumerate(result["rewrites"], 1):
                st.markdown(f"""
                <div class="glass-card">
                    <div class="card-header">
                        <div class="card-icon" style="background: rgba(99,102,241,0.08);">#{i}</div>
                        <div class="card-label" style="color: #4f46e5;">Bullet Point {i}</div>
                    </div>
                    <div class="card-item" style="color: #94a3b8; text-decoration: line-through;">
                        ❌ {rw['original']}
                    </div>
                    <div class="card-item" style="color: #16a34a; font-weight: 600;">
                        ✅ {rw['rewritten']}
                    </div>
                    <div class="card-item" style="color: #64748b; font-size: 0.85rem; font-style: italic;">
                        💡 {rw['explanation']}
                    </div>
                </div>""", unsafe_allow_html=True)

            render_card("General Writing Tips", "📝", result["general_tips"], "#d97706", "rgba(217,119,6,0.08)")
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">✍️</div>
            <div class="empty-title">Paste weak bullet points to rewrite</div>
            <div class="empty-desc">AI transforms boring bullets into powerful, quantified impact statements</div>
        </div>""", unsafe_allow_html=True)


# ── Footer ──
st.markdown("""
<div class="footer">
    Crafted with Precision & Code
</div>""", unsafe_allow_html=True)

