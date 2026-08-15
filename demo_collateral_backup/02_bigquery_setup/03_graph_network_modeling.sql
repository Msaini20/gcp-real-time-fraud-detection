CREATE OR REPLACE PROPERTY GRAPH `admin-demo-test1.fraud_engine.fintech_fraud_graph`
  NODE TABLES (
    `admin-demo-test1.fraud_engine.dim_accounts` KEY (account_id) LABEL Account PROPERTIES (account_id, customer_name, kyc_status),
    `admin-demo-test1.fraud_engine.dim_devices` KEY (device_id) LABEL Device PROPERTIES (device_id, device_type, is_emulator),
    `admin-demo-test1.fraud_engine.dim_addresses` KEY (address_id) LABEL Address PROPERTIES (address_id, full_address, is_commercial_drop)
  )
  EDGE TABLES (
    `admin-demo-test1.fraud_engine.rel_account_device` KEY (account_id, device_id)
      SOURCE KEY (account_id) REFERENCES `admin-demo-test1.fraud_engine.dim_accounts`(account_id)
      DESTINATION KEY (device_id) REFERENCES `admin-demo-test1.fraud_engine.dim_devices`(device_id) LABEL USED_DEVICE,
    `admin-demo-test1.fraud_engine.rel_account_address` KEY (account_id, address_id)
      SOURCE KEY (account_id) REFERENCES `admin-demo-test1.fraud_engine.dim_accounts`(account_id)
      DESTINATION KEY (address_id) REFERENCES `admin-demo-test1.fraud_engine.dim_addresses`(address_id) LABEL SHIPPED_TO
  );
