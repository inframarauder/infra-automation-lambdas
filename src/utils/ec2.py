import boto3


def cleanup():
    print("**CLEANING UP EC2 INSTANCES**")

    ec2 = boto3.resource("ec2")

    # iterate over instances in all regions
    regions = ec2.meta.client.describe_regions()["Regions"]

    for region in regions:
        region_name = region["RegionName"]

        # check for running instances with tag 'AutoCleanup'= true and terminate them
        client = boto3.client("ec2", region_name=region_name)
        filters = [
            {"Name": "tag:AutoCleanup", "Values": ["true"]},
            {"Name": "instance-state-name", "Values": ["running"]},
        ]
        res = client.describe_instances(Filters=filters)
        reservations = res["Reservations"]

        if len(reservations) > 0:
            for reservation in res["Reservations"]:
                instances = reservation["Instances"]
                print(
                    "Terminating %d instances in region: %s"
                    % (len(instances), region_name),
                )
                for instance in instances:
                    instance_id = instance["InstanceId"]
                    instance_type = instance["InstanceType"]

                    print(
                        "Instance %s of type %s terminated"
                        % (instance_id, instance_type)
                    )
                    client.terminate_instances(InstanceIds=[instance_id])
        else:
            print("No instances to terminate in region: %s" % region_name)
