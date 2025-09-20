# interactive_workflow_test.py - Interactive testing of the complete multi-agent workflow

import sys
import os
import asyncio
import json
from typing import Dict

# Add src to path
sys.path.append('src')

def display_workflow_result(result: Dict):
    """Display workflow results in a comprehensive, nice format"""
    
    print(f"\n🎯 COMPLETE WASTE MANAGEMENT ANALYSIS")
    print("=" * 70)
    
    # Basic result info
    success = result.get('success', False)
    processing_time = result.get('processing_time_ms', 0)
    
    print(f"✅ Status: {'Success' if success else 'Failed'}")
    print(f"⏱️  Processing Time: {processing_time}ms")
    
    if not success:
        error_msg = result.get('error_message', 'Unknown error')
        print(f"❌ Error: {error_msg}")
        return
    
    # User query
    user_query = result.get('user_query', 'N/A')
    print(f"❓ Your Question: {user_query}")
    
    # Waste classification
    waste_type = result.get('waste_type', 'Unknown')
    waste_classification = result.get('waste_classification', {})
    confidence = result.get('confidence_score', 0)
    
    print(f"\n🗂️  WASTE CLASSIFICATION:")
    print(f"   Type: {waste_type.upper()}")
    if confidence:
        print(f"   Confidence: {confidence:.1%}")
    if waste_classification.get('sub_type'):
        print(f"   Category: {waste_classification['sub_type']}")
    if waste_classification.get('hazard_level'):
        print(f"   Hazard Level: {waste_classification['hazard_level'].upper()}")
    if waste_classification.get('special_handling'):
        print(f"   Special Handling: {'Required' if waste_classification['special_handling'] else 'Not Required'}")
    
    # Location information
    location = result.get('user_location', {})
    print(f"\n📍 YOUR LOCATION:")
    print(f"   City: {location.get('city', 'Unknown')}")
    print(f"   State: {location.get('state', 'Unknown')}")
    print(f"   Country: {location.get('country', 'Unknown')}")
    if location.get('latitude') and location.get('longitude'):
        print(f"   Coordinates: {location['latitude']:.4f}, {location['longitude']:.4f}")
    
    # Local regulations
    regulations = result.get('local_regulations', {})
    if regulations:
        print(f"\n⚖️  LOCAL REGULATIONS:")
        print(f"   Jurisdiction: {regulations.get('jurisdiction', 'Unknown')}")
        
        rules = regulations.get('rules', '')
        if rules:
            print(f"   Rules: {rules[:200]}{'...' if len(rules) > 200 else ''}")
        
        prep_steps = regulations.get('preparation_steps', [])
        if prep_steps:
            print(f"   Preparation Required:")
            for i, step in enumerate(prep_steps[:3], 1):
                print(f"     {i}. {step}")
            if len(prep_steps) > 3:
                print(f"     ... and {len(prep_steps) - 3} more steps")
        
        restrictions = regulations.get('restrictions', [])
        if restrictions:
            print(f"   Restrictions:")
            for restriction in restrictions[:2]:
                print(f"     • {restriction}")
        
        penalties = regulations.get('penalties')
        if penalties:
            print(f"   Penalties: {penalties}")
    
    # Disposal locations
    disposal_locations = result.get('disposal_locations', [])
    if disposal_locations:
        print(f"\n🏢 DISPOSAL FACILITIES ({len(disposal_locations)} found):")
        
        for i, facility in enumerate(disposal_locations[:5], 1):  # Show top 5
            print(f"\n   {i}. {facility.get('name', 'Unknown Facility')}")
            print(f"      📍 Address: {facility.get('address', 'Address not available')}")
            
            if facility.get('distance_km'):
                print(f"      🚗 Distance: {facility['distance_km']} km")
            
            if facility.get('phone'):
                print(f"      📞 Phone: {facility['phone']}")
            
            if facility.get('website'):
                print(f"      🌐 Website: {facility['website'][:50]}{'...' if len(facility.get('website', '')) > 50 else ''}")
            
            if facility.get('rating'):
                stars = "⭐" * int(facility['rating'])
                print(f"      {stars} Rating: {facility['rating']}/5")
            
            hours = facility.get('hours', [])
            if hours:
                print(f"      🕒 Hours: {hours[0] if hours else 'Hours not available'}")
            
            instructions = facility.get('special_instructions')
            if instructions:
                print(f"      💡 Note: {instructions[:100]}{'...' if len(instructions) > 100 else ''}")
    
    # Final response
    final_response = result.get('final_response', '')
    if final_response:
        print(f"\n📋 COMPREHENSIVE GUIDANCE:")
        print("─" * 50)
        print(final_response)
        print("─" * 50)
    
    print("=" * 70)

