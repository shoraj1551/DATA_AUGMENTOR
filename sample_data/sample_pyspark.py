from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg

# Initialize Spark
spark = SparkSession.builder.appName("SalesAnalysis").getOrCreate()

# Read data
df = spark.read.csv("sales_data.csv", header=True, inferSchema=True)

# Collect all data (potential performance issue)
all_data = df.collect()

# Process data
result = df.groupBy("category").agg(
    sum("amount").alias("total_sales"),
    avg("amount").alias("avg_sales")
)

# Show results
result.show()
