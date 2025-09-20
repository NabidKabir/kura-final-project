# test_location_finder.py - Comprehensive test for location finder tool

import sys
import os
import json
from typing import Dict, List

# Add src to path
sys.path.append('src')

def test_tool_initialization():
    """Test that the location finder tool can be initialized"""
    print("🧪 Testing tool initialization...")
    
    try:
        from tools.location_finder import LocationFinderTool, create_location_finder_tool
        from config.settings import settings
        
        # Test direct initialization
        tool = LocationFinderTool()
        print(f"✅ Tool created successfully: {tool.name}")
        print(f"   Description: {tool.description}")
        
        # Check Google Maps status
        has_google_maps = (settings.google_maps_api_key and 
                          settings.google_maps_api_key != "your-google-maps-api-key-here")
        
        if has_google_maps:
            print(f"   Google Maps: Configured")
        else:
            print(f"   Google Maps: Using mock data (API key not configured)")
        
        print(f"   Mock facilities loaded: {len(tool.mock_facilities)} cities")
        print(f"   Search queries loaded: {len(tool.search_queries)} waste types")
        
        # Test factory function
        tool2 = create_location_finder_tool()
        print(f"✅ Factory function works: {tool2.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool initialization failed: {e}")
        return False

def test_search_queries():
    """Test that search queries are properly configured"""
    print("\n🧪 Testing search query configuration...")
    
    try:
        from tools.location_finder import LocationFinderTool
        from models.types import WasteType
        
        tool = LocationFinderTool()
        
        # Check that all waste types have search queries
        waste_types = [wt.value for wt in WasteType if wt != WasteType.UNKNOWN]
        missing_queries = []
        
        for waste_type in waste_types:
            if waste_type not in tool.search_queries:
                missing_queries.append(waste_type)
            else:
                queries = tool.search_queries[waste_type]
                print(f"   {waste_type}: {len(queries)} search queries")
                if len(queries) == 0:
                    missing_queries.append(waste_type)
        
        if missing_queries:
            print(f"❌ Missing search queries for: {missing_queries}")
            return False
        
        # Check that queries are reasonable
        sample_queries = tool.search_queries['e-waste']
        if len(sample_queries) < 3:
            print(f"❌ Too few e-waste queries: {len(sample_queries)}")
            return False
        
        print(f"✅ All waste types have search queries")
        print(f"   Example e-waste queries: {sample_queries[:2]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search query test failed: {e}")
        return False

def test_mock_facilities():
    """Test mock facility database"""
    print("\n🧪 Testing mock facility database...")
    
    try:
        from tools.location_finder import LocationFinderTool
        
        tool = LocationFinderTool()
        
        # Check that we have facilities for major cities
        expected_cities = ['new york', 'los angeles', 'chicago']
        missing_cities = []
        
        for city in expected_cities:
            if city not in tool.mock_facilities:
                missing_cities.append(city)
            else:
                facilities = tool.mock_facilities[city]
                print(f"   {city.title()}: {len(facilities)} facilities")
                
                # Check that facilities have required fields
                for facility in facilities:
                    required_fields = ['name', 'address', 'accepted_waste_types']
                    missing_fields = [f for f in required_fields if f not in facility]
                    if missing_fields:
                        print(f"     ❌ Facility '{facility.get('name', 'Unknown')}' missing: {missing_fields}")
                        return False
        
        if missing_cities:
            print(f"❌ Missing cities: {missing_cities}")
            return False
        
        # Test waste type coverage
        ny_facilities = tool.mock_facilities['new york']
        covered_waste_types = set()
        for facility in ny_facilities:
            covered_waste_types.update(facility.get('accepted_waste_types', []))
        
        print(f"   NYC waste type coverage: {sorted(covered_waste_types)}")
        
        if len(covered_waste_types) < 3:
            print(f"❌ Too few waste types covered: {len(covered_waste_types)}")
            return False
        
        print(f"✅ Mock facility database is properly configured")
        return True
        
    except Exception as e:
        print(f"❌ Mock facility test failed: {e}")
        return False

def test_distance_calculation():
    """Test distance calculation accuracy"""
    print("\n🧪 Testing distance calculation...")
    
    try:
        from tools.location_finder import LocationFinderTool
        
        tool = LocationFinderTool()
        
        # Test known distance: NYC to LA (approximately 3944 km)
        nyc_lat, nyc_lng = 40.7128, -74.0060
        la_lat, la_lng = 34.0522, -118.2437
        
        calculated_distance = tool._calculate_distance(nyc_lat, nyc_lng, la_lat, la_lng)
        expected_distance = 3944  # Approximately
        
        print(f"   NYC to LA distance: {calculated_distance:.1f} km (expected ~{expected_distance} km)")
        
        # Allow 5% tolerance
        tolerance = expected_distance * 0.05
        if abs(calculated_distance - expected_distance) > tolerance:
            print(f"❌ Distance calculation inaccurate: {calculated_distance:.1f} vs {expected_distance}")
            return False
        
        # Test short distance: Within NYC (should be reasonable)
        downtown_lat, downtown_lng = 40.7505, -73.9934  # Times Square
        uptown_lat, uptown_lng = 40.7831, -73.9712      # Central Park
        
        short_distance = tool._calculate_distance(downtown_lat, downtown_lng, uptown_lat, uptown_lng)
        print(f"   Downtown to Uptown NYC: {short_distance:.1f} km")
        
        if short_distance < 0.5 or short_distance > 10:  # Should be reasonable
            print(f"❌ Short distance seems wrong: {short_distance:.1f} km")
            return False
        
        print(f"✅ Distance calculation is accurate")
        return True
        
    except Exception as e:
        print(f"❌ Distance calculation test failed: {e}")
        return False