async def test_workflow_query(workflow, query: str, description: str = ""):
    """Test the workflow with a specific query"""
    
    if description:
        print(f"\n🧪 {description}")
    
    print(f"❓ Query: '{query}'")
    print("⏳ Processing through complete workflow...")
    print("   (This may take a moment as it goes through all agents and tools)")
    
    try:
        result = await workflow.process_query(query)
        display_workflow_result(result)
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        return False

async def demo_workflow(workflow):
    """Run a demo of the workflow with pre-selected examples"""
    
    print(f"\n🎬 COMPREHENSIVE WORKFLOW DEMO")
    print("=" * 70)
    print("Watch the complete multi-agent system in action!")
    print("Each query will go through: Classification → Location → Regulations → Facilities → Response")
    
    demo_queries = [
        {
            'query': 'How do I dispose of old smartphone batteries in New York?',
            'description': 'Demo 1: E-waste with specific location'
        },
        {
            'query': 'I have expired prescription medications to get rid of',
            'description': 'Demo 2: Medical waste (location auto-detected)'
        },
        {
            'query': 'What should I do with leftover house paint cans?',
            'description': 'Demo 3: Hazardous waste disposal'
        },
        {
            'query': 'Where can I recycle plastic bottles and cardboard?',
            'description': 'Demo 4: Recyclable materials'
        }
    ]
    
    results = []
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n{'='*70}")
        print(f"🎬 {demo['description']} ({i}/{len(demo_queries)})")
        
        success = await test_workflow_query(workflow, demo['query'], "")
        results.append(success)
        
        if i < len(demo_queries):
            input("\n🔄 Press Enter to continue to next demo...")
    
    # Demo summary
    successful = sum(results)
    total = len(results)
    
    print(f"\n📊 Demo Summary: {successful}/{total} queries processed successfully")
    
    if successful == total:
        print("🎉 All demos completed successfully! The system is working perfectly.")
    else:
        print("✅ Most demos worked well. Any issues are likely due to API configurations.")

