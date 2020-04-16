#!/usr/local/bin/python3


"""
AWS Multitool

Script to query resource information from AWS and modify/delete resource tags.


Optional flags:
  -h, --help        Show help message and exit
  -p, --profile     Use specific AWS profile (can be used multiple times,
                        defaults to AWS_ACCOUNTS list)


AWS Resources:
  (AWS Resources to interact with)

    ec2                 Query/modify EC2 info/tags from AWS
    ebs                 Query/modify EBS info/tags from AWS
    elb                 Query ELB info from AWS
    rds                 Query RDS info from AWS


EC2 commands:
  (Command line options for EC2 resource)

    query               Query EC2 tags/info from AWS

        -n, --team-numbers      List of team number to query
        -T, --tag               Tag key to search for
        -V, --values            Tag values to search for
        -e, --empty             Include empty tag values (does not include untagged
                                    resources)
        -t, --tags              List of tags to query (defaults to all tags)
        -a, --all               Query all EC2 instances

    update              Update EC2 tags

        -i, --input     Path to input file containing list of InstanceIds
        -t, --tag       Tag key to update/set
        -v, --value     Value to set tag to

    delete              Delete EC2 tags

        -i, --input     Path to input file containing list of InstanceIds
        -t, --tag       Tag key to delete
        -v, --value     Delete tag only if given value
        -a, --all       Delete all tags with given name, regardless of value

    configure           Update EC2 tags

        -i, --input     Path to CSV with desired tag configuration
        -d, --delete    Delete tags without given values (by default, blank values are not changed)


EBS commands:
  (Command line options for EBS resource)

    query               Query EBS tags/info from AWS

        -n, --team-numbers      List of team number to query
        -T, --tag               Tag key to search for
        -V, --values            Tag values to search for
        -e, --empty             Include empty tag values (does not include untagged
                                    resources)
        -t, --tags              List of tags to query (defaults to all tags)
        -a, --all               Query all EBS volumes

    update              Update EBS tags

        -i, --input     Path to input file containing list of InstanceIds
        -t, --tag       Tag key to update/set
        -v, --value     Value to set tag to

    delete              Delete EBS tags

        -i, --input     Path to input file containing list of InstanceIds
        -t, --tag       Tag key to delete
        -v, --value     Delete tag only if given value
        -a, --all       Delete all tags with given name, regardless of value

    configure           Update EBS tags

        -i, --input     Path to CSV with desired tag configuration
        -d, --delete    Delete tags without given values (by default, blank values are not changed)


ELB commands:
  (Command line options for ELB resource)

    query               Query ELB information

        -i, --input             Path to input JSON file containing ELB data (will not
                                    pull data from AWS)
        -n, --team-numbers      List of team number to query
        -u, --underutilized     Output underutilized ELB information (will take some time)
        -a, --all               Output all ELB information


ELB commands:
  (Command line options for ELB resource)

    query               Query RDS information


Example Usage:

    ./aws_multitool.py ec2 query -n 6 25 98

        Pull all EC2 instance tags/information for teams 6/06, 25, and 98 into separate files

    ./aws_multitool.py ec2 update -i ./instance_ids.txt -t hello -n world

        Change/set tag 'hello' to value 'world' on given list of EC2 instances

    ./aws_multitool.py ebs delete -i ./volume_ids.txt -t hello -a

        Delete tag 'hello' from the given list of EBS volumes

    ./aws_multitool.py configure -i ./config.tags.team00.csv

        Edit tags of instances in the input CSV file to match the values found in the file

    ./aws_multitool.py elb query -n 5 42

        Pull all ALB/ELBs for teams 5/05 and 42 into separate files, and include utilization status




Author(s):  Kevin R. Murphy and Jacob F. Grant
Created: 08/19/19
"""

import argparse
import boto3
import botocore.exceptions
import csv
import datetime
import json
import re



### AWS Accounts

AWS_ACCOUNTS = [
    '5466ReadOnly',     # Prod ReadOnly
]


### I/O Functions

def get_file_name(file_name_list, file_extension):
    """Generate a file name given the inputs"""
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    file_name_list.append(date)
    file_name_list.append(file_extension)
    return '.'.join(x.strip() for x in file_name_list if x.strip())


def read_file(file_name):
    """Read from a JSON file"""
    with open(file_name) as f:
        if file_name.endswith('.json'):
            data = json.load(f)
        else:
            data = f.read().splitlines()
        return data


def get_ids_from_file(file_name, resource_id):
    """Read a list of resource IDs from csv file."""
    data = []
    with open(file_name) as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            data.append(row)
    try:
        id_index = data[0].index(resource_id)
    except ValueError:
        print(resource_id + " not found in headers. Using first column.")
        id_index = 0
    if data[0][id_index] == resource_id:
        return [d[0] for d in data[1:]]
    else:
        return [d[0] for d in data]


