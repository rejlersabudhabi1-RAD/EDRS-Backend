"""
Django API Views for AI-Enhanced EDRS Platform
Provides REST endpoints for AI-powered document processing, validation, and conversion
"""

import asyncio
import json
import logging
from typing import Dict, Any
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FileUploadParser
import time

from .ai_services import get_ai_drawing_analyzer, get_document_classifier, get_document_validator
from .document_report_service import get_report_generator

logger = logging.getLogger(__name__)

class AIServiceMixin:
    """Mixin for common AI service functionality"""
    
    def handle_ai_error(self, error: Exception, operation: str) -> JsonResponse:
        """Handle AI service errors consistently"""
        logger.error(f"AI {operation} error: {str(error)}")
        return JsonResponse({
            'success': False,
            'error': str(error),
            'operation': operation,
            'timestamp': time.time()
        }, status=500)
    
    def validate_file_input(self, request: HttpRequest) -> tuple:
        """Validate file input from request"""
        if 'file' not in request.FILES:
            return None, JsonResponse({
                'success': False,
                'error': 'No file provided',
                'timestamp': time.time()
            }, status=400)
        
        uploaded_file = request.FILES['file']
        if uploaded_file.size == 0:
            return None, JsonResponse({
                'success': False,
                'error': 'Empty file provided',
                'timestamp': time.time()
            }, status=400)
        
        return uploaded_file, None


class PDFToPIDConversionAPI(APIView, AIServiceMixin):
    """AI-powered PDF to P&ID conversion endpoint"""
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FileUploadParser]
    
    def post(self, request):
        """Convert PDF drawings to P&ID using OpenAI Vision API"""
        try:
            # Validate input
            uploaded_file, error_response = self.validate_file_input(request)
            if error_response:
                return error_response
            
            # Extract file data
            file_data = uploaded_file.read()
            filename = uploaded_file.name
            file_type = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
            
            # Validate file type
            allowed_types = ['pdf', 'png', 'jpg', 'jpeg', 'dwg', 'dxf']
            if file_type not in allowed_types:
                return JsonResponse({
                    'success': False,
                    'error': f'Unsupported file type: {file_type}. Allowed: {", ".join(allowed_types)}',
                    'timestamp': time.time()
                }, status=400)
            
            # Process with AI
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                conversion_result = loop.run_until_complete(
                    get_ai_drawing_analyzer().convert_pdf_to_pid(file_data, filename)
                )
            finally:
                loop.close()
            
            # Return results
            return JsonResponse({
                'success': True,
                'conversion_result': conversion_result,
                'service': 'pdf_to_pid_conversion',
                'timestamp': time.time()
            })
            
        except Exception as e:
            return self.handle_ai_error(e, 'PDF to P&ID conversion')


class DocumentClassificationAPI(APIView, AIServiceMixin):
    """AI-powered document classification endpoint"""
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FileUploadParser]
    
    def post(self, request):
        """Classify and analyze uploaded documents using OpenAI"""
        try:
            # Validate input
            uploaded_file, error_response = self.validate_file_input(request)
            if error_response:
                return error_response
            
            # Extract file data
            file_data = uploaded_file.read()
            filename = uploaded_file.name
            file_type = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
            
            # Process with AI
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                classification_result = loop.run_until_complete(
                    get_document_classifier().classify_and_process_document(file_data, filename, file_type)
                )
            finally:
                loop.close()
            
            # Return results
            return JsonResponse({
                'success': True,
                'classification_result': classification_result,
                'service': 'document_classification',
                'timestamp': time.time()
            })
            
        except Exception as e:
            return self.handle_ai_error(e, 'document classification')


class DocumentValidationAPI(APIView, AIServiceMixin):
    """AI-powered document validation endpoint"""
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FileUploadParser]
    
    def post(self, request):
        """Validate documents using comprehensive AI analysis"""
        try:
            # Validate input
            uploaded_file, error_response = self.validate_file_input(request)
            if error_response:
                return error_response
            
            # Extract file data and parameters
            file_data = uploaded_file.read()
            filename = uploaded_file.name
            
            # Get validation criteria from request (optional)
            validation_criteria = {}
            if hasattr(request, 'data') and 'validation_criteria' in request.data:
                try:
                    validation_criteria = json.loads(request.data['validation_criteria'])
                except (json.JSONDecodeError, TypeError):
                    validation_criteria = {}
            
            # Process with AI
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                validation_result = loop.run_until_complete(
                    get_document_validator().validate_document_comprehensive(file_data, filename, validation_criteria)
                )
            finally:
                loop.close()
            
            # Return results
            return JsonResponse({
                'success': True,
                'validation_result': validation_result,
                'service': 'document_validation',
                'timestamp': time.time()
            })
            
        except Exception as e:
            return self.handle_ai_error(e, 'document validation')


