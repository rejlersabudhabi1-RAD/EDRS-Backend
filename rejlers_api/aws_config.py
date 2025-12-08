"""
AWS Configuration for Rejlers AI-Powered ERP System
Handles AWS services integration including S3, SES, and CloudWatch
"""

import os
from django.conf import settings
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import logging

logger = logging.getLogger(__name__)

class AWSConfig:
    """
    AWS Configuration and Service Manager
    """
    
    def __init__(self):
        # AWS Credentials
        self.access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = os.getenv('AWS_DEFAULT_REGION', 'eu-north-1')
        
        # SES Configuration
        self.ses_access_key_id = os.getenv('AWS_SES_ACCESS_KEY_ID')
        self.ses_secret_access_key = os.getenv('AWS_SES_SECRET_ACCESS_KEY')
        
        # S3 Configuration
        self.s3_bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME', 'rejlers-erp-storage')
        
        # Initialize clients
        self._s3_client = None
        self._ses_client = None
        self._cloudwatch_client = None
    
    @property
    def s3_client(self):
        """Initialize and return S3 client"""
        if self._s3_client is None:
            try:
                self._s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                    region_name=self.region_name
                )
                logger.info("AWS S3 client initialized successfully")
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                raise
        return self._s3_client
    
    @property
    def ses_client(self):
        """Initialize and return SES client"""
        if self._ses_client is None:
            try:
                self._ses_client = boto3.client(
                    'ses',
                    aws_access_key_id=self.ses_access_key_id,
                    aws_secret_access_key=self.ses_secret_access_key,
                    region_name=self.region_name
                )
                logger.info("AWS SES client initialized successfully")
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to initialize SES client: {e}")
                raise
        return self._ses_client
    
    @property
    def cloudwatch_client(self):
        """Initialize and return CloudWatch client"""
        if self._cloudwatch_client is None:
            try:
                self._cloudwatch_client = boto3.client(
                    'logs',
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                    region_name=self.region_name
                )
                logger.info("AWS CloudWatch client initialized successfully")
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to initialize CloudWatch client: {e}")
                raise
        return self._cloudwatch_client
    
    def test_s3_connection(self):
        """Test S3 connection and permissions"""
        try:
            # List buckets to test connection
            response = self.s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            
            # Check if our bucket exists
            if self.s3_bucket_name in buckets:
                logger.info(f"✅ S3 bucket '{self.s3_bucket_name}' found and accessible")
                return True, f"S3 connection successful. Bucket '{self.s3_bucket_name}' is accessible."
            else:
                logger.warning(f"⚠️ S3 bucket '{self.s3_bucket_name}' not found in available buckets: {buckets}")
                return False, f"Bucket '{self.s3_bucket_name}' not found. Available buckets: {buckets}"
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"❌ S3 connection failed: {error_code} - {error_message}")
            return False, f"S3 connection failed: {error_message}"
        except Exception as e:
            logger.error(f"❌ Unexpected S3 error: {e}")
            return False, f"Unexpected S3 error: {str(e)}"
    
    def test_ses_connection(self):
        """Test SES connection and sending capabilities"""
        try:
            # Get SES sending quota to test connection
            response = self.ses_client.get_send_quota()
            
            # Get verified email addresses
            identities = self.ses_client.list_verified_email_addresses()
            
            quota_info = {
                'max_24_hour': response.get('Max24HourSend', 0),
                'max_send_rate': response.get('MaxSendRate', 0),
                'sent_last_24_hours': response.get('SentLast24Hours', 0)
            }
            
            verified_emails = identities.get('VerifiedEmailAddresses', [])
            
            logger.info(f"✅ SES connection successful. Quota: {quota_info}")
            return True, {
                'status': 'SES connection successful',
                'quota': quota_info,
                'verified_emails': verified_emails
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"❌ SES connection failed: {error_code} - {error_message}")
            return False, f"SES connection failed: {error_message}"
        except Exception as e:
            logger.error(f"❌ Unexpected SES error: {e}")
            return False, f"Unexpected SES error: {str(e)}"
    
    def send_test_email(self, to_email, from_email=None):
        """Send a test email to verify SES functionality"""
        if not from_email:
            from_email = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@rejlers.com')
        
        try:
            response = self.ses_client.send_email(
                Destination={
                    'ToAddresses': [to_email],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': 'UTF-8',
                            'Data': '''
                            <html>
                            <body>
                            <h2>🎉 Rejlers AI-Powered ERP System - AWS Connection Test</h2>
                            <p>Congratulations! Your AWS SES integration is working correctly.</p>
                            <p><strong>System Details:</strong></p>
                            <ul>
                                <li>✅ AWS SES Connection: Active</li>
                                <li>✅ Email Delivery: Functional</li>
                                <li>✅ AI-Powered ERP System: Ready</li>
                            </ul>
                            <p>Your Oil & Gas engineering platform is now connected to AWS services.</p>
                            <hr>
                            <small>Generated by Rejlers AI-Powered ERP System</small>
                            </body>
                            </html>
                            ''',
                        },
                        'Text': {
                            'Charset': 'UTF-8',
                            'Data': 'Rejlers AI-Powered ERP System - AWS SES connection test successful! Your system is ready for Oil & Gas engineering tasks.',
                        },
                    },
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': '✅ Rejlers AI-ERP: AWS Connection Test Successful',
                    },
                },
                Source=from_email,
            )
            
            message_id = response['MessageId']
            logger.info(f"✅ Test email sent successfully. MessageId: {message_id}")
            return True, f"Test email sent successfully to {to_email}. MessageId: {message_id}"
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"❌ Failed to send test email: {error_code} - {error_message}")
            return False, f"Failed to send test email: {error_message}"
        except Exception as e:
            logger.error(f"❌ Unexpected email error: {e}")
            return False, f"Unexpected email error: {str(e)}"

# Global AWS configuration instance
aws_config = AWSConfig()