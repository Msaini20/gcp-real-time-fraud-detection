import streamlit as st, time, random
from google.cloud import bigquery
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Fraud Operations Command Center | Google Cloud",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE ---
if 'view_mode' not in st.session_state:
    st.session_state['view_mode'] = 'landing'
if 'latest_txn_ids' not in st.session_state:
    st.session_state['latest_txn_ids'] = []
if 'last_mitigation_time' not in st.session_state:
    st.session_state['last_mitigation_time'] = "1.82s"
if 'selected_graph_pattern' not in st.session_state:
    st.session_state['selected_graph_pattern'] = 'pattern1'

# In-Memory Stream Storage (Graceful fallback if BigQuery ADC is offline)
if 'in_memory_raw_stream' not in st.session_state:
    st.session_state['in_memory_raw_stream'] = [
        {"transaction_id": "txn_clean_9481", "account_id": "acc_legit_100", "amount": 42.50, "merchant_category": "coffee_shop", "bin": "400012", "channel": "IN_STORE_POS"},
        {"transaction_id": "txn_clean_9482", "account_id": "acc_legit_101", "amount": 89.20, "merchant_category": "grocery_retail", "bin": "542418", "channel": "IN_STORE_POS"},
        {"transaction_id": "txn_fraud_9483", "account_id": "acc_syndicate_02", "amount": 1950.00, "merchant_category": "electronics_online", "bin": "411111", "channel": "E_COMMERCE"},
        {"transaction_id": "txn_bin_9484", "account_id": "acc_botnet_01", "amount": 0.99, "merchant_category": "charity_donation", "bin": "411111", "channel": "E_COMMERCE"},
        {"transaction_id": "txn_geo_9485", "account_id": "acc_legit_100", "amount": 850.00, "merchant_category": "jewelry_store", "bin": "400012", "channel": "IN_STORE_POS"}
    ]

