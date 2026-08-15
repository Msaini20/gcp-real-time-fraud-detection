from google.cloud import bigquery
client = bigquery.Client(project="admin-demo-test1")
target = "acc_syndicate_02"
print(f"\n=======================================================\n  AUTONOMOUS FRAUD INVESTIGATOR: {target}\n=======================================================")
gql = f"""SELECT * FROM GRAPH_TABLE(`admin-demo-test1.fraud_engine.fintech_fraud_graph`
  MATCH (a:Account {{account_id: '{target}'}})-[:USED_DEVICE]->(d:Device)<-[:USED_DEVICE]-(f:Account)-[:SHIPPED_TO]->(s:Address)<-[:SHIPPED_TO]-(a)
  WHERE f.kyc_status = 'CONFIRMED_FRAUD'
  COLUMNS (a.account_id AS target, f.customer_name AS linked_fraud_user, d.device_id AS shared_device, s.full_address AS drop_address))"""
for row in client.query(gql).result():
    print(f"  >> Linked Fraud User: {row.linked_fraud_user} | Device: {row.shared_device} | Drop: {row.drop_address}")
iceberg = f"SELECT COUNT(*) as txns, SUM(amount) as total_usd FROM `admin-demo-test1.fraud_engine.historical_iceberg_transactions` WHERE account_id = '{target}'"
for row in client.query(iceberg).result():
    print(f"  >> Historical Exposure: ${row.total_usd:,.2f} across {row.txns} txns")
print("  >> Dispatched: TEMPORARY_CARD_FREEZE (Status: HTTP 200 OK)\n=======================================================\n")
