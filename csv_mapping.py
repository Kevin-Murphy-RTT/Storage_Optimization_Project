#!/usr/local/bin/python3
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


if __name__ == "__main__":
    main()