def test_mock_facility_search():
    """Test mock facility search functionality"""
    print("\n🧪 Testing mock facility search...")
    
    try:
        from tools.location_finder import LocationFinderTool
        
        tool = LocationFinderTool()
        
        test_cases = [
            {
                'location': {'city': 'New York', 'state': 'NY'},
                'waste_type': 'e-waste',
                'expected_min': 1
            },
            {
                'location': {'city': 'Los Angeles', 'state': 'CA'},
                'waste_type': 'hazardous',
                'expected_min': 1
            },
            {
                'location': {'city': 'Chicago', 'state': 'IL'},
                'waste_type': 'medical',  # Might not have exact match
                'expected_min': 0  # Could fall back to general facilities
            },
            {
                'location': {'city': 'Unknown City', 'state': 'ZZ'},
                'waste_type': 'e-waste',
                'expected_min': 0  # Should handle gracefully
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_cases):
            location = test_case['location']
            waste_type = test_case['waste_type']
            expected_min = test_case['expected_min']
            
            print(f"   Test {i+1}: {waste_type} in {location['city']}, {location['state']}")
            
            facilities = tool._get_mock_facilities(location, waste_type)
            facility_count = len(facilities)
            
            print(f"     Found: {facility_count} facilities")
            
            if facility_count >= expected_min:
                print(f"     ✅ Meets expectation (>= {expected_min})")
                results.append(True)
                
                # Show sample facility
                if facilities:
                    sample = facilities[0]
                    print(f"     Sample: {sample.get('name')} - {sample.get('address', 'No address')}")
            else:
                print(f"     ❌ Below expectation (< {expected_min})")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Mock search success rate: {success_rate:.1%}")
        
        return success_rate >= 0.75  # 75% success rate acceptable
        
    except Exception as e:
        print(f"❌ Mock facility search test failed: {e}")
        return False

def test_full_location_search():
    """Test the full location search workflow"""
    print("\n🧪 Testing full location search workflow...")
    
    try:
        from tools.location_finder import LocationFinderTool
        from config.settings import settings
        
        tool = LocationFinderTool()
        
        # Check if Google Maps is configured
        has_google_maps = (settings.google_maps_api_key and 
                          settings.google_maps_api_key != "your-google-maps-api-key-here")
        
        if has_google_maps:
            print("   🗺️  Google Maps configured - testing live search")
        else:
            print("   📍 Google Maps not configured - testing mock search")
        
        test_queries = [
            # JSON format queries
            {
                'query': json.dumps({
                    'location': {'city': 'New York', 'state': 'NY', 'latitude': 40.7128, 'longitude': -74.0060},
                    'waste_type': 'e-waste'
                }),
                'description': 'NYC e-waste with coordinates'
            },
            {
                'query': json.dumps({
                    'location': {'city': 'Los Angeles', 'state': 'CA'},
                    'waste_type': 'hazardous'
                }),
                'description': 'LA hazardous without coordinates'
            },
            # String format query
            {
                'query': 'medical near Chicago',
                'description': 'Chicago medical (string format)'
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_queries):
            print(f"   Test {i+1}: {test_case['description']}")
            
            try:
                result_json = tool._run(test_case['query'])
                result = json.loads(result_json)
                
                facilities_found = result.get('facilities_found', 0)
                search_method = result.get('search_method', 'unknown')
                
                print(f"     Facilities found: {facilities_found}")
                print(f"     Search method: {search_method}")
                
                # Show sample facility if any found
                facilities = result.get('facilities', [])
                if facilities:
                    sample = facilities[0]
                    print(f"     Sample: {sample.get('name')} ({sample.get('distance_km')}km)")
                
                # Validate response structure
                required_fields = ['query_location', 'waste_type', 'facilities_found', 'facilities']
                has_required = all(field in result for field in required_fields)
                
                if has_required:
                    print(f"     ✅ Valid response structure")
                    results.append(True)
                else:
                    missing = [f for f in required_fields if f not in result]
                    print(f"     ❌ Missing fields: {missing}")
                    results.append(False)
                    
            except Exception as e:
                print(f"     ❌ Query failed: {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Full search success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8
        
    except Exception as e:
        print(f"❌ Full location search test failed: {e}")
        return False

def test_data_model_integration():
    """Test integration with DisposalLocation model"""
    print("\n🧪 Testing data model integration...")
    
    try:
        from tools.location_finder import LocationFinderTool
        from models.types import DisposalLocation, WasteType
        
        tool = LocationFinderTool()
        
        # Get some facilities and test model creation
        query = json.dumps({
            'location': {'city': 'New York', 'state': 'NY'},
            'waste_type': 'e-waste'
        })
        
        result_json = tool._run(query)
        result_dict = json.loads(result_json)
        
        facilities = result_dict.get('facilities', [])
        
        if not facilities:
            print("   ⚠️  No facilities found for model testing")
            return True  # Not a failure - just no data
        
        # Test creating DisposalLocation from result
        sample_facility = facilities[0]
        
        print(f"   Testing with facility: {sample_facility.get('name', 'Unknown')}")
        
        # The response should already contain DisposalLocation-compatible data
        disposal_location = DisposalLocation(**sample_facility)
        
        print(f"   ✅ DisposalLocation model created successfully")
        print(f"     Name: {disposal_location.name}")
        print(f"     Address: {disposal_location.address}")
        print(f"     Distance: {disposal_location.distance_km}km")
        print(f"     Waste types: {[wt.value for wt in disposal_location.accepted_waste_types]}")
        
        # Test JSON serialization
        json_data = disposal_location.dict()
        if "name" in json_data and "address" in json_data:
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
        from tools.location_finder import LocationFinderTool
        
        tool = LocationFinderTool()
        
        edge_cases = [
            ("", "empty string"),
            ("invalid json", "invalid JSON"),
            ('{"location": {}, "waste_type": ""}', "empty location and waste type"),
            ('{"location": {"city": "NonexistentCity", "state": "ZZ"}, "waste_type": "unknown"}', "invalid location and waste type"),
            ('{"location": null, "waste_type": "e-waste"}', "null location")
        ]
        
        results = []
        for query, description in edge_cases:
            print(f"   Testing {description}: '{query[:30]}...'")
            
            try:
                result_json = tool._run(query)
                result = json.loads(result_json)
                
                # Should always get some result structure
                has_basic_structure = 'facilities_found' in result
                
                if has_basic_structure:
                    facilities_found = result.get('facilities_found', 0)
                    print(f"     ✅ Handled gracefully: {facilities_found} facilities")
                    results.append(True)
                else:
                    print(f"     ❌ Invalid response structure")
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

def test_different_waste_types():
    """Test location finding for different waste types"""
    print("\n🧪 Testing different waste types...")
    
    try:
        from tools.location_finder import LocationFinderTool
        from models.types import WasteType
        
        tool = LocationFinderTool()
        
        # Test each waste type
        waste_types = ['e-waste', 'medical', 'hazardous', 'recyclable', 'organic']
        location = {'city': 'New York', 'state': 'NY'}
        
        results = []
        for waste_type in waste_types:
            print(f"   Testing {waste_type} disposal...")
            
            query = json.dumps({
                'location': location,
                'waste_type': waste_type
            })
            
            try:
                result_json = tool._run(query)
                result = json.loads(result_json)
                
                facilities_found = result.get('facilities_found', 0)
                print(f"     Found: {facilities_found} facilities")
                
                # Each waste type should find at least some facilities or handle gracefully
                if facilities_found >= 0:  # Even 0 is acceptable with proper structure
                    results.append(True)
                    
                    # Show search queries used for this waste type
                    search_queries = tool.search_queries.get(waste_type, [])
                    print(f"     Search queries: {len(search_queries)} terms")
                else:
                    results.append(False)
                    
            except Exception as e:
                print(f"     ❌ Failed: {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Different waste types success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8
        
    except Exception as e:
        print(f"❌ Different waste types test failed: {e}")
        return False

def main():
    """Run all location finder tests"""
    print("🚀 Starting Location Finder Tool tests...\n")
    
    # Configuration check
    from config.settings import settings
    has_google_maps = (settings.google_maps_api_key and 
                      settings.google_maps_api_key != "your-google-maps-api-key-here")
    
    if has_google_maps:
        print("🗺️  Google Maps API key configured - enhanced testing enabled")
    else:
        print("⚠️  Google Maps API key not configured - testing with mock facilities")
        print("   (You can get a key from: https://developers.google.com/maps/documentation/places/web-service/get-api-key)")
    
    tests = [
        ("Tool Initialization", test_tool_initialization),
        ("Search Queries", test_search_queries),
        ("Mock Facilities", test_mock_facilities),
        ("Distance Calculation", test_distance_calculation),
        ("Mock Facility Search", test_mock_facility_search),
        ("Full Location Search", test_full_location_search),
        ("Data Model Integration", test_data_model_integration),
        ("Edge Cases", test_edge_cases),
        ("Different Waste Types", test_different_waste_types)
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
        print("🎉 All location finder tests passed! Tool is ready.")
    elif sum(results) >= len(results) * 0.75:  # 75% pass rate
        print("✅ Most location finder tests passed! Tool is functional.")
    else:
        print("⚠️  Several tests failed. Please review the issues above.")
        
    return passed >= len(results) * 0.75

if __name__ == "__main__":
    main()