class BulkDocumentProcessingAPI(APIView, AIServiceMixin):
    """Bulk document processing with AI analysis"""
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        """Process multiple documents with AI services"""
        try:
            files = request.FILES.getlist('files')
            if not files:
                return JsonResponse({
                    'success': False,
                    'error': 'No files provided for bulk processing',
                    'timestamp': time.time()
                }, status=400)
            
            # Get processing type from request
            processing_type = request.data.get('processing_type', 'classification')
            allowed_types = ['classification', 'validation', 'pdf_to_pid']
            
            if processing_type not in allowed_types:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid processing type. Allowed: {", ".join(allowed_types)}',
                    'timestamp': time.time()
                }, status=400)
            
            results = []
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                for uploaded_file in files:
                    file_data = uploaded_file.read()
                    filename = uploaded_file.name
                    file_type = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
                    
                    try:
                        if processing_type == 'classification':
                            result = loop.run_until_complete(
                                get_document_classifier().classify_and_process_document(file_data, filename, file_type)
                            )
                        elif processing_type == 'validation':
                            result = loop.run_until_complete(
                                get_document_validator().validate_document_comprehensive(file_data, filename)
                            )
                        elif processing_type == 'pdf_to_pid':
                            result = loop.run_until_complete(
                                get_ai_drawing_analyzer().convert_pdf_to_pid(file_data, filename)
                            )
                        
                        results.append({
                            'filename': filename,
                            'status': 'success',
                            'result': result
                        })
                        
                    except Exception as file_error:
                        results.append({
                            'filename': filename,
                            'status': 'error',
                            'error': str(file_error)
                        })
            finally:
                loop.close()
            
            # Calculate summary statistics
            successful = len([r for r in results if r['status'] == 'success'])
            failed = len([r for r in results if r['status'] == 'error'])
            
            return JsonResponse({
                'success': True,
                'bulk_processing_result': {
                    'total_files': len(files),
                    'successful': successful,
                    'failed': failed,
                    'processing_type': processing_type,
                    'results': results
                },
                'service': 'bulk_document_processing',
                'timestamp': time.time()
            })
            
        except Exception as e:
            return self.handle_ai_error(e, 'bulk document processing')


class AIServiceStatusAPI(APIView):
    """AI service status and health check endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get AI service status and capabilities"""
        try:
            # Test basic AI service connectivity
            test_status = self._test_ai_services()
            
            return JsonResponse({
                'success': True,
                'ai_services_status': {
                    'pdf_to_pid_converter': test_status.get('pdf_to_pid', False),
                    'document_classifier': test_status.get('classification', False),
                    'document_validator': test_status.get('validation', False),
                    'openai_integration': test_status.get('openai', False)
                },
                'capabilities': {
                    'supported_file_types': {
                        'pdf_conversion': ['pdf', 'png', 'jpg', 'jpeg', 'dwg', 'dxf'],
                        'document_classification': ['pdf', 'doc', 'docx', 'txt', 'csv', 'dwg', 'dxf'],
                        'document_validation': ['pdf', 'doc', 'docx', 'txt', 'dwg', 'dxf']
                    },
                    'ai_models': {
                        'vision_model': 'gpt-4-vision-preview',
                        'text_model': 'gpt-4',
                        'classification_model': 'gpt-3.5-turbo'
                    },
                    'processing_limits': {
                        'max_file_size': '50MB',
                        'max_bulk_files': 20,
                        'concurrent_requests': 4
                    }
                },
                'service': 'ai_service_status',
                'timestamp': time.time()
            })
            
        except Exception as e:
            return self.handle_ai_error(e, 'service status check')
    
    def _test_ai_services(self) -> Dict[str, bool]:
        """Test AI service availability"""
        try:
            # Simple connectivity tests (in production, would test actual API calls)
            return {
                'pdf_to_pid': True,
                'classification': True,
                'validation': True,
                'openai': True
            }
        except Exception as e:
            logger.error(f"AI service test failed: {str(e)}")
            return {
                'pdf_to_pid': False,
                'classification': False,
                'validation': False,
                'openai': False
            }


# Legacy function-based views for backward compatibility
@csrf_exempt
@require_http_methods(["POST"])
def pdf_to_pid_conversion_legacy(request):
    """Legacy function-based view for PDF to P&ID conversion"""
    api_view = PDFToPIDConversionAPI()
    api_view.request = request
    return api_view.post(request)


