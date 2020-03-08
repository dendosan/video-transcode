'''
You need to have AWS credentials in ~/.aws/credentials
[default]
aws_access_key_id=KEY_ID
aws_secret_access_key=ACCESS_KEY
'''

import boto3
from botocore.exceptions import ClientError

ORIGINALS_BUCKET = "originalvideos"
MODIFIED_BUCKET = "modifiedvideos"


def upload_file(file_name, bucket):
    """
    Function to upload a file to an S3 bucket
    """
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)

    return response


def download_file(file_name, bucket):
    """
    Function to download a given file from an S3 bucket
    """
    s3 = boto3.resource('s3')
    output = f"downloads/{file_name}"
    print(f"file_name is {file_name}")
    print(f"output is {output}")
    s3.Bucket(bucket).download_file(f"uploads/{file_name}", output)

    return output


def list_files(bucket):
    """
    Function to list files in a given S3 bucket
    """
    s3 = boto3.client('s3')
    contents = []
    try:
        for item in s3.list_objects(Bucket=bucket)['Contents']:
            if bucket == ORIGINALS_BUCKET:
                contents.append(item['Key'])
            else:
                # https://modifiedvideos.s3.amazonaws.com/uploads/SampleVideos2.mp4
                print(item['Key'])
                url = "https://%s.s3.amazonaws.com/%s" % (bucket, item['Key'])
                print(url)
                contents.append(url)
    except Exception:
        pass

    return contents
