This file is dedicated to describe all the assumptions made for each assessment question

Assumptions for create shared directory:
	The developers are part of a Unix group called developers.
	SSH/SFTP access is already configured for all developers.
	The script is executed with sudo or by a user with appropriate permissions to change ownership and permissions of directories and files.

Assumptions for lambda function:
	AWS Lambda function has the necessary IAM role permissions to create EC2 instances and S3 buckets.
	The VPC, SUBNET, SG ID is provided as a constant variable.
	The script will be executed with the necessary AWS credentials and region configuration.

Assumptions for Jenkin pipeline:
	Jenkins is already setup in the aws