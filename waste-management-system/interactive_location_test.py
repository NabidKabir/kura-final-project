# interactive_location_test.py - Interactive testing of the Location Finder Tool

import sys
import os
import json
from typing import Dict, List

# Add src to path
sys.path.append('src')

def display_facility_results(result_json: str):
    """Display facility search results in a nice format"""
    try:
        result = json.loads(result_json)
        
        print(f"\n🗺️  Facility Search Results:")
        print("=" * 70)
        
        # Query info
        query_location = result.get('query_location', {})
        print(f"📍 Search Location: {query_location.get('city', 'N/A')}, {query_location.get('state', 'N/A')}")
        print(f"🗑️  Waste Type: {result.get('waste_type', 'N/A').upper()}")
        print(f"📊 Search Radius: {result.get('search_radius_km', 'N/A')} km")
        print(f"🔍 Search Method: {result.get('search_method', 'N/A').title()}")
        print(f"📈 Facilities Found: {result.get('facilities_found', 0)}")
        
        facilities = result.get('facilities', [])
        
        if not facilities:
            print(f"\n❌ No facilities found for this waste type in this area.")
            if result.get('suggestion'):
                print(f"💡 Suggestion: {result['suggestion']}")
            print("=" * 70)
            return
        
        print(f"\n🏢 DISPOSAL FACILITIES:")
        print("-" * 70)
        
        for i, facility in enumerate(facilities, 1):
            print(f"\n{i}. {facility.get('name', 'Unknown Facility')}")
            print(f"   📍 Address: {facility.get('address', 'Address not available')}")
            
            if facility.get('distance_km'):
                print(f"   🚗 Distance: {facility['distance_km']} km")
            
            if facility.get('phone'):
                print(f"   📞 Phone: {facility['phone']}")
            
            if facility.get('website'):
                print(f"   🌐 Website: {facility['website']}")
            
            if facility.get('rating'):
                stars = "⭐" * int(facility['rating'])
                print(f"   {stars} Rating: {facility['rating']}/5")
            
            # Accepted waste types
            waste_types = facility.get('accepted_waste_types', [])
            if waste_types:
                types_str = ", ".join(waste_types)
                print(f"   ♻️  Accepts: {types_str}")
            
            # Hours
            hours = facility.get('hours', [])
            if hours:
                print(f"   🕒 Hours:")
                for hour in hours[:3]:  # Show first 3 lines
                    print(f"      {hour}")
                if len(hours) > 3:
                    print(f"      ... and {len(hours) - 3} more")
            
            # Special instructions
            instructions = facility.get('special_instructions')
            if instructions:
                print(f"   💡 Instructions: {instructions}")
            
            if i < len(facilities):
                print("   " + "-" * 50)
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"❌ Error displaying results: {e}")

def test_specific_search(tool, location_data: Dict, waste_type: str):
    """Test facility search for specific location and waste type"""
    
    city = location_data.get('city', 'Unknown')
    state = location_data.get('state', 'Unknown')
    
    print(f"\n🔍 Searching for {waste_type} disposal facilities near {city}, {state}")
    print("⏳ Processing...")
    
    try:
        query = json.dumps({
            'location': location_data,
            'waste_type': waste_type,
            'radius_km': 25
        })
        
        result_json = tool._run(query)
        display_facility_results(result_json)
        
        # Show what search method was used
        result = json.loads(result_json)
        search_method = result.get('search_method', 'unknown')
        
        if search_method == 'google_maps':
            print(f"🗺️  Used Google Maps API for live facility search")
        elif search_method == 'mock_database':
            print(f"📍 Used mock facility database (Google Maps not available)")
        else:
            print(f"🔧 Used search method: {search_method}")
            
    except Exception as e:
        print(f"❌ Facility search failed: {e}")

