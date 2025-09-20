# interactive_regulation_test.py - Interactive testing of the Regulation Lookup Tool

import sys
import os
import json
from typing import Dict, List

# Add src to path
sys.path.append('src')

def display_regulation_result(result_json: str):
    """Display regulation results in a nice format"""
    try:
        result = json.loads(result_json)
        
        print(f"\n⚖️  Regulation Information:")
        print("=" * 60)
        print(f"🏛️  Jurisdiction: {result.get('jurisdiction', 'N/A')}")
        print(f"🗂️  Waste Type: {result.get('waste_type', 'N/A').upper()}")
        
        if result.get('applicable_location'):
            loc = result['applicable_location']
            print(f"📍 Location: {loc.get('city', 'N/A')}, {loc.get('state', 'N/A')}")
            print(f"📊 Level: {loc.get('jurisdiction_level', 'N/A').title()}")
        
        print(f"\n📋 RULES:")
        print(f"   {result.get('rules', 'No rules specified')}")
        
        if result.get('preparation_steps'):
            print(f"\n🔧 PREPARATION STEPS:")
            for i, step in enumerate(result['preparation_steps'], 1):
                print(f"   {i}. {step}")
        
        if result.get('restrictions'):
            print(f"\n🚫 RESTRICTIONS:")
            for i, restriction in enumerate(result['restrictions'], 1):
                print(f"   {i}. {restriction}")
        
        if result.get('disposal_methods'):
            print(f"\n♻️  DISPOSAL METHODS:")
            for i, method in enumerate(result['disposal_methods'], 1):
                print(f"   {i}. {method}")
        
        if result.get('penalties'):
            print(f"\n⚠️  PENALTIES:")
            print(f"   {result['penalties']}")
        
        if result.get('source_url'):
            print(f"\n🔗 SOURCE:")
            print(f"   {result['source_url']}")
        
        if result.get('last_updated'):
            print(f"\n📅 LAST UPDATED:")
            print(f"   {result['last_updated']}")
        
        if result.get('note'):
            print(f"\n💡 NOTE:")
            print(f"   {result['note']}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error displaying result: {e}")

def test_specific_regulation(tool, location_data: Dict, waste_type: str):
    """Test regulation lookup for specific location and waste type"""
    
    city = location_data.get('city', 'Unknown')
    state = location_data.get('state', 'Unknown')
    
    print(f"\n🔍 Looking up regulations for {waste_type} in {city}, {state}")
    print("⏳ Processing...")
    
    try:
        query = json.dumps({
            'location': location_data,
            'waste_type': waste_type
        })
        
        result_json = tool._run(query)
        display_regulation_result(result_json)
        
        # Show what type of regulation this was
        result = json.loads(result_json)
        jurisdiction = result.get('jurisdiction', '')
        
        if 'Federal' in jurisdiction or 'General' in jurisdiction:
            print(f"\n💡 This is a federal/general regulation - no specific state law found")
        elif state.upper() in jurisdiction.upper():
            print(f"✅ This is a state-specific regulation for {state}")
        else:
            print(f"📋 This regulation comes from: {jurisdiction}")
            
    except Exception as e:
        print(f"❌ Regulation lookup failed: {e}")

def browse_available_regulations(tool):
    """Browse through available regulations in the database"""
    
    print(f"\n📚 Available Regulations in Database:")
    print("=" * 50)
    
    db = tool.regulation_db
    
    for state, regulations in db.items():
        if state == 'DEFAULT':
            state_name = "Federal/General Guidelines"
        else:
            state_name = f"{state} State"
        
        print(f"\n🏛️  {state_name}:")
        for waste_type in regulations.keys():
            print(f"   • {waste_type}")
    
    print("\n" + "=" * 50)

def get_example_combinations():
    """Return interesting location/waste type combinations to test"""
    return [
        # State-specific regulations (should find specific rules)
        {"location": {"city": "New York", "state": "NY"}, "waste_type": "e-waste", "description": "NY e-waste (strict state rules)"},
        {"location": {"city": "Los Angeles", "state": "CA"}, "waste_type": "hazardous", "description": "CA hazardous (strict state rules)"},
        {"location": {"city": "Austin", "state": "TX"}, "waste_type": "e-waste", "description": "TX e-waste (different from NY/CA)"},
        
        # Fallback cases (should use federal guidelines)
        {"location": {"city": "Miami", "state": "FL"}, "waste_type": "e-waste", "description": "FL e-waste (fallback - no FL rules)"},
        {"location": {"city": "Seattle", "state": "WA"}, "waste_type": "medical", "description": "WA medical (fallback)"},
        {"location": {"city": "Denver", "state": "CO"}, "waste_type": "recyclable", "description": "CO recyclable (fallback)"},
        
        # Different waste types in same state
        {"location": {"city": "Albany", "state": "NY"}, "waste_type": "medical", "description": "NY medical waste"},
        {"location": {"city": "Albany", "state": "NY"}, "waste_type": "hazardous", "description": "NY hazardous waste"},
        {"location": {"city": "Albany", "state": "NY"}, "waste_type": "organic", "description": "NY organic waste"},
        
        # Edge cases
        {"location": {"city": "Unknown", "state": "ZZ"}, "waste_type": "unknown", "description": "Invalid state/waste (fallback)"}
    ]

