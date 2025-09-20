# interactive_geolocation_test.py - Interactive testing of the Geolocation Tool

import sys
import os
import json
from typing import Dict

# Add src to path
sys.path.append('src')

def display_location_result(result_json: str):
    """Display location results in a nice format"""
    try:
        result = json.loads(result_json)
        
        print(f"\n📍 Location Result:")
        print("=" * 50)
        print(f"🏙️  City: {result.get('city', 'N/A')}")
        print(f"🗺️  State: {result.get('state', 'N/A')}")
        print(f"📮 ZIP Code: {result.get('zipcode', 'N/A')}")
        print(f"🌍 Country: {result.get('country', 'N/A')}")
        print(f"📧 Full Address: {result.get('address', 'N/A')}")
        
        if result.get('latitude') and result.get('longitude'):
            print(f"🎯 Coordinates: {result['latitude']:.6f}, {result['longitude']:.6f}")
            print(f"   Google Maps: https://maps.google.com/?q={result['latitude']},{result['longitude']}")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error displaying result: {e}")

def test_specific_location(tool, location_input: str):
    """Test geolocation for a specific input"""
    
    display_input = location_input if location_input.strip() else "(auto-detect from IP)"
    print(f"\n🔍 Finding location for: '{display_input}'")
    print("⏳ Processing...")
    
    try:
        result_json = tool._run(location_input)
        display_location_result(result_json)
        
        # Show what methods were likely used
        result = json.loads(result_json)
        
        print(f"\n🔧 Detection method info:")
        if result.get('latitude') and result.get('longitude'):
            if location_input.strip() and (',' in location_input or len(location_input) > 20):
                print("   Likely used: Google Maps Geocoding API (if configured) or IP fallback")
            elif not location_input.strip():
                print("   Likely used: IP-based geolocation")
            else:
                print("   Likely used: Address parsing + geocoding or fallback")
        else:
            print("   Likely used: Partial address parsing or fallback data")
            
    except Exception as e:
        print(f"❌ Location detection failed: {e}")

def get_example_locations():
    """Return example locations to test"""
    return [
        "",  # Auto-detect
        "New York, NY",
        "Los Angeles, CA", 
        "Chicago, IL",
        "90210",  # Beverly Hills ZIP
        "10001",  # NYC ZIP
        "San Francisco",
        "Miami, FL",
        "Seattle, WA",
        "40.7128, -74.0060",  # NYC coordinates
        "37.7749, -122.4194",  # SF coordinates
        "123 Main Street, Boston, MA",
        "Times Square, New York",
        "Golden Gate Bridge, San Francisco",
        "Austin, TX",
        "Portland, OR"
    ]

