# Big Data Project Setup and Execution

## Prerequisites

- Docker installed
- Docker containers for Spark, Kafka, and Cassandra running

## Copying Files to Docker Containers

### For Spark

```sh
docker cp sparkstream.py projetbigdata-spark-master-1:/opt/bitnami/spark/sparkstream.py  
docker cp GBT_Model12 projetbigdata-spark-master-1:/opt/bitnami/spark/GBT_Model12
