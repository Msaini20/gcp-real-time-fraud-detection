import sys
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

bucket_name = sys.argv[1]
spark = SparkSession.builder \
    .appName("DeltaToIcebergConversion") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.iceberg_catalog.type", "hadoop") \
    .config("spark.sql.catalog.iceberg_catalog.warehouse", f"gs://{bucket_name}/iceberg_warehouse") \
    .getOrCreate()

schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("account_id", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("merchant_category", StringType(), True),
    StructField("device_id", StringType(), True),
    StructField("timestamp", StringType(), True),
])

data = [
    ("hist_001", "acc_syndicate_01", 120.50, "groceries", "dev_fp_ring_99", "2024-01-15 10:20:00"),
    ("hist_002", "acc_syndicate_01", 450.00, "electronics", "dev_fp_ring_99", "2024-03-22 14:10:00"),
    ("hist_003", "acc_syndicate_02", 980.00, "luxury_retail", "dev_fp_ring_99", "2024-06-11 18:30:00"),
    ("hist_004", "acc_legit_100", 35.00, "gas_station", "dev_fp_clean_01", "2025-02-01 08:45:00"),
    ("hist_005", "acc_syndicate_03", 2200.00, "crypto_exchange", "dev_fp_ring_99", "2025-07-19 22:15:00")
]

df = spark.createDataFrame(data, schema)
df.writeTo("iceberg_catalog.fraud_lakehouse.historical_transactions").tableProperty("write.format.default", "parquet").createOrReplace()
spark.stop()
