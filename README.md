# Big Data Project Setup and Execution

## Prerequisites

- Docker installed
- Docker containers for Spark, Kafka, and Cassandra running

## Copying Files to Docker Containers

### For Spark

\`\`\`sh
docker cp sparkstream.py projetbigdata-spark-master-1:/opt/bitnami/spark/sparkstream.py  

docker cp GBT_Model12 projetbigdata-spark-master-1:/opt/bitnami/spark/GBT_Model12
\`\`\`

### For Kafka

\`\`\`sh
docker cp csvread.py projetbigdata-kafka-1:/csvread.py
docker cp churn-bigml-20.csv projetbigdata-kafka-1:/churn-bigml-20.csv
\`\`\`

## Running the Applications

### Kafka

Open a terminal and execute:

\`\`\`sh
docker exec -it projetbigdata-kafka-1 /bin/bash
python3 csvread.py
\`\`\`

### Spark

Open another terminal and execute:

\`\`\`sh
docker exec -it projetbigdata-spark-master-1 /bin/bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 sparkstream.py
\`\`\`

### Cassandra

Open another terminal and execute:

\`\`\`sh
docker exec -it projetbigdata-cassandra-1 cqlsh
\`\`\`

In the Cassandra shell, run:

\`\`\`sql
USE spark_streams;
SELECT * FROM predictions;
\`\`\`