def browse_available_cities(tool):
    """Browse available mock cities and their facilities"""
    
    print(f"\n📚 Available Mock Cities and Facilities:")
    print("=" * 60)
    
    mock_facilities = tool.mock_facilities
    
    for city, facilities in mock_facilities.items():
        print(f"\n🏙️  {city.title()}:")
        print(f"   Total facilities: {len(facilities)}")
        
        # Group by waste type
        waste_type_counts = {}
        for facility in facilities:
            for waste_type in facility.get('accepted_waste_types', []):
                waste_type_counts[waste_type] = waste_type_counts.get(waste_type, 0) + 1
        
        print(f"   Waste types covered:")
        for waste_type, count in sorted(waste_type_counts.items()):
            print(f"     • {waste_type}: {count} facilities")
        
        # Show sample facilities
        print(f"   Sample facilities:")
        for facility in facilities[:2]:  # Show first 2
            print(f"     • {facility.get('name', 'Unknown')}")
    
    print("\n" + "=" * 60)

def get_example_searches():
    """Return interesting search examples"""
    return [
        # Major cities with good coverage
        {"location": {"city": "New York", "state": "NY"}, "waste_type": "e-waste", "description": "NYC electronics recycling"},
        {"location": {"city": "Los Angeles", "state": "CA"}, "waste_type": "hazardous", "description": "LA hazardous waste disposal"},
        {"location": {"city": "Chicago", "state": "IL"}, "waste_type": "medical", "description": "Chicago medical waste"},
        
        # Different waste types in same city
        {"location": {"city": "New York", "state": "NY"}, "waste_type": "medical", "description": "NYC medication disposal"},
        {"location": {"city": "New York", "state": "NY"}, "waste_type": "recyclable", "description": "NYC recycling centers"},
        
        # Test with coordinates (for Google Maps if available)
        {"location": {"city": "San Francisco", "state": "CA", "latitude": 37.7749, "longitude": -122.4194}, "waste_type": "organic", "description": "SF composting (with coordinates)"},
        
        # Edge cases
        {"location": {"city": "Small Town", "state": "MT"}, "waste_type": "e-waste", "description": "Small town (fallback test)"},
    ]

def compare_waste_types(tool):
    """Compare facilities for different waste types in the same city"""
    
    print(f"\n🔍 COMPARING WASTE TYPE FACILITIES")
    print("=" * 60)
    print("Let's see what facilities are available for different waste types in NYC...\n")
    
    waste_types = ['e-waste', 'medical', 'hazardous', 'recyclable', 'organic']
    location = {'city': 'New York', 'state': 'NY'}
    
    for i, waste_type in enumerate(waste_types, 1):
        print(f"🗑️  {i}. {waste_type.upper()} Disposal Options:")
        print("-" * 40)
        
        query = json.dumps({
            'location': location,
            'waste_type': waste_type
        })
        
        try:
            result_json = tool._run(query)
            result = json.loads(result_json)
            
            facilities_found = result.get('facilities_found', 0)
            print(f"Facilities found: {facilities_found}")
            
            if facilities_found > 0:
                # Show top 2 facilities
                facilities = result.get('facilities', [])
                for j, facility in enumerate(facilities[:2], 1):
                    print(f"  {j}. {facility.get('name', 'Unknown')}")
                    print(f"     📍 {facility.get('address', 'No address')}")
                    if facility.get('distance_km'):
                        print(f"     🚗 {facility['distance_km']}km away")
            else:
                print("  No specific facilities found")
            
        except Exception as e:
            print(f"  ❌ Search failed: {e}")
        
        print()  # Blank line
        
        if i < len(waste_types):
            input("Press Enter to continue to next waste type...")

def quick_demo(tool):
    """Run a quick demo with pre-selected examples"""
    
    print(f"\n🎬 QUICK DEMO - Facility Search Examples")
    print("=" * 60)
    print("Let's see facility search results for different scenarios...\n")
    
    demo_examples = [
        {"location": {"city": "New York", "state": "NY"}, "waste_type": "e-waste", "description": "Electronics recycling in NYC"},
        {"location": {"city": "Los Angeles", "state": "CA"}, "waste_type": "hazardous", "description": "Hazardous waste in LA"},
        {"location": {"city": "Chicago", "state": "IL"}, "waste_type": "medical", "description": "Medical waste in Chicago"},
        {"location": {"city": "Unknown City", "state": "ZZ"}, "waste_type": "recyclable", "description": "Edge case - unknown location"}
    ]
    
    for i, example in enumerate(demo_examples, 1):
        print(f"🎬 Demo {i}/{len(demo_examples)}: {example['description']}")
        test_specific_search(tool, example['location'], example['waste_type'])
        
        if i < len(demo_examples):
            input("\nPress Enter to continue to next demo...")
    
    print(f"\n🎉 Demo complete! You've seen {len(demo_examples)} different search scenarios.")

