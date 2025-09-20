# test_regulation_lookup.py - Comprehensive test for regulation lookup tool

import sys
import os
import json
from typing import Dict

# Add src to path
sys.path.append('src')

def test_tool_initialization():
    """Test that the regulation lookup tool can be initialized"""
    print("🧪 Testing tool initialization...")
    
    try:
        from tools.regulation_lookup import RegulationLookupTool, create_regulation_lookup_tool
        
        # Test direct initialization
        tool = RegulationLookupTool()
        print(f"✅ Tool created successfully: {tool.name}")
        print(f"   Description: {tool.description}")
        print(f"   Database initialized: {len(tool.regulation_db)} jurisdictions")
        
        # Test factory function
        tool2 = create_regulation_lookup_tool()
        print(f"✅ Factory function works: {tool2.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool initialization failed: {e}")
        return False

def test_database_content():
    """Test that the regulation database has expected content"""
    print("\n🧪 Testing regulation database content...")
    
    try:
        from tools.regulation_lookup import RegulationLookupTool
        
        tool = RegulationLookupTool()
        db = tool.regulation_db
        
        # Check that we have expected states
        expected_states = ['NY', 'CA', 'TX', 'DEFAULT']
        missing_states = [state for state in expected_states if state not in db]
        
        if missing_states:
            print(f"❌ Missing states: {missing_states}")
            return False
        else:
            print(f"✅ All expected states present: {expected_states}")
        
        # Check that NY has expected waste types
        ny_waste_types = list(db['NY'].keys())
        expected_waste_types = ['e-waste', 'medical', 'hazardous', 'recyclable', 'organic']
        
        missing_types = [wt for wt in expected_waste_types if wt not in ny_waste_types]
        if missing_types:
            print(f"❌ NY missing waste types: {missing_types}")
            return False
        else:
            print(f"✅ NY has all expected waste types: {len(ny_waste_types)} types")
        
        # Check that regulations have required fields
        sample_reg = db['NY']['e-waste']
        required_fields = ['jurisdiction', 'rules', 'preparation_steps', 'disposal_methods']
        
        missing_fields = [field for field in required_fields if field not in sample_reg]
        if missing_fields:
            print(f"❌ Sample regulation missing fields: {missing_fields}")
            return False
        else:
            print(f"✅ Sample regulation has all required fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Database content test failed: {e}")
        return False

