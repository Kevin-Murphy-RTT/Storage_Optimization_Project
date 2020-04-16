#!/usr/bin/env python
#coding: utf-8

import boto3
import sys
import pandas

AWS_ACCOUNTS = [
    # 'ptc-ms-prod',  # ptc-ms-prod ReadOnly
    'RTTAdmin'  #RoundTower test account - Admin
]

AWS_REGIONS = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    # 'ap-east-1',
    # 'ap-south-1',
    # 'ap-northeast-3',
    # 'ap-northeast-2',
    # 'ap-southeast-1',
    # 'ap-southeast-2',
    # 'ap-northeast-1',
    # 'ca-central-1',
    # 'cn-north-1',
    # 'cn-northwest-1',
    'eu-central-1',
    'eu-west-1',
    'eu-west-2',
    'eu-west-3',
    'eu-north-1'
    # 'me-south-1',
    # 'sa-east-1',
    # 'us-gov-east-1',
    # 'us-gov-west-1'
]

AWS_CONFIG_QUERIES = [
    'AWS::ACM::Certificate',
    'AWS::ApiGateway::RestApi',
    'AWS::ApiGateway::Stage',
    'AWS::ApiGatewayV2::Api',
    'AWS::ApiGatewayV2::Stage',
    'AWS::AutoScaling::AutoScalingGroup',
    'AWS::AutoScaling::LaunchConfiguration',
    'AWS::AutoScaling::ScalingPolicy',
    'AWS::AutoScaling::ScheduledAction',
    'AWS::CloudFormation::Stack',
    'AWS::CloudFront::Distribution',
    'AWS::CloudFront::StreamingDistribution',
    'AWS::CloudTrail::Trail',
    'AWS::CloudWatch::Alarm',
    'AWS::CodeBuild::Project',
    'AWS::CodePipeline::Pipeline',
    'AWS::Config::ResourceCompliance',
    'AWS::DynamoDB::Table',
    'AWS::EC2::CustomerGateway',
    'AWS::EC2::EgressOnlyInternetGateway',
    'AWS::EC2::EIP',
    'AWS::EC2::FlowLog',
    'AWS::EC2::Host',
    'AWS::EC2::Instance',
    'AWS::EC2::InternetGateway',
    'AWS::EC2::NatGateway',
    'AWS::EC2::NetworkAcl',
    'AWS::EC2::NetworkInterface',
    'AWS::EC2::RegisteredHAInstance',
    'AWS::EC2::RouteTable',
    'AWS::EC2::SecurityGroup',
    'AWS::EC2::Subnet',
    'AWS::EC2::Volume',
    'AWS::EC2::VPC',
    'AWS::EC2::VPCEndpoint',
    'AWS::EC2::VPCEndpointService',
    'AWS::EC2::VPCPeeringConnection',
    'AWS::EC2::VPNConnection',
    'AWS::EC2::VPNGateway',
    'AWS::ElasticBeanstalk::Application',
    'AWS::ElasticBeanstalk::ApplicationVersion',
    'AWS::ElasticBeanstalk::Environment',
    'AWS::ElasticLoadBalancing::LoadBalancer',
    'AWS::ElasticLoadBalancingV2::LoadBalancer',
    'AWS::Elasticsearch::Domain',
    'AWS::IAM::Group',
    'AWS::IAM::Policy',
    'AWS::IAM::Role',
    'AWS::IAM::User',
    'AWS::KMS::Key',
    'AWS::Lambda::Function',
    'AWS::QLDB::Ledger',
    'AWS::RDS::DBCluster',
    'AWS::RDS::DBClusterSnapshot',
    'AWS::RDS::DBInstance',
    'AWS::RDS::DBSecurityGroup',
    'AWS::RDS::DBSnapshot',
    'AWS::RDS::DBSubnetGroup',
    'AWS::RDS::EventSubscription',
    'AWS::Redshift::Cluster',
    'AWS::Redshift::ClusterParameterGroup',
    'AWS::Redshift::ClusterSecurityGroup',
    'AWS::Redshift::ClusterSnapshot',
    'AWS::Redshift::ClusterSubnetGroup',
    'AWS::Redshift::EventSubscription',
    'AWS::S3::AccountPublicAccessBlock',
    'AWS::S3::Bucket',
    'AWS::ServiceCatalog::CloudFormationProduct',
    'AWS::ServiceCatalog::CloudFormationProvisionedProduct',
    'AWS::ServiceCatalog::Portfolio',
    'AWS::Shield::Protection',
    'AWS::ShieldRegional::Protection',
    'AWS::SQS::Queue',
    'AWS::SSM::AssociationCompliance',
    'AWS::SSM::ManagedInstanceInventory',
    'AWS::SSM::PatchCompliance',
    'AWS::WAF::RateBasedRule',
    'AWS::WAF::Rule',
    'AWS::WAF::RuleGroup',
    'AWS::WAF::WebACL',
    'AWS::WAFRegional::RateBasedRule',
    'AWS::WAFRegional::Rule',
    'AWS::WAFRegional::RuleGroup',
    'AWS::WAFRegional::WebACL',
    'AWS::WAFv2::IPSet',
    'AWS::WAFv2::ManagedRuleSet',
    'AWS::WAFv2::RegexPatternSet',
    'AWS::WAFv2::RuleGroup',
    'AWS::WAFv2::WebACL',
    'AWS::XRay::EncryptionConfig',
]

