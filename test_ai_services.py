"""
AI Service Testing Script for EDRS Platform
Tests all OpenAI integrations and AI services to ensure functionality
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Add the Django app directory to Python path
sys.path.append('/path/to/your/django/project')  # Update this path

class EDRSAITester:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.auth_token = None
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }

    def log_test(self, test_name, status, details=None, error=None):
        """Log test result"""
        self.test_results['total_tests'] += 1
        if status == 'PASS':
            self.test_results['passed_tests'] += 1
        else:
            self.test_results['failed_tests'] += 1
        
        test_result = {
            'test_name': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'error': error
        }
        self.test_results['test_details'].append(test_result)
        
        print(f"[{status}] {test_name}")
        if details:
            print(f"  Details: {details}")
        if error:
            print(f"  Error: {error}")

    def test_openai_connection(self):
        """Test OpenAI API connection"""
        try:
            import openai
            from django.conf import settings
            
            # Test OpenAI client initialization
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Test simple completion
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt="Test connection",
                max_tokens=5
            )
            
            if response.choices:
                self.log_test(
                    "OpenAI API Connection",
                    "PASS",
                    f"Successfully connected. Response: {response.choices[0].text.strip()}"
                )
                return True
            else:
                self.log_test("OpenAI API Connection", "FAIL", "No response from API")
                return False
                
        except Exception as e:
            self.log_test("OpenAI API Connection", "FAIL", error=str(e))
            return False

    def authenticate(self, username="testuser", password="testpass123"):
        """Authenticate with the Django API"""
        try:
            auth_data = {
                'username': username,
                'password': password
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login/",
                json=auth_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access')
                self.log_test("API Authentication", "PASS", "Successfully authenticated")
                return True
            else:
                self.log_test(
                    "API Authentication", 
                    "FAIL", 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("API Authentication", "FAIL", error=str(e))
            return False

    def get_auth_headers(self):
        """Get authentication headers"""
        return {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        } if self.auth_token else {}

    def test_service_status_endpoint(self):
        """Test AI service status endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/api/ai/service-status/",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Service Status Endpoint",
                    "PASS",
                    f"Services: {', '.join(data.get('services', {}).keys())}"
                )
                return True
            else:
                self.log_test(
                    "Service Status Endpoint",
                    "FAIL",
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Service Status Endpoint", "FAIL", error=str(e))
            return False

    def test_pdf_to_pid_endpoint(self):
        """Test PDF to P&ID conversion endpoint"""
        try:
            # Create a test file
            test_content = b"Test PDF content for P&ID conversion"
            
            files = {
                'file': ('test_diagram.pdf', test_content, 'application/pdf')
            }
            
            headers = {'Authorization': f'Bearer {self.auth_token}'} if self.auth_token else {}
            
            response = requests.post(
                f"{self.base_url}/api/ai/pdf-to-pid-conversion/",
                files=files,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test(
                    "PDF to P&ID Endpoint",
                    "PASS",
                    f"Processing time: {data.get('conversion_result', {}).get('processing_time', 'N/A')}"
                )
                return True
            else:
                self.log_test(
                    "PDF to P&ID Endpoint",
                    "FAIL",
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("PDF to P&ID Endpoint", "FAIL", error=str(e))
            return False

    def test_document_classification_endpoint(self):
        """Test document classification endpoint"""
        try:
            # Create a test document
            test_content = b"This is a test document for classification analysis."
            
            files = {
                'file': ('test_document.txt', test_content, 'text/plain')
            }
            
            headers = {'Authorization': f'Bearer {self.auth_token}'} if self.auth_token else {}
            
            response = requests.post(
                f"{self.base_url}/api/ai/document-classification/",
                files=files,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                classification = data.get('classification_result', {}).get('classification', {})
                self.log_test(
                    "Document Classification Endpoint",
                    "PASS",
                    f"Type: {classification.get('primary_type', 'N/A')}, Confidence: {classification.get('confidence_score', 'N/A')}"
                )
                return True
            else:
                self.log_test(
                    "Document Classification Endpoint",
                    "FAIL",
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Document Classification Endpoint", "FAIL", error=str(e))
            return False

    def test_document_validation_endpoint(self):
        """Test document validation endpoint"""
        try:
            # Create a test document
            test_content = b"Test document content for comprehensive validation analysis."
            
            files = {
                'file': ('test_validation.pdf', test_content, 'application/pdf')
            }
            
            data = {
                'validation_criteria': json.dumps({
                    'check_completeness': True,
                    'check_compliance': True,
                    'check_quality': True
                })
            }
            
            headers = {'Authorization': f'Bearer {self.auth_token}'} if self.auth_token else {}
            
            response = requests.post(
                f"{self.base_url}/api/ai/document-validation/",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                result_data = response.json()
                validation = result_data.get('validation_result', {})
                self.log_test(
                    "Document Validation Endpoint",
                    "PASS",
                    f"Overall Score: {validation.get('overall_score', 'N/A')}, Processing Time: {validation.get('processing_metrics', {}).get('processing_time', 'N/A')}"
                )
                return True
            else:
                self.log_test(
                    "Document Validation Endpoint",
                    "FAIL",
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Document Validation Endpoint", "FAIL", error=str(e))
            return False

    def test_bulk_processing_endpoint(self):
        """Test bulk processing endpoint"""
        try:
            # Create multiple test files
            files = []
            for i in range(2):
                content = f"Test document {i+1} for bulk processing".encode()
                files.append(('files', (f'test_bulk_{i+1}.txt', content, 'text/plain')))
            
            data = {'processing_type': 'classification'}
            headers = {'Authorization': f'Bearer {self.auth_token}'} if self.auth_token else {}
            
            response = requests.post(
                f"{self.base_url}/api/ai/bulk-processing/",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                result_data = response.json()
                bulk_result = result_data.get('bulk_processing_result', {})
                self.log_test(
                    "Bulk Processing Endpoint",
                    "PASS",
                    f"Processed: {bulk_result.get('total_processed', 0)} files, Success: {bulk_result.get('successful_processes', 0)}"
                )
                return True
            else:
                self.log_test(
                    "Bulk Processing Endpoint",
                    "FAIL",
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Bulk Processing Endpoint", "FAIL", error=str(e))
            return False

    def test_django_ai_services(self):
        """Test Django AI services directly"""
        try:
            import django
            from django.conf import settings
            
            # Configure Django settings
            if not settings.configured:
                settings.configure(
                    DEBUG=True,
                    SECRET_KEY='test-key-for-ai-testing',
                    INSTALLED_APPS=[
                        'django.contrib.auth',
                        'django.contrib.contenttypes',
                        # Add your app here
                    ],
                    DATABASES={
                        'default': {
                            'ENGINE': 'django.db.backends.sqlite3',
                            'NAME': ':memory:',
                        }
                    }
                )
            
            django.setup()
            
            # Test service imports
            from backend.ai_services import (
                PDFToPIDConverter,
                DocumentClassificationService,
                DocumentValidationService
            )
            
            # Test service initialization
            pdf_converter = PDFToPIDConverter()
            classifier = DocumentClassificationService()
            validator = DocumentValidationService()
            
            self.log_test(
                "Django AI Services Import",
                "PASS",
                "All AI services imported successfully"
            )
            return True
            
        except Exception as e:
            self.log_test("Django AI Services Import", "FAIL", error=str(e))
            return False

    def run_comprehensive_test(self):
        """Run all AI service tests"""
        print("="*60)
        print("EDRS AI Service Comprehensive Testing")
        print("="*60)
        
        # Test 1: OpenAI Connection
        print("\n1. Testing OpenAI API Connection...")
        self.test_openai_connection()
        
        # Test 2: Django Services
        print("\n2. Testing Django AI Services...")
        self.test_django_ai_services()
        
        # Test 3: API Authentication
        print("\n3. Testing API Authentication...")
        auth_success = self.authenticate()
        
        if auth_success:
            # Test 4: Service Status
            print("\n4. Testing Service Status Endpoint...")
            self.test_service_status_endpoint()
            
            # Test 5: PDF to P&ID
            print("\n5. Testing PDF to P&ID Conversion...")
            self.test_pdf_to_pid_endpoint()
            
            # Test 6: Document Classification
            print("\n6. Testing Document Classification...")
            self.test_document_classification_endpoint()
            
            # Test 7: Document Validation
            print("\n7. Testing Document Validation...")
            self.test_document_validation_endpoint()
            
            # Test 8: Bulk Processing
            print("\n8. Testing Bulk Processing...")
            self.test_bulk_processing_endpoint()
        else:
            print("\nSkipping API endpoint tests due to authentication failure")
        
        # Print Summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = self.test_results['total_tests']
        passed = self.test_results['passed_tests']
        failed = self.test_results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed > 0:
            print(f"\nFAILED TESTS:")
            for test in self.test_results['test_details']:
                if test['status'] == 'FAIL':
                    print(f"  - {test['test_name']}: {test['error']}")
        
        print(f"\nTest completed at: {self.test_results['timestamp']}")
        
        # Save detailed results
        with open('ai_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"Detailed results saved to: ai_test_results.json")

def main():
    """Main testing function"""
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print("WARNING: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-api-key'")
    
    # Initialize tester
    tester = EDRSAITester()
    
    # Run comprehensive tests
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()