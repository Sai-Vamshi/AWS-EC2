"""This file contains the logic to understand a user message request
 from YA and return a response in the format of
 a YA message object accordingly
"""
from yellowant.messageformat import MessageClass, MessageAttachmentsClass
import boto3
from yellowant_api.models import awsec2, UserIntegration


class CommandCenter(object):
    """Handles user commands
    Args:
        yellowant_integration_id (int): The integration id of a YA user
        self.commands (str): Invoke name of the command the user is calling
        args (dict): Any arguments required for the command to run
    """
    def __init__(self, yellowant_user_id, yellowant_integration_id, function_name, args,application_invoke_name):
        self.yellowant_user_id = yellowant_user_id
        self.application_invoke_name = application_invoke_name
        self.yellowant_integration_id = yellowant_integration_id
        self.id = UserIntegration.objects.get(yellowant_integration_invoke_name=self.application_invoke_name)
        self.aws_access_key = awsec2.objects.get(id=self.id).AWS_APIAccessKey
        self.aws_secret_token = awsec2.objects.get(id=self.id).AWS_APISecretAccess
        self.function_name = function_name
        self.args = args

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
            'region': self.region,
            'running-instance-list': self.running_instance_list,

        }
        return self.commands[self.function_name](self.args)

    def running_instances(self, args):
        """ Function which returns the running instances in AWS-EC2 by taking region as input"""
        message = MessageClass()
        region = args["Region"]

        # Boto3 resource creation by providing the access_id and access_secret
        ec2 = boto3.resource(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                             aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
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
        """ Function which creates a new instance in AWS-EC2 by taking region and image-id"""
        message = MessageClass()
        region = args["Region"]
        image_id = args["Image-ID"]

        # Boto3 resource creation by providing the access_id and access_secret
        ec2 = boto3.resource(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                             aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
                             config=None)
        ec2.create_instances(ImageId=image_id, MinCount=1, MaxCount=5)

        message.message_text = "New Instance Created"
        return message.to_json()

    def health_status(self, args):
        """Function which returns the health status of instances in AWS-EC2 by taking region as input"""
        message = MessageClass()
        region = args["Region"]

        # Boto3 resource creation by providing the access_id and access_secret
        ec2 = boto3.resource(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                             aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
                             config=None)
        for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
            attachment = MessageAttachmentsClass()
            s = status["InstanceStatus"]["Status"]
            attachment.title = s
            message.attach(attachment)

        message.message_text = "Instances Health Status are:"
        return message.to_json()

    def stop_instance(self, args):
        """Function which stops the running instances in AWS-EC2 by taking region and instance-id as input"""
        message = MessageClass()
        region = args["Region"]
        instanceid = args["Instance-ID"].replace(",", " ").split()

        # Boto3 resource creation by providing the access_id and access_secret
        ec2 = boto3.resource(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                             aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
                             config=None)
        ec2.instances.filter(InstanceIds=instanceid).stop()

        message.message_text = "Instance Stopped"
        return message.to_json()

    def start_instance(self, args):
        """ Function which starts the stopped instances in AWS-EC2 by taking region and instance-id as input"""
        message = MessageClass()
        region = args["Region"]
        instanceid = args["Instance-ID"]

        # Boto3 client creation by providing the access_id and access_secret
        ec2 = boto3.client(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                           verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                           aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
                           config=None)
        response = ec2.start_instances(
            InstanceIds=[instanceid]
        )

        message.message_text = "Instance Started"
        return message.to_json()

    def desc_groups(self, args):
        """ Function which returns the description of Security groups in AWS-EC2 by taking region
         and Security group-id as input"""
        message = MessageClass()
        region = args["Region"]
        sgid = args["Security-group-ID"].replace(",", " ").split()
        print(sgid)

        # Boto3 client creation by providing the access_id and access_secret
        ec2 = boto3.client(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                           verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                           aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
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
        """ Function which creates a Security group in AWS-EC2 by taking region, group name
        # and description as input"""
        message = MessageClass()
        region = args["Region"]
        sgid = args["Group-Name"]
        desc = args["Description"]

        # Boto3 client creation by providing the access_id and access_secret
        ec2 = boto3.client(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                           verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                           aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
                           config=None)
        response = ec2.describe_vpcs()
        vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

        response = ec2.create_security_group(GroupName=sgid,
                                             Description=desc,
                                             VpcId=vpc_id)
        attachment = MessageAttachmentsClass()
        d = response["GroupId"]
        attachment.title = d
        message.message_text = "Security group created:"
        message.attach(attachment)

        return message.to_json()

    def del_secgroup(self, args):
        """ Function which deletes a Security group in AWS-EC2 by taking region and
         Security group-id as input"""
        region = args["Region"]
        sgid = args["Security-group-ID"]
        message = MessageClass()

        # Boto3 client creation by providing the access_id and access_secret
        ec2 = boto3.client(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                           verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                           aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
                           config=None)

        response = ec2.delete_security_group(GroupId=sgid)
        attachment = MessageAttachmentsClass()
        message.message_text = "Security group deleted"
        message.attach(attachment)

        return message.to_json()

    def auth_secgroup(self, args):
        """ Function which authorises Security group ingress in AWS-EC2 by taking region,
         Security group-id, Protocol, From-port, To-port and Ip-range as input"""
        region = args["Region"]
        sgid = args["Security-group-ID"]
        protocol = args["protocol"]
        from_port = int(args["FromPort"])
        to_port = int(args["ToPort"])
        ip_range = args["IpRange"]
        message = MessageClass()

        # Boto3 client creation by providing the access_id and access_secret
        ec2 = boto3.client(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                           verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                           aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
                           config=None)

        data = ec2.authorize_security_group_ingress(
            GroupId=sgid,
            IpPermissions=[
                {'IpProtocol': protocol,
                 'FromPort': from_port,
                 'ToPort': to_port,
                 'IpRanges': [{'CidrIp': ip_range}]}
            ])
        attachment = MessageAttachmentsClass()
        attachment.title = data
        message.message_text = "Ingress Successfully Set :"
        message.attach(attachment)

        return message.to_json()

    def auth_secgroupeg(self, args):
        """ Function which authorises Security group egress in AWS-EC2 by taking region,
         Security group-id, Protocol, From-port, To-port and Ip-range as input"""
        region = args["Region"]
        sgid = args["Security-group-ID"]
        protocol = args["protocol"]
        from_port = int(args["FromPort"])
        to_port = int(args["ToPort"])
        ip_range = args["IpRange"]
        message = MessageClass()

        # Boto3 client creation by providing the access_id and access_secret
        ec2 = boto3.client(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                           verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                           aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
                           config=None)

        data = ec2.authorize_security_group_egress(
            GroupId=sgid,
            IpPermissions=[
                {'IpProtocol': protocol,
                 'FromPort': from_port,
                 'ToPort': to_port,
                 'IpRanges': [{'CidrIp': ip_range}]}
            ])
        attachment = MessageAttachmentsClass()
        attachment.title = data
        message.message_text = "Egress Successfully Set :"
        message.attach(attachment)

        return message.to_json()

    def revoke_secgroup(self, args):
        """ Function which revokes Security group ingress in AWS-EC2 by taking region,
         Security group-id, Protocol, From-port, To-port and Ip-range as input"""
        region = args["Region"]
        sgid = args["Security-group-ID"]
        protocol = args["protocol"]
        from_port = int(args["FromPort"])
        to_port = int(args["ToPort"])
        ip_range = args["IpRange"]
        region = args["Region"]
        message = MessageClass()

        # Boto3 client creation by providing the access_id and access_secret
        ec2 = boto3.client(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                           verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                           aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
                           config=None)

        data = ec2.revoke_security_group_ingress(
            GroupId=sgid,
            IpPermissions=[
                {'IpProtocol': protocol,
                 'FromPort': from_port,
                 'ToPort': to_port,
                 'IpRanges': [{'CidrIp': ip_range}]}
            ])
        attachment = MessageAttachmentsClass()
        attachment.title = data
        message.message_text = "Ingress Successfully Revoked :"
        message.attach(attachment)

        return message.to_json()

    def revoke_secgroupeg(self, args):
        """ Function which revokes Security group egress in AWS-EC2 by taking region,
         Security group-id, Protocol, From-port, To-port and Ip-range as input"""
        region = args["Region"]
        sgid = args["Security-group-ID"]
        protocol = args["protocol"]
        from_port = int(args["FromPort"])
        to_port = int(args["ToPort"])
        ip_range = args["IpRange"]
        message = MessageClass()

        # Boto3 client creation by providing the access_id and access_secret
        ec2 = boto3.client(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                           verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                           aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
                           config=None)

        data = ec2.revoke_security_group_egress(
            GroupId=sgid,
            IpPermissions=[
                {'IpProtocol': protocol,
                 'FromPort': from_port,
                 'ToPort': to_port,
                 'IpRanges': [{'CidrIp': ip_range}]}
            ])
        attachment = MessageAttachmentsClass()
        attachment.title = data
        message.message_text = "Egress Successfully Revoked :"
        message.attach(attachment)

        return message.to_json()

    def region(self, args):
        """ Basic inactive function to get dynamic inputs in  all other functions."""
        m = MessageClass()
        print('123124')
        data = {'list': []}
        data['list'].append({"Region_Name": "us-east-1"})
        data['list'].append({"Region_Name": "us-east-2"})
        data['list'].append({"Region_Name": "us-west-1"})
        data['list'].append({"Region_Name": "us-west-2"})
        data['list'].append({"Region_Name": "ap-northeast-1"})
        data['list'].append({"Region_Name": "ap-northeast-2"})
        data['list'].append({"Region_Name": "ap-south-1"})
        data['list'].append({"Region_Name": "ap-southeast-1"})
        data['list'].append({"Region_Name": "ap-southeast-1"})
        data['list'].append({"Region_Name": "ca-central-1"})
        data['list'].append({"Region_Name": "eu-central-1"})
        data['list'].append({"Region_Name": "eu-west-1"})
        data['list'].append({"Region_Name": "eu-west-2"})
        data['list'].append({"Region_Name": "eu-west-3"})
        data['list'].append({"Region_Name": "sa-east-1"})
        m.data = data
        return m.to_json()

    def running_instance_list(self, args):
        message = MessageClass()
        region = args["Region"]

        # Boto3 client creation by providing the access_id and access_secret
        ec2 = boto3.resource(service_name='ec2', region_name=region, api_version=None, use_ssl=True,
                             verify=None, endpoint_url=None, aws_access_key_id=self.aws_access_key,
                             aws_secret_access_key=self.aws_secret_token, aws_session_token=None,
                             config=None)
        instances = ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            attachment = MessageAttachmentsClass()
            attachment.title = instance.id
            message.attach(attachment)

        message.message_text = "Instances Running are:"
        return message.to_json()
