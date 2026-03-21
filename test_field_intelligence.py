"""
Quick test of Field Intelligence module
"""

import numpy as np
from field_intelligence import (
    analyze_vegetation_coverage,
    analyze_soil_moisture,
    calculate_field_health_score
)

print("🧪 Testing Field Intelligence Module")
print("=" * 60)

# Create a test image (simulated field)
# 70% green vegetation, 30% brown soil
test_image = np.zeros((100, 100, 3), dtype=np.uint8)

# Add green areas (HSV: H=60, S=255, V=255 = bright green)
test_image[:70, :, :] = [0, 255, 0]  # Green plants
test_image[70:, :, :] = [139, 69, 19]  # Brown soil

print("\n✅ Test 1: Vegetation Coverage Analysis")
vegetation_pct, vegetation_level = analyze_vegetation_coverage(test_image)
print(f"   Vegetation Coverage: {vegetation_pct}%")
print(f"   Vegetation Level: {vegetation_level}")
assert vegetation_level in ["Healthy", "Moderate", "Low"], "Invalid vegetation level"
print("   ✓ PASSED")

print("\n✅ Test 2: Soil Moisture Estimation")
moisture_score, moisture_level = analyze_soil_moisture(test_image)
print(f"   Moisture Score: {int(moisture_score)}%")
print(f"   Moisture Level: {moisture_level}")
assert moisture_level in ["High", "Medium", "Low"], "Invalid moisture level"
print("   ✓ PASSED")

print("\n✅ Test 3: Field Health Score Calculation")
health_score, health_label = calculate_field_health_score(vegetation_pct, moisture_score)
print(f"   Health Score: {health_score}/10")
print(f"   Health Label: {health_label}")
assert 0 <= health_score <= 10, "Invalid health score range"
assert health_label in ["Healthy", "Moderate", "Poor"], "Invalid health label"
print("   ✓ PASSED")

print("\n✅ Test 4: Different Scenarios")

# Scenario 1: Low vegetation, low moisture (poor field)
poor_image = np.ones((100, 100, 3), dtype=np.uint8) * 200  # All gray/light
veg_pct, _ = analyze_vegetation_coverage(poor_image)
moist, _ = analyze_soil_moisture(poor_image)
health, label = calculate_field_health_score(veg_pct, moist)
print(f"   Poor Field: Health={health}/10 ({label})")
assert label == "Poor", "Should be classified as Poor"
print("   ✓ PASSED")

# Scenario 2: High vegetation, high moisture (healthy field)
healthy_image = np.zeros((100, 100, 3), dtype=np.uint8)
healthy_image[:90, :, :] = [0, 255, 0]  # 90% green
healthy_image[90:, :, :] = [50, 50, 50]  # 10% dark soil
veg_pct, _ = analyze_vegetation_coverage(healthy_image)
moist, _ = analyze_soil_moisture(healthy_image)
health, label = calculate_field_health_score(veg_pct, moist)
print(f"   Healthy Field: Health={health}/10 ({label})")
assert label == "Healthy", "Should be classified as Healthy"
print("   ✓ PASSED")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - Field Intelligence Module is Ready!")
print("=" * 60)
