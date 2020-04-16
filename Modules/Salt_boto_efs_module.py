"""Skip to content
Search or jump to…

Pull requests
Issues
Marketplace
Explore
 
@Kevin-Murphy-RTT 
Learn Git and GitHub without any code!
Using the Hello World guide, you’ll start a branch, write comments, and open a pull request.



504 lines (370 sloc)  14.5 KB"""
  
# -*- coding: utf-8 -*-
'''
Connection module for Amazon EFS
.. versionadded:: 2017.7.0
'''


# Import python libs
from __future__ import absolute_import
import logging


# Import 3rd-party libs
import salt.ext.six as six
try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

# Import salt libs
from salt.utils.versions import LooseVersion as _LooseVersion

log = logging.getLogger(__name__)

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

def __virtual__():
    '''
    Only load if boto3 libraries exist and if boto3 libraries are greater than
    a given version.
    '''

    required_boto_version = '1.0.0'

    if not HAS_BOTO3:
        return (False, "The boto3.efs module cannot be loaded: " +
                "boto3 library not found")
    elif _LooseVersion(boto3.__version__) < \
         _LooseVersion(required_boto_version):
        return (False, "The boto3.efs module cannot be loaded:" +
                "boto3 library version incorrect")
    else:
        return True


def _get_conn(key=None,
              keyid=None,
              profile=None,
              region=None,
              **kwargs):
    '''
    Create a boto3 client connection to EFS
    '''
    client = None
    if profile:
        if isinstance(profile, str):
            if profile in __pillar__:
                profile = __pillar__[profile]
            elif profile in __opts__:
                profile = __opts__[profile]
    elif key or keyid or region:
        profile = {}
        if key:
            profile['key'] = key
        if keyid:
            profile['keyid'] = keyid
        if region:
            profile['region'] = region

    if isinstance(profile, dict):
        if 'region' in profile:
            profile['region_name'] = profile['region']
            profile.pop('region', None)
        if 'key' in profile:
            profile['aws_secret_access_key'] = profile['key']
            profile.pop('key', None)
        if 'keyid' in profile:
            profile['aws_access_key_id'] = profile['keyid']
            profile.pop('keyid', None)

        client = boto3.client('efs', **profile)
    else:
        client = boto3.client('efs')

    return client


def create_file_system(name,
                       performance_mode='generalPurpose',
                       keyid=None,
                       key=None,
                       profile=None,
                       region=None,
                       **kwargs):
    '''
    Creates a new, empty file system.
    name
        (string) - The name for the new file system
    performance_mode
        (string) - The PerformanceMode of the file system. Can be either
        generalPurpose or maxIO
    returns
        (dict) - A dict of the data for the elastic file system
    CLI Example:
    .. code-block::
        salt 'my-minion' boto_efs.create_file_system efs-name generalPurpose
    '''
    import os
    import base64
    creation_token = base64.b64encode(os.urandom(46), ['-', '_'])
    tags = {"Key": "Name", "Value": name}

    client = _get_conn(key=key, keyid=keyid, profile=profile, region=region)

    response = client.create_file_system(CreationToken=creation_token,
                                         PerformanceMode=performance_mode)

    if 'FileSystemId' in response:
        client.create_tags(FileSystemId=response['FileSystemId'], Tags=tags)

    if 'Name' in response:
        response['Name'] = name

    return response


