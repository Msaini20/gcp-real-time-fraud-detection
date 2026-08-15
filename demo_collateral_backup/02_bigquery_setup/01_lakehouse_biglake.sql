CREATE SCHEMA IF NOT EXISTS `admin-demo-test1.fraud_engine` OPTIONS (location = 'us-central1');

CREATE OR REPLACE EXTERNAL TABLE `admin-demo-test1.fraud_engine.historical_iceberg_transactions`
WITH CONNECTION `admin-demo-test1.us-central1.biglake_conn`
OPTIONS (
  format = 'ICEBERG',
  uris = ['gs://admin-demo-test1-fraud-lakehouse/iceberg_warehouse/fraud_lakehouse/historical_transactions/metadata/*.metadata.json']
);
