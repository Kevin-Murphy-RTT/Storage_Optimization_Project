import boto3
import csv
import datetime

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
    'ef-wc-ecco-l-stage1-n1',
    'ef-wc-ecco-l-stage1-n2'
]

class describe_efs:
    def get_efs_name_tag(fsys):
        name = "Name-Tag-Not-Set"
        if 'Tags' not in fsys:
            return name
        for tag in fsys['Tags']:
            if tag['Key'] == "Name":
                return tag['Value']
        # return name

    # def describe_mount_targets(MaxItems=None, Marker=None, FileSystemId=FSID, MountTargetId=None):
    #     """Receives FileSystem ID and Returns the 'OwnerId', 'MountTargetId', 'FileSystemId', 'SubnetId', 'LifeCycleState',
    #     'IpAddress', and 'NetworkInterfaceId.'   """
    #
    #     session = boto3.Session(profile_name=profile, region_name=region)
    #     efs = session.client('efs')
    #     mount_targets = efs.describe_mount_targets(FileSystemId='string')
    #     filename = datetime.datetime.now()
    #     if mount_targets['FileSystems']: #Only create the file if there are EFS File Systems in the region
    #         with open("EFS  " + profile + " " + region + " " + filename.strftime("%d %B %Y") + ".csv", 'w') as csv_file:    #Opens csv file
    #         csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)  #Settings for CSV file
    #         csv_writer.writerow(['OwnerId', 'MountTargetId', 'FileSystemId', 'SubnetId', 'LifeCycleState', 'IpAddress', 'NetworkInterfaceId'])  #Prints Column Headers
    #             for fsys in mount_targets['FileSystems']:
    #                 csv_writer.writerow([str(fsys['OwnerId']),
    #                                      str(fsys['MountTargetId']),
    #                                      str(fsys['FileSystemId']),
    #                                      str(fsys['SubnetId']),
    #                                      str(fsys['LifeCycleState']),
    #                                      str(fsys['IpAddress']),
    #                                      str(fsys['NetworkInterfaceId'])])


    def describe_efs_systems(profile, region):
        """Returns the 'OwnerId', 'FileSystemId', 'Name', 'CreationTime', 'LifeCycleState', and 'NumberOfMountTargets' of all EFS 
        File Systems in all regions. """

        session = boto3.Session(profile_name=profile, region_name=region)
        efs = session.client('efs')
        file_systems = efs.describe_file_systems()
        filename = datetime.datetime.now()
        if file_systems['FileSystems']: #Only create the file if there are EFS File Systems in the region
            with open("EFS  " + profile + " " + region + " " + filename.strftime("%d %B %Y") + ".csv", 'w') as csv_file:    #Opens csv file
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)  #Settings for CSV file
                csv_writer.writerow(['OwnerId', 'FileSystemId', 'Name', 'CreationTime', 'LifeCycleState', 'NumberOfMountTargets'])  #Prints Column Headers
                for fsys in file_systems['FileSystems']:
                    fs_OwnerId = fsys['OwnerId']
                    fs_FileSystemId = fsys['FileSystemId']
                    fs_efs_name = get_efs_name_tag(fsys)
                    fs_CreationTime = sys['CreationTime']
                    fs_LifeCycleState = fsys['LifeCycleState']
                    fs_NumberOfMountTargets = fsys['NumberOfMountTargets']
                    # fs_mount_targets = describe_mount_targets(fs_FileSystemId)
                    csv_writer.writerow([str(fs_OwnerId),
                                        str(fs_FileSystemId),
                                        str(fs_efs_name),
                                        str(fs_CreationTime),
                                        str(fs_LifeCycleState),
                                        str(fs_NumberOfMountTargets)]
                                        )



   
### Main Function
def main():
    """Main function"""
    aws_accounts = AWS_ACCOUNTS
    regions = AWS_REGIONS

    for aws_profile in aws_accounts:
        print("Using account " + aws_profile + "...")
        for region in regions:
            print("region = " + str(region))
            describe_efs_systems(aws_profile, region)