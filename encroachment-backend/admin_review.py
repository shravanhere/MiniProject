"""
MODULE 5: ADMIN REVIEW AND VERIFICATION
Allows admins to manually verify AI-detected encroachments

FUNCTIONS:
- View flagged encroachments
- Approve or reject detections
- Add remarks/notes
- Update status
- Track verification history

This ensures human validation and reduces false positives!
"""

from database import (
    get_pending_encroachments,
    get_encroachment,
    verify_encroachment,
    get_all_encroachments
)
from datetime import datetime

class AdminReview:
    """
    Handles admin review and verification of encroachments.
    """
    
    def __init__(self):
        pass
    
    def get_pending_reviews(self):
        """
        Get all encroachments waiting for admin review.
        Sorted by severity (high first).
        
        Returns:
            List of pending encroachment records
        """
        pending = get_pending_encroachments()
        
        # Sort by severity: high > medium > low
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        pending.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))
        
        return pending
    
    def get_review_details(self, encroachment_id):
        """
        Get detailed information about a specific encroachment.
        
        Args:
            encroachment_id: ID of encroachment to review
            
        Returns:
            Dictionary with complete encroachment details
        """
        encroachment = get_encroachment(encroachment_id)
        
        if not encroachment:
            return None
        
        # Add additional context
        review_info = {
            **encroachment,
            'requires_urgent_review': encroachment.get('severity') == 'high',
            'days_pending': self._calculate_days_pending(encroachment.get('created_at')),
        }
        
        return review_info
    
    def _calculate_days_pending(self, created_at):
        """
        Calculate how many days encroachment has been pending.
        
        Args:
            created_at: Creation timestamp string
            
        Returns:
            Number of days (integer)
        """
        if not created_at:
            return 0
        
        try:
            created = datetime.fromisoformat(created_at)
            now = datetime.now()
            delta = now - created
            return delta.days
        except:
            return 0
    
    def approve_encroachment(self, encroachment_id, admin_user_id, remarks=None):
        """
        Admin confirms the encroachment is valid.
        
        Args:
            encroachment_id: ID of encroachment
            admin_user_id: ID of admin user making decision
            remarks: Optional notes/comments
            
        Returns:
            Boolean indicating success
        """
        try:
            verify_encroachment(
                encroachment_id=encroachment_id,
                user_id=admin_user_id,
                status='confirmed',
                remarks=remarks or 'Encroachment confirmed by admin review'
            )
            return True
        except Exception as e:
            print(f"Error approving encroachment: {e}")
            return False
    
    def reject_encroachment(self, encroachment_id, admin_user_id, remarks=None):
        """
        Admin marks the detection as false positive.
        
        Args:
            encroachment_id: ID of encroachment
            admin_user_id: ID of admin user making decision
            remarks: Required - reason for rejection
            
        Returns:
            Boolean indicating success
        """
        try:
            verify_encroachment(
                encroachment_id=encroachment_id,
                user_id=admin_user_id,
                status='false_positive',
                remarks=remarks or 'Marked as false positive'
            )
            return True
        except Exception as e:
            print(f"Error rejecting encroachment: {e}")
            return False
    
    def request_site_visit(self, encroachment_id, admin_user_id, remarks=None):
        """
        Flag encroachment for physical site inspection.
        
        Args:
            encroachment_id: ID of encroachment
            admin_user_id: ID of admin user
            remarks: Details about site visit request
            
        Returns:
            Boolean indicating success
        """
        try:
            verify_encroachment(
                encroachment_id=encroachment_id,
                user_id=admin_user_id,
                status='site_visit_required',
                remarks=remarks or 'Site visit requested for verification'
            )
            return True
        except Exception as e:
            print(f"Error requesting site visit: {e}")
            return False
    
    def bulk_approve(self, encroachment_ids, admin_user_id, remarks=None):
        """
        Approve multiple encroachments at once.
        Useful for obvious cases.
        
        Args:
            encroachment_ids: List of encroachment IDs
            admin_user_id: ID of admin user
            remarks: Optional bulk approval note
            
        Returns:
            Dictionary with success count and failures
        """
        results = {
            'success_count': 0,
            'failed_ids': []
        }
        
        for enc_id in encroachment_ids:
            success = self.approve_encroachment(enc_id, admin_user_id, remarks)
            if success:
                results['success_count'] += 1
            else:
                results['failed_ids'].append(enc_id)
        
        return results
    
    def get_verification_statistics(self):
        """
        Get statistics about verification progress.
        
        Returns:
            Dictionary with verification stats
        """
        all_encroachments = get_all_encroachments()
        
        stats = {
            'total': len(all_encroachments),
            'pending': 0,
            'confirmed': 0,
            'false_positive': 0,
            'site_visit': 0,
            'by_severity': {'high': 0, 'medium': 0, 'low': 0}
        }
        
        for enc in all_encroachments:
            status = enc.get('status', 'pending')
            
            if status == 'pending':
                stats['pending'] += 1
            elif status == 'confirmed':
                stats['confirmed'] += 1
            elif status == 'false_positive':
                stats['false_positive'] += 1
            elif status == 'site_visit_required':
                stats['site_visit'] += 1
            
            # Count by severity (only for unverified)
            if status == 'pending' and enc.get('is_encroachment'):
                severity = enc.get('severity', 'low')
                if severity in stats['by_severity']:
                    stats['by_severity'][severity] += 1
        
        # Calculate percentages
        if stats['total'] > 0:
            stats['verified_percentage'] = ((stats['confirmed'] + stats['false_positive']) / stats['total']) * 100
        else:
            stats['verified_percentage'] = 0
        
        return stats
    
    def get_high_priority_cases(self, limit=10):
        """
        Get highest priority cases that need immediate review.
        
        Priorities:
        1. High severity + oldest first
        2. Multiple days pending
        3. Large overlap percentage
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of high-priority encroachment records
        """
        pending = get_pending_encroachments()
        
        # Score each encroachment
        for enc in pending:
            score = 0
            
            # Severity points
            if enc.get('severity') == 'high':
                score += 100
            elif enc.get('severity') == 'medium':
                score += 50
            
            # Age points (1 point per day)
            days = self._calculate_days_pending(enc.get('created_at'))
            score += days
            
            # Overlap points
            overlap = enc.get('overlap_percentage', 0)
            score += overlap
            
            enc['priority_score'] = score
        
        # Sort by priority score (highest first)
        pending.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        return pending[:limit]
    
    def add_review_note(self, encroachment_id, admin_user_id, note):
        """
        Add a note to an encroachment without changing status.
        Useful for keeping track of investigation progress.
        
        Args:
            encroachment_id: ID of encroachment
            admin_user_id: ID of admin user
            note: Note text
            
        Returns:
            Boolean indicating success
        """
        try:
            # Get current encroachment
            enc = get_encroachment(encroachment_id)
            if not enc:
                return False
            
            # Append note to existing remarks
            existing_remarks = enc.get('remarks', '')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            new_remarks = f"{existing_remarks}\n[{timestamp}] {note}".strip()
            
            # Update without changing status
            verify_encroachment(
                encroachment_id=encroachment_id,
                user_id=admin_user_id,
                status=enc.get('status', 'pending'),
                remarks=new_remarks
            )
            
            return True
        except Exception as e:
            print(f"Error adding note: {e}")
            return False


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_pending_for_review():
    """
    Quick function to get all pending reviews.
    
    Example:
        pending = get_pending_for_review()
        print(f"{len(pending)} cases waiting for review")
    """
    reviewer = AdminReview()
    return reviewer.get_pending_reviews()


