# tf-cloud-destoy-lambda

This is an AWS Lambda function that will trigger a destroy run on Terraform Cloud. It is deployed as a cron job and runs everyday at 5.30AM IST.

- searches for all workspaces with the tag `auto-destroy` in the organization
- checks if the workspace has any resources
- triggers a destroy run if the workspace has resources