def write_file(file_name, data, file_type=None):
    """Write data to file"""
    if not file_name:
        if file_name.endswith('.json'):
            file_type = 'json'
        if file_name.endswith('.csv'):
            file_type = 'csv'

    # JSON file
    if file_type == 'json':
        with open(file_name, 'w') as outfile:
            json.dump(data, outfile, default=str)
            return

    # CSV file
    if file_type == 'csv':
        with open(file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
            return

    # Other file
    with open(file_name, 'w', newline='') as f:
        for line in data:
            f.write(line)
            f.write('\n')


def output_data_to_file(file_name_list, file_extension, statement, data, check_data=True):
    """Write out a file with a given name and print statement"""
    file_name = get_file_name(file_name_list, file_extension)
    if check_data:
        if len(data) <= 1:
            print("No " + statement + " found. Skipping " + file_name)
            return
    print("Writing " + statement + " to " + file_name)
    write_file(
        file_name,
        data,
        file_extension
    )


### AWS Client Functions


def get_ec2_client(aws_profile):
    """Return a boto3 EC2 client object for a given AWS profile"""
    try:
        ec2_client = boto3.session.Session(profile_name=aws_profile).client('ec2')
    except botocore.exceptions.ProfileNotFound:
        print("ERROR: Profile " + str(aws_profile) + " not found")
        ec2_client = None
    return ec2_client


def get_elb_client(aws_profile, v2=False):
    """Return a boto3 ELB client object for a given AWS profile"""
    try:
        if v2:
            elb_client = boto3.session.Session(profile_name=aws_profile).client('elbv2')
        else:
            elb_client = boto3.session.Session(profile_name=aws_profile).client('elb')
    except botocore.exceptions.ProfileNotFound:
        print("ERROR: Profile " + str(aws_profile) + " not found")
        elb_client = None
    return elb_client


def get_aws_client(aws_profile, aws_resource):
    """Return a boto3 client object for a given profile and resource"""
    try:
        aws_client = boto3.session.Session(profile_name=aws_profile).client(aws_resource)
    except botocore.exceptions.ProfileNotFound:
        print("ERROR: Profile " + str(aws_profile) + " not found")
        aws_client = None
    return aws_client


### Generic Functions

def get_team_strings(team_number, regex=False, quiet=False):
    """Return a list of strings to search for by team"""
    if not quiet:
        qprint = lambda x : print("Using team number " + team_number + str(x))
    else:
        qprint = lambda x : None
    team_number = str(team_number)
    team_strings = [('-' + team_number + '-')]
    if len(team_number) == 1:
        qprint("/0" + team_number)
        team_strings.append('-0' + team_number + '-')
    if team_number[0] == '0':
        qprint("/" + team_number[1:])
        team_strings.append('-' + team_number[1:] + '-')
    if len(team_strings) == 1:
        qprint('')
    if regex:
        s = 0
        while s < len(team_strings):
            team_strings[s] = '*' + team_strings[s] + '*'
            s += 1
    return team_strings


### EC2 Resource Functions

def generate_ec2_args(tag_name, tag_values):
    """Return all team numbers"""
    tag_name ='tag:' + tag_name
    ec2_args = {
        'Filters': [
            {
                'Name': tag_name,
                'Values': tag_values
            },
        ]
    }
    return ec2_args


def get_instances(ec2_args, ec2_client):
    """Return all instances for a set of EC2 arguments"""
    instances = []
    while True:
        try:
            response = ec2_client.describe_instances(**ec2_args)
        except botocore.exceptions.ClientError as err:
            # Check for invalid or malformed InstanceIds
            if err.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                invalid_resources = err.response['Error']['Message'].split("'")[1].split(', ')
                valid_resources = [i for i in ec2_args['InstanceIds'] if i not in invalid_resources]
                valid_ec2_args = {'InstanceIds': valid_resources}
                if not valid_ec2_args:
                    print("No valid instances to search for.")
                    return
                return get_instances(valid_ec2_args, ec2_client)
            if err.response['Error']['Code'] == 'InvalidInstanceID.Malformed':
                invalid_resources = [err.response['Error']['Message'].split('"')[1]]
                valid_resources = [i for i in ec2_args['InstanceIds'] if i not in invalid_resources]
                valid_ec2_args = {'InstanceIds': valid_resources}
                if not valid_ec2_args:
                    print("No valid instances to search for.")
                    return
                return get_instances(valid_ec2_args, ec2_client)
            else:
                raise
        for instance in response['Reservations']:
            # This may be inaccurate. Consider removing.
            for i in instance['Instances']:
                i['OwnerId'] = instance['OwnerId']
            instances += instance['Instances']
        # Continue if response is truncated
        try:
            ec2_args['NextToken'] = response['NextToken']
        except KeyError:
            break
    return instances


def get_volumes(ebs_args, ec2_client):
    """Return all instances for a set of EC2 arguments"""
    volumes = []
    while True:
        try:
            response = ec2_client.describe_volumes(**ebs_args)
        except botocore.exceptions.ClientError as err:
            # Check for invalid or malformed VolumeIds
            if err.response['Error']['Code'] == 'InvalidVolume.NotFound':
                invalid_resources = [err.response['Error']['Message'].split("'")[1]]
                valid_resources = [v for v in ebs_args['VolumeIds'] if v not in invalid_resources]
                valid_ebs_args = {'VolumeIds': valid_resources}
                return get_volumes(valid_ebs_args, ec2_client)
            if err.response['Error']['Code'] == 'InvalidParameterValue':
                invalid_resources = [err.response['Error']['Message'].split('(', 1)[1].split(')')[0]]
                valid_resources = [i for i in ebs_args['VolumeIds'] if i not in invalid_resources]
                valid_ebs_args = {'VolumeIds': valid_resources}
                return get_volumes(valid_ebs_args, ec2_client)
            else:
                raise
        volumes += response['Volumes']
        # Continue if response is truncated
        try:
            ebs_args['NextToken'] = response['NextToken']
        except KeyError:
            break
    return volumes


def get_rds_resources(rds_client):
    """Return all DB instances for a set of RDS arguments"""
    rds_args={}
    rds_instances = []
    while True:
        response = rds_client.describe_db_instances(**rds_args)
        for rds_instance in response['DBInstances']:
            rds_instances.append(rds_instance)
        # Continue if response is truncated
        try:
            rds_args['Marker'] = response['Marker']
        except KeyError:
            break
    return rds_instances


def combine_resource_lists(resources, new_resources, id_key):
    """Combine two lists of resources, preserving order and removing duplicates"""
    resource_ids = set()
    for resource in resources:
        resource_ids.add(resource[id_key])
    for resource in new_resources:
        if resource[id_key] not in resource_ids:
            resources.append(resource)
    return resources


def get_resource_ids(resources, id_key):
    """Get list of resource Ids"""
    resource_ids = []
    for resource in resources:
        resource_ids.append([resource[id_key]])
    return resource_ids


def get_resource_info(resources, headers):
    """Return list of list of resource information"""
    resource_info = [headers]
    for resource in resources:
        new_resource = []
        for h in headers:
            new_value = ''
            try:
                new_value = str(resource[h])
            except KeyError:
                try:
                    for tag in resource['Tags']:
                        if tag['Key'] == h:
                            new_value = str(tag['Value'])
                            break
                except KeyError:
                    pass
            new_resource.append(new_value)
        resource_info.append(new_resource)
    return resource_info


def get_current_state(resources):
    """Add the current resource state"""
    for resource in resources:
        try:
            resource['CurrentState'] = resource['State']['Name']
        except (KeyError, TypeError):
            try:
                resource['CurrentState'] = resource['State']['Code']
            except (KeyError, TypeError):
                try:
                    resource['CurrentState'] = resource['State']
                except KeyError:
                    pass
    return resources


# Tagging Functions

def get_all_tag_names(resources, quiet=False):
    """Return a sorted list of all tags names found"""
    tag_names = set()
    for resource in resources:
        try:
            for tag in resource['Tags']:
                tag_names.add(tag['Key'])
        except KeyError:
            pass

    # Sort with "Name" tag first
    try:
        tag_names.remove('Name')
        name_removed = True
    except:
        name_removed = False
    tag_names = list(tag_names)
    tag_names.sort()
    if name_removed:
        tag_names = ['Name'] + tag_names

    if not quiet:
        print(tag_names)
    return tag_names


def get_resource_tags(resources, tag_names, id_key):
    """Return a list of lists of instance tags"""
    tags_list = [[id_key] + tag_names]
    for resource in resources:
        instance_list = [resource[id_key]]

        # Get dictionary of instance's tags
        instance_tags = {}
        try:
            for tag in resource['Tags']:
                try:
                    instance_tags[tag['Key']] = tag['Value']
                except KeyError as e:
                    print(str(e))
        except KeyError:
            pass

        for tag in tag_names:
            try:
                tag_value = instance_tags[tag]
            except KeyError:
                tag_value = ''
            instance_list.append(tag_value)
        
        tags_list.append(instance_list)

    return tags_list


def update_resource_tags(resource_id, ec2_client, tag_dict, dry_run=False, debugging=False):
    """Update/create resource instance tags"""
    tag_list = []
    for tag_name in tag_dict:
        tag_list.append(
            {
                'Key': tag_name,
                'Value': tag_dict[tag_name]
            }
        )
    try:
        response = ec2_client.create_tags(
            DryRun=dry_run,
            Resources=[
                resource_id
            ],
            Tags=tag_list
        )
    except botocore.exceptions.ClientError as e:
        if debugging:
            print(str(e))


def delete_resource_tags(resource_id, ec2_client, tag_name, tag_value=None, dry_run=False, debugging=False):
    """Delete resource instance tags"""
    ec2_args = {
        'DryRun': dry_run,
        'Resources': [resource_id],
        'Tags': [
            {
                'Key': tag_name
            }
        ]
    }
    if tag_value or tag_value == '':
        ec2_args['Tags'][0]['Value'] = tag_value

    try:
        response = ec2_client.delete_tags(**ec2_args)
    except botocore.exceptions.ClientError as e:
        if debugging:
            print(str(e))



# ELB Functions

def get_load_balancers(elb_client):
    """Return list of Elastic Load Balancers"""
    elb_args = {}
    load_balancers = []
    while True:
        response = elb_client.describe_load_balancers(**elb_args)
        try:
            for elb in response['LoadBalancers']:
                load_balancers.append(elb)
        except KeyError:
            for elb in response['LoadBalancerDescriptions']:
                load_balancers.append(elb)
        # Continue if response is truncated
        try:
            elb_args['Marker'] = response['NextMarker']
        except KeyError:
            break
    return load_balancers


def get_instance_states(load_balancers, elb_client):
    """Add/update the instance states for all load balancers"""
    for elb in load_balancers:
        try:
            response = elb_client.describe_instance_health(LoadBalancerName=elb['LoadBalancerName'])
        except AttributeError:
            continue
        try:
            elb['InstanceStates'] = response['InstanceStates']
        except KeyError:
            print('Error')
    return load_balancers


def get_target_info(load_balancers, elb_client):
    """Add/update target groups and health for all load balancers"""
    for elb in load_balancers:
        try:
            response = elb_client.describe_target_groups(LoadBalancerArn=elb['LoadBalancerArn'])
        except AttributeError:
            continue
        target_group = response['TargetGroups']
        for target in target_group:
            response = elb_client.describe_target_health(TargetGroupArn=target['TargetGroupArn'])
            target['TargetHealthDescriptions'] = response['TargetHealthDescriptions']
        elb['TargetGroups'] = target_group
    return load_balancers


def get_underutilized_elbs(load_balancers, utilization_level=0):
    """Generate a list of underutilized ELBs"""
    underutilized_elbs = []
    for elb in load_balancers:
        # ELBs
        try:
            if len(elb['InstanceStates']) <= utilization_level:
                underutilized_elbs.append(elb)
        except KeyError:
            pass
        # ELBs v2
        try:
            for target in elb['TargetGroups']:
                if len(target['TargetHealthDescriptions']) <= utilization_level:
                    underutilized_elbs.append(elb)
                    continue
        except KeyError:
            pass
    return underutilized_elbs


def get_underutilized_elbs2(load_balancers, utilization_level=0):
    """Generate a list of underutilized ELBs"""
    underutilized_elbs = []
    for elb in load_balancers:
        elb['Underutilized'] = False
        # ELBs
        try:
            elb['UtilizationLevel'] = len(elb['InstanceStates'])
            if len(elb['InstanceStates']) <= utilization_level:
                elb['Underutilized'] = True
        except KeyError:
            pass
        # ELBs v2
        try:
            for target in elb['TargetGroups']:
                if len(target['TargetHealthDescriptions']) <= utilization_level:
                    underutilized_elbs.append(elb)
                    continue
        except KeyError:
            pass
    return underutilized_elbs


def add_undertutilized_boolean(underutilized_elbs, all_elbs):
    """Add underutilized signifier to ELB list"""
    ulb_names = set()
    for elb in underutilized_elbs:
        ulb_names.add(elb['LoadBalancerName'])
    for elb in all_elbs:
        if elb['LoadBalancerName'] in ulb_names:
            elb['Underutilized'] = True
        else:
            elb['Underutilized'] = False
    return all_elbs


### Parser Functions

def ec2_resource_subparser(subparsers):
    """Create the subparser for EC2"""
    # EC2 resource parser
    ec2_resource_parser = subparsers.add_parser(
        'ec2',
        help='Query/modify EC2 info/tags from AWS'
    )

    # EC2 subparser
    ec2_subparser = ec2_resource_parser.add_subparsers(
        title='EC2 commands',
        description='(Command line options for EC2 resource)',
        help='Command help',
        dest='command'
    )

    # EC2 Query subparser
    ec2_subparser_query = ec2_subparser.add_parser(
        'query',
        help='Query EC2 information and tags'
    )
    ec2_subparser_query_type = ec2_subparser_query.add_mutually_exclusive_group()
    ec2_subparser_query_type.add_argument(
        '-i',
        '--input',
        action='store',
        help='Path to input file containing list of InstanceIds'
    )
    ec2_subparser_query.add_argument(
        '-H',
        '--header',
        action='store',
        help='Header of input file (defaults to InstanceId)',
        default='InstanceId'
    )
    ec2_subparser_query_type.add_argument(
        '-n',
        '--team-numbers',
        nargs='+',
        dest='numbers',
        help='List of team number to query'
    )
    ec2_subparser_query_type.add_argument(
        '-T',
        '--tag',
        action='store',
        help='Tag key to search for'
    )
    ec2_subparser_query.add_argument(
        '-V',
        '--values',
        nargs='+',
        help='Values to search for'
    )
    ec2_subparser_query.add_argument(
        '-e',
        '--empty',
        action='store_true',
        help='Include empty tag values (does not include untagged resources)',
        default=False
    )
    ec2_subparser_query.add_argument(
        '-t',
        '--tags',
        nargs='*',
        help='List of tags to query (defaults to all tags)'
    )
    ec2_subparser_query.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='Query all EC2 instances',
        default=False
    )

    # EC2 Update subparser
    ec2_subparser_update = ec2_subparser.add_parser(
        'update',
        help='Update EC2 tags'
    )
    ec2_subparser_update.add_argument(
        '-i',
        '--input',
        action='store',
        help='Path to input file containing list of InstanceIds',
        required=True
    )
    ec2_subparser_update.add_argument(
        '-t',
        '--tag',
        action='store',
        help='Tag key to update/set',
        required=True
    )
    ec2_subparser_update.add_argument(
        '-v',
        '--value',
        action='store',
        help='Value to set tag to',
        required=True
    )

    # EC2 Delete subparser
    ec2_subparser_delete = ec2_subparser.add_parser(
        'delete',
        help='Delete EC2 tags'
    )
    ec2_subparser_delete.add_argument(
        '-i',
        '--input',
        action='store',
        help='Path to input file containing list of InstanceIds',
        required=True
    )
    ec2_subparser_delete.add_argument(
        '-t',
        '--tag',
        action='store',
        help='Tag key to delete',
        required=True
    )
    ec2_subparser_delete_value = ec2_subparser_delete.add_mutually_exclusive_group()
    ec2_subparser_delete_value.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='Delete all tags with given name, regardless of value',
        default=False
    )
    ec2_subparser_delete_value.add_argument(
        '-v',
        '--value',
        action='store',
        help='Delete tag only if given value',
        default=''
    )

    # EC2 Configure subparser
    ec2_subparser_configure = ec2_subparser.add_parser(
        'configure',
        help='Configure EC2 tags using input file'
    )
    ec2_subparser_configure.add_argument(
        '-i',
        '--input',
        action='store',
        help='Path to CSV with desired tag configuration',
        required=True
    )
    ec2_subparser_configure.add_argument(
        '-d',
        '--delete',
        action='store_true',
        help='Delete tags without given values',
        default=False
    )


