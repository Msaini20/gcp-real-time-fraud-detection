import streamlit as st, time, random, textwrap
from google.cloud import bigquery
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Fraud Operations Command Center | Google Cloud",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE INITIALIZATION ---
if 'view_mode' not in st.session_state:
    st.session_state['view_mode'] = 'landing'
if 'latest_txn_ids' not in st.session_state:
    st.session_state['latest_txn_ids'] = []
if 'last_mitigation_time' not in st.session_state:
    st.session_state['last_mitigation_time'] = "1.82s"
if 'selected_graph_pattern' not in st.session_state:
    st.session_state['selected_graph_pattern'] = 'pattern1'
if 'pos_scenario' not in st.session_state:
    st.session_state['pos_scenario'] = 'normal'
if 'pos_tx_state' not in st.session_state:
    st.session_state['pos_tx_state'] = 'idle'
if 'kyc_persona' not in st.session_state:
    st.session_state['kyc_persona'] = 'marcus'
if 'sidebar_injection_choice' not in st.session_state:
    st.session_state['sidebar_injection_choice'] = 'syndicate'
if 'sms_reply_state' not in st.session_state:
    st.session_state['sms_reply_state'] = 'pending'
if 'active_story' not in st.session_state:
    st.session_state['active_story'] = 'story1'
if 'triage_status' not in st.session_state:
    st.session_state['triage_status'] = 'idle'
if 'triage_stage_step' not in st.session_state:
    st.session_state['triage_stage_step'] = 0

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

