from google.cloud import bigquery
client = bigquery.Client(project="admin-demo-test1")
insert_sql = """INSERT INTO `admin-demo-test1.fraud_engine.live_transactions_stream` VALUES
('txn_live_901', 'acc_syndicate_02', 1850.00, 'electronics_online', 'dev_fp_ring_99', '198.51.100.24', '104 Industrial Pkwy Ste B', CURRENT_TIMESTAMP());"""
client.query(insert_sql).result()
print("Live transaction streamed successfully!")