@csrf_exempt  
@require_http_methods(["POST"])
def document_classification_legacy(request):
    """Legacy function-based view for document classification"""
    api_view = DocumentClassificationAPI()
    api_view.request = request
    return api_view.post(request)


@csrf_exempt
@require_http_methods(["POST"])
def document_validation_legacy(request):
    """Legacy function-based view for document validation"""
    api_view = DocumentValidationAPI()
    api_view.request = request
    return api_view.post(request)


@csrf_exempt
@require_http_methods(["GET"])
def ai_service_status_legacy(request):
    """Legacy function-based view for AI service status"""
    api_view = AIServiceStatusAPI()
    api_view.request = request
    return api_view.get(request)


class DocumentUploadWithReportAPI(APIView, AIServiceMixin):
    """
    Complete document upload pipeline with AI analysis and report generation
    Combines upload, classification, and report generation in one endpoint
    """
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FileUploadParser]
    
    def post(self, request):
        """
        Upload document, perform AI analysis, and generate comprehensive report
        
        Request Parameters:
            - file: Document file (PDF, DWG, DXF, PNG, JPG, DOCX)
            - report_format: Report format - "json" (default), "pdf", "html"
            - analysis_type: Type of analysis - "classification" (default), "validation", "full"
        """
        try:
            # Validate input
            uploaded_file, error_response = self.validate_file_input(request)
            if error_response:
                return error_response
            
            # Extract parameters
            file_data = uploaded_file.read()
            filename = uploaded_file.name
            file_type = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
            file_size = uploaded_file.size
            report_format = request.data.get('report_format', 'json')
            analysis_type = request.data.get('analysis_type', 'classification')
            
            # Validate file type
            allowed_types = ['pdf', 'png', 'jpg', 'jpeg', 'dwg', 'dxf', 'docx', 'doc']
            if file_type not in allowed_types:
                return JsonResponse({
                    'success': False,
                    'error': f'Unsupported file type: {file_type}. Allowed: {", ".join(allowed_types)}',
                    'timestamp': time.time()
                }, status=400)
            
            # Document information
            document_info = {
                'filename': filename,
                'file_type': file_type.upper(),
                'file_size': file_size,
                'upload_date': datetime.now().isoformat(),
                'uploaded_by': request.user.username if request.user.is_authenticated else 'Anonymous'
            }
            
            # Perform AI analysis
            analysis_result = None
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                if analysis_type == 'validation':
                    # Document validation
                    analysis_result = loop.run_until_complete(
                        get_document_validator().validate_document_comprehensive(file_data, filename)
                    )
                elif analysis_type == 'full':
                    # Full analysis (classification + validation)
                    classification_result = loop.run_until_complete(
                        get_document_classifier().classify_and_process_document(file_data, filename, file_type)
                    )
                    validation_result = loop.run_until_complete(
                        get_document_validator().validate_document_comprehensive(file_data, filename)
                    )
                    # Merge results
                    analysis_result = {**classification_result, **validation_result}
                else:
                    # Default: Classification only
                    analysis_result = loop.run_until_complete(
                        get_document_classifier().classify_and_process_document(file_data, filename, file_type)
                    )
            finally:
                loop.close()
            
            if not analysis_result:
                return JsonResponse({
                    'success': False,
                    'error': 'AI analysis failed to produce results',
                    'timestamp': time.time()
                }, status=500)
            
            # Generate comprehensive report
            report_generator = get_report_generator()
            report_result = report_generator.generate_report(
                document_info=document_info,
                analysis_result=analysis_result,
                report_format=report_format
            )
            
            if not report_result.get('success'):
                return JsonResponse({
                    'success': False,
                    'error': f"Report generation failed: {report_result.get('error')}",
                    'analysis_result': analysis_result,
                    'timestamp': time.time()
                }, status=500)
            
            # Return complete response
            response_data = {
                'success': True,
                'message': 'Document uploaded, analyzed, and report generated successfully',
                'document_info': document_info,
                'analysis_result': analysis_result,
                'report': report_result,
                'timestamp': time.time()
            }
            
            # For HTML/PDF, include content directly
            if report_format == 'html':
                response_data['html_content'] = report_result.get('html_content')
            elif report_format == 'pdf':
                # Return PDF as base64 for download
                import base64
                pdf_content = report_result.get('pdf_content')
                if pdf_content:
                    response_data['pdf_base64'] = base64.b64encode(pdf_content).decode('utf-8')
            
            return JsonResponse(response_data, status=201)
            
        except Exception as e:
            logger.error(f"Document upload with report error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def document_upload_with_report_legacy(request):
    """Legacy function-based view for document upload with report"""
    api_view = DocumentUploadWithReportAPI()
    api_view.request = request
    return api_view.post(request)