# --- HIGH-CONTRAST GOOGLE DESIGN SYSTEM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700;800&family=Roboto+Mono:wght@400;500;600&display=swap');
    
    /* Global Canvas */
    .stApp {
        background-color: #FFFFFF !important;
        font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    html, body, [class*="css"], .stMarkdown, p, label {
        font-family: 'Google Sans', sans-serif !important;
        color: #202124;
    }

    /* 🌟 HIGH CONTRAST HEADINGS FIX */
h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5,
[data-testid="stMarkdownContainer"] h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
    color: #1A73E8 !important;
    font-weight: 700 !important;
    opacity: 1.0 !important;
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

    /* 🚫 BULLETPROOF FIX FOR SELECTBOX, RADIO & DROPDOWN MENUS */
    div[data-baseweb="select"],
    div[data-baseweb="select"] *,
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] *,
    ul[data-baseweb="menu"],
    ul[data-baseweb="menu"] *,
    div[role="listbox"],
    div[role="listbox"] *,
    ul[role="listbox"],
    ul[role="listbox"] *,
    li[role="option"],
    li[role="option"] *,
    div[role="option"],
    div[role="option"] *,
    div[data-testid="stSelectboxVirtualDropdown"],
    div[data-testid="stSelectboxVirtualDropdown"] * {
        background-color: #FFFFFF !important;
        color: #202124 !important;
    }

    li[role="option"]:hover,
    li[role="option"]:hover *,
    li[role="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"] *,
    div[role="option"]:hover,
    div[role="option"]:hover *,
    div[role="option"][aria-selected="true"],
    div[role="option"][aria-selected="true"] * {
        background-color: #E8F0FE !important;
        color: #1A73E8 !important;
        font-weight: 700 !important;
    }

    div[data-baseweb="select"] > div {
        border: 1.5px solid #DADCE0 !important;
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
    }

    /* Code Box */
    .code-box {
        background-color: #F8F9FA;
        border: 1px solid #DADCE0;
        border-left: 4px solid #1A73E8;
        border-radius: 8px;
        padding: 14px 16px;
        font-family: 'Roboto Mono', monospace;
        font-size: 0.84rem;
        color: #202124 !important;
        line-height: 1.5;
        white-space: pre-wrap;
        margin-top: 4px;
        min-height: 190px;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1A73E8 0%, #4285F4 100%);
        border-radius: 12px;
        padding: 24px 22px;
        margin-bottom: 18px;
        box-shadow: 0 3px 12px rgba(26, 115, 232, 0.20);
    }
    .hero-title {
        font-size: 2.0rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .hero-sub {
        font-size: 1.0rem;
        color: #E8F0FE !important;
        line-height: 1.45;
    }

    /* Executive Cards */
    .exec-card {
        background-color: #FFFFFF;
        border: 1px solid #E8EAED;
        border-radius: 10px;
        padding: 20px 22px;
        margin-bottom: 14px;
        box-shadow: 0 2px 6px rgba(60,64,67, 0.05);
        min-height: 220px;
    }
    .exec-card p, .exec-card span, .exec-card div {
        color: #3C4043 !important;
    }

    /* Executive Impact Ribbon */
    .exec-impact-banner {
        background: linear-gradient(90deg, #188038 0%, #137333 100%);
        color: #FFFFFF !important;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(24,128,56,0.18);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .exec-impact-banner * {
        color: #FFFFFF !important;
    }

    /* Buttons */
    button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #1A73E8 0%, #4285F4 100%) !important;
        background-color: #1A73E8 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        font-size: 0.94rem !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(26, 115, 232, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    button[kind="primary"] *,
    button[data-testid="stBaseButton-primary"] * {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"] {
        background-color: #FFFFFF !important;
        color: #202124 !important;
        border: 1.5px solid #DADCE0 !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        font-size: 0.94rem !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 3px rgba(60,64,67, 0.08) !important;
        transition: all 0.2s ease !important;
    }
    button[kind="secondary"]:hover,
    button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #EEF4FD !important;
        color: #1A73E8 !important;
        border-color: #1A73E8 !important;
    }
    button[kind="secondary"] *,
    button[data-testid="stBaseButton-secondary"] * {
        color: #202124 !important;
        font-weight: 700 !important;
    }
    button[kind="secondary"]:hover *,
    button[data-testid="stBaseButton-secondary"]:hover * {
        color: #1A73E8 !important;
    }

    /* 💳 PREMIUM REALISTIC PAYMENT CARDS */
    .pos-card-container {
        border-radius: 14px;
        padding: 22px 24px;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        border: 1px solid rgba(255,255,255,0.15);
    }
    .pos-card-container,
    .pos-card-container * {
        color: #FFFFFF !important;
    }
    .pos-card-chip {
        width: 44px;
        height: 34px;
        background: linear-gradient(135deg, #F9D976 0%, #E9B642 50%, #D49E24 100%);
        border-radius: 6px;
        border: 1px solid #B8860B;
        position: relative;
        display: inline-block;
        box-shadow: inset 0 1px 2px rgba(255,255,255,0.6), 0 1px 3px rgba(0,0,0,0.3);
    }
    .pos-card-pan {
        font-family: 'Roboto Mono', monospace !important;
        font-size: 1.30rem !important;
        font-weight: 700 !important;
        letter-spacing: 3px !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.6) !important;
        margin: 14px 0 12px 0 !important;
        color: #FFFFFF !important;
    }
    .pos-card-meta {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        font-size: 0.85rem;
    }
    .pos-card-holder {
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 0.90rem;
    }

    /* 📟 VERIFONE HARDWARE POS DISPLAY */
    .pos-terminal-frame {
        background: #FFFFFF;
        border: 1.5px solid #DADCE0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(60,64,67, 0.08);
    }
    .pos-terminal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1.5px solid #F1F3F4;
        padding-bottom: 10px;
        margin-bottom: 14px;
    }
    .pos-amount-display {
        background: #F8F9FA;
        border: 1.5px solid #E8EAED;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .pos-tap-zone {
        background: #EEF4FD;
        border: 2px dashed #4285F4;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        color: #1A73E8 !important;
        font-weight: 700;
        font-size: 0.88rem;
        margin-bottom: 14px;
    }
    .pos-tap-zone * {
        color: #1A73E8 !important;
    }

    /* 🧠 GEMINI DECISION DOSSIER BOX */
    .dossier-frame {
        background: #FFFFFF;
        border: 1.5px solid #DADCE0;
        border-radius: 12px;
        padding: 20px 22px;
        box-shadow: 0 4px 16px rgba(60,64,67, 0.08);
        min-height: 480px;
    }
    .dossier-hud-bar {
        display: flex;
        gap: 10px;
        margin-bottom: 14px;
        flex-wrap: wrap;
    }
    .dossier-pill {
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 800;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .dossier-pill-danger {
        background: #FCE8E6;
        color: #C5221F !important;
        border: 1px solid #FAD2CF;
    }
    .dossier-pill-danger * {
        color: #C5221F !important;
    }
    .dossier-pill-success {
        background: #E6F4EA;
        color: #137333 !important;
        border: 1px solid #CEEAD6;
    }
    .dossier-pill-success * {
        color: #137333 !important;
    }
    .dossier-pill-info {
        background: #E8F0FE;
        color: #1A73E8 !important;
        border: 1px solid #D2E3FC;
    }
    .dossier-pill-info * {
        color: #1A73E8 !important;
    }

    /* Stream Table */
    .stream-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 6px;
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid #E8EAED;
        font-size: 0.84rem;
        background-color: #FFFFFF !important;
    }
    .stream-table th {
        background-color: #F8F9FA !important;
        color: #202124 !important;
        text-align: left;
        padding: 8px 10px;
        font-weight: 600;
        border-bottom: 1.5px solid #DADCE0;
    }
    .stream-table td {
        padding: 8px 10px;
        border-bottom: 1px solid #E8EAED;
        color: #202124 !important;
        background-color: #FFFFFF !important;
    }
    .row-new td {
        background-color: #FEF7E0 !important;
        color: #B06000 !important;
        font-weight: 600;
    }
    .row-new { border-left: 4px solid #FBBC04 !important; }
    .row-fraud td {
        background-color: #FCE8E6 !important;
        color: #C5221F !important;
    }
    .row-fraud { border-left: 4px solid #EA4335 !important; }
    .row-clean td {
        background-color: #E6F4EA !important;
        color: #137333 !important;
    }
    .row-clean { border-left: 4px solid #34A853 !important; }

    /* Badges */
    .badge-new { background: #FBBC04; color: #202124 !important; padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; }
    .badge-fraud { background: #EA4335; color: #FFFFFF !important; padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; }
    .badge-clean { background: #34A853; color: #FFFFFF !important; padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; }

    /* Info Banners */
    .box-blue {
        background-color: #F8FAFD;
        border: 1px solid #D2E3FC;
        border-left: 4px solid #4285F4;
        padding: 14px 16px;
        border-radius: 8px;
        line-height: 1.55;
        min-height: 190px;
    }
    .box-blue p, .box-blue span, .box-blue div, .box-blue b { color: #174EA6 !important; }
    
    .box-green {
        background-color: #FFFFFF;
        border: 1.5px solid #CEEAD6;
        border-left: 5px solid #34A853;
        padding: 16px 18px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(52,168,83,0.06);
    }
    .box-green p, .box-green span, .box-green div { color: #202124 !important; }

    section[data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
        border-right: 1px solid #E8EAED !important;
    }

    /* 🌟 PROMINENT EXECUTIVE TOP NAVIGATION TABS */
    .stTabs,
    [data-testid="stTabs"],
    div[data-baseweb="tab-list"] {
        margin-top: 14px !important;
        margin-bottom: 24px !important;
    }

    [data-testid="stTabs"] div[data-baseweb="tab-list"],
    div[data-baseweb="tab-list"] {
        gap: 14px !important;
        padding: 8px 0 16px 0 !important;
        border-bottom: 2.5px solid #DADCE0 !important;
    }

    [data-testid="stTabs"] button,
    [data-testid="stTabs"] button[data-baseweb="tab"],
    button[data-baseweb="tab"],
    button[data-testid="stTab"] {
        height: auto !important;
        min-height: 52px !important;
        padding: 14px 28px !important;
        border-radius: 10px 10px 0 0 !important;
        background-color: #F8F9FA !important;
        border: 1.5px solid #DADCE0 !important;
        border-bottom: none !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stTabs"] button *,
    [data-testid="stTabs"] button p,
    [data-testid="stTabs"] button span,
    [data-testid="stTabs"] button div,
    button[data-baseweb="tab"] *,
    button[data-testid="stTab"] * {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #5F6368 !important;
    }

    [data-testid="stTabs"] button:hover,
    button[data-baseweb="tab"]:hover {
        background-color: #EEF4FD !important;
        border-color: #4285F4 !important;
    }

    [data-testid="stTabs"] button:hover *,
    button[data-baseweb="tab"]:hover * {
        color: #1A73E8 !important;
    }

    [data-testid="stTabs"] button[aria-selected="true"],
    button[data-baseweb="tab"][aria-selected="true"],
    button[data-testid="stTab"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        border: 2.5px solid #1A73E8 !important;
        border-bottom: 3.5px solid #FFFFFF !important;
        margin-bottom: -3px !important;
        box-shadow: 0 -3px 10px rgba(26,115,232,0.18) !important;
    }

    [data-testid="stTabs"] button[aria-selected="true"] *,
    button[data-baseweb="tab"][aria-selected="true"] *,
    button[data-testid="stTab"][aria-selected="true"] * {
        font-size: 1.18rem !important;
        font-weight: 800 !important;
        color: #1A73E8 !important;
    }

    /* 📋 CLEAN EXPANDER & AUDIT LOG TABLE */
    div[data-testid="stExpander"] {
        border: 1.5px solid #DADCE0 !important;
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
        margin-top: 14px !important;
        box-shadow: 0 1px 4px rgba(60,64,67, 0.04) !important;
        width: 100% !important;
    }
    summary[data-testid="stExpanderSummary"],
    details[data-testid="stExpander"] summary {
        font-size: 1.0rem !important;
        font-weight: 700 !important;
        color: #1A73E8 !important;
        padding: 12px 16px !important;
        background: #F8F9FA !important;
        border-radius: 6px !important;
    }
    summary[data-testid="stExpanderSummary"] p,
    summary[data-testid="stExpanderSummary"] span,
    summary[data-testid="stExpanderSummary"] div {
        font-size: 1.0rem !important;
        font-weight: 700 !important;
        color: #1A73E8 !important;
    }

    /* Code and Badge Styles */
    code {
        background-color: #F1F3F4 !important;
        color: #202124 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 0.82rem !important;
        border: 1px solid #DADCE0 !important;
    }

    /* Enterprise Stepper Cards */
    .stepper-card {
        background: #FFFFFF !important;
        border: 1.5px solid #DADCE0 !important;
        border-radius: 8px !important;
        padding: 14px 16px !important;
        box-shadow: 0 1px 4px rgba(60,64,67, 0.06) !important;
        position: relative !important;
    }
    .stepper-card-active {
        border: 1.5px solid #34A853 !important;
        border-left: 5px solid #137333 !important;
        background: #FFFFFF !important;
    }
    .stepper-card-pending {
        border: 1.5px solid #FBBC04 !important;
        border-left: 5px solid #F29900 !important;
        background: #FFFFFF !important;
    }
    .stepper-card-inactive {
        border: 1px solid #DADCE0 !important;
        background: #FAFAFA !important;
        opacity: 0.85 !important;
    }
    .stepper-num {
        font-size: 0.70rem !important;
        font-weight: 800 !important;
        color: #5F6368 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    .stepper-title {
        font-size: 0.98rem !important;
        font-weight: 800 !important;
        color: #202124 !important;
        margin: 3px 0 5px 0 !important;
    }
    .stepper-tag {
        display: inline-block !important;
        background: #E6F4EA !important;
        color: #137333 !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        padding: 3px 8px !important;
        border-radius: 4px !important;
        border: 1px solid #CEEAD6 !important;
    }
    .stepper-tag-pending {
        background: #FEF7E0 !important;
        color: #B06000 !important;
        border: 1px solid #FEEFC3 !important;
    }
    .stepper-tag-inactive {
        background: #F1F3F4 !important;
        color: #5F6368 !important;
        border: 1px solid #DADCE0 !important;
    }

    /* Smartphone Chat Simulation */
    .phone-mockup-frame {
        background: #FFFFFF !important;
        border: 2px solid #DADCE0 !important;
        border-radius: 16px !important;
        padding: 16px !important;
        box-shadow: 0 4px 16px rgba(60,64,67, 0.08) !important;
    }
    .phone-top-bar {
        display: flex !important;
        justify-content: space-between !important;
        font-size: 0.75rem !important;
        color: #5F6368 !important;
        font-weight: 700 !important;
        padding-bottom: 8px !important;
        border-bottom: 1px solid #F1F3F4 !important;
        margin-bottom: 12px !important;
    }
    .phone-sender-header {
        font-size: 0.88rem !important;
        font-weight: 800 !important;
        color: #1A73E8 !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        margin-bottom: 12px !important;
    }
    .chat-bubble-incoming {
        background: #F1F3F4 !important;
        color: #202124 !important;
        border-radius: 12px 12px 12px 2px !important;
        padding: 12px 14px !important;
        font-size: 0.86rem !important;
        line-height: 1.5 !important;
        margin-bottom: 12px !important;
        border: 1px solid #DADCE0 !important;
    }
    .chat-bubble-incoming * {
        color: #202124 !important;
    }
    .chat-bubble-outgoing {
        background: #1A73E8 !important;
        color: #FFFFFF !important;
        border-radius: 12px 12px 2px 12px !important;
        padding: 10px 14px !important;
        font-size: 0.86rem !important;
        line-height: 1.5 !important;
        margin-bottom: 12px !important;
        margin-left: 20% !important;
        text-align: right !important;
    }
    .chat-bubble-outgoing * {
        color: #FFFFFF !important;
    }

    /* Driver License Realistic Mockup */
    .dl-card-frame {
        background: #FFFFFF;
        border: 1.5px solid #DADCE0;
        border-radius: 10px;
        padding: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .dl-header {
        background: linear-gradient(90deg, #1A73E8 0%, #0D47A1 100%);
        color: #FFFFFF !important;
        padding: 6px 10px;
        border-radius: 6px 6px 0 0;
        font-weight: 800;
        font-size: 0.88rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .dl-header * { color: #FFFFFF !important; }
    .dl-header-fake {
        background: linear-gradient(90deg, #C5221F 0%, #8C1D18 100%);
    }
    .dl-body {
        border: 1px solid #DADCE0;
        border-top: none;
        border-radius: 0 0 6px 6px;
        padding: 12px;
        background: #FAFAFA;
        display: flex;
        gap: 12px;
    }
    .dl-portrait-box {
        width: 110px;
        height: 135px;
        background: #FFFFFF;
        border: 1.5px solid #DADCE0;
        border-radius: 6px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    .dl-portrait-fake {
        border: 2px solid #EA4335 !important;
    }
    .dl-portrait-clean {
        border: 2px solid #34A853 !important;
    }
    .dl-info-fields {
        flex: 1;
        font-size: 0.82rem;
        line-height: 1.45;
    }
    .dl-field-label {
        font-size: 0.65rem;
        color: #5F6368 !important;
        font-weight: 700;
        text-transform: uppercase;
    }
    .dl-field-val {
        font-weight: 700;
        color: #202124 !important;
        margin-bottom: 4px;
    }
    .dl-tamper-highlight {
        background-color: #FCE8E6;
        border: 1px dashed #EA4335;
        padding: 1px 4px;
        border-radius: 3px;
        color: #C5221F !important;
        font-weight: 700;
    }
    .dl-clean-highlight {
        background-color: #E6F4EA;
        border: 1px solid #34A853;
        padding: 1px 4px;
        border-radius: 3px;
        color: #137333 !important;
        font-weight: 700;
    }
    .scan-hud-tag {
        position: absolute;
        bottom: 2px;
        left: 2px;
        right: 2px;
        background: rgba(234, 67, 53, 0.90);
        color: #FFFFFF !important;
        font-size: 0.60rem;
        font-weight: 800;
        text-align: center;
        padding: 2px;
        border-radius: 3px;
    }
    .scan-hud-tag-clean {
        background: rgba(52, 168, 83, 0.90);
    }
</style>
""", unsafe_allow_html=True)

# Helper functions to render raw SVG/HTML without markdown indentation bugs
def render_svg_clean(svg_markup):
    clean = textwrap.dedent(svg_markup).strip()
    st.markdown(clean, unsafe_allow_html=True)

def render_html(html_str):
    clean = " ".join(html_str.split())
    #clean = textwrap.dedent(html_str).strip()
    st.markdown(clean, unsafe_allow_html=True)

# ==============================================================================
# STREAMLINED SIDEBAR NAVIGATION & CONSOLIDATED INJECTOR
# ==============================================================================
with st.sidebar:
    st.markdown("<h2 style='color:#1A73E8; margin-top:0; margin-bottom:0px; font-weight:700;'>🛡️ Google Cloud</h2>", unsafe_allow_html=True)
    st.caption("Agentic Fraud Defense Platform")
    
    current_idx = 0 if st.session_state['view_mode'] == 'landing' else (1 if st.session_state['view_mode'] == 'pos_simulator' else 2)
    nav_selection = st.radio(
        "Platform View:",
        [
            "🏢 1. Executive Briefing",
            "📱 2. Live POS Simulator",
            "🛡️ 3. Operations Command Center"
        ],
        index=current_idx,
        label_visibility="collapsed"
    )
    
    if "1. Executive" in nav_selection and st.session_state['view_mode'] != 'landing':
        st.session_state['view_mode'] = 'landing'
        st.rerun()
    elif "2. Live POS" in nav_selection and st.session_state['view_mode'] != 'pos_simulator':
        st.session_state['view_mode'] = 'pos_simulator'
        st.rerun()
    elif "3. Operations" in nav_selection and st.session_state['view_mode'] not in ['demo', 'operations']:
        st.session_state['view_mode'] = 'operations'
        st.rerun()

    st.divider()

    # Consolidated Clean Threat Vector Ingestion Box
    st.markdown("#### ⚡ **Threat Vector Simulator**")
    st.caption("Push live financial crime events into BigQuery streams:")
    
    inj_choice = st.selectbox(
        "Select Attack Vector:",
        [
            "🟢 Legitimate Coffee Swipes (acc_legit_100)",
            "🚨 Syndicate Ring Bust-Out (acc_syndicate_02)",
            "⚡ Botnet Card Testing / BIN Attack (411111)",
            "✈️ Impossible Geo-Travel (NY ➔ London)",
            "🔑 ATO Credential Reset (dev_fp_ring_99)"
        ]
    )

    if st.button("🚀  Inject Live Event Stream", type="primary", use_container_width=True):
        ts = int(time.time())
        start_t = time.time()

        if "Legitimate" in inj_choice:
            t1, t2 = f"txn_clean_{ts}", f"txn_clean_{ts+1}"
            if client:
                try:
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_stream` (transaction_id, account_id, amount, merchant_category, device_id, channel, latitude, longitude, timestamp) VALUES ('{t1}', 'acc_legit_100', 42.50, 'coffee_shop', 'dev_fp_clean_01', 'IN_STORE_POS', 37.7749, -122.4194, CURRENT_TIMESTAMP()), ('{t2}', 'acc_legit_101', 89.20, 'grocery_retail', 'dev_fp_clean_02', 'IN_STORE_POS', 37.7833, -122.4167, CURRENT_TIMESTAMP());").result()
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_scored` (transaction_id, account_id, amount, is_suspicious_device, is_high_risk_amount, is_bin_attack, is_impossible_travel, processed_at) VALUES ('{t1}', 'acc_legit_100', 42.50, FALSE, FALSE, FALSE, FALSE, CURRENT_TIMESTAMP()), ('{t2}', 'acc_legit_101', 89.20, FALSE, FALSE, FALSE, FALSE, CURRENT_TIMESTAMP());").result()
                except Exception: pass
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_legit_100", "amount": 42.50, "merchant_category": "coffee_shop", "bin": "400012", "channel": "IN_STORE_POS"})
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_legit_101", "amount": 89.20, "merchant_category": "grocery_retail", "bin": "542418", "channel": "IN_STORE_POS"})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_legit_100", "amount": 42.50, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": False, "is_high_risk_amount": False})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_legit_101", "amount": 89.20, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": False, "is_high_risk_amount": False})
            st.session_state['latest_txn_ids'] = [t1, t2]
            st.session_state['pos_scenario'] = 'normal'
            st.session_state['pos_tx_state'] = 'idle'
            st.session_state['last_mitigation_time'] = f"{time.time() - start_t + random.uniform(0.1, 0.2):.2f}s"
            st.toast("✅ Legitimate Stream Scored!", icon="🟢")

        elif "Syndicate" in inj_choice:
            t1, t2 = f"txn_fraud_{ts}", f"txn_fraud_{ts+1}"
            if client:
                try:
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_stream` (transaction_id, account_id, amount, merchant_category, device_id, channel, timestamp) VALUES ('{t1}', 'acc_syndicate_02', 1950.00, 'electronics_online', 'dev_fp_ring_99', 'E_COMMERCE', CURRENT_TIMESTAMP()), ('{t2}', 'acc_syndicate_03', 2400.00, 'crypto_exchange', 'dev_fp_ring_99', 'E_COMMERCE', CURRENT_TIMESTAMP());").result()
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_scored` (transaction_id, account_id, amount, is_suspicious_device, is_high_risk_amount, is_bin_attack, is_impossible_travel, processed_at) VALUES ('{t1}', 'acc_syndicate_02', 1950.00, TRUE, TRUE, FALSE, FALSE, CURRENT_TIMESTAMP()), ('{t2}', 'acc_syndicate_03', 2400.00, TRUE, TRUE, FALSE, FALSE, CURRENT_TIMESTAMP());").result()
                except Exception: pass
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_syndicate_02", "amount": 1950.00, "merchant_category": "electronics_online", "bin": "411111", "channel": "E_COMMERCE"})
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_syndicate_03", "amount": 2400.00, "merchant_category": "crypto_exchange", "bin": "411111", "channel": "E_COMMERCE"})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_syndicate_02", "amount": 1950.00, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": True})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_syndicate_03", "amount": 2400.00, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": True})
            st.session_state['latest_txn_ids'] = [t1, t2]
            st.session_state['selected_graph_pattern'] = 'pattern1'
            st.session_state['pos_scenario'] = 'syndicate'
            st.session_state['pos_tx_state'] = 'idle'
            st.session_state['last_mitigation_time'] = f"{time.time() - start_t + random.uniform(0.12, 0.28):.2f}s"
            st.toast("🚨 Syndicate Attack Intercepted!", icon="🚨")

        elif "Botnet" in inj_choice:
            t1, t2 = f"txn_bin_{ts}", f"txn_bin_{ts+1}"
            if client:
                try:
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_stream` (transaction_id, account_id, amount, merchant_category, device_id, card_bin, card_pan_masked, auth_response_code, channel, timestamp) VALUES ('{t1}', 'acc_botnet_01', 0.99, 'charity_donation', 'dev_fp_bot_01', '411111', '411111******1029', 'DECLINED_CVV', 'E_COMMERCE', CURRENT_TIMESTAMP()), ('{t2}', 'acc_botnet_01', 1.25, 'digital_gaming', 'dev_fp_bot_01', '411111', '411111******1030', 'DECLINED_CVV', 'E_COMMERCE', CURRENT_TIMESTAMP());").result()
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_scored` (transaction_id, account_id, amount, is_suspicious_device, is_high_risk_amount, is_bin_attack, is_impossible_travel, processed_at) VALUES ('{t1}', 'acc_botnet_01', 0.99, TRUE, FALSE, TRUE, FALSE, CURRENT_TIMESTAMP()), ('{t2}', 'acc_botnet_01', 1.25, TRUE, FALSE, TRUE, FALSE, CURRENT_TIMESTAMP());").result()
                except Exception: pass
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_botnet_01", "amount": 0.99, "merchant_category": "charity_donation", "bin": "411111", "channel": "E_COMMERCE"})
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_botnet_01", "amount": 1.25, "merchant_category": "digital_gaming", "bin": "411111", "channel": "E_COMMERCE"})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_botnet_01", "amount": 0.99, "is_bin_attack": True, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": False})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_botnet_01", "amount": 1.25, "is_bin_attack": True, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": False})
            st.session_state['latest_txn_ids'] = [t1, t2]
            st.session_state['pos_scenario'] = 'botnet'
            st.session_state['pos_tx_state'] = 'idle'
            st.session_state['last_mitigation_time'] = f"{time.time() - start_t + random.uniform(0.1, 0.2):.2f}s"
            st.toast("⚡ High-Velocity BIN Attack Stopped!", icon="⚡")

        elif "Impossible" in inj_choice:
            t1, t2 = f"txn_geo_ny_{ts}", f"txn_geo_lon_{ts+1}"
            if client:
                try:
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_stream` (transaction_id, account_id, amount, merchant_category, device_id, channel, latitude, longitude, timestamp) VALUES ('{t1}', 'acc_legit_100', 120.00, 'luxury_retail', 'pos_ny_01', 'IN_STORE_POS', 40.7128, -74.0060, CURRENT_TIMESTAMP()), ('{t2}', 'acc_legit_100', 850.00, 'jewelry_store', 'pos_london_02', 'IN_STORE_POS', 51.5074, -0.1278, CURRENT_TIMESTAMP());").result()
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.live_transactions_scored` (transaction_id, account_id, amount, is_suspicious_device, is_high_risk_amount, is_bin_attack, is_impossible_travel, calculated_speed_kmh, processed_at) VALUES ('{t1}', 'acc_legit_100', 120.00, FALSE, FALSE, FALSE, FALSE, 0.0, CURRENT_TIMESTAMP()), ('{t2}', 'acc_legit_100', 850.00, TRUE, TRUE, FALSE, TRUE, 22400.0, CURRENT_TIMESTAMP());").result()
                except Exception: pass
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_legit_100", "amount": 120.00, "merchant_category": "luxury_retail", "bin": "400012", "channel": "IN_STORE_POS"})
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_legit_100", "amount": 850.00, "merchant_category": "jewelry_store", "bin": "400012", "channel": "IN_STORE_POS"})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t1, "account_id": "acc_legit_100", "amount": 120.00, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": False, "is_high_risk_amount": False})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": t2, "account_id": "acc_legit_100", "amount": 850.00, "is_bin_attack": False, "is_impossible_travel": True, "is_suspicious_device": True, "is_high_risk_amount": True})
            st.session_state['latest_txn_ids'] = [t1, t2]
            st.session_state['pos_scenario'] = 'impossible_travel'
            st.session_state['pos_tx_state'] = 'idle'
            st.session_state['last_mitigation_time'] = f"{time.time() - start_t + random.uniform(0.1, 0.2):.2f}s"
            st.toast("✈️ Geo-Velocity Anomaly Flagged!", icon="✈️")

        else:
            e1, e2, e3 = f"evt_ato_{ts}_1", f"evt_ato_{ts}_2", f"evt_ato_{ts}_3"
            if client:
                try:
                    client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.auth_events_stream` (event_id, account_id, device_id, ip_address, event_type, timestamp) VALUES ('{e1}', 'acc_legit_100', 'dev_fp_ring_99', '198.51.100.24', 'PASSWORD_RESET', CURRENT_TIMESTAMP()), ('{e2}', 'acc_legit_101', 'dev_fp_ring_99', '198.51.100.24', '2FA_PHONE_CHANGED', CURRENT_TIMESTAMP()), ('{e3}', 'acc_legit_102', 'dev_fp_ring_99', '198.51.100.24', 'PASSWORD_RESET', CURRENT_TIMESTAMP());").result()
                except Exception: pass
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": e1, "account_id": "acc_legit_100 (Sarah C.)", "amount": 0.00, "merchant_category": "auth_password_reset", "bin": "N/A", "channel": "MOBILE_AUTH"})
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": e2, "account_id": "acc_legit_101 (Jordan V.)", "amount": 0.00, "merchant_category": "auth_2fa_phone_change", "bin": "N/A", "channel": "MOBILE_AUTH"})
            st.session_state['in_memory_raw_stream'].insert(0, {"transaction_id": e3, "account_id": "acc_legit_102 (Taylor R.)", "amount": 0.00, "merchant_category": "auth_password_reset", "bin": "N/A", "channel": "MOBILE_AUTH"})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": e1, "account_id": "acc_legit_100 (Sarah C.)", "amount": 0.00, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": False, "is_ato": True})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": e2, "account_id": "acc_legit_101 (Jordan V.)", "amount": 0.00, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": False, "is_ato": True})
            st.session_state['in_memory_scored_stream'].insert(0, {"transaction_id": e3, "account_id": "acc_legit_102 (Taylor R.)", "amount": 0.00, "is_bin_attack": False, "is_impossible_travel": False, "is_suspicious_device": True, "is_high_risk_amount": False, "is_ato": True})
            st.session_state['latest_txn_ids'] = [e1, e2, e3]
            st.session_state['selected_graph_pattern'] = 'pattern2'
            st.session_state['pos_scenario'] = 'ato'
            st.session_state['pos_tx_state'] = 'idle'
            st.session_state['last_mitigation_time'] = f"{time.time() - start_t + random.uniform(0.1, 0.2):.2f}s"
            st.toast("🔑 ATO Multi-Account Reset Flagged!", icon="🔑")
        
        st.rerun()

    st.divider()
    st.markdown("🟢 **Continuous Queries:** `ACTIVE`  \n🟢 **BigQuery Graph:** `OPTIMIZED`  \n🟢 **Vertex AI Biometrics:** `ONLINE`")

# ==============================================================================
# VIEW 1: EXECUTIVE BRIEFING
# ==============================================================================
if st.session_state['view_mode'] == 'landing':
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🛡️ Google Cloud Real-Time Fraud Defense Perimeter</div>
        <div class="hero-sub">Autonomous Financial Crime Defense: BigQuery Continuous Queries • In-Warehouse Graph (ISO GQL) • Apache Iceberg • Vertex AI Multimodal</div>
    </div>
    """, unsafe_allow_html=True)

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("📱  Launch Point-of-Sale Simulator", type="primary", use_container_width=True):
            st.session_state['view_mode'] = 'pos_simulator'
            st.rerun()
    with col_nav2:
        if st.button("🛡️  Enter Operations Command Center", use_container_width=True):
            st.session_state['view_mode'] = 'operations'
            st.rerun()

    st.write("")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown("""
        <div class="exec-card" style="border-left: 5px solid #EA4335;">
            <h4 style="color: #C5221F; margin-top:0; font-weight:700;">💼 1. Business Problem to Solve</h4>
            <p style="font-size:0.90rem; line-height:1.6;">
            <b>The $30B+ Coordinated Financial Crime Crisis:</b><br>
            • <b>Synthetic Bust-Out:</b> Dormant accounts leveraged for synchronized $2,500+ credit cash-outs.<br>
            • <b>ATO Fan-In:</b> Rooted emulator hardware hijacking 3+ customer profiles in minutes.<br>
            • <b>High-Speed BIN Attacks:</b> Botnets brute-forcing card validation micro-charges.<br>
            • <b>AI Deepfake KYC:</b> Synthetic diffusion portraits bypassing legacy document OCR.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="exec-card" style="border-left: 5px solid #4285F4;">
            <h4 style="color: #174EA6; margin-top:0; font-weight:700;">☁️ 3. Key Data Cloud Services Used</h4>
            <p style="font-size:0.90rem; line-height:1.6;">
            • <b>BigQuery Continuous Queries:</b> Sub-second stream scoring & GIS geo-velocity math.<br>
            • <b>BigQuery Property Graph (ISO GQL):</b> In-warehouse multi-hop traversals with zero ETL.<br>
            • <b>BigLake & Apache Iceberg:</b> Open lakehouse format querying GCS archives in place.<br>
            • <b>Vertex AI (Gemini Multimodal):</b> Pixel-level biometric deepfake inspection & containment.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_e2:
        st.markdown("""
        <div class="exec-card" style="border-left: 5px solid #FBBC04;">
            <h4 style="color: #B06000; margin-top:0; font-weight:700;">🎯 2. Key Demo Objectives</h4>
            <p style="font-size:0.90rem; line-height:1.6;">
            • <b>Sub-Second Interception:</b> Score live authorizations in &lt; 150ms.<br>
            • <b>Expose Syndicate Topology:</b> Traverse 4 hops in BigQuery in 28ms.<br>
            • <b>Geo-Speed Anomaly Detection:</b> Flag impossible continent travel in 5 mins.<br>
            • <b>Autonomous Remediation:</b> Freeze compromised cards & SMS notify in <b>&lt; 2s</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="exec-card" style="border-left: 5px solid #34A853;">
            <h4 style="color: #137333; margin-top:0; font-weight:700;">📈 4. Key Executive Takeaways & ROI</h4>
            <p style="font-size:0.90rem; line-height:1.6;">
            • <b>Zero Data Movement:</b> Stream, graph, lakehouse, and AI inside BigQuery.<br>
            • <b>Prevent Real-Time Losses:</b> Shifting from 48-hour triage to sub-2-second proactive defense.<br>
            • <b>40%+ TCO Reduction:</b> Eliminates standalone graph databases & streaming clusters.<br>
            • <b>Governed & Open:</b> Built on <b>ISO GQL</b>, <b>Apache Iceberg</b>, and <b>Gemini</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# VIEW 2: LIVE POINT-OF-SALE SIMULATOR
# ==============================================================================
elif st.session_state['view_mode'] == 'pos_simulator':
    st.markdown('<h2 style="color:#1A73E8; margin-top:0px; margin-bottom:2px; font-weight:700;">💳 Live Point-of-Sale (POS) & Checkout Simulator</h2>', unsafe_allow_html=True)
    st.caption("Simulate contactless checkout from the customer perspective and inspect Gemini's sub-second autonomous decision reasoning.")
    st.write("")

    # 5-WAY QUICK SCENARIO SELECTOR BAR
    st.markdown("##### 🎯 **Select Transaction Threat Vector to Simulate:**")
    p1, p2, p3, p4, p5 = st.columns(5)
    
    with p1:
        is_s1 = st.session_state['pos_scenario'] == 'normal'
        if st.button("🟢 1. Clean ($4.50)", type="primary" if is_s1 else "secondary", use_container_width=True, key="p_scen_1"):
            st.session_state['pos_scenario'] = 'normal'
            st.session_state['pos_tx_state'] = 'idle'
            st.rerun()

    with p2:
        is_s2 = st.session_state['pos_scenario'] == 'syndicate'
        if st.button("🚨 2. Syndicate ($2.5k)", type="primary" if is_s2 else "secondary", use_container_width=True, key="p_scen_2"):
            st.session_state['pos_scenario'] = 'syndicate'
            st.session_state['pos_tx_state'] = 'idle'
            st.rerun()

    with p3:
        is_s3 = st.session_state['pos_scenario'] == 'botnet'
        if st.button("⚡ 3. BIN Bot ($0.99)", type="primary" if is_s3 else "secondary", use_container_width=True, key="p_scen_3"):
            st.session_state['pos_scenario'] = 'botnet'
            st.session_state['pos_tx_state'] = 'idle'
            st.rerun()

    with p4:
        is_s4 = st.session_state['pos_scenario'] == 'impossible_travel'
        if st.button("✈️ 4. Geo-Speed ($850)", type="primary" if is_s4 else "secondary", use_container_width=True, key="p_scen_4"):
            st.session_state['pos_scenario'] = 'impossible_travel'
            st.session_state['pos_tx_state'] = 'idle'
            st.rerun()

    with p5:
        is_s5 = st.session_state['pos_scenario'] == 'ato'
        if st.button("🔑 5. ATO Reset ($0)", type="primary" if is_s5 else "secondary", use_container_width=True, key="p_scen_5"):
            st.session_state['pos_scenario'] = 'ato'
            st.session_state['pos_tx_state'] = 'idle'
            st.rerun()

    st.write("")

    scenarios_meta = {
        "normal": {
            "title": "Verifone V400m Smart POS (pos_sf_441)", "customer": "SARAH CONNOR", "account_id": "acc_legit_100",
            "amount": "$4.50", "merchant": "Blue Bottle Coffee - San Francisco, CA", "pan": "•••• •••• •••• 9481", "exp": "08/29",
            "card_brand": "VISA SIGNATURE", "channel": "EMV CONTACTLESS NFC", "card_theme": "linear-gradient(135deg, #1A73E8 0%, #0D47A1 100%)",
            "is_fraud": False, "status_title": "TRANSACTION APPROVED", "status_code": "AUTH-849201", "score": "0.4% (Low Risk)",
            "speed_sla": "0.16s", "plain_summary": "Routine $4.50 coffee tap by Sarah Connor in San Francisco. Zero anomaly signals detected.",
            "why_decision": [
                ("📊 Normal Spending Routine", "Matches cardholder's verified daily coffee and retail transaction profile."),
                ("📍 Local Presence Confirmed", "Physical card tapped at verified San Francisco coordinates matching recent device activity."),
                ("📱 Authentic Hardware ID", "Authentic hardware signature; no proxy or rooted emulator flags.")
            ],
            "action_taken": "Transaction approved immediately on payment network without customer friction in 0.16s."
        },
        "syndicate": {
            "title": "Flagship Electronics POS Terminal (pos_de_882)", "customer": "JORDAN VANCE", "account_id": "acc_syndicate_02",
            "amount": "$2,499.00", "merchant": "Best Buy Electronics - Wilmington, DE", "pan": "•••• •••• •••• 9483", "exp": "11/28",
            "card_brand": "MASTERCARD WORLD ELITE", "channel": "MOBILE NFC CHECKOUT", "card_theme": "linear-gradient(135deg, #202124 0%, #3C4043 50%, #17181C 100%)",
            "is_fraud": True, "status_title": "TRANSACTION DECLINED / BLOCKED", "status_code": "DECLINE-05 (FRAUD_SUSPECTED)", "score": "99.2% (Critical Risk)",
            "speed_sla": "1.42s", "plain_summary": "$2,499.00 purchase blocked on dormant account originating from known syndicate emulator.",
            "why_decision": [
                ("🚨 Extreme Spending Spike", "Transaction amount is 30x higher than customer's previous 90-day baseline average."),
                ("📱 Rooted Hardware Signature", "Originated from virtual Android emulator signature dev_fp_ring_99."),
                ("🕸️ Syndicate Graph Linkage", "BigQuery Graph links account to confirmed fraudster Alex Mercer and freight drop 104 Industrial Pkwy.")
            ],
            "action_taken": "Card temporarily frozen on payment network. 2-way verification SMS dispatched to cardholder."
        },
        "botnet": {
            "title": "Stripe / Cybersource Gateway API (api_gw_991)", "customer": "BOTNET INGRESS PROBE", "account_id": "acc_botnet_01",
            "amount": "$0.99", "merchant": "Digital Charity Donation / Gaming Micro-Charge", "pan": "•••• •••• •••• 1029", "exp": "01/27",
            "card_brand": "VISA TESTING PAN", "channel": "E-COMMERCE API INGRESS", "card_theme": "linear-gradient(135deg, #C5221F 0%, #8C1D18 100%)",
            "is_fraud": True, "status_title": "TRANSACTION BLOCKED / RATE-LIMITED", "status_code": "DECLINE-82 (BIN_BURST_ATTACK)", "score": "99.7% (Critical Risk)",
            "speed_sla": "0.11s", "plain_summary": "Sub-second $0.99 card validation probe blocked by BigQuery Continuous Queries BIN velocity filter.",
            "why_decision": [
                ("⚡ High-Velocity BIN Brute Force", "Over 80 authorization attempts/sec detected against issuer BIN 411111."),
                ("🔄 Sequential CVV Cycling", "Multiple sequential expiration dates and CVV codes tested from the same IP proxy subnet."),
                ("🤖 Non-Human Automation", "Sub-millisecond headless browser execution without human mouse or touch telemetry.")
            ],
            "action_taken": "Authorization dropped at perimeter gateway; originating proxy subnet blacklisted for 24 hours."
        },
        "impossible_travel": {
            "title": "London Heathrow T5 Duty Free POS (pos_lhr_104)", "customer": "SARAH CONNOR", "account_id": "acc_legit_100",
            "amount": "$850.00", "merchant": "Harrods Luxury Boutique - London, UK", "pan": "•••• •••• •••• 9481", "exp": "08/29",
            "card_brand": "VISA GOLD ELITE", "channel": "EMV CONTACTLESS NFC", "card_theme": "linear-gradient(135deg, #E37400 0%, #B06000 50%, #7E4000 100%)",
            "is_fraud": True, "status_title": "TRANSACTION BLOCKED / STEP-UP REQUIRED", "status_code": "DECLINE-71 (GEO_VELOCITY_ANOMALY)", "score": "96.8% (High Risk)",
            "speed_sla": "0.14s", "plain_summary": "Physical card tapped in London 5 minutes after a verified tap in New York (22,400 km/h anomaly).",
            "why_decision": [
                ("✈️ Impossible Travel Velocity", "GIS Math: ST_Distance(NY, London) = 5,570 km within 5 minutes (22,400 km/h)."),
                ("📍 Concurrent Device Location", "Cardholder device GPS confirmed active in San Francisco / New York."),
                ("⚠️ Cloned Magstripe Anomaly", "Physical terminal in London attempted swipe without valid EMV token.")
            ],
            "action_taken": "Transaction blocked; push notification and SMS alert dispatched requesting biometric confirmation."
        },
        "ato": {
            "title": "Mobile Banking Security Gateway (auth_gw_77)", "customer": "JORDAN VANCE", "account_id": "acc_legit_101",
            "amount": "$0.00 (Password & 2FA Reset)", "merchant": "Mobile Account Security Portal", "pan": "•••• •••• •••• 9482", "exp": "12/30",
            "card_brand": "VIRTUAL ACCESS TOKEN", "channel": "MOBILE AUTHENTICATION", "card_theme": "linear-gradient(135deg, #7B1FA2 0%, #4A148C 100%)",
            "is_fraud": True, "status_title": "SESSION TERMINATED / STEP-UP 2FA", "status_code": "AUTH_BLOCKED (ATO_FAN_IN)", "score": "98.9% (Critical Risk)",
            "speed_sla": "0.18s", "plain_summary": "Credential reset hijacked by rooted emulator attempting rapid multi-account fan-in takeover.",
            "why_decision": [
                ("🔑 Multi-Account Fan-In Origin", "Single rooted Android emulator dev_fp_ring_99 initiated 3 password resets in 4 minutes."),
                ("🌐 High-Risk Proxy ASN", "Request originated from high-risk hosting ASN (Proxy: 198.51.100.24)."),
                ("📱 Rapid 2FA Phone Tampering", "Immediate attempt to swap registered MFA phone number upon password reset.")
            ],
            "action_taken": "Active session invalidated immediately; mandatory out-of-band identity verification requested."
        }
    }

    scen_key = st.session_state['pos_scenario']
    if scen_key not in scenarios_meta:
        scen_key = "normal"
    current = scenarios_meta[scen_key]

    col_sim_left, col_sim_right = st.columns([1.1, 1.25], gap="large")
    
    # LEFT COLUMN: VERIFONE HARDWARE POS TERMINAL
    with col_sim_left:
        terminal_html = f"""
        <div class="pos-terminal-frame">
            <div class="pos-terminal-header">
                <div>
                    <b style="font-size:0.95rem; color:#202124;">📟 {current['title']}</b>
                    <div style="font-size:0.75rem; color:#5F6368; margin-top:2px;">Network: <b>5G Ultra Secure</b> • EMV L2 Kernel Ready</div>
                </div>
                <span style="background:#E6F4EA; color:#137333 !important; font-size:0.72rem; font-weight:800; padding:4px 8px; border-radius:4px; border:1px solid #CEEAD6;">ONLINE</span>
            </div>

            <div class="pos-amount-display">
                <div>
                    <div style="font-size:0.70rem; font-weight:800; color:#5F6368; text-transform:uppercase; letter-spacing:0.5px;">AMOUNT DUE</div>
                    <div style="font-size:1.80rem; font-weight:800; color:#202124; margin-top:1px;">{current['amount']}</div>
                    <div style="font-size:0.80rem; color:#5F6368; margin-top:2px;">📍 {current['merchant']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.8rem;">📶</div>
                    <div style="font-size:0.68rem; font-weight:700; color:#1A73E8;">NFC READY</div>
                </div>
            </div>

            <div class="pos-card-container" style="background:{current['card_theme']};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div style="font-weight:800; font-size:0.92rem; letter-spacing:1px; color:#FFFFFF !important;">💳 {current['card_brand']}</div>
                    <div style="font-size:0.80rem; opacity:0.90; color:#FFFFFF !important;">📶 Contactless</div>
                </div>
                <div style="margin-bottom:10px;">
                    <div class="pos-card-chip">
                        <div style="position:absolute; top:10px; left:0; right:0; height:1px; background:#B8860B;"></div>
                        <div style="position:absolute; bottom:10px; left:0; right:0; height:1px; background:#B8860B;"></div>
                        <div style="position:absolute; top:0; bottom:0; left:14px; width:1px; background:#B8860B;"></div>
                        <div style="position:absolute; top:0; bottom:0; right:14px; width:1px; background:#B8860B;"></div>
                    </div>
                </div>
                <div class="pos-card-pan" style="color:#FFFFFF !important;">{current['pan']}</div>
                <div class="pos-card-meta">
                    <div>
                        <div style="font-size:0.62rem; text-transform:uppercase; opacity:0.80; color:#FFFFFF !important;">CARDHOLDER</div>
                        <div class="pos-card-holder" style="color:#FFFFFF !important;">{current['customer']}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:0.62rem; text-transform:uppercase; opacity:0.80; color:#FFFFFF !important;">EXPIRES</div>
                        <div style="font-family:'Roboto Mono', monospace; font-weight:700; font-size:0.85rem; color:#FFFFFF !important;">{current['exp']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:0.62rem; text-transform:uppercase; opacity:0.80; color:#FFFFFF !important;">CHANNEL</div>
                        <div style="font-size:0.75rem; font-weight:600; color:#FFFFFF !important;">{current['channel']}</div>
                    </div>
                </div>
            </div>
            
            <div class="pos-tap-zone">
                (( 📶 Ready for Contactless Tap or Chip Insertion ))
            </div>
        </div>
        """
        render_html(terminal_html)

        st.write("")
        if st.button("💳  TAP CARD / AUTHORIZE NOW", type="primary", use_container_width=True):
            st.session_state['pos_tx_state'] = 'authorized'
            st.toast(f"⚡ {current['status_title']} ({current['speed_sla']})", icon="🟢" if not current['is_fraud'] else "🚨")
            st.rerun()

        if st.session_state['pos_tx_state'] == 'authorized':
            if not current['is_fraud']:
                appr_html = f"""
                <div style="background:#E6F4EA; border:1.5px solid #34A853; border-left:6px solid #137333; border-radius:8px; padding:12px 16px; margin-top:12px; box-shadow:0 2px 6px rgba(52,168,83,0.10);">
                    <div style="color:#137333; font-weight:800; font-size:1.0rem;">🟢 {current['status_title']}</div>
                    <div style="font-size:0.84rem; color:#202124; margin-top:2px;">Auth Code: <code>{current['status_code']}</code> • Intercept SLA: <b>{current['speed_sla']}</b></div>
                </div>
                """
                render_html(appr_html)
            else:
                decl_html = f"""
                <div style="background:#FCE8E6; border:1.5px solid #EA4335; border-left:6px solid #C5221F; border-radius:8px; padding:12px 16px; margin-top:12px; box-shadow:0 2px 6px rgba(234,67,53,0.10);">
                    <div style="color:#C5221F; font-weight:800; font-size:1.0rem;">🚨 {current['status_title']}</div>
                    <div style="font-size:0.84rem; color:#202124; margin-top:2px;">Decline Code: <code>{current['status_code']}</code> • Intercept SLA: <b>{current['speed_sla']}</b></div>
                </div>
                """
                render_html(decl_html)

    # RIGHT COLUMN: GEMINI MULTIMODAL DECISION DOSSIER
    with col_sim_right:
        if st.session_state['pos_tx_state'] == 'idle':
            idle_dossier = """
            <div class="dossier-frame" style="display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:40px 24px;">
                <div style="font-size:3.8rem; margin-bottom:12px;">🧠</div>
                <h4 style="color:#1A73E8; margin-bottom:6px; font-weight:700;">Gemini Autonomous Decision Engine</h4>
                <p style="color:#5F6368; font-size:0.92rem; max-width:420px; line-height:1.55;">
                    The real-time authorization engine is standing by.<br>
                    Click <b>'💳 TAP CARD / AUTHORIZE NOW'</b> on the left terminal to trigger Gemini's real-time risk diagnostic dossier.
                </p>
            </div>
            """
            render_html(idle_dossier)
        else:
            badge_class = "dossier-pill-danger" if current['is_fraud'] else "dossier-pill-success"
            verdict_icon = "🚨" if current['is_fraud'] else "🟢"
            border_col = "#EA4335" if current['is_fraud'] else "#34A853"
            bg_act = "#FCE8E6" if current['is_fraud'] else "#E6F4EA"
            border_act = "#FAD2CF" if current['is_fraud'] else "#CEEAD6"
            col_act = "#C5221F" if current['is_fraud'] else "#137333"

            reasons_html = ""
            for heading, detail in current['why_decision']:
                reasons_html += f"""
                <div style="display:flex; gap:10px; margin-bottom:10px; align-items:flex-start; font-size:0.86rem; line-height:1.5;">
                    <div style="font-size:1.1rem; line-height:1.2;">{verdict_icon}</div>
                    <div>
                        <b style="color:#202124;">{heading}:</b>
                        <span style="color:#3C4043;"> {detail}</span>
                    </div>
                </div>
                """

            dossier_html = f"""
            <div class="dossier-frame">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1.5px solid #F1F3F4; padding-bottom:12px; margin-bottom:14px;">
                    <div>
                        <h4 style="color:#1A73E8; margin:0; font-weight:800;">🧠 Gemini Autonomous Decision Dossier</h4>
                        <div style="font-size:0.75rem; color:#5F6368; margin-top:2px;">Engine: Vertex AI Gemini Multimodal • BigQuery Continuous Queries</div>
                    </div>
                </div>

                <div class="dossier-hud-bar">
                    <span class="dossier-pill {badge_class}">
                        {verdict_icon} {current['status_title']}
                    </span>
                    <span class="dossier-pill dossier-pill-info">
                        ⚡ {current['speed_sla']} Decision SLA
                    </span>
                    <span class="dossier-pill {badge_class}">
                        🎯 Risk Score: {current['score']}
                    </span>
                </div>

                <div style="background:#F8F9FA; border:1px solid #DADCE0; border-left:4px solid {border_col}; border-radius:8px; padding:12px 16px; margin-bottom:16px;">
                    <b style="color:#202124; font-size:0.90rem;">Diagnostic Executive Summary:</b>
                    <div style="font-size:0.86rem; color:#3C4043; margin-top:4px; line-height:1.5;">{current['plain_summary']}</div>
                </div>

                <div style="margin-bottom:16px;">
                    <b style="color:#202124; font-size:0.90rem;">Multimodal AI Risk Evidence Matrix:</b>
                    <div style="margin-top:8px;">
                        {reasons_html}
                    </div>
                </div>

                <div style="background:{bg_act}; border:1px solid {border_act}; border-radius:8px; padding:12px 16px; margin-top:10px;">
                    <b style="color:{col_act}; font-size:0.88rem;">Autonomous Policy Action:</b>
                    <div style="font-size:0.84rem; color:{col_act}; margin-top:3px; font-weight:600;">{current['action_taken']}</div>
                </div>
            </div>
            """
            render_html(dossier_html)

# ==============================================================================
# VIEW 3: STREAMLINED OPERATIONS COMMAND CENTER
# ==============================================================================
else:
    # Sleek Compact Title
    st.markdown('<h3 style="color:#1A73E8; margin-top:0px; margin-bottom:2px; font-weight:700;">🛡️ Real-Time Fraud Operations Command Center</h3>', unsafe_allow_html=True)
    st.caption("Google Cloud Agentic Data Platform • BigQuery Continuous Queries • In-Warehouse Graph (ISO GQL) • Vertex AI")

    # ==========================================================================
    # ENHANCEMENT 1: EXECUTIVE BUSINESS IMPACT & FINANCIAL ROI RIBBON
    # ==========================================================================
    st.markdown("""
    <div class="exec-impact-banner">
        <div style="flex: 1.2;">
            <div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.90;">CAPITAL PROTECTED (TODAY)</div>
            <div style="font-size: 1.25rem; font-weight: 800; margin-top: 1px;">💰 $1,420,000 Prevented</div>
        </div>
        <div style="flex: 1; text-align: center; border-left: 1px solid rgba(255,255,255,0.25); border-right: 1px solid rgba(255,255,255,0.25); padding: 0 10px;">
            <div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.90;">DECISION VELOCITY</div>
            <div style="font-size: 1.25rem; font-weight: 800; margin-top: 1px;">⚡ 0.16s SLA <span style="font-size:0.72rem; font-weight:600; opacity:0.85;">(vs 48hr)</span></div>
        </div>
        <div style="flex: 1; text-align: center; border-right: 1px solid rgba(255,255,255,0.25); padding: 0 10px;">
            <div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.90;">FALSE POSITIVES</div>
            <div style="font-size: 1.25rem; font-weight: 800; margin-top: 1px;">🎯 &lt; 0.1% Friction</div>
        </div>
        <div style="flex: 1; text-align: right;">
            <div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.90;">INFRASTRUCTURE TCO</div>
            <div style="font-size: 1.25rem; font-weight: 800; margin-top: 1px;">📉 42% Cost Savings</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 4 Main Operations Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔴 1. Live Stream Interception", 
        "🕸️ 2. Property Graph (ISO GQL)", 
        "🤖 3. Autonomous Triage", 
        "🎭 4. Multimodal KYC & Deepfake"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: STREAM INTERCEPTION
    # --------------------------------------------------------------------------
    with tab1:
        st.subheader("Sub-Second Stream Processing & Multi-Vector Anomaly Scoring")
        st.caption("BigQuery Continuous Queries scoring events at ingestion: 🟡 **New Ingest**, 🔴 **High Risk / Fraud**, 🟢 **Clean Approved**.")
        st.write("")
        ca, cb = st.columns(2)
        with ca:
            st.markdown("##### 📥 Raw Ingestion Stream (`live_transactions_stream`)")
            raw_rows = []
            if client:
                try:
                    raw_rows = list(client.query(f"SELECT transaction_id, account_id, amount, merchant_category, COALESCE(card_bin, 'N/A') as bin, COALESCE(channel, 'POS') as channel FROM `{PROJECT_ID}.fraud_engine.live_transactions_stream` ORDER BY timestamp DESC LIMIT 5").result())
                except Exception: pass
            if not raw_rows:
                raw_rows = [type('Row', (), d) for d in st.session_state['in_memory_raw_stream'][:5]]

            tbl = '<table class="stream-table"><tr><th>Txn ID</th><th>Account</th><th>Amount</th><th>Category</th><th>BIN</th></tr>'
            for r in raw_rows:
                is_new = r.transaction_id in st.session_state['latest_txn_ids']
                tbl += f'<tr class="{"row-new" if is_new else "row-clean"}"><td><b>{r.transaction_id}</b></td><td>{r.account_id}</td><td>${r.amount:,.2f}</td><td>{r.merchant_category}</td><td><code>{r.bin}</code></td></tr>'
            tbl += '</table>'
            st.markdown(tbl, unsafe_allow_html=True)

        with cb:
            st.markdown("##### ⚡ Scored Anomaly Stream (`live_transactions_scored`)")
            sc_rows = []
            if client:
                try:
                    sc_rows = list(client.query(f"SELECT transaction_id, account_id, amount, is_bin_attack, is_impossible_travel, is_suspicious_device, is_high_risk_amount FROM `{PROJECT_ID}.fraud_engine.live_transactions_scored` ORDER BY processed_at DESC LIMIT 5").result())
                except Exception: pass
            if not sc_rows:
                sc_rows = [type('Row', (), d) for d in st.session_state['in_memory_scored_stream'][:5]]

            tbl2 = '<table class="stream-table"><tr><th>Txn ID</th><th>Account</th><th>BIN Attack</th><th>Geo Travel</th><th>Verdict</th></tr>'
            for r in sc_rows:
                is_new = r.transaction_id in st.session_state['latest_txn_ids']
                is_fraud = r.is_bin_attack or r.is_impossible_travel or r.is_suspicious_device or r.is_high_risk_amount
                badge = '<span class="badge-fraud">🚨 BLOCKED</span>' if is_fraud else '<span class="badge-clean">🟢 APPROVED</span>'
                tbl2 += f'<tr class="{"row-new" if is_new else ("row-fraud" if is_fraud else "row-clean")}"><td><b>{r.transaction_id}</b></td><td>{r.account_id}</td><td>{"⚠️ True" if r.is_bin_attack else "False"}</td><td>{"⚠️ True" if r.is_impossible_travel else "False"}</td><td>{badge}</td></tr>'
            tbl2 += '</table>'
            st.markdown(tbl2, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 2: PROPERTY GRAPH (ISO GQL)
    # --------------------------------------------------------------------------
    with tab2:
        st.subheader("In-Warehouse Property Graph: Multi-Hop ISO GQL Pattern Traversals")
        st.caption("Native BigQuery graph queries exposing complex fraud rings with **zero data movement**.")
        st.write("")

        btn_c1, btn_c2, btn_c3 = st.columns(3)
        with btn_c1:
            is_p1 = st.session_state['selected_graph_pattern'] == 'pattern1'
            if st.button("🕸️ Pattern 1: 4-Hop Syndicate Ring", type="primary" if is_p1 else "secondary", use_container_width=True):
                st.session_state['selected_graph_pattern'] = 'pattern1'
                st.rerun()

        with btn_c2:
            is_p2 = st.session_state['selected_graph_pattern'] == 'pattern2'
            if st.button("🔑 Pattern 2: ATO Reset Fan-In", type="primary" if is_p2 else "secondary", use_container_width=True):
                st.session_state['selected_graph_pattern'] = 'pattern2'
                st.rerun()

        with btn_c3:
            is_p3 = st.session_state['selected_graph_pattern'] == 'pattern3'
            if st.button("💸 Pattern 3: Mule Layering", type="primary" if is_p3 else "secondary", use_container_width=True):
                st.session_state['selected_graph_pattern'] = 'pattern3'
                st.rerun()

        st.write("")

        if st.session_state['selected_graph_pattern'] == 'pattern1':
            svg_syndicate = """
<div style="background-color:#FFFFFF; border:1.5px solid #D2E3FC; border-radius:10px; padding:18px; text-align:center; margin-bottom:14px; box-shadow:0 2px 8px rgba(26,115,232,0.08);">
<svg viewBox="0 0 1000 320" width="100%" height="280" xmlns="http://www.w3.org/2000/svg">
<line x1="180" y1="70" x2="480" y2="140" stroke="#EA4335" stroke-width="3.5" stroke-dasharray="8,5" />
<line x1="180" y1="240" x2="480" y2="140" stroke="#EA4335" stroke-width="3.5" stroke-dasharray="8,5" />
<line x1="520" y1="140" x2="820" y2="70" stroke="#EA4335" stroke-width="3.5" stroke-dasharray="8,5" />
<line x1="180" y1="70" x2="820" y2="240" stroke="#FBBC04" stroke-width="3" />
<line x1="180" y1="240" x2="820" y2="240" stroke="#FBBC04" stroke-width="3" />
<rect x="290" y="88" width="100" height="20" rx="4" fill="#FCE8E6" stroke="#EA4335" stroke-width="1"/>
<text x="340" y="102" font-size="10" font-weight="700" fill="#C5221F" text-anchor="middle">USED_DEVICE</text>
<rect x="290" y="195" width="100" height="20" rx="4" fill="#FCE8E6" stroke="#EA4335" stroke-width="1"/>
<text x="340" y="209" font-size="10" font-weight="700" fill="#C5221F" text-anchor="middle">USED_DEVICE</text>
<rect x="630" y="88" width="100" height="20" rx="4" fill="#FCE8E6" stroke="#EA4335" stroke-width="1"/>
<text x="680" y="102" font-size="10" font-weight="700" fill="#C5221F" text-anchor="middle">USED_DEVICE</text>
<rect x="460" y="248" width="95" height="20" rx="4" fill="#FEF7E0" stroke="#FBBC04" stroke-width="1"/>
<text x="507" y="262" font-size="10" font-weight="700" fill="#B06000" text-anchor="middle">SHIPPED_TO</text>
<g>
<circle cx="180" cy="70" r="44" fill="#FCE8E6" stroke="#EA4335" stroke-width="3" />
<text x="180" y="65" font-size="13" font-weight="800" fill="#C5221F" text-anchor="middle">Jordan Vance</text>
<text x="180" y="82" font-size="10" font-weight="600" fill="#5F6368" text-anchor="middle">acc_syndicate_02</text>
</g>
<g>
<circle cx="180" cy="240" r="44" fill="#FCE8E6" stroke="#EA4335" stroke-width="3" />
<text x="180" y="235" font-size="13" font-weight="800" fill="#C5221F" text-anchor="middle">Taylor Reed</text>
<text x="180" y="252" font-size="10" font-weight="600" fill="#5F6368" text-anchor="middle">acc_syndicate_03</text>
</g>
<g>
<rect x="380" y="95" width="240" height="90" rx="10" fill="#F8FAFD" stroke="#1A73E8" stroke-width="3" />
<text x="500" y="125" font-size="14" font-weight="800" fill="#174EA6" text-anchor="middle">📱 Shared Emulator Bridge</text>
<text x="500" y="146" font-size="12" font-weight="700" fill="#C5221F" text-anchor="middle">dev_fp_ring_99</text>
<text x="500" y="166" font-size="10" font-weight="600" fill="#5F6368" text-anchor="middle">Rooted Android Hardware ID</text>
</g>
<g>
<circle cx="820" cy="70" r="46" fill="#FCE8E6" stroke="#EA4335" stroke-width="3.5" />
<text x="820" y="60" font-size="13" font-weight="800" fill="#C5221F" text-anchor="middle">Alex Mercer</text>
<text x="820" y="76" font-size="10" font-weight="700" fill="#EA4335" text-anchor="middle">🚨 CONFIRMED FRAUD</text>
<text x="820" y="90" font-size="9" fill="#5F6368" text-anchor="middle">acc_syndicate_01</text>
</g>
<g>
<circle cx="820" cy="240" r="44" fill="#E8F0FE" stroke="#4285F4" stroke-width="3" />
<text x="820" y="234" font-size="13" font-weight="800" fill="#174EA6" text-anchor="middle">🏢 Freight Drop</text>
<text x="820" y="252" font-size="10" font-weight="600" fill="#5F6368" text-anchor="middle">104 Industrial Pkwy</text>
</g>
<g transform="translate(160, 290)">
<rect x="0" y="0" width="680" height="24" rx="4" fill="#F8F9FA" stroke="#DADCE0" stroke-width="1"/>
<circle cx="16" cy="12" r="5" fill="#EA4335" /><text x="28" y="15" font-size="10" font-weight="700" fill="#3C4043">Confirmed Fraudster</text>
<circle cx="180" cy="12" r="5" fill="#FBBC04" /><text x="192" y="15" font-size="10" font-weight="700" fill="#3C4043">Target Account</text>
<rect x="330" y="6" width="12" height="12" rx="2" fill="#1A73E8" /><text x="348" y="15" font-size="10" font-weight="700" fill="#3C4043">Shared Hardware Bridge</text>
<circle cx="560" cy="12" r="5" fill="#4285F4" /><text x="572" y="15" font-size="10" font-weight="700" fill="#3C4043">Drop Address</text>
</g>
</svg>
</div>
"""
            render_svg_clean(svg_syndicate)
            
            c_q1, c_q2 = st.columns([1, 1], gap="medium")
            with c_q1:
                gql_p1 = """SELECT * FROM GRAPH_TABLE(
  `admin-demo-test1.fraud_engine.fintech_fraud_graph`
  MATCH (suspicious:Account)-[e1:USED_DEVICE]->(d:Device)
        <-[e2:USED_DEVICE]-(fraud:Account)-[e3:SHIPPED_TO]->(addr:Address)
        <-[e4:SHIPPED_TO]-(suspicious)
  WHERE fraud.kyc_status = 'CONFIRMED_FRAUD'
  COLUMNS (suspicious.account_id, fraud.customer_name, d.device_id, addr.full_address)
);"""
                st.markdown(f'<div class="code-box">{gql_p1}</div>', unsafe_allow_html=True)
            with c_q2:
                st.markdown("""
                <div class="box-blue">
                  <b style="font-size:0.95rem; color:#174EA6;">⚡ In-Warehouse Graph Intelligence (28ms)</b>
                  <p style="font-size:0.86rem; line-height:1.55; margin-top:6px; margin-bottom:0;">
                  • <b>4-Hop Ring Uncovered:</b> Directly links Jordan Vance to confirmed fraudster Alex Mercer via rooted emulator <code>dev_fp_ring_99</code>.<br>
                  • <b>Zero Data Movement:</b> Executed natively inside BigQuery across 100M+ nodes without exporting tables.<br>
                  • <b>Autonomous Remediation:</b> Instantly triggers network-level hold on all linked accounts.
                  </p>
                </div>
                """, unsafe_allow_html=True)

        elif st.session_state['selected_graph_pattern'] == 'pattern2':
            svg_ato = """
<div style="background-color:#FFFFFF; border:1.5px solid #FCE8E6; border-radius:10px; padding:18px; text-align:center; margin-bottom:14px; box-shadow:0 2px 8px rgba(234,67,53,0.08);">
<svg viewBox="0 0 1000 300" width="100%" height="270" xmlns="http://www.w3.org/2000/svg">
<line x1="330" y1="140" x2="680" y2="55" stroke="#EA4335" stroke-width="3" stroke-dasharray="6,4" />
<line x1="330" y1="140" x2="680" y2="140" stroke="#EA4335" stroke-width="3" stroke-dasharray="6,4" />
<line x1="330" y1="140" x2="680" y2="225" stroke="#EA4335" stroke-width="3" stroke-dasharray="6,4" />

<rect x="460" y="76" width="130" height="20" rx="4" fill="#FCE8E6" stroke="#EA4335" stroke-width="1"/>
<text x="525" y="90" font-size="9" font-weight="700" fill="#C5221F" text-anchor="middle">PASSWORD_RESET</text>

<rect x="460" y="130" width="130" height="20" rx="4" fill="#FCE8E6" stroke="#EA4335" stroke-width="1"/>
<text x="525" y="144" font-size="9" font-weight="700" fill="#C5221F" text-anchor="middle">2FA_PHONE_CHANGED</text>

<rect x="460" y="186" width="130" height="20" rx="4" fill="#FCE8E6" stroke="#EA4335" stroke-width="1"/>
<text x="525" y="200" font-size="9" font-weight="700" fill="#C5221F" text-anchor="middle">PASSWORD_RESET</text>

<g>
<rect x="90" y="85" width="240" height="110" rx="10" fill="#FCE8E6" stroke="#EA4335" stroke-width="3.5" />
<text x="210" y="120" font-size="14" font-weight="800" fill="#C5221F" text-anchor="middle">🚨 Attacking Emulator</text>
<text x="210" y="142" font-size="13" font-weight="800" fill="#C5221F" text-anchor="middle">dev_fp_ring_99</text>
<text x="210" y="162" font-size="10" font-weight="600" fill="#5F6368" text-anchor="middle">IP: 198.51.100.24 (Proxy)</text>
<text x="210" y="178" font-size="9" font-weight="700" fill="#EA4335" text-anchor="middle">FAN-IN HIJACK ORIGIN</text>
</g>

<g>
<circle cx="740" cy="55" r="42" fill="#F8FAFD" stroke="#1A73E8" stroke-width="2.5" />
<text x="740" y="50" font-size="12" font-weight="800" fill="#174EA6" text-anchor="middle">Sarah Connor</text>
<text x="740" y="66" font-size="9" font-weight="700" fill="#C5221F" text-anchor="middle">acc_legit_100</text>
</g>

<g>
<circle cx="740" cy="140" r="42" fill="#F8FAFD" stroke="#1A73E8" stroke-width="2.5" />
<text x="740" y="135" font-size="12" font-weight="800" fill="#174EA6" text-anchor="middle">Jordan Vance</text>
<text x="740" y="151" font-size="9" font-weight="700" fill="#C5221F" text-anchor="middle">acc_legit_101</text>
</g>

<g>
<circle cx="740" cy="225" r="42" fill="#F8FAFD" stroke="#1A73E8" stroke-width="2.5" />
<text x="740" y="220" font-size="12" font-weight="800" fill="#174EA6" text-anchor="middle">Taylor Reed</text>
<text x="740" y="236" font-size="9" font-weight="700" fill="#C5221F" text-anchor="middle">acc_legit_102</text>
</g>
</svg>
</div>
"""
            render_svg_clean(svg_ato)
            
            c_q1, c_q2 = st.columns([1, 1], gap="medium")
            with c_q1:
                gql_p2 = """SELECT * FROM GRAPH_TABLE(
  `admin-demo-test1.fraud_engine.fintech_fraud_graph`
  MATCH (d:Device {device_id: 'dev_fp_ring_99'})<-[r:USED_DEVICE]-(victim:Account)
  COLUMNS (
    d.device_id, 
    victim.account_id, 
    victim.customer_name, 
    r.event_type, 
    r.timestamp
  )
);"""
                st.markdown(f'<div class="code-box">{gql_p2}</div>', unsafe_allow_html=True)
            with c_q2:
                st.markdown("""
                <div class="box-blue">
                  <b style="font-size:0.95rem; color:#174EA6;">⚡ Account Takeover (ATO) Fan-In Detection (18ms)</b>
                  <p style="font-size:0.86rem; line-height:1.55; margin-top:6px; margin-bottom:0;">
                  • <b>Multi-Account Attack Origin:</b> A single rooted Android emulator (<code>dev_fp_ring_99</code>) initiated 3 credential resets across unrelated accounts within 4 minutes.<br>
                  • <b>Graph Pattern Matching:</b> Rapid 1-to-N fan-in topology flagged before unauthorized fund transfers could execute.<br>
                  • <b>Autonomous Remediation:</b> Instantly invalidated active auth tokens and dispatched SMS step-up verification.
                  </p>
                </div>
                """, unsafe_allow_html=True)

        else:
            svg_mule = """
<div style="background-color:#FFFFFF; border:1.5px solid #FEF7E0; border-radius:10px; padding:18px; text-align:center; margin-bottom:14px; box-shadow:0 2px 8px rgba(251,188,4,0.08);">
<svg viewBox="0 0 1000 280" width="100%" height="260" xmlns="http://www.w3.org/2000/svg">
<line x1="160" y1="130" x2="380" y2="130" stroke="#EA4335" stroke-width="3.5" />
<line x1="460" y1="130" x2="680" y2="130" stroke="#FBBC04" stroke-width="3.5" />
<line x1="760" y1="130" x2="890" y2="130" stroke="#EA4335" stroke-width="3.5" stroke-dasharray="6,4" />

<rect x="230" y="105" width="100" height="20" rx="4" fill="#FCE8E6" stroke="#EA4335" stroke-width="1"/>
<text x="280" y="119" font-size="9" font-weight="700" fill="#C5221F" text-anchor="middle">$10,000 INFLOW</text>

<rect x="530" y="105" width="100" height="20" rx="4" fill="#FEF7E0" stroke="#FBBC04" stroke-width="1"/>
<text x="580" y="119" font-size="9" font-weight="700" fill="#B06000" text-anchor="middle">4x $2,450 SPLIT</text>

<rect x="790" y="105" width="90" height="20" rx="4" fill="#FCE8E6" stroke="#EA4335" stroke-width="1"/>
<text x="835" y="119" font-size="9" font-weight="700" fill="#C5221F" text-anchor="middle">CRYPTO CASHOUT</text>

<g>
<circle cx="120" cy="130" r="44" fill="#FCE8E6" stroke="#EA4335" stroke-width="3" />
<text x="120" y="125" font-size="12" font-weight="800" fill="#C5221F" text-anchor="middle">Victim Account</text>
<text x="120" y="142" font-size="9" fill="#5F6368" text-anchor="middle">Phished Inflow</text>
</g>

<g>
<circle cx="420" cy="130" r="44" fill="#FEF7E0" stroke="#FBBC04" stroke-width="3" />
<text x="420" y="125" font-size="12" font-weight="800" fill="#B06000" text-anchor="middle">Mule Tier 1</text>
<text x="420" y="142" font-size="9" fill="#5F6368" text-anchor="middle">Rapid Smurfing</text>
</g>

<g>
<circle cx="720" cy="130" r="44" fill="#FEF7E0" stroke="#FBBC04" stroke-width="3" />
<text x="720" y="125" font-size="12" font-weight="800" fill="#B06000" text-anchor="middle">Mule Tier 2</text>
<text x="720" y="142" font-size="9" fill="#5F6368" text-anchor="middle">Layered Transfers</text>
</g>

<g>
<circle cx="930" cy="130" r="44" fill="#FCE8E6" stroke="#EA4335" stroke-width="3.5" />
<text x="930" y="125" font-size="12" font-weight="800" fill="#C5221F" text-anchor="middle">Off-Ramp</text>
<text x="930" y="142" font-size="9" font-weight="700" fill="#EA4335" text-anchor="middle">Crypto Cash-Out</text>
</g>
</svg>
</div>
"""
            render_svg_clean(svg_mule)
            
            c_q1, c_q2 = st.columns([1, 1], gap="medium")
            with c_q1:
                gql_p3 = """SELECT * FROM GRAPH_TABLE(
  `admin-demo-test1.fraud_engine.fintech_fraud_graph`
  MATCH (src:Account)-[t:TRANSFERRED*1..3]->(dst:Account)
  WHERE src.kyc_status = 'VICTIM_COMPROMISED'
  COLUMNS (
    src.account_id AS origin, 
    dst.account_id AS destination, 
    COUNT(t) AS hop_count
  )
);"""
                st.markdown(f'<div class="code-box">{gql_p3}</div>', unsafe_allow_html=True)
            with c_q2:
                st.markdown("""
                <div class="box-blue">
                  <b style="font-size:0.95rem; color:#174EA6;">⚡ Variable-Length Path Traversal (31ms)</b>
                  <p style="font-size:0.86rem; line-height:1.55; margin-top:6px; margin-bottom:0;">
                  • <b>Smurfing & Layering Exposed:</b> Traced a $10,000 phished deposit through 4 rapid $2,450 micro-splits into Tier-2 mules and offshore crypto wallets.<br>
                  • <b>Variable Path Query (<code>*1..3</code>):</b> Traverses multiple intermediary accounts in milliseconds inside BigQuery without custom recursive code.<br>
                  • <b>Autonomous Remediation:</b> Froze downstream destination wallets prior to blockchain broadcasting.
                  </p>
                </div>
                """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 3: AUTONOMOUS AGENT TRIAGE (DYNAMIC ANIMATED STATE MACHINE)
    # --------------------------------------------------------------------------
    with tab3:
        col_hdr_l, col_hdr_r = st.columns([2.2, 1.4], gap="large")
        with col_hdr_l:
            st.subheader("Autonomous Fraud Incident Triage & Closed-Loop Remediation")
            st.caption("Sub-2-Second Closed Loop: Continuous Queries ➔ BigQuery Property Graph ➔ Autonomous Policy Containment ➔ Cardholder SMS.")
        
        with col_hdr_r:
            st.write("")
            b_c1, b_c2 = st.columns(2)
            with b_c1:
                if st.button("⚡  Trigger Live Triage", type="primary", use_container_width=True):
                    sim_box = st.empty()
                    steps = [
                        ("📥 1. Intercepting Stream Anomaly", "BigQuery Continuous Queries flagged $2,499.00 authorization burst on dormant account...", 25),
                        ("🕸️ 2. Executing ISO GQL Graph Traversal", "In-warehouse graph traversal mapped 4 hops to isolate Alex Mercer syndicate ring...", 50),
                        ("🔒 3. Applying Payment Network Policy Hold", "Card PAN •••• 9483 frozen on payment rails and active session tokens revoked...", 75),
                        ("📱 4. Dispatched 2-Way Cardholder SMS", "Pub/Sub + SMS shortcode 44102 alert delivered to Sarah Connor's device...", 100)
                    ]
                    for title, desc, pct in steps:
                        sim_box.markdown(f"""
                        <div style="background:#F8FAFD; border:1.5px solid #1A73E8; border-left:6px solid #1A73E8; border-radius:8px; padding:14px 18px; margin-bottom:16px; box-shadow:0 2px 10px rgba(26,115,232,0.12);">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <b style="color:#174EA6; font-size:1.02rem;">⚡ Autonomous Remediation in Progress: {title}</b>
                                <span style="background:#E8F0FE; color:#1A73E8; font-weight:800; font-size:0.78rem; padding:3px 8px; border-radius:4px;">{pct}% COMPLETE</span>
                            </div>
                            <div style="font-size:0.84rem; color:#3C4043; margin-bottom:10px;">{desc}</div>
                            <div style="width:100%; background:#E8EAED; border-radius:4px; height:6px; overflow:hidden;">
                                <div style="width:{pct}%; background:#1A73E8; height:100%; transition:width 0.3s ease;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        time.sleep(0.35)
                    sim_box.empty()
                    
                    st.session_state['triage_status'] = 'completed'
                    st.session_state['last_mitigation_time'] = "1.42s"
                    st.session_state['sms_reply_state'] = 'pending'
                    st.toast("🛡️ Autonomous Incident Contained & Card Frozen (1.42s SLA)!", icon="🟢")
                    st.rerun()

            with b_c2:
                if st.button("🔄  Reset Incident", use_container_width=True):
                    st.session_state['triage_status'] = 'idle'
                    st.session_state['sms_reply_state'] = 'pending'
                    st.toast("Simulation Reset to Unmitigated State.", icon="🔄")
                    st.rerun()

        st.write("")

        # DYNAMIC STATUS BANNER (BEFORE VS AFTER TRIAGE)
        is_done = st.session_state['triage_status'] == 'completed'
        if not is_done:
            st.markdown("""
            <div style="background:#FCE8E6; border:1.5px solid #EA4335; border-left:6px solid #C5221F; border-radius:8px; padding:14px 18px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 6px rgba(234,67,53,0.06);">
                <div>
                    <div style="color:#C5221F; font-size:1.05rem; font-weight:800;">🚨 UNMITIGATED CRITICAL THREAT: INC-8849201</div>
                    <div style="font-size:0.84rem; color:#3C4043; margin-top:2px;">Suspicious $2,499.00 electronics purchase on dormant syndicate profile <code>acc_syndicate_02</code></div>
                </div>
                <div style="text-align:right;">
                    <span style="background:#C5221F; color:#FFFFFF !important; font-weight:800; font-size:0.78rem; padding:4px 10px; border-radius:4px; letter-spacing:0.5px;">EXPOSURE: $2,499.00</span>
                    <div style="font-size:0.75rem; color:#C5221F; font-weight:700; margin-top:3px;">ACTION REQUIRED: TRIGGER TRIAGE</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#E6F4EA; border:1.5px solid #34A853; border-left:6px solid #137333; border-radius:8px; padding:14px 18px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 6px rgba(52,168,83,0.06);">
                <div>
                    <div style="color:#137333; font-size:1.05rem; font-weight:800;">🛡️ INCIDENT CONTAINED & NEUTRALIZED: INC-8849201</div>
                    <div style="font-size:0.84rem; color:#3C4043; margin-top:2px;">Card frozen on payment network • $0.00 financial loss • 2-Way verification SMS active</div>
                </div>
                <div style="text-align:right;">
                    <span style="background:#137333; color:#FFFFFF !important; font-weight:800; font-size:0.78rem; padding:4px 10px; border-radius:4px; letter-spacing:0.5px;">EXPOSURE: $0.00 (SAVED)</span>
                    <div style="font-size:0.75rem; color:#137333; font-weight:700; margin-top:3px;">⚡ 1.42s CLOSED LOOP SLA</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 4-Card Enterprise Playbook Stepper
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            if is_done:
                st.markdown("""
                <div class="stepper-card stepper-card-active">
                    <div class="stepper-num">STEP 1 • STREAM SCORING</div>
                    <div class="stepper-title">⚡ Anomaly Ingest</div>
                    <div style="font-size:0.80rem; color:#3C4043; line-height:1.45; margin-bottom:8px;">Flagged $2,499 burst & emulator device signature.</div>
                    <span class="stepper-tag">🟢 SCORED • 110ms</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="stepper-card stepper-card-pending">
                    <div class="stepper-num">STEP 1 • STREAM SCORING</div>
                    <div class="stepper-title">⚡ Anomaly Ingest</div>
                    <div style="font-size:0.80rem; color:#3C4043; line-height:1.45; margin-bottom:8px;">Pending trigger from real-time stream.</div>
                    <span class="stepper-tag stepper-tag-pending">🟡 PENDING TRIGGER</span>
                </div>
                """, unsafe_allow_html=True)

        with s2:
            if is_done:
                st.markdown("""
                <div class="stepper-card stepper-card-active">
                    <div class="stepper-num">STEP 2 • PROPERTY GRAPH</div>
                    <div class="stepper-title">🕸️ Graph Linkage</div>
                    <div style="font-size:0.80rem; color:#3C4043; line-height:1.45; margin-bottom:8px;">Linked to Alex Mercer ring via dev_fp_ring_99.</div>
                    <span class="stepper-tag">🟢 TRAVERSED • 28ms</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="stepper-card stepper-card-inactive">
                    <div class="stepper-num">STEP 2 • PROPERTY GRAPH</div>
                    <div class="stepper-title">🕸️ Graph Linkage</div>
                    <div style="font-size:0.80rem; color:#5F6368; line-height:1.45; margin-bottom:8px;">Traverses 4 hops in BigQuery.</div>
                    <span class="stepper-tag stepper-tag-inactive">⚪ QUEUED</span>
                </div>
                """, unsafe_allow_html=True)

        with s3:
            if is_done:
                st.markdown("""
                <div class="stepper-card stepper-card-active">
                    <div class="stepper-num">STEP 3 • NETWORK HOLD</div>
                    <div class="stepper-title">🔒 Policy Containment</div>
                    <div style="font-size:0.80rem; color:#3C4043; line-height:1.45; margin-bottom:8px;">Placed temporary hold on PAN & revoked token.</div>
                    <span class="stepper-tag">🟢 FROZEN • 45ms</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="stepper-card stepper-card-inactive">
                    <div class="stepper-num">STEP 3 • NETWORK HOLD</div>
                    <div class="stepper-title">🔒 Policy Containment</div>
                    <div style="font-size:0.80rem; color:#5F6368; line-height:1.45; margin-bottom:8px;">Zero-loss card network hold.</div>
                    <span class="stepper-tag stepper-tag-inactive">⚪ QUEUED</span>
                </div>
                """, unsafe_allow_html=True)

        with s4:
            if is_done:
                st.markdown("""
                <div class="stepper-card stepper-card-active">
                    <div class="stepper-num">STEP 4 • SMS DISPATCH</div>
                    <div class="stepper-title">📱 2-Way Notification</div>
                    <div style="font-size:0.80rem; color:#3C4043; line-height:1.45; margin-bottom:8px;">Dispatched verification SMS via Pub/Sub & Twilio.</div>
                    <span class="stepper-tag">🟢 DELIVERED • 120ms</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="stepper-card stepper-card-inactive">
                    <div class="stepper-num">STEP 4 • SMS DISPATCH</div>
                    <div class="stepper-title">📱 2-Way Notification</div>
                    <div style="font-size:0.80rem; color:#5F6368; line-height:1.45; margin-bottom:8px;">2-Way cardholder confirmation.</div>
                    <span class="stepper-tag stepper-tag-inactive">⚪ QUEUED</span>
                </div>
                """, unsafe_allow_html=True)

        st.write("")

        # Master-Detail Investigation Cockpit (2-Column Grid)
        c_cockpit_l, c_cockpit_r = st.columns([1.25, 0.95], gap="large")

        # LEFT COLUMN: CHRONICLE-STYLE THREAT DOSSIER
        with c_cockpit_l:
            with st.container(border=True):
                st.markdown("##### 📋 **Correlated Threat Evidence Matrix (Chronicle SecOps)**")
                
                if not is_done:
                    st.markdown("""
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#FCE8E6; border:1px solid #FAD2CF; padding:10px 14px; border-radius:6px; margin-bottom:14px;">
                        <div>
                            <div style="color:#C5221F; font-weight:800; font-size:0.92rem;">🚨 UNMITIGATED THREAT: SYNDICATE BUST-OUT</div>
                            <div style="font-size:0.78rem; color:#5F6368;">High-risk anomaly awaiting autonomous containment</div>
                        </div>
                        <span style="background:#EA4335; color:#FFFFFF !important; font-weight:800; font-size:0.75rem; padding:4px 8px; border-radius:4px;">99.8% RISK</span>
                    </div>

                    <table style="width:100%; border-collapse:collapse; font-size:0.86rem; line-height:1.7;">
                        <tr style="border-bottom:1px solid #F1F3F4;">
                            <td style="width:32%; color:#5F6368; font-weight:700; padding:8px 0;">Hardware Signature</td>
                            <td style="color:#202124;"><code>dev_fp_ring_99</code> <span style="background:#FCE8E6; color:#C5221F; font-size:0.75rem; font-weight:700; padding:2px 6px; border-radius:4px; margin-left:4px;">Rooted Emulator</span></td>
                        </tr>
                        <tr style="border-bottom:1px solid #F1F3F4;">
                            <td style="width:32%; color:#5F6368; font-weight:700; padding:8px 0;">Pending Charge</td>
                            <td style="color:#C5221F; font-weight:800;">$2,499.00 at Best Buy Electronics</td>
                        </tr>
                        <tr style="border-bottom:1px solid #F1F3F4;">
                            <td style="width:32%; color:#5F6368; font-weight:700; padding:8px 0;">Blast Radius</td>
                            <td style="color:#202124;"><b>3 Accounts Vulnerable:</b> <code>acc_legit_100</code>, <code>acc_legit_101</code>, <code>acc_legit_102</code></td>
                        </tr>
                        <tr>
                            <td style="color:#5F6368; font-weight:700; padding:8px 0;">Remediation Status</td>
                            <td style="color:#C5221F; font-weight:700;">🔴 Awaiting Trigger ➔ Click 'Trigger Live Triage' above</td>
                        </tr>
                    </table>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#E6F4EA; border:1px solid #CEEAD6; padding:10px 14px; border-radius:6px; margin-bottom:14px;">
                        <div>
                            <div style="color:#137333; font-weight:800; font-size:0.92rem;">✅ THREAT NEUTRALIZED & CONTAINED</div>
                            <div style="font-size:0.78rem; color:#5F6368;">Correlated across Stream, Graph, and Identity vectors</div>
                        </div>
                        <span style="background:#137333; color:#FFFFFF !important; font-weight:800; font-size:0.75rem; padding:4px 8px; border-radius:4px;">100% CONTAINED</span>
                    </div>

                    <table style="width:100%; border-collapse:collapse; font-size:0.86rem; line-height:1.7;">
                        <tr style="border-bottom:1px solid #F1F3F4;">
                            <td style="width:32%; color:#5F6368; font-weight:700; padding:8px 0;">Hardware Signature</td>
                            <td style="color:#202124;"><code>dev_fp_ring_99</code> <span style="background:#FCE8E6; color:#C5221F; font-size:0.75rem; font-weight:700; padding:2px 6px; border-radius:4px; margin-left:4px;">Rooted Emulator (Blacklisted)</span></td>
                        </tr>
                        <tr style="border-bottom:1px solid #F1F3F4;">
                            <td style="width:32%; color:#5F6368; font-weight:700; padding:8px 0;">Freight Drop Origin</td>
                            <td style="color:#202124;"><code>104 Industrial Pkwy Ste B, Wilmington DE</code></td>
                        </tr>
                        <tr style="border-bottom:1px solid #F1F3F4;">
                            <td style="width:32%; color:#5F6368; font-weight:700; padding:8px 0;">Blast Radius</td>
                            <td style="color:#202124;"><b>3 Accounts Protected:</b> <code>acc_legit_100</code>, <code>acc_legit_101</code>, <code>acc_legit_102</code></td>
                        </tr>
                        <tr style="border-bottom:1px solid #F1F3F4;">
                            <td style="width:32%; color:#5F6368; font-weight:700; padding:8px 0;">Network Action</td>
                            <td style="color:#137333; font-weight:700;">✅ Auth Hold Enacted • Virtual Replacement Card Issued</td>
                        </tr>
                        <tr>
                            <td style="color:#5F6368; font-weight:700; padding:8px 0;">Mitigation SLA</td>
                            <td style="color:#1A73E8; font-weight:800;">⚡ 1.42s Autonomous Containment</td>
                        </tr>
                    </table>
                    """, unsafe_allow_html=True)

        # RIGHT COLUMN: INTERACTIVE 2-WAY SMARTPHONE SMS SIMULATION
        with c_cockpit_r:
            st.markdown("""
            <div class="phone-mockup-frame">
                <div class="phone-top-bar">
                    <span style="font-weight:700; color:#5F6368;">9:41 AM</span>
                    <span style="font-weight:700; color:#5F6368;">📶 5G • 100% 🔋</span>
                </div>
                <div class="phone-sender-header">
                    <span style="font-size:1.2rem;">🛡️</span>
                    <div>
                        <div style="font-size:0.90rem; font-weight:800; color:#1A73E8;">Bank Fraud Defense</div>
                        <div style="font-size:0.70rem; color:#5F6368; font-weight:600;">Verified SMS Shortcode: 44102</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if not is_done:
                st.markdown("""
                <div style="text-align:center; padding:55px 12px; color:#5F6368;">
                    <div style="font-size:3.5rem; margin-bottom:8px;">📱</div>
                    <b style="color:#202124;">Cardholder Device (Sarah C.)</b>
                    <div style="font-size:0.82rem; margin-top:4px;">No active alerts. Waiting for autonomous triage trigger...</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="chat-bubble-incoming">
                    <b>Bank Security Alert:</b> Did you attempt a <b>$2,499.00</b> charge at <i>Best Buy Electronics</i>? We temporarily held your card to protect you.<br><br>
                    Reply <b>1</b> for YES or <b>2</b> for NO.
                </div>
                """, unsafe_allow_html=True)

                if st.session_state['sms_reply_state'] == 'legit':
                    st.markdown("""
                    <div class="chat-bubble-outgoing">
                        <b>1</b> (Yes, this was me)
                    </div>
                    <div class="chat-bubble-incoming" style="background:#E6F4EA !important; border-color:#CEEAD6 !important; color:#137333 !important;">
                        <b>✅ Transaction Confirmed:</b> Temporary hold released. Thank you for securing your account!
                    </div>
                    """, unsafe_allow_html=True)
                elif st.session_state['sms_reply_state'] == 'fraud':
                    st.markdown("""
                    <div class="chat-bubble-outgoing" style="background:#EA4335 !important;">
                        <b>2</b> (No, unauthorized!)
                    </div>
                    <div class="chat-bubble-incoming" style="background:#FCE8E6 !important; border-color:#FAD2CF !important; color:#C5221F !important;">
                        <b>🚨 Card Permanently Blocked:</b> Transaction rejected ($0 loss). A new contactless card has been expedited to your address.
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if is_done:
                st.write("")
                st.caption("Simulate Cardholder Response:")
                btn_sms_l, btn_sms_r = st.columns(2)
                with btn_sms_l:
                    if st.button("🟢  Reply 1 (Verify)", use_container_width=True, key="sms_yes"):
                        st.session_state['sms_reply_state'] = 'legit'
                        st.rerun()
                with btn_sms_r:
                    if st.button("🚨  Reply 2 (Block)", use_container_width=True, key="sms_no"):
                        st.session_state['sms_reply_state'] = 'fraud'
                        st.rerun()

    # --------------------------------------------------------------------------
    # TAB 4: MULTIMODAL KYC & DEEPFAKE FORENSICS (CLEAN MASTER-DETAIL LAYOUT)
    # --------------------------------------------------------------------------
    with tab4:
        st.subheader("Multimodal KYC Forensics: AI Deepfake & Document Tampering")
        st.caption("Vertex AI Gemini 5-Point Biometric Forensics: Inspecting identity documents for AI-generated synthetic portraits (StyleGAN/Diffusion) and font tampering.")
        st.write("")

        # 2-Column Master-Detail Layout
        col_master, col_detail = st.columns([3.6, 8.4], gap="large")

        # LEFT MASTER COLUMN: COMPACT SUBMISSIONS LIST
        with col_master:
            st.markdown("##### 📁 **Incoming KYC Queue**")
            
            p_sel = st.session_state['kyc_persona']
            
            # Persona 1: Marcus
            c1 = st.container(border=True)
            with c1:
                k1_active = p_sel == 'marcus'
                st.markdown(f"**🎭 Marcus Vance** {'🔹 *(Selected)*' if k1_active else ''}  \n`TX-883910-09` • <span class='badge-fraud'>AI DEEPFAKE</span>", unsafe_allow_html=True)
                if st.button("Inspect Marcus Vance", type="primary" if k1_active else "secondary", use_container_width=True, key="btn_k1"):
                    st.session_state['kyc_persona'] = 'marcus'
                    st.rerun()

            # Persona 2: Jordan
            c2 = st.container(border=True)
            with c2:
                k2_active = p_sel == 'jordan'
                st.markdown(f"**🚨 Jordan Vance** {'🔹 *(Selected)*' if k2_active else ''}  \n`DL-948201-DE` • <span class='badge-fraud'>FONT SPLICED</span>", unsafe_allow_html=True)
                if st.button("Inspect Jordan Vance", type="primary" if k2_active else "secondary", use_container_width=True, key="btn_k2"):
                    st.session_state['kyc_persona'] = 'jordan'
                    st.rerun()

            # Persona 3: Taylor
            c3 = st.container(border=True)
            with c3:
                k3_active = p_sel == 'taylor'
                st.markdown(f"**🚨 Taylor Reed** {'🔹 *(Selected)*' if k3_active else ''}  \n`UB-449102` • <span class='badge-fraud'>ALTERED BILL</span>", unsafe_allow_html=True)
                if st.button("Inspect Taylor Reed", type="primary" if k3_active else "secondary", use_container_width=True, key="btn_k3"):
                    st.session_state['kyc_persona'] = 'taylor'
                    st.rerun()

            # Persona 4: Sarah
            c4 = st.container(border=True)
            with c4:
                k4_active = p_sel == 'sarah'
                st.markdown(f"**🟢 Sarah Jenkins** {'🔹 *(Selected)*' if k4_active else ''}  \n`CA-551928-01` • <span class='badge-clean'>REAL ID CLEAN</span>", unsafe_allow_html=True)
                if st.button("Inspect Sarah Jenkins", type="primary" if k4_active else "secondary", use_container_width=True, key="btn_k4"):
                    st.session_state['kyc_persona'] = 'sarah'
                    st.rerun()

        # RIGHT DETAIL COLUMN: UNIFIED DOCUMENT + FORENSIC DOSSIER
        with col_detail:
            st.markdown("##### 🔬 **Forensic Inspection & Biometric HUD Dossier**")
            
            p = st.session_state['kyc_persona']
            
            d_l, d_r = st.columns([1.05, 1.15], gap="medium")

            with d_l:
                if p == 'marcus':
                    st.markdown("""
                    <div class="dl-card-frame">
                        <div class="dl-header dl-header-fake">
                            <div>🏛️ STATE OF TEXAS — DL</div>
                            <div style="font-size:0.70rem; background:rgba(255,255,255,0.25); padding:1px 6px; border-radius:3px;">USA</div>
                        </div>
                        <div class="dl-body">
                            <div class="dl-portrait-box dl-portrait-fake">
                                <div style="font-size:3.0rem;">👨‍💼</div>
                                <div class="scan-hud-tag">🚨 FAKE FACE</div>
                            </div>
                            <div class="dl-info-fields">
                                <div class="dl-field-label">DL No</div>
                                <div class="dl-field-val">TX-883910-09</div>
                                <div class="dl-field-label">Name</div>
                                <div class="dl-field-val">MARCUS VANCE</div>
                                <div class="dl-field-label">Address</div>
                                <div class="dl-field-val"><span class="dl-tamper-highlight">104 Industrial Pkwy</span></div>
                                <div style="font-size:0.75rem; color:#5F6368;">DOB: 1991-04-18 • EXP: 2029</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif p == 'jordan':
                    st.markdown("""
                    <div class="dl-card-frame">
                        <div class="dl-header dl-header-fake">
                            <div>🏛️ STATE OF DELAWARE — DL</div>
                            <div style="font-size:0.70rem; background:rgba(255,255,255,0.25); padding:1px 6px; border-radius:3px;">USA</div>
                        </div>
                        <div class="dl-body">
                            <div class="dl-portrait-box dl-portrait-fake">
                                <div style="font-size:3.0rem;">🧔</div>
                                <div class="scan-hud-tag">⚠️ SPLICED</div>
                            </div>
                            <div class="dl-info-fields">
                                <div class="dl-field-label">DL No</div>
                                <div class="dl-field-val"><span class="dl-tamper-highlight">DL-948201-DE</span></div>
                                <div class="dl-field-label">Name</div>
                                <div class="dl-field-val">JORDAN VANCE</div>
                                <div class="dl-field-label">Address</div>
                                <div class="dl-field-val"><span class="dl-tamper-highlight">104 Industrial Pkwy</span></div>
                                <div style="font-size:0.75rem; color:#5F6368;">DOB: 1989-11-04 • EXP: 2028</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif p == 'taylor':
                    st.markdown("""
                    <div class="dl-card-frame">
                        <div class="dl-header dl-header-fake">
                            <div>⚡ DELMARVA POWER BILL</div>
                            <div style="font-size:0.70rem; background:rgba(255,255,255,0.25); padding:1px 6px; border-radius:3px;">PDF</div>
                        </div>
                        <div class="dl-body">
                            <div class="dl-portrait-box dl-portrait-fake">
                                <div style="font-size:3.0rem;">📑</div>
                                <div class="scan-hud-tag">⚠️ OVERWRITE</div>
                            </div>
                            <div class="dl-info-fields">
                                <div class="dl-field-label">Account No</div>
                                <div class="dl-field-val">UB-449102-DEL</div>
                                <div class="dl-field-label">Customer</div>
                                <div class="dl-field-val">TAYLOR REED</div>
                                <div class="dl-field-label">Address</div>
                                <div class="dl-field-val"><span class="dl-tamper-highlight">104 Industrial Pkwy</span></div>
                                <div style="font-size:0.75rem; color:#C5221F; font-weight:700;">Vector Overwrite Flag</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="dl-card-frame">
                        <div class="dl-header">
                            <div>🏛️ CALIFORNIA REAL ID</div>
                            <div style="font-size:0.75rem; color:#FBBC04 !important; font-weight:800;">⭐ REAL ID</div>
                        </div>
                        <div class="dl-body">
                            <div class="dl-portrait-box dl-portrait-clean">
                                <div style="font-size:3.0rem;">👩‍💼</div>
                                <div class="scan-hud-tag scan-hud-tag-clean">🟢 CLEAN</div>
                            </div>
                            <div class="dl-info-fields">
                                <div class="dl-field-label">DL No</div>
                                <div class="dl-field-val">CA-551928-01</div>
                                <div class="dl-field-label">Name</div>
                                <div class="dl-field-val">SARAH JENKINS</div>
                                <div class="dl-field-label">Address</div>
                                <div class="dl-field-val"><span class="dl-clean-highlight">742 Evergreen Terr</span></div>
                                <div style="font-size:0.75rem; color:#137333; font-weight:700;">Hologram Authenticated</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with d_r:
                if st.button("🔍  Run Live Biometric Scan", type="primary", use_container_width=True):
                    s_t = time.time()
                    with st.spinner("Analyzing biometric markers..."):
                        time.sleep(0.5)
                        is_tamp = p != 'sarah'
                        name = "MARCUS VANCE" if p == 'marcus' else ("JORDAN VANCE" if p == 'jordan' else ("TAYLOR REED" if p == 'taylor' else "SARAH JENKINS"))
                        addr = "104 Industrial Pkwy Ste B, Wilmington DE" if is_tamp else "742 Evergreen Terr, Sunnyvale CA"
                        conf = 0.992 if p == 'marcus' else (0.984 if is_tamp else 0.997)
                        dec = "REJECT_DEEPFAKE_PORTRAIT" if p == 'marcus' else ("REJECT_FORGED_ID" if is_tamp else "APPROVE")
                        g_link = "Direct Link to Alex Mercer via dev_fp_ring_99" if is_tamp else "No adverse graph links."
                        if client:
                            try:
                                client.query(f"INSERT INTO `{PROJECT_ID}.fraud_engine.kyc_audit_log` (document_uri, applicant_name, extracted_address, is_tampered, confidence_score, forensic_analysis, graph_syndicate_link, decision, scanned_at) VALUES ('{p}_doc', '{name}', '{addr}', {is_tamp}, {conf}, 'Scan complete', '{g_link}', '{dec}', CURRENT_TIMESTAMP());").result()
                            except Exception: pass
                    st.toast("✅ Biometric Scan Verified!", icon="🔬")

                if p == 'marcus':
                    st.markdown("""
                    <div style="background:#FFFFFF; border:1px solid #E8EAED; border-left:4px solid #EA4335; border-radius:8px; padding:12px; margin-top:8px;">
                        <b style="color:#C5221F; font-size:0.92rem;">🎭 AI DEEPFAKE DETECTED (99.2%)</b>
                        <div style="font-size:0.80rem; line-height:1.5; color:#3C4043; margin-top:4px;">
                        • <b>Pupil Reflection:</b> <span style="color:#C5221F; font-weight:700;">FAILED</span> (Asymmetrical light vectors)<br>
                        • <b>Earlobe Seam:</b> <span style="color:#C5221F; font-weight:700;">FAILED</span> (Diffusion blending seam)<br>
                        • <b>Spectral Noise:</b> <span style="color:#C5221F; font-weight:700;">FAILED</span> (GAN frequency artifact)<br>
                        • <b>Graph Link:</b> Matches Alex Mercer syndicate drop
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif p == 'jordan' or p == 'taylor':
                    st.markdown("""
                    <div style="background:#FFFFFF; border:1px solid #E8EAED; border-left:4px solid #EA4335; border-radius:8px; padding:12px; margin-top:8px;">
                        <b style="color:#C5221F; font-size:0.92rem;">🚨 DOCUMENT FORGERY (98.4%)</b>
                        <div style="font-size:0.80rem; line-height:1.5; color:#3C4043; margin-top:4px;">
                        • <b>Font Splicing:</b> <span style="color:#C5221F; font-weight:700;">FAILED</span> (Kerning gap & spliced text)<br>
                        • <b>Hologram Foil:</b> <span style="color:#C5221F; font-weight:700;">FAILED</span> (Non-diffractive overlay)<br>
                        • <b>Graph Link:</b> Linked to <code>dev_fp_ring_99</code> emulator
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background:#FFFFFF; border:1px solid #E8EAED; border-left:4px solid #34A853; border-radius:8px; padding:12px; margin-top:8px;">
                        <b style="color:#137333; font-size:0.92rem;">✅ AUTHENTICATED & APPROVED (99.7%)</b>
                        <div style="font-size:0.80rem; line-height:1.5; color:#3C4043; margin-top:4px;">
                        • <b>Pupil Reflection:</b> <span style="color:#137333; font-weight:700;">PASSED</span> (Natural optical refraction)<br>
                        • <b>Facial Boundary:</b> <span style="color:#137333; font-weight:700;">PASSED</span> (Organic natural edge)<br>
                        • <b>Hologram Star:</b> <span style="color:#137333; font-weight:700;">PASSED</span> (Diffraction verified)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.write("")
        st.divider()
        
        # FULL-WIDTH CLEAN AUDIT LOG DRAWER
        with st.expander("📋 View Live BigQuery KYC Forensic Audit Trail (fraud_engine.kyc_audit_log)", expanded=False):
            a_rows = []
            if client:
                try:
                    a_rows = list(client.query(f"SELECT applicant_name, extracted_address, is_tampered, confidence_score, decision, graph_syndicate_link FROM `{PROJECT_ID}.fraud_engine.kyc_audit_log` ORDER BY scanned_at DESC LIMIT 5").result())
                except Exception: pass
            if not a_rows:
                a_rows = [
                    type('Row', (), {"applicant_name": "MARCUS VANCE", "extracted_address": "104 Industrial Pkwy Ste B, Wilmington DE", "is_tampered": True, "confidence_score": 0.992, "decision": "REJECT_DEEPFAKE_PORTRAIT", "graph_syndicate_link": "Direct Link to Alex Mercer via dev_fp_ring_99"}),
                    type('Row', (), {"applicant_name": "JORDAN VANCE", "extracted_address": "104 Industrial Pkwy Ste B, Wilmington DE", "is_tampered": True, "confidence_score": 0.984, "decision": "REJECT_FORGED_ID", "graph_syndicate_link": "Direct Link to Alex Mercer via dev_fp_ring_99"}),
                    type('Row', (), {"applicant_name": "SARAH JENKINS", "extracted_address": "742 Evergreen Terr, Sunnyvale CA", "is_tampered": False, "confidence_score": 0.997, "decision": "APPROVE", "graph_syndicate_link": "Clean history"})
                ]

            a_tbl = '<table class="stream-table"><tr><th>Applicant</th><th>Extracted Address</th><th>Tampered</th><th>Confidence</th><th>Verdict</th><th>Graph Syndicate Correlation</th></tr>'
            for r in a_rows:
                badge = '<span class="badge-fraud">🚨 REJECT</span>' if 'REJECT' in r.decision else '<span class="badge-clean">🟢 APPROVE</span>'
                a_tbl += f'<tr><td><b>{r.applicant_name}</b></td><td><code>{r.extracted_address}</code></td><td>{"⚠️ True" if r.is_tampered else "False"}</td><td>{r.confidence_score*100:.1f}%</td><td>{badge}</td><td>{r.graph_syndicate_link}</td></tr>'
            a_tbl += '</table>'
            st.markdown(a_tbl, unsafe_allow_html=True)
