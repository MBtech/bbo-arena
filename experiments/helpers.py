import subprocess
import os
import time
import json
import paramiko
import sys
import math
from scp import SCPClient
import gevent
import re
import requests
import fileinput 

spotPrices = {
    'm5.large': 0.03,
    'm5.xlarge': 0.05,
    'm5.2xlarge': 0.1,
    'm5.4xlarge': 0.2,
    'm5a.large': 0.03,
    'm5a.xlarge': 0.05,
    'm5a.2xlarge': 0.1,
    'm5a.4xlarge': 0.2,
    'c5n.large': 0.03, # 3.9G in reality 
    'c5n.xlarge': 0.05,
    'c5n.2xlarge': 0.1,
    'c5n.4xlarge': 0.2,
    'c5.large': 0.03,
    'c5.xlarge': 0.05,
    'c5.2xlarge': 0.1,
    'c5.4xlarge': 0.2,
    'r5.large': 0.03,
    'r5.xlarge': 0.05,
    'r5.2xlarge': 0.1,
    'r5.4xlarge': 0.2,
}

memory = {
    'm5.large': 6,
    'm5.xlarge': 14,
    'm5.2xlarge': 29,
    'm5.4xlarge': 60,
    'm5a.large': 6,
    'm5a.xlarge': 14,
    'm5a.2xlarge': 29,
    'm5a.4xlarge': 60,
    'c5n.large': 3, # 3.9G in reality 
    'c5n.xlarge': 8,
    'c5n.2xlarge': 19,
    'c5n.4xlarge': 39,
    'c5.large': 2,
    'c5.xlarge': 6,
    'c5.2xlarge': 14,
    'c5.4xlarge': 29,
    'r5.large': 14,
    'r5.xlarge': 29,
    'r5.2xlarge': 60,
    'r5.4xlarge': 120,
    'i3.large': 13,
    'i3.xlarge': 28,
    'i3.2xlarge': 59,
    'i3.4xlarge': 120
}

cpus = {
    'large': 2,
    'xlarge': 4,
    '2xlarge': 8,
    '4xlarge': 16,
}

def editFiles(region, instType, numInstances, spotPrice):
    replacementString = 'regions = '+ region
    stringToBeReplaced = 'regions = '
    editFile = '../../ansible-spark/inventory/ec2.ini'
    changeLine(replacementString, stringToBeReplaced, editFile)

    replacementString = "region: " + region
    stringToBeReplaced = "region: "
    editFile = '../../ansible-spark/group_vars/all/main.yml'
    changeLine(replacementString, stringToBeReplaced, editFile)

    replacementString = "instance_type: " + instType
    stringToBeReplaced = "instance_type: "
    editFile = '../../ansible-spark/group_vars/all/main.yml'
    changeLine(replacementString, stringToBeReplaced, editFile)

    replacementString = "slave_count: " + str(numInstances)
    stringToBeReplaced = "slave_count: "
    editFile = '../../ansible-spark/group_vars/all/main.yml'
    changeLine(replacementString, stringToBeReplaced, editFile)

    replacementString = "spot_price: " + str(spotPrice)
    stringToBeReplaced = "spot_price: "
    editFile = '../../ansible-spark/group_vars/all/main.yml'
    changeLine(replacementString, stringToBeReplaced, editFile)

def changeLine(replacementString, stringToBeReplaced, filename):
    for line in fileinput.input([filename], inplace=True):
        if line.strip().startswith(stringToBeReplaced):
            line = replacementString+'\n'
        sys.stdout.write(line)

def getNWorkers(url):
    r = requests.get(url = url)
    lines = r.text.splitlines()
    # f = open('ui.html', 'r')
    # lines = f.readlines()
    numWorkers = 0
    for line in lines:
        if "Alive Workers:" in line:
            numWorkers = cleanhtml(line.strip('\n').strip()).split(':')[1].strip()
            break
    return int(numWorkers)

def getHostInfo(filename='host_file'):
    data = json.load(open(filename))
    hosts = {'masters': [], 'workers': []}
    for hostKey in data['_meta']['hostvars'].keys():
        hostVars = data['_meta']['hostvars'][hostKey]
        publicIP = hostVars["ec2_ip_address"]
        privateIP = hostVars["ec2_private_ip_address"]
        instanceID = hostVars["ec2_id"]
        instanceType = hostVars["ec2_instance_type"]
        if hostVars["ec2_tag_ds_role"] == "spark_master":
            hosts['masters'].append({'publicIP': publicIP, 'privateIP': privateIP, 'id': instanceID, 'type': instanceType})
        if hostVars["ec2_tag_ds_role"] == "spark_slave":
            hosts['workers'].append({'publicIP': publicIP, 'privateIP': privateIP, 'id': instanceID, 'type': instanceType})
        
    print(hosts)
    return hosts

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def my_special_round(x, base=10):
    return int(base * math.ceil(float(x)/base))

