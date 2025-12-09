"""
Document Report Generation Service
Generates comprehensive analysis reports for uploaded documents
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime
import io
from decouple import config

# Optional PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)


class DocumentReportGenerator:
    """Generate comprehensive analysis reports for documents"""
    
    def __init__(self):
        self.report_template = "comprehensive"
        
    def generate_report(self, 
                       document_info: Dict[str, Any], 
                       analysis_result: Dict[str, Any],
                       report_format: str = "json") -> Dict[str, Any]:
        """
        Generate comprehensive document analysis report
        
        Args:
            document_info: Basic document information (filename, type, size, etc.)
            analysis_result: AI analysis results from classification/validation
            report_format: Output format - "json", "pdf", "html"
        
        Returns:
            Report data with download link and metadata
        """
        try:
            # Generate report ID
            report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Compile report data
            report_data = self._compile_report_data(document_info, analysis_result, report_id)
            
            # Generate based on format
            if report_format == "pdf" and REPORTLAB_AVAILABLE:
                report_file = self._generate_pdf_report(report_data)
                return {
                    "success": True,
                    "report_id": report_id,
                    "format": "pdf",
                    "report_data": report_data,
                    "download_url": f"/api/ai/reports/{report_id}/download",
                    "pdf_content": report_file.getvalue() if report_file else None
                }
            elif report_format == "html":
                html_content = self._generate_html_report(report_data)
                return {
                    "success": True,
                    "report_id": report_id,
                    "format": "html",
                    "report_data": report_data,
                    "html_content": html_content,
                    "download_url": f"/api/ai/reports/{report_id}/download"
                }
            else:
                # JSON format (default)
                return {
                    "success": True,
                    "report_id": report_id,
                    "format": "json",
                    "report_data": report_data,
                    "download_url": f"/api/ai/reports/{report_id}/download"
                }
                
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "report_id": None
            }
    
    def _compile_report_data(self, 
                            document_info: Dict[str, Any], 
                            analysis_result: Dict[str, Any],
                            report_id: str) -> Dict[str, Any]:
        """Compile comprehensive report data"""
        
        # Extract classification data
        classification = analysis_result.get('classification', {})
        metadata = analysis_result.get('metadata', {})
        recommendations = analysis_result.get('processing_recommendations', [])
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            document_info, classification, metadata
        )
        
        # Compile findings
        findings = self._compile_findings(analysis_result)
        
        # Risk assessment
        risk_assessment = self._generate_risk_assessment(classification, findings)
        
        # Compliance status
        compliance_status = self._generate_compliance_status(classification, metadata)
        
        return {
            "report_id": report_id,
            "generated_at": datetime.now().isoformat(),
            "document_information": {
                "filename": document_info.get('filename', 'Unknown'),
                "file_type": document_info.get('file_type', 'Unknown'),
                "file_size": document_info.get('file_size', 0),
                "upload_date": document_info.get('upload_date', datetime.now().isoformat()),
                "uploaded_by": document_info.get('uploaded_by', 'System')
            },
            "executive_summary": executive_summary,
            "classification_results": {
                "primary_type": classification.get('primary_type', 'Unknown'),
                "subcategory": classification.get('subcategory', 'General'),
                "confidence_score": classification.get('confidence_score', 0.0),
                "complexity_level": classification.get('complexity_level', 'Medium'),
                "safety_criticality": classification.get('safety_criticality', 'Standard')
            },
            "metadata_analysis": metadata,
            "findings": findings,
            "risk_assessment": risk_assessment,
            "compliance_status": compliance_status,
            "processing_recommendations": recommendations,
            "ai_analysis_details": {
                "model_used": analysis_result.get('model_used', 'gpt-3.5-turbo'),
                "processing_time": analysis_result.get('processing_time', 'N/A'),
                "accuracy_estimate": analysis_result.get('accuracy_score', 'N/A')
            },
            "next_actions": self._generate_next_actions(recommendations)
        }
    
    def _generate_executive_summary(self, 
                                    document_info: Dict[str, Any],
                                    classification: Dict[str, Any],
                                    metadata: Dict[str, Any]) -> str:
        """Generate executive summary"""
        filename = document_info.get('filename', 'the document')
        doc_type = classification.get('primary_type', 'engineering document')
        confidence = classification.get('confidence_score', 0)
        complexity = classification.get('complexity_level', 'Medium')
        
        summary = f"""
        Document '{filename}' has been analyzed and classified as a {doc_type} 
        with {confidence:.1%} confidence. The document complexity is assessed as {complexity}.
        
        Key characteristics identified: {metadata.get('document_purpose', 'General documentation')}
        
        Technical complexity: {complexity}
        Safety impact: {classification.get('safety_criticality', 'Standard')}
        Recommended review level: {metadata.get('review_level', 'Standard technical review')}
        """
        
        return summary.strip()
    
    def _compile_findings(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compile analysis findings"""
        findings = []
        
        # Extract findings from different sources
        classification = analysis_result.get('classification', {})
        
        # Quality findings
        if 'quality_issues' in analysis_result:
            for issue in analysis_result['quality_issues']:
                findings.append({
                    "category": "Quality",
                    "severity": issue.get('severity', 'Medium'),
                    "description": issue.get('description', ''),
                    "recommendation": issue.get('recommendation', '')
                })
        
        # Compliance findings
        if 'compliance_issues' in analysis_result:
            for issue in analysis_result['compliance_issues']:
                findings.append({
                    "category": "Compliance",
                    "severity": issue.get('severity', 'High'),
                    "description": issue.get('description', ''),
                    "recommendation": issue.get('recommendation', '')
                })
        
        # If no specific findings, generate from classification
        if not findings:
            findings.append({
                "category": "Analysis Complete",
                "severity": "Info",
                "description": f"Document successfully classified as {classification.get('primary_type', 'Unknown')}",
                "recommendation": "Proceed with standard processing workflow"
            })
        
        return findings
    
    def _generate_risk_assessment(self, 
                                  classification: Dict[str, Any],
                                  findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate risk assessment"""
        
        # Calculate risk level based on findings
        high_severity_count = sum(1 for f in findings if f.get('severity') in ['High', 'Critical'])
        safety_criticality = classification.get('safety_criticality', 'Standard')
        
        if high_severity_count > 0 or safety_criticality == 'Critical':
            risk_level = "High"
            risk_description = "Immediate attention required"
        elif safety_criticality == 'High':
            risk_level = "Medium"
            risk_description = "Enhanced review recommended"
        else:
            risk_level = "Low"
            risk_description = "Standard processing acceptable"
        
        return {
            "overall_risk_level": risk_level,
            "risk_description": risk_description,
            "safety_impact": safety_criticality,
            "mitigation_required": high_severity_count > 0,
            "critical_findings_count": high_severity_count
        }
    
    def _generate_compliance_status(self, 
                                    classification: Dict[str, Any],
                                    metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance status"""
        
        applicable_standards = metadata.get('applicable_standards', [])
        if isinstance(applicable_standards, str):
            applicable_standards = [applicable_standards]
        
        return {
            "applicable_standards": applicable_standards,
            "compliance_level": metadata.get('compliance_level', 'To Be Determined'),
            "regulatory_requirements": metadata.get('regulatory_requirements', []),
            "verification_status": "Pending Review",
            "certification_required": classification.get('safety_criticality') in ['High', 'Critical']
        }
    
    def _generate_next_actions(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate prioritized next actions"""
        
        next_actions = []
        
        if recommendations:
            for idx, rec in enumerate(recommendations[:5], 1):  # Top 5 actions
                next_actions.append({
                    "priority": str(idx),
                    "action": rec.get('action', 'Review Document'),
                    "responsible": rec.get('responsible_role', 'Engineering Team'),
                    "timeline": rec.get('estimated_time', 'TBD'),
                    "description": rec.get('description', '')
                })
        else:
            next_actions.append({
                "priority": "1",
                "action": "Initial Review",
                "responsible": "Document Owner",
                "timeline": "1-2 business days",
                "description": "Perform initial quality and completeness review"
            })
        
        return next_actions
    
    def _generate_pdf_report(self, report_data: Dict[str, Any]) -> io.BytesIO:
        """Generate PDF report using ReportLab"""
        if not REPORTLAB_AVAILABLE:
            raise Exception("ReportLab not available for PDF generation")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30
        )
        story.append(Paragraph("Document Analysis Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Report ID and Date
        story.append(Paragraph(f"<b>Report ID:</b> {report_data['report_id']}", styles['Normal']))
        story.append(Paragraph(f"<b>Generated:</b> {report_data['generated_at']}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Document Information
        story.append(Paragraph("<b>Document Information</b>", styles['Heading2']))
        doc_info = report_data['document_information']
        story.append(Paragraph(f"Filename: {doc_info['filename']}", styles['Normal']))
        story.append(Paragraph(f"Type: {doc_info['file_type']}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Executive Summary
        story.append(Paragraph("<b>Executive Summary</b>", styles['Heading2']))
        story.append(Paragraph(report_data['executive_summary'], styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Classification Results
        story.append(Paragraph("<b>Classification Results</b>", styles['Heading2']))
        classification = report_data['classification_results']
        story.append(Paragraph(f"Primary Type: {classification['primary_type']}", styles['Normal']))
        story.append(Paragraph(f"Confidence: {classification['confidence_score']:.1%}", styles['Normal']))
        story.append(Paragraph(f"Complexity: {classification['complexity_level']}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Document Analysis Report - {report_data['report_id']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8fafc; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                h1 {{ color: #1f2937; border-bottom: 3px solid #10b981; padding-bottom: 10px; }}
                h2 {{ color: #374151; margin-top: 30px; }}
                .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
                .info-item {{ background: #f3f4f6; padding: 15px; border-radius: 8px; }}
                .info-label {{ font-weight: bold; color: #6b7280; font-size: 14px; }}
                .info-value {{ color: #1f2937; margin-top: 5px; }}
                .findings {{ margin: 20px 0; }}
                .finding-item {{ border-left: 4px solid #10b981; padding: 15px; margin: 10px 0; background: #f9fafb; }}
                .severity-high {{ border-left-color: #ef4444; }}
                .severity-medium {{ border-left-color: #f59e0b; }}
                .action-item {{ background: #e0f2fe; padding: 15px; margin: 10px 0; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Document Analysis Report</h1>
                <p><strong>Report ID:</strong> {report_data['report_id']}</p>
                <p><strong>Generated:</strong> {report_data['generated_at']}</p>
                
                <h2>Document Information</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Filename</div>
                        <div class="info-value">{report_data['document_information']['filename']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">File Type</div>
                        <div class="info-value">{report_data['document_information']['file_type']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Classification</div>
                        <div class="info-value">{report_data['classification_results']['primary_type']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Confidence</div>
                        <div class="info-value">{report_data['classification_results']['confidence_score']:.1%}</div>
                    </div>
                </div>
                
                <h2>Executive Summary</h2>
                <p>{report_data['executive_summary']}</p>
                
                <h2>Risk Assessment</h2>
                <div class="info-item">
                    <div class="info-label">Overall Risk Level</div>
                    <div class="info-value">{report_data['risk_assessment']['overall_risk_level']}</div>
                    <p style="margin-top: 10px;">{report_data['risk_assessment']['risk_description']}</p>
                </div>
                
                <h2>Next Actions</h2>
                <div class="findings">
                    {''.join([f'''
                    <div class="action-item">
                        <strong>Priority {action['priority']}: {action['action']}</strong><br>
                        <small>Responsible: {action['responsible']} | Timeline: {action['timeline']}</small>
                        <p>{action['description']}</p>
                    </div>
                    ''' for action in report_data['next_actions']])}
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# Global service instance
_report_generator = None

def get_report_generator() -> DocumentReportGenerator:
    """Get or create report generator instance"""
    global _report_generator
    if _report_generator is None:
        _report_generator = DocumentReportGenerator()
    return _report_generator
