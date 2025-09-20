# test_basic_setup.py - Test our basic setup

import sys
import os
sys.path.append('src')

def test_configuration():
    """Test that configuration loads properly"""
    print("🧪 Testing configuration setup...")
    
    try:
        from config.settings import settings, validate_settings
        
        print(f"✅ Settings loaded:")
        print(f"   Environment: {settings.environment}")
        print(f"   LLM Model: {settings.llm_model}")
        print(f"   Database URL: {settings.database_url}")
        print(f"   API Port: {settings.api_port}")
        
        # Note: We'll skip validation for now since OpenAI key might not be set yet
        if settings.openai_api_key:
            validate_settings()
        else:
            print("⚠️  OpenAI API key not set - add it to .env file later")
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_data_models():
    """Test that our data models work correctly"""
    print("\n🧪 Testing data models...")
    
    try:
        from models.types import (
            WasteType, HazardLevel, WasteClassificationResult, 
            LocationModel, UserQuery, WasteManagementState
        )
        
        # Test enum types
        print(f"✅ Waste types available: {list(WasteType)}")
        print(f"✅ Hazard levels available: {list(HazardLevel)}")
        
        # Test creating a classification result
        classification = WasteClassificationResult(
            primary_type=WasteType.E_WASTE,
            sub_type="battery",
            confidence=0.85,
            hazard_level=HazardLevel.MEDIUM,
            special_handling=True,
            description="Laptop battery disposal"
        )
        print(f"✅ Created classification: {classification.primary_type} ({classification.confidence})")
        
        # Test location model
        location = LocationModel(
            city="New York",
            state="NY",
            zipcode="10001",
            latitude=40.7128,
            longitude=-74.0060
        )
        print(f"✅ Created location: {location.city}, {location.state}")
        
        # Test user query model
        query = UserQuery(
            query="How do I dispose of old laptop batteries?",
            location=location
        )
        print(f"✅ Created user query: {query.query[:50]}...")
        
        # Test state management
        state = WasteManagementState(
            user_query=query.query,
            user_location=location.dict(),
            waste_type=None,
            waste_classification=None,
            local_regulations=None,
            disposal_locations=None,
            final_response=None,
            error_message=None
        )
        print(f"✅ Created workflow state with query: {state['user_query'][:30]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Data models test failed: {e}")
        return False

def test_dependencies():
    """Test that key dependencies are available"""
    print("\n🧪 Testing key dependencies...")
    
    dependencies = [
        "pydantic",
        "fastapi", 
        "langchain",
        "langgraph",
        "openai"
    ]
    
    results = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} imported successfully")
            results.append(True)
        except ImportError as e:
            print(f"❌ {dep} import failed: {e}")
            results.append(False)
    
    return all(results)

def main():
    """Run all basic tests"""
    print("🚀 Starting basic setup tests...\n")
    
    tests = [
        ("Configuration", test_configuration),
        ("Data Models", test_data_models), 
        ("Dependencies", test_dependencies)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            if result:
                print(f"✅ {test_name} test passed!\n")
            else:
                print(f"❌ {test_name} test failed!\n")
        except Exception as e:
            print(f"💥 {test_name} test crashed: {e}\n")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 Test Summary: {passed}/{total} tests passed")
    
    if all(results):
        print("🎉 All basic setup tests passed! Ready for next step.")
    else:
        print("⚠️  Some tests failed. Please fix issues before continuing.")
        
    return all(results)

if __name__ == "__main__":
    main()