CLIENT_LIST = [
    'KRM_Industries',
    'Medina_Inc'
]

SERVERS = [
    'serv1'
]

def get_instance_name(InstanceID):
    session = boto3.session.Session()
    ec2 = session.resource('ec2')
    ec2instance = ec2.Instance(InstanceID)
    for tags in ec2instance.tags:
        if tags["Key"] == 'Name':
            instancename = tags["Value"]

    return instancename

def get_cpu_number(InstanceID):
    session = boto3.session.Session()
    ec2 = session.resource('ec2')
    instance = ec2.Instance(InstanceID)
    corecount = instance.cpu_options['CoreCount']
    threadspercore = instance.cpu_options['ThreadsPerCore']
    cpu_number = (corecount * threadspercore)
    return cpu_number

def get_volume_size(InstanceID):
    volume_dict = {}
    session = boto3.session.Session()
    ec2 = session.resource('ec2')
    instance = ec2.Instance(InstanceID)
    for ebs_info in instance.block_device_mappings:
        device_name = ebs_info['DeviceName']
        volume_id = ebs_info['Ebs']['VolumeId']
        volume_dict[device_name] = volume_id

    for k, v in volume_dict.items():
        volume = ec2.Volume(v)
        volume_dict[k] = str(volume.size) + ' GiB'

    return volume_dict

# def save_to_file(file_name, contents):
def save_to_file(profile, region, contents):
    with open("EC2  " + profile + " " + region + " " + filename.strftime("%d %B %Y") + ".csv", 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['instance_id', 'launch_time', 'type', 'state', 'name', 'volumes'])
    # fh = open(file_name, 'w')
    # fh.write(contents)
    fh.close()


def get_vpc_name(InstanceID):
    ec2 = boto3.resource('ec2')
    ec2intance = ec2.Instance(InstanceID)
    vpc_id = ec2intance.vpc_id
    vpc = ec2.Vpc(vpc_id)
    for vpc_dict in vpc.tags:
        vpc_name = vpc_dict['Value']

    return vpc_name

def get_instances_info(credentials_name):
    instance_list = []
    session = boto3.session.Session(profile_name=credentials_name)
    ec2 = session.client('ec2', region_name='cn-north-1')
    ec2_instances = ec2.describe_instances()
    contents = []
    for instance in ec2_instances['Reservations']:
        #print(instance)
        for list in instance['Instances']:
            instance_id = list['InstanceId']
            instance_name = get_instance_name(instance_id)
            #public_dns_name = list['PublicDnsName']
            #public_ip = list['PublicIp']
            private_ip = list['PrivateIpAddress']
            instance_type = list['InstanceType']
            region = list['Placement']['AvailabilityZone']
            cpu_num = get_cpu_number(instance_id)
            ebs_volume=get_volume_size(instance_id)
            status = list['State']['Name']
            vpc_name = get_vpc_name(instance_id)
            launch_time = str(list['LaunchTime']).split('+')[0]
            contents = []
            print("instance_id:%s \tinstance_name:%s \tinstance_type:%s  \tprivate_ip:%s \tregion:%s \tcpu_num:%s \tebs_volume:%s \tstatus: %s \tvpc_name:%s \tlaunch_time:%s" % \
                      (instance_id, instance_name, instance_type, private_ip, region, cpu_num, ebs_volume, status, vpc_name, launch_time))


if __name__ == '__main__':
    items=sys.argv[1]
    get_instances_info(items)
