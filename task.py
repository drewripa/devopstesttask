import boto3
import socket
import time
from datetime import datetime


def isopen(ip, port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.settimeout(1)
   return 0 if s.connect_ex((ip, port))==0 else 1

#Step 1:
#Resolve IP addresses for our DNS names
serverNames = ['one.drewripa.ga', 'two.drewripa.ga', 'three.drewripa.ga']
serverIPs = []
for serverName in serverNames:
    serverIPs.append(socket.gethostbyname(serverName))
#TODO: Remove line
print(serverIPs)
print(
    "=================================================================================================\n"
    "| Servers IP addresses checked                                                                  |\n"
    "================================================================================================="
)

#Step 2:
#Get access to our EC2 instances via awscli (using boto3 lib) and get all needed info
#TCP check = 22 port
#HTTP ckeck = 80 port
ec2 = boto3.resource('ec2')
complexInstanceInfo=[]

instances = ec2.instances.filter(
    Filters=[
        {
            'Name': 'ip-address',
            'Values': serverIPs
        }
    ])
for instance in instances:
    instanceName = ''
    for tag in instance.tags:
        if tag['Key'] == 'Name':
            instanceName = tag['Value']

    complexInstanceInfo.append([instance.id,
                               instanceName,
                               instance.public_ip_address,
                               serverNames[serverIPs.index(instance.public_ip_address)],
                               instance.state['Name'],
                               (isopen(instance.public_ip_address, 80)),
                               (isopen(instance.public_ip_address, 22))])
#TODO: Remove line
print(complexInstanceInfo)
print(
    "=================================================================================================\n"
    "| Instances information checked                                                                  |\n"
    "================================================================================================="
)

#Step 3:
#AMI creation
for instanceInfo in complexInstanceInfo:
    print(instanceInfo[4])
    if instanceInfo[4] == 'stopped':
        try:
            instance = ec2.Instance(instanceInfo[0])
            image = instance.create_image(
                Name=instanceInfo[1]+"-ami",
                Description="%s %s" % (instanceInfo[1], datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                NoReboot = True
            )
            print(
                "=================================================================================================\n"
                "| AMI creation started. Waiting for finishing                                                   |\n"
                "================================================================================================="
            )
            timer = 0
            while image.state == 'pending':
                time.sleep(5)
                timer+=5
                print("| %s seconds passed" % timer)
                image.load()
            if image.state == 'available':
                print(
                    "=================================================================================================\n"
                    "| AMI creation successfully finished                                                            |\n"
                    "================================================================================================="
                )
                timer = 0
            instance.terminate()
            print(
                "=================================================================================================\n"
                "| Stopped instance termination started                                                          |\n"
                "================================================================================================="
            )
            while instance.state != 'terminated':
                time.sleep(5)
                timer+=5
                print("| %s seconds passed" % timer)
            print(
                "=================================================================================================\n"
                "| Stopped instance terminated successfully                                                      |\n"
                "================================================================================================="
            )
        except Exception, e:
            print(str(e))
