import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError
from werkzeug.utils import secure_filename
import uuid

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is required")
    
    def upload_file(self, file_obj, user_id, original_filename, content_type):
        """
        Upload file to S3 bucket.
        
        Args:
            file_obj: File object to upload
            user_id: ID of the user uploading the file
            original_filename: Original name of the file
            content_type: MIME type of the file
            
        Returns:
            dict: Contains 's3_key' and 's3_url' on success
            
        Raises:
            Exception: If upload fails
        """
        try:
            # Generate unique filename
            file_extension = os.path.splitext(original_filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            s3_key = f"images/{user_id}/{unique_filename}"
            
            # Upload file
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read'
                }
            )
            
            # Generate public URL
            s3_url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{s3_key}"
            
            return {
                's3_key': s3_key,
                's3_url': s3_url
            }
            
        except NoCredentialsError:
            raise Exception("AWS credentials not found")
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")
    
    def delete_file(self, s3_key):
        """
        Delete file from S3 bucket.
        
        Args:
            s3_key: S3 key of the file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception as e:
            print(f"Failed to delete file from S3: {str(e)}")
            return False
    
    def generate_presigned_url(self, s3_key, expiration=3600):
        """
        Generate a presigned URL for private file access.
        
        Args:
            s3_key: S3 key of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def file_exists(self, s3_key):
        """
        Check if file exists in S3 bucket.
        
        Args:
            s3_key: S3 key to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False