def start_parallel(client, output="/tmp/sar.dat", interval=5):
    result = client.run_command("rm -rf {}".format(output), greenlet_timeout=300)
    client.join(result)
    # result = client.run_command("mkdir -p {}".format(output))
    # client.join(result)
    cmd_start = "nohup sar -p -A -o {} {} > /dev/null 2>&1 &".format(output, interval)
    print(cmd_start)
    result = client.run_command(cmd_start, greenlet_timeout=300)
    client.join(result)

def stop_parallel(client):
    cmd_kill = "pkill -x sar"
    result = client.run_command(cmd_kill, greenlet_timeout=300)
    client.join(result)

def export_parallel(client, input="/tmp/sar.dat", output="/tmp/sar.csv", interval=5):
    result = client.run_command("rm -rf {}".format(output), greenlet_timeout=300)
    client.join(result)
    # TODO: this tool does not support multiple devices
    cmd_general = 'sadf -dh -t {} {} -- -p -bBqSwW -u ALL -I SUM -r ALL | csvcut -d ";" -C "# hostname,interval,CPU,INTR" | sed "1s/\[\.\.\.\]//g" > {}'.format(interval, input, "/tmp/sar_general.csv")
    cmd_disk = 'sadf -dh -t {} {} -- -p -d | csvcut -d ";" -C "# hostname,interval,DEV" | sed "1s/\[\.\.\.\]//g" > {}'.format(interval, input, "/tmp/sar_disk.csv")
    cmd_network = 'sadf -dh -t {} {} -- -p -n DEV | csvcut -d ";" -C "# hostname,interval,IFACE" | sed "1s/\[\.\.\.\]//g" > {}'.format(interval, input, "/tmp/sar_network.csv")
    cmd_join = 'csvjoin -c timestamp /tmp/sar_general.csv /tmp/sar_disk.csv | csvjoin -c timestamp - /tmp/sar_network.csv | csvformat -u 3 > {}'.format("/tmp/sar.csv")
    result = client.run_command(cmd_general, greenlet_timeout=300)
    client.join(result)
    result = client.run_command(cmd_disk, greenlet_timeout=300)
    client.join(result)
    result = client.run_command(cmd_network, greenlet_timeout=300)
    client.join(result)
    result = client.run_command(cmd_join, greenlet_timeout=300)
    client.join(result)

def getfiles_parallel(client, framework, end_index, confFile, ips, parentDir='sar_logs/'):
    dir = confFile.split('/')[-1].split('.')[0]
    if not os.path.exists(parentDir+dir):
        os.makedirs(parentDir+dir)
    print(dir)
    copy_args = [{'local_file': parentDir+dir+"/"+framework+"_"+str(i)+".csv",
                      'remote_file': '/tmp/sar.csv'} for i in range(0, end_index)]
    result = client.scp_recv('/tmp/sar.csv', parentDir+dir+"/"+framework+"_%s.csv", copy_args=copy_args)
    gevent.joinall(result)
    # client.join(output)

def start(client, output="/tmp/sar.dat", interval=5):
    client.exec_command("rm -f".format(output))
    client.exec_command("mkdir -p {}".format(os.path.dirname(output)))
    cmd_start = "nohup sar -p -A -o {} {} > /dev/null 2>&1 &".format(output, interval)
    # print(cmd_start)
    client.exec_command(cmd_start)

def stop(client):
    cmd_kill = "pkill -x sar"
    client.exec_command(cmd_kill)

def export(client, input="/tmp/sar.dat", output="/tmp/sar.csv", interval=5):
    client.exec_command('mkdir -p {}'.format(os.path.dirname(output)))
    # TODO: this tool does not support multiple devices
    cmd_general = 'sadf -dh -t {} {} -- -p -bBqSwW -u ALL -I SUM -r ALL | csvcut -d ";" -C "# hostname,interval,CPU,INTR" | sed "1s/\[\.\.\.\]//g" > {}'.format(interval, input, "/tmp/sar_general.csv")
    cmd_disk = 'sadf -dh -t {} {} -- -p -d | csvcut -d ";" -C "# hostname,interval,DEV" | sed "1s/\[\.\.\.\]//g" > {}'.format(interval, input, "/tmp/sar_disk.csv")
    cmd_network = 'sadf -dh -t {} {} -- -p -n DEV | csvcut -d ";" -C "# hostname,interval,IFACE" | sed "1s/\[\.\.\.\]//g" > {}'.format(interval, input, "/tmp/sar_network.csv")
    cmd_join = 'csvjoin -c timestamp /tmp/sar_general.csv /tmp/sar_disk.csv | csvjoin -c timestamp - /tmp/sar_network.csv | csvformat -u 3 > {}'.format("/tmp/sar.csv")
