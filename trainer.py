from pyspark.ml.feature import MinMaxScaler, StringIndexer, VectorAssembler
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType
from pyspark.ml.classification import RandomForestClassifier, LogisticRegression, LinearSVC
from pyspark.sql.functions import col,count

# Create the SparkSession
spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.debug.maxToStringFields", 100)

# Define the schema
# Define the schema
schema = StructType([
    StructField("state", StringType(), True),
    StructField("account length", LongType(), True),
    StructField("area code", LongType(), True),
    StructField("international plan", StringType(), True),
    StructField("voice mail plan", StringType(), True),
    StructField("number vmail messages", LongType(), True),
    StructField("total day minutes", DoubleType(), True),
    StructField("total day calls", LongType(), True),
    StructField("total day charge", DoubleType(), True),
    StructField("total eve minutes", DoubleType(), True),
    StructField("total eve calls", LongType(), True),
    StructField("total eve charge", DoubleType(), True),
    StructField("total night minutes", DoubleType(), True),
    StructField("total night calls", LongType(), True),
    StructField("total night charge", DoubleType(), True),
    StructField("total intl minutes", DoubleType(), True),
    StructField("total intl calls", LongType(), True),
    StructField("total intl charge", DoubleType(), True),
    StructField("customer service calls", DoubleType(), True),
    StructField("churn", StringType(), True)
])

# Load the data
data = "churn-bigml-80.csv"
df = spark.read.format('csv').option('header', True).schema(schema).load(data)
df = df.withColumnRenamed("churn", "label")

#traiter les valeurs manquantes
null_counts = df.select([col(c).isNull().cast('int').alias(c) for c in df.columns]) \
                .groupBy().sum().collect()[0]

# Affichage des comptes de valeurs nulles par colonne
for col_name, null_count in zip(df.columns, null_counts):
    print(col_name, null_count)

#supprimer les valeurs manquantes
df=df.dropna()


#traiter les valeurs dupliques
duplicate_count = df.groupBy(df.columns).count().where('count > 1')
duplicate_count.show()
#drop duplicates si il ya des valeusr dupliques
df = df.dropDuplicates()

df = df.toDF(*(c.lower().replace(' ', '_') for c in df.columns))


# Définir les transformateurs
train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)

# Define transformers
ohe = StringIndexer(inputCols=['state', 'international_plan', 'voice_mail_plan','label'],
                    outputCols=['state_ohe', 'international_plan_ohe', 'voice_mail_plan_ohe','label_churn'])

inputs = ['account_length', 'area_code', 'number_vmail_messages', 'total_day_minutes', 'total_day_calls', 'total_day_charge', 'total_eve_minutes', 'total_eve_calls', 'total_eve_charge', 'total_night_minutes', 'total_night_calls', 'total_night_charge', 'total_intl_minutes', 'total_intl_calls','total_intl_charge','customer_service_calls']

assembler1 = VectorAssembler(inputCols=inputs, outputCol="features_scaled1")
scaler = MinMaxScaler(inputCol="features_scaled1", outputCol="features_scaled")
assembler2 = VectorAssembler(inputCols=['state_ohe', 'international_plan_ohe', 'voice_mail_plan_ohe','features_scaled'],
                             outputCol="features")

# Apply transformers
train_data = ohe.fit(train_data).transform(train_data)
train_data = assembler1.transform(train_data)
train_data = scaler.fit(train_data).transform(train_data)
train_data = assembler2.transform(train_data)

test_data = ohe.fit(test_data).transform(test_data)
test_data = assembler1.transform(test_data)
test_data = scaler.fit(test_data).transform(test_data)
test_data = assembler2.transform(test_data)

# Select features and label
train_selected = train_data.select("features", "label_churn")
test_selected = test_data.select("features", "label_churn")
train_selected.show(truncate=False)
# Create the RandomForestClassifier
rf = RandomForestClassifier(featuresCol="features", labelCol="label_churn", maxBins=64)

# Fit the RandomForestClassifier
rf_model = rf.fit(train_selected)

# Make predictions on the test set
predictions = rf_model.transform(test_selected)
predictions.select('label_churn','prediction').show()

# Evaluate model performance
evaluator = MulticlassClassificationEvaluator(labelCol="label_churn", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)

print("Accuracy:", accuracy)



rf_model.save("random_forest_model",overwrite=True)