"""
AgriIntel-AI Modules Package
=============================
Core intelligent agent modules for crop recommendation, seed intelligence, and field analysis.
"""

from .llm_agent import (
    generate_advice,
    generate_seed_advice,
    generate_field_insights,
    is_ollama_available,
    warm_up_model,
    OLLAMA_API_URL,
    MODEL_NAME
)

from .seed_agent import (
    get_seed_recommendations,
    get_all_crops,
    get_available_seasons_for_crop,
    get_available_regions_for_crop,
    SUPPORTED_REGIONS
)

from .field_intelligence import (
    analyze_vegetation_coverage,
    analyze_soil_moisture,
    calculate_field_health_score,
    generate_field_report
)

__all__ = [
    # LLM Agent
    'generate_advice',
    'generate_seed_advice',
    'generate_field_insights',
    'is_ollama_available',
    'warm_up_model',
    'OLLAMA_API_URL',
    'MODEL_NAME',
    # Seed Agent
    'get_seed_recommendations',
    'get_all_crops',
    'get_available_seasons_for_crop',
    'get_available_regions_for_crop',
    'SUPPORTED_REGIONS',
    # Field Intelligence
    'analyze_vegetation_coverage',
    'analyze_soil_moisture',
    'calculate_field_health_score',
    'generate_field_report'
]
