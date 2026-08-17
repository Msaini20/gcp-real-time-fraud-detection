# 🛡️ Google Cloud Autonomous Real-Time Fraud & Syndicate Ring Detection Platform

[![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![BigQuery](https://img.shields.io/badge/BigQuery-Continuous_Queries_%26_ISO_GQL_Graph-34A853?style=for-the-badge&logo=google-bigquery&logoColor=white)](https://cloud.google.com/bigquery)
[![Apache Iceberg](https://img.shields.io/badge/Lakehouse-Apache_Iceberg_%26_BigLake-0083B0?style=for-the-badge&logo=apache&logoColor=white)](https://iceberg.apache.org/)
[![Vertex AI](https://img.shields.io/badge/Vertex_AI-Gemini_Multimodal_Biometrics-FBBC04?style=for-the-badge&logo=google&logoColor=black)](https://cloud.google.com/vertex-ai)


---

## 📌 Executive Summary

Modern financial crime is no longer dominated by isolated stolen credit cards. Today, Tier-1 financial institutions face a **$30B+ multi-vector threat crisis** driven by coordinated synthetic identity syndicates, botnet card-testing attacks, account takeover (ATO) rings, and generative AI deepfake identity documents.

Traditional anti-fraud systems rely on fragmented point solutions, separate graph databases, rigid rules engines, and slow batch ETL pipelines that take 24–48 hours to discover anomalies.

This reference architecture implements an **Autonomous, Zero-Data-Movement Defense Perimeter** powered entirely by **Google Cloud’s unified Agentic Data Platform**:
1. **Sub-Second Stream Interception:** BigQuery Continuous Queries scoring live Point-of-Sale (POS) authorizations with real-time GIS Geo-velocity math and BIN attack filters.
2. **In-Warehouse Property Graph (ISO GQL):** Uncovering 4-hop syndicate rings, shared hardware emulators, and money mule chains with zero data movement.
3. **Open Lakehouse Modernization:** Dataproc Serverless (PySpark) transforming legacy Delta archives into open **Apache Iceberg** tables governed by **BigLake**.
4. **Multimodal Biometric KYC Forensics:** Vertex AI (Gemini 1.5/2.0) inspecting applicant identity documents with pixel-level 5-point biometric analysis (pupil reflection asymmetry, GAN substrate noise, hairline blending).
5. **Closed-Loop Agentic Containment:** Autonomous Gemini Agent synthesizing stream, graph, and KYC signals to execute automated risk containment in **< 2 seconds**.

---

## 🏛️ System Architecture

```
                                  [ EDGE TOUCHPOINTS ]
             POS Terminals • E-Commerce Checkouts • Mobile Devices • KYC Submissions
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. INGESTION & REAL-TIME STREAM INTERCEPTION                                           │
│    • Cloud Pub/Sub: High-throughput ingestion buffer                                   │
│    • BigQuery Continuous Queries: Real-time SQL stream scoring (< 500ms SLA)           │
│      - ST_DISTANCE Geo-Velocity Math: Flags NY -> London card swipes in < 15 mins      │
│      - Sliding-Window BIN Attack Defense: Blocks $0.99 micro-transaction botnets       │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. STORAGE & OPEN LAKEHOUSE LAYER                                                      │
│    • Cloud Storage (GCS): Raw Bronze & Silver archives                                 │
│    • Dataproc Serverless (PySpark): Batch Delta-to-Iceberg modernization               │
│    • BigLake Metastore: Open Apache Iceberg tables queried in place with zero ETL      │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. IN-WAREHOUSE PROPERTY GRAPH ENGINE (BigQuery Core)                                  │
│    • Native ISO GQL Graph: `admin-demo-test1.fraud_engine.fintech_fraud_graph`         │
│      - Nodes: `dim_accounts`, `dim_devices`, `dim_addresses`                           │
│      - Edges: `USED_DEVICE`, `AUTHENTICATED_FROM`, `SHIPPED_TO`                        │
│      - Multi-Hop Traversals: Exposes emulator hardware bridges & shared freight drops  │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. MULTIMODAL AI & AUTONOMOUS INVESTIGATOR AGENT                                       │
│    • Vertex AI (Gemini Multimodal via BigQuery ML Remote Endpoints):                   │
│      - 5-Point Biometric Forensics: Pupil reflections, GAN artifacts, font splicing    │
│    • Autonomous Gemini Fraud Agent: Corroborates stream + graph + KYC signals          │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. COMMAND CENTER & AUTOMATED REMEDIATION (< 2s Closed-Loop SLA)                       │
│    • Streamlit UI on Cloud Run / Cloud Shell: Operations Command Center                │
│    • Cloud Functions Webhooks: Freeze credit cards, revoke 2FA tokens, dispatch SMS    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Repository Structure

```
├── 01_lakehouse_pyspark/
│   └── spark_delta_to_iceberg.py       # Dataproc Serverless PySpark Delta-to-Iceberg modernization
├── 02_bigquery_setup/
│   ├── 01_lakehouse_biglake.sql         # BigLake Iceberg external tables & GCS object tables
│   ├── 02_ml_and_continuous_queries.sql # Sub-second BigQuery Continuous Queries stream scoring
│   ├── 03_graph_network_modeling.sql    # BigQuery Property Graph (ISO GQL) DDL & traversals
│   └── 04_multimodal_kyc_bigquery_ml.sql# Vertex AI Gemini remote model & KYC audit tables
├── 03_agentic_ai/
│   ├── agent.py                         # Autonomous Gemini Fraud Agent reasoning loop
│   └── kyc_multimodal_analyzer.py       # 5-point biometric KYC deepfake analyzer
├── 04_stream_simulation/
│   └── stream_simulator.py              # Point-of-Sale POS & auth event stream generator
├── 05_collaterals/
│   └── DEMO_EXECUTIVE_COVER_PAGE.md     # 1-page C-suite briefing overview
├── app.py                               # Operations Command Center (Streamlit Web App)
├── deploy_all.sh                        # Automated full-stack GCP deployment script
└── restore_and_run_v3_latest.sh         # One-click restore and launch script
```

---

## ⚡ Quickstart Deployment Guide

### Prerequisites
* Google Cloud Platform Project (e.g. `admin-demo-test1`)
* Google Cloud SDK (`gcloud`) initialized
* Cloud Shell or Linux VM environment
* Python 3.10+

### Option A: One-Click Launch (Recommended)
To immediately restore and run the latest Command Center on port 8080:

```bash
# 1. Clone repository or extract demo kit
git clone <repo_url> ~/fraud_detection_demo
cd ~/fraud_detection_demo

# 2. Run the one-click launch script
bash restore_and_run_v3_latest.sh
```

Open **Web Preview on port 8080** in Cloud Shell to access the Command Center.

---

### Option B: Full Infrastructure Deployment

To provision BigQuery datasets, BigLake Iceberg tables, Continuous Queries, Property Graph, and Vertex AI models from scratch:

```bash
# 1. Set your GCP Project
export PROJECT_ID="admin-demo-test1"
gcloud config set project $PROJECT_ID

# 2. Authenticate Application Default Credentials (ADC)
gcloud auth application-default login

# 3. Execute Automated Deployment
chmod +x deploy_all.sh
./deploy_all.sh
```

---

## 🎯 Live Operations Demo Guide

The Command Center provides two operational modes:

### 1. Executive Briefing Landing Page
* Summarizes the **Business Problem**, **Demo Objectives**, **Data Cloud Services Used**, and **Executive ROI**.
* Click **"Enter Live Demo Operations"** to enter the operational dashboard.

### 2. Operations Command Center (4 Core Tabs)

#### Tab 1: 🔴 Live Stream Interception
* Intercepts live point-of-sale authorizations in real time.
* Test sidebar stream injections:
  * 🟢 **Push Normal Stream:** Regular POS coffee & grocery transactions.
  * 🚨 **Push Syndicate Bust-Out:** Coordinated high-ticket electronics purchases.
  * ⚡ **Push BIN Attack:** Automated micro-transactions ($0.99) testing card numbers.
  * ✈️ **Push Impossible Travel:** NY $\rightarrow$ London card swipes within 5 minutes ($22,400\text{ km/h}$).
  * 🔑 **Push ATO Event:** Multi-account credential resets from a single emulator.

#### Tab 2: 🕸️ Property Graph & Multi-Hop Traversals
Click through interactive pattern buttons to inspect native ISO GQL queries:
1. **4-Hop Syndicate Ring:**
   ```sql
   SELECT * FROM GRAPH_TABLE(
     `admin-demo-test1.fraud_engine.fintech_fraud_graph`
     MATCH (suspicious:Account)-[e1:USED_DEVICE]->(d:Device)<-[e2:USED_DEVICE]-(fraud:Account)
           -[e3:SHIPPED_TO]->(addr:Address)<-[e4:SHIPPED_TO]-(suspicious)
     WHERE fraud.kyc_status = 'CONFIRMED_FRAUD' AND suspicious.account_id != fraud.account_id
     COLUMNS (suspicious.account_id, fraud.customer_name, d.device_id, addr.full_address)
   );
   ```
2. **Account Takeover (ATO) Fan-In:** Uncovers 1 emulator resetting passwords across 3 accounts in < 4 minutes.
3. **Layered Money Mule Dispersal:** Transitive path expressions (`*2..4`) tracking fan-out wire laundering.

#### Tab 3: 🤖 Autonomous Agent Triage
* Click **"Launch Autonomous Triage Loop"**.
* Gemini Agent investigates multi-vector signals, generates an executive threat dossier, freezes compromised cards, and revokes sessions in **< 2 seconds**.

#### Tab 4: 🎭 Multimodal KYC & Deepfake Forensics
* Select applicant identity documents:
  * 🎭 **Marcus Vance:** AI Deepfake Synthetic Portrait (StyleGAN/Diffusion with pupil reflection mismatch).
  * 🚨 **Jordan Vance:** Delaware Driver License with Helvetica font splicing.
  * 🚨 **Taylor Reed:** Altered utility bill with Photoshop address overwrite.
  * 🟢 **Sarah Jenkins:** Legitimate California REAL ID.
* Click **"Run Live KYC Forensic Inspection"** to execute 5-point biometric analysis and cross-check the property graph.

---

## 📈 Key Business Takeaways & ROI

| Capability | Legacy Approach | Google Cloud Agentic Solution | Business Impact |
| :--- | :--- | :--- | :--- |
| **Data Movement** | Multi-hop ETL across Kafka, Neo4j, and OCR | **Zero Data Movement** (All in BigQuery) | **40%+ TCO Reduction** |
| **Stream Scoring** | Batch hourly jobs | **Sub-second Continuous Queries** | Immediate POS decline |
| **Graph Analytics** | External specialized graph databases | **Native ISO GQL Property Graph** | Sub-35ms graph queries |
| **KYC Verification** | Human manual review (24–48 hours) | **Vertex AI Gemini Multimodal** | Instant deepfake catch |
| **Remediation SLA**| 48-hour reactive investigations | **< 2s Autonomous Containment** | Proactive loss prevention |

---

## 📄 License & Attribution
Licensed under the Apache License, Version 2.0. Developed for Google Cloud Financial Services Architecture demonstrations.