#    modified_header = 'timestamp,cpu.%usr,cpu.%nice,cpu.%sys,cpu.%iowait,cpu.%steal,cpu.%irq,cpu.%soft,cpu.%guest,cpu.%gnice,cpu.%idle,task.proc/s,task.cswch/s,intr.intr/s,swap.pswpin/s,swap.pswpout/s,paging.pgpgin/s,paging.pgpgout/s,paging.fault/s,paging.majflt/s,paging.pgfree/s,paging.pgscank/s,paging.pgscand/s,paging.pgsteal/s,paging.%vmeff,io.tps,io.rtps,io.wtps,io.bread/s,io.bwrtn/s,memory.kbmemfree,memory.kbavail,memory.kbmemused,memory.%memused,memory.kbbuffers,memory.kbcached,memory.kbcommit,memory.%commit,memory.kbactive,memory.kbinact,memory.kbdirty,memory.kbanonpg,memory.kbslab,memory.kbkstack,memory.kbpgtbl,memory.kbvmused,swap.kbswpfree,swap.kbswpused,swap.%swpused,swap.kbswpcad,swap.%swpcad,load.runq-sz,load.plist-sz,load.ldavg-1,load.ldavg-5,load.ldavg-15,load.blocked,disk.tps,disk.rd_sec/s,disk.wr_sec/s,disk.avgrq-sz,disk.avgqu-sz,disk.await,disk.svctm,disk.%util,network.rxpck/s,network.txpck/s,network.rxkB/s,network.txkB/s,network.rxcmp/s,network.txcmp/s,network.rxmcst/s,network.%ifutil'
#    cmd_create = 'echo {} > {}'.format(modified_header, output)
#    cmd_header = 'tail -n +2 {} >> {}'.format("/tmp/sar_join.csv", output)
    client.exec_command(cmd_general)
    client.exec_command(cmd_disk)
    client.exec_command(cmd_network)
    client.exec_command(cmd_join)
#    client.exec_command(cmd_create)
#    client.exec_command(cmd_header)

def getfiles(scp, dir, filename):
    
    if not os.path.exists(dir):
        os.makedirs(dir)
    print(dir)
    scp.get('/tmp/sar.csv', dir+filename)

def getEnv(filename='environment'):
    fp = open(filename, 'r')
    lines = fp.readlines()
    lines = [x.strip('\n') for x in lines]
    vars = dict()
    for line in lines:
        vars[line.split('=')[0]] = line.split('=')[1]
    fp.close()
    return vars

def setEnv(vars, filename='environment'):
    fp = open(filename, 'w')
    for key in vars.keys():
        fp.write(str(key)+"="+str(vars[key][0])+'\n')

    fp.close()

def run_cmd(cmd, cwd=".", shell=False):
    print(cmd)
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, cwd=cwd, shell=shell)
    output, error = process.communicate()
    return output

def get_runtime():
#    original_cwd = os.getcwd()
#    os.chdir(os.getcwd()+"/../")

    resultFile = open("runtime", 'r')
    runtime = float(resultFile.readlines()[-1])
#    os.chdir(original_cwd)
    return runtime

def run_benchmark(config_file, parent_dir = 'configs/', benchmark='ml/rf', timeout=1800):
    print("Provision machines and run the benchmark")
#    original_cwd = os.getcwd()
#    os.chdir(os.getcwd()+"/../")

    cmd = "python provision.py " + parent_dir + config_file + " " + benchmark + " 100 " + str(timeout)
    run_cmd(cmd)

#    os.chdir(original_cwd)
def calculate_cost(params):
    total_cost = 0.0
    for framework in params.keys():
        # print(cost[params[framework]['type']])
        # print(params[framework]['number'])
        total_cost += cost[params[framework]['type']] * (params[framework]['number']/3600.0)
    return float(total_cost)

def maxRuntime(cost, threshold):
    return (threshold/cost)+20

def waitTilUp(publicIps):
    notUp = True
    while notUp:
        for ip in publicIps:
            response= os.system("ping -c 1 " + ip + " >/dev/null 2>&1")
            if response==0:
                notUp = False
            else:
                notUp = True
                break
        time.sleep(1)
    return True

def vm_size(family, size):
    if size == 1:
        if family== "c5":
            return 'xlarge'
        else:
            return 'large'
    elif size == 2:
        if family == "c5":
            return '2xlarge'
        else:
            return 'xlarge'
    elif size == 8:
        return '2xlarge'
