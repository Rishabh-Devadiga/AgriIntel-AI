"""
Seed Intelligence Agent for Crop Recommendation System
=======================================================
This module provides intelligent seed variety recommendations based on:
- Predicted crop
- User location/region
- Selected season
- Historical yield and disease resistance data

The agent filters the seed varieties dataset and recommends the best
seeds ranked by expected yield.

Author: ML Pipeline
Date: 2026
"""

import pandas as pd
import os
from typing import List, Optional, Dict
from functools import lru_cache


# ============================================================
# Configuration
# ============================================================

SEED_DATASET_PATH = "seed_varieties_200_rows.csv"

# Supported regions
SUPPORTED_REGIONS = [
    "Maharashtra",
    "Punjab",
    "Karnataka",
    "Tamil Nadu",
    "Uttar Pradesh",
    "Gujarat",
    "Rajasthan"
]

# Global cache for dataset
_seed_dataset_cache = None


# ============================================================
# Dataset Loading
# ============================================================

def load_seed_dataset() -> Optional[pd.DataFrame]:
    """
    Load the seed varieties dataset from CSV file.
    
    Uses module-level caching to load the dataset only once per session.
    
    Returns:
    --------
    pd.DataFrame : Seed varieties dataset with columns:
        - Crop: Crop name
        - Variety: Seed variety name
        - Region: Geographic region
        - Season: Farming season
        - Yield_t_ha: Expected yield in tons per hectare
        - Duration_days: Growing duration in days
        - Disease_Resistance: Disease resistance level (Low/Medium/High)
        - Special_Trait: Special characteristics
    Optional[pd.DataFrame] : None if dataset not found
    """
    global _seed_dataset_cache
    
    if _seed_dataset_cache is not None:
        return _seed_dataset_cache
    
    try:
        if not os.path.exists(SEED_DATASET_PATH):
            print(f"⚠️ Warning: Seed dataset not found at {SEED_DATASET_PATH}")
            return None
        
        df = pd.read_csv(SEED_DATASET_PATH)
        
        # Data cleaning and standardization
        df['Crop'] = df['Crop'].str.strip().str.lower()
        df['Region'] = df['Region'].str.strip()
        df['Season'] = df['Season'].str.strip()
        df['Variety'] = df['Variety'].str.strip()
        
        _seed_dataset_cache = df
        return df
    
    except Exception as e:
        print(f"❌ Error loading seed dataset: {str(e)}")
        return None


# ============================================================
# Seed Recommendation Functions
# ============================================================

