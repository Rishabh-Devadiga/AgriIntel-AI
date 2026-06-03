"""
Field Intelligence Module
==========================
This module provides image-based field analysis without requiring ML model training.
Uses simple image processing techniques to estimate vegetation coverage, soil moisture,
and calculate field health scores.

Author: ML Pipeline
Date: 2026
"""

import numpy as np
import streamlit as st
from PIL import Image
import io
import pandas as pd
from typing import Tuple, Optional


# ============================================================
# Vegetation Analysis
# ============================================================

def analyze_vegetation_coverage(image_array: np.ndarray) -> Tuple[float, str]:
    """
    Analyze vegetation coverage by detecting green pixels.
    
    Uses HSV color space for robust green detection across different
    lighting conditions.
    
    Parameters:
    -----------
    image_array : np.ndarray
        Image array in RGB format
    
    Returns:
    --------
    tuple : (vegetation_percentage, vegetation_level_label)
        vegetation_percentage: 0-100 (percentage of green pixels)
        vegetation_level_label: "Healthy", "Moderate", or "Low"
    """
    try:
        # Detect vegetation using a simple RGB heuristic so OpenCV is not required.
        red = image_array[:, :, 0].astype(np.int16)
        green = image_array[:, :, 1].astype(np.int16)
        blue = image_array[:, :, 2].astype(np.int16)

        green_mask = (
            (green > red + 12)
            & (green > blue + 8)
            & (green > 40)
        )
        
        # Calculate percentage of green pixels
        total_pixels = green_mask.size
        green_pixels = np.count_nonzero(green_mask)
        vegetation_percentage = (green_pixels / total_pixels) * 100
        
        # Classify vegetation level
        if vegetation_percentage > 50:
            level = "Healthy"
        elif vegetation_percentage > 25:
            level = "Moderate"
        else:
            level = "Low"
        
        return round(vegetation_percentage, 1), level
    
    except Exception as e:
        st.error(f"❌ Error analyzing vegetation: {str(e)}")
        return 0.0, "Unknown"


# ============================================================
# Moisture Analysis
# ============================================================

def analyze_soil_moisture(image_array: np.ndarray) -> Tuple[float, str]:
    """
    Estimate soil moisture using grayscale brightness analysis.
    
    Principle: Darker soil regions typically indicate higher moisture content.
    Lighter regions indicate drier soil.
    
    Parameters:
    -----------
    image_array : np.ndarray
        Image array in RGB format
    
    Returns:
    --------
    tuple : (moisture_score, moisture_level_label)
        moisture_score: 0-100 (estimated moisture percentage)
        moisture_level_label: "High", "Medium", or "Low"
    """
    try:
        # Convert to grayscale without OpenCV.
        gray_image = np.mean(image_array.astype(np.float32), axis=2)
        
        # Calculate average brightness (0-255 scale)
        avg_brightness = np.mean(gray_image)
        
        # Normalize to 0-100 scale (inverted: darker = more moisture)
        # Darker pixels (low brightness) = higher moisture
        # Lighter pixels (high brightness) = lower moisture
        moisture_score = 100 - (avg_brightness / 255 * 100)
        
        # Classify moisture level
        if moisture_score > 60:
            level = "High"
        elif moisture_score > 30:
            level = "Medium"
        else:
            level = "Low"
        
        return round(moisture_score, 1), level
    
    except Exception as e:
        st.error(f"❌ Error analyzing moisture: {str(e)}")
        return 0.0, "Unknown"


# ============================================================
# Field Health Calculation
# ============================================================

def calculate_field_health_score(
    vegetation_percentage: float,
    moisture_score: float
) -> Tuple[float, str]:
    """
    Calculate overall field health score.
    
    Formula: health_score = (vegetation_score * 0.6) + (moisture_score * 0.4)
    
    Weights:
    - Vegetation: 60% (primary indicator of field health)
    - Moisture: 40% (supporting indicator)
    
    Parameters:
    -----------
    vegetation_percentage : float
        Vegetation coverage percentage (0-100)
    moisture_score : float
        Estimated moisture score (0-100)
    
    Returns:
    --------
    tuple : (health_score, health_label)
        health_score: 0-10 (overall field health)
        health_label: "Healthy", "Moderate", or "Poor"
    """
    try:
        # Normalize vegetation to 0-10 scale
        vegetation_score = (vegetation_percentage / 10)
        
        # Normalize moisture to 0-10 scale
        moisture_normalized = (moisture_score / 10)
        
        # Calculate weighted health score
        health_score = (vegetation_score * 0.6) + (moisture_normalized * 0.4)
        
        # Classify health
        if health_score >= 7:
            label = "Healthy"
        elif health_score >= 4:
            label = "Moderate"
        else:
            label = "Poor"
        
        return round(health_score, 1), label
    
    except Exception as e:
        st.error(f"❌ Error calculating health score: {str(e)}")
        return 0.0, "Unknown"


# ============================================================
# Field Analysis Report
# ============================================================

def generate_field_report(
    seed_name: str,
    vegetation_percentage: float,
    vegetation_level: str,
    moisture_score: float,
    moisture_level: str,
    health_score: float,
    health_label: str
) -> dict:
    """
    Generate a comprehensive field analysis report.
    
    Parameters:
    -----------
    seed_name : str
        Name of seed/crop variety
    vegetation_percentage : float
        Vegetation coverage percentage
    vegetation_level : str
        Vegetation level classification
    moisture_score : float
        Estimated moisture score
    moisture_level : str
        Moisture level classification
    health_score : float
        Overall field health score
    health_label : str
        Health score classification
    
    Returns:
    --------
    dict : Comprehensive analysis report
    """
    report = {
        'seed_name': seed_name,
        'vegetation_coverage': vegetation_percentage,
        'vegetation_level': vegetation_level,
        'soil_moisture': moisture_score,
        'moisture_level': moisture_level,
        'health_score': health_score,
        'health_label': health_label,
        'timestamp': pd.Timestamp.now()
    }
    return report


if __name__ == "__main__":
    print("Field Intelligence Module loaded successfully")
