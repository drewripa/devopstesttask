import boto3
import socket

servernames = ['one.drewripa.ga', 'two.drewripa.ga', 'three.drewripa.ga']
for servername in servernames:
    print(socket.gethostbyname(servername))

ec2 = boto3.resource('ec2')

instances = ec2.instances.filter(
    Filters=[
        {
            'Name': 'instance-state-name',
            'Values': ['running']
        }
    ])
for instance in instances:
    print(instance.id, instance.instance_type, instance.public_ip_address)