def get_seed_recommendations(
    crop: str,
    region: str,
    season: str,
    top_n: int = 3
) -> List[Dict]:
    """
    Get the best seed variety recommendations for a given crop.
    
    This function implements an intelligent filtering strategy:
    1. First, tries to find seeds matching crop + region + season
    2. If no match, falls back to crop + region
    3. If still no match, falls back to crop only
    4. Sorts by yield (descending) and returns top N varieties
    
    Parameters:
    -----------
    crop : str
        Predicted crop name
    region : str
        User's location/state
    season : str
        Farming season (Kharif/Rabi/Transition/Zaid)
    top_n : int
        Number of top recommendations to return (default=3)
    
    Returns:
    --------
    List[Dict] : List of recommended seed varieties with details:
        Each dict contains:
        - 'Variety': Seed variety name
        - 'Yield_t_ha': Expected yield
        - 'Disease_Resistance': Disease resistance level
        - 'Special_Trait': Special characteristics
        - 'Duration_days': Growing duration
        - 'Region': Region where this variety works best
        - 'Season': Best season for this variety
    
    Examples:
    ---------
    >>> recommendations = get_seed_recommendations('rice', 'Punjab', 'Kharif', top_n=3)
    >>> for rec in recommendations:
    ...     print(f"{rec['Variety']}: {rec['Yield_t_ha']} t/ha")
    """
    
    try:
        # Load dataset
        df = load_seed_dataset()
        if df is None or df.empty:
            return []
        
        # Normalize inputs
        crop = crop.strip().lower()
        region = region.strip()
        season = season.strip()
        
        # Strategy 1: Filter by crop + region + season
        filtered = df[
            (df['Crop'] == crop) &
            (df['Region'] == region) &
            (df['Season'] == season)
        ]
        
        # Strategy 2: Fallback to crop + region (if no exact match)
        if filtered.empty:
            filtered = df[
                (df['Crop'] == crop) &
                (df['Region'] == region)
            ]
        
        # Strategy 3: Fallback to crop only (if still no match)
        if filtered.empty:
            filtered = df[df['Crop'] == crop]
        
        # If still no results, return empty list
        if filtered.empty:
            return []
        
        # Sort by yield (descending) and select top N
        filtered = filtered.sort_values('Yield_t_ha', ascending=False)
        top_varieties = filtered.head(top_n)
        
        # Convert to list of dictionaries with relevant info
        recommendations = []
        for _, row in top_varieties.iterrows():
            recommendation = {
                'Variety': row['Variety'],
                'Yield_t_ha': round(float(row['Yield_t_ha']), 2),
                'Disease_Resistance': row['Disease_Resistance'],
                'Special_Trait': row['Special_Trait'],
                'Duration_days': int(row['Duration_days']),
                'Region': row['Region'],
                'Season': row['Season']
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    except Exception as e:
        print(f"❌ Error getting seed recommendations: {str(e)}")
        return []


def get_all_crops() -> List[str]:
    """
    Get all unique crop names available in the seed dataset.
    
    Returns:
    --------
    List[str] : Sorted list of crop names
    """
    try:
        df = load_seed_dataset()
        if df is None or df.empty:
            return []
        
        crops = sorted(df['Crop'].unique().tolist())
        return crops
    except Exception as e:
        print(f"❌ Error getting crop list: {str(e)}")
        return []


def get_available_seasons_for_crop(crop: str) -> List[str]:
    """
    Get available seasons for a specific crop.
    
    Parameters:
    -----------
    crop : str
        Crop name
    
    Returns:
    --------
    List[str] : List of available seasons for this crop
    """
    try:
        df = load_seed_dataset()
        if df is None or df.empty:
            return []
        
        crop = crop.strip().lower()
        seasons = sorted(
            df[df['Crop'] == crop]['Season'].unique().tolist()
        )
        return seasons
    except Exception as e:
        print(f"❌ Error getting seasons: {str(e)}")
        return []


def get_available_regions_for_crop(crop: str) -> List[str]:
    """
    Get available regions for a specific crop.
    
    Parameters:
    -----------
    crop : str
        Crop name
    
    Returns:
    --------
    List[str] : List of available regions for this crop
    """
    try:
        df = load_seed_dataset()
        if df is None or df.empty:
            return []
        
        crop = crop.strip().lower()
        regions = sorted(
            df[df['Crop'] == crop]['Region'].unique().tolist()
        )
        return regions
    except Exception as e:
        print(f"❌ Error getting regions: {str(e)}")
        return []


# ============================================================
# Helper Functions for UI
# ============================================================

def format_seed_recommendation(recommendation: Dict) -> str:
    """
    Format a seed recommendation for display in the UI.
    
    Parameters:
    -----------
    recommendation : Dict
        Single seed recommendation dictionary
    
    Returns:
    --------
    str : Formatted recommendation string
    """
    return f"""
    **{recommendation['Variety']}**
    
    - **Yield**: {recommendation['Yield_t_ha']} t/ha
    - **Disease Resistance**: {recommendation['Disease_Resistance']}
    - **Growing Period**: {recommendation['Duration_days']} days
    - **Special Trait**: {recommendation['Special_Trait']}
    - **Best Region**: {recommendation['Region']}
    - **Best Season**: {recommendation['Season']}
    """


def get_recommendation_summary(recommendations: List[Dict]) -> str:
    """
    Get a summary of all recommendations.
    
    Parameters:
    -----------
    recommendations : List[Dict]
        List of seed recommendations
    
    Returns:
    --------
    str : Summary string
    """
    if not recommendations:
        return "❌ No seed varieties found for the selected criteria."
    
    summary = f"✅ Found **{len(recommendations)}** recommended seed varieties:\n\n"
    for i, rec in enumerate(recommendations, 1):
        summary += f"{i}. **{rec['Variety']}** - {rec['Yield_t_ha']} t/ha yield\n"
    
    return summary


# ============================================================
# Testing and Validation
# ============================================================

if __name__ == "__main__":
    """Test the seed agent module"""
    
    print("🌾 Seed Intelligence Agent - Testing")
    print("=" * 50)
    
    # Test 1: Load dataset
    print("\n✓ Test 1: Loading seed dataset...")
    df = load_seed_dataset()
    if df is not None:
        print(f"  - Dataset loaded successfully!")
        print(f"  - Total records: {len(df)}")
        print(f"  - Columns: {', '.join(df.columns.tolist())}")
    else:
        print("  - Failed to load dataset")
    
    # Test 2: Get recommendations for a test crop
    print("\n✓ Test 2: Getting seed recommendations...")
    recommendations = get_seed_recommendations('rice', 'Punjab', 'Kharif', top_n=3)
    if recommendations:
        print(f"  - Found {len(recommendations)} recommendations")
        for rec in recommendations:
            print(f"    • {rec['Variety']}: {rec['Yield_t_ha']} t/ha")
    else:
        print("  - No recommendations found (dataset might not be loaded)")
    
    # Test 3: Get all crops
    print("\n✓ Test 3: Getting available crops...")
    crops = get_all_crops()
    if crops:
        print(f"  - Total crops: {len(crops)}")
        print(f"  - Sample crops: {', '.join(crops[:5])}")
    else:
        print("  - No crops found")
    
    print("\n" + "=" * 50)
    print("Testing complete!")
