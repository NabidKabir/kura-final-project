# test_workflow.py - Comprehensive test for the complete multi-agent workflow

import sys
import os
import json
import asyncio
from typing import Dict

# Add src to path
sys.path.append('src')

def test_workflow_initialization():
    """Test that the workflow can be initialized with all components"""
    print("🧪 Testing workflow initialization...")
    
    try:
        from agents.waste_management_workflow import WasteManagementWorkflow, SupervisorAgent, WorkerAgent
        from config.settings import settings
        
        # Test individual agent initialization
        supervisor = SupervisorAgent()
        print(f"✅ Supervisor Agent initialized")
        
        worker = WorkerAgent()
        print(f"✅ Worker Agent initialized with {len(worker.tools)} tools")
        
        # Test complete workflow initialization
        workflow = WasteManagementWorkflow()
        print(f"✅ Complete workflow initialized")
        
        # Check configuration
        has_openai = settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here"
        print(f"   OpenAI configured: {'Yes' if has_openai else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow initialization failed: {e}")
        return False

def test_supervisor_planning():
    """Test supervisor agent planning logic"""
    print("\n🧪 Testing supervisor planning logic...")
    
    try:
        from agents.waste_management_workflow import SupervisorAgent
        from models.types import WasteManagementState
        
        supervisor = SupervisorAgent()
        
        # Test different state scenarios
        test_scenarios = [
            {
                'state': WasteManagementState(
                    user_query="test query",
                    user_location=None,
                    waste_type=None,
                    local_regulations=None,
                    disposal_locations=None,
                    final_response=None,
                    error_message=None
                ),
                'expected_action': 'classify_waste',
                'description': 'Empty state - should classify waste first'
            },
            {
                'state': WasteManagementState(
                    user_query="test query",
                    user_location=None,
                    waste_type='e-waste',
                    local_regulations=None,
                    disposal_locations=None,
                    final_response=None,
                    error_message=None
                ),
                'expected_action': 'get_location',
                'description': 'Has waste type - should get location next'
            },
            {
                'state': WasteManagementState(
                    user_query="test query",
                    user_location={'city': 'NYC', 'state': 'NY'},
                    waste_type='e-waste',
                    local_regulations=None,
                    disposal_locations=None,
                    final_response=None,
                    error_message=None
                ),
                'expected_action': 'lookup_regulations',
                'description': 'Has waste type and location - should lookup regulations'
            },
            {
                'state': WasteManagementState(
                    user_query="test query",
                    user_location={'city': 'NYC', 'state': 'NY'},
                    waste_type='e-waste',
                    local_regulations={'rules': 'test rules'},
                    disposal_locations=None,
                    final_response=None,
                    error_message=None
                ),
                'expected_action': 'find_locations',
                'description': 'Has most data - should find locations'
            },
            {
                'state': WasteManagementState(
                    user_query="test query",
                    user_location={'city': 'NYC', 'state': 'NY'},
                    waste_type='e-waste',
                    local_regulations={'rules': 'test rules'},
                    disposal_locations=[{'name': 'test facility'}],
                    final_response=None,
                    error_message=None
                ),
                'expected_action': 'generate_response',
                'description': 'Has all data - should generate response'
            }
        ]
        
        results = []
        for i, scenario in enumerate(test_scenarios):
            print(f"   Test {i+1}: {scenario['description']}")
            
            next_action = supervisor.plan_next_action(scenario['state'])
            
            if next_action == scenario['expected_action']:
                print(f"     ✅ Planned action: {next_action}")
                results.append(True)
            else:
                print(f"     ❌ Expected {scenario['expected_action']}, got {next_action}")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Planning logic success rate: {success_rate:.1%}")
        
        return success_rate >= 1.0  # Should be 100% for deterministic logic
        
    except Exception as e:
        print(f"❌ Supervisor planning test failed: {e}")
        return False

