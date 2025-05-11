# infra-automation-lambdas

These are a collection of AWS Lambda functions that automate various infrastructure tasks in my personal projects/experiments. The functions are deployed using AWS SAM.
The functions are described below:

## terraform-cloud-apply

    This is an AWS Lambda function that will trigger an apply run on Terraform Cloud. It is deployed as a cron job and runs everyday at 5.00AM IST.

    - searches for all workspaces with the tag `auto-apply` in the organization
    - checks if the workspace has any resources
    - triggers an apply run if the workspace has resources

## aws-cleanup

    This is an AWS Lambda function that will clean up unused resources in the AWS account using boto3. It is deployed as a cron job and runs everyday at 6.00AM IST. Works on resources tagged with `auto-destroy` tag set to `true`. The function will check for the following resources:
    - EC2 instances
    - EBS volumes
    - EKS clusters
    - ECS clusters
