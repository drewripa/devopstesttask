import boto3
import socket
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

#Step 3:
#AMI creation
for instanceInfo in complexInstanceInfo:
    if instanceInfo[4] == 'Stopped':
        try :
            instance = ec2.Instance(instanceInfo[0])
            image = instance.create_image(
                Name=instanceInfo[1]+"-ami",
                Description="%s %s" % (instanceInfo[1], datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                NoReboot = True
            )
        except:
            print("Ooops")