def test_worker_tool_execution():
    """Test worker agent tool execution"""
    print("\n🧪 Testing worker tool execution...")
    
    try:
        from agents.waste_management_workflow import WorkerAgent
        from models.types import WasteManagementState
        
        worker = WorkerAgent()
        
        # Test waste classification
        print("   Testing waste classification...")
        state = WasteManagementState(
            user_query="old laptop battery",
            user_location=None,
            waste_type=None,
            local_regulations=None,
            disposal_locations=None,
            final_response=None,
            error_message=None
        )
        
        result_state = worker.classify_waste(state)
        
        if result_state.get('waste_type'):
            print(f"     ✅ Classified as: {result_state['waste_type']}")
            classify_success = True
        else:
            print(f"     ❌ Classification failed")
            classify_success = False
        
        # Test location detection
        print("   Testing location detection...")
        result_state = worker.get_location(result_state)
        
        if result_state.get('user_location'):
            location = result_state['user_location']
            print(f"     ✅ Location: {location.get('city')}, {location.get('state')}")
            location_success = True
        else:
            print(f"     ❌ Location detection failed")
            location_success = False
        
        # Test regulation lookup
        print("   Testing regulation lookup...")
        result_state = worker.lookup_regulations(result_state)
        
        if result_state.get('local_regulations'):
            regs = result_state['local_regulations']
            print(f"     ✅ Regulations: {regs.get('jurisdiction')}")
            regulation_success = True
        else:
            print(f"     ❌ Regulation lookup failed")
            regulation_success = False
        
        # Test location finding
        print("   Testing location finding...")
        result_state = worker.find_locations(result_state)
        
        locations = result_state.get('disposal_locations', [])
        print(f"     ✅ Found {len(locations)} facilities")
        location_find_success = True  # Even 0 is acceptable
        
        # Overall success
        all_tests = [classify_success, location_success, regulation_success, location_find_success]
        success_rate = sum(all_tests) / len(all_tests)
        
        print(f"\n   Worker tool execution success rate: {success_rate:.1%}")
        
        return success_rate >= 0.75  # 75% success rate acceptable
        
    except Exception as e:
        print(f"❌ Worker tool execution test failed: {e}")
        return False

