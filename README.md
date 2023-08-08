# aws-cleanup-lambda

A lambda function cron job to run daily at 5.30AM IST (12.00AM UTC) to cleanup AWS resources (EC2 instances).
The resources eligible for cleanup must have the tag `AutoCleanup` with value `true`.
