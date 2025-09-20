# interactive_classifier_test.py - Interactive testing of the Waste Classification Tool

import sys
import os
import json
from typing import Dict

# Add src to path
sys.path.append('src')

def display_classification_result(result_json: str, source: str = ""):
    """Display classification results in a nice format"""
    try:
        result = json.loads(result_json)
        
        print(f"\n🎯 Classification Result {source}:")
        print("=" * 50)
        print(f"🗂️  Waste Type: {result['primary_type'].upper()}")
        if result.get('sub_type'):
            print(f"📋 Sub-category: {result['sub_type']}")
        print(f"🎯 Confidence: {result['confidence']:.1%}")
        print(f"⚠️  Hazard Level: {result['hazard_level'].upper()}")
        print(f"🔧 Special Handling Required: {'YES' if result['special_handling'] else 'NO'}")
        
        if result.get('description'):
            print(f"💡 Reasoning: {result['description']}")
            
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error displaying result: {e}")

def test_specific_item(tool, waste_description: str):
    """Test classification for a specific waste item"""
    
    print(f"\n🔍 Analyzing: '{waste_description}'")
    print("⏳ Processing...")
    
    # Test with full tool (OpenAI + fallback)
    try:
        result_json = tool._run(waste_description)
        display_classification_result(result_json, "(OpenAI + Fallback)")
        
        # Also show what fallback alone would give
        print(f"\n🔄 For comparison, fallback classification only:")
        fallback_result = tool._fallback_classification(waste_description)
        fallback_json = json.dumps({
            "primary_type": fallback_result["primary_type"],
            "sub_type": fallback_result.get("sub_type", "general"),
            "confidence": fallback_result["confidence"],
            "hazard_level": fallback_result["hazard_level"],
            "special_handling": fallback_result["special_handling"],
            "description": fallback_result.get("reasoning", "Keyword-based classification")
        })
        display_classification_result(fallback_json, "(Fallback Only)")
        
    except Exception as e:
        print(f"❌ Classification failed: {e}")

def get_example_items():
    """Return a list of interesting example items to test"""
    return [
        "old iPhone with cracked screen and dead battery",
        "expired prescription painkillers from last year", 
        "half-empty can of latex wall paint",
        "used motor oil from car maintenance",
        "pile of old magazines and newspapers",
        "broken LED light bulbs",
        "leftover birthday cake and food scraps",
        "empty plastic detergent containers",
        "old smoke detector (might contain radioactive material)",
        "used syringes from diabetes medication",
        "car battery that won't hold charge anymore",
        "bag of grass clippings and leaves",
        "old laptop computer that doesn't work",
        "bottle of expired nail polish remover",
        "cardboard boxes from online shopping"
    ]

def interactive_mode():
    """Interactive mode where user can input their own waste descriptions"""
    
    try:
        from tools.waste_classifier import create_waste_classifier
        from config.settings import settings
        
        print("🧠 Initializing Waste Classification Tool...")
        tool = create_waste_classifier()
        
        # Check if OpenAI is configured
        has_openai = settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here"
        
        if has_openai:
            print("🔑 OpenAI API configured - you'll get AI-powered classifications!")
        else:
            print("⚠️  OpenAI not configured - using keyword-based fallback only")
            print("   (Still very accurate for most common waste types!)")
        
        print("\n" + "="*60)
        print("🗑️  INTERACTIVE WASTE CLASSIFICATION TOOL")
        print("="*60)
        print("Enter waste descriptions and see how they get classified!")
        print("Type 'examples' to see example items")
        print("Type 'quit' to exit")
        print("="*60)
        
        while True:
            print("\n" + "─" * 40)
            user_input = input("🗑️  What waste do you want to classify? ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for testing! Goodbye!")
                break
                
            if user_input.lower() in ['examples', 'ex', 'e']:
                print("\n📋 Here are some interesting examples to try:")
                examples = get_example_items()
                for i, example in enumerate(examples, 1):
                    print(f"   {i:2d}. {example}")
                print("\nCopy any of these to test, or create your own!")
                continue
            
            # Classify the waste
            test_specific_item(tool, user_input)
            
            # Ask if they want to continue
            continue_choice = input("\n❓ Test another item? (y/n): ").strip().lower()
            if continue_choice in ['n', 'no']:
                print("👋 Thanks for testing! Goodbye!")
                break
                
    except ImportError as e:
        print(f"❌ Could not import waste classifier: {e}")
        print("Make sure you've run the setup and tests first!")
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def quick_demo():
    """Run a quick demo with pre-selected interesting items"""
    
    try:
        from tools.waste_classifier import create_waste_classifier
        
        print("🧠 Initializing Waste Classification Tool...")
        tool = create_waste_classifier()
        
        print("\n" + "="*60)
        print("🎬 QUICK DEMO - Waste Classification Examples")
        print("="*60)
        
        demo_items = [
            "old smartphone that won't charge",
            "leftover prescription antibiotics",
            "empty plastic yogurt containers", 
            "used car engine oil",
            "banana peels and coffee grounds"
        ]
        
        for i, item in enumerate(demo_items, 1):
            print(f"\n🎬 Demo {i}/{len(demo_items)}")
            test_specific_item(tool, item)
            
            if i < len(demo_items):
                input("Press Enter to continue to next demo...")
        
        print(f"\n🎉 Demo complete! You've seen {len(demo_items)} different waste types classified.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def main():
    """Main menu for interactive testing"""
    
    print("🚀 Welcome to the Waste Classification Tool Tester!")
    print("\nWhat would you like to do?")
    print("1. Interactive mode - classify your own waste descriptions")
    print("2. Quick demo - see examples with pre-selected items")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            interactive_mode()
            break
        elif choice == '2':
            quick_demo()
            
            # Ask if they want to try interactive mode too
            try_interactive = input("\n❓ Want to try interactive mode too? (y/n): ").strip().lower()
            if try_interactive in ['y', 'yes']:
                interactive_mode()
            break
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()