"""
MODULE 3: ENCROACHMENT CHECKING
Simple overlap detection between buildings and public zones

HOW IT WORKS:
1. Get building rectangles from detection
2. Check if they overlap with public zones
3. Calculate overlap percentage
4. Flag as encroachment if overlap > threshold

SIMPLE APPROACH:
- Uses rectangle coordinates (no complex geometry)
- Easy to understand and modify
"""

from config import Config

class EncroachmentChecker:
    """
    Checks if detected buildings overlap with public zones.
    """
    
    def __init__(self):
        # Load settings
        self.public_zones = Config.PUBLIC_ZONES
        self.overlap_threshold = Config.OVERLAP_THRESHOLD
    
    def calculate_rectangle_intersection(self, rect1, rect2):
        """
        Calculate intersection area between two rectangles.
        
        Args:
            rect1: (x, y, width, height) or [x, y, w, h]
            rect2: (x, y, width, height) or [x, y, w, h]
            
        Returns:
            Intersection area in pixels
        """
        # Extract coordinates
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        # Calculate corners
        rect1_right = x1 + w1
        rect1_bottom = y1 + h1
        rect2_right = x2 + w2
        rect2_bottom = y2 + h2
        
        # Find intersection boundaries
        intersect_left = max(x1, x2)
        intersect_top = max(y1, y2)
        intersect_right = min(rect1_right, rect2_right)
        intersect_bottom = min(rect1_bottom, rect2_bottom)
        
        # Calculate intersection dimensions
        intersect_width = max(0, intersect_right - intersect_left)
        intersect_height = max(0, intersect_bottom - intersect_top)
        
        # Calculate area
        intersection_area = intersect_width * intersect_height
        
        return intersection_area
    
    def check_building_overlap(self, building):
        """
        Check if a building overlaps with any public zone.
        
        Args:
            building: Dictionary with 'bbox' key [x, y, w, h]
            
        Returns:
            List of overlaps (one per zone that overlaps)
        """
        overlaps = []
        
        # Get building rectangle
        building_bbox = building['bbox']
        building_area = building['area']
        
        # Check against each public zone
        for zone in self.public_zones:
            # Get zone coordinates
            zone_x, zone_y, zone_x2, zone_y2 = zone['coordinates']
            zone_width = zone_x2 - zone_x
            zone_height = zone_y2 - zone_y
            zone_rect = (zone_x, zone_y, zone_width, zone_height)
            
            # Calculate intersection
            intersection_area = self.calculate_rectangle_intersection(
                building_bbox, 
                zone_rect
            )
            
            # If there's overlap
            if intersection_area > 0:
                # Calculate overlap percentage
                overlap_percentage = (intersection_area / building_area) * 100
                
                # Store overlap info
                overlap = {
                    'zone_name': zone['name'],
                    'zone_type': zone['type'],
                    'intersection_area': float(intersection_area),
                    'overlap_percentage': float(overlap_percentage),
                    'zone_coordinates': zone['coordinates']
                }
                
                overlaps.append(overlap)
        
        return overlaps
    
    def determine_severity(self, overlap_percentage):
        """
        Determine encroachment severity based on overlap.
        
        Args:
            overlap_percentage: How much building overlaps (0-100)
            
        Returns:
            Severity level: 'low', 'medium', 'high'
        """
        if overlap_percentage >= 50:
            return 'high'
        elif overlap_percentage >= 25:
            return 'medium'
        else:
            return 'low'
    
    def check_encroachments(self, buildings):
        """
        Check all buildings for encroachments.
        
        Args:
            buildings: List of building dictionaries from detection
            
        Returns:
            List of encroachment records
        """
        encroachments = []
        
        for building in buildings:
            # Check this building
            overlaps = self.check_building_overlap(building)
            
            # If building overlaps any public zone
            if overlaps:
                for overlap in overlaps:
                    overlap_pct = overlap['overlap_percentage']
                    
                    # Only flag if overlap exceeds threshold
                    is_encroachment = overlap_pct >= self.overlap_threshold
                    
                    if is_encroachment:
                        # Create encroachment record
                        encroachment = {
                            'building_id': building['id'],
                            'building_bbox': building['bbox'],
                            'building_area': building['area'],
                            'building_center': building['center'],
                            'zone_name': overlap['zone_name'],
                            'zone_type': overlap['zone_type'],
                            'intersection_area': overlap['intersection_area'],
                            'overlap_percentage': overlap_pct,
                            'severity': self.determine_severity(overlap_pct),
                            'is_encroachment': True
                        }
                        
                        encroachments.append(encroachment)
        
        return encroachments
    
    def generate_summary(self, encroachments):
        """
        Generate summary statistics for encroachments.
        
        Args:
            encroachments: List of encroachment records
            
        Returns:
            Summary dictionary
        """
        if not encroachments:
            return {
                'total_encroachments': 0,
                'severity_breakdown': {'high': 0, 'medium': 0, 'low': 0},
                'affected_zones': [],
                'total_intersection_area': 0
            }
        
        # Count by severity
        severity_count = {'high': 0, 'medium': 0, 'low': 0}
        for enc in encroachments:
            severity_count[enc['severity']] += 1
        
        # Get unique affected zones
        affected_zones = list(set(enc['zone_name'] for enc in encroachments))
        
        # Calculate total intersection area
        total_area = sum(enc['intersection_area'] for enc in encroachments)
        
        summary = {
            'total_encroachments': len(encroachments),
            'severity_breakdown': severity_count,
            'affected_zones': affected_zones,
            'total_intersection_area': float(total_area)
        }
        
        return summary
    
    def analyze_image_detections(self, detection_result):
        """
        Complete analysis: check all buildings from detection.
        
        Args:
            detection_result: Result from BuildingDetector
            
        Returns:
            Complete analysis with encroachments and summary
        """
        buildings = detection_result['buildings']
        
        # Check for encroachments
        encroachments = self.check_encroachments(buildings)
        
        # Generate summary
        summary = self.generate_summary(encroachments)
        
        # Prepare full result
        result = {
            'total_buildings': detection_result['num_buildings'],
            'total_encroachments': summary['total_encroachments'],
            'encroachments': encroachments,
            'summary': summary,
            'public_zones_checked': len(self.public_zones)
        }
        
        return result


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def check_encroachment_simple(detection_result):
    """
    Simple one-line function to check encroachments.
    
    Example:
        detection = detect_buildings_simple('image.jpg')
        result = check_encroachment_simple(detection)
        print(f"Found {result['total_encroachments']} encroachments")
    
    Args:
        detection_result: Output from BuildingDetector
        
    Returns:
        Encroachment analysis results
    """
    checker = EncroachmentChecker()
    return checker.analyze_image_detections(detection_result)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == '__main__':
    """
    Test the encroachment checker
    Run with: python encroachment.py
    """
    
    print("\n" + "="*60)
    print("⚠️  ENCROACHMENT CHECKER MODULE - TEST")
    print("="*60 + "\n")
    
    # Create sample buildings (simulating detection results)
    sample_buildings = [
        {
            'id': 0,
            'bbox': [150, 150, 200, 200],  # Overlaps Park Zone
            'area': 40000,
            'center': [250, 250]
        },
        {
            'id': 1,
            'bbox': [650, 150, 200, 200],  # Overlaps Government Zone
            'area': 40000,
            'center': [750, 250]
        },
        {
            'id': 2,
            'bbox': [1100, 150, 200, 200],  # No overlap (outside zones)
            'area': 40000,
            'center': [1200, 250]
        }
    ]
    
    sample_detection = {
        'num_buildings': len(sample_buildings),
        'buildings': sample_buildings,
        'total_area': 120000
    }
    
    print(f"Testing with {len(sample_buildings)} sample buildings...")
    print(f"Public zones configured: {len(Config.PUBLIC_ZONES)}\n")
    
    # Run encroachment check
    checker = EncroachmentChecker()
    result = checker.analyze_image_detections(sample_detection)
    
    # Print results
    print("Results:")
    print(f"  Total buildings checked: {result['total_buildings']}")
    print(f"  Encroachments found: {result['total_encroachments']}")
    
    if result['total_encroachments'] > 0:
        print("\n  Severity breakdown:")
        for severity, count in result['summary']['severity_breakdown'].items():
            if count > 0:
                print(f"    {severity.upper()}: {count}")
        
        print("\n  Affected zones:")
        for zone in result['summary']['affected_zones']:
            print(f"    - {zone}")
        
        print("\n  Encroachment details:")
        for enc in result['encroachments']:
            print(f"\n    Building {enc['building_id']}:")
            print(f"      Zone: {enc['zone_name']}")
            print(f"      Overlap: {enc['overlap_percentage']:.1f}%")
            print(f"      Severity: {enc['severity']}")
    else:
        print("  No encroachments detected!")
    
    print("\n" + "="*60)
    print("✅ MODULE TEST PASSED!")
    print("="*60 + "\n")
