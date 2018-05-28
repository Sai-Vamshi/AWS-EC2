"""This file contains the logic to understand a user message request from YA and return a response in the format of 
a YA message object accordingly
"""
from yellowant.messageformat import MessageClass, MessageAttachmentsClass, AttachmentFieldsClass
import boto3
from django.conf import settings

from yellowant_api.models import UserIntegration
#from .commands_by_invoke_name import commands_by_invoke_name


class CommandCenter(object):
    """Handles user commands
    
    Args:
        yellowant_integration_id (int): The integration id of a YA user
        command_name (str): Invoke name of the command the user is calling
        args (dict): Any arguments required for the command to run
    """
    def __init__(self, yellowant_user_id, yellowant_integration_id, function_name, args):
        self.yellowant_user_id = yellowant_user_id
        self.yellowant_integration_id = yellowant_integration_id
        self.function_name = function_name
        self.args = args


    #print("abcd")

    def parse(self):
        self.commands = {
            'running-instances': self.running_instances,
            'new-instance': self.new_instance,
            'health-status': self.health_status,
            'stop-instance': self.stop_instance,
            'start-instance': self.start_instance,
            'desc-security-group': self.desc_groups,
            'create-sec-group': self.create_secgroup,
            'delete-security-group': self.del_secgroup,
            'authorize-security-group': self.auth_secgroup,
            'authorize-security-group-regress': self.auth_secgroupeg,
            'revoke-security-group-ingress': self.revoke_secgroup,
            'revoke-security-group-egress': self.revoke_secgroupeg,

        }
        
        return self.commands[self.function_name](self.args)

    def running_instances(self, args):
        message = MessageClass()
        #message.message_text = "Instances Running are:"
        ec2 = boto3.resource(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)
        instances = ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            attachment = MessageAttachmentsClass()
            attachment.title = instance.id
            message.attach(attachment)

        message.message_text = "Instances Running are:"
        return message.to_json()

    def new_instance(self, args):
        message = MessageClass()
        ImageId = args["Image-ID"]
        ec2 = boto3.resource(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)
        ec2.create_instances(ImageId=ImageId, MinCount=1, MaxCount=5)

        message.message_text = "New Instance Created"
        return message.to_json()

    def health_status(self, args):
        message = MessageClass()
        # message.message_text = "Instances Running are:"
        ec2 = boto3.resource(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)
        for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
            attachment = MessageAttachmentsClass()
            s = status["InstanceStatus"]["Status"]
            attachment.title = s
            message.attach(attachment)

        message.message_text = "Instances Health Status are:"
        return message.to_json()

    def stop_instance(self, args):
        message = MessageClass()
        InstanceId = args["Instance-ID"].replace(",", " ").split()

        ec2 = boto3.resource(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)
        ec2.instances.filter(InstanceIds=InstanceId).stop()

        message.message_text = "Instance Stopped"
        return message.to_json()

    def start_instance(self, args):
        message = MessageClass()
        InstanceId = args["Instance-ID"]

        ec2 = boto3.client(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)
        response = ec2.start_instances(
            InstanceIds=[InstanceId]
        )

        message.message_text = "Instance Started"
        return message.to_json()

    def desc_groups(self, args):
        message = MessageClass()
        sgid = args["Security-group-ID"].replace(",", " ").split()
        print(sgid)
        # message.message_text = "Instances Running are:"
        ec2 = boto3.client(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)
        response = ec2.describe_security_groups(GroupIds=sgid)
        attachment = MessageAttachmentsClass()
        for i in range(len(response["SecurityGroups"])):
            d = response["SecurityGroups"][i]["Description"]
            attachment.title = d
            message.message_text = "Description of Security groups are:"
            message.attach(attachment)

        return message.to_json()

    def create_secgroup(self, args):
        message = MessageClass()
        sgid = args["Group-Name"]
        desc = args["Description"]
        ec2 = boto3.client(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)
        response = ec2.describe_vpcs()
        vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

        response = ec2.create_security_group(GroupName=sgid,
                                             Description = desc,
                                                 VpcId=vpc_id)
        attachment = MessageAttachmentsClass()
        d = response["GroupId"]
        attachment.title = d
        message.message_text = "Security group created:"
        message.attach(attachment)

        return message.to_json()

    def del_secgroup(self, args):
        sgid = args["Security-group-ID"]
        message = MessageClass()
        ec2 = boto3.client(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)

        response = ec2.delete_security_group(GroupId=sgid)
        attachment = MessageAttachmentsClass()
        message.message_text = "Security group deleted"
        message.attach(attachment)

        return message.to_json()

    def auth_secgroup(self, args):
        sgid = args["Security-group-ID"]
        protocol = args["protocol"]
        FromPort = int(args["FromPort"])
        ToPort = int(args["ToPort"])
        IpRange =  args["IpRange"]
        message = MessageClass()
        ec2 = boto3.client(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)

        data = ec2.authorize_security_group_ingress(
            GroupId=sgid,
            IpPermissions=[
                {'IpProtocol': protocol ,
                 'FromPort': FromPort,
                 'ToPort': ToPort,
                 'IpRanges': [{'CidrIp': IpRange}]}
            ])
        attachment = MessageAttachmentsClass()
        attachment.title = data
        message.message_text = "Ingress Successfully Set :"
        message.attach(attachment)

        return message.to_json()

    def auth_secgroupeg(self, args):
        sgid = args["Security-group-ID"]
        protocol = args["protocol"]
        FromPort = int(args["FromPort"])
        ToPort = int(args["ToPort"])
        IpRange =  args["IpRange"]
        message = MessageClass()
        ec2 = boto3.client(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)

        data = ec2.authorize_security_group_egress(
            GroupId=sgid,
            IpPermissions=[
                {'IpProtocol': protocol ,
                 'FromPort': FromPort,
                 'ToPort': ToPort,
                 'IpRanges': [{'CidrIp': IpRange}]}
            ])
        attachment = MessageAttachmentsClass()
        attachment.title = data
        message.message_text = "Egress Successfully Set :"
        message.attach(attachment)

        return message.to_json()

    def revoke_secgroup(self, args):
        sgid = args["Security-group-ID"]
        protocol = args["protocol"]
        FromPort = int(args["FromPort"])
        ToPort = int(args["ToPort"])
        IpRange =  args["IpRange"]
        message = MessageClass()
        ec2 = boto3.client(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)

        data = ec2.revoke_security_group_ingress(
            GroupId=sgid,
            IpPermissions=[
                {'IpProtocol': protocol ,
                 'FromPort': FromPort,
                 'ToPort': ToPort,
                 'IpRanges': [{'CidrIp': IpRange}]}
            ])
        attachment = MessageAttachmentsClass()
        attachment.title = data
        message.message_text = "Ingress Successfully Revoked :"
        message.attach(attachment)

        return message.to_json()

    def revoke_secgroupeg(self, args):
        sgid = args["Security-group-ID"]
        protocol = args["protocol"]
        FromPort = int(args["FromPort"])
        ToPort = int(args["ToPort"])
        IpRange =  args["IpRange"]
        message = MessageClass()
        ec2 = boto3.client(service_name='ec2', region_name="us-east-2", api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_ACCESS_SECRET, aws_session_token=None,
                             config=None)

        data = ec2.revoke_security_group_egress(
            GroupId=sgid,
            IpPermissions=[
                {'IpProtocol': protocol ,
                 'FromPort': FromPort,
                 'ToPort': ToPort,
                 'IpRanges': [{'CidrIp': IpRange}]}
            ])
        attachment = MessageAttachmentsClass()
        attachment.title = data
        message.message_text = "Egress Successfully Revoked :"
        message.attach(attachment)

        return message.to_json()


