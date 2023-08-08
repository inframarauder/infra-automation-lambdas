import boto3

def ec2_cleanup():
    ec2 = boto3.resource('ec2')

    print("**CLEANING UP EC2 INSTANCES**")

    # iterate over instances in all regions 
    regions = ec2.describe_regions().get('Regions',[] )

    for region in regions :
        region_name=region['RegionName']
        print("Checking Region: %s " % region_name)

        # check for instances with tag 'AutoCleanup'= true and terminate them
        client = boto3.client('ec2', region_name=region_name)
        tag_filter = [
            {
                'Name': 'tag:AutoCleanup',  
                'Values': ['true']
            }
        ]
        res = client.describe_instances(Filters=tag_filter)
        termination_count = 0
        for reservation in res['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']

                print("Terminating instance: %s of type %s" % (instance_id, instance_type))
                client.terminate_instances(InstanceIds=[instance_id])
                termination_count += 1
        
        if termination_count == 0:
            print("No instances to terminate in region: %s" % region_name)
        else:
            print("Terminated %d instances in region: %s" % (termination_count, region_name))



def handler(event, context):
    ec2_cleanup()
