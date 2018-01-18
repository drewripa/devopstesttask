import boto3
import socket

servernames = ['one.drewripa.ga', 'two.drewripa.ga', 'three.drewripa.ga']
servernamesIP = []
for servername in servernames:
    servernamesIP.append(socket.gethostbyname(servername))
print(servernamesIP)

ec2 = boto3.resource('ec2')

instances = ec2.instances.filter(
    Filters=[
        {
            'Name': 'ip-address',
            'Values': servernamesIP
        }
    ])
for instance in instances:
    print(instance.id, instance.instance_type, instance.public_ip_address)
