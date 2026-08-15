CREATE OR REPLACE MODEL `admin-demo-test1.fraud_engine.fraud_classifier`
OPTIONS (model_type = 'BOOSTED_TREE_CLASSIFIER', input_label_cols = ['is_fraud']) AS
SELECT amount, IF(device_id LIKE '%emulator%' OR device_id LIKE '%ring%', 1, 0) AS is_emulator,
  IF(merchant_category = 'high_risk_electronics', 1, 0) AS is_high_risk,
  CASE WHEN account_id LIKE '%syndicate%' THEN 1 ELSE 0 END AS is_fraud
FROM `admin-demo-test1.fraud_engine.historical_iceberg_transactions`;

CREATE OR REPLACE TABLE `admin-demo-test1.fraud_engine.live_transactions_stream` (
  transaction_id STRING, account_id STRING, amount FLOAT64, merchant_category STRING,
  device_id STRING, ip_address STRING, shipping_address STRING, timestamp TIMESTAMP
) OPTIONS (enable_change_history = TRUE);

CREATE OR REPLACE TABLE `admin-demo-test1.fraud_engine.live_transactions_scored` (
  transaction_id STRING, account_id STRING, amount FLOAT64, merchant_category STRING,
  device_id STRING, is_suspicious_device BOOLEAN, is_high_risk_amount BOOLEAN, processed_at TIMESTAMP
);
