"""
Token Optimization Configuration for AI Analysis
Reduces API costs while maintaining quality
"""

# Token limits per analysis type (reduced by 50-60% from original)
TOKEN_LIMITS = {
    # Component analysis: Most important, keep reasonable
    'component_analysis': 1500,      # Was 3500 → 57% reduction
    
    # Compliance checking: Important but can be concise
    'compliance_check': 1200,        # Was 3000 → 60% reduction
    
    # Risk assessment: Focused on critical items
    'risk_assessment': 1000,         # Was 2000 → 50% reduction
    
    # Recommendations: Brief and actionable
    'recommendations': 800,          # Was 1500 → 47% reduction
    
    # Technical details: Concise extraction
    'technical_details': 800,        # Was 1500 → 47% reduction
    
    # Summary: Executive brief only
    'summary': 500,                  # Was 800 → 38% reduction
}

# Temperature settings (lower = more focused, uses fewer tokens)
TEMPERATURE_SETTINGS = {
    'component_analysis': 0.1,       # Was 0.2 → More focused
    'compliance_check': 0.1,         # Was 0.1 → Keep precise
    'risk_assessment': 0.2,          # Was 0.3 → More focused
    'recommendations': 0.3,          # Was 0.4 → Slightly more focused
    'technical_details': 0.1,        # Was 0.2 → More precise
    'summary': 0.3,                  # Was 0.4 → Slightly focused
}

# Model selection (gpt-4-turbo is cheaper than gpt-4)
MODEL_SETTINGS = {
    'primary': 'gpt-4-turbo',        # Main analysis model
    'fallback': 'gpt-4o-mini',       # For summaries (much cheaper)
}

# Analysis optimization flags
OPTIMIZATION_FLAGS = {
    # ⚡ STREAMLINED MODE - Use single API call instead of 6 separate calls
    'use_streamlined_analyzer': True,  # 80% faster, 80% cheaper (NEW!)
    
    # Skip detailed analysis for small/simple documents
    'skip_detailed_for_small_docs': True,
    'small_doc_threshold_kb': 100,
    
    # Use cached results for repeated analysis
    'enable_caching': True,
    'cache_ttl_hours': 24,
    
    # Batch multiple questions in single API call
    'enable_batching': True,
    
    # Use cheaper model for non-critical tasks
    'use_mini_for_summary': True,
    'use_mini_for_recommendations': False,  # Keep quality here
    
    # Skip optional analysis sections
    'skip_technical_details_if_simple': True,
    
    # Limit content sent to API (compress/truncate)
    'max_content_length': 15000,     # characters (8000 for streamlined)
    'truncate_method': 'smart',      # 'smart' or 'simple'
}

# Cost tracking (approximate, as of Dec 2024)
COST_PER_1K_TOKENS = {
    'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
    'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
}

def calculate_estimated_cost(analysis_type: str, use_mini: bool = False) -> dict:
    """Calculate estimated cost for an analysis"""
    model = 'gpt-4o-mini' if use_mini else 'gpt-4-turbo'
    token_limit = TOKEN_LIMITS.get(analysis_type, 1000)
    
    # Estimate input tokens (prompt + context)
    input_tokens = min(2000, token_limit * 0.5)  # Conservative estimate
    output_tokens = token_limit
    
    input_cost = (input_tokens / 1000) * COST_PER_1K_TOKENS[model]['input']
    output_cost = (output_tokens / 1000) * COST_PER_1K_TOKENS[model]['output']
    
    return {
        'model': model,
        'estimated_input_tokens': input_tokens,
        'estimated_output_tokens': output_tokens,
        'estimated_cost_usd': round(input_cost + output_cost, 4)
    }

def get_total_estimated_cost() -> dict:
    """Get total estimated cost for full analysis"""
    total_cost = 0
    breakdown = {}
    
    for analysis_type in TOKEN_LIMITS.keys():
        use_mini = (
            OPTIMIZATION_FLAGS['use_mini_for_summary'] and 'summary' in analysis_type or
            OPTIMIZATION_FLAGS['use_mini_for_recommendations'] and 'recommendations' in analysis_type
        )
        cost_info = calculate_estimated_cost(analysis_type, use_mini)
        breakdown[analysis_type] = cost_info
        total_cost += cost_info['estimated_cost_usd']
    
    return {
        'total_estimated_cost_usd': round(total_cost, 4),
        'breakdown': breakdown,
        'note': 'Costs are estimates and may vary based on actual token usage'
    }

# Print cost summary on import (for debugging)
if __name__ == '__main__':
    import json
    cost_summary = get_total_estimated_cost()
    print(json.dumps(cost_summary, indent=2))
