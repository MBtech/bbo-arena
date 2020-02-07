import boto3
import time
import json
import random

def request_spot(client, inst_count, price, type, specJson = 'instances.json', region=0):
    settings = json.load(open('settings.json', 'r'))
    zones = settings['zones']
    specs = json.load(open(specJson, 'r'))
    specs['InstanceType'] = type
    #specs['Placement']['AvailabilityZone'] = zones[region % len(zones)]
    # print specs
    response = client.request_spot_instances(
        InstanceCount=inst_count,
        LaunchSpecification=specs,
        SpotPrice=price,
        Type='one-time'
    )
    # print response
    requestIds = list()
    for request in response['SpotInstanceRequests']:
        requestIds.append(request['SpotInstanceRequestId'])
    # print requestIds
    return requestIds

def request_instances(client, instanceCount, instanceType, specJson='instances.json'):
    specs = json.load(open(specJson, 'r'))
    specs['InstanceType'] = instanceType
    specs['MaxCount']=instanceCount
    specs['MinCount']=instanceCount
    response = client.run_instances(
        **specs
    )
    instanceIds = list()
    for resp in response['Instances']:
        instanceIds.append(resp['InstanceId'])

    return instanceIds


def get_spot_instance_ids(client, requestIds):
    response = dict()
    response = client.describe_spot_instance_requests(
    SpotInstanceRequestIds=requestIds
    )
    instanceIds = list()
    for request in response['SpotInstanceRequests']:
        if 'InstanceId' in request.keys():
            instanceIds.append(request['InstanceId'])
    print(instanceIds)
    return instanceIds

def get_num_of_running_instances(client, instanceIds):
    statuses = list()
    for i in range(0, len(instanceIds), 100):
        if i+100 > len(instanceIds):
            response = client.describe_instance_status(InstanceIds=instanceIds[i:len(instanceIds)])
        else:
            response = client.describe_instance_status(InstanceIds=instanceIds[i:i+100])
        statuses.extend(response['InstanceStatuses'])
    return len(statuses)

def get_instance_public_ips(client, instanceIds):
    response = client.describe_instances(
        InstanceIds=instanceIds
    )
    ips = list()
    for request in response['Reservations'][0]['Instances']:
        ips.append(request['PublicIpAddress'])
    return ips

def get_instance_private_ips(client, instanceIds):
    response = client.describe_instances(
        InstanceIds=instanceIds
    )
    ips = list()
    for request in response['Reservations'][0]['Instances']:
        ips.append(request['PrivateIpAddress'])
    return ips

def is_instance_running(client, instanceIds):
    response = client.describe_instance_status(InstanceIds=instanceIds, IncludeAllInstances=True)
    check = True
    for status in response['InstanceStatuses']:
        print(status['InstanceState']['Name'])
        if status['InstanceState']['Name'] not in 'running':
            check = False
            break
    print("Returning " + str(check))
    return check


def reboot_instances(client, instanceIds):
    client.reboot_instances(InstanceIds=instanceIds)
    while True:
        if is_instance_running(client, instanceIds):
            break
        time.sleep(1)
    print("Instances Rebooted")
