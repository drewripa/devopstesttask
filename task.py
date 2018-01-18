import boto3
import socket


def isopen(ip, port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.settimeout(1)
   return 0 if s.connect_ex((ip, port)) else 1

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
    complexInstanceInfo.append([instance.id,
                                instance.public_ip_address,
                                serverNames[serverIPs.index(instance.public_ip_address)],
                                instance.state['Name'],
                               (isopen(instance.public_ip_address, 80)),
                               (isopen(instance.public_ip_address, 22)),
                               (isopen(instance.public_ip_address, 666))])
#TODO: Remove line
print(complexInstanceInfo)
