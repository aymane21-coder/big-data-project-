import json
import time
import logging
from kafka import KafkaProducer
from pyspark.ml.feature import MinMaxScaler, StringIndexer, VectorAssembler
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType

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

# Create the SparkSession
spark = SparkSession.builder.getOrCreate()

def read_csv_stream():
    data = "churn-bigml-20.csv"
    df = spark.read.format('csv').option('header', True).schema(schema).load(data)
    df = df.withColumnRenamed("churn", "label")
    df = df.toDF(*(c.lower().replace(' ', '_') for c in df.columns))

    # Define transformers
    ohe = StringIndexer(inputCols=['state', 'international_plan', 'voice_mail_plan', 'label'],
                        outputCols=['state_ohe', 'international_plan_ohe', 'voice_mail_plan_ohe', 'label_churn'])

    inputs = ['account_length', 'area_code', 'number_vmail_messages', 'total_day_minutes', 'total_day_calls',
              'total_day_charge', 'total_eve_minutes', 'total_eve_calls', 'total_eve_charge', 'total_night_minutes',
              'total_night_calls', 'total_night_charge', 'total_intl_minutes', 'total_intl_calls', 'total_intl_charge',
              'customer_service_calls']

    assembler1 = VectorAssembler(inputCols=inputs, outputCol="features_scaled1")
    scaler = MinMaxScaler(inputCol="features_scaled1", outputCol="features_scaled")
    assembler2 = VectorAssembler(
        inputCols=['state_ohe', 'international_plan_ohe', 'voice_mail_plan_ohe', 'features_scaled'],
        outputCol="features")

    # Apply transformers
    df = ohe.fit(df).transform(df)
    df = assembler1.transform(df)
    df = scaler.fit(df).transform(df)
    df = assembler2.transform(df)



    producer = KafkaProducer(bootstrap_servers=['kafka:9093'], max_block_ms=5000, api_version=(2, 5, 0))

    while True:
        try:
            # Lire le fichier CSV

            # Émettre chaque ligne en tant qu'événement vers Kafka
            for row in df.collect():

                row_dict = {
                    "state": row.state,
                    "account_length": row.account_length,
                    "area_code": row.area_code,
                    "international_plan": row.international_plan,
                    "voice_mail_plan": row.voice_mail_plan,
                    "number_vmail_messages": row.number_vmail_messages,
                    "total_day_minutes": row.total_day_minutes,
                    "total_day_calls": row.total_day_calls,
                    "total_day_charge": row.total_day_charge,
                    "total_eve_minutes": row.total_eve_minutes,
                    "total_eve_calls": row.total_eve_calls,
                    "total_eve_charge": row.total_eve_charge,
                    "total_night_minutes": row.total_night_minutes,
                    "total_night_calls": row.total_night_calls,
                    "total_night_charge": row.total_night_charge,
                    "total_intl_minutes": row.total_intl_minutes,
                    "total_intl_calls": row.total_intl_calls,
                    "total_intl_charge": row.total_intl_charge,
                    "customer_service_calls": row.customer_service_calls,
                    "features": row.features.tolist(),
                    "label_churn": row.label_churn
                }
                json_data = json.dumps(row_dict)  # Convertir la ligne en format JSON

                print(json_data)
                producer.send('topics', json_data.encode('utf-8'))
                time.sleep(3)  # Ajouter un petit délai entre l'envoi de chaque ligne
        except Exception as e:
            logging.error(f'Une erreur s\'est produite: {e}')
            continue


read_csv_stream()