def approve_case(encroachment_id, admin_id, remarks=None):
    """
    Quick approve function.
    
    Example:
        approve_case(5, admin_id=1, remarks="Verified through satellite imagery")
    """
    reviewer = AdminReview()
    return reviewer.approve_encroachment(encroachment_id, admin_id, remarks)


def reject_case(encroachment_id, admin_id, remarks):
    """
    Quick reject function.
    
    Example:
        reject_case(7, admin_id=1, remarks="Shadow misidentified as building")
    """
    reviewer = AdminReview()
    return reviewer.reject_encroachment(encroachment_id, admin_id, remarks)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == '__main__':
    """
    Test the admin review module
    Run with: python admin_review.py
    """
    
    print("\n" + "="*60)
    print("👨‍💼 ADMIN REVIEW MODULE - TEST")
    print("="*60 + "\n")
    
    print("NOTE: This module works with the database.")
    print("Make sure to run database.py first to initialize!\n")
    
    reviewer = AdminReview()
    
    # Test: Get pending reviews
    print("1. Getting pending reviews...")
    pending = reviewer.get_pending_reviews()
    print(f"   ✓ Found {len(pending)} pending reviews\n")
    
    # Test: Get statistics
    print("2. Getting verification statistics...")
    stats = reviewer.get_verification_statistics()
    print(f"   Total encroachments: {stats['total']}")
    print(f"   Pending: {stats['pending']}")
    print(f"   Confirmed: {stats['confirmed']}")
    print(f"   False positives: {stats['false_positive']}")
    print(f"   Verified: {stats['verified_percentage']:.1f}%\n")
    
    # Test: High priority cases
    print("3. Getting high-priority cases...")
    priority = reviewer.get_high_priority_cases(limit=5)
    print(f"   ✓ Found {len(priority)} high-priority cases\n")
    
    if priority:
        print("   Top priority case:")
        case = priority[0]
        print(f"     ID: {case.get('id')}")
        print(f"     Severity: {case.get('severity')}")
        print(f"     Priority Score: {case.get('priority_score', 0)}\n")
    
    print("="*60)
    print("✅ MODULE TEST PASSED!")
    print("="*60)
    print("\nFunctions available:")
    print("  - get_pending_reviews()")
    print("  - approve_encroachment()")
    print("  - reject_encroachment()")
    print("  - request_site_visit()")
    print("  - get_verification_statistics()")
    print("  - get_high_priority_cases()")
    print("="*60 + "\n")
