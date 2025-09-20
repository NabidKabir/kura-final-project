# src/tools/waste_classifier.py - Intelligent waste classification using OpenAI

import json
import re
from typing import Dict, Optional
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from pydantic import Field

# Import our data models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from models.types import WasteType, HazardLevel, WasteClassificationResult
from config.settings import settings

class WasteClassificationTool(BaseTool):
    """
    This tool classifies waste based on user descriptions using OpenAI.
    
    How it works:
    1. Takes a user's description of waste
    2. Uses a carefully crafted prompt to guide OpenAI's classification  
    3. Returns structured data about waste type, hazard level, and handling requirements
    4. Includes confidence scoring and fallback logic
    """
    
    name: str = "waste_classifier"
    description: str = (
        "Classifies waste type based on user description. "
        "Input should be a description of the waste item. "
        "Returns waste type, hazard level, and disposal requirements."
    )
    
    # Initialize the OpenAI model
    llm: ChatOpenAI = Field(default_factory=lambda: ChatOpenAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        openai_api_key=settings.openai_api_key
    ))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"🧠 Waste Classification Tool initialized with model: {settings.llm_model}")

    def _create_classification_prompt(self, waste_description: str) -> list:
        """
        Create a structured prompt that guides OpenAI to classify waste correctly.
        This prompt engineering is crucial for accurate classification.
        """
        
        system_message = SystemMessage(content=f"""
You are an expert waste management classifier. Your job is to classify waste items based on descriptions and provide disposal guidance.

WASTE CATEGORIES:
- e-waste: Electronics, batteries, computers, phones, cables, electronic components
- medical: Medications, needles, syringes, medical devices, bandages, medical waste
- hazardous: Chemicals, paint, oil, pesticides, cleaning products, toxic materials
- recyclable: Paper, cardboard, plastic bottles, glass, aluminum cans, clean containers
- organic: Food scraps, yard waste, compostable materials
- household: General trash that doesn't fit other categories

HAZARD LEVELS:
- low: Safe for normal handling (recyclables, organic waste)
- medium: Requires some caution (some e-waste, household chemicals)
- high: Requires special handling (medical sharps, toxic chemicals)
- critical: Extremely dangerous, requires professional disposal (asbestos, radioactive materials)

Respond ONLY with a JSON object in this exact format:
{{
    "primary_type": "one of: e-waste, medical, hazardous, recyclable, organic, household",
    "sub_type": "specific category like 'battery', 'medication', 'paint', etc.",
    "confidence": 0.XX,
    "hazard_level": "one of: low, medium, high, critical",
    "special_handling": true/false,
    "reasoning": "brief explanation of classification",
    "preparation_needed": ["list", "of", "preparation", "steps"]
}}
""")
        
        human_message = HumanMessage(content=f"""
Classify this waste item: "{waste_description}"

Consider:
- What material is it made of?
- Are there any hazardous components?
- What's the best disposal method?
- Any special handling requirements?

Respond with JSON only.
""")
        
        return [system_message, human_message]

    def _fallback_classification(self, waste_description: str) -> Dict:
        """
        Fallback classification using simple keyword matching if OpenAI fails.
        This ensures our system always provides some response.
        """
        
        waste_description_lower = waste_description.lower()
        
        # Define keyword patterns for each waste type
        classification_rules = [
            # E-waste patterns
            {
                "keywords": ["battery", "electronic", "computer", "laptop", "phone", "tablet", "tv", "monitor", "cable", "charger"],
                "type": "e-waste",
                "sub_type": "electronics",
                "hazard": "medium",
                "special_handling": True
            },
            # Medical waste patterns
            {
                "keywords": ["needle", "syringe", "medication", "medicine", "pill", "bandage", "medical", "thermometer"],
                "type": "medical", 
                "sub_type": "medical_device",
                "hazard": "high",
                "special_handling": True
            },
            # Hazardous waste patterns
            {
                "keywords": ["paint", "oil", "chemical", "pesticide", "cleaner", "solvent", "acid", "gasoline"],
                "type": "hazardous",
                "sub_type": "chemical",
                "hazard": "high", 
                "special_handling": True
            },
            # Recyclable patterns
            {
                "keywords": ["plastic", "bottle", "can", "cardboard", "paper", "glass", "jar", "container"],
                "type": "recyclable",
                "sub_type": "container",
                "hazard": "low",
                "special_handling": False
            },
            # Organic patterns
            {
                "keywords": ["food", "organic", "compost", "yard", "leaves", "fruit", "vegetable"],
                "type": "organic",
                "sub_type": "compostable", 
                "hazard": "low",
                "special_handling": False
            }
        ]
        
        # Find best match
        best_match = None
        highest_score = 0
        
        for rule in classification_rules:
            matches = sum(1 for keyword in rule["keywords"] if keyword in waste_description_lower)
            score = matches / len(rule["keywords"])
            
            if matches > 0 and score > highest_score:
                highest_score = score
                best_match = rule
        
        if best_match:
            return {
                "primary_type": best_match["type"],
                "sub_type": best_match["sub_type"],
                "confidence": min(0.6 + highest_score * 0.3, 0.9),  # Cap confidence for fallback
                "hazard_level": best_match["hazard"],
                "special_handling": best_match["special_handling"],
                "reasoning": f"Keyword-based classification (fallback mode)",
                "preparation_needed": ["Check local disposal guidelines"]
            }
        
        # Ultimate fallback
        return {
            "primary_type": "household",
            "sub_type": "general",
            "confidence": 0.3,
            "hazard_level": "low", 
            "special_handling": False,
            "reasoning": "Could not classify - defaulting to household waste",
            "preparation_needed": ["Consult local waste management for proper disposal"]
        }

    def _parse_llm_response(self, response_text: str) -> Dict:
        """
        Parse the JSON response from OpenAI, with error handling.
        """
        try:
            # Try to extract JSON from the response
            # Sometimes LLMs include extra text around the JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Validate required fields
                required_fields = ["primary_type", "confidence", "hazard_level", "special_handling"]
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Missing required field: {field}")
                
                # Validate waste type is in our enum
                if result["primary_type"] not in [wt.value for wt in WasteType]:
                    print(f"⚠️  Invalid waste type: {result['primary_type']}, defaulting to household")
                    result["primary_type"] = "household"
                
                # Validate hazard level
                if result["hazard_level"] not in [hl.value for hl in HazardLevel]:
                    print(f"⚠️  Invalid hazard level: {result['hazard_level']}, defaulting to low")
                    result["hazard_level"] = "low"
                
                return result
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"⚠️  Failed to parse LLM response: {e}")
            print(f"Raw response: {response_text}")
            
        return None

    def _run(self, waste_description: str) -> str:
        """
        Main execution method - this is what gets called when the tool is used.
        Returns a JSON string with classification results.
        """
        
        print(f"🔍 Classifying waste: '{waste_description[:50]}...'")
        
        try:
            # Create the prompt messages
            messages = self._create_classification_prompt(waste_description)
            
            # Get response from OpenAI
            response = self.llm(messages)
            response_text = response.content
            
            print(f"🤖 OpenAI response received (length: {len(response_text)})")
            
            # Parse the response
            classification_data = self._parse_llm_response(response_text)
            
            if classification_data is None:
                print("❌ OpenAI classification failed, using fallback")
                classification_data = self._fallback_classification(waste_description)
            
            # Create the structured result
            result = WasteClassificationResult(
                primary_type=WasteType(classification_data["primary_type"]),
                sub_type=classification_data.get("sub_type", "general"),
                confidence=float(classification_data["confidence"]),
                hazard_level=HazardLevel(classification_data["hazard_level"]),
                special_handling=bool(classification_data["special_handling"]),
                description=classification_data.get("reasoning", "AI classification")
            )
            
            print(f"✅ Classification complete: {result.primary_type.value} (confidence: {result.confidence:.2f})")
            
            # Return as JSON string for LangChain compatibility
            return json.dumps(result.dict())
            
        except Exception as e:
            print(f"❌ Classification error: {e}")
            
            # Use fallback classification
            fallback_data = self._fallback_classification(waste_description)
            result = WasteClassificationResult(
                primary_type=WasteType(fallback_data["primary_type"]),
                sub_type=fallback_data.get("sub_type", "general"),
                confidence=float(fallback_data["confidence"]),
                hazard_level=HazardLevel(fallback_data["hazard_level"]),
                special_handling=bool(fallback_data["special_handling"]),
                description=f"Fallback classification due to error: {str(e)}"
            )
            
            return json.dumps(result.dict())

    async def _arun(self, waste_description: str) -> str:
        """Async version of the run method"""
        return self._run(waste_description)

# Convenience function to create the tool
def create_waste_classifier() -> WasteClassificationTool:
    """Factory function to create a waste classification tool"""
    return WasteClassificationTool()

if __name__ == "__main__":
    # Quick test of the classification tool
    print("🧪 Testing Waste Classification Tool...")
    
    tool = create_waste_classifier()
    
    test_items = [
        "old laptop battery",
        "expired prescription medication", 
        "empty plastic water bottles",
        "leftover house paint",
        "food scraps from dinner"
    ]
    
    for item in test_items:
        print(f"\n📝 Testing: {item}")
        result_json = tool._run(item)
        result = json.loads(result_json)
        print(f"   Type: {result['primary_type']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Hazard: {result['hazard_level']}")
        print(f"   Special handling: {result['special_handling']}")