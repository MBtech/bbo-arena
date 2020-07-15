#!/bin/bash
source configs/environment

MASTER_IP=$1
BENCHMARK=$2
b=$3
DIRECTORY=$4
MASTER_PRIV=$5
SCALE=$6
PARTITIONS=$7
MEMORY=$8

ssh -t -i $KEYPATH ubuntu@$MASTER_IP "
  sed -i \"s/hibench.spark.master.*/hibench.spark.master   spark:\/\/$MASTER_PRIV:7077/g\" ~/HiBench/conf/spark.conf
  sed -i \"s/hibench.scale.profile.*/hibench.scale.profile    $SCALE/g\" ~/HiBench/conf/hibench.conf
  sed -i \"s/hibench.default.map.parallelism.*/hibench.default.map.parallelism    $PARTITIONS/g\" ~/HiBench/conf/hibench.conf
  sed -i \"s/hibench.default.shuffle.parallelism.*/hibench.default.shuffle.parallelism    $PARTITIONS/g\" ~/HiBench/conf/hibench.conf
  sed -i \"s/spark.executor.memory.*/spark.executor.memory    $MEMORY/g\" ~/HiBench/conf/spark.conf
  sed -i \"s/spark.driver.memory.*/spark.driver.memory    14G/g\" ~/HiBench/conf/spark.conf
  sed -i \"s/hibench.hdfs.master.*/hibench.hdfs.master    s3a:\\/\\/bbo-dataset/g\" ~/HiBench/conf/hadoop.conf
"

echo "Starting up the benchmark"
# Start benchmark with spark

start=`date +%s`
ssh -t -i $KEYPATH ubuntu@$MASTER_IP "/usr/bin/time -f \"%e\" ~/HiBench/bin/workloads/$BENCHMARK/spark/run.sh" > $DIRECTORY/log
end=`date +%s`
wall_runtime=$((end-start))
echo $wall_runtime >> wall_runtime
 
scp -i $KEYPATH ubuntu@$MASTER_IP:/home/ubuntu/HiBench/report/${b}/spark/conf/../bench.log $DIRECTORY/bench.log

cat $DIRECTORY/log | grep "failed to run successfully"| wc -l | awk '{print $1}' > $DIRECTORY/error.log
cat $DIRECTORY/log | tail -1 | grep -E ^[+-]?[0-9]+\.?[0-9]*.*$ >> runtime

rm ~/.ssh/known_hosts