import subprocess
import sys
import os
import boto3
import json
from aws_helpers import *
import multiprocessing
import pickle
import timeout_decorator

def provision_instances()
region='us-east-2'
client = boto3.client('ec2', region_name=region)

instanceCount= 1
instanceType = 'm5.large'

instanceIds = request_instances(client, instanceCount, instanceType, specJson='instances.json')
waiter = client.get_waiter('instance_running')
waiter.wait(InstanceIds=instanceIds, WaiterConfig={'Delay': 10, 'MaxAttempts': 300})
instanceIps = get_instance_public_ips(client, instanceIds)
print(instanceIps)