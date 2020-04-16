# Package Imports
import boto3

# Module Imports
import helpers
from botocore.exceptions import ClientError

# Cleaner Settings
RESOURCE_NAME = "Elastic File System"  # Not plural
WHITELIST_NAME = "efs"
BOTO3_NAME = "efs"
BOTO3_LIST_FUNCTION = "describe_file_systems"

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

class delete_efs:
    def clean_efs() -> list:
        """Main ordering for cleaning resources.
        Returns:
            A list of all terminated resources
        """
        helpers.starting_clean_print(RESOURCE_NAME)
        efs_client = boto3.client(BOTO3_NAME)
        file_systems = get_file_systems(efs_client)
        terminated_file_systems = delete_file_systems(efs_client, file_systems)
        helpers.finished_clean_print(RESOURCE_NAME, terminated_file_systems)
        return terminated_file_systems

    def get_file_systems(efs_client) -> list:
        """Get all resources in an account
        Args:
            efs_client (boto3.client): A efs client
        Returns:
            A list of resources
        """
        file_systems_list = []
        paginator = efs_client.get_paginator(BOTO3_LIST_FUNCTION)
        pages = paginator.paginate()
        for page in pages:
            # Your going to have to look through the response and append the correct value to the list
            file_system = page["FileSystems"]
            file_systems_list = file_systems_list + file_system
        return file_systems_list

    def delete_file_systems(efs_client, file_system_list) -> list:
        """Deletes all resources from a list
        Args:
            efs_client (boto3.Client): A boto3 client for EFS
            file_system_list (list): A list of resources
        Returns:
            A list of terminated resources
        """
        terminated_file_systems = []
        for file_system in file_system_list:
            file_system_id = file_system["FileSystemId"] # Get the name used for the deletion here.
            if helpers.check_in_whitelist(file_system_id, WHITELIST_NAME):  # TODO need to create a cleaner for the mount targets
                continue
            try:
                efs_client.delete_file_system(
                    FileSystemId=file_system_id
                )
            except ClientError as error:
                error_string = "{0} on {1} - {2}".format(error, RESOURCE_NAME,
                                                        file_system_id)
                print(error_string)
                terminated_file_systems.append(error_string)
                continue
            terminated_file_systems.append(file_system_id)
        return terminated_file_systems