def ebs_resource_subparser(subparsers):
    """Create the subparser for EBS"""
    # EBS resource parser
    ebs_resource_parser = subparsers.add_parser(
        'ebs',
        help='Query/modify EBS info/tags from AWS'
    )

    # EBS subparser
    ebs_subparser = ebs_resource_parser.add_subparsers(
        title='EBS commands',
        description='(Command line options for EBS resource)',
        help='Command help',
        dest='command'
    )

    # EBS Query subparser
    ebs_subparser_query = ebs_subparser.add_parser(
        'query',
        help='Query EBS information and tags'
    )
    ebs_subparser_query_type = ebs_subparser_query.add_mutually_exclusive_group()
    ebs_subparser_query_type.add_argument(
        '-i',
        '--input',
        action='store',
        help='Path to input file containing list of InstanceIds'
    )
    ebs_subparser_query.add_argument(
        '-H',
        '--header',
        action='store',
        help='Header of input file (defaults to VolumeId)',
        default='VolumeId'
    )
    ebs_subparser_query_type.add_argument(
        '-n',
        '--team-numbers',
        nargs='+',
        dest='numbers',
        help='List of team number to query'
    )
    ebs_subparser_query_type.add_argument(
        '-T',
        '--tag',
        action='store',
        help='Tag key to search for'
    )
    ebs_subparser_query.add_argument(
        '-V',
        '--values',
        nargs='*',
        help='Values to search for'
    )
    ebs_subparser_query.add_argument(
        '-e',
        '--empty',
        action='store_true',
        help='Include empty tag values (does not include untagged resources)',
        default=False
    )
    ebs_subparser_query.add_argument(
        '-t',
        '--tags',
        nargs='*',
        help='List of tags to query (defaults to all tags)'
    )
    ebs_subparser_query.add_argument(
        '-u',
        '--unattached',
        action='store_true',
        help='Output unattached EBS volumes',
        default=False
    )
    ebs_subparser_query.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='Query all EC2 instances',
        default=False
    )

    # EBS Update subparser
    ebs_subparser_update = ebs_subparser.add_parser(
        'update',
        help='Update EBS tags'
    )
    ebs_subparser_update.add_argument(
        '-i',
        '--input',
        action='store',
        help='Path to input file containing list of InstanceIds',
        required=True
    )
    ebs_subparser_update.add_argument(
        '-t',
        '--tag',
        action='store',
        help='Tag key to update/set',
        required=True
    )
    ebs_subparser_update.add_argument(
        '-v',
        '--value',
        action='store',
        help='Value to set tag to',
        required=True
    )

    # EBS Delete subparser
    ebs_subparser_delete = ebs_subparser.add_parser(
        'delete',
        help='Delete EBS tags'
    )
    ebs_subparser_delete.add_argument(
        '-i',
        '--input',
        action='store',
        help='Path to input file containing list of InstanceIds',
        required=True
    )
    ebs_subparser_delete.add_argument(
        '-t',
        '--tag',
        action='store',
        help='Tag key to delete',
        required=True
    )
    ebs_subparser_delete_value = ebs_subparser_delete.add_mutually_exclusive_group()
    ebs_subparser_delete_value.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='Delete all tags with given name, regardless of value',
        default=False
    )
    ebs_subparser_delete_value.add_argument(
        '-v',
        '--value',
        action='store',
        help='Delete tag only if given value',
        default=''
    )

    # EBS Configure subparser
    ebs_subparser_configure = ebs_subparser.add_parser(
        'configure',
        help='Configure EBS tags using input file'
    )
    ebs_subparser_configure.add_argument(
        '-i',
        '--input',
        action='store',
        help='Path to CSV with desired tag configuration',
        required=True
    )
    ebs_subparser_configure.add_argument(
        '-d',
        '--delete',
        action='store_true',
        help='Delete tags without given values',
        default=False
    )


