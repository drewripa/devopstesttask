import boto3
import socket
import time
from datetime import datetime

import math
from dateutil.parser import *
from dateutil.tz import *


#Functions section
def isopen(ip, port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.settimeout(1)
   return 'Opened' if s.connect_ex((ip, port))==0 else 'Closed'

def printInstanceInfo(instanceID,
                      instanceName,
                      instanceInetName,
                      instanceState,
                      instance80,
                      instance22):
    print(
        "| %s | %s | %s | %s | %s | %s |\n" 
        "================================================================================================="
        % (instanceID,
           nameCutter(instanceName, 17),
           nameCutter(instanceInetName, 17),
           nameCutter(instanceState, 10),
           nameCutter(instance80, 7),
           nameCutter(instance22, 8))
    )

def nameCutter(strName, letCount):
    strName=str(strName).replace('\'','')
    i=len(strName)
    if i < letCount:
        return strName+" "*(letCount-i)
    if i> letCount:
        return strName[:-4]+"."*3
    else:
        return strName

def instanceAMIcreate(instanceComplexInfo, ec2Context):
    for instanceInfo in instanceComplexInfo:
        if instanceInfo[4] == 'stopped':
            try:
                instance = ec2Context.Instance(instanceInfo[0])
                image = instance.create_image(
                    Name=instanceInfo[1] + "-ami",
                    Description="%s %s" % (instanceInfo[1], datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    NoReboot=True
                )
                print(
                    "=================================================================================================\n"
                    "| AMI creation started. Waiting for finishing                                                   |\n"
                    "================================================================================================="
                )
                timer = 0
                while image.state == 'pending':
                    time.sleep(5)
                    timer += 5
                    print("| %s seconds passed" % timer)
                    image.load()
                if image.state == 'available':
                    print(
                        "=================================================================================================\n"
                        "| AMI creation successfully finished                                                            |\n"
                        "================================================================================================="
                    )
                return instanceInfo[0]
            except Exception, e:
                print(str(e))
                return ''

def instanceTermination(instanceID, ec2Context):
    try:
        instance = ec2Context.Instance(instanceID)
        instance.terminate()
        print(
            "=================================================================================================\n"
            "| Stopped instance termination started                                                          |\n"
            "================================================================================================="
        )
        timer = 0
        while instance.state != 'terminated':
            time.sleep(5)
            timer += 5
            print("| %s seconds passed" % timer)
            instance.load()
        print(
            "=================================================================================================\n"
            "| Stopped instance terminated successfully                                                      |\n"
            "================================================================================================="
        )
        return instance.placement['AvailabilityZone']
    except Exception, e:
        print(str(e))
        return ''

def getComplexInfoByIPs(serverIPs):
    ec2 = boto3.resource('ec2')
    complexInstanceInfo = []
    instances = ec2.instances.filter(
        Filters=[
            {
                'Name': 'ip-address',
                'Values': serverIPs
            }
        ])
    print(
        "=================================================================================================\n"
        "=================================================================================================\n"
        "| ID                  | Name              | DNS Name          | State      | TCP:22  | HTTP:80  |\n"
        "================================================================================================="
    )
    for instance in instances:
        instanceName = ''
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                instanceName = tag['Value']
        instanceID = instance.id
        instancePublicIP = instance.public_ip_address
        instanceInetName = serverNames[serverIPs.index(instancePublicIP)]
        instanceState = instance.state['Name']
        instance80 = isopen(instance.public_ip_address, 80)
        instance22 =isopen(instance.public_ip_address, 22)
        complexInstanceInfo.append([instanceID,
                                    instanceName,
                                    instancePublicIP,
                                    instanceInetName,
                                    instanceState,
                                    instance80,
                                    instance22])
        printInstanceInfo(
            instanceID,
            instanceName,
            instanceInetName,
            instanceState,
            instance80,
            instance22
        )
    print(
        "=================================================================================================\n"
        "| Instances information checked                                                                 |\n"
        "================================================================================================="
    )
    return complexInstanceInfo, ec2

def getComplexInfoByIDs(instanceIDs):
    ec2 = boto3.resource('ec2')
    complexInstanceInfo = []
    instances = ec2.instances.filter(
        Filters=[
            {
                'Name': 'instance-id',
                'Values': instanceIDs
            }
        ])
    print(
        "=================================================================================================\n"
        "=================================================================================================\n"
        "| ID                  | Name              | DNS Name          | State      | TCP:22  | HTTP:80  |\n"
        "================================================================================================="
    )
    for instance in instances:
        instanceName = ''
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                instanceName = tag['Value']
        instanceID = instance.id
        instanceInetName = serverNames[serverIDs.index(instanceID)]
        instanceState = instance.state['Name']
        instance80 = isopen(instance.public_ip_address, 80)
        instance22 =isopen(instance.public_ip_address, 22)
        complexInstanceInfo.append([instanceID,
                                    instanceName,
                                    instanceInetName,
                                    instanceState,
                                    instance80,
                                    instance22])
        printInstanceInfo(
            instanceID,
            instanceName,
            instanceInetName,
            instanceState,
            instance80,
            instance22
        )
    print(
        "=================================================================================================\n"
        "| Instances information checked                                                                 |\n"
        "================================================================================================="
    )


def cleanOldAMI(region):
    try:
        print(
            "=================================================================================================\n"
            "| Deregistration of old AMIs started                                                            |\n"
            "================================================================================================="
        )
        ec2Context = boto3.resource("ec2", region_name=region)
        images = ec2Context.images.filter(
            Owners=['self']
        )
        for image in images:
            creation_time = parse(image.creation_date)
            current = datetime.now(creation_time.tzinfo)
            ami_age = int(math.ceil(((current-creation_time).total_seconds()/(3600))/24))
            if ami_age > 7:
                image.deregister()
#No snapshot removal included due to 'Clean up AMIs' task
        print(
            "=================================================================================================\n"
            "| Deregistration of old AMIs complete                                                           |\n"
            "================================================================================================="
        )
    except Exception, e:
        print(str(e))

#Step 1:
#Resolve IP addresses for our DNS names
serverNames = ['one.drewripa.ga', 'two.drewripa.ga', 'three.drewripa.ga']
serverIPs = []
for serverName in serverNames:
    serverIPs.append(socket.gethostbyname(serverName))

print(
    "=================================================================================================\n"
    "| Servers IP addresses checked                                                                  |\n"
    "================================================================================================="
)

#Step 2:
#Get access to our EC2 instances via awscli (using boto3 lib) and get all needed info
#TCP check = 22 port
#HTTP ckeck = 80 port
complexInstanceInfo, ec2 = getComplexInfoByIPs(serverIPs)
#dummy list
serverIDs = []
c = 0
while c < len(serverIPs):
    serverIDs.append('')
    c+=1
for instance in complexInstanceInfo:
    serverIDs[serverIPs.index(instance[2])] = instance[0]

#Step 3:
#AMI creation
instanceID = instanceAMIcreate(complexInstanceInfo,ec2)
#Step 4:
#Stopped instance termination
region = ''
if instanceID != '':
    region = instanceTermination(instanceID, ec2)

#Step 5:
#Clean AMI older ten 1 week in terminated instance region
if region != '':
    cleanOldAMI(region)

#Step 6:
#All instances info for this lines execution time
getComplexInfoByIDs(serverIDs)



