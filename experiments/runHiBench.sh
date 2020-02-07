#!/bin/bash
source configs/environment

MASTER_IP=$1
BENCHMARK=$2
b=$3


echo "Starting up the benchmark"
# Start benchmark with spark
start=`date +%s`
ssh -t -i $KEYPATH ubuntu@$MASTER_IP "/usr/bin/time -f \"%e\" ~/HiBench/bin/workloads/$BENCHMARK/spark/run.sh" > log
end=`date +%s`
wall_runtime=$((end-start))
echo $wall_runtime >> wall_runtime

scp -i $KEYPATH ubuntu@$MASTER_IP:/home/ubuntu/HiBench/report/${b}/spark/conf/../bench.log bench.log
j=$(echo $(ls bench_log/ | wc -l))

cp bench.log bench_log/bench-${j}.log

cat log | grep "failed to run successfully"| wc -l | awk '{print $1}' > error.log
cat log | tail -1 | grep -E ^[+-]?[0-9]+\.?[0-9]*.*$ >> runtime

echo "END OF EXPERIMENT\n"  >> log


rm ~/.ssh/known_hosts
