import os
import json
import paramiko
import sys
from scp import SCPClient
from helpers import *
from pssh.clients import ParallelSSHClient

## This needs to be executed with python 3 and it is incompatible with Python 2
def sar_helper(ip,  dir, filename, command, config):
    print(ip, dir, filename, command, config)
    # time.sleep(10)
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #client.set_missing_host_key_policy(paramiko.WarningPolicy())
    client.connect(ip, username=config["username"], password="", pkey=None, key_filename=config["keyname"])

    # SCPCLient takes a paramiko transport as an argument
    scp = SCPClient(client.get_transport(), socket_timeout=60)

    scp.close()
    if command=="start":
        start(client)
    elif command=="terminate":
        stop(client)
    elif command=="collectcsv":
        
        getfiles(scp, dir, filename)
    else:
        export(client)


def sar(command, directory, hosts, filenames):
    # "keyname": "/Users/mb/Downloads/bilal-us-east.pem.txt"
    config = json.load(open('config.json'))

    client = ParallelSSHClient(hosts,  user=config["username"], password="", pkey=config["keyname"], timeout=600, pool_size=64)

    if command=="start":
        start_parallel(client)
    elif command=="terminate":
        stop_parallel(client)
    elif command=="collectcsv":
        count = 0
        for host in hosts:
            
            sar_helper(host, directory, filenames[count], command, config)
            count +=1

        # getfiles_parallel(client, framework, len(hosts), confFile, hosts)
    else:
        export_parallel(client)
