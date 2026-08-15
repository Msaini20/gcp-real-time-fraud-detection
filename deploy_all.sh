#!/usr/bin/env bash
# ==============================================================================
# Automated End-to-End Setup Script: Real-Time Fraud & Syndicate Ring Demo
# Target: Google Cloud (Argolis)
# ==============================================================================

set -e

export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1"
export BUCKET_NAME="${PROJECT_ID}-fraud-lakehouse"
export BQ_DATASET="fraud_engine"

echo "================================================================="
echo " Starting Full Deployment for Project: ${PROJECT_ID} (${REGION})"
echo "================================================================="

# 1. Enable APIs
echo "[1/6] Enabling Google Cloud APIs..."
gcloud services enable \
  bigquery.googleapis.com \
  bigqueryconnection.googleapis.com \
  dataproc.googleapis.com \
  pubsub.googleapis.com \
  storage.googleapis.com \
  compute.googleapis.com

# 2. Provision GCS, Pub/Sub, and Subnet
echo "[2/6] Provisioning Storage, Pub/Sub, and Network Resources..."
gcloud storage buckets create gs://${BUCKET_NAME} --location=${REGION} || true
gcloud pubsub topics create fraud-transactions-topic || true
gcloud compute networks create dataproc-vpc --subnet-mode=custom 2>/dev/null || true
gcloud compute networks subnets create dataproc-subnet \
    --network=dataproc-vpc --region=${REGION} --range=10.0.0.0/24 \
    --enable-private-ip-google-access 2>/dev/null || true
gcloud compute firewall-rules create allow-dataproc-internal \
    --network=dataproc-vpc --allow=tcp,udp,icmp --source-ranges=10.0.0.0/24 2>/dev/null || true

# 3. Create BigQuery Dataset & BigLake Connection
echo "[3/6] Setting up BigQuery Datasets & BigLake Connection..."
bq --location=${REGION} mk -d ${PROJECT_ID}:${BQ_DATASET} 2>/dev/null || true
bq mk --connection --location=${REGION} --project_id=${PROJECT_ID} \
    --connection_type=CLOUD_RESOURCE biglake_conn 2>/dev/null || true

BIGLAKE_SA=$(bq show --format=json --connection ${PROJECT_ID}.${REGION}.biglake_conn | jq -r '.cloudResource.serviceAccountId')
gcloud storage buckets add-iam-policy-binding gs://${BUCKET_NAME} \
    --member="serviceAccount:${BIGLAKE_SA}" \
    --role="roles/storage.objectViewer"

# 4. Submit Dataproc Serverless PySpark Iceberg ETL
echo "[4/6] Executing PySpark Iceberg ETL on Dataproc Serverless..."
gcloud storage cp 01_lakehouse_pyspark/spark_delta_to_iceberg.py gs://${BUCKET_NAME}/scripts/
COMPUTE_SA=$(gcloud compute project-info describe --format="value(commonInstanceMetadata.items[0].value)" 2>/dev/null || echo "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com")
gcloud dataproc batches submit pyspark gs://${BUCKET_NAME}/scripts/spark_delta_to_iceberg.py \
  --project=${PROJECT_ID} --region=${REGION} --subnet=dataproc-subnet \
  --deps-bucket=gs://${BUCKET_NAME} --version=2.2 \
  --properties="spark.jars.packages=org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0" \
  -- ${BUCKET_NAME}

# 5. Create BigQuery Tables, ML Models, and Property Graph
echo "[5/6] Registering BigLake Iceberg table, BQML Model, and Property Graph..."
bq query --use_legacy_sql=false < 02_bigquery_setup/01_lakehouse_biglake.sql
bq query --use_legacy_sql=false < 02_bigquery_setup/02_ml_and_continuous_queries.sql
bq query --use_legacy_sql=false < 02_bigquery_setup/03_graph_network_modeling.sql

# 6. Summary
echo "================================================================="
echo "  Deployment Complete! Run 'python3 03_agentic_ai/agent.py' to demo."
echo "================================================================="
