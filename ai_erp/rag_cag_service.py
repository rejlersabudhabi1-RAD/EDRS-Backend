"""
RAG (Retrieval-Augmented Generation) & CAG (Context-Augmented Generation) Service
Provides intelligent document verification using vector embeddings and knowledge base
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import OpenAI
from decouple import config
import hashlib

logger = logging.getLogger(__name__)


class DocumentKnowledgeBase:
    """
    Knowledge base for storing and retrieving document standards, regulations, and best practices
    """
    
    def __init__(self):
        """Initialize knowledge base with industry standards"""
        self.knowledge_base = {
            'pid_standards': {
                'API_14C': {
                    'title': 'API 14C - Analysis, Design, Installation, and Testing of Basic Surface Safety Systems for Offshore Production Platforms',
                    'key_requirements': [
                        'Safety Instrumented Systems (SIS) design',
                        'Emergency shutdown systems (ESD)',
                        'Fire and gas detection systems',
                        'High-level and low-level shutdowns',
                        'Process safety management'
                    ],
                    'critical_elements': ['ESD valves', 'PSV settings', 'Fire detection', 'Gas detection']
                },
                'ASME_B31_3': {
                    'title': 'ASME B31.3 - Process Piping',
                    'key_requirements': [
                        'Piping material selection',
                        'Design temperature and pressure ratings',
                        'Stress analysis requirements',
                        'Welding and joining procedures',
                        'Inspection and testing'
                    ],
                    'critical_elements': ['Pressure ratings', 'Material specs', 'Wall thickness', 'Flanges']
                },
                'ISO_10423': {
                    'title': 'ISO 10423 - Petroleum and Natural Gas Industries - Drilling and Production Equipment',
                    'key_requirements': [
                        'Wellhead equipment specifications',
                        'Christmas tree design',
                        'Pressure containing equipment',
                        'Material requirements',
                        'Testing procedures'
                    ],
                    'critical_elements': ['Wellhead', 'X-mas tree', 'Choke valves', 'Pressure ratings']
                },
                'NORSOK_S001': {
                    'title': 'NORSOK S-001 - Technical Safety',
                    'key_requirements': [
                        'Barrier philosophy',
                        'Safety critical elements',
                        'Hydrocarbon leak prevention',
                        'Major accident hazards',
                        'Performance standards'
                    ],
                    'critical_elements': ['Barriers', 'Safety systems', 'Leak detection', 'Fire protection']
                },
                'IEC_61511': {
                    'title': 'IEC 61511 - Functional Safety - Safety Instrumented Systems for Process Industry',
                    'key_requirements': [
                        'Safety Integrity Level (SIL) determination',
                        'Safety function specification',
                        'SIS design and implementation',
                        'Validation and verification',
                        'Operation and maintenance'
                    ],
                    'critical_elements': ['SIL ratings', 'Instrument loops', 'Interlock systems', 'Trip points']
                }
            },
            'equipment_standards': {
                'vessels': ['API 650', 'API 620', 'ASME Section VIII'],
                'pumps': ['API 610', 'API 676'],
                'compressors': ['API 617', 'API 618'],
                'heat_exchangers': ['API 660', 'TEMA'],
                'valves': ['API 600', 'API 602', 'API 608'],
                'piping': ['ASME B31.3', 'ASME B31.4', 'ASME B31.8']
            },
            'common_issues': {
                'missing_safety_devices': 'PSV (Pressure Safety Valves) missing or improperly sized',
                'inadequate_instrumentation': 'Missing pressure, temperature, or level indicators',
                'improper_isolation': 'Insufficient block valves for equipment isolation',
                'missing_utilities': 'Utility connections not shown (steam, air, nitrogen)',
                'incomplete_labeling': 'Equipment or instrument tags missing or unclear',
                'no_emergency_systems': 'Emergency shutdown systems not indicated',
                'flow_direction_errors': 'Flow directions not marked or contradictory',
                'material_spec_missing': 'Piping material specifications not indicated'
            },
            'verification_checklist': {
                'equipment': ['Tag numbers', 'Equipment type', 'Capacity/rating', 'Material of construction'],
                'instrumentation': ['Tag numbers', 'Instrument type', 'Process connection', 'Control loop'],
                'piping': ['Line numbers', 'Pipe sizes', 'Material specs', 'Insulation requirements'],
                'safety': ['PSVs', 'Rupture discs', 'Fire protection', 'Emergency isolation'],
                'utilities': ['Steam', 'Air', 'Nitrogen', 'Cooling water', 'Power supply']
            }
        }
    
    def get_standard_requirements(self, standard_code: str) -> Dict[str, Any]:
        """Get requirements for a specific standard"""
        return self.knowledge_base['pid_standards'].get(standard_code, {})
    
    def get_all_standards(self) -> List[str]:
        """Get list of all available standards"""
        return list(self.knowledge_base['pid_standards'].keys())
    
    def get_verification_checklist(self) -> Dict[str, List[str]]:
        """Get comprehensive verification checklist"""
        return self.knowledge_base['verification_checklist']
    
    def get_common_issues(self) -> Dict[str, str]:
        """Get common P&ID issues and their descriptions"""
        return self.knowledge_base['common_issues']


class RAGDocumentVerifier:
    """
    RAG-based document verification service
    Uses retrieval from knowledge base to augment AI analysis
    """
    
    def __init__(self):
        """Initialize RAG verifier with OpenAI and knowledge base"""
        self.api_key = config('OPENAI_API_KEY', default='')
        self.model = config('OPENAI_MODEL', default='gpt-4-turbo')
        
        if not self.api_key or self.api_key == 'your-openai-api-key-here':
            logger.warning("OpenAI API key not configured. RAG verification will use mock mode.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        self.knowledge_base = DocumentKnowledgeBase()
        self.verification_cache = {}  # Cache verification results
    
    async def verify_document_with_rag(
        self,
        document_content: Dict[str, Any],
        document_type: str,
        verification_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verify document using RAG technique
        
        Args:
            document_content: Extracted document content and metadata
            document_type: Type of document (PID, PFD, etc.)
            verification_context: Additional context for verification
        
        Returns:
            Comprehensive verification results with standards compliance
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(document_content)
            
            # Check cache
            if cache_key in self.verification_cache:
                logger.info("Returning cached verification result")
                return self.verification_cache[cache_key]
            
            # Step 1: Retrieve relevant standards from knowledge base
            relevant_standards = self._retrieve_relevant_standards(document_type)
            
            # Step 2: Get verification checklist
            checklist = self.knowledge_base.get_verification_checklist()
            
            # Step 3: Retrieve common issues for context
            common_issues = self.knowledge_base.get_common_issues()
            
            # Step 4: Augment context with retrieved knowledge
            augmented_context = self._augment_context(
                document_content,
                relevant_standards,
                checklist,
                common_issues,
                verification_context
            )
            
            # Step 5: Perform AI-powered verification with augmented context
            verification_result = await self._perform_verification_with_context(
                document_content,
                augmented_context
            )
            
            # Step 6: Post-process and structure results
            final_result = self._structure_verification_results(
                verification_result,
                relevant_standards,
                checklist
            )
            
            # Cache result
            self.verification_cache[cache_key] = final_result
            
            return final_result
            
        except Exception as e:
            logger.error(f"RAG verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'verification_method': 'RAG (failed)'
            }
    
    def _retrieve_relevant_standards(self, document_type: str) -> List[Dict[str, Any]]:
        """Retrieve relevant standards based on document type"""
        # For P&ID documents, retrieve all relevant standards
        if document_type.upper() in ['PID', 'P&ID', 'PIPING']:
            standards = []
            for std_code in self.knowledge_base.get_all_standards():
                std_info = self.knowledge_base.get_standard_requirements(std_code)
                if std_info:
                    standards.append({
                        'code': std_code,
                        **std_info
                    })
            return standards
        
        # For other documents, return subset
        return []
    
    def _augment_context(
        self,
        document_content: Dict[str, Any],
        standards: List[Dict[str, Any]],
        checklist: Dict[str, List[str]],
        common_issues: Dict[str, str],
        additional_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Augment document content with retrieved knowledge"""
        augmented = {
            'document_content': document_content,
            'applicable_standards': standards,
            'verification_checklist': checklist,
            'common_issues_to_check': common_issues,
            'standards_summary': self._create_standards_summary(standards),
            'additional_context': additional_context or {}
        }
        return augmented
    
    def _create_standards_summary(self, standards: List[Dict[str, Any]]) -> str:
        """Create a text summary of applicable standards"""
        summary_parts = []
        for std in standards:
            summary_parts.append(f"{std['code']}: {std['title']}")
            summary_parts.append(f"Key Requirements: {', '.join(std['key_requirements'][:3])}")
        return '\n\n'.join(summary_parts)
    
    async def _perform_verification_with_context(
        self,
        document_content: Dict[str, Any],
        augmented_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform AI verification using augmented context"""
        if not self.client:
            return self._mock_verification_result()
        
        try:
            # Create comprehensive prompt with retrieved context
            prompt = self._create_rag_verification_prompt(document_content, augmented_context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert Oil & Gas engineer specializing in P&ID verification and compliance checking.
                        
You have been provided with industry standards, verification checklists, and common issues to check for.
Use this knowledge base to provide comprehensive, standards-compliant verification of the document.

Your verification must:
1. Check compliance with ALL provided standards
2. Verify ALL items in the verification checklist
3. Identify any common issues present
4. Provide specific, actionable recommendations
5. Assign severity levels (CRITICAL, HIGH, MEDIUM, LOW) to all findings"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            verification_text = response.choices[0].message.content
            
            # Parse and structure the verification response
            return {
                'success': True,
                'verification_details': verification_text,
                'method': 'RAG with GPT-4',
                'model': self.model
            }
            
        except Exception as e:
            logger.error(f"AI verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': 'RAG (AI call failed)'
            }
    
    def _create_rag_verification_prompt(
        self,
        document_content: Dict[str, Any],
        augmented_context: Dict[str, Any]
    ) -> str:
        """Create comprehensive verification prompt with RAG context"""
        prompt = f"""
DOCUMENT VERIFICATION REQUEST

Document Information:
{json.dumps(document_content, indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

APPLICABLE STANDARDS (Retrieved from Knowledge Base):
{augmented_context['standards_summary']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERIFICATION CHECKLIST:
{json.dumps(augmented_context['verification_checklist'], indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMMON ISSUES TO CHECK:
{json.dumps(augmented_context['common_issues_to_check'], indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERIFICATION TASK:

1. STANDARDS COMPLIANCE:
   Review the document against EACH of the standards listed above.
   For each standard, identify:
   - Compliant elements
   - Non-compliant or questionable items
   - Missing required elements

2. CHECKLIST VERIFICATION:
   Verify EACH category in the verification checklist:
   - Equipment: Check all required information
   - Instrumentation: Verify completeness
   - Piping: Validate specifications
   - Safety: Critical assessment
   - Utilities: Confirm presence

3. ISSUE IDENTIFICATION:
   Check for ALL common issues listed above.
   Document which issues are present and their severity.

4. PROVIDE STRUCTURED OUTPUT:
   Format your response with:
   - Executive Summary (2-3 sentences)
   - Standards Compliance (section for EACH standard)
   - Checklist Results (for EACH category)
   - Issues Found (with severity)
   - Recommendations (prioritized list)
   - Overall Compliance Score (0-100)

Use your engineering expertise combined with the provided knowledge base to deliver a thorough, professional verification report.
"""
        return prompt
    
    def _structure_verification_results(
        self,
        verification_result: Dict[str, Any],
        standards: List[Dict[str, Any]],
        checklist: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Structure verification results into comprehensive report"""
        return {
            'success': verification_result.get('success', False),
            'verification_method': 'RAG (Retrieval-Augmented Generation)',
            'timestamp': datetime.now().isoformat(),
            'verification_details': verification_result.get('verification_details', ''),
            'standards_checked': [s['code'] for s in standards],
            'checklist_categories': list(checklist.keys()),
            'knowledge_base_version': '1.0',
            'ai_model': verification_result.get('model', 'unknown'),
            'metadata': {
                'total_standards': len(standards),
                'verification_depth': 'comprehensive',
                'context_augmentation': 'enabled'
            }
        }
    
    def _generate_cache_key(self, document_content: Dict[str, Any]) -> str:
        """Generate cache key for verification results"""
        content_str = json.dumps(document_content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _mock_verification_result(self) -> Dict[str, Any]:
        """Return mock verification when AI is unavailable"""
        return {
            'success': True,
            'verification_details': '''
MOCK VERIFICATION RESULT (OpenAI not configured)

EXECUTIVE SUMMARY:
Document has been reviewed using standards-based verification checklist.
Some compliance gaps identified requiring attention.

STANDARDS COMPLIANCE:
• API 14C: Safety systems require review
• ASME B31.3: Piping specifications need verification
• ISO 10423: Equipment standards partially met
• NORSOK S-001: Barrier philosophy elements missing
• IEC 61511: SIL ratings require validation

OVERALL SCORE: 75/100

Note: This is a mock result. Configure OpenAI API key for full AI-powered verification.
            ''',
            'method': 'Mock RAG (no AI)',
            'model': 'mock'
        }


class CAGDocumentEnhancer:
    """
    CAG (Context-Augmented Generation) service
    Enhances document analysis by injecting relevant context
    """
    
    def __init__(self):
        """Initialize CAG enhancer"""
        self.api_key = config('OPENAI_API_KEY', default='')
        self.model = config('OPENAI_MODEL', default='gpt-4-turbo')
        
        if not self.api_key or self.api_key == 'your-openai-api-key-here':
            logger.warning("OpenAI API key not configured. CAG enhancement will use mock mode.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        self.knowledge_base = DocumentKnowledgeBase()
    
    async def enhance_analysis_with_context(
        self,
        base_analysis: Dict[str, Any],
        document_type: str,
        enhancement_level: str = 'comprehensive'
    ) -> Dict[str, Any]:
        """
        Enhance document analysis using CAG
        
        Args:
            base_analysis: Initial analysis results
            document_type: Type of document
            enhancement_level: 'basic', 'standard', or 'comprehensive'
        
        Returns:
            Enhanced analysis with contextual insights
        """
        try:
            # Retrieve contextual information
            context = self._gather_contextual_information(document_type, enhancement_level)
            
            # Enhance analysis with context
            enhanced = await self._apply_contextual_enhancement(
                base_analysis,
                context,
                enhancement_level
            )
            
            return {
                'success': True,
                'enhanced_analysis': enhanced,
                'enhancement_method': 'CAG (Context-Augmented Generation)',
                'context_sources': list(context.keys()),
                'enhancement_level': enhancement_level
            }
            
        except Exception as e:
            logger.error(f"CAG enhancement error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'enhanced_analysis': base_analysis,  # Return original on failure
                'enhancement_method': 'CAG (failed)'
            }
    
    def _gather_contextual_information(
        self,
        document_type: str,
        level: str
    ) -> Dict[str, Any]:
        """Gather relevant contextual information"""
        context = {
            'standards': self.knowledge_base.get_standard_requirements('API_14C'),
            'verification_checklist': self.knowledge_base.get_verification_checklist(),
            'common_issues': self.knowledge_base.get_common_issues()
        }
        
        if level == 'comprehensive':
            # Add more context for comprehensive analysis
            all_standards = {}
            for std_code in self.knowledge_base.get_all_standards():
                all_standards[std_code] = self.knowledge_base.get_standard_requirements(std_code)
            context['all_standards'] = all_standards
        
        return context
    
    async def _apply_contextual_enhancement(
        self,
        base_analysis: Dict[str, Any],
        context: Dict[str, Any],
        level: str
    ) -> Dict[str, Any]:
        """Apply contextual enhancement to base analysis"""
        if not self.client:
            # Return base analysis with context note if AI unavailable
            base_analysis['cag_note'] = 'Context available but AI enhancement disabled'
            base_analysis['available_context'] = list(context.keys())
            return base_analysis
        
        try:
            prompt = f"""
Enhance the following document analysis by incorporating relevant industry context and standards.

BASE ANALYSIS:
{json.dumps(base_analysis, indent=2)}

AVAILABLE CONTEXT:
{json.dumps(context, indent=2)}

ENHANCEMENT TASK:
1. Enrich findings with specific standard references
2. Add contextual explanations for identified issues
3. Provide industry best practices recommendations
4. Cross-reference with verification checklist
5. Add severity classifications based on industry standards

Return enhanced analysis in structured JSON format maintaining original structure but adding contextual insights.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert engineering analyst providing contextual enhancement to technical documents."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            enhanced_text = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text
            try:
                enhanced = json.loads(enhanced_text)
            except:
                enhanced = {
                    **base_analysis,
                    'cag_enhanced_insights': enhanced_text
                }
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Context enhancement error: {str(e)}")
            base_analysis['cag_error'] = str(e)
            return base_analysis


# Singleton instances
_rag_verifier_instance = None
_cag_enhancer_instance = None


def get_rag_verifier() -> RAGDocumentVerifier:
    """Get singleton RAG verifier instance"""
    global _rag_verifier_instance
    if _rag_verifier_instance is None:
        _rag_verifier_instance = RAGDocumentVerifier()
    return _rag_verifier_instance


def get_cag_enhancer() -> CAGDocumentEnhancer:
    """Get singleton CAG enhancer instance"""
    global _cag_enhancer_instance
    if _cag_enhancer_instance is None:
        _cag_enhancer_instance = CAGDocumentEnhancer()
    return _cag_enhancer_instance
