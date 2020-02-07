#!/bin/bash
source configs/environment

MASTER_IP=$1
MASTER_PRIV=$2
MEMORY=$3
BENCHMARK=$4
PARTITIONS=$5
SCALE=$6

rm ~/.ssh/known_hosts

ssh -t -i $KEYPATH ubuntu@$MASTER_IP "
  sed -i \"s/hibench.spark.master.*/hibench.spark.master   spark:\/\/$MASTER_PRIV:7077/g\" ~/HiBench/conf/spark.conf
  sed -i \"s/hibench.scale.profile.*/hibench.scale.profile    $SCALE/g\" ~/HiBench/conf/hibench.conf
  sed -i \"s/hibench.default.map.parallelism.*/hibench.default.map.parallelism    $PARTITIONS/g\" ~/HiBench/conf/hibench.conf
  sed -i \"s/hibench.default.shuffle.parallelism.*/hibench.default.shuffle.parallelism    $PARTITIONS/g\" ~/HiBench/conf/hibench.conf
  sed -i \"s/spark.executor.memory.*/spark.executor.memory    $MEMORY/g\" ~/HiBench/conf/spark.conf
  sed -i \"s/spark.driver.memory.*/spark.driver.memory    14G/g\" ~/HiBench/conf/spark.conf
"

ssh -t -i $KEYPATH ubuntu@$MASTER_IP "/usr/bin/time -f \"%e\" ~/HiBench/bin/workloads/$BENCHMARK/prepare/prepare.sh" > prep.log