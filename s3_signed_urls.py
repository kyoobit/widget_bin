#!/usr/bin/env python3

from argparse import ArgumentParser

# https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
import boto3
from botocore.exceptions import NoCredentialsError

# uv: An extremely fast Python package and project manager
# Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# Install latest python (3.13): uv python install
# Create a virtual environment: uv venv
# Add required libraries: uv pip install --upgrade boto3
#
# export AWS_ACCESS_KEY_ID=<YOUR_ACCESS_KEY_ID>
# export AWS_SECRET_ACCESS_KEY=<YOUR_SECRET_ACCESS_KEY>
# uv run python s3_signed_urls.py --help

def generate_presigned_url(bucket_name:str, object_key:str, expiration:int) -> str:
    """Generate and return a presigned_url"""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_url.html
    try:
        s3_client = boto3.client('s3')
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration,
            )
        return response
    except NoCredentialsError:
        print("Credentials not available")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('object_keys', metavar='<path>', nargs='+')
    parser.add_argument('--bucket', '-B', dest='bucket_name', default='some-bucket-prefix')
    parser.add_argument('--expire', dest='expiration', type=int, default=84600)
    args = parser.parse_args()
    for object_key in args.object_keys:
        presigned_url = generate_presigned_url(args.bucket_name, object_key, args.expiration)
        print(presigned_url)
