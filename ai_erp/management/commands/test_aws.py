"""
AWS Connection Test Management Command
Test AWS services connectivity for Rejlers AI-Powered ERP System
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from rejlers_api.aws_config import aws_config
import json

class Command(BaseCommand):
    help = 'Test AWS services connectivity (S3, SES, CloudWatch)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--service',
            type=str,
            help='Test specific service: s3, ses, or all',
            default='all',
            choices=['s3', 'ses', 'all']
        )
        
        parser.add_argument(
            '--send-test-email',
            type=str,
            help='Send test email to specified address (requires SES)',
            metavar='EMAIL'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
    
    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        service = options['service']
        test_email = options.get('send_test_email')
        
        self.stdout.write(self.style.SUCCESS('🚀 Testing AWS Services for Rejlers AI-Powered ERP System'))
        self.stdout.write('=' * 70)
        
        results = {}
        
        # Test S3 Connection
        if service in ['s3', 'all']:
            self.stdout.write('\n📦 Testing AWS S3 Connection...')
            success, message = aws_config.test_s3_connection()
            results['s3'] = {'success': success, 'message': message}
            
            if success:
                self.stdout.write(self.style.SUCCESS(f'✅ S3: {message}'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ S3: {message}'))
        
        # Test SES Connection
        if service in ['ses', 'all']:
            self.stdout.write('\n📧 Testing AWS SES Connection...')
            success, result = aws_config.test_ses_connection()
            results['ses'] = {'success': success, 'result': result}
            
            if success:
                self.stdout.write(self.style.SUCCESS('✅ SES: Connection successful'))
                if options['verbose'] and isinstance(result, dict):
                    self.stdout.write(f'   Quota Info: {json.dumps(result.get("quota", {}), indent=2)}')
                    verified_emails = result.get('verified_emails', [])
                    if verified_emails:
                        self.stdout.write(f'   Verified Emails: {", ".join(verified_emails)}')
                    else:
                        self.stdout.write(self.style.WARNING('   ⚠️ No verified email addresses found'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ SES: {result}'))
        
        # Send Test Email if requested
        if test_email:
            self.stdout.write(f'\n📨 Sending test email to {test_email}...')
            if 'ses' not in results or not results['ses']['success']:
                self.stdout.write(self.style.ERROR('❌ Cannot send email: SES connection failed'))
            else:
                success, message = aws_config.send_test_email(test_email)
                results['test_email'] = {'success': success, 'message': message}
                
                if success:
                    self.stdout.write(self.style.SUCCESS(f'✅ Email: {message}'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ Email: {message}'))
        
        # Summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('📊 AWS Services Summary:')
        
        all_successful = True
        for service_name, result in results.items():
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f'✅ {service_name.upper()}: Connected'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ {service_name.upper()}: Failed'))
                all_successful = False
        
        if all_successful:
            self.stdout.write(self.style.SUCCESS('\n🎉 All AWS services are working correctly!'))
            self.stdout.write('🌟 Your Rejlers AI-Powered ERP System is ready for Oil & Gas operations!')
        else:
            self.stdout.write(self.style.WARNING('\n⚠️ Some AWS services need attention.'))
            
        self.stdout.write('=' * 70)