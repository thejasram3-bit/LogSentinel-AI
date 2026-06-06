import streamlit as st
import pandas as pd
import time
import json
from model import parse_log_file, predict_block
from explainer import explain_anomaly

# ── Page Config ─────────────────────────────────
st.set_page_config(
    page_title="LogSentinel AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── FULL CSS ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
    background-color: #080c14 !important;
    color: #e2eaf8 !important;
}

.main { background-color: #080c14 !important; }
.block-container {
    padding: 1.5rem 2rem !important;
    max-width: 1400px !important;
}

.main::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: #0d1420 !important;
    border-right: 1px solid #1a2540 !important;
}
[data-testid="stSidebar"] * { color: #e2eaf8 !important; }

[data-testid="stMetric"] {
    background: #0d1420 !important;
    border: 1px solid #1a2540 !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stMetric"]:hover {
    border-color: #00d4ff !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.15) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] {
    color: #4a6080 !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: #00d4ff !important;
    font-size: 28px !important;
    font-weight: 800 !important;
}
[data-testid="stMetricDelta"] { font-size: 11px !important; }

.stButton > button {
    background: linear-gradient(135deg, #00d4ff, #0099cc) !important;
    color: #080c14 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px 24px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 16px rgba(0,212,255,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 28px rgba(0,212,255,0.5) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #1a2540 !important;
    color: #7090b0 !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #00d4ff !important;
    color: #00d4ff !important;
    box-shadow: 0 0 12px rgba(0,212,255,0.2) !important;
}

[data-testid="stFileUploader"] {
    background: #0d1420 !important;
    border: 2px dashed #1a2540 !important;
    border-radius: 14px !important;
    padding: 20px !important;
    transition: all 0.3s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #00d4ff !important;
    background: rgba(0,212,255,0.03) !important;
}

[data-testid="stExpander"] {
    background: #0d1420 !important;
    border: 1px solid #1a2540 !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
    transition: all 0.3s !important;
    overflow: hidden !important;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(255,61,110,0.4) !important;
    box-shadow: 0 0 20px rgba(255,61,110,0.08) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    padding: 14px 18px !important;
    color: #e2eaf8 !important;
}

[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #00d4ff, #00e5a0) !important;
    border-radius: 4px !important;
    box-shadow: 0 0 10px rgba(0,212,255,0.4) !important;
}
[data-testid="stProgressBar"] {
    background: #1a2540 !important;
    border-radius: 4px !important;
}

hr {
    border-color: #1a2540 !important;
    margin: 1.2rem 0 !important;
}

[data-testid="stSlider"] > div > div > div {
    background: linear-gradient(90deg, #00d4ff, #0099cc) !important;
}
[data-testid="stSlider"] > div > div > div > div {
    background: #00d4ff !important;
    box-shadow: 0 0 10px rgba(0,212,255,0.5) !important;
}

[data-testid="stCodeBlock"] {
    background: #111927 !important;
    border: 1px solid #1a2540 !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}

[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid !important;
}

[data-testid="stSpinner"] { color: #00d4ff !important; }

[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    border: 1px solid #1a2540 !important;
    color: #7090b0 !important;
    border-radius: 8px !important;
    transition: all 0.3s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: #00d4ff !important;
    color: #00d4ff !important;
    box-shadow: 0 0 12px rgba(0,212,255,0.2) !important;
}

[data-testid="stCheckbox"] label { color: #7090b0 !important; }

[data-testid="stNumberInput"] input {
    background: #111927 !important;
    border-color: #1a2540 !important;
    color: #e2eaf8 !important;
    border-radius: 8px !important;
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0d1420; }
::-webkit-scrollbar-thumb { background: #1a2540; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #00d4ff; }
</style>
""", unsafe_allow_html=True)

# ── HEADER HTML ──────────────────────────────────
st.markdown("""
<div style="background: linear-gradient(135deg, #0d1420 0%, #111927 100%); border: 1px solid #1a2540; border-radius: 18px; padding: 32px 36px; margin-bottom: 24px; position: relative; overflow: hidden;">
<div style="position: absolute; top: -40px; right: -40px; width: 200px; height: 200px; background: radial-gradient(circle, rgba(0,212,255,0.08) 0%, transparent 70%); border-radius: 50%;"></div>
<div style="position: absolute; bottom: -60px; left: 20%; width: 300px; height: 200px; background: radial-gradient(circle, rgba(162,89,255,0.06) 0%, transparent 70%); border-radius: 50%;"></div>
<div style="display: flex; align-items: center; gap: 18px; position: relative;">
<div style="width: 56px; height: 56px; background: linear-gradient(135deg, #00d4ff, #a259ff); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 28px; box-shadow: 0 0 24px rgba(0,212,255,0.4); flex-shrink: 0;">🛡️</div>
<div>
<div style="font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800; letter-spacing: -0.5px; background: linear-gradient(90deg, #ffffff, #00d4ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1;">LogSentinel AI</div>
<div style="font-size: 13px; color: #4a6080; font-family: 'JetBrains Mono', monospace; margin-top: 4px;">Log Anomaly Detection + LLM Explanation System</div>
</div>
<div style="margin-left: auto; display: flex; align-items: center; gap: 10px;">
<div style="display: flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 20px; border: 1px solid rgba(0,229,160,0.3); background: rgba(0,229,160,0.08); font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00e5a0;">
<div style="width: 8px; height: 8px; background: #00e5a0; border-radius: 50%; box-shadow: 0 0 6px #00e5a0; animation: none;"></div>
LIVE MONITORING
</div>
<div style="padding: 8px 16px; border-radius: 20px; border: 1px solid rgba(162,89,255,0.3); background: rgba(162,89,255,0.08); font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #a259ff;">Transformer · F1: 93.27%</div>
</div>
</div>
<div style="margin-top: 20px; display: flex; gap: 32px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #4a6080; border-top: 1px solid #1a2540; padding-top: 16px; position: relative;">
<span>📋 Upload HDFS log</span>
<span style="color: #1a2540;">→</span>
<span>🔍 Drain3 Parser</span>
<span style="color: #1a2540;">→</span>
<span>🧠 Transformer Model</span>
<span style="color: #1a2540;">→</span>
<span>✨ Gemini LLM</span>
<span style="color: #1a2540;">→</span>
<span>📊 Live Results</span>
</div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="text-align:center; padding: 10px 0 20px;">
<div style="width: 52px; height: 52px; background: linear-gradient(135deg, #00d4ff, #a259ff); border-radius: 14px; display: inline-flex; align-items: center; justify-content: center; font-size: 26px; box-shadow: 0 0 20px rgba(0,212,255,0.35); margin-bottom: 10px;">🛡️</div>
<div style="font-size:18px; font-weight:800; color:#e2eaf8;">LogSentinel AI</div>
<div style="font-size:10px; color:#4a6080; font-family:'JetBrains Mono',monospace;">v1.0 · System Pipeline</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("**⚙️ Detection Settings**", unsafe_allow_html=True)
    threshold = st.slider("Anomaly Threshold", 0.3, 0.9, 0.5, 0.05, help="Higher = stricter (fewer alerts)")
    show_normal = st.checkbox("Show normal blocks", value=False)
    explain_top = st.number_input("Max LLM explanations", 1, 20, 5, help="Gemini API rate limit: 15/min")

    st.divider()

    st.markdown("**📊 Model Performance**", unsafe_allow_html=True)
    st.markdown("""
<div style="display:flex; flex-direction:column; gap:8px; margin-top:8px;">
<div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:#111927; border-radius:8px; border:1px solid #1a2540;">
<span style="font-size:12px; color:#7090b0;">F1 Score</span>
<span style="font-size:13px; font-weight:700; color:#00d4ff;">93.27%</span>
</div>
<div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:#111927; border-radius:8px; border:1px solid #1a2540;">
<span style="font-size:12px; color:#7090b0;">Precision</span>
<span style="font-size:13px; font-weight:700; color:#00e5a0;">98.61%</span>
</div>
<div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:#111927; border-radius:8px; border:1px solid #1a2540;">
<span style="font-size:12px; color:#7090b0;">Recall</span>
<span style="font-size:13px; font-weight:700; color:#ffb800;">88.48%</span>
</div>
<div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:#111927; border-radius:8px; border:1px solid #1a2540;">
<span style="font-size:12px; color:#7090b0;">Params</span>
<span style="font-size:13px; font-weight:700; color:#a259ff;">27,617</span>
</div>
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.markdown("**🔗 Pipeline Status**", unsafe_allow_html=True)
    st.markdown("""
<div style="display:flex; flex-direction:column; gap:6px; margin-top:8px;">
<div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#7090b0;">
<div style="width:8px;height:8px;background:#00e5a0;border-radius:50%; box-shadow:0 0 6px #00e5a0;flex-shrink:0;"></div>
Drain3 Log Parser
</div>
<div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#7090b0;">
<div style="width:8px;height:8px;background:#00e5a0;border-radius:50%; box-shadow:0 0 6px #00e5a0;flex-shrink:0;"></div>
Transformer Model
</div>
<div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#7090b0;">
<div style="width:8px;height:8px;background:#a259ff;border-radius:50%; box-shadow:0 0 6px #a259ff;flex-shrink:0;"></div>
Gemini LLM API
</div>
<div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#7090b0;">
<div style="width:8px;height:8px;background:#00e5a0;border-radius:50%; box-shadow:0 0 6px #00e5a0;flex-shrink:0;"></div>
Cache System
</div>
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.markdown("""
<div style="font-size:10px; color:#2a3a50; text-align:center; line-height:1.6;">
LogSentinel Active Monitoring<br>
System fully functional
</div>
""", unsafe_allow_html=True)

# ── UPLOAD SECTION ───────────────────────────────
st.markdown("""
<div style="background: #0d1420; border: 1px solid #1a2540; border-radius: 14px; padding: 24px; margin-bottom: 20px;">
<div style="font-size:14px; font-weight:700; margin-bottom:12px; color:#e2eaf8;">📂 Upload Log File</div>
<div style="font-size:12px; color:#4a6080; font-family:'JetBrains Mono',monospace; margin-bottom:14px;">Supports HDFS format logs · .log · .txt</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drop your HDFS log file here",
    type=["log", "txt"],
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)

col_a, col_b, col_c = st.columns([2, 2, 8])
with col_a:
    demo_clicked = st.button("▶ Run Demo Log", type="secondary", use_container_width=True)
with col_b:
    if st.button("🗑️ Clear", type="secondary", use_container_width=True):
        st.rerun()

# ── DEMO DATA ────────────────────────────────────
DEMO_LOG = """081109 203615 148 INFO dfs.DataNode$DataXceiver: Receiving block blk_9999000001 src: /10.251.100.1:50010 dest: /10.251.100.1:50010
081109 203615 149 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_9999000001 terminating
081109 203615 150 INFO dfs.DataNode$PacketResponder: Received block blk_9999000001 of size 67108864 from /10.251.100.1
081109 203616 155 INFO dfs.DataNode$DataXceiver: Receiving block blk_8888000002 src: /10.251.101.1:50010 dest: /10.251.101.1:50010
081109 203616 156 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_8888000002 terminating
081109 203616 159 INFO dfs.DataNode$PacketResponder: Received block blk_8888000002 of size 67108864 from /10.251.101.1
081109 203618 169 ERROR dfs.DataNode$DataXceiver: java.io.IOException for block blk_6666000004
081109 203618 170 ERROR dfs.DataNode$DataXceiver: java.io.IOException for block blk_6666000004
081109 203618 171 ERROR dfs.DataNode$DataXceiver: java.io.IOException for block blk_6666000004
081109 203618 172 INFO dfs.DataNode$DataXceiver: Receiving block blk_6666000004 src: /10.251.103.1:50010
081109 203619 174 INFO dfs.DataNode$DataXceiver: Receiving block blk_5555000005 src: /10.251.104.1:50010
081109 203619 175 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_5555000005 terminating
081109 203619 178 INFO dfs.DataNode$PacketResponder: Received block blk_5555000005 of size 67108864 from /10.251.104.1
081109 203620 181 ERROR dfs.DataNode$DataXceiver: java.io.IOException for block blk_4444000006
081109 203620 182 ERROR dfs.DataNode$DataXceiver: java.io.IOException for block blk_4444000006
081109 203620 183 ERROR dfs.DataNode$DataXceiver: java.io.IOException for block blk_4444000006
081109 203620 184 ERROR dfs.DataNode$DataXceiver: java.io.IOException for block blk_4444000006
081109 203620 185 ERROR dfs.DataNode$DataXceiver: java.io.IOException for block blk_4444000006"""

if demo_clicked:
    log_text    = DEMO_LOG
    run_analysis = True
elif uploaded:
    log_text    = uploaded.read().decode("utf-8", errors="ignore")
    run_analysis = True
else:
    run_analysis = False
    st.markdown("""
<div style="text-align:center; padding:40px; background:#0d1420; border:1px dashed #1a2540; border-radius:14px; color:#2a3a50; font-family:'JetBrains Mono',monospace; font-size:12px;">
↑ Upload a log file or click Run Demo Log to see the system in action
</div>
""", unsafe_allow_html=True)

# ── ANALYSIS ─────────────────────────────────────
if run_analysis:
    st.divider()

    # Scanning animation
    scan_placeholder = st.empty()
    scan_placeholder.markdown("""
<div style="background: #0d1420; border:1px solid #1a2540; border-radius:12px; padding:20px; text-align:center; font-family:'JetBrains Mono',monospace;">
<div style="font-size:24px; margin-bottom:8px;">🔍</div>
<div style="color:#00d4ff; font-size:13px; font-weight:600;">Parsing log file through Drain3 pipeline...</div>
<div style="color:#4a6080; font-size:11px; margin-top:4px;">Extracting Block IDs → Mapping Events → Building Sequences</div>
</div>
""", unsafe_allow_html=True)

    blocks = parse_log_file(log_text)
    time.sleep(0.4)
    scan_placeholder.empty()

    if not blocks:
        st.markdown("""
<div style="background:rgba(255,61,110,0.08); border:1px solid rgba(255,61,110,0.3); border-radius:12px; padding:20px; text-align:center; color:#ff3d6e;">
❌ No HDFS blocks found. Check that your log file is in HDFS format.
</div>
""", unsafe_allow_html=True)
        st.stop()

    # Model inference animation
    model_placeholder = st.empty()
    model_placeholder.markdown("""
<div style="background: #0d1420; border:1px solid rgba(0,212,255,0.2); border-radius:12px; padding:20px; text-align:center; font-family:'JetBrains Mono',monospace; box-shadow: 0 0 20px rgba(0,212,255,0.08);">
<div style="font-size:24px; margin-bottom:8px;">🧠</div>
<div style="color:#00d4ff; font-size:13px; font-weight:600;">Transformer model analyzing sequences...</div>
<div style="color:#4a6080; font-size:11px; margin-top:4px;">27,617 parameters · 93.27% F1 · Running inference</div>
</div>
""", unsafe_allow_html=True)

    results = []
    for block_id, events in blocks.items():
        prob = predict_block(events)
        results.append({
            "block_id": block_id,
            "events":   events,
            "prob":     prob,
            "anomaly":  prob >= threshold
        })
    time.sleep(0.3)
    model_placeholder.empty()

    total     = len(results)
    anomalies = [r for r in results if r["anomaly"]]
    normals   = [r for r in results if not r["anomaly"]]
    n_anom    = len(anomalies)
    n_norm    = len(normals)

    # ── Summary Cards ────────────────────────────
    st.markdown("""
<div style="font-size:16px; font-weight:700; margin-bottom:14px; color:#e2eaf8;">
📊 Analysis Summary
</div>
""", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Blocks Analyzed", total)
    with m2:
        st.metric("🔴 Anomalies Detected", n_anom,
                  delta=f"{n_anom/total*100:.1f}% of total",
                  delta_color="inverse")
    with m3:
        st.metric("🟢 Normal Blocks", n_norm)
    with m4:
        st.metric("⚡ Threshold", f"{threshold*100:.0f}%")

    # ── Health bar ───────────────────────────────
    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    health = n_norm / total if total > 0 else 1
    health_color = "#00e5a0" if health > 0.8 else "#ffb800" if health > 0.5 else "#ff3d6e"
    health_label = "Healthy" if health > 0.8 else "Warning" if health > 0.5 else "Critical"

    st.markdown(f"""
<div style="background:#0d1420; border:1px solid #1a2540; border-radius:12px; padding:16px 20px; margin-bottom:8px;">
<div style="display:flex; justify-content:space-between; margin-bottom:8px;">
<span style="font-size:12px; color:#7090b0; font-family:'JetBrains Mono',monospace;">SYSTEM HEALTH</span>
<span style="font-size:12px; font-weight:700; color:{health_color}; font-family:'JetBrains Mono',monospace;">{health_label} · {health*100:.1f}%</span>
</div>
<div style="background:#1a2540; border-radius:4px; height:8px; overflow:hidden;">
<div style="width:{health*100:.1f}%; height:100%; background:linear-gradient(90deg, {health_color}, {health_color}99); border-radius:4px; box-shadow: 0 0 10px {health_color}66;"></div>
</div>
</div>
""", unsafe_allow_html=True)

    st.divider()
     # ── Anomaly Results ───────────────────────────
    if n_anom == 0:
        st.markdown(f"""
<div style="background:rgba(0,229,160,0.06); border:1px solid rgba(0,229,160,0.2); border-radius:14px; padding:32px; text-align:center;">
<div style="font-size:36px; margin-bottom:12px;">✅</div>
<div style="font-size:18px; font-weight:700; color:#00e5a0; margin-bottom:6px;">All Clear — No Anomalies Detected</div>
<div style="font-size:13px; color:#4a6080;">All {total} blocks passed the anomaly threshold check</div>
</div>
""", unsafe_allow_html=True)

    else:
        st.markdown(f"""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
<div style="width:36px; height:36px; background:rgba(255,61,110,0.15); border:1px solid rgba(255,61,110,0.3); border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:18px;">🔴</div>
<div>
<div style="font-size:16px; font-weight:700; color:#ff3d6e;">{n_anom} Anomalies Detected</div>
<div style="font-size:11px; color:#4a6080; font-family:'JetBrains Mono',monospace;">Sorted by anomaly probability · LLM explanation for top {explain_top}</div>
</div>
</div>
""", unsafe_allow_html=True)

        # Sort by probability
        anomalies_sorted = sorted(anomalies, key=lambda x: x["prob"], reverse=True)
        explained_count  = 0

        for r in anomalies_sorted:
            block_id  = r["block_id"]
            events    = r["events"]
            prob      = r["prob"]
            event_str = ",".join(events)

            prob_pct = prob * 100
            prob_color = "#ff3d6e" if prob > 0.8 else "#ffb800" if prob > 0.6 else "#a259ff"

            with st.expander(
                f"🔴  {block_id}   ·   {prob_pct:.1f}% anomaly score",
                expanded=(explained_count == 0)
            ):
                col1, col2 = st.columns([1, 2])

                with col1:
                    # Anomaly score ring visual
                    st.markdown(f"""
<div style="background:#111927; border:1px solid #1a2540; border-radius:12px; padding:16px; margin-bottom:12px; text-align:center;">
<div style="font-size:36px; font-weight:800; color:{prob_color}; font-family:'JetBrains Mono',monospace; text-shadow: 0 0 20px {prob_color}66;">{prob_pct:.1f}%</div>
<div style="font-size:10px; color:#4a6080; font-family:'JetBrains Mono',monospace; letter-spacing:1px; margin-top:4px;">ANOMALY SCORE</div>
</div>
<div style="background:#111927; border:1px solid #1a2540; border-radius:10px; padding:12px;">
<div style="font-size:10px; color:#4a6080; margin-bottom:6px; font-family:'JetBrains Mono',monospace;">EVENT SEQUENCE</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:11px; color:#00d4ff; word-break:break-all; line-height:1.8;">{" → ".join(events)}</div>
<div style="font-size:10px; color:#4a6080; margin-top:8px;">{len(events)} events · Block ID matched</div>
</div>
""", unsafe_allow_html=True)

                with col2:
                    if explained_count < explain_top:
                        with st.spinner("✨ Gemini AI generating explanation..."):
                            exp = explain_anomaly(block_id, events, prob)
                        explained_count += 1

                        sev = exp.get("severity", "High").strip().lower()
                        sev_config = {
                            "critical": ("#ff3d6e", "rgba(255,61,110,0.1)", "rgba(255,61,110,0.25)", "🔴"),
                            "high":     ("#ffb800", "rgba(255,184,0,0.1)", "rgba(255,184,0,0.25)",   "🟠"),
                            "medium":   ("#a259ff", "rgba(162,89,255,0.1)", "rgba(162,89,255,0.25)",  "🟡"),
                            "low":      ("#00e5a0", "rgba(0,229,160,0.1)", "rgba(0,229,160,0.25)",   "🟢"),
                        }
                        clr, bg, border, icon = sev_config.get(
                            sev, ("#ffb800","rgba(255,184,0,0.1)","rgba(255,184,0,0.25)","🟠"))

                        sev_label = exp.get('severity', 'High')

                        st.markdown(f"""
<div style="background:#111927; border:1px solid #1a2540; border-radius:12px; padding:18px; height:100%;">
<div style="display:inline-flex; align-items:center; gap:6px; padding:5px 12px; border-radius:20px; background:{bg}; border:1px solid {border}; margin-bottom:14px;">
<span>{icon}</span>
<span style="font-size:11px; font-weight:700; color:{clr}; letter-spacing:0.5px;">{sev_label.upper()}</span>
</div>

<div style="margin-bottom:12px;">
<div style="font-size:10px; color:#4a6080; font-family:'JetBrains Mono',monospace; letter-spacing:1px; margin-bottom:4px;">📌 WHAT IS HAPPENING</div>
<div style="font-size:13px; color:#e2eaf8; line-height:1.6;">{exp.get('what', '—')}</div>
</div>

<div style="margin-bottom:12px;">
<div style="font-size:10px; color:#4a6080; font-family:'JetBrains Mono',monospace; letter-spacing:1px; margin-bottom:4px;">🔧 LIKELY CAUSE</div>
<div style="font-size:12px; color:#a0b4cc; line-height:1.6;">{exp.get('cause', '—')}</div>
</div>

<div style="margin-bottom:12px; background:rgba(0,212,255,0.04); border:1px solid rgba(0,212,255,0.15); border-radius:8px; padding:10px 12px;">
<div style="font-size:10px; color:#4a6080; font-family:'JetBrains Mono',monospace; letter-spacing:1px; margin-bottom:4px;">⚡ RECOMMENDED ACTION</div>
<div style="font-size:12px; color:#00d4ff; line-height:1.6; font-weight:600;">{exp.get('action', '—')}</div>
</div>

<div style="background:rgba(255,61,110,0.04); border:1px solid rgba(255,61,110,0.15); border-radius:8px; padding:10px 12px;">
<div style="font-size:10px; color:#4a6080; font-family:'JetBrains Mono',monospace; letter-spacing:1px; margin-bottom:4px;">⚠️ IF IGNORED</div>
<div style="font-size:12px; color:#ff7096; line-height:1.6;">{exp.get('impact', '—')}</div>
</div>
</div>
""", unsafe_allow_html=True)
                    else:
                        st.markdown("""
<div style="background:#111927; border:1px dashed #1a2540; border-radius:10px; padding:20px; text-align:center; color:#4a6080; font-size:12px;">
LLM explanation limit reached.<br>
Increase limit in sidebar settings.
</div>
""", unsafe_allow_html=True)

    # ── Normal blocks ─────────────────────────────
    if show_normal and n_norm > 0:
        st.divider()
        st.markdown(f"""
<div style="font-size:15px; font-weight:700; color:#00e5a0; margin-bottom:12px;">
🟢 Normal Blocks ({n_norm})
</div>
""", unsafe_allow_html=True)

        for r in normals:
            st.markdown(f"""
<div style="display:flex; align-items:center; gap:12px; padding:10px 14px; background:#0d1420; border:1px solid #1a2540; border-radius:8px; margin-bottom:4px; font-family:'JetBrains Mono',monospace; font-size:11px;">
<div style="width:8px;height:8px;background:#00e5a0;border-radius:50%; box-shadow:0 0 6px #00e5a0;flex-shrink:0;"></div>
<span style="color:#7090b0;">{r['block_id']}</span>
<span style="color:#1a2540;">·</span>
<span style="color:#4a6080;">{','.join(r['events'])}</span>
<span style="margin-left:auto; color:#00e5a0;">{r['prob']*100:.1f}%</span>
</div>
""", unsafe_allow_html=True)

    # ── Export ────────────────────────────────────
    st.divider()
    st.markdown("""
<div style="font-size:14px; font-weight:700; margin-bottom:12px; color:#e2eaf8;">
💾 Export Results
</div>
""", unsafe_allow_html=True)

    export_data = [{
        "block_id":     r["block_id"],
        "events":       ",".join(r["events"]),
        "anomaly_prob": r["prob"],
        "is_anomaly":   r["anomaly"]
    } for r in results]

    col_d1, col_d2 = st.columns([2, 8])
    with col_d1:
        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name="logsentinel_results.json",
            mime="application/json",
            use_container_width=True
        )

# ── Footer ────────────────────────────────────────
st.markdown("""
<div style="margin-top: 48px; background: #0d1420; border: 1px solid #1a2540; border-radius: 12px; padding: 20px 28px; display: flex; align-items: center; justify-content: space-between;">
<div style="font-size:13px; font-weight:700; color:#e2eaf8;">🛡️ LogSentinel AI</div>
<div style="font-size:10px; color:#2a3a50; font-family:'JetBrains Mono',monospace; text-align:center;">System Active</div>
<div style="display:flex; gap:8px;">
<span style="font-size:10px; padding:3px 10px; border-radius:20px; background:rgba(0,212,255,0.08); border:1px solid rgba(0,212,255,0.15); color:#00d4ff; font-family:'JetBrains Mono',monospace;">Transformer</span>
<span style="font-size:10px; padding:3px 10px; border-radius:20px; background:rgba(162,89,255,0.08); border:1px solid rgba(162,89,255,0.15); color:#a259ff; font-family:'JetBrains Mono',monospace;">Gemini LLM</span>
</div>
</div>
""", unsafe_allow_html=True)

    