def test_regulation_finding():
    """Test the regulation finding logic"""
    print("\n🧪 Testing regulation finding logic...")
    
    try:
        from tools.regulation_lookup import RegulationLookupTool
        
        tool = RegulationLookupTool()
        
        test_cases = [
            {
                'location': {'city': 'New York', 'state': 'NY'},
                'waste_type': 'e-waste',
                'expected_jurisdiction': 'New York State',
                'should_find': True
            },
            {
                'location': {'city': 'Los Angeles', 'state': 'CA'},
                'waste_type': 'hazardous', 
                'expected_jurisdiction': 'California State',
                'should_find': True
            },
            {
                'location': {'city': 'Miami', 'state': 'FL'},  # FL not in database
                'waste_type': 'e-waste',
                'expected_jurisdiction': 'Federal/General Guidelines',
                'should_find': True  # Should find default
            },
            {
                'location': {'city': 'Austin', 'state': 'TX'},
                'waste_type': 'medical',  # TX doesn't have medical, should use default
                'expected_jurisdiction': 'Federal/General Guidelines', 
                'should_find': True
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_cases):
            print(f"   Test {i+1}: {test_case['waste_type']} in {test_case['location']['city']}, {test_case['location']['state']}")
            
            regulation = tool._find_best_regulation(test_case['location'], test_case['waste_type'])
            
            if test_case['should_find']:
                if regulation:
                    found_jurisdiction = regulation.get('jurisdiction', 'Unknown')
                    print(f"     Found: {found_jurisdiction}")
                    
                    # Check if jurisdiction matches expected (allowing for partial matches)
                    if test_case['expected_jurisdiction'] in found_jurisdiction or found_jurisdiction in test_case['expected_jurisdiction']:
                        print(f"     ✅ Correct jurisdiction")
                        results.append(True)
                    else:
                        print(f"     ❌ Expected '{test_case['expected_jurisdiction']}', got '{found_jurisdiction}'")
                        results.append(False)
                else:
                    print(f"     ❌ No regulation found when expected")
                    results.append(False)
            else:
                if not regulation:
                    print(f"     ✅ No regulation found as expected")
                    results.append(True)
                else:
                    print(f"     ❌ Found regulation when none expected")
                    results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Regulation finding success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8
        
    except Exception as e:
        print(f"❌ Regulation finding test failed: {e}")
        return False

def test_fallback_generation():
    """Test fallback regulation creation"""
    print("\n🧪 Testing fallback regulation generation...")
    
    try:
        from tools.regulation_lookup import RegulationLookupTool
        
        tool = RegulationLookupTool()
        
        test_cases = [
            {'waste_type': 'e-waste', 'location': {'state': 'ZZ'}},
            {'waste_type': 'medical', 'location': {'state': 'XX'}}, 
            {'waste_type': 'unknown', 'location': {'state': 'YY'}}  # Unknown waste type
        ]
        
        results = []
        for i, test_case in enumerate(test_cases):
            print(f"   Test {i+1}: {test_case['waste_type']} fallback")
            
            fallback = tool._create_fallback_regulation(
                test_case['waste_type'], 
                test_case['location']
            )
            
            # Check required fields
            required_fields = ['jurisdiction', 'rules', 'preparation_steps', 'disposal_methods']
            has_all_fields = all(field in fallback for field in required_fields)
            
            if has_all_fields:
                print(f"     ✅ Has all required fields")
                print(f"     Jurisdiction: {fallback['jurisdiction']}")
                print(f"     Rules: {fallback['rules'][:50]}...")
                results.append(True)
            else:
                missing = [f for f in required_fields if f not in fallback]
                print(f"     ❌ Missing fields: {missing}")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Fallback generation success rate: {success_rate:.1%}")
        
        return success_rate >= 1.0  # Should always work
        
    except Exception as e:
        print(f"❌ Fallback generation test failed: {e}")
        return False

def test_full_regulation_lookup():
    """Test the full regulation lookup workflow"""
    print("\n🧪 Testing full regulation lookup workflow...")
    
    try:
        from tools.regulation_lookup import RegulationLookupTool
        
        tool = RegulationLookupTool()
        
        test_queries = [
            # JSON format queries
            {
                'query': json.dumps({
                    'location': {'city': 'New York', 'state': 'NY'},
                    'waste_type': 'e-waste'
                }),
                'description': 'NY e-waste (JSON format)'
            },
            {
                'query': json.dumps({
                    'location': {'city': 'San Francisco', 'state': 'CA'},
                    'waste_type': 'hazardous'
                }),
                'description': 'CA hazardous (JSON format)'
            },
            # String format queries
            {
                'query': 'medical in TX',
                'description': 'TX medical (string format)'
            },
            {
                'query': 'recyclable in FL',
                'description': 'FL recyclable (fallback case)'
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_queries):
            print(f"   Test {i+1}: {test_case['description']}")
            
            try:
                result_json = tool._run(test_case['query'])
                result = json.loads(result_json)
                
                print(f"     Jurisdiction: {result.get('jurisdiction')}")
                print(f"     Has rules: {'Yes' if result.get('rules') else 'No'}")
                print(f"     Preparation steps: {len(result.get('preparation_steps', []))}")
                print(f"     Disposal methods: {len(result.get('disposal_methods', []))}")
                
                # Validate required fields
                required_fields = ['jurisdiction', 'rules']
                has_required = all(result.get(field) for field in required_fields)
                
                if has_required:
                    print(f"     ✅ Valid regulation returned")
                    results.append(True)
                else:
                    print(f"     ❌ Missing required fields")
                    results.append(False)
                    
            except Exception as e:
                print(f"     ❌ Query failed: {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n   Full lookup success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8
        
    except Exception as e:
        print(f"❌ Full regulation lookup test failed: {e}")
        return False

def test_data_model_integration():
    """Test integration with RegulationInfo model"""
    print("\n🧪 Testing data model integration...")
    
    try:
        from tools.regulation_lookup import RegulationLookupTool
        from models.types import RegulationInfo, WasteType
        from datetime import datetime
        
        tool = RegulationLookupTool()
        
        # Get a regulation and try to create RegulationInfo from it
        query = json.dumps({
            'location': {'city': 'New York', 'state': 'NY'},
            'waste_type': 'e-waste'
        })
        
        result_json = tool._run(query)
        result_dict = json.loads(result_json)
        
        print(f"   Testing with NY e-waste regulation...")
        
        # Try to create RegulationInfo model
        # Handle datetime parsing
        last_updated = result_dict.get('last_updated')
        if isinstance(last_updated, str):
            last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        
        regulation_info = RegulationInfo(
            jurisdiction=result_dict['jurisdiction'],
            waste_type=WasteType(result_dict['waste_type']),
            rules=result_dict['rules'],
            preparation_steps=result_dict.get('preparation_steps', []),
            restrictions=result_dict.get('restrictions', []),
            penalties=result_dict.get('penalties'),
            last_updated=last_updated,
            source_url=result_dict.get('source_url')
        )
        
        print(f"   ✅ RegulationInfo model created successfully")
        print(f"     Jurisdiction: {regulation_info.jurisdiction}")
        print(f"     Waste Type: {regulation_info.waste_type.value}")
        print(f"     Preparation Steps: {len(regulation_info.preparation_steps)}")
        
        # Test JSON serialization
        json_data = regulation_info.dict()
        if "jurisdiction" in json_data and "waste_type" in json_data:
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
        from tools.regulation_lookup import RegulationLookupTool
        
        tool = RegulationLookupTool()
        
        edge_cases = [
            ("", "empty string"),
            ("invalid json", "invalid JSON"),
            ('{"location": {}, "waste_type": ""}', "empty location and waste type"),
            ('{"location": {"state": "INVALID"}, "waste_type": "unknown"}', "invalid state and waste type"),
            ('{"location": null, "waste_type": "e-waste"}', "null location")
        ]
        
        results = []
        for query, description in edge_cases:
            print(f"   Testing {description}: '{query[:30]}...'")
            
            try:
                result_json = tool._run(query)
                result = json.loads(result_json)
                
                # Should always get some result, even if it's fallback
                has_jurisdiction = result.get('jurisdiction')
                has_rules = result.get('rules')
                
                if has_jurisdiction and has_rules:
                    print(f"     ✅ Handled gracefully: {has_jurisdiction[:30]}...")
                    results.append(True)
                else:
                    print(f"     ❌ Failed to handle edge case properly")
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

def test_different_states():
    """Test regulations for different states to show variety"""
    print("\n🧪 Testing different state regulations...")
    
    try:
        from tools.regulation_lookup import RegulationLookupTool
        
        tool = RegulationLookupTool()
        
        state_tests = [
            {'state': 'NY', 'waste_type': 'e-waste', 'name': 'New York'},
            {'state': 'CA', 'waste_type': 'e-waste', 'name': 'California'},
            {'state': 'TX', 'waste_type': 'e-waste', 'name': 'Texas'},
            {'state': 'WA', 'waste_type': 'e-waste', 'name': 'Washington (fallback)'}
        ]
        
        results = []
        for test in state_tests:
            query = json.dumps({
                'location': {'state': test['state']},
                'waste_type': test['waste_type']
            })
            
            print(f"   Testing {test['name']} e-waste regulations...")
            
            result_json = tool._run(query)
            result = json.loads(result_json)
            
            jurisdiction = result.get('jurisdiction', 'Unknown')
            rules = result.get('rules', '')
            
            print(f"     Jurisdiction: {jurisdiction}")
            print(f"     Rules preview: {rules[:80]}...")
            
            if jurisdiction and rules:
                results.append(True)
                print(f"     ✅ Got regulation")
            else:
                results.append(False)
                print(f"     ❌ No regulation")
        
        success_rate = sum(results) / len(results)
        print(f"\n   Different states success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8
        
    except Exception as e:
        print(f"❌ Different states test failed: {e}")
        return False

def main():
    """Run all regulation lookup tests"""
    print("🚀 Starting Regulation Lookup Tool tests...\n")
    
    tests = [
        ("Tool Initialization", test_tool_initialization),
        ("Database Content", test_database_content),
        ("Regulation Finding", test_regulation_finding),
        ("Fallback Generation", test_fallback_generation),
        ("Full Regulation Lookup", test_full_regulation_lookup),
        ("Data Model Integration", test_data_model_integration),
        ("Edge Cases", test_edge_cases),
        ("Different States", test_different_states)
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
        print("🎉 All regulation lookup tests passed! Tool is ready.")
    elif sum(results) >= len(results) * 0.8:  # 80% pass rate
        print("✅ Most regulation lookup tests passed! Tool is functional.")
    else:
        print("⚠️  Several tests failed. Please review the issues above.")
        
    return passed >= len(results) * 0.8

if __name__ == "__main__":
    main()