def elb_resource_subparser(subparsers):
    """Create the subparser for ELB"""
    # ELB resource parser
    elb_resource_parser = subparsers.add_parser(
        'elb',
        help='Query ELB info from AWS'
    )

    # ELB subparser
    elb_subparser = elb_resource_parser.add_subparsers(
        title='ELB commands',
        description='(Command line options for ELB resource)',
        help='Command help',
        dest='command'
    )

    # ELB Query subparser
    elb_subparser_query = elb_subparser.add_parser(
        'query',
        help='Query ELB information'
    )
    elb_subparser_query.add_argument(
        '-i',
        '--input',
        action='store',
        help='Path to input JSON file containing ELB data (will not pull data from AWS)'
    )
    elb_subparser_query.add_argument(
        '-n',
        '--team-numbers',
        nargs='+',
        dest='numbers',
        help='List of team number to query',
        default=''
    )
    '''
    elb_subparser_query.add_argument(
        '-t',
        '--tags',
        nargs='*',
        help='List of tags to query (defaults to all tags)'
    )
    elb_subparser_query.add_argument(
        '-T',
        '--target-info',
        action='store',
        help='Query health info of ELB targets'
    )
    '''
    elb_subparser_query.add_argument(
        '-u',
        '--underutilized',
        action='store_true',
        help='Output underutilized ELB information (will take some time)',
        default=False
    )
    elb_subparser_query.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='Output all ELB information',
        default=False
    )


