import boto3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

AUTO_DESTROY_TAG = {'Key': 'auto-destroy', 'Value': 'true'}

def get_all_regions(service_name):
    ec2 = boto3.client('ec2')
    regions = [r['RegionName'] for r in ec2.describe_regions()['Regions']]
    return regions

def terminate_ec2_instances():
    logger.info("====Scanning for EC2 instances with auto-destroy tag===")
    regions = get_all_regions('ec2')
    found = False
    for region in regions:
        ec2 = boto3.resource('ec2', region_name=region)
        instances = list(ec2.instances.filter(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running']},
                {'Name': f'tag:{AUTO_DESTROY_TAG["Key"]}', 'Values': [AUTO_DESTROY_TAG["Value"]]}
            ]
        ))
        if instances:
            found = True
            for instance in instances:
                logger.info(f"Terminating EC2 instance {instance.id} in {region}")
                instance.terminate()
        else:
            logger.info(f"No EC2 instances to terminate in {region}")
    if not found:
        logger.info("No EC2 instances found with auto-destroy tag.")

def delete_eks_clusters():
    logger.info("===Scanning for EKS clusters with auto-destroy tag===")
    regions = get_all_regions('eks')
    found = False
    for region in regions:
        eks = boto3.client('eks', region_name=region)
        clusters = eks.list_clusters()['clusters']
        for cluster_name in clusters:
            tags = eks.list_tags_for_resource(
                resourceArn=f'arn:aws:eks:{region}:{boto3.client("sts").get_caller_identity()["Account"]}:cluster/{cluster_name}'
            )['tags']
            if tags.get(AUTO_DESTROY_TAG['Key']) == AUTO_DESTROY_TAG['Value']:
                found = True
                logger.info(f"Deleting EKS cluster {cluster_name} in {region}")
                eks.delete_cluster(name=cluster_name)
        if not clusters:
            logger.info(f"No EKS clusters found in {region}")
    if not found:
        logger.info("No EKS clusters found with auto-destroy tag.")

def delete_ecs_clusters():
    logger.info("===Scanning for ECS clusters with auto-destroy tag===")
    regions = get_all_regions('ecs')
    found = False
    for region in regions:
        ecs = boto3.client('ecs', region_name=region)
        cluster_arns = ecs.list_clusters()['clusterArns']
        for arn in cluster_arns:
            tags = ecs.list_tags_for_resource(resourceArn=arn)['tags']
            tag_dict = {tag['key']: tag['value'] for tag in tags}
            if tag_dict.get(AUTO_DESTROY_TAG['Key']) == AUTO_DESTROY_TAG['Value']:
                found = True
                logger.info(f"Deleting ECS cluster {arn} in {region}")
                # Must delete all services first
                services = ecs.list_services(cluster=arn)['serviceArns']
                for service_arn in services:
                    logger.info(f"Deleting ECS service {service_arn} in cluster {arn}")
                    ecs.update_service(cluster=arn, service=service_arn, desiredCount=0)
                    ecs.delete_service(cluster=arn, service=service_arn, force=True)
                ecs.delete_cluster(cluster=arn)
        if not cluster_arns:
            logger.info(f"No ECS clusters found in {region}")
    if not found:
        logger.info("No ECS clusters found with auto-destroy tag.")

def delete_ebs_volumes():
    logger.info("===Scanning for EBS volumes with auto-destroy tag===")
    regions = get_all_regions('ec2')
    found = False
    for region in regions:
        ec2 = boto3.resource('ec2', region_name=region)
        volumes = list(ec2.volumes.filter(
            Filters=[
                {'Name': f'tag:{AUTO_DESTROY_TAG["Key"]}', 'Values': [AUTO_DESTROY_TAG["Value"]]}
            ]
        ))
        if volumes:
            found = True
            for volume in volumes:
                logger.info(f"Deleting EBS volume {volume.id} in {region}")
                try:
                    volume.delete()
                except Exception as e:
                    logger.error(f"Failed to delete volume {volume.id}: {e}")
        else:
            logger.info(f"No EBS volumes to delete in {region}")
    if not found:
        logger.info("No EBS volumes found with auto-destroy tag.")

def handler(event, context):
    terminate_ec2_instances()
    delete_eks_clusters()
    delete_ecs_clusters()
    delete_ebs_volumes()
    logger.info("Cleanup complete.")

if __name__ == "__main__":
    handler(None, None)