def compare_state_regulations(tool):
    """Compare regulations for the same waste type across different states"""
    
    print(f"\n🔍 COMPARING STATE REGULATIONS")
    print("=" * 60)
    print("Let's see how e-waste regulations differ across states...\n")
    
    states_to_compare = [
        {"city": "New York", "state": "NY", "name": "New York"},
        {"city": "Los Angeles", "state": "CA", "name": "California"}, 
        {"city": "Austin", "state": "TX", "name": "Texas"},
        {"city": "Miami", "state": "FL", "name": "Florida (fallback)"}
    ]
    
    for i, location in enumerate(states_to_compare, 1):
        print(f"📍 {i}. {location['name']} E-Waste Regulations:")
        print("-" * 40)
        
        query = json.dumps({
            'location': {'city': location['city'], 'state': location['state']},
            'waste_type': 'e-waste'
        })
        
        try:
            result_json = tool._run(query)
            result = json.loads(result_json)
            
            print(f"Jurisdiction: {result.get('jurisdiction')}")
            print(f"Rules: {result.get('rules', '')[:120]}...")
            print(f"Preparation Steps: {len(result.get('preparation_steps', []))} steps")
            
            if result.get('penalties'):
                print(f"Penalties: {result['penalties'][:100]}...")
            
        except Exception as e:
            print(f"❌ Failed to get regulation: {e}")
        
        print()  # Blank line
        
        if i < len(states_to_compare):
            input("Press Enter to continue to next state...")

def quick_demo(tool):
    """Run a quick demo with pre-selected interesting examples"""
    
    print(f"\n🎬 QUICK DEMO - Regulation Examples")
    print("=" * 60)
    print("Let's see some interesting regulation differences...\n")
    
    demo_examples = [
        {"location": {"city": "New York", "state": "NY"}, "waste_type": "e-waste", "description": "NY has strict e-waste laws"},
        {"location": {"city": "San Francisco", "state": "CA"}, "waste_type": "hazardous", "description": "CA has comprehensive hazardous waste rules"},
        {"location": {"city": "Miami", "state": "FL"}, "waste_type": "medical", "description": "FL uses federal guidelines (no state-specific rules)"},
        {"location": {"city": "Albany", "state": "NY"}, "waste_type": "organic", "description": "NY has composting requirements"}
    ]
    
    for i, example in enumerate(demo_examples, 1):
        print(f"🎬 Demo {i}/{len(demo_examples)}: {example['description']}")
        test_specific_regulation(tool, example['location'], example['waste_type'])
        
        if i < len(demo_examples):
            input("\nPress Enter to continue to next demo...")
    
    print(f"\n🎉 Demo complete! You've seen {len(demo_examples)} different regulation examples.")

def interactive_mode(tool):
    """Interactive mode for custom regulation lookups"""
    
    print(f"\n📚 INTERACTIVE REGULATION LOOKUP")
    print("=" * 60)
    print("Look up waste disposal regulations for any location and waste type!")
    print("\nAvailable waste types:")
    print("• e-waste (electronics, batteries)")
    print("• medical (medications, sharps)")  
    print("• hazardous (paint, chemicals)")
    print("• recyclable (plastic, glass, paper)")
    print("• organic (food scraps, yard waste)")
    print("• household (general trash)")
    print("\nType 'examples' to see example combinations")
    print("Type 'browse' to see available regulations")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        print(f"\n" + "─" * 40)
        
        # Get location
        location_input = input("📍 Enter location (City, State): ").strip()
        
        if location_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Thanks for exploring regulations! Goodbye!")
            break
            
        if location_input.lower() in ['examples', 'ex', 'e']:
            print(f"\n📋 Here are some interesting examples to try:")
            examples = get_example_combinations()
            for i, example in enumerate(examples, 1):
                loc = example['location']
                print(f"   {i:2d}. {example['waste_type']} in {loc['city']}, {loc['state']} - {example['description']}")
            continue
            
        if location_input.lower() in ['browse', 'br', 'b']:
            browse_available_regulations(tool)
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
        
        # Look up regulation
        location_data = {'city': city, 'state': state.upper()}
        test_specific_regulation(tool, location_data, waste_type)
        
        # Ask if they want to continue
        continue_choice = input("\n❓ Look up another regulation? (y/n): ").strip().lower()
        if continue_choice in ['n', 'no']:
            print("👋 Thanks for exploring regulations! Goodbye!")
            break

def main():
    """Main menu for interactive regulation testing"""
    
    try:
        from tools.regulation_lookup import create_regulation_lookup_tool
        
        print("📚 Initializing Regulation Lookup Tool...")
        tool = create_regulation_lookup_tool()
        
        print("🚀 Welcome to the Regulation Lookup Tool Explorer!")
        print("\nWhat would you like to do?")
        print("1. Interactive mode - look up regulations for any location/waste type")
        print("2. Quick demo - see examples with pre-selected combinations")
        print("3. Compare states - see how regulations differ across states")
        print("4. Browse database - see all available regulations")
        print("5. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-5): ").strip()
            
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
                compare_state_regulations(tool)
                
                try_interactive = input("\n❓ Want to try interactive mode? (y/n): ").strip().lower()
                if try_interactive in ['y', 'yes']:
                    interactive_mode(tool)
                break
            elif choice == '4':
                browse_available_regulations(tool)
                
                try_interactive = input("\n❓ Want to try interactive mode? (y/n): ").strip().lower()
                if try_interactive in ['y', 'yes']:
                    interactive_mode(tool)
                break
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")
                
    except ImportError as e:
        print(f"❌ Could not import regulation lookup tool: {e}")
        print("Make sure you've run the setup and tests first!")
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()