def interactive_mode(tool):
    """Interactive mode for custom facility searches"""
    
    print(f"\n🗺️  INTERACTIVE FACILITY FINDER")
    print("=" * 60)
    print("Find waste disposal facilities for any location and waste type!")
    print("\nAvailable waste types:")
    print("• e-waste (electronics, batteries)")
    print("• medical (medications, sharps)")  
    print("• hazardous (paint, chemicals)")
    print("• recyclable (plastic, glass, paper)")
    print("• organic (food scraps, yard waste)")
    print("• household (general trash)")
    print("\nType 'examples' to see example searches")
    print("Type 'browse' to see available mock cities")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        print(f"\n" + "─" * 40)
        
        # Get location
        location_input = input("📍 Enter location (City, State): ").strip()
        
        if location_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Thanks for exploring facilities! Goodbye!")
            break
            
        if location_input.lower() in ['examples', 'ex', 'e']:
            print(f"\n📋 Here are some interesting examples to try:")
            examples = get_example_searches()
            for i, example in enumerate(examples, 1):
                loc = example['location']
                coords = f" (lat/lng: {loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')})" if loc.get('latitude') else ""
                print(f"   {i:2d}. {example['waste_type']} in {loc['city']}, {loc['state']}{coords}")
                print(f"       {example['description']}")
            continue
            
        if location_input.lower() in ['browse', 'br', 'b']:
            browse_available_cities(tool)
            continue
            
        if not location_input:
            continue
        
        # Parse location
        if ',' in location_input:
            parts = [p.strip() for p in location_input.split(',')]
            city, state = parts[0], parts[1] if len(parts) > 1 else 'NY'
        else:
            city, state = location_input, 'NY'
        
        # Get waste type
        waste_type = input("🗑️  Enter waste type: ").strip().lower()
        
        if not waste_type:
            continue
        
        # Optional: Get coordinates for enhanced search
        coords_input = input("📍 Enter coordinates (lat, lng) [optional]: ").strip()
        location_data = {'city': city, 'state': state.upper()}
        
        if coords_input and ',' in coords_input:
            try:
                lat_str, lng_str = coords_input.split(',')
                location_data['latitude'] = float(lat_str.strip())
                location_data['longitude'] = float(lng_str.strip())
                print(f"   ✅ Using coordinates for enhanced search")
            except ValueError:
                print(f"   ⚠️  Invalid coordinates, searching without them")
        
        # Search for facilities
        test_specific_search(tool, location_data, waste_type)
        
        # Ask if they want to continue
        continue_choice = input("\n❓ Search for more facilities? (y/n): ").strip().lower()
        if continue_choice in ['n', 'no']:
            print("👋 Thanks for exploring facilities! Goodbye!")
            break

