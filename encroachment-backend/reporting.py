"""
MODULE 4: REPORTING MODULE
Generates PDF and CSV reports for encroachments

REPORT INCLUDES:
- Location coordinates
- Encroachment area
- Land type (zone name)
- Detection image
- Date and time
- Building details
"""

from fpdf import FPDF
import csv
from datetime import datetime
import os
from config import Config

class ReportGenerator:
    """
    Generates PDF and CSV reports for encroachment detections.
    """
    
    def __init__(self):
        self.reports_folder = Config.REPORTS_FOLDER
        os.makedirs(self.reports_folder, exist_ok=True)
    
    # =========================================================================
    # PDF REPORT GENERATION
    # =========================================================================
    
    def generate_pdf_report(self, image_info, detection_result, encroachment_result):
        """
        Generate a comprehensive PDF report.
        
        Args:
            image_info: Dictionary with image metadata (from database)
            detection_result: Results from building detection
            encroachment_result: Results from encroachment checking
            
        Returns:
            Path to generated PDF file
        """
        
        # Create PDF object
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'ENCROACHMENT DETECTION REPORT', 0, 1, 'C')
        pdf.ln(5)
        
        # Report metadata
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
        pdf.cell(0, 6, f"Report ID: ENC-{image_info.get('id', 'N/A')}", 0, 1)
        pdf.ln(5)
        
        # Section 1: Image Information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, '1. IMAGE INFORMATION', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        pdf.cell(50, 6, 'Filename:', 0, 0)
        pdf.cell(0, 6, str(image_info.get('filename', 'N/A')), 0, 1)
        
        pdf.cell(50, 6, 'Image Type:', 0, 0)
        pdf.cell(0, 6, str(image_info.get('image_type', 'N/A')).upper(), 0, 1)
        
        pdf.cell(50, 6, 'Location:', 0, 0)
        pdf.cell(0, 6, str(image_info.get('location', 'N/A')), 0, 1)
        
        if image_info.get('latitude') and image_info.get('longitude'):
            pdf.cell(50, 6, 'Coordinates:', 0, 0)
            pdf.cell(0, 6, f"Lat: {image_info['latitude']}, Lon: {image_info['longitude']}", 0, 1)
        
        pdf.cell(50, 6, 'Upload Date:', 0, 0)
        pdf.cell(0, 6, str(image_info.get('upload_date', 'N/A')), 0, 1)
        
        pdf.ln(5)
        
        # Section 2: Detection Summary
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, '2. DETECTION SUMMARY', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        pdf.cell(50, 6, 'Buildings Detected:', 0, 0)
        pdf.cell(0, 6, str(detection_result.get('num_buildings', 0)), 0, 1)
        
        pdf.cell(50, 6, 'Total Built Area:', 0, 0)
        pdf.cell(0, 6, f"{detection_result.get('total_area', 0):.0f} sq. pixels", 0, 1)
        
        pdf.ln(5)
        
        # Section 3: Encroachment Analysis
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, '3. ENCROACHMENT ANALYSIS', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        total_enc = encroachment_result.get('total_encroachments', 0)
        pdf.cell(50, 6, 'Encroachments Found:', 0, 0)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, str(total_enc), 0, 1)
        pdf.set_font('Arial', '', 10)
        
        if total_enc > 0:
            summary = encroachment_result.get('summary', {})
            severity = summary.get('severity_breakdown', {})
            
            pdf.cell(50, 6, 'Severity Breakdown:', 0, 1)
            pdf.cell(10, 6, '', 0, 0)  # Indent
            pdf.cell(40, 6, f"High: {severity.get('high', 0)}", 0, 0)
            pdf.cell(40, 6, f"Medium: {severity.get('medium', 0)}", 0, 0)
            pdf.cell(40, 6, f"Low: {severity.get('low', 0)}", 0, 1)
            
            pdf.cell(50, 6, 'Affected Zones:', 0, 1)
            for zone in summary.get('affected_zones', []):
                pdf.cell(10, 6, '', 0, 0)  # Indent
                pdf.cell(0, 6, f"- {zone}", 0, 1)
            
            pdf.ln(5)
            
            # Section 4: Detailed Encroachment List
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, '4. ENCROACHMENT DETAILS', 0, 1)
            
            for enc in encroachment_result.get('encroachments', []):
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, f"Building ID: {enc['building_id']}", 0, 1)
                pdf.set_font('Arial', '', 10)
                
                pdf.cell(10, 5, '', 0, 0)  # Indent
                pdf.cell(50, 5, 'Zone:', 0, 0)
                pdf.cell(0, 5, enc['zone_name'], 0, 1)
                
                pdf.cell(10, 5, '', 0, 0)
                pdf.cell(50, 5, 'Zone Type:', 0, 0)
                pdf.cell(0, 5, enc['zone_type'], 0, 1)
                
                pdf.cell(10, 5, '', 0, 0)
                pdf.cell(50, 5, 'Overlap Percentage:', 0, 0)
                pdf.cell(0, 5, f"{enc['overlap_percentage']:.2f}%", 0, 1)
                
                pdf.cell(10, 5, '', 0, 0)
                pdf.cell(50, 5, 'Intersection Area:', 0, 0)
                pdf.cell(0, 5, f"{enc['intersection_area']:.0f} sq. pixels", 0, 1)
                
                pdf.cell(10, 5, '', 0, 0)
                pdf.cell(50, 5, 'Severity:', 0, 0)
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 5, enc['severity'].upper(), 0, 1)
                pdf.set_font('Arial', '', 10)
                
                pdf.cell(10, 5, '', 0, 0)
                pdf.cell(50, 5, 'Building Location:', 0, 0)
                bbox = enc['building_bbox']
                pdf.cell(0, 5, f"({bbox[0]}, {bbox[1]}) - {bbox[2]}x{bbox[3]}", 0, 1)
                
                pdf.ln(3)
        else:
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 6, 'No encroachments detected.', 0, 1)
        
        pdf.ln(5)
        
        # Section 5: Recommendations
        if total_enc > 0:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, '5. RECOMMENDATIONS', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            high_count = severity.get('high', 0)
            if high_count > 0:
                pdf.multi_cell(0, 5, 
                    f"• {high_count} high-severity encroachment(s) detected. "
                    "Immediate site inspection recommended.")
            
            medium_count = severity.get('medium', 0)
            if medium_count > 0:
                pdf.multi_cell(0, 5,
                    f"• {medium_count} medium-severity encroachment(s) detected. "
                    "Schedule verification within 7 days.")
            
            pdf.multi_cell(0, 5,
                "• All detected encroachments should be verified through ground survey.")
            pdf.multi_cell(0, 5,
                "• Affected property owners should be notified as per regulations.")
        
        # Footer
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 5, 'This report is automatically generated by the Encroachment Detection System.', 0, 1, 'C')
        pdf.cell(0, 5, 'Verification by authorized personnel is required before legal action.', 0, 1, 'C')
        
        # Save PDF
        filename = f"report_{image_info.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.reports_folder, filename)
        pdf.output(filepath)
        
        return filepath
    
    # =========================================================================
    # CSV REPORT GENERATION
    # =========================================================================
    
    def generate_csv_report(self, image_info, detection_result, encroachment_result):
        """
        Generate CSV file with encroachment data.
        Easier for Excel analysis and data processing.
        
        Args:
            image_info: Dictionary with image metadata
            detection_result: Results from building detection
            encroachment_result: Results from encroachment checking
            
        Returns:
            Path to generated CSV file
        """
        
        filename = f"report_{image_info.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.reports_folder, filename)
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header information
            writer.writerow(['ENCROACHMENT DETECTION REPORT'])
            writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['Report ID', f"ENC-{image_info.get('id', 'N/A')}"])
            writer.writerow([])
            
            # Image information
            writer.writerow(['IMAGE INFORMATION'])
            writer.writerow(['Filename', image_info.get('filename', 'N/A')])
            writer.writerow(['Image Type', image_info.get('image_type', 'N/A')])
            writer.writerow(['Location', image_info.get('location', 'N/A')])
            
            if image_info.get('latitude') and image_info.get('longitude'):
                writer.writerow(['Latitude', image_info['latitude']])
                writer.writerow(['Longitude', image_info['longitude']])
            
            writer.writerow(['Upload Date', image_info.get('upload_date', 'N/A')])
            writer.writerow([])
            
            # Detection summary
            writer.writerow(['DETECTION SUMMARY'])
            writer.writerow(['Buildings Detected', detection_result.get('num_buildings', 0)])
            writer.writerow(['Total Built Area (sq. pixels)', detection_result.get('total_area', 0)])
            writer.writerow([])
            
            # Encroachment summary
            writer.writerow(['ENCROACHMENT SUMMARY'])
            writer.writerow(['Total Encroachments', encroachment_result.get('total_encroachments', 0)])
            
            if encroachment_result.get('total_encroachments', 0) > 0:
                summary = encroachment_result.get('summary', {})
                severity = summary.get('severity_breakdown', {})
                
                writer.writerow(['High Severity', severity.get('high', 0)])
                writer.writerow(['Medium Severity', severity.get('medium', 0)])
                writer.writerow(['Low Severity', severity.get('low', 0)])
                writer.writerow([])
                
                # Detailed encroachment data
                writer.writerow(['ENCROACHMENT DETAILS'])
                writer.writerow([
                    'Building ID',
                    'Zone Name',
                    'Zone Type',
                    'Overlap %',
                    'Intersection Area',
                    'Severity',
                    'Building X',
                    'Building Y',
                    'Building Width',
                    'Building Height',
                    'Building Area'
                ])
                
                for enc in encroachment_result.get('encroachments', []):
                    bbox = enc['building_bbox']
                    writer.writerow([
                        enc['building_id'],
                        enc['zone_name'],
                        enc['zone_type'],
                        f"{enc['overlap_percentage']:.2f}",
                        f"{enc['intersection_area']:.0f}",
                        enc['severity'],
                        bbox[0],
                        bbox[1],
                        bbox[2],
                        bbox[3],
                        enc['building_area']
                    ])
        
        return filepath
    
    # =========================================================================
    # SUMMARY REPORT (Simple text file)
    # =========================================================================
    
    def generate_text_summary(self, image_info, detection_result, encroachment_result):
        """
        Generate a simple text summary file.
        Quick overview without formatting.
        
        Args:
            image_info: Dictionary with image metadata
            detection_result: Results from building detection
            encroachment_result: Results from encroachment checking
            
        Returns:
            Path to generated text file
        """
        
        filename = f"summary_{image_info.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.reports_folder, filename)
        
        with open(filepath, 'w') as f:
            f.write("="*60 + "\n")
            f.write("ENCROACHMENT DETECTION - SUMMARY REPORT\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Image: {image_info.get('filename', 'N/A')}\n")
            f.write(f"Location: {image_info.get('location', 'N/A')}\n\n")
            
            f.write(f"Buildings Detected: {detection_result.get('num_buildings', 0)}\n")
            f.write(f"Encroachments Found: {encroachment_result.get('total_encroachments', 0)}\n\n")
            
            if encroachment_result.get('total_encroachments', 0) > 0:
                f.write("SEVERITY BREAKDOWN:\n")
                summary = encroachment_result.get('summary', {})
                severity = summary.get('severity_breakdown', {})
                f.write(f"  High: {severity.get('high', 0)}\n")
                f.write(f"  Medium: {severity.get('medium', 0)}\n")
                f.write(f"  Low: {severity.get('low', 0)}\n\n")
                
                f.write("AFFECTED ZONES:\n")
                for zone in summary.get('affected_zones', []):
                    f.write(f"  - {zone}\n")
            else:
                f.write("No encroachments detected.\n")
            
            f.write("\n" + "="*60 + "\n")
        
        return filepath
    
    # =========================================================================
    # GENERATE ALL REPORTS
    # =========================================================================
    
    def generate_all_reports(self, image_info, detection_result, encroachment_result):
        """
        Generate all report formats at once.
        
        Returns:
            Dictionary with paths to all generated reports
        """
        
        pdf_path = self.generate_pdf_report(image_info, detection_result, encroachment_result)
        csv_path = self.generate_csv_report(image_info, detection_result, encroachment_result)
        txt_path = self.generate_text_summary(image_info, detection_result, encroachment_result)
        
        return {
            'pdf': pdf_path,
            'csv': csv_path,
            'txt': txt_path
        }