def rds_resource_subparser(subparsers):
    """Create the subparser for RDS"""
    # RDS resource parser
    rds_resource_parser = subparsers.add_parser(
        'rds',
        help='Query RDS info from AWS'
    )

    # RDS subparser
    rds_subparser = rds_resource_parser.add_subparsers(
        title='RDS commands',
        description='(Command line options for RDS resource)',
        help='Command help',
        dest='command'
    )

    # RDS Query subparser
    rds_subparser_query = rds_subparser.add_parser(
        'query',
        help='Query RDS information'
    )
    # There are currently no command line arguements for rds query


### Main Function

def main():
    """Main function"""
    main_parser = argparse.ArgumentParser(description='Query resource information from AWS and modify/delete resource tags.')
    #'''
    main_parser.add_argument(
        '-p',
        '--profile',
        action='append',
        help='Use specific AWS profile (can be used multiple times, defaults to AWS_ACCOUNTS list)'
    )

    # AWS Resource subparser
    subparsers = main_parser.add_subparsers(
        title='AWS Resources',
        description='(AWS Resources to interact with)',
        help='Command help',
        dest='resource'
    )
    ec2_resource_subparser(subparsers)
    ebs_resource_subparser(subparsers)
    elb_resource_subparser(subparsers)
    rds_resource_subparser(subparsers)
    args = main_parser.parse_args()

    # Set AWS profiles
    try:
        if args.profile:
            aws_accounts = args.profile
        else:
            aws_accounts = AWS_ACCOUNTS
    except AttributeError:
        aws_accounts = AWS_ACCOUNTS

    # EC2
    if args.resource == 'ec2':
        # Query (EC2)
        if args.command == 'query':
            queries = []
            if args.input:
                instance_ids = get_ids_from_file(args.input, args.header)
                query = {}
                query['file_name_list'] = ['ec2', 'input']
                query['ec2_args'] = {'InstanceIds': instance_ids}
                queries.append(query)

            if args.numbers:
                for team_number in args.numbers:
                    query = {}
                    query['file_name_list'] = ['ec2', 'team' + str(team_number)]
                    query['ec2_args'] = generate_ec2_args(
                        'Name',
                        get_team_strings(team_number, regex=True)
                    )
                    queries.append(query)

            if args.tag:
                query = {}
                query['file_name_list'] = ['ec2', 'tag-' + args.tag]

                if args.values:
                    tag_values = args.values
                else:
                    tag_values = []

                if args.empty:
                    tag_values.append('')

                query['ec2_args'] = generate_ec2_args(
                    args.tag,
                    tag_values
                )
                queries.append(query)

            if args.all:
                query = {}
                query['file_name_list'] = ['ec2', 'all']
                query['ec2_args'] = {}
                queries.append(query)

            for query in queries:
                file_name_list = query['file_name_list']
                ec2_args = query['ec2_args']

                team_instances = []
                for aws_profile in aws_accounts:
                    print("Using account " + aws_profile + "...")
                    ec2_client = get_ec2_client(aws_profile)
                    if not ec2_client:
                        print("Could not generate EC2 client for " + aws_profile)
                        continue

                    team_instances = combine_resource_lists(
                        team_instances,
                        get_instances(ec2_args, ec2_client),
                        'InstanceId'
                    )

                team_instances = get_current_state(team_instances)

                info_headers = [
                    'InstanceId',
                    'Name',
                    'InstanceType',
                    'LaunchTime',
                    'PrivateIpAddress',
                    'OwnerId',
                    't_AppID',
                    'CurrentState'
                ]

                if args.tags:
                    for tag in args.tags:
                        if tag not in info_headers:
                            info_headers.append(tag)

                if args.tag:
                    if args.tag not in info_headers:
                        info_headers.append(args.tag)

                # Write team information file (CSV)
                output_data_to_file(
                    ['info'] + file_name_list,
                    'csv',
                    'EC2 information',
                    get_resource_info(team_instances, info_headers)
                )
                # Write team InstanceIds file (CSV)
                output_data_to_file(
                    ['ids'] + file_name_list,
                    'csv',
                    'EC2 InstanceIds',
                    get_resource_ids(team_instances, 'InstanceId')
                )
                # Write all team tags file (CSV)
                output_data_to_file(
                    ['all', 'tags'] + file_name_list,
                    'csv',
                    'all EC2 tags',
                    get_resource_tags(
                        team_instances,
                        get_all_tag_names(team_instances, True),
                        'InstanceId'
                    )
                )
                # Write specified team tags file (CSV)
                if args.tags:
                    output_data_to_file(
                        ['tags'] + file_name_list,
                        'csv',
                        'specified EC2 tags',
                        get_resource_tags(
                            team_instances,
                            args.tags,
                            'InstanceId'
                        )
                    )
                # Write raw info file (JSON)
                output_data_to_file(
                    ['data'] + file_name_list,
                    'json',
                    'EC2 data',
                    team_instances
                )

        # Update (EC2)
        if args.command == 'update':
            print("Updating tag " + args.tag + " to value " + args.value)
            new_tags = {args.tag: args.value}
            if args.input:
                instance_ids = get_ids_from_file(args.input, args.header)
            else:
                print("No instances given")
                return

            for aws_profile in aws_accounts:
                print("Using account " + aws_profile + "...")
                ec2_client = get_ec2_client(aws_profile)
                if not ec2_client:
                    print("Could not generate EC2 resource for " + aws_profile)
                    continue

                for instance_id in instance_ids:
                    update_resource_tags(
                        instance_id,
                        ec2_client,
                        new_tags
                    )

        # Delete (EC2)
        if args.command == 'delete':
            if args.value:
                print("Deleting tag " + args.tag + " with value " + args.value)
            elif args.value == '' and not args.all:
                print("Deleting blank tag " + args.tag)
            else:
                print("Deleting tag " + args.tag)

            instance_ids = get_ids_from_file(args.input, args.header)

            for aws_profile in aws_accounts:
                print("Using account " + aws_profile + "...")
                ec2_client = get_ec2_client(aws_profile)
                if not ec2_client:
                    print("Could not generate EC2 resource for " + aws_profile)
                    continue

                if args.all:
                    delete_value = None
                else:
                    delete_value = args.value
                for instance_id in instance_ids:
                    delete_resource_tags(
                        instance_id,
                        ec2_client,
                        args.tag,
                        delete_value
                    )

        # Configure (EC2)
        if args.command == 'configure':
            print("Updating tags from " + args.input + "...")

            desired_tags = {}
            with open(args.input) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        tag_names = row.copy()
                    else:
                        desired_tags[row[0]] = {}
                        t = 1
                        while t < len(row):
                            desired_tags[row[0]][tag_names[t]] = row[t]
                            t += 1
                    line_count += 1

            for aws_profile in aws_accounts:
                print("Using account " + aws_profile + "...")
                ec2_client = get_ec2_client(aws_profile)
                if not ec2_client:
                    print("Could not generate EC2 resource for " + aws_profile)
                    continue

                for instance in desired_tags:
                    new_tags = {}
                    delete_tags = []
                    for tag in desired_tags[instance]:
                        if desired_tags[instance][tag]:
                            new_tags[tag] = desired_tags[instance][tag]
                        if desired_tags[instance][tag] == '' and args.delete:
                            delete_tags.append(tag)

                    # Update instances tags
                    update_resource_tags(
                        instance,
                        ec2_client,
                        new_tags
                    )
                    # Delete any instance tags
                    for tag in delete_tags:
                        delete_resource_tags(
                            instance,
                            ec2_client,
                            tag
                        )

    # EBS
    if args.resource == 'ebs':
        # Query (EBS)
        if args.command == 'query':
            queries = []
            if args.input:
                volume_ids = get_ids_from_file(args.input, args.header)
                query = {}
                query['file_name_list'] = ['ebs', 'input']
                query['ec2_args'] = {'VolumeIds': volume_ids}
                queries.append(query)

            if args.numbers:
                for team_number in args.numbers:
                    query = {}
                    query['file_name_list'] = ['ebs', 'team' + str(team_number)]
                    query['ec2_args'] = generate_ec2_args(
                        'Name',
                        get_team_strings(team_number, regex=True)
                    )
                    queries.append(query)

            if args.tag:
                query = {}
                query['file_name_list'] = ['ebs', 'tag-' + args.tag]

                if args.values:
                    tag_values = args.values
                else:
                    tag_values = []

                if args.empty:
                    tag_values.append('')

                query['ec2_args'] = generate_ec2_args(
                    args.tag,
                    tag_values
                )
                queries.append(query)

            if args.all:
                query = {}
                query['file_name_list'] = ['ebs', 'all']
                query['ec2_args'] = {}
                queries.append(query)

            for query in queries:
                file_name_list = query['file_name_list']
                ec2_args = query['ec2_args']

                team_volumes = []
                for aws_profile in aws_accounts:
                    print("Using account " + aws_profile + "...")
                    ec2_client = get_ec2_client(aws_profile)
                    if not ec2_client:
                        print("Could not generate EC2 client for " + aws_profile)
                        continue

                    team_volumes = combine_resource_lists(
                        team_volumes,
                        get_volumes(ec2_args, ec2_client),
                        'VolumeId'
                    )

                team_volumes = get_current_state(team_volumes)

                info_headers = [
                    'VolumeId',
                    'Name',
                    'Size',
                    'VolumeType',
                    'CurrentState'
                ]

                if args.tags:
                    for tag in args.tags:
                        if tag not in info_headers:
                            info_headers.append(tag)

                if args.tag:
                    if args.tag not in info_headers:
                        info_headers.append(args.tag)

                if args.unattached:
                    unattached_team_volumes = []
                    for volume in team_volumes:
                        if volume['State'] != 'in-use':
                            unattached_team_volumes.append(volume)

                    # Write unattached team info (CSV)
                    output_data_to_file(
                        ['unattached', 'info'] + file_name_list,
                        'csv',
                        'unattached EBS information',
                        get_resource_info(unattached_team_volumes, info_headers)
                    )
                    # Write unattached team VolumeIds file (CSV)
                    output_data_to_file(
                        ['unattached', 'ids'] + file_name_list,
                        'csv',
                        'unattached EBS VolumeIds',
                        get_resource_ids(unattached_team_volumes, 'VolumeId')
                    )
                    # Write all unattached team tags file (CSV)
                    output_data_to_file(
                        ['unattached', 'all', 'tags'] + file_name_list,
                        'csv',
                        'all unattached EBS tags',
                        get_resource_tags(
                            unattached_team_volumes,
                            get_all_tag_names(unattached_team_volumes, True),
                            'VolumeId'
                        )
                    )
                    # Write specified unattached team tags file (CSV)
                    if args.tags:
                        output_data_to_file(
                            ['unattached', 'tags'] + file_name_list,
                            'csv',
                            'specified unattached EBS tags',
                            get_resource_tags(
                                unattached_team_volumes,
                                args.tags,
                                'VolumeId'
                            )
                        )

                # All EBS data
                # Write team info file (CSV)
                output_data_to_file(
                    ['info'] + file_name_list,
                    'csv',
                    'EBS information',
                    get_resource_info(team_volumes, info_headers)
                )
                # Write team VolumeIds file (CSV)
                output_data_to_file(
                    ['ids'] + file_name_list,
                    'csv',
                    'EBS VolumeIds',
                    get_resource_ids(team_volumes, 'VolumeId')
                )
                # Write all team tags file (CSV)
                output_data_to_file(
                    ['all', 'tags'] + file_name_list,
                    'csv',
                    'all EBS tags',
                    get_resource_tags(
                        team_volumes,
                        get_all_tag_names(team_volumes, True),
                        'VolumeId'
                    )
                )
                # Write specified team tags file (CSV)
                if args.tags:
                    output_data_to_file(
                        ['tags'] + file_name_list,
                        'csv',
                        'specified EBS tags',
                        get_resource_tags(
                            team_volumes,
                            args.tags,
                            'VolumeId'
                        )
                    )
                # Write raw info file (JSON)
                output_data_to_file(
                    ['data'] + file_name_list,
                    'json',
                    'EBS data',
                    team_volumes
                )

        # Update (EBS)
        if args.command == 'update':
            print("Updating tag " + args.tag + " to value " + args.value)
            new_tags = {args.tag: args.value}
            if args.input:
                volume_ids = get_ids_from_file(args.input, args.header)
            else:
                print("No volumes given")
                return

            for aws_profile in aws_accounts:
                print("Using account " + aws_profile + "...")
                ec2_client = get_ec2_client(aws_profile)
                if not ec2_client:
                    print("Could not generate EC2 resource for " + aws_profile)
                    continue

                for volume_id in volume_ids:
                    update_resource_tags(
                        volume_id,
                        ec2_client,
                        new_tags
                    )

        # Delete (EBS)
        if args.command == 'delete':
            if args.value:
                print("Deleting tag " + args.tag + " with value " + args.value)
            elif args.value == '' and not args.all:
                print("Deleting blank tag " + args.tag)
            else:
                print("Deleting tag " + args.tag)

            volume_ids = get_ids_from_file(args.input, args.header)

            for aws_profile in aws_accounts:
                print("Using account " + aws_profile + "...")
                ec2_client = get_ec2_client(aws_profile)
                if not ec2_client:
                    print("Could not generate EC2 resource for " + aws_profile)
                    continue

                if args.all:
                    delete_value = None
                else:
                    delete_value = args.value
                for volume_id in volume_ids:
                    delete_resource_tags(
                        volume_id,
                        ec2_client,
                        args.tag,
                        delete_value
                    )

        # Configure (EBS)
        if args.command == 'configure':
            print("Updating tags from " + args.input + "...")

            desired_tags = {}
            with open(args.input) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        tag_names = row.copy()
                    else:
                        desired_tags[row[0]] = {}
                        t = 1
                        while t < len(row):
                            desired_tags[row[0]][tag_names[t]] = row[t]
                            t += 1
                    line_count += 1

            for aws_profile in aws_accounts:
                print("Using account " + aws_profile + "...")
                ec2_client = get_ec2_client(aws_profile)
                if not ec2_client:
                    print("Could not generate EC2 resource for " + aws_profile)
                    continue

                for instance in desired_tags:
                    new_tags = {}
                    delete_tags = []
                    for tag in desired_tags[instance]:
                        if desired_tags[instance][tag]:
                            new_tags[tag] = desired_tags[instance][tag]
                        if desired_tags[instance][tag] == '' and args.delete:
                            delete_tags.append(tag)

                    # Update instances tags
                    update_resource_tags(
                        instance,
                        ec2_client,
                        new_tags
                    )
                    # Delete any instance tags
                    for tag in delete_tags:
                        delete_resource_tags(
                            instance,
                            ec2_client,
                            tag
                        )

    # ELB
    if args.resource == 'elb':
        # Query (ELB)
        if args.command == 'query':
            if args.input:
                with open(args.input) as json_file:
                    load_balancers = json.load(json_file)
            else:
                load_balancers = {'elb': [], 'elbv2': []}
                for aws_profile in aws_accounts:
                    print("Using account " + aws_profile + "...")

                    # Classic ELB
                    elb_client = get_elb_client(aws_profile, v2=False)
                    if not elb_client:
                        print("Could not generate EC2 client for " + aws_profile)
                        continue

                    elbs = get_load_balancers(elb_client)
                    if args.underutilized:
                        print("Getting instance states...")
                        elbs = get_instance_states(elbs, elb_client)
                    load_balancers['elb'] = combine_resource_lists(
                        load_balancers['elb'],
                        elbs,
                        'LoadBalancerName'
                    )
                    # ELB v2
                    elb_client = get_elb_client(aws_profile, v2=True)
                    elbs = get_load_balancers(elb_client)
                    if args.underutilized:
                        print("Getting target info...")
                        elbs = get_target_info(elbs, elb_client)
                    load_balancers['elbv2'] = combine_resource_lists(
                        load_balancers['elbv2'],
                        elbs,
                        'LoadBalancerName'
                    )

            t = 0
            team_numbers = args.numbers
            while t < len(team_numbers) + 1:
                team_load_balancers = {'elb': [], 'elbv2': []}

                for elb_version in load_balancers:
                    try:
                        team_strings = get_team_strings(team_numbers[t])
                        file_name_list = [elb_version, 'team' + str(team_numbers[t])]
                        for elb in load_balancers[elb_version]:
                            for string in team_strings:
                                if string in elb['LoadBalancerName']:
                                    team_load_balancers[elb_version].append(elb)
                                    break
                    except IndexError:
                        if not args.all:
                            break
                        team_load_balancers = load_balancers
                        file_name_list = [elb_version, 'all']

                    if elb_version == 'elb':
                        info_headers = [
                            'LoadBalancerName',
                            'DNSName',
                            'VpcId'
                        ]
                    else:
                        team_load_balancers[elb_version] = get_current_state(team_load_balancers[elb_version])
                        info_headers = [
                            'LoadBalancerName',
                            'DNSName',
                            'VpcId',
                            'Type',
                            'LoadBalancerArn',
                            'CurrentState'
                        ]
                    if args.underutilized:
                        team_load_balancers[elb_version] = add_undertutilized_boolean(
                            get_underutilized_elbs(team_load_balancers[elb_version]),
                            team_load_balancers[elb_version]
                        )
                        info_headers += ['Underutilized']
                    
                    # Write ELB information
                    output_data_to_file(
                        ['info'] + file_name_list,
                        'csv',
                        'ELB information',
                        get_resource_info(
                            team_load_balancers[elb_version],
                            info_headers
                        )
                    )
                    # Write underutilized ELB information
                    if args.underutilized:
                        output_data_to_file(
                            ['underutilized', 'info'] + file_name_list,
                            'csv',
                            'underutilized ELB information',
                            get_resource_info(
                                get_underutilized_elbs(team_load_balancers[elb_version]),
                                info_headers
                            )
                        )

                    # Write ELB names file (CSV)
                    output_data_to_file(
                        ['names'] + file_name_list,
                        'csv',
                        'ELB names',
                        get_resource_ids(team_load_balancers[elb_version], 'LoadBalancerName')
                    )
                    # Write underutilized ELB names
                    if args.underutilized:
                        output_data_to_file(
                            ['underutilized', 'names'] + file_name_list,
                            'csv',
                            'underutilized ELB names',
                            get_resource_ids(
                                get_underutilized_elbs(team_load_balancers[elb_version]),
                                'LoadBalancerName'
                            )
                        )

                t += 1

            # Write all raw info file (JSON)
            output_data_to_file(
                ['data', 'elastic_load_balancers'],
                'json',
                'all ELB data',
                load_balancers
            )

    # RDS
    if args.resource == 'rds':
        # Query (RDS)
        if args.command == 'query':
            rds_instances = []
            for aws_profile in aws_accounts:
                print("Using account " + aws_profile + "...")
                rds_client = get_aws_client(aws_profile, 'rds')
                if not rds_client:
                    print("Could not generate EC2 client for " + aws_profile)
                    continue

                rds_instances = combine_resource_lists(
                    rds_instances,
                    get_rds_resources(rds_client),
                    'DBInstanceIdentifier'
                )

            info_headers = [
                'DBInstanceIdentifier',
                'DBInstanceClass',
                'Engine',
                'EngineVersion',
                'MasterUsername',
                'DBName',
                'DBInstanceArn',
                'AllocatedStorage',
                'DBInstanceStatus',
                'InstanceCreateTime',
                'AvailabilityZone',
                'MultiAZ',
                'PubliclyAccessible',
                'StorageEncrypted'
            ]

            file_name_list = ['rds']

            # Write RDS information file (CSV)
            output_data_to_file(
                ['info'] + file_name_list,
                'csv',
                'RDS information',
                get_resource_info(rds_instances, info_headers)
            )
            # Write team InstanceIds file (CSV)
            output_data_to_file(
                ['ids'] + file_name_list,
                'csv',
                'RDS InstanceIds',
                get_resource_ids(rds_instances, 'DBInstanceIdentifier')
            )
            # Write raw info file (JSON)
            output_data_to_file(
                ['data'] + file_name_list,
                'json',
                'RDS data',
                rds_instances
            )





if __name__ == "__main__":
    main()