def test_google_maps_vs_mock(tool):
    """Compare Google Maps results vs mock data (if Google Maps available)"""
    
    from config.settings import settings
    has_google_maps = (settings.google_maps_api_key and 
                      settings.google_maps_api_key != "your-google-maps-api-key-here")
    
    if not has_google_maps:
        print(f"\n⚠️  Google Maps API not configured - can't compare methods")
        print("   Add your API key to .env file to test live Google Maps search")
        return
    
    print(f"\n🔍 GOOGLE MAPS vs MOCK DATA COMPARISON")
    print("=" * 60)
    print("Comparing live Google Maps search with mock facility database...\n")
    
    # Test location with coordinates (for Google Maps) and known mock data
    test_location = {
        'city': 'New York',
        'state': 'NY',
        'latitude': 40.7128,
        'longitude': -74.0060
    }
    
    waste_type = 'e-waste'
    
    print(f"Testing {waste_type} facilities in {test_location['city']}, {test_location['state']}")
    
    # Search with full location (should use Google Maps)
    print(f"\n1. Google Maps Search (with coordinates):")
    query_with_coords = json.dumps({
        'location': test_location,
        'waste_type': waste_type
    })
    
    result_gm = tool._run(query_with_coords)
    result_gm_dict = json.loads(result_gm)
    
    print(f"   Method: {result_gm_dict.get('search_method', 'unknown')}")
    print(f"   Facilities: {result_gm_dict.get('facilities_found', 0)}")
    
    # Search without coordinates (should use mock)
    print(f"\n2. Mock Database Search (without coordinates):")
    location_no_coords = {'city': test_location['city'], 'state': test_location['state']}
    query_mock = json.dumps({
        'location': location_no_coords,
        'waste_type': waste_type
    })
    
    result_mock = tool._run(query_mock)
    result_mock_dict = json.loads(result_mock)
    
    print(f"   Method: {result_mock_dict.get('search_method', 'unknown')}")
    print(f"   Facilities: {result_mock_dict.get('facilities_found', 0)}")
    
    print(f"\n📊 Summary:")
    print(f"   Google Maps found: {result_gm_dict.get('facilities_found', 0)} facilities")
    print(f"   Mock database has: {result_mock_dict.get('facilities_found', 0)} facilities")
    print(f"   Both methods provide facility information for disposal guidance")

def main():
    """Main menu for interactive facility finding"""
    
    try:
        from tools.location_finder import create_location_finder_tool
        from config.settings import settings
        
        print("🗺️  Initializing Location Finder Tool...")
        tool = create_location_finder_tool()
        
        # Check configuration
        has_google_maps = (settings.google_maps_api_key and 
                          settings.google_maps_api_key != "your-google-maps-api-key-here")
        
        if has_google_maps:
            print("🗺️  Google Maps API configured - live facility search available!")
        else:
            print("📍 Google Maps not configured - using comprehensive mock facility database")
        
        print("🚀 Welcome to the Facility Finder Explorer!")
        print("\nWhat would you like to do?")
        print("1. Interactive mode - search for facilities anywhere")
        print("2. Quick demo - see examples with pre-selected locations")
        print("3. Compare waste types - see facilities for different waste types")
        print("4. Browse mock cities - see available mock facility data")
        if has_google_maps:
            print("5. Compare Google Maps vs Mock - see search method differences")
            print("6. Exit")
        else:
            print("5. Exit")
        
        max_choice = 6 if has_google_maps else 5
        
        while True:
            choice = input(f"\nEnter your choice (1-{max_choice}): ").strip()
            
            if choice == '1':
                interactive_mode(tool)
                break
            elif choice == '2':
                quick_demo(tool)
                
                try_interactive = input("\n❓ Want to try interactive mode too? (y/n): ").strip().lower()
                if try_interactive in ['y', 'yes']:
                    interactive_mode(tool)
                break
            elif choice == '3':
                compare_waste_types(tool)
                
                try_interactive = input("\n❓ Want to try interactive mode? (y/n): ").strip().lower()
                if try_interactive in ['y', 'yes']:
                    interactive_mode(tool)
                break
            elif choice == '4':
                browse_available_cities(tool)
                
                try_interactive = input("\n❓ Want to try interactive mode? (y/n): ").strip().lower()
                if try_interactive in ['y', 'yes']:
                    interactive_mode(tool)
                break
            elif choice == '5' and has_google_maps:
                test_google_maps_vs_mock(tool)
                
                try_interactive = input("\n❓ Want to try interactive mode? (y/n): ").strip().lower()
                if try_interactive in ['y', 'yes']:
                    interactive_mode(tool)
                break
            elif choice == str(max_choice):
                print("👋 Goodbye!")
                break
            else:
                print(f"❌ Invalid choice. Please enter 1-{max_choice}.")
                
    except ImportError as e:
        print(f"❌ Could not import location finder tool: {e}")
        print("Make sure you've run the setup and tests first!")
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()