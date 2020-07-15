import subprocess
import os
import sys 
from helpers import * 
from aws_helpers import *
import massedit
import boto3
from mysar import sar 
import timeout_decorator
import math

def createReport(directoryName, scale, framework, benchmarkName, did_timeout=False):
    errors = open(directoryName+'error.log', 'r')
    runtime = 0
    if did_timeout:
        completed=False
        runtime = timeout
        walltime = timeout 
    elif int(errors.readlines()[0].strip('\n')) == 0:
        completed = True
        f = open(directoryName+'log')
        runtime = float(f.readlines()[-1].strip('\n'))
        walltime = runtime
    else:
        f = open(directoryName+'log')
        walltime = float(f.readlines()[-1].strip('\n'))
        runtime = -1
        completed = False

    data ={
    "completed": completed,
    "datasize": scale,
    "elapsed_time": runtime,
    "wall_time": walltime, 
    "framework": framework,
    "workload": benchmarkName
    }   

    json.dump(data, open(directoryName+'report.json', 'w'))

timeout = 3600
framework = 'spark'
scale = 'huge'
benchmark = 'ml/svd'
region = 'us-east-2'
instType = 'r5.xlarge'
start =40
end = 40
step = 1
numNodes = [x for x in range(start, end+step, step)]
numNodes.reverse()

instTypes = ['m5.large']

for instType in instTypes:
    editFiles(region, instType, numNodes[0], spotPrices[instType])

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

    os.chdir(currentDir)
    client = boto3.client('ec2', region_name=region)
    #  'ml/svd', 'ml/pca',
    benchmarks = ['ml/linear', 'ml/lda']

    for num in numNodes:

        index = 0
        while len(hosts['workers']) != num:
            client.terminate_instances(InstanceIds=[hosts['workers'][0]['id']])
            del hosts['workers'][0]

        print("Connecting to master node: " + masterIP)
        url='http://'+masterIP+':8080/api/v1'
        while getNWorkers(url) != num:
            time.sleep(30)

        for benchmark in benchmarks:
            benchmarkName = benchmark.split('/')[1]
            directoryName = 'dataset/'+ str(num) + "_" + instType + "_" + benchmarkName + "_" + framework + "_" + scale + "_1/"
            os.makedirs(directoryName, exist_ok=True)

            numPartitions = 2 * cpus[instanceSize] * len(hosts['workers'])
            # cmd = './prepHibench.sh ' + masterIP + " " + masterPrivateIP + " " + str(availableMemory) + "G " + benchmark \
            #                     + " " + str(numPartitions) + " " + scale + " " + directoryName
            # run_cmd(cmd)

            # os.chdir(currentDir)

        
            workerIPs = [host['publicIP'] for host in hosts['workers']]
            filenames = ['sar_node'+str(i)+'.csv' for i in range(1, len(hosts['workers'])+1)]
            sar('terminate', directoryName, workerIPs, filenames)
            sar('start', directoryName, workerIPs, filenames)
            # use timeout here is running on linux. gtimeout is for mac
            cmd = './runHibench.sh ' + masterIP + " " + benchmark + " " + benchmark.split('/')[1] + \
                            " " + directoryName + " " + masterPrivateIP + " " + scale + " " + str(numPartitions) + " " + \
                            str(availableMemory) + "G "

            f = timeout_decorator.timeout(timeout, timeout_exception=Exception)(run_cmd)
            timeout_flag = False
            try:
                f(cmd)
                timeout_flag = False
            except Exception:
                timeout_flag = True


            sar('terminate', directoryName, workerIPs, filenames)
            sar('export', directoryName, workerIPs, filenames)
            sar('collectcsv', directoryName, workerIPs, filenames)

            createReport(directoryName, scale, framework, benchmarkName, did_timeout=timeout_flag)
        # sys.exit()

    while len(hosts['workers']) != 0:
        client.terminate_instances(InstanceIds=[hosts['workers'][0]['id']])
        del hosts['workers'][0]
    client.terminate_instances(InstanceIds=[hosts['masters'][0]['id']])