def create_mount_target(filesystemid,
                        subnetid,
                        ipaddress=None,
                        securitygroups=None,
                        keyid=None,
                        key=None,
                        profile=None,
                        region=None,
                        **kwargs):
    '''
    Creates a mount target for a file system.
    You can then mount the file system on EC2 instances via the mount target.
    You can create one mount target in each Availability Zone in your VPC.
    All EC2 instances in a VPC within a given Availability Zone share a
    single mount target for a given file system.
    If you have multiple subnets in an Availability Zone,
    you create a mount target in one of the subnets.
    EC2 instances do not need to be in the same subnet as the mount target
    in order to access their file system.
    filesystemid
        (string) - ID of the file system for which to create the mount target.
    subnetid
        (string) - ID of the subnet to add the mount target in.
    ipaddress
        (string) - Valid IPv4 address within the address range
                    of the specified subnet.
    securitygroups
        (list[string]) - Up to five VPC security group IDs,
                            of the form sg-xxxxxxxx.
                            These must be for the same VPC as subnet specified.
    returns
        (dict) - A dict of the response data
    CLI Example:
    .. code-block::
        salt 'my-minion' boto_efs.create_mount_target filesystemid subnetid
    '''

    client = _get_conn(key=key, keyid=keyid, profile=profile, region=region)

    return client.create_mount_point(FileSystemId=filesystemid,
                                     SubnetId=subnetid,
                                     IpAddress=ipaddress,
                                     SecurityGroups=securitygroups)


def create_tags(filesystemid,
                tags,
                keyid=None,
                key=None,
                profile=None,
                region=None,
                **kwargs):
    '''
    Creates or overwrites tags associated with a file system.
    Each tag is a key-value pair. If a tag key specified in the request
    already exists on the file system, this operation overwrites
    its value with the value provided in the request.
    filesystemid
        (string) - ID of the file system for whose tags will be modified.
    tags
        (dict) - The tags to add to the file system
    CLI Example:
    .. code-block::
        salt 'my-minion' boto_efs.create_tags
    '''

    client = _get_conn(key=key, keyid=keyid, profile=profile, region=region)

    new_tags = []
    for k, v in six.iteritems(tags):
        new_tags.append({'Key': k, 'Value': v})

    client.create_tags(FileSystemId=filesystemid, Tags=new_tags)


def delete_file_system(filesystemid,
                       keyid=None,
                       key=None,
                       profile=None,
                       region=None,
                       **kwargs):
    '''
    Deletes a file system, permanently severing access to its contents.
    Upon return, the file system no longer exists and you can't access
    any contents of the deleted file system. You can't delete a file system
    that is in use. That is, if the file system has any mount targets,
    you must first delete them.
    filesystemid
        (string) - ID of the file system to delete.
    CLI Example:
    .. code-block::
        salt 'my-minion' boto_efs.delete_file_system filesystemid
    '''

    client = _get_conn(key=key, keyid=keyid, profile=profile, region=region)

    client.delete_file_system(FileSystemId=filesystemid)


def delete_mount_target(mounttargetid,
                       keyid=None,
                       key=None,
                       profile=None,
                       region=None,
                       **kwargs):
    '''
    Deletes the specified mount target.
    This operation forcibly breaks any mounts of the file system via the
    mount target that is being deleted, which might disrupt instances or
    applications using those mounts. To avoid applications getting cut off
    abruptly, you might consider unmounting any mounts of the mount target,
    if feasible. The operation also deletes the associated network interface.
    Uncommitted writes may be lost, but breaking a mount target using this
    operation does not corrupt the file system itself.
    The file system you created remains.
    You can mount an EC2 instance in your VPC via another mount target.
    mounttargetid
        (string) - ID of the mount target to delete
    CLI Example:
    .. code-block::
        salt 'my-minion' boto_efs.delete_mount_target mounttargetid
    '''

    client = _get_conn(key=key, keyid=keyid, profile=profile, region=region)

    client.delete_mount_target(MountTargetId=mounttargetid)


def delete_tags(filesystemid,
                tags,
                keyid=None,
                key=None,
                profile=None,
                region=None,
                **kwargs):
    '''
    Deletes the specified tags from a file system.
    filesystemid
        (string) - ID of the file system for whose tags will be removed.
    tags
        (list[string]) - The tag keys to delete to the file system
    CLI Example:
    .. code-block::
        salt 'my-minion' boto_efs.delete_tags
    '''

    client = _get_conn(key=key, keyid=keyid, profile=profile, region=region)

    client.delete_tags(FileSystemId=filesystemid, Tags=tags)


