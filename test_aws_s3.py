"""
AWS S3 Connection Test Script
Tests connection to AWS S3 and lists/creates bucket
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rejlers_api.settings')
django.setup()

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from decouple import config

def test_aws_credentials():
    """Test AWS credentials"""
    print("\n" + "="*70)
    print("  AWS S3 CONNECTION TEST")
    print("="*70 + "\n")
    
    # Get credentials from environment
    access_key = config('AWS_ACCESS_KEY_ID', default='')
    secret_key = config('AWS_SECRET_ACCESS_KEY', default='')
    region = config('AWS_DEFAULT_REGION', default='ap-south-1')
    bucket_name = config('AWS_STORAGE_BUCKET_NAME', default='rejlers-edrs-project')
    
    print(f"📋 Configuration:")
    print(f"   Access Key ID: {access_key[:10]}...{access_key[-4:] if len(access_key) > 14 else 'NOT SET'}")
    print(f"   Region: {region}")
    print(f"   Bucket Name: {bucket_name}\n")
    
    if not access_key or access_key.startswith('dummy'):
        print("❌ ERROR: AWS credentials not configured!")
        return False
    
    try:
        # Initialize S3 client
        print("🔄 Initializing S3 client...")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        print("✅ S3 client initialized successfully!\n")
        
        # Test 1: List all buckets
        print("🔄 Testing connection - Listing buckets...")
        response = s3_client.list_buckets()
        buckets = response.get('Buckets', [])
        
        print(f"✅ Connection successful! Found {len(buckets)} bucket(s):")
        for bucket in buckets:
            print(f"   • {bucket['Name']} (Created: {bucket['CreationDate']})")
        print()
        
        # Test 2: Check if our bucket exists
        print(f"🔄 Checking if bucket '{bucket_name}' exists...")
        bucket_exists = any(b['Name'] == bucket_name for b in buckets)
        
        if bucket_exists:
            print(f"✅ Bucket '{bucket_name}' exists!\n")
            
            # Test 3: List objects in bucket
            print(f"🔄 Listing objects in '{bucket_name}'...")
            try:
                objects = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=10)
                if 'Contents' in objects:
                    print(f"✅ Found {len(objects['Contents'])} object(s):")
                    for obj in objects['Contents']:
                        size_mb = obj['Size'] / (1024 * 1024)
                        print(f"   • {obj['Key']} ({size_mb:.2f} MB)")
                else:
                    print("✅ Bucket is empty (no objects found)")
                print()
            except ClientError as e:
                print(f"⚠️  Could not list objects: {e}")
                print()
            
            # Test 4: Get bucket location
            print(f"🔄 Getting bucket location...")
            try:
                location = s3_client.get_bucket_location(Bucket=bucket_name)
                bucket_region = location['LocationConstraint'] or 'us-east-1'
                print(f"✅ Bucket location: {bucket_region}")
                
                if bucket_region != region and bucket_region != 'us-east-1':
                    print(f"⚠️  WARNING: Bucket is in {bucket_region} but configured region is {region}")
                print()
            except ClientError as e:
                print(f"⚠️  Could not get bucket location: {e}")
                print()
                
        else:
            print(f"⚠️  Bucket '{bucket_name}' does not exist!\n")
            print("🔄 Would you like to create it? (Will be created in next step)")
            print()
            
            # Test 5: Create bucket
            print(f"🔄 Attempting to create bucket '{bucket_name}'...")
            try:
                if region == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                print(f"✅ Bucket '{bucket_name}' created successfully!")
                print()
                
                # Enable versioning
                print("🔄 Enabling versioning on bucket...")
                s3_client.put_bucket_versioning(
                    Bucket=bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
                print("✅ Versioning enabled!")
                print()
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'BucketAlreadyExists':
                    print(f"⚠️  Bucket already exists but owned by another account")
                elif error_code == 'BucketAlreadyOwnedByYou':
                    print(f"✅ Bucket already exists and you own it!")
                else:
                    print(f"❌ Failed to create bucket: {e}")
                print()
        
        # Final summary
        print("="*70)
        print("  ✅ AWS S3 CONNECTION TEST PASSED!")
        print("="*70)
        print("\n📊 Summary:")
        print(f"   • AWS Account: Connected ✅")
        print(f"   • Region: {region} ✅")
        print(f"   • Total Buckets: {len(buckets)} ✅")
        print(f"   • Target Bucket: {bucket_name} {'✅' if bucket_exists else '⚠️  (needs creation)'}")
        print()
        print("💡 You can now use S3 for file storage in the application!")
        print()
        
        return True
        
    except NoCredentialsError:
        print("❌ ERROR: No AWS credentials found!")
        print("   Please check your .env file configuration.")
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS Error ({error_code}): {error_message}")
        
        if error_code == 'InvalidAccessKeyId':
            print("   The AWS Access Key ID is invalid.")
        elif error_code == 'SignatureDoesNotMatch':
            print("   The AWS Secret Access Key is incorrect.")
        elif error_code == 'AccessDenied':
            print("   Access denied. Check IAM permissions for S3.")
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_aws_credentials()
    sys.exit(0 if success else 1)