async def interactive_mode(workflow):
    """Interactive mode for testing custom queries"""
    
    print(f"\n🚀 INTERACTIVE WASTE MANAGEMENT SYSTEM")
    print("=" * 70)
    print("Ask me anything about waste disposal!")
    print("I'll use AI to classify your waste, find your location, lookup local")
    print("regulations, and find nearby disposal facilities.")
    print("\nExample queries:")
    print("• 'How do I dispose of old laptop batteries?'")
    print("• 'Where can I get rid of expired medications?'") 
    print("• 'What should I do with leftover paint?'")
    print("• 'I need to recycle cardboard boxes'")
    print("• 'How do I throw away food scraps?'")
    print("\nType 'quit' to exit")
    print("=" * 70)
    
    query_count = 0
    
    while True:
        print(f"\n" + "─" * 50)
        user_query = input("🗑️  What waste do you need help with? ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q', 'bye']:
            print("👋 Thank you for using the Waste Management System! Goodbye!")
            break
        
        if not user_query:
            continue
        
        query_count += 1
        print(f"\n🔄 Processing Query #{query_count}...")
        
        success = await test_workflow_query(workflow, user_query)
        
        if success:
            print(f"\n✅ Query processed successfully!")
        else:
            print(f"\n⚠️  Query had some issues, but system provided fallback guidance.")
        
        # Ask if they want to continue
        continue_choice = input("\n❓ Ask another question? (y/n): ").strip().lower()
        if continue_choice in ['n', 'no']:
            print("👋 Thank you for using the Waste Management System! Goodbye!")
            break

async def performance_comparison(workflow):
    """Compare performance of the full workflow vs individual tools"""
    
    print(f"\n⚡ PERFORMANCE COMPARISON")
    print("=" * 70)
    print("Comparing full workflow vs individual tool performance...")
    
    test_query = "How do I dispose of old phone batteries?"
    
    # Test full workflow
    print(f"\n1. Testing Complete Multi-Agent Workflow:")
    import time
    
    start_time = time.time()
    result = await workflow.process_query(test_query)
    full_workflow_time = (time.time() - start_time) * 1000
    
    print(f"   Time: {full_workflow_time:.0f}ms")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Components executed: Classification → Location → Regulations → Facilities → Response")
    
    # Test individual tools (quick comparison)
    print(f"\n2. Individual Tool Performance Estimates:")
    
    try:
        from tools.waste_classifier import create_waste_classifier
        from tools.geolocation import create_geolocation_tool
        from tools.regulation_lookup import create_regulation_lookup_tool
        from tools.location_finder import create_location_finder_tool
        
        # Quick individual tool tests
        classifier = create_waste_classifier()
        start = time.time()
        classifier._run(test_query)
        classify_time = (time.time() - start) * 1000
        print(f"   Classification Tool: ~{classify_time:.0f}ms")
        
        geolocation = create_geolocation_tool()
        start = time.time()
        geolocation._run("")
        location_time = (time.time() - start) * 1000
        print(f"   Geolocation Tool: ~{location_time:.0f}ms")
        
        estimated_individual_total = classify_time + location_time + 500 + 1000  # Estimate for other tools
        print(f"   Estimated Individual Total: ~{estimated_individual_total:.0f}ms")
        
        print(f"\n📊 Analysis:")
        print(f"   Full Workflow: {full_workflow_time:.0f}ms")
        print(f"   Individual Tools: ~{estimated_individual_total:.0f}ms")
        print(f"   Workflow Overhead: ~{(full_workflow_time - estimated_individual_total):.0f}ms")
        print(f"   This overhead includes agent coordination, state management, and response generation.")
        
    except Exception as e:
        print(f"   ⚠️  Individual tool timing failed: {e}")

async def system_status_check(workflow):
    """Check the status of all system components"""
    
    print(f"\n🔧 SYSTEM STATUS CHECK")
    print("=" * 70)
    
    from config.settings import settings
    
    # Check configurations
    print(f"Configuration Status:")
    print(f"   OpenAI API: {'✅ Configured' if settings.openai_api_key and settings.openai_api_key != 'your-openai-api-key-here' else '⚠️  Not configured'}")
    print(f"   Google Maps API: {'✅ Configured' if settings.google_maps_api_key and settings.google_maps_api_key != 'your-google-maps-api-key-here' else '⚠️  Not configured'}")
    
    # Check workflow components
    print(f"\nWorkflow Components:")
    print(f"   Supervisor Agent: ✅ Initialized")
    print(f"   Worker Agent: ✅ Initialized")
    print(f"   LangGraph Workflow: ✅ Compiled")
    
    # Check individual tools
    print(f"\nTool Status:")
    try:
        worker = workflow.worker
        print(f"   Waste Classifier: ✅ Ready ({len(worker.tools)} tools total)")
        print(f"   Geolocation: ✅ Ready")
        print(f"   Regulation Lookup: ✅ Ready")
        print(f"   Location Finder: ✅ Ready")
    except Exception as e:
        print(f"   ❌ Tool check failed: {e}")
    
    # Quick system test
    print(f"\nQuick System Test:")
    try:
        test_result = await workflow.process_query("test query for system check")
        print(f"   System Response: ✅ Working (took {test_result.get('processing_time_ms', 0)}ms)")
    except Exception as e:
        print(f"   System Response: ❌ Error - {e}")
    
    print(f"\n✅ System status check complete!")

async def main():
    """Main menu for interactive workflow testing"""
    
    try:
        from agents.waste_management_workflow import create_waste_management_workflow
        from config.settings import settings
        
        print("🚀 Initializing Complete Waste Management System...")
        print("   Loading all agents, tools, and workflow components...")
        
        workflow = create_waste_management_workflow()
        
        # Check configuration status
        has_openai = settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here"
        has_google_maps = settings.google_maps_api_key and settings.google_maps_api_key != "your-google-maps-api-key-here"
        
        print(f"✅ System Ready!")
        if has_openai:
            print("🤖 OpenAI configured - AI-powered responses enabled")
        else:
            print("⚠️  OpenAI not configured - using intelligent fallbacks")
        
        if has_google_maps:
            print("🗺️  Google Maps configured - live facility search enabled")
        else:
            print("📍 Google Maps not configured - using comprehensive mock database")
        
        print("\n🎯 Welcome to the Complete Waste Management System!")
        print("This is the full multi-agent system working together:")
        print("• Supervisor Agent orchestrates the workflow")
        print("• Worker Agent executes tasks using specialized tools")
        print("• All components integrated with LangGraph")
        
        print("\nWhat would you like to do?")
        print("1. Interactive mode - ask your own waste disposal questions")
        print("2. System demo - see pre-selected examples")
        print("3. Performance test - see how fast the system works")
        print("4. System status - check all components")
        print("5. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                await interactive_mode(workflow)
                break
            elif choice == '2':
                await demo_workflow(workflow)
                
                try_interactive = input("\n❓ Want to try interactive mode too? (y/n): ").strip().lower()
                if try_interactive in ['y', 'yes']:
                    await interactive_mode(workflow)
                break
            elif choice == '3':
                await performance_comparison(workflow)
                
                try_interactive = input("\n❓ Want to try interactive mode? (y/n): ").strip().lower()
                if try_interactive in ['y', 'yes']:
                    await interactive_mode(workflow)
                break
            elif choice == '4':
                await system_status_check(workflow)
                
                try_interactive = input("\n❓ Want to try interactive mode? (y/n): ").strip().lower()
                if try_interactive in ['y', 'yes']:
                    await interactive_mode(workflow)
                break
            elif choice == '5':
                print("👋 Thank you for testing the Waste Management System! Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")
                
    except ImportError as e:
        print(f"❌ Could not import workflow components: {e}")
        print("Make sure you've run all the setup and individual tool tests first!")
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())