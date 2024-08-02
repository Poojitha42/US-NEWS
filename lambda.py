import boto3
import time

# Constants
VPC_ID = 'vpc-xxxxxxxx'  # Assuming the vpcid as vpc-xxxxxxxx
SUBNET_ID = 'subnet-xxxxxxxx'  # Assuming the subnetid as subnet-xxxxxxxx
SECURITY_GROUP_ID = 'sg-xxxxxxxx'  # Assuming the SG id as sg-xxxxxxxx
YOUR_NAME = 'pooja'  

# Create AWS clients
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')

# Function to get the latest ECS optimized AMI
def get_latest_ecs_ami():
    try:
        response = ec2_client.describe_images(
            Owners=['amazon'],
            Filters=[
                {'Name': 'name', 'Values': ['amzn2-ami-ecs-hvm-*-x86_64-ebs']},
                {'Name': 'state', 'Values': ['available']}
            ]
        )
        images = response['Images']
        latest_image = max(images, key=lambda x: x['CreationDate'])
        return latest_image['ImageId']
    except Exception as e:
        print(f"Error getting latest ECS AMI: {e}")
        raise

# Function to create EC2 instances
def create_ec2_instances(ami_id):
    instance_ids = []
    for i in range(1, 11):
        instance_name = f'myinstance{i}'
        try:
            response = ec2_client.run_instances(
                ImageId=ami_id,
                InstanceType='t3.micro',
                MaxCount=1,
                MinCount=1,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [{'Key': 'Name', 'Value': instance_name}]
                    }
                ],
                NetworkInterfaces=[
                    {
                        'AssociatePublicIpAddress': True,
                        'DeviceIndex': 0,
                        'SubnetId': SUBNET_ID,
                        'Groups': [SECURITY_GROUP_ID]
                    }
                ]
            )
            instance_id = response['Instances'][0]['InstanceId']
            instance_ids.append(instance_id)
            print(f'Created instance {instance_name} with ID {instance_id}')
        except Exception as e:
            print(f"Error creating instance {instance_name}: {e}")
            continue
    return instance_ids

# Function to create S3 buckets and upload respective instance IDs
def create_s3_buckets_and_upload_ids(instance_ids):
    for i, instance_id in enumerate(instance_ids, start=1):
        bucket_name = f'{YOUR_NAME}-mys3bucket{i}'
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            print(f'Created S3 bucket: {bucket_name}')
            
            file_name = f'instance{i}_id.txt'
            with open(f'/tmp/{file_name}', 'w') as file:
                file.write(instance_id)
            
            s3_client.upload_file(f'/tmp/{file_name}', bucket_name, file_name)
            print(f'Uploaded instance ID {instance_id} to {bucket_name}/{file_name}')
        except Exception as e:
            print(f"Error creating bucket or uploading file to {bucket_name}: {e}")

# Main handler function for AWS Lambda
def lambda_handler(event, context):
    try:
        ami_id = get_latest_ecs_ami()
        instance_ids = create_ec2_instances(ami_id)
        if not instance_ids:
            raise Exception("No EC2 instances were created.")
        time.sleep(60)  # Wait for instances to be ready
        create_s3_buckets_and_upload_ids(instance_ids)
        return {
            'statusCode': 200,
            'body': 'Successfully created EC2 instances and S3 buckets.'
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': f'Error: {e}'
        }