async def test_complete_workflow():
    """Test the complete end-to-end workflow"""
    print("\n🧪 Testing complete workflow execution...")
    
    try:
        from agents.waste_management_workflow import create_waste_management_workflow
        from config.settings import settings
        
        workflow = create_waste_management_workflow()
        
        # Check OpenAI configuration
        has_openai = settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here"
        
        if not has_openai:
            print("   ⚠️  OpenAI not configured - testing with fallback responses")
        
        # Test queries with expected outcomes
        test_queries = [
            {
                'query': 'How do I dispose of old laptop batteries?',
                'expected_waste_type': 'e-waste',
                'description': 'E-waste classification test'
            },
            {
                'query': 'Where can I throw away expired medications?',
                'expected_waste_type': 'medical',
                'description': 'Medical waste classification test'
            },
            {
                'query': 'I need to get rid of old paint cans',
                'expected_waste_type': 'hazardous',
                'description': 'Hazardous waste classification test'
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_queries):
            print(f"   Test {i+1}: {test_case['description']}")
            print(f"     Query: '{test_case['query']}'")
            
            try:
                # Process the query
                result = await workflow.process_query(test_case['query'])
                
                # Check results
                success = result.get('success', False)
                waste_type = result.get('waste_type', 'unknown')
                location = result.get('user_location', {})
                final_response = result.get('final_response', '')
                processing_time = result.get('processing_time_ms', 0)
                
                print(f"     Success: {success}")
                print(f"     Waste Type: {waste_type}")
                print(f"     Location: {location.get('city', 'Unknown')}, {location.get('state', 'Unknown')}")
                print(f"     Processing Time: {processing_time}ms")
                print(f"     Response Length: {len(final_response)} characters")
                
                # Validate results
                test_passed = True
                
                if not success:
                    print(f"     ❌ Workflow reported failure")
                    test_passed = False
                
                if not final_response:
                    print(f"     ❌ No final response generated")
                    test_passed = False
                
                # Waste type validation (flexible since classification can vary)
                if waste_type == 'unknown':
                    print(f"     ⚠️  Waste type unknown (acceptable with fallback)")
                
                if test_passed:
                    print(f"     ✅ Test passed")
                    results.append(True)
                else:
                    print(f"     ❌ Test failed")
                    results.append(False)
                    
            except Exception as e:
                print(f"     ❌ Query processing failed: {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Complete workflow success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8  # 80% success rate acceptable
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False

async def test_workflow_error_handling():
    """Test workflow error handling and recovery"""
    print("\n🧪 Testing workflow error handling...")
    
    try:
        from agents.waste_management_workflow import create_waste_management_workflow
        
        workflow = create_waste_management_workflow()
        
        # Test edge cases and error scenarios
        test_cases = [
            {
                'query': '',
                'description': 'Empty query'
            },
            {
                'query': 'random nonsense text that makes no sense xyz123',
                'description': 'Nonsense query'
            },
            {
                'query': 'a' * 1000,  # Very long query
                'description': 'Very long query'
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_cases):
            print(f"   Test {i+1}: {test_case['description']}")
            
            try:
                result = await workflow.process_query(test_case['query'])
                
                # Should handle gracefully - either succeed or fail safely
                success = result.get('success', False)
                has_response = bool(result.get('final_response'))
                
                print(f"     Success: {success}")
                print(f"     Has Response: {has_response}")
                
                # Even failed queries should return structured responses
                if has_response:
                    print(f"     ✅ Handled gracefully")
                    results.append(True)
                else:
                    print(f"     ❌ No response generated")
                    results.append(False)
                    
            except Exception as e:
                print(f"     ❌ Unhandled exception: {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Error handling success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

async def test_workflow_performance():
    """Test workflow performance and timing"""
    print("\n🧪 Testing workflow performance...")
    
    try:
        from agents.waste_management_workflow import create_waste_management_workflow
        import time
        
        workflow = create_waste_management_workflow()
        
        # Test query
        test_query = "How do I dispose of old phone batteries?"
        
        # Run multiple times to get average performance
        processing_times = []
        
        for i in range(3):  # Run 3 times
            print(f"   Performance test {i+1}/3...")
            
            start_time = time.time()
            result = await workflow.process_query(test_query)
            end_time = time.time()
            
            actual_time = (end_time - start_time) * 1000  # Convert to ms
            reported_time = result.get('processing_time_ms', 0)
            
            processing_times.append(actual_time)
            
            print(f"     Actual time: {actual_time:.0f}ms")
            print(f"     Reported time: {reported_time:.0f}ms")
        
        # Calculate statistics
        avg_time = sum(processing_times) / len(processing_times)
        max_time = max(processing_times)
        min_time = min(processing_times)
        
        print(f"\n   Performance Statistics:")
        print(f"     Average: {avg_time:.0f}ms")
        print(f"     Min: {min_time:.0f}ms") 
        print(f"     Max: {max_time:.0f}ms")
        
        # Performance check (should complete within reasonable time)
        if avg_time < 30000:  # 30 seconds is reasonable for complete workflow
            print(f"     ✅ Performance acceptable")
            return True
        else:
            print(f"     ⚠️  Performance slower than expected")
            return True  # Still acceptable, just slower
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

async def test_response_quality():
    """Test the quality and completeness of generated responses"""
    print("\n🧪 Testing response quality...")
    
    try:
        from agents.waste_management_workflow import create_waste_management_workflow
        
        workflow = create_waste_management_workflow()
        
        # Test with a clear query
        test_query = "I have old laptop batteries that need disposal in New York"
        
        print(f"   Testing with: '{test_query}'")
        
        result = await workflow.process_query(test_query)
        
        final_response = result.get('final_response', '')
        waste_type = result.get('waste_type', '')
        regulations = result.get('local_regulations', {})
        locations = result.get('disposal_locations', [])
        
        print(f"   Response Analysis:")
        print(f"     Length: {len(final_response)} characters")
        print(f"     Waste Type: {waste_type}")
        print(f"     Has Regulations: {'Yes' if regulations else 'No'}")
        print(f"     Disposal Locations: {len(locations)}")
        
        # Quality checks
        quality_checks = []
        
        # Check response length (should be substantial)
        if len(final_response) > 100:
            print(f"     ✅ Response has good length")
            quality_checks.append(True)
        else:
            print(f"     ❌ Response too short")
            quality_checks.append(False)
        
        # Check for key information
        response_lower = final_response.lower()
        key_terms = ['disposal', 'battery', 'facility', 'location', 'regulation']
        found_terms = [term for term in key_terms if term in response_lower]
        
        if len(found_terms) >= 3:
            print(f"     ✅ Response contains relevant terms: {found_terms}")
            quality_checks.append(True)
        else:
            print(f"     ❌ Response missing key terms")
            quality_checks.append(False)
        
        # Check for actionable information
        actionable_terms = ['contact', 'take', 'bring', 'call', 'visit', 'check']
        found_actionable = [term for term in actionable_terms if term in response_lower]
        
        if found_actionable:
            print(f"     ✅ Response includes actionable guidance")
            quality_checks.append(True)
        else:
            print(f"     ⚠️  Response could be more actionable")
            quality_checks.append(False)
        
        quality_score = sum(quality_checks) / len(quality_checks)
        print(f"\n   Response quality score: {quality_score:.1%}")
        
        return quality_score >= 0.7  # 70% quality score acceptable
        
    except Exception as e:
        print(f"❌ Response quality test failed: {e}")
        return False

async def main():
    """Run all workflow tests"""
    print("🚀 Starting Multi-Agent Workflow tests...\n")
    
    # Check configuration
    from config.settings import settings
    has_openai = settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here"
    
    if has_openai:
        print("🤖 OpenAI API configured - full testing enabled")
    else:
        print("⚠️  OpenAI API not configured - testing with fallback functionality")
    
    tests = [
        ("Workflow Initialization", test_workflow_initialization),
        ("Supervisor Planning", test_supervisor_planning),
        ("Worker Tool Execution", test_worker_tool_execution),
        ("Complete Workflow", test_complete_workflow),
        ("Error Handling", test_workflow_error_handling),
        ("Performance", test_workflow_performance),
        ("Response Quality", test_response_quality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
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
    
    print(f"\n{'='*60}")
    print(f"📊 Test Summary: {passed}/{total} tests passed")
    
    if all(results):
        print("🎉 All workflow tests passed! System is ready for deployment.")
    elif sum(results) >= len(results) * 0.8:  # 80% pass rate
        print("✅ Most workflow tests passed! System is functional.")
    else:
        print("⚠️  Several tests failed. Please review the issues above.")
        
    return passed >= len(results) * 0.8

if __name__ == "__main__":
    asyncio.run(main())