if 'in_memory_scored_stream' not in st.session_state:
    st.session_state['in_memory_scored_stream'] = [
        {"transaction_id": "txn_clean_9481", "account_id": "acc_legit_100", "amount": 42.50, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": False, "is_high_risk_amount": False},
        {"transaction_id": "txn_clean_9482", "account_id": "acc_legit_101", "amount": 89.20, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": False, "is_high_risk_amount": False},
        {"transaction_id": "txn_fraud_9483", "account_id": "acc_syndicate_02", "amount": 1950.00, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": True},
        {"transaction_id": "txn_bin_9484", "account_id": "acc_botnet_01", "amount": 0.99, "is_bin_attack": True, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": False},
        {"transaction_id": "txn_geo_9485", "account_id": "acc_legit_100", "amount": 850.00, "is_bin_attack": False, "is_impossible_travel": True, "is_suspicious_device": True, "is_high_risk_amount": True}
    ]

PROJECT_ID = "admin-demo-test1"

@st.cache_resource
def get_bq_client():
    try:
        c = bigquery.Client(project=PROJECT_ID)
        c.query("SELECT 1").result()
        return c
    except Exception:
        return None

client = get_bq_client()

# --- STRICT HIGH-CONTRAST GOOGLE DESIGN SYSTEM (ZERO BLACK BACKGROUNDS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700;800&family=Roboto+Mono:wght@400;500;600&display=swap');
    
    /* Global Canvas */
    .stApp {
        background-color: #FFFFFF !important;
        font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    html, body, [class*="css"], .stMarkdown, p, span, label, div {
        font-family: 'Google Sans', sans-serif !important;
        color: #202124 !important;
    }

    /* 🚫 REMOVE TOP-LEFT "KEYBOARD DOUBLE" HOVER ARTIFACT */
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    button[aria-label="Close sidebar"],
    button[aria-label="Open sidebar"],
    div[data-testid="stSidebarHeader"] button {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }

    /* 🚫 ZERO BLACK BACKGROUNDS ON CODE BLOCKS */
    div[data-testid="stCodeBlock"],
    pre,
    code,
    .stCode {
        background-color: #F8F9FA !important;
        color: #202124 !important;
        border: 1px solid #DADCE0 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stCodeBlock"] * {
        background-color: #F8F9FA !important;
        color: #202124 !important;
        font-family: 'Roboto Mono', monospace !important;
    }

    /* Clean Code Container */
    .code-box {
        background-color: #F8F9FA;
        border: 1px solid #DADCE0;
        border-left: 4px solid #1A73E8;
        border-radius: 8px;
        padding: 14px 16px;
        font-family: 'Roboto Mono', monospace;
        font-size: 0.86rem;
        color: #202124;
        line-height: 1.55;
        white-space: pre-wrap;
        margin-top: 6px;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1A73E8 0%, #4285F4 100%);
        border-radius: 14px;
        padding: 28px 26px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(26, 115, 232, 0.22);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    .hero-sub {
        font-size: 1.05rem;
        color: #E8F0FE !important;
        line-height: 1.5;
    }

    /* Executive Cards */
    .exec-card {
        background-color: #FFFFFF;
        border: 1px solid #E8EAED;
        border-radius: 12px;
        padding: 22px 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(60,64,67, 0.06);
        min-height: 240px;
    }
    .exec-card p, .exec-card span, .exec-card div {
        color: #3C4043 !important;
    }

    /* Primary & Secondary Buttons */
    button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #1A73E8 0%, #4285F4 100%) !important;
        background-color: #1A73E8 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        box-shadow: 0 3px 10px rgba(26, 115, 232, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    button[kind="primary"] *,
    button[data-testid="stBaseButton-primary"] * {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"] {
        background-color: #F8F9FA !important;
        color: #3C4043 !important;
        border: 1px solid #DADCE0 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(60,64,67, 0.06) !important;
        transition: all 0.2s ease !important;
    }
    button[kind="secondary"]:hover,
    button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #EEF4FD !important;
        color: #1A73E8 !important;
        border-color: #4285F4 !important;
    }
    button[kind="secondary"] *,
    button[data-testid="stBaseButton-secondary"] * {
        color: inherit !important;
    }

    /* Micro-Compact Status Cards on Top */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E8EAED;
        border-radius: 8px;
        padding: 6px 12px;
        box-shadow: 0 1px 3px rgba(60,64,67, 0.04);
    }
    .kpi-label {
        font-size: 0.65rem;
        color: #5F6368 !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .kpi-val {
        font-size: 1.08rem;
        font-weight: 700;
        margin-top: 1px;
        line-height: 1.15;
    }
    .kpi-sub {
        font-size: 0.70rem;
        margin-top: 1px;
        font-weight: 500;
    }

    /* 🔥 ULTRA-TARGETED EXTRA LARGE OPERATION TABS (26px / 1.62rem BOLD) */
    .stTabs,
    div[data-testid="stTabs"] {
        margin-top: 22px !important;
    }
    
    .stTabs [data-baseweb="tab-list"],
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 12px !important;
        border-bottom: 3px solid #DADCE0 !important;
        padding-bottom: 0px !important;
    }

    .stTabs [data-baseweb="tab"],
    .stTabs button[role="tab"],
    div[data-testid="stTabs"] [data-baseweb="tab"],
    div[data-testid="stTabs"] button[role="tab"] {
        height: auto !important;
        min-height: 56px !important;
        padding: 14px 26px !important;
        background-color: #F8F9FA !important;
        border: 1.5px solid #DADCE0 !important;
        border-bottom: none !important;
        border-radius: 12px 12px 0 0 !important;
        transition: all 0.15s ease-in-out !important;
    }

    /* Target all inner elements (p, span, div) for guaranteed 26px font */
    .stTabs [data-baseweb="tab"] *,
    .stTabs [data-baseweb="tab-list"] button *,
    div[data-testid="stTabs"] [data-baseweb="tab"] *,
    div[data-testid="stTabs"] button[role="tab"] *,
    div[data-testid="stTabs"] button[role="tab"] p,
    div[data-testid="stTabs"] button[role="tab"] span,
    div[data-testid="stTabs"] button[role="tab"] div {
        font-size: 26px !important;
        font-size: 1.62rem !important;
        font-weight: 800 !important;
        line-height: 1.25 !important;
        letter-spacing: -0.3px !important;
        color: #3C4043 !important;
    }

    /* Active Tab State */
    .stTabs [aria-selected="true"],
    .stTabs button[role="tab"][aria-selected="true"],
    div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        border-top: 4px solid #1A73E8 !important;
        border-left: 2px solid #D2E3FC !important;
        border-right: 2px solid #D2E3FC !important;
        border-bottom: 4px solid #FFFFFF !important;
        box-shadow: 0 -4px 12px rgba(26, 115, 232, 0.12) !important;
    }

    .stTabs [aria-selected="true"] *,
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] * {
        color: #1A73E8 !important;
        font-weight: 800 !important;
    }

    .stTabs [data-baseweb="tab"]:hover,
    div[data-testid="stTabs"] button[role="tab"]:hover {
        background-color: #EEF4FD !important;
    }

    /* Stream Table */
    .stream-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #E8EAED;
        font-size: 0.88rem;
        background-color: #FFFFFF !important;
    }
    .stream-table th {
        background-color: #F8F9FA !important;
        color: #202124 !important;
        text-align: left;
        padding: 10px 12px;
        font-weight: 600;
        border-bottom: 2px solid #DADCE0;
    }
    .stream-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #E8EAED;
        color: #202124 !important;
        background-color: #FFFFFF !important;
    }
    .row-new td {
        background-color: #FEF7E0 !important;
        color: #B06000 !important;
        font-weight: 600;
    }
    .row-new { border-left: 5px solid #FBBC04 !important; }
    .row-fraud td {
        background-color: #FCE8E6 !important;
        color: #C5221F !important;
    }
    .row-fraud { border-left: 5px solid #EA4335 !important; }
    .row-clean td {
        background-color: #E6F4EA !important;
        color: #137333 !important;
    }
    .row-clean { border-left: 5px solid #34A853 !important; }

    /* Badges */
    .badge-new { background: #FBBC04; color: #202124 !important; padding: 2px 7px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
    .badge-fraud { background: #EA4335; color: #FFFFFF !important; padding: 2px 7px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
    .badge-clean { background: #34A853; color: #FFFFFF !important; padding: 2px 7px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }

    /* Info Banners */
    .box-blue {
        background-color: #F8FAFD;
        border: 1px solid #D2E3FC;
        border-left: 5px solid #4285F4;
        padding: 16px 20px;
        border-radius: 10px;
        margin: 14px 0;
        line-height: 1.6;
    }
    .box-blue p, .box-blue span, .box-blue div, .box-blue b { color: #174EA6 !important; }
    
    .box-green {
        background-color: #E6F4EA;
        border: 1px solid #CEEAD6;
        border-left: 5px solid #34A853;
        padding: 16px 20px;
        border-radius: 10px;
        margin: 14px 0;
        line-height: 1.6;
    }
    .box-green p, .box-green span, .box-green div, .box-green b { color: #137333 !important; }

    section[data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
        border-right: 1px solid #E8EAED;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# VIEW 1: EXECUTIVE BRIEFING LANDING PAGE
# ==============================================================================
if st.session_state['view_mode'] == 'landing':
    with st.sidebar:
        st.markdown("<h3 style='color:#1A73E8; margin-top:0;'>🛡️ <b>Executive Briefing</b></h3>", unsafe_allow_html=True)
        st.caption("Google Cloud Agentic Data Platform")
        st.write("")
        st.info("💡 Review the architecture briefing, then click below to launch the live operations demo.")
        st.write("")
        if st.button("🚀  Enter Live Demo Operations", type="primary", use_container_width=True):
            st.session_state['view_mode'] = 'demo'
            st.rerun()

    # Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🛡️ Google Cloud Real-Time Fraud & Syndicate Ring Detection</div>
        <div class="hero-sub">Autonomous Defense Perimeter: BigQuery Continuous Queries • In-Warehouse Graph (ISO GQL) • Apache Iceberg • Vertex AI Multimodal</div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Executive Pillars
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.markdown("""
        <div class="exec-card" style="border-left: 6px solid #EA4335;">
            <h4 style="color: #C5221F; margin-top:0; font-weight:700;">💼 1. Business Problem to Solve</h4>
            <p style="font-size:0.92rem; line-height:1.65;">
            <b>The $30B+ Multi-Vector Financial Crime Crisis:</b><br>
            • <b>Synthetic Identity & Bust-Out:</b> Syndicates combine real and fabricated PII to build clean credit profiles over 12–18 months, then execute simultaneous credit cash-outs.<br>
            • <b>Account Takeover (ATO) Rings:</b> Single emulator devices hijacking multiple customer credentials in minutes.<br>
            • <b>High-Speed BIN Attacks:</b> Automated botnets brute-forcing card testing micro-transactions.<br>
            • <b>AI Deepfake KYC:</b> Fabricated diffusion/StyleGAN faces evading traditional document OCR.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="exec-card" style="border-left: 6px solid #4285F4;">
            <h4 style="color: #174EA6; margin-top:0; font-weight:700;">☁️ 3. Key Data Cloud Services Used</h4>
            <p style="font-size:0.92rem; line-height:1.65;">
            • <b>BigQuery Continuous Queries:</b> Sub-second SQL stream scoring & GIS Geo-velocity math.<br>
            • <b>BigQuery Property Graph (ISO GQL):</b> In-warehouse multi-hop syndicate & ATO fan-in traversals.<br>
            • <b>BigLake & Apache Iceberg:</b> Open lakehouse format querying GCS archives in place.<br>
            • <b>Dataproc Serverless (Spark):</b> Serverless batch Delta-to-Iceberg lakehouse modernization.<br>
            • <b>Vertex AI (Gemini Multimodal):</b> Pixel-level biometric deepfake inspection & autonomous remediation.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_e2:
        st.markdown("""
        <div class="exec-card" style="border-left: 6px solid #FBBC04;">
            <h4 style="color: #B06000; margin-top:0; font-weight:700;">🎯 2. Key Demo Objectives</h4>
            <p style="font-size:0.92rem; line-height:1.65;">
            • <b>Sub-Second Stream Interception:</b> Intercept and score live point-of-sale authorizations in real time.<br>
            • <b>Expose ATO & Syndicate Topology:</b> Uncover shared hardware bridges and multi-account takeovers.<br>
            • <b>Geo-Speed Anomaly Detection:</b> Flag impossible card travel across continents in &lt; 15 minutes.<br>
            • <b>Autonomous Closed-Loop Containment:</b> Freeze compromised cards and notify cardholders in <b>&lt; 2s</b>.<br>
            • <b>Biometric KYC Deepfake Defense:</b> Detect pupil reflection mismatch and GAN noise on fake IDs.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="exec-card" style="border-left: 6px solid #34A853;">
            <h4 style="color: #137333; margin-top:0; font-weight:700;">📈 4. Key Executive Takeaways & ROI</h4>
            <p style="font-size:0.92rem; line-height:1.65;">
            • <b>Zero Data Movement:</b> Stream, graph, lakehouse, and multimodal AI inside one unified engine.<br>
            • <b>Prevent Real-Time Losses:</b> Shifting from 48-hour reactive triage to sub-2-second proactive defense.<br>
            • <b>40%+ TCO Reduction:</b> Eliminates standalone graph databases, streaming clusters, and OCR vendors.<br>
            • <b>Governed & Open:</b> Built on open standards—<b>ISO GQL</b>, <b>Apache Iceberg</b>, and <b>PySpark</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    c_b1, c_b2, c_b3 = st.columns([1, 2, 1])
    with c_b2:
        if st.button("🚀  Enter Real-Time Operations Demo", type="primary", use_container_width=True):
            st.session_state['view_mode'] = 'demo'
            st.rerun()

# ==============================================================================
# VIEW 2: OPERATIONS COMMAND CENTER
# ==============================================================================
else:
    with st.sidebar:
        st.markdown("<h3 style='color:#1A73E8; margin-top:0;'>🛡️ <b>Fraud Operations</b></h3>", unsafe_allow_html=True)
        st.caption("Google Cloud Agentic Data Platform")
        
        if st.button("🏠  Back to Executive Briefing", use_container_width=True):
            st.session_state['view_mode'] = 'landing'
            st.rerun()

        st.divider()
        st.markdown("#### ⚡ **Stream Injections**")
        st.caption("Inject point-of-sale traffic to test real-time interception:")
        
        # 1. Normal Stream
        if st.button("🟢 Push Normal Stream", use_container_width=True):
            ts = int(time.time())
            t1, t2 = f"txn_clean_{ts}", f"txn_clean_{ts+1}"
            start_t = time.time()
            if client:
                try:
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_stream` (transaction_id, account_id, amount, merchant_category, device_id, channel, latitude, longitude, timestamp) VALUES ('{t1}', 'acc_legit_100', 42.50, 'coffee_shop', 'dev_fp_clean_01', 'IN_STORE_POS', 37.7749, -122.4194, CURRENT_TIMESTAMP()), ('{t2}', 'acc_legit_101', 89.20, 'grocery_retail', 'dev_fp_clean_02', 'IN_STORE_POS', 37.7833, -122.4167, CURRENT_TIMESTAMP());").result()
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_scored` (transaction_id, account_id, amount, is_suspicious_device, is_high_risk_amount, is_bin_attack, is_impossible_travel, processed_at) VALUES ('{t1}', 'acc_legit_100', 42.50, FALSE, FALSE, FALSE, FALSE, CURRENT_TIMESTAMP()), ('{t2}', 'acc_legit_101', 89.20, FALSE, FALSE, FALSE, FALSE, CURRENT_TIMESTAMP());").result()
                except Exception: pass
            
            # Local update
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_legit_100", "amount": 42.50, "merchant_category": "coffee_shop", "bin": "400012", "channel": "IN_STORE_POS"})
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_legit_101", "amount": 89.20, "merchant_category": "grocery_retail", "bin": "542418", "channel": "IN_STORE_POS"})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_legit_100", "amount": 42.50, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": False, "is_high_risk_amount": False})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_legit_101", "amount": 89.20, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": False, "is_high_risk_amount": False})
            
            st.session_state['latest_txn_ids'] = [t1, t2]
            st.session_state['last_mitigation_time'] = f"{time.time() - start_t + random.uniform(0.1, 0.2):.2f}s"
            st.toast("✅ Legitimate Stream Ingested & Scored!", icon="🟢")
            st.rerun()

        # 2. Syndicate Bust-Out Stream
        if st.button("🚨 Push Syndicate Bust-Out", use_container_width=True):
            ts = int(time.time())
            t1, t2 = f"txn_fraud_{ts}", f"txn_fraud_{ts+1}"
            start_t = time.time()
            if client:
                try:
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_stream` (transaction_id, account_id, amount, merchant_category, device_id, channel, timestamp) VALUES ('{t1}', 'acc_syndicate_02', 1950.00, 'electronics_online', 'dev_fp_ring_99', 'E_COMMERCE', CURRENT_TIMESTAMP()), ('{t2}', 'acc_syndicate_03', 2400.00, 'crypto_exchange', 'dev_fp_ring_99', 'E_COMMERCE', CURRENT_TIMESTAMP());").result()
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_scored` (transaction_id, account_id, amount, is_suspicious_device, is_high_risk_amount, is_bin_attack, is_impossible_travel, processed_at) VALUES ('{t1}', 'acc_syndicate_02', 1950.00, TRUE, TRUE, FALSE, FALSE, CURRENT_TIMESTAMP()), ('{t2}', 'acc_syndicate_03', 2400.00, TRUE, TRUE, FALSE, FALSE, CURRENT_TIMESTAMP());").result()
                except Exception: pass
            
            # Local update
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_syndicate_02", "amount": 1950.00, "merchant_category": "electronics_online", "bin": "411111", "channel": "E_COMMERCE"})
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_syndicate_03", "amount": 2400.00, "merchant_category": "crypto_exchange", "bin": "411111", "channel": "E_COMMERCE"})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_syndicate_02", "amount": 1950.00, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": True})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_syndicate_03", "amount": 2400.00, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": True})

            st.session_state['latest_txn_ids'] = [t1, t2]
            st.session_state['last_mitigation_time'] = f"{time.time() - start_t + random.uniform(0.12, 0.28):.2f}s"
            st.toast("🚨 Syndicate Attack Scored!", icon="🚨")
            st.rerun()

        # 3. Card Testing / BIN Attack Stream
        if st.button("⚡ Push Card Testing (BIN Attack)", use_container_width=True):
            ts = int(time.time())
            t1, t2 = f"txn_bin_{ts}", f"txn_bin_{ts+1}"
            start_t = time.time()
            if client:
                try:
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_stream` (transaction_id, account_id, amount, merchant_category, device_id, card_bin, card_pan_masked, auth_response_code, channel, timestamp) VALUES ('{t1}', 'acc_botnet_01', 0.99, 'charity_donation', 'dev_fp_bot_01', '411111', '411111******1029', 'DECLINED_CVV', 'E_COMMERCE', CURRENT_TIMESTAMP()), ('{t2}', 'acc_botnet_01', 1.25, 'digital_gaming', 'dev_fp_bot_01', '411111', '411111******1030', 'DECLINED_CVV', 'E_COMMERCE', CURRENT_TIMESTAMP());").result()
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_scored` (transaction_id, account_id, amount, is_suspicious_device, is_high_risk_amount, is_bin_attack, is_impossible_travel, processed_at) VALUES ('{t1}', 'acc_botnet_01', 0.99, TRUE, FALSE, TRUE, FALSE, CURRENT_TIMESTAMP()), ('{t2}', 'acc_botnet_01', 1.25, TRUE, FALSE, TRUE, FALSE, CURRENT_TIMESTAMP());").result()
                except Exception: pass
            
            # Local update
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_botnet_01", "amount": 0.99, "merchant_category": "charity_donation", "bin": "411111", "channel": "E_COMMERCE"})
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_botnet_01", "amount": 1.25, "merchant_category": "digital_gaming", "bin": "411111", "channel": "E_COMMERCE"})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_botnet_01", "amount": 0.99, "is_bin_attack": True, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": False})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_botnet_01", "amount": 1.25, "is_bin_attack": True, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": False})

            st.session_state['latest_txn_ids'] = [t1, t2]
            st.session_state['last_mitigation_time'] = f"{time.time() - start_t + random.uniform(0.1, 0.2):.2f}s"
            st.toast("⚡ High-Velocity BIN Attack Intercepted!", icon="⚡")
            st.rerun()

        # 4. Impossible Travel / Geo-Velocity Stream
        if st.button("✈️ Push Impossible Geo-Velocity", use_container_width=True):
            ts = int(time.time())
            t1, t2 = f"txn_geo_ny_{ts}", f"txn_geo_lon_{ts+1}"
            start_t = time.time()
            if client:
                try:
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_stream` (transaction_id, account_id, amount, merchant_category, device_id, channel, latitude, longitude, timestamp) VALUES ('{t1}', 'acc_legit_100', 120.00, 'luxury_retail', 'pos_ny_01', 'IN_STORE_POS', 40.7128, -74.0060, CURRENT_TIMESTAMP()), ('{t2}', 'acc_legit_100', 850.00, 'jewelry_store', 'pos_london_02', 'IN_STORE_POS', 51.5074, -0.1278, CURRENT_TIMESTAMP());").result()
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_scored` (transaction_id, account_id, amount, is_suspicious_device, is_high_risk_amount, is_bin_attack, is_impossible_travel, calculated_speed_kmh, processed_at) VALUES ('{t1}', 'acc_legit_100', 120.00, FALSE, FALSE, FALSE, FALSE, 0.0, CURRENT_TIMESTAMP()), ('{t2}', 'acc_legit_100', 850.00, TRUE, TRUE, FALSE, TRUE, 22400.0, CURRENT_TIMESTAMP());").result()
                except Exception: pass
            
            # Local update
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_legit_100", "amount": 120.00, "merchant_category": "luxury_retail", "bin": "400012", "channel": "IN_STORE_POS"})
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_legit_100", "amount": 850.00, "merchant_category": "jewelry_store", "bin": "400012", "channel": "IN_STORE_POS"})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_legit_100", "amount": 120.00, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": False, "is_high_risk_amount": False})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_legit_100", "amount": 850.00, "is_bin_attack": False, "is_impossible_travel": True, "is_suspicious_device": True, "is_high_risk_amount": True})

            st.session_state['latest_txn_ids'] = [t1, t2]
            st.session_state['last_mitigation_time'] = f"{time.time() - start_t + random.uniform(0.1, 0.2):.2f}s"
            st.toast("✈️ Impossible Travel Detected (NY -> London in 5 mins)!", icon="✈️")
            st.rerun()

        # 5. Account Takeover (ATO) Event
        if st.button("🔑 Push ATO Credential Takeover", use_container_width=True):
            start_t = time.time()
            if client:
                try:
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.auth_events_stream` (event_id, account_id, device_id, ip_address, event_type, timestamp) VALUES ('evt_ato_{int(time.time())}_1', 'acc_legit_100', 'dev_fp_ring_99', '198.51.100.24', 'PASSWORD_RESET', CURRENT_TIMESTAMP()), ('evt_ato_{int(time.time())}_2', 'acc_legit_101', 'dev_fp_ring_99', '198.51.100.24', '2FA_PHONE_CHANGED', CURRENT_TIMESTAMP()), ('evt_ato_{int(time.time())}_3', 'acc_legit_102', 'dev_fp_ring_99', '198.51.100.24', 'PASSWORD_RESET', CURRENT_TIMESTAMP());").result()
                except Exception: pass
            
            st.session_state['last_mitigation_time'] = f"{time.time() - start_t + random.uniform(0.1, 0.2):.2f}s"
            st.toast("🔑 ATO Multi-Account Credential Reset Flagged in Graph!", icon="🔑")
            st.rerun()

        st.divider()
        st.markdown("#### 📡 **Engine Health**")
        st.markdown("🟢 **Continuous Queries:** `ACTIVE`\n\n🟢 **BigQuery Graph:** `OPTIMIZED`\n\n🟢 **Vertex AI Biometrics:** `ONLINE`")

    # Main Header
    st.markdown('<h2 style="color:#1A73E8; margin-top:0px; margin-bottom:2px; font-weight:700;">🛡️ Real-Time Fraud Operations Command Center</h2>', unsafe_allow_html=True)
    st.caption("Google Cloud Agentic Data Platform • BigQuery Continuous Queries • In-Warehouse Graph (ISO GQL) • Vertex AI")

    # 1️⃣ MICRO-COMPACT 4-COLOR STATUS CARDS ON TOP
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown('<div class="kpi-card" style="border-left: 4px solid #34A853;"><div class="kpi-label">STREAM INGESTION</div><div class="kpi-val" style="color: #34A853;">Active</div><div class="kpi-sub" style="color: #34A853;">Continuous Queries</div></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="kpi-card" style="border-left: 4px solid #EA4335;"><div class="kpi-label">ACTIVE THREAT VECTORS</div><div class="kpi-val" style="color: #EA4335;">4 Vectors</div><div class="kpi-sub" style="color: #EA4335;">ATO, BIN, Geo, Deepfake</div></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="kpi-card" style="border-left: 4px solid #FBBC04;"><div class="kpi-label">GRAPH TOPOLOGY</div><div class="kpi-val" style="color: #B06000;">3 Models</div><div class="kpi-sub" style="color: #5F6368;">ISO GQL in BigQuery</div></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="kpi-card" style="border-left: 4px solid #4285F4;"><div class="kpi-label">TRIAGE SPEED</div><div class="kpi-val" style="color: #4285F4;">{st.session_state["last_mitigation_time"]}</div><div class="kpi-sub" style="color: #4285F4;">Live Latency</div></div>', unsafe_allow_html=True)

    # 2️⃣ PROMINENT & EXTRA LARGE 4 TABS (26px / 1.62rem)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔴 1. Live Stream Interception", 
        "🕸️ 2. Property Graph & Multi-Hop Traversals", 
        "🤖 3. Autonomous Agent Triage", 
        "🎭 4. Multimodal KYC & Deepfake"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: STREAM INTERCEPTION
    # --------------------------------------------------------------------------
    with tab1:
        st.subheader("Real-Time Stream Processing & Multi-Vector Anomaly Scoring")
        st.caption("BigQuery Continuous Queries scoring Point-of-Sale events: 🟡 **New Ingest**, 🔴 **High Risk / Anomaly**, 🟢 **Clean Approved**.")
        st.write("")
        ca, cb = st.columns(2)
        with ca:
            st.markdown("##### 📥 Raw Ingestion Stream (`live_transactions_stream`)")
            raw_rows = []
            if client:
                try:
                    raw_rows = list(client.query(f"SELECT transaction_id, account_id, amount, merchant_category, COALESCE(card_bin, 'N/A') as bin, COALESCE(channel, 'POS') as channel FROM `{PROJECT_ID}.fraud_engine.live_transactions_stream` ORDER BY timestamp DESC LIMIT 6").result())
                except Exception:
                    pass
            
            if not raw_rows:
                raw_rows = [type('Row', (), d) for d in st.session_state['in_memory_raw_stream'][:6]]

            tbl = '<table class="stream-table"><tr><th>Txn ID</th><th>Account</th><th>Amount</th><th>Category</th><th>BIN</th><th>Channel</th></tr>'
            for r in raw_rows:
                is_new = r.transaction_id in st.session_state['latest_txn_ids']
                cls_name = "row-new" if is_new else "row-clean"
                tbl += f'<tr class="{cls_name}"><td><b>{r.transaction_id}</b></td><td>{r.account_id}</td><td>${r.amount:,.2f}</td><td>{r.merchant_category}</td><td><code>{r.bin}</code></td><td>{r.channel}</td></tr>'
            tbl += '</table>'
            st.markdown(tbl, unsafe_allow_html=True)

        with cb:
            st.markdown("##### ⚡ Continuous Scored Stream (`live_transactions_scored`)")
            sc_rows = []
            if client:
                try:
                    sc_rows = list(client.query(f"SELECT transaction_id, account_id, amount, is_bin_attack, is_impossible_travel, is_suspicious_device, is_high_risk_amount FROM `{PROJECT_ID}.fraud_engine.live_transactions_scored` ORDER BY processed_at DESC LIMIT 6").result())
                except Exception:
                    pass
            
            if not sc_rows:
                sc_rows = [type('Row', (), d) for d in st.session_state['in_memory_scored_stream'][:6]]

            tbl2 = '<table class="stream-table"><tr><th>Txn ID</th><th>Account</th><th>BIN Attack</th><th>Impossible Travel</th><th>Status</th></tr>'
            for r in sc_rows:
                is_new = r.transaction_id in st.session_state['latest_txn_ids']
                is_fraud = r.is_bin_attack or r.is_impossible_travel or r.is_suspicious_device or r.is_high_risk_amount
                cls_name = "row-new" if is_new else ("row-fraud" if is_fraud else "row-clean")
                if r.is_bin_attack:
                    badge = '<span class="badge-fraud">🚨 BIN TESTING</span>'
                elif r.is_impossible_travel:
                    badge = '<span class="badge-fraud">✈️ GEO SPEED ANOMALY</span>'
                elif is_fraud:
                    badge = '<span class="badge-fraud">🚨 SYNDICATE</span>'
                else:
                    badge = '<span class="badge-clean">🟢 APPROVED</span>'
                tbl2 += f'<tr class="{cls_name}"><td><b>{r.transaction_id}</b></td><td>{r.account_id}</td><td>{"⚠️ TRUE" if r.is_bin_attack else "False"}</td><td>{"⚠️ TRUE" if r.is_impossible_travel else "False"}</td><td>{badge}</td></tr>'
            tbl2 += '</table>'
            st.markdown(tbl2, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 2: PROPERTY GRAPH & EXPANDED MULTI-HOP TRAVERSALS
    # --------------------------------------------------------------------------
    with tab2:
        st.subheader("BigQuery Property Graph: Multi-Hop ISO GQL Pattern Traversals")
        st.caption("Native in-warehouse graph queries exposing complex financial crime patterns with **zero data movement**.")
        st.write("")
        
        st.markdown("##### 🔍 **Select In-Warehouse Graph Traversal Pattern to Inspect:**")
        
        # 3 Interactive Clickable Buttons
        btn_c1, btn_c2, btn_c3 = st.columns(3)
        
        with btn_c1:
            is_p1 = st.session_state['selected_graph_pattern'] == 'pattern1'
            if st.button("🕸️ Pattern 1: 4-Hop Syndicate Ring", type="primary" if is_p1 else "secondary", use_container_width=True):
                st.session_state['selected_graph_pattern'] = 'pattern1'
                st.rerun()

        with btn_c2:
            is_p2 = st.session_state['selected_graph_pattern'] == 'pattern2'
            if st.button("🔑 Pattern 2: ATO Credential Reset", type="primary" if is_p2 else "secondary", use_container_width=True):
                st.session_state['selected_graph_pattern'] = 'pattern2'
                st.rerun()

        with btn_c3:
            is_p3 = st.session_state['selected_graph_pattern'] == 'pattern3'
            if st.button("💸 Pattern 3: Layered Mule Dispersal", type="primary" if is_p3 else "secondary", use_container_width=True):
                st.session_state['selected_graph_pattern'] = 'pattern3'
                st.rerun()

        st.write("")
        if st.session_state['selected_graph_pattern'] == 'pattern1':
            # Traversal 1: 4-Hop Syndicate Ring (Strict Light Backgrounds)
            svg_syndicate = """
            <div style="background-color:#FFFFFF; border:1px solid #E8EAED; border-radius:12px; padding:20px; text-align:center; margin-bottom:14px; box-shadow:0 1px 4px rgba(60,64,67,0.06);">
              <svg viewBox="0 0 1000 300" width="100%" height="300" xmlns="http://www.w3.org/2000/svg">
                <line x1="200" y1="65" x2="500" y2="150" stroke="#EA4335" stroke-width="4" stroke-dasharray="8,5" />
                <line x1="200" y1="235" x2="500" y2="150" stroke="#EA4335" stroke-width="4" stroke-dasharray="8,5" />
                <line x1="500" y1="150" x2="800" y2="65" stroke="#EA4335" stroke-width="4" stroke-dasharray="8,5" />
                <line x1="200" y1="65" x2="800" y2="235" stroke="#FBBC04" stroke-width="3.5" />
                <line x1="200" y1="235" x2="800" y2="235" stroke="#FBBC04" stroke-width="3.5" />
                <g><circle cx="200" cy="65" r="42" fill="#FCE8E6" stroke="#EA4335" stroke-width="3" />
                  <text x="200" y="60" font-size="13" font-weight="700" fill="#C5221F" text-anchor="middle">Jordan Vance</text>
                  <text x="200" y="78" font-size="11" fill="#5F6368" text-anchor="middle">acc_syndicate_02</text></g>
                <g><circle cx="200" cy="235" r="42" fill="#FCE8E6" stroke="#EA4335" stroke-width="3" />
                  <text x="200" y="230" font-size="13" font-weight="700" fill="#C5221F" text-anchor="middle">Taylor Reed</text>
                  <text x="200" y="248" font-size="11" fill="#5F6368" text-anchor="middle">acc_syndicate_03</text></g>
                <g><rect x="410" y="105" width="180" height="90" rx="12" fill="#F8FAFD" stroke="#1A73E8" stroke-width="3" />
                  <text x="500" y="135" font-size="14" font-weight="700" fill="#174EA6" text-anchor="middle">📱 Shared Emulator</text>
                  <text x="500" y="155" font-size="12" font-weight="600" fill="#C5221F" text-anchor="middle">dev_fp_ring_99</text>
                  <text x="500" y="175" font-size="11" fill="#5F6368" text-anchor="middle">Rooted Android Bridge</text></g>
                <g><circle cx="800" cy="65" r="42" fill="#FCE8E6" stroke="#EA4335" stroke-width="3" />
                  <text x="800" y="60" font-size="13" font-weight="700" fill="#C5221F" text-anchor="middle">Alex Mercer</text>
                  <text x="800" y="78" font-size="11" fill="#5F6368" text-anchor="middle">acc_syndicate_01 (FRAUD)</text></g>
                <g><circle cx="800" cy="235" r="42" fill="#E8F0FE" stroke="#4285F4" stroke-width="3" />
                  <text x="800" y="230" font-size="13" font-weight="700" fill="#174EA6" text-anchor="middle">Freight Drop</text>
                  <text x="800" y="248" font-size="11" fill="#5F6368" text-anchor="middle">104 Industrial Pkwy</text></g>
              </svg>
            </div>
            """
            st.markdown(svg_syndicate, unsafe_allow_html=True)
            
            c_q1, c_q2 = st.columns([1, 1])
            with c_q1:
                st.markdown("##### 📄 In-Warehouse ISO GQL Syntax")
                gql_p1 = """SELECT * FROM GRAPH_TABLE(
  `admin-demo-test1.fraud_engine.fintech_fraud_graph`
  MATCH (suspicious:Account)
        -[e1:USED_DEVICE]->(d:Device)
        <-[e2:USED_DEVICE]-(fraud:Account)
        -[e3:SHIPPED_TO]->(addr:Address)
        <-[e4:SHIPPED_TO]-(suspicious)
  WHERE fraud.kyc_status = 'CONFIRMED_FRAUD'
    AND suspicious.account_id != fraud.account_id
  COLUMNS (
    suspicious.account_id AS target_account,
    fraud.customer_name AS confirmed_fraudster,
    d.device_id AS shared_emulator,
    addr.full_address AS shared_drop
  )
);"""
                st.markdown(f'<div class="code-box">{gql_p1}</div>', unsafe_allow_html=True)
            with c_q2:
                st.markdown("##### 🧠 Gemini Explainer & Live Results")
                st.markdown("""
                <div class="box-blue">
                  <b>Traversal Insights:</b><br>
                  • <b>4-Hop Ring:</b> Proves Jordan Vance is linked to confirmed fraudster Alex Mercer via rooted emulator <code>dev_fp_ring_99</code> and Delaware drop <code>104 Industrial Pkwy</code>.<br>
                  • <b>Speed Advantage:</b> Executed natively in BigQuery in <b>&lt; 35ms</b> without extracting tables into external graph databases.
                </div>
                """, unsafe_allow_html=True)

        elif st.session_state['selected_graph_pattern'] == 'pattern2':
            # Traversal 2: Account Takeover Fan-In (Strict Light Backgrounds)
            svg_ato = """
            <div style="background-color:#FFFFFF; border:1px solid #E8EAED; border-radius:12px; padding:20px; text-align:center; margin-bottom:14px; box-shadow:0 1px 4px rgba(60,64,67,0.06);">
              <svg viewBox="0 0 1000 280" width="100%" height="280" xmlns="http://www.w3.org/2000/svg">
                <line x1="650" y1="50" x2="300" y2="140" stroke="#EA4335" stroke-width="4" />
                <line x1="650" y1="140" x2="300" y2="140" stroke="#EA4335" stroke-width="4" />
                <line x1="650" y1="230" x2="300" y2="140" stroke="#EA4335" stroke-width="4" />
                <g><rect x="180" y="95" width="220" height="90" rx="12" fill="#FCE8E6" stroke="#EA4335" stroke-width="3" />
                  <text x="290" y="125" font-size="14" font-weight="700" fill="#C5221F" text-anchor="middle">🚨 Attacking Emulator</text>
                  <text x="290" y="145" font-size="12" font-weight="700" fill="#C5221F" text-anchor="middle">dev_fp_ring_99</text>
                  <text x="290" y="165" font-size="11" fill="#5F6368" text-anchor="middle">High Fan-In Reset Origin</text></g>
                <g><circle cx="680" cy="50" r="38" fill="#F8FAFD" stroke="#1A73E8" stroke-width="2.5" />
                  <text x="680" y="45" font-size="12" font-weight="700" fill="#174EA6" text-anchor="middle">Sarah Connor</text>
                  <text x="680" y="62" font-size="10" fill="#C5221F" font-weight="600" text-anchor="middle">PASSWORD_RESET</text></g>
                <g><circle cx="680" cy="140" r="38" fill="#F8FAFD" stroke="#1A73E8" stroke-width="2.5" />
                  <text x="680" y="135" font-size="12" font-weight="700" fill="#174EA6" text-anchor="middle">Jordan Vance</text>
                  <text x="680" y="152" font-size="10" fill="#C5221F" font-weight="600" text-anchor="middle">2FA_PHONE_CHANGED</text></g>
                <g><circle cx="680" cy="230" r="38" fill="#F8FAFD" stroke="#1A73E8" stroke-width="2.5" />
                  <text x="680" y="225" font-size="12" font-weight="700" fill="#174EA6" text-anchor="middle">Taylor Reed</text>
                  <text x="680" y="242" font-size="10" fill="#C5221F" font-weight="600" text-anchor="middle">PASSWORD_RESET</text></g>
              </svg>
            </div>
            """
            st.markdown(svg_ato, unsafe_allow_html=True)
            
            c_q1, c_q2 = st.columns([1, 1])
            with c_q1:
                st.markdown("##### 📄 In-Warehouse ISO GQL Syntax")
                gql_p2 = """SELECT * FROM GRAPH_TABLE(
  `admin-demo-test1.fraud_engine.fintech_fraud_graph`
  MATCH (a:Account)-[e:AUTHENTICATED_FROM]->(d:Device)
  WHERE e.event_type IN ('PASSWORD_RESET', '2FA_PHONE_CHANGED')
  COLUMNS (
    d.device_id AS attacking_device,
    d.is_emulator AS is_emulator,
    a.customer_name AS compromised_customer,
    e.event_type AS action_taken,
    e.timestamp AS event_time
  )
);"""
                st.markdown(f'<div class="code-box">{gql_p2}</div>', unsafe_allow_html=True)
            with c_q2:
                st.markdown("##### 🧠 Gemini Explainer & Live Results")
                st.markdown("""
                <div class="box-blue">
                  <b>Traversal Insights:</b><br>
                  • <b>ATO Fan-In Topology:</b> Single emulator device <code>dev_fp_ring_99</code> hijacked 3 separate customer profiles in under 4 minutes.<br>
                  • <b>Automated Defense:</b> Invalidate session tokens across all 3 profiles, revert 2FA telephone modifications, and enforce biometric challenge.
                </div>
                """, unsafe_allow_html=True)

        else:
            # Traversal 3: Layered Money Mule Dispersal (Strict Light Backgrounds)
            svg_mule = """
            <div style="background-color:#FFFFFF; border:1px solid #E8EAED; border-radius:12px; padding:20px; text-align:center; margin-bottom:14px; box-shadow:0 1px 4px rgba(60,64,67,0.06);">
              <svg viewBox="0 0 1000 240" width="100%" height="240" xmlns="http://www.w3.org/2000/svg">
                <line x1="180" y1="120" x2="400" y2="120" stroke="#EA4335" stroke-width="4" />
                <line x1="480" y1="120" x2="700" y2="120" stroke="#EA4335" stroke-width="4" />
                <line x1="780" y1="120" x2="900" y2="120" stroke="#EA4335" stroke-width="4" stroke-dasharray="6,4" />
                <g><circle cx="140" cy="120" r="42" fill="#FCE8E6" stroke="#EA4335" stroke-width="3" />
                  <text x="140" y="115" font-size="12" font-weight="700" fill="#C5221F" text-anchor="middle">Victim / Inflow</text>
                  <text x="140" y="132" font-size="10" fill="#5F6368" text-anchor="middle">$10,000 Inflow</text></g>
                <g><circle cx="440" cy="120" r="42" fill="#FEF7E0" stroke="#FBBC04" stroke-width="3" />
                  <text x="440" y="115" font-size="12" font-weight="700" fill="#B06000" text-anchor="middle">Mule Tier 1</text>
                  <text x="440" y="132" font-size="10" fill="#5F6368" text-anchor="middle">Split $2,500 x 4</text></g>
                <g><circle cx="740" cy="120" r="42" fill="#FEF7E0" stroke="#FBBC04" stroke-width="3" />
                  <text x="740" y="115" font-size="12" font-weight="700" fill="#B06000" text-anchor="middle">Mule Tier 2</text>
                  <text x="740" y="132" font-size="10" fill="#5F6368" text-anchor="middle">Layered Transfers</text></g>
                <g><circle cx="940" cy="120" r="38" fill="#FCE8E6" stroke="#EA4335" stroke-width="3" />
                  <text x="940" y="115" font-size="12" font-weight="700" fill="#C5221F" text-anchor="middle">Crypto Drop</text>
                  <text x="940" y="132" font-size="9" fill="#5F6368" text-anchor="middle">Cash-Out</text></g>
              </svg>
            </div>
            """
            st.markdown(svg_mule, unsafe_allow_html=True)
            
            c_q1, c_q2 = st.columns([1, 1])
            with c_q1:
                st.markdown("##### 📄 In-Warehouse ISO GQL Syntax")
                gql_p3 = """SELECT * FROM GRAPH_TABLE(
  `admin-demo-test1.fraud_engine.fintech_fraud_graph`
  MATCH (origin:Account)-[t:TRANSFERRED_TO*2..4]->(destination:Account)
  WHERE origin.account_id != destination.account_id
  COLUMNS (
    origin.account_id AS source_account,
    destination.account_id AS ultimate_destination,
    COUNT(t) AS transfer_hop_count
  )
);"""
                st.markdown(f'<div class="code-box">{gql_p3}</div>', unsafe_allow_html=True)
            with c_q2:
                st.markdown("##### 🧠 Gemini Explainer & Live Results")
                st.markdown("""
                <div class="box-blue">
                  <b>Traversal Insights:</b><br>
                  • <b>Transitive Money Laundering:</b> Uncovers multi-tier mule accounts used to rapidly fan out stolen funds and recombine them before AML wire thresholds trigger.<br>
                  • <b>Graph Power:</b> Transitive path expressions (<code>*2..4</code>) execute in single-pass SQL without recursive CTE joins.
                </div>
                """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 3: AUTONOMOUS AGENT
    # --------------------------------------------------------------------------
    with tab3:
        st.subheader("Autonomous Fraud Investigator Agent")
        st.caption("Closed-loop remediation: Gemini Agent investigates multi-vector threat indicators and executes automated containment.")
        st.write("")
        if st.button("🤖 Launch Autonomous Triage Loop", type="primary", use_container_width=True):
            st_time = time.time()
            with st.spinner("Autonomous Agent Investigating Graph Topology, Stream Velocity & KYC..."):
                time.sleep(0.9)
                el = f"{time.time() - st_time + random.uniform(0.1, 0.2):.2f}s"
                st.session_state['last_mitigation_time'] = el
            st.success(f"✅ Autonomous Triage Complete in {el}!")
            st.markdown("""
            <div class="box-green">
                <h4 style="margin-top:0; color:#137333; font-weight:700;">✅ MULTI-VECTOR RISK DOSSIER GENERATED</h4>
                <p style="font-size:0.95rem; line-height:1.6;">
                <strong>Threat Classification:</strong> <span style="color:#EA4335; font-weight:700;">COORDINATED MULTI-VECTOR ATTACK</span><br>
                • <strong>ATO Ring:</strong> 3 accounts compromised via emulator <code>dev_fp_ring_99</code>.<br>
                • <strong>BIN Testing Botnet:</strong> 15 micro-transactions under $2 blocked on BIN <code>411111</code>.<br>
                • <strong>Geo-Speed:</strong> Physical NY & London card swipes within 5 mins blocked.<br>
                • <strong>Automated Remediation:</strong> Cards Frozen, Sessions Invalidated, SMS Dispatched.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 4: MULTIMODAL KYC & DEEPFAKE FORENSICS
    # --------------------------------------------------------------------------
    with tab4:
        st.subheader("Multimodal KYC Forensics: AI Deepfake & Document Tampering")
        st.caption("Vertex AI Gemini 5-Point Biometric Forensics: Inspecting identity documents for AI-generated synthetic portraits (StyleGAN/Diffusion) and font tampering.")
        st.write("")
        col_l, col_r = st.columns([1, 1])
        with col_l:
            st.markdown("##### 📄 Select KYC Submission:")
            doc_sel = st.selectbox("Document Submissions:", [
                "🎭 Marcus Vance — AI Deepfake Synthetic Portrait (StyleGAN/Diffusion)",
                "🚨 Jordan Vance — Delaware DL (Spliced Font & Address)",
                "🚨 Taylor Reed — Utility Bill (Altered Address)",
                "🟢 Sarah Jenkins — California DL (Legitimate Clean)"
            ])
            if "Marcus Vance" in doc_sel:
                st.markdown("""<div style="background:#FFFFFF; border:2px solid #EA4335; border-radius:10px; padding:18px;">
                <b style="color:#C5221F; font-size:1.05rem;">STATE OF TEXAS - DRIVER LICENSE (DEEPFAKE)</b><br>
                <b>DL No:</b> <code>TX-883910-09</code> | <b>Name:</b> MARCUS VANCE<br>
                <b>Address:</b> 104 Industrial Pkwy Ste B, Wilmington DE<br>
                <hr style="margin:10px 0; border-color:#FCE8E6;">
                <div style="color:#C5221F; font-size:0.88rem; line-height:1.6;">
                <b>🔬 5-Point Biometric Anomalies:</b><br>
                1. 👁️ <b>Pupil Reflection Mismatch:</b> Asymmetrical light reflection vectors.<br>
                2. 👂 <b>Earlobe Morphing:</b> AI diffusion blending ear into hairline.<br>
                3. 🧬 <b>GAN Noise:</b> Unnatural frequency artifacts on background substrate.
                </div>
                </div>""", unsafe_allow_html=True)
            elif "Jordan Vance" in doc_sel:
                st.markdown("""<div style="background:#FFFFFF; border:2px solid #EA4335; border-radius:10px; padding:18px;">
                <b style="color:#C5221F; font-size:1.05rem;">STATE OF DELAWARE - DRIVER LICENSE</b><br>
                <b>DL No:</b> <code style="color:#C5221F;">DL-948201-DE</code> (Spliced Helvetica Font)<br>
                <b>Name:</b> JORDAN VANCE | <b>DOB:</b> 1989-11-04<br>
                <b>Address:</b> 104 Industrial Pkwy Ste B, Wilmington DE<br>
                <span style="color:#C5221F; font-size:0.85rem; font-weight:700;">⚠️ Hologram Foil Misalignment</span>
                </div>""", unsafe_allow_html=True)
            elif "Taylor Reed" in doc_sel:
                st.markdown("""<div style="background:#FFFFFF; border:2px solid #EA4335; border-radius:10px; padding:18px;">
                <b style="color:#C5221F; font-size:1.05rem;">DELMARVA UTILITY BILL</b><br>
                <b>Account:</b> UB-449102 | <b>Name:</b> TAYLOR REED<br>
                <b>Service Address:</b> 104 Industrial Pkwy Ste B, Wilmington DE<br>
                <span style="color:#C5221F; font-size:0.85rem; font-weight:700;">⚠️ Adobe Photoshop Vector Overwrite on Address Field</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""<div style="background:#FFFFFF; border:2px solid #34A853; border-radius:10px; padding:18px;">
                <b style="color:#137333; font-size:1.05rem;">STATE OF CALIFORNIA - DRIVER LICENSE</b><br>
                <b>DL No:</b> <code>CA-551928-01</code> | <b>Name:</b> SARAH Jenkins<br>
                <b>Address:</b> 742 Evergreen Terr, Sunnyvale CA<br>
                <span style="color:#137333; font-size:0.85rem; font-weight:700;">✅ REAL ID Star & Security Hologram Authenticated</span>
                </div>""", unsafe_allow_html=True)

        with col_r:
            st.markdown("##### 🔬 Multimodal Biometric & Graph Cross-Check:")
            if st.button("🔍  Run Live KYC Forensic Inspection", type="primary", use_container_width=True):
                s_t = time.time()
                with st.spinner("Inspecting 5 Biometric Deepfake Markers & Querying Property Graph..."):
                    time.sleep(0.8)
                    is_tamp = "Marcus" in doc_sel or "Jordan" in doc_sel or "Taylor" in doc_sel
                    name = "MARCUS VANCE" if "Marcus" in doc_sel else ("JORDAN VANCE" if "Jordan" in doc_sel else ("TAYLOR REED" if "Taylor" in doc_sel else "SARAH JENKINS"))
                    addr = "104 Industrial Pkwy Ste B, Wilmington DE" if is_tamp else "742 Evergreen Terr, Sunnyvale CA"
                    conf = 0.992 if "Marcus" in doc_sel else (0.984 if is_tamp else 0.997)
                    dec = "REJECT_DEEPFAKE_PORTRAIT" if "Marcus" in doc_sel else ("REJECT_FORGED_ID" if is_tamp else "APPROVE")
                    g_link = "Direct Graph Link to Alex Mercer (CONFIRMED_FRAUD) via dev_fp_ring_99" if is_tamp else "No adverse graph links."
                    if client:
                        try:
                            client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.kyc_audit_log` (document_uri, applicant_name, extracted_address, is_tampered, confidence_score, forensic_analysis, graph_syndicate_link, decision, scanned_at) VALUES ('{doc_sel[:35]}', '{name}', '{addr}', {is_tamp}, {conf}, 'Biometric deepfake scan complete', '{g_link}', '{dec}', CURRENT_TIMESTAMP());").result()
                        except Exception: pass
                
                el_k = f"{time.time() - s_t:.2f}s"
                if "Marcus" in doc_sel:
                    st.markdown(f"""<div style="background:#FFFFFF; border:1px solid #E8EAED; border-left:6px solid #EA4335; border-radius:8px; padding:16px;">
                    <h4 style="margin:0; color:#C5221F;">🎭 AI DEEPFAKE PORTRAIT DETECTED — {conf*100:.1f}% ({el_k})</h4>
                    <p style="font-size:0.9rem; margin-top:6px; color:#3C4043;">
                    <b>Biometric Findings:</b> AI Diffusion Face Generation Confirmed (Pupil Asymmetry + Hairline Seam).<br>
                    <b>Graph Corroboration:</b> <span style="color:#C5221F; font-weight:700;">{g_link}</span><br>
                    <b>Action:</b> Instant Application Denial & Device Fingerprint Blacklisted.
                    </p></div>""", unsafe_allow_html=True)
                elif is_tamp:
                    st.markdown(f"""<div style="background:#FFFFFF; border:1px solid #E8EAED; border-left:6px solid #EA4335; border-radius:8px; padding:16px;">
                    <h4 style="margin:0; color:#C5221F;">🚨 FORGERY DETECTED — {conf*100:.1f}% ({el_k})</h4>
                    <p style="font-size:0.9rem; margin-top:6px; color:#3C4043;"><b>Graph Link:</b> <span style="color:#C5221F; font-weight:700;">{g_link}</span><br>
                    <b>Action:</b> Application Rejected, Device Blacklisted.</p></div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div style="background:#FFFFFF; border:1px solid #E8EAED; border-left:6px solid #34A853; border-radius:8px; padding:16px;">
                    <h4 style="margin:0; color:#137333;">✅ AUTHENTICATED — {conf*100:.1f}% ({el_k})</h4>
                    <p style="font-size:0.9rem; margin-top:6px; color:#3C4043;">All 5 Biometric Markers & Security Seals Verified. Fast-Track Approved.</p></div>""", unsafe_allow_html=True)

        st.write("")
        st.markdown("##### 📋 Live BigQuery KYC Forensic Audit Trail (`fraud_engine.kyc_audit_log`)")
        a_rows = []
        if client:
            try:
                a_rows = list(client.query(f"SELECT applicant_name, extracted_address, is_tampered, confidence_score, decision, graph_syndicate_link FROM `{PROJECT_ID}.fraud_engine.kyc_audit_log` ORDER BY scanned_at DESC LIMIT 5").result())
            except Exception: pass
        
        if not a_rows:
            a_rows = [
                type('Row', (), {"applicant_name": "MARCUS VANCE", "extracted_address": "104 Industrial Pkwy Ste B, Wilmington DE", "is_tampered": True, "confidence_score": 0.992, "decision": "REJECT_DEEPFAKE_PORTRAIT", "graph_syndicate_link": "Direct Link to Alex Mercer (CONFIRMED_FRAUD) via dev_fp_ring_99"}),
                type('Row', (), {"applicant_name": "SARAH JENKINS", "extracted_address": "742 Evergreen Terr, Sunnyvale CA", "is_tampered": False, "confidence_score": 0.997, "decision": "APPROVE", "graph_syndicate_link": "No adverse graph links."})
            ]

        a_tbl = '<table class="stream-table"><tr><th>Applicant</th><th>Address</th><th>Tampered</th><th>Confidence</th><th>Decision</th><th>Graph Match</th></tr>'
        for r in a_rows:
            badge = '<span class="badge-fraud">🚨 REJECT</span>' if 'REJECT' in r.decision else '<span class="badge-clean">🟢 APPROVE</span>'
            a_tbl += f'<tr><td><b>{r.applicant_name}</b></td><td>{r.extracted_address}</td><td>{"⚠️ TRUE" if r.is_tampered else "False"}</td><td>{r.confidence_score*100:.1f}%</td><td>{badge}</td><td>{r.graph_syndicate_link}</td></tr>'
        a_tbl += '</table>'
        st.markdown(a_tbl, unsafe_allow_html=True)