def get_file_systems(filesystemid=None,
                     keyid=None,
                     key=None,
                     profile=None,
                     region=None,
                     **kwargs):
    '''
    Get all EFS properties or a specific instance property
    if filesystemid is specified
    filesystemid
        (string) - ID of the file system to retrieve properties
    returns
        (list[dict]) - list of all elastic file system properties
    CLI Example:
    .. code-block::
        salt 'my-minion' boto_efs.get_file_systems efs-id
    '''

    result = None
    client = _get_conn(key=key, keyid=keyid, profile=profile, region=region)

    if filesystemid:
        response = client.describe_file_systems(FileSystemId=filesystemid)
        result = response["FileSystems"]
    else:
        response = client.describe_file_systems()

        result = response["FileSystems"]

        while "NextMarker" in response:
            response = client.describe_file_systems(
                        Marker=response["NextMarker"])
            result.extend(response["FileSystems"])

    return result


def get_mount_targets(filesystemid=None,
                      mounttargetid=None,
                      keyid=None,
                      key=None,
                      profile=None,
                      region=None,
                      **kwargs):
    '''
    Get all the EFS mount point properties for a specific filesystemid or
    the properties for a specific mounttargetid. One or the other must be
    specified
    filesystemid
        (string) - ID of the file system whose mount targets to list
                   Must be specified if mounttargetid is not
    mounttargetid
        (string) - ID of the mount target to have its properties returned
                   Must be specified if filesystemid is not
    returns
        (list[dict]) - list of all mount point properties
    CLI Example:
    .. code-block::
        salt 'my-minion' boto_efs.get_mount_targets
    '''

    result = None
    client = _get_conn(key=key, keyid=keyid, profile=profile, region=region)

    if filesystemid:
        response = client.describe_mount_targets(FileSystemId=filesystemid)
        result = response["MountTargets"]
        while "NextMarker" in response:
            response = client.describe_mount_targets(FileSystemId=filesystemid,
                                                 Marker=response["NextMarker"])
            result.extend(response["MountTargets"])
    elif mounttargetid:
        response = client.describe_mount_targets(MountTargetId=mounttargetid)
        result = response["MountTargets"]

    return result


def get_tags(filesystemid,
             keyid=None,
             key=None,
             profile=None,
             region=None,
             **kwargs):
    '''
    Return the tags associated with an EFS instance.
    filesystemid
        (string) - ID of the file system whose tags to list
    returns
        (list) - list of tags as key/value pairs
    CLI Example:
    .. code-block::
        salt 'my-minion' boto_efs.get_tags efs-id
    '''
    client = _get_conn(key=key, keyid=keyid, profile=profile, region=region)
    response = client.describe_tags(FileSystemId=filesystemid)
    result = response["Tags"]

    while "NextMarker" in response:
        response = client.describe_tags(FileSystemId=filesystemid,
                                        Marker=response["NextMarker"])
        result.extend(response["Tags"])

    return result


def set_security_groups(mounttargetid,
                        securitygroup,
                        keyid=None,
                        key=None,
                        profile=None,
                        region=None,
                        **kwargs):
    '''
    Modifies the set of security groups in effect for a mount target
    mounttargetid
        (string) - ID of the mount target whose security groups will be modified
    securitygroups
        (list[string]) - list of no more than 5 VPC security group IDs.
    CLI Example:
    .. code-block::
        salt 'my-minion' boto_efs.set_security_groups my-mount-target-id my-sec-group
    '''

    client = _get_conn(key=key, keyid=keyid, profile=profile, region=region)
    client.modify_mount_target_security_groups(MountTargetId=mounttargetid,
                                               SecurityGroups=securitygroup)
© 2020 GitHub, Inc.
Terms
Privacy
Security
Status
Help
Contact GitHub
Pricing
API
Training
Blog
About
