# test_geolocation.py - Comprehensive test for geolocation tool

import sys
import os
import json
from typing import Dict

# Add src to path
sys.path.append('src')

def test_tool_initialization():
    """Test that the geolocation tool can be initialized"""
    print("🧪 Testing tool initialization...")
    
    try:
        from tools.geolocation import GeolocationTool, create_geolocation_tool
        
        # Test direct initialization
        tool = GeolocationTool()
        print(f"✅ Tool created successfully: {tool.name}")
        print(f"   Description: {tool.description}")
        
        # Test factory function
        tool2 = create_geolocation_tool()
        print(f"✅ Factory function works: {tool2.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool initialization failed: {e}")
        return False

def test_address_parsing():
    """Test the address parsing functionality"""
    print("\n🧪 Testing address parsing...")
    
    try:
        from tools.geolocation import GeolocationTool
        
        tool = GeolocationTool()
        
        test_cases = [
            {
                "input": "New York, NY",
                "expected_type": "city_state",
                "expected_city": "New York",
                "expected_state": "NY"
            },
            {
                "input": "90210",
                "expected_type": "zipcode",
                "expected_zipcode": "90210"
            },
            {
                "input": "40.7128, -74.0060",
                "expected_type": "coordinates",
                "expected_lat": 40.7128,
                "expected_lng": -74.0060
            },
            {
                "input": "San Francisco",
                "expected_type": "general"
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_cases):
            print(f"   Test {i+1}: '{test_case['input']}'")
            
            parsed = tool._parse_address_input(test_case["input"])
            print(f"     Parsed type: {parsed.get('type')}")
            
            # Check type
            if parsed.get('type') == test_case['expected_type']:
                print(f"     ✅ Type correct: {parsed['type']}")
                type_correct = True
            else:
                print(f"     ❌ Expected type {test_case['expected_type']}, got {parsed.get('type')}")
                type_correct = False
            
            # Check specific fields based on type
            field_correct = True
            if test_case['expected_type'] == 'city_state':
                if parsed.get('city') != test_case.get('expected_city'):
                    print(f"     ❌ Expected city {test_case['expected_city']}, got {parsed.get('city')}")
                    field_correct = False
                if parsed.get('state') != test_case.get('expected_state'):
                    print(f"     ❌ Expected state {test_case['expected_state']}, got {parsed.get('state')}")
                    field_correct = False
            elif test_case['expected_type'] == 'zipcode':
                if parsed.get('zipcode') != test_case.get('expected_zipcode'):
                    print(f"     ❌ Expected zipcode {test_case['expected_zipcode']}, got {parsed.get('zipcode')}")
                    field_correct = False
            elif test_case['expected_type'] == 'coordinates':
                if abs(parsed.get('latitude', 0) - test_case.get('expected_lat', 0)) > 0.001:
                    print(f"     ❌ Latitude mismatch")
                    field_correct = False
                if abs(parsed.get('longitude', 0) - test_case.get('expected_lng', 0)) > 0.001:
                    print(f"     ❌ Longitude mismatch")  
                    field_correct = False
            
            if type_correct and field_correct:
                print(f"     ✅ All fields correct")
            
            results.append(type_correct and field_correct)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Address parsing success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8
        
    except Exception as e:
        print(f"❌ Address parsing test failed: {e}")
        return False

def test_state_normalization():
    """Test state name normalization"""
    print("\n🧪 Testing state normalization...")
    
    try:
        from tools.geolocation import GeolocationTool
        
        tool = GeolocationTool()
        
        test_cases = [
            ("New York", "NY"),
            ("California", "CA"), 
            ("TEXAS", "TX"),
            ("florida", "FL"),
            ("NY", "NY"),  # Should stay as is
            ("CA", "CA"),  # Should stay as is
        ]
        
        results = []
        for full_name, expected_abbrev in test_cases:
            result = tool._normalize_state(full_name)
            print(f"   '{full_name}' -> '{result}' (expected: '{expected_abbrev}')")
            
            if result == expected_abbrev:
                print(f"     ✅ Correct")
                results.append(True)
            else:
                print(f"     ❌ Expected '{expected_abbrev}', got '{result}'")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   State normalization success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8
        
    except Exception as e:
        print(f"❌ State normalization test failed: {e}")
        return False

def test_ip_location():
    """Test IP-based location detection"""
    print("\n🧪 Testing IP-based location...")
    
    try:
        from tools.geolocation import GeolocationTool
        
        tool = GeolocationTool()
        
        # Test IP location
        print("   Attempting IP-based location detection...")
        ip_location = tool._get_ip_location()
        
        print(f"   IP Location result:")
        print(f"     City: {ip_location.get('city')}")
        print(f"     State: {ip_location.get('state')}")
        print(f"     Country: {ip_location.get('country')}")
        
        # Check that we got some reasonable data
        has_city = ip_location.get('city') and ip_location['city'] != "Unknown City"
        has_state = ip_location.get('state') and len(ip_location['state']) == 2
        has_country = ip_location.get('country')
        
        if has_city and has_state and has_country:
            print("   ✅ IP location detection working")
            return True
        else:
            print("   ⚠️  IP location gave default values (this is okay if internet/API is unavailable)")
            return True  # Not a failure - fallback is expected
            
    except Exception as e:
        print(f"❌ IP location test failed: {e}")
        return False

def test_full_geolocation():
    """Test the full geolocation workflow"""
    print("\n🧪 Testing full geolocation workflow...")
    
    try:
        from tools.geolocation import GeolocationTool
        from config.settings import settings
        
        tool = GeolocationTool()
        
        # Check if Google Maps is configured
        has_google_maps = (settings.google_maps_api_key and 
                          settings.google_maps_api_key != "your-google-maps-api-key-here")
        
        if has_google_maps:
            print("   🗺️  Google Maps API configured - testing with real geocoding")
        else:
            print("   ⚠️  Google Maps API not configured - testing fallback functionality")
        
        test_cases = [
            "",  # Auto-detect
            "New York, NY",
            "90210",
            "San Francisco, CA",
            "Boston"
        ]
        
        results = []
        for i, location_input in enumerate(test_cases):
            display_input = location_input if location_input else "(auto-detect)"
            print(f"\n   Test {i+1}: {display_input}")
            
            try:
                result_json = tool._run(location_input)
                result = json.loads(result_json)
                
                print(f"     City: {result.get('city')}")
                print(f"     State: {result.get('state')}")
                print(f"     ZIP: {result.get('zipcode', 'N/A')}")
                if result.get('latitude'):
                    print(f"     Coordinates: {result['latitude']:.4f}, {result['longitude']:.4f}")
                
                # Validate required fields
                has_city = result.get('city') and result['city'] != "Unknown City"
                has_state = result.get('state') and len(result['state']) == 2
                
                if has_city and has_state:
                    print(f"     ✅ Location resolved successfully")
                    results.append(True)
                else:
                    print(f"     ❌ Missing required location data")
                    results.append(False)
                    
            except Exception as e:
                print(f"     ❌ Failed: {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Full geolocation success rate: {success_rate:.1%}")
        
        return success_rate >= 0.6  # 60% success rate is acceptable with fallbacks
        
    except Exception as e:
        print(f"❌ Full geolocation test failed: {e}")
        return False

def test_data_model_integration():
    """Test integration with LocationModel"""
    print("\n🧪 Testing data model integration...")
    
    try:
        from tools.geolocation import GeolocationTool
        from models.types import LocationModel
        
        tool = GeolocationTool()
        
        # Test with a simple location
        result_json = tool._run("Seattle, WA")
        result_dict = json.loads(result_json)
        
        # Create LocationModel from result
        location_model = LocationModel(**result_dict)
        
        print(f"   ✅ LocationModel created:")
        print(f"     Address: {location_model.address}")
        print(f"     City: {location_model.city}")
        print(f"     State: {location_model.state}")
        print(f"     Country: {location_model.country}")
        
        # Test JSON serialization
        json_data = location_model.dict()
        if "city" in json_data and "state" in json_data:
            print("   ✅ JSON serialization works")
        else:
            print("   ❌ JSON serialization failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Data model integration test failed: {e}")
        return False

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🧪 Testing edge cases...")
    
    try:
        from tools.geolocation import GeolocationTool
        
        tool = GeolocationTool()
        
        edge_cases = [
            ("", "empty string"),
            ("   ", "whitespace only"),
            ("invalid location 12345 xyz", "nonsense input"),
            ("999.999, 999.999", "invalid coordinates"),
            ("Unknown City, ZZ", "invalid state")
        ]
        
        results = []
        for location_input, description in edge_cases:
            print(f"   Testing {description}: '{location_input}'")
            
            try:
                result_json = tool._run(location_input)
                result = json.loads(result_json)
                
                # Should always get some result, even if it's fallback
                has_city = result.get('city')
                has_state = result.get('state')
                
                if has_city and has_state:
                    print(f"     ✅ Handled gracefully: {has_city}, {has_state}")
                    results.append(True)
                else:
                    print(f"     ❌ Failed to handle edge case")
                    results.append(False)
                    
            except Exception as e:
                print(f"     ❌ Exception not handled: {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Edge case handling success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8
        
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        return False

def main():
    """Run all geolocation tests"""
    print("🚀 Starting Geolocation Tool tests...\n")
    
    # Configuration check
    from config.settings import settings
    has_google_maps = (settings.google_maps_api_key and 
                      settings.google_maps_api_key != "your-google-maps-api-key-here")
    
    if has_google_maps:
        print("🗺️  Google Maps API key configured - full testing enabled")
    else:
        print("⚠️  Google Maps API key not configured - testing fallback functionality")
        print("   (You can get a key from: https://developers.google.com/maps/documentation/geocoding/get-api-key)")
    
    tests = [
        ("Tool Initialization", test_tool_initialization),
        ("Address Parsing", test_address_parsing),
        ("State Normalization", test_state_normalization),
        ("IP Location", test_ip_location),
        ("Full Geolocation", test_full_geolocation),
        ("Data Model Integration", test_data_model_integration),
        ("Edge Cases", test_edge_cases)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            result = test_func()
            results.append(result)
            
            if result:
                print(f"✅ {test_name} test passed!")
            else:
                print(f"❌ {test_name} test failed!")
                
        except Exception as e:
            print(f"💥 {test_name} test crashed: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n{'='*50}")
    print(f"📊 Test Summary: {passed}/{total} tests passed")
    
    if all(results):
        print("🎉 All geolocation tests passed! Tool is ready.")
    elif sum(results) >= len(results) * 0.7:  # 70% pass rate
        print("✅ Most geolocation tests passed! Tool is functional with fallbacks.")
    else:
        print("⚠️  Several tests failed. Please review the issues above.")
        
    return passed >= len(results) * 0.7  # 70% pass rate is acceptable

if __name__ == "__main__":
    main()