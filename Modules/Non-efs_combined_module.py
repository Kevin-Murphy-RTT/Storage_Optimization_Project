import boto3
import csv
import datetime
#awscli command for later:
#aws resourcegroupstaggingapi get-resources --region us-east-1 --output json > rgsa_us-east-1.json
#https://console.aws.amazon.com/resource-groups/tag-editor/find-resources

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

def get_ec2_name_tag(instance): #Pull the name of the EC2 instance, as it is a tag and not a default key:value
    name = "Name-Tag-Not-Set"
    if 'Tags' not in instance:
        return name
    for tag in instance['Tags']:
        if tag['Key'] == "Name":
            return tag['Value']
    return name

def get_value_result(value,item): #determines if the value is in the item, to avoid error
    result = str(value) + " Has No Value"
    if value not in item:
        return result
    else:
        return item[value]

def get_ec2_instances(profile, region):
    session = boto3.Session(profile_name=profile, region_name=region)
    ec2 = session.client('ec2')
    response = ec2.describe_instances()
    filename = datetime.datetime.now()
    if response['Reservations']:
        with open("EC2  " + profile + " " + region + " " + filename.strftime("%d %B %Y") + ".csv", 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['instance_id', 'launch_time', 'type', 'state', 'name'])
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    csv_writer.writerow([instance['InstanceId'],
                                        str(instance['LaunchTime']),
                                        str(instance['InstanceType']),
                                        str(instance['State']['Name']),
                                        get_ec2_name_tag(instance)])

def get_DynamoDB_resources(profile, region):
    session = boto3.Session(profile_name=profile, region_name=region)
    aws_client = session.client('dynamodb')
    table_list = aws_client.list_tables()
    filename = datetime.datetime.now()
    if table_list['TableNames']:
        with open("DynamoDB  " + profile + " " + region + " " + filename.strftime("%d %B %Y") + ".csv", 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['TableName', 'TableStatus', 'CreationDateTime', 'ProvisionedThroughput', 'TableSizeBytes'])
            for returned in table_list['TableNames']:
                table_description = aws_client.describe_table(TableName=returned)
                csv_writer.writerow([str(table_description['Table']['TableName']),
                                     str(table_description['Table']['TableStatus']),
                                     str(table_description['Table']['CreationDateTime']),
                                     str(table_description['Table']['ProvisionedThroughput']),
                                     str(table_description['Table']['TableSizeBytes'])])

def get_ecs_resources(profile, region):
    session = boto3.Session(profile_name=profile, region_name=region)
    aws_client = session.client('ecs')
    cluster_list = aws_client.list_clusters(maxResults=100)
    filename = datetime.datetime.now()
    if cluster_list['clusterArns']:
        with open("ECS  " + profile + " " + region + " " + filename.strftime("%d %B %Y") + ".csv", 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['clusterName',
                                 'status',
                                 'registeredContainerInstancesCount',
                                 'runningTasksCount',
                                 'activeServicesCount'])
            for i in cluster_list['clusterArns']:
                cluster_description = aws_client.describe_clusters(clusters=[i])
                for response in cluster_description['clusters']:
                    csv_writer.writerow([str(response['clusterName']),
                                         str(response['status']),
                                         str(response['registeredContainerInstancesCount']),
                                         str(response['runningTasksCount']),
                                         str(response['activeServicesCount'])])

def get_rds_instances(profile, region):
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client('rds')
    response = client.describe_db_instances()
    filename = datetime.datetime.now()
    with open("RDS Report on " + profile + " " + region + " " + filename.strftime("%d %B %Y") + ".csv", 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['DBInstanceIdentifier','DBInstanceClass','AllocatedStorage','InstanceCreateTime','Engine'])
        for i in response['DBInstances']:
            db_instance_name = i['DBInstanceIdentifier']
            db_type = i['DBInstanceClass']
            db_storage = i['AllocatedStorage']
            db_created = i['InstanceCreateTime']
            db_engine: object = i['Engine']
            csv_writer.writerow([str(db_instance_name),
                                 str(db_type),
                                 str(db_storage),
                                 str(db_created),
                                 str(db_engine)])

def get_s3_resources(profile, region):
    session = boto3.Session(profile_name=profile, region_name=region)
    aws_client = session.client('s3')
    bucket_list = aws_client.list_buckets()
    filename = datetime.datetime.now()
    if bucket_list['Buckets']:
        with open("S3  " + profile + " " + region + " " + filename.strftime("%d %B %Y") + ".csv", 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Name', 'CreationDate'])
            for returned in bucket_list['Buckets']:
                csv_writer.writerow([str(returned['Name']),
                                     str(returned['CreationDate'])])

def get_config_resources(profile, region,): #returns configservice results per account per region
    session = boto3.Session(profile_name=profile, region_name=region)
    config_client = session.client('config')
    config_queries = AWS_CONFIG_QUERIES
    filename = datetime.datetime.now()
    with open('Config Report ' + str(profile) + ' ' + str(region) + ' ' +
              filename.strftime("%I.%M%p %d %B %Y") + '.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['accountId',
                             'arn',
                             'resourceType',
                             'resourceId',
                             'resourceName',
                             'awsRegion',
                             'availabilityZone',
                             'resourceCreationTime'])
        for query in config_queries:
            response = config_client.list_discovered_resources(resourceType=query)
            if response['resourceIdentifiers']:
                for entry in response['resourceIdentifiers']:
                    answer = config_client.get_resource_config_history(resourceType=entry['resourceType'],
                                                                       resourceId=entry['resourceId'])
                    if answer['configurationItems']:
                        for item in answer['configurationItems']:
                            csv_writer.writerow([get_value_result('accountId',item),
                                                 get_value_result('arn',item),
                                                 get_value_result('resourceType',item),
                                                 get_value_result('resourceId',item),
                                                 get_value_result('resourceName',item),
                                                 get_value_result('awsRegion',item),
                                                 get_value_result('availabilityZone',item),
                                                 get_value_result('resourceCreationTime',item)])

### Main Function

def main():
    """Main function"""
    aws_accounts = AWS_ACCOUNTS
    regions = AWS_REGIONS

    for aws_profile in aws_accounts:
        print("Using account " + aws_profile + "...")
        for region in regions:
            print("region = " + str(region))
            get_ec2_instances(aws_profile, region)
            get_DynamoDB_resources(aws_profile, region)
            get_ecs_resources(aws_profile, region)
            get_rds_instances(aws_profile, region)
            get_s3_resources(aws_profile, region)
            try:
                get_config_resources(aws_profile, region)
            except:
                print("Could not complete ConfigService request")

if __name__ == "__main__":
    main()

