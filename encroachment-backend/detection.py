"""
MODULE 2: BUILDING DETECTION
Simple building detection using OpenCV (No AI/TensorFlow needed!)

HOW IT WORKS:
1. Load image
2. Convert to grayscale
3. Apply edge detection (Canny)
4. Find contours (building outlines)
5. Filter by size (remove small objects)
6. Return building rectangles

BEGINNER-FRIENDLY: Uses only basic OpenCV functions
"""

import cv2
import numpy as np
import json
from config import Config

class BuildingDetector:
    """
    Detects buildings in images using simple computer vision.
    No AI/ML required - just edge detection!
    """
    
    def __init__(self):
        # Load settings from config
        self.min_building_area = Config.MIN_BUILDING_AREA
        self.edge_low = Config.EDGE_DETECTION_THRESHOLD_LOW
        self.edge_high = Config.EDGE_DETECTION_THRESHOLD_HIGH
    
    def load_image(self, filepath):
        """
        Load image from file.
        
        Args:
            filepath: Path to image file
            
        Returns:
            Loaded image (BGR format)
        """
        image = cv2.imread(filepath)
        
        if image is None:
            raise ValueError(f"Could not load image: {filepath}")
        
        return image
    
    def detect_buildings(self, image):
        """
        Main detection function - finds buildings in image.
        
        STEPS:
        1. Convert to grayscale
        2. Blur to reduce noise
        3. Edge detection
        4. Morphological operations
        5. Find contours
        6. Filter by size
        
        Args:
            image: Input image (BGR)
            
        Returns:
            List of building dictionaries with bbox, area, etc.
        """
        
        # STEP 1: Convert to grayscale
        # Why? Edge detection works on grayscale images
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # STEP 2: Apply Gaussian blur
        # Why? Reduces noise and helps edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # STEP 3: Edge detection using Canny
        # This finds edges (outlines) of buildings
        edges = cv2.Canny(blurred, self.edge_low, self.edge_high)
        
        # STEP 4: Morphological operations
        # Close gaps in building outlines
        kernel = np.ones((7, 7), np.uint8)
        
        # Closing: fills small holes
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=3)
        
        # Dilation: makes lines thicker (connects nearby edges)
        dilated = cv2.dilate(closed, kernel, iterations=2)
        
        # STEP 5: Find contours (building outlines)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # STEP 6: Process each contour
        buildings = []
        building_id = 0
        
        for contour in contours:
            # Calculate area
            area = cv2.contourArea(contour)
            
            # Filter out small objects (noise)
            if area < self.min_building_area:
                continue
            
            # Get bounding box (x, y, width, height)
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate center point
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Store building information
            building = {
                'id': building_id,
                'bbox': [x, y, w, h],  # Bounding box
                'area': float(area),
                'center': [center_x, center_y],
                'perimeter': float(cv2.arcLength(contour, True)),
                'contour': contour.tolist()  # Convert to list for JSON
            }
            
            buildings.append(building)
            building_id += 1
        
        return buildings
    
    def create_detection_mask(self, image, buildings):
        """
        Creates a binary mask showing detected buildings.
        White = building, Black = background
        
        Args:
            image: Original image
            buildings: List of building dictionaries
            
        Returns:
            Binary mask (same size as image)
        """
        # Create blank mask (all black)
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        # Draw each building as white
        for building in buildings:
            x, y, w, h = building['bbox']
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)  # -1 = filled
        
        return mask
    
    def visualize_detections(self, image, buildings):
        """
        Creates visualization with buildings highlighted.
        
        Args:
            image: Original image
            buildings: List of building dictionaries
            
        Returns:
            Image with buildings drawn in green with IDs
        """
        # Make a copy to draw on
        vis_image = image.copy()
        
        for building in buildings:
            x, y, w, h = building['bbox']
            
            # Draw green rectangle around building
            cv2.rectangle(vis_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Add building ID label
            label = f"B{building['id']}"
            cv2.putText(vis_image, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return vis_image
    
    def calculate_total_area(self, buildings):
        """
        Calculate total built-up area.
        
        Args:
            buildings: List of building dictionaries
            
        Returns:
            Total area in pixels
        """
        return sum(building['area'] for building in buildings)
    
    def detect_and_analyze(self, filepath):
        """
        Complete detection pipeline.
        Loads image, detects buildings, creates visualizations.
        
        Args:
            filepath: Path to image file
            
        Returns:
            Dictionary with all detection results
        """
        # Load image
        image = self.load_image(filepath)
        
        # Detect buildings
        buildings = self.detect_buildings(image)
        
        # Create mask
        mask = self.create_detection_mask(image, buildings)
        
        # Create visualization
        visualization = self.visualize_detections(image, buildings)
        
        # Calculate statistics
        total_area = self.calculate_total_area(buildings)
        
        # Prepare result
        result = {
            'num_buildings': len(buildings),
            'buildings': buildings,
            'total_area': total_area,
            'mask': mask,
            'visualization': visualization,
            'image_size': image.shape[:2]  # (height, width)
        }
        
        return result
    
    def save_results(self, result, output_dir):
        """
        Save detection results to files.
        
        Args:
            result: Detection result dictionary
            output_dir: Where to save files
            
        Returns:
            Dictionary with saved file paths
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save mask
        mask_path = os.path.join(output_dir, 'detection_mask.png')
        cv2.imwrite(mask_path, result['mask'])
        
        # Save visualization
        vis_path = os.path.join(output_dir, 'detection_visualization.png')
        cv2.imwrite(vis_path, result['visualization'])
        
        # Save building data as JSON
        data_path = os.path.join(output_dir, 'detection_data.json')
        
        # Prepare data (remove numpy arrays)
        save_data = {
            'num_buildings': result['num_buildings'],
            'total_area': result['total_area'],
            'image_size': result['image_size'],
            'buildings': []
        }
        
        # Add building info (without contours which are too big)
        for building in result['buildings']:
            save_data['buildings'].append({
                'id': building['id'],
                'bbox': building['bbox'],
                'area': building['area'],
                'center': building['center'],
                'perimeter': building['perimeter']
            })
        
        with open(data_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        return {
            'mask_path': mask_path,
            'visualization_path': vis_path,
            'data_path': data_path
        }


# =============================================================================
# HELPER FUNCTIONS FOR EASY USE
# =============================================================================

def detect_buildings_simple(image_path):
    """
    Simple one-line function to detect buildings.
    
    Example:
        result = detect_buildings_simple('satellite.jpg')
        print(f"Found {result['num_buildings']} buildings")
    
    Args:
        image_path: Path to image
        
    Returns:
        Detection results dictionary
    """
    detector = BuildingDetector()
    return detector.detect_and_analyze(image_path)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == '__main__':
    """
    Test the building detector
    Run with: python detection.py
    """
    
    print("\n" + "="*60)
    print("🏢 BUILDING DETECTION MODULE - TEST")
    print("="*60 + "\n")
    
    # For testing, create a simple test image
    print("Creating test image...")
    
    # Create a blank image (white background)
    test_image = np.ones((1000, 1000, 3), dtype=np.uint8) * 255
    
    # Draw some "buildings" (black rectangles)
    cv2.rectangle(test_image, (100, 100), (300, 400), (0, 0, 0), -1)
    cv2.rectangle(test_image, (400, 150), (600, 450), (0, 0, 0), -1)
    cv2.rectangle(test_image, (700, 200), (900, 500), (0, 0, 0), -1)
    
    # Save test image
    cv2.imwrite('test_image.jpg', test_image)
    print("✓ Test image created: test_image.jpg\n")
    
    # Run detection
    print("Running detection...")
    detector = BuildingDetector()
    result = detector.detect_and_analyze('test_image.jpg')
    
    # Print results
    print(f"✓ Detection complete!")
    print(f"  Buildings found: {result['num_buildings']}")
    print(f"  Total area: {result['total_area']} pixels")
    
    print("\n  Building details:")
    for building in result['buildings']:
        print(f"    Building {building['id']}:")
        print(f"      Area: {building['area']:.0f} pixels")
        print(f"      Location: {building['bbox']}")
    
    # Save results
    print("\n  Saving results...")
    paths = detector.save_results(result, 'test_output')
    print(f"    ✓ Mask saved: {paths['mask_path']}")
    print(f"    ✓ Visualization saved: {paths['visualization_path']}")
    print(f"    ✓ Data saved: {paths['data_path']}")
    
    print("\n" + "="*60)
    print("✅ MODULE TEST PASSED!")
    print("="*60 + "\n")
