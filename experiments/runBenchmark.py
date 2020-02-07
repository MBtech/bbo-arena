import subprocess
import os
import sys 
from helpers import * 
from aws_helpers import *
import massedit
import boto3

currentDir = os.getcwd()
os.chdir('../../ansible-spark')

cmd = 'ansible-playbook -i inventory/ec2.py ds_platform.yaml --skip-tags yarn,ami'
cmd = cmd.split()
print(cmd)
subprocess.Popen(cmd).communicate()

cmd = './inventory/ec2.py --list'
cmd = cmd.split()
print(cmd)
subprocess.call(cmd, stdout=open('host_file', 'w'))

hosts = getHostInfo()

masterIP = hosts['masters'][0]['publicIP']
masterPrivateIP = hosts['masters'][0]['privateIP']
instanceType = hosts['workers'][0]['type']
availableMemory = memory[instanceType]
instanceSize = instanceType.split('.')[1]
# Twice as many partitions as cpus
scale = 'small'
benchmark = 'ml/svd'
region = 'us-east-2'

os.chdir(currentDir)

numNodes = [4, 3, 2, 1]
client = boto3.client('ec2', region_name=region)

for num in numNodes:
    index = 0
    while len(hosts['workers']) != num:
        client.terminate_instances(InstanceIds=[hosts['workers'][0]['id']])
        del hosts['workers'][0]

    url='http://'+masterIP+':8080/api/v1'
    while getNWorkers(url) != num:
        time.sleep(30)

    numPartitions = 2 * cpus[instanceSize] * len(hosts['workers'])
    cmd = './prepHibench.sh ' + masterIP + " " + masterPrivateIP + " " + str(availableMemory) + "G " + benchmark + " " + str(numPartitions) + " " + scale
    run_cmd(cmd)

    # os.chdir(currentDir)
    cmd = './runHibench.sh ' + masterIP + " " + benchmark + " " + benchmark.split('/')[1]
    run_cmd(cmd)