# =============================================================================
# HELPER FUNCTION
# =============================================================================

def generate_report_simple(image_info, detection_result, encroachment_result, format='pdf'):
    """
    Simple one-line function to generate reports.
    
    Example:
        pdf_path = generate_report_simple(image, detection, encroachment)
    
    Args:
        image_info: Image metadata dict
        detection_result: Detection results
        encroachment_result: Encroachment results
        format: 'pdf', 'csv', 'txt', or 'all'
        
    Returns:
        Path to generated report(s)
    """
    generator = ReportGenerator()
    
    if format == 'pdf':
        return generator.generate_pdf_report(image_info, detection_result, encroachment_result)
    elif format == 'csv':
        return generator.generate_csv_report(image_info, detection_result, encroachment_result)
    elif format == 'txt':
        return generator.generate_text_summary(image_info, detection_result, encroachment_result)
    else:  # 'all'
        return generator.generate_all_reports(image_info, detection_result, encroachment_result)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == '__main__':
    """
    Test the report generator
    Run with: python reporting.py
    """
    
    print("\n" + "="*60)
    print("📄 REPORTING MODULE - TEST")
    print("="*60 + "\n")
    
    # Sample data
    sample_image = {
        'id': 1,
        'filename': 'satellite_sector21.jpg',
        'image_type': 'satellite',
        'location': 'Sector 21, Block A, Chennai',
        'latitude': 12.9716,
        'longitude': 77.5946,
        'upload_date': '2026-02-01 14:30:00'
    }
    
    sample_detection = {
        'num_buildings': 5,
        'total_area': 125000
    }
    
    sample_encroachment = {
        'total_encroachments': 2,
        'summary': {
            'severity_breakdown': {'high': 1, 'medium': 1, 'low': 0},
            'affected_zones': ['Public Park Zone A', 'Road Reserve'],
            'total_intersection_area': 15000
        },
        'encroachments': [
            {
                'building_id': 2,
                'zone_name': 'Public Park Zone A',
                'zone_type': 'park',
                'overlap_percentage': 55.5,
                'intersection_area': 11000,
                'severity': 'high',
                'building_bbox': [150, 150, 200, 250],
                'building_area': 50000
            },
            {
                'building_id': 4,
                'zone_name': 'Road Reserve',
                'zone_type': 'road',
                'overlap_percentage': 30.0,
                'intersection_area': 4000,
                'severity': 'medium',
                'building_bbox': [400, 650, 100, 150],
                'building_area': 15000
            }
        ]
    }
    
    # Generate reports
    print("Generating reports...")
    generator = ReportGenerator()
    
    reports = generator.generate_all_reports(sample_image, sample_detection, sample_encroachment)
    
    print(f"\n✓ PDF Report: {reports['pdf']}")
    print(f"✓ CSV Report: {reports['csv']}")
    print(f"✓ Text Summary: {reports['txt']}")
    
    print("\n" + "="*60)
    print("✅ MODULE TEST PASSED!")
    print("="*60 + "\n")