def quick_demo():
    """Run a quick demo with pre-selected locations"""
    
    try:
        from tools.geolocation import create_geolocation_tool
        from config.settings import settings
        
        print("📍 Initializing Geolocation Tool...")
        tool = create_geolocation_tool()
        
        # Check configuration
        has_google_maps = (settings.google_maps_api_key and 
                          settings.google_maps_api_key != "your-google-maps-api-key-here")
        
        if has_google_maps:
            print("🗺️  Google Maps API configured - enhanced accuracy available!")
        else:
            print("⚠️  Google Maps API not configured - using fallback methods")
            print("   (Still works great for most locations!)")
        
        print("\n" + "="*60)
        print("🎬 QUICK DEMO - Geolocation Examples")
        print("="*60)
        
        demo_locations = [
            ("", "Auto-detect your location"),
            ("New York, NY", "City and state"),
            ("90210", "ZIP code only"),
            ("40.7128, -74.0060", "GPS coordinates"),
            ("Golden Gate Bridge, San Francisco", "Famous landmark")
        ]
        
        for i, (location_input, description) in enumerate(demo_locations, 1):
            print(f"\n🎬 Demo {i}/{len(demo_locations)}: {description}")
            test_specific_location(tool, location_input)
            
            if i < len(demo_locations):
                input("Press Enter to continue to next demo...")
        
        print(f"\n🎉 Demo complete! You've seen {len(demo_locations)} different location types processed.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def interactive_mode():
    """Interactive mode for testing custom locations"""
    
    try:
        from tools.geolocation import create_geolocation_tool
        from config.settings import settings
        
        print("📍 Initializing Geolocation Tool...")
        tool = create_geolocation_tool()
        
        # Check configuration
        has_google_maps = (settings.google_maps_api_key and 
                          settings.google_maps_api_key != "your-google-maps-api-key-here")
        
        if has_google_maps:
            print("🗺️  Google Maps API configured - enhanced accuracy!")
        else:
            print("⚠️  Google Maps API not configured - using smart fallbacks")
        
        print("\n" + "="*60)
        print("📍 INTERACTIVE GEOLOCATION TOOL")
        print("="*60)
        print("Enter locations and see how they get processed!")
        print("\nSupported formats:")
        print("• City, State (e.g., 'Seattle, WA')")
        print("• ZIP codes (e.g., '10001')")
        print("• Coordinates (e.g., '40.7128, -74.0060')")
        print("• Addresses (e.g., '123 Main St, Boston, MA')")
        print("• Landmarks (e.g., 'Times Square, NYC')")
        print("• Just press Enter for auto-detection")
        print("\nType 'examples' to see test examples")
        print("Type 'quit' to exit")
        print("="*60)
        
        while True:
            print("\n" + "─" * 40)
            user_input = input("📍 Enter location (or press Enter for auto-detect): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for testing! Goodbye!")
                break
                
            if user_input.lower() in ['examples', 'ex', 'e']:
                print("\n📋 Here are some interesting examples to try:")
                examples = get_example_locations()
                for i, example in enumerate(examples, 1):
                    display_example = example if example else "(just press Enter for auto-detect)"
                    print(f"   {i:2d}. {display_example}")
                print("\nCopy any of these to test, or create your own!")
                continue
            
            # Test the location
            test_specific_location(tool, user_input)
            
            # Ask if they want to continue
            continue_choice = input("\n❓ Test another location? (y/n): ").strip().lower()
            if continue_choice in ['n', 'no']:
                print("👋 Thanks for testing! Goodbye!")
                break
                
    except ImportError as e:
        print(f"❌ Could not import geolocation tool: {e}")
        print("Make sure you've run the setup and tests first!")
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_accuracy():
    """Test accuracy against known locations"""
    
    try:
        from tools.geolocation import create_geolocation_tool
        
        print("📍 Initializing Geolocation Tool...")
        tool = create_geolocation_tool()
        
        print("\n" + "="*60)
        print("🎯 ACCURACY TEST - Known Locations")
        print("="*60)
        print("Testing against locations with known coordinates...")
        
        # Test cases with known coordinates for accuracy checking
        known_locations = [
            {
                "input": "New York, NY",
                "expected_lat": 40.7128,
                "expected_lng": -74.0060,
                "tolerance": 0.1  # Degrees tolerance
            },
            {
                "input": "Los Angeles, CA", 
                "expected_lat": 34.0522,
                "expected_lng": -118.2437,
                "tolerance": 0.1
            },
            {
                "input": "Chicago, IL",
                "expected_lat": 41.8781,
                "expected_lng": -87.6298,
                "tolerance": 0.1
            }
        ]
        
        accurate_results = 0
        
        for i, test_case in enumerate(known_locations, 1):
            print(f"\n🎯 Accuracy test {i}/{len(known_locations)}: {test_case['input']}")
            
            result_json = tool._run(test_case['input'])
            result = json.loads(result_json)
            
            if result.get('latitude') and result.get('longitude'):
                lat_diff = abs(result['latitude'] - test_case['expected_lat'])
                lng_diff = abs(result['longitude'] - test_case['expected_lng'])
                
                print(f"   Expected: {test_case['expected_lat']:.4f}, {test_case['expected_lng']:.4f}")
                print(f"   Got:      {result['latitude']:.4f}, {result['longitude']:.4f}")
                print(f"   Difference: {lat_diff:.4f}°, {lng_diff:.4f}°")
                
                if lat_diff <= test_case['tolerance'] and lng_diff <= test_case['tolerance']:
                    print(f"   ✅ Within tolerance ({test_case['tolerance']}°)")
                    accurate_results += 1
                else:
                    print(f"   ⚠️  Outside tolerance")
            else:
                print(f"   ⚠️  No coordinates returned")
        
        accuracy_rate = accurate_results / len(known_locations)
        print(f"\n📊 Accuracy rate: {accuracy_rate:.1%} ({accurate_results}/{len(known_locations)})")
        
        if accuracy_rate >= 0.7:
            print("🎉 Good accuracy! Geolocation is working well.")
        else:
            print("⚠️  Lower accuracy - likely due to API configuration or network issues.")
            print("   This is still okay for waste management purposes!")
        
    except Exception as e:
        print(f"❌ Accuracy test failed: {e}")

def main():
    """Main menu for interactive testing"""
    
    print("🚀 Welcome to the Geolocation Tool Tester!")
    print("\nWhat would you like to do?")
    print("1. Interactive mode - test your own locations")
    print("2. Quick demo - see examples with pre-selected locations")
    print("3. Accuracy test - test against known coordinates")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            interactive_mode()
            break
        elif choice == '2':
            quick_demo()
            
            # Ask if they want to try other modes
            try_other = input("\n❓ Want to try interactive mode too? (y/n): ").strip().lower()
            if try_other in ['y', 'yes']:
                interactive_mode()
            break
        elif choice == '3':
            test_accuracy()
            
            try_interactive = input("\n❓ Want to try interactive mode? (y/n): ").strip().lower()
            if try_interactive in ['y', 'yes']:
                interactive_mode()
            break
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()