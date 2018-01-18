import boto3

ec2 = boto3.resource('ec2')

instances = ec2.instances
for instance in instances:
    print(instance.id, instance.instance_type, instance.public_ip_address, instance.state)
