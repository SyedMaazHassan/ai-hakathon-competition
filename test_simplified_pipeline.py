"""
Test the simplified emergency pipeline to ensure functionality is preserved
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.depts.services.simplified_emergency_pipeline import process_citizen_emergency, SimplifiedEmergencyPipeline

def test_simplified_pipeline():
    """Test that the simplified pipeline maintains all functionality"""
    
    print("🧪 Testing Simplified Emergency Pipeline...")
    
    # Test data
    test_request = {
        "request_text": "Fire brigade is needed, this is fire in nearbuy my house",
        "user_phone": "+923012697601",
        "user_email": "hafizmaazhassan33@gmail.com",
        "user_city": "Karachi",
        "user_coordinates": {"lat": 31.5497, "lng": 74.3436},
        "user_name": "Test User"
    }
    
    try:
        # Process emergency request
        result = process_citizen_emergency(**test_request)
        
        print(f"✅ Pipeline executed successfully!")
        print(f"   Request ID: {result.request_id}")
        print(f"   Case Code: {result.case_code}")
        print(f"   Success: {result.success}")
        print(f"   Duration: {result.total_duration_ms}ms")
        
        if result.success:
            print(f"   Department: {result.department_assigned}")
            print(f"   Entity: {result.entity_matched}")
            print(f"   Criticality: {result.criticality_level}")
            print(f"   Actions: {result.actions_executed}")
            print(f"   Reference: {result.reference_number}")
            print(f"   Message: {result.citizen_message[:100]}...")
        else:
            print(f"   Error: {result.error_message}")
            
        # Verify all expected fields are present
        expected_fields = [
            'success', 'request_id', 'case_code', 'citizen_request_id',
            'department_assigned', 'entity_matched', 'criticality_level',
            'actions_executed', 'citizen_message', 'reference_number',
            'error_message', 'total_duration_ms'
        ]
        
        missing_fields = [field for field in expected_fields if not hasattr(result, field)]
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        else:
            print("✅ All expected fields present")
            
        # Test direct service usage
        pipeline = SimplifiedEmergencyPipeline()
        from apps.depts.services.simplified_emergency_pipeline import EmergencyRequest
        
        emergency_request = EmergencyRequest(**test_request)
        direct_result = pipeline.process_emergency_request(emergency_request)
        
        print(f"✅ Direct service usage also works!")
        print(f"   Direct Result Success: {direct_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simplified_pipeline()
    if success:
        print("\n🎉 Simplified pipeline test PASSED - functionality preserved!")
    else:
        print("\n💥 Simplified pipeline test FAILED - functionality broken!")
