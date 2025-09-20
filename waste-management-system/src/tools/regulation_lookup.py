# src/tools/regulation_lookup.py - Local waste disposal regulation lookup

import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from pydantic import Field

# Import our configuration and models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.types import RegulationInfo, WasteType, LocationModel
from config.settings import settings

class RegulationLookupTool(BaseTool):
    """
    This tool looks up local waste disposal regulations based on location and waste type.
    
    How it works:
    1. Takes location data and waste type as input
    2. Searches through regulation database (mock for now, real DB later)
    3. Finds most specific regulation (city > county > state > general)
    4. Returns structured regulation information with rules, steps, restrictions
    5. Provides fallback general guidance when specific regulations aren't available
    """
    
    name: str = "regulation_lookup"
    description: str = (
        "Looks up local waste disposal regulations based on location and waste type. "
        "Input should be location data (dict) and waste type (string). "
        "Returns local regulations, preparation steps, and disposal requirements."
    )
    regulation_db: Dict = Field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"⚖️  Regulation Lookup Tool initialized")
        # Initialize the regulation database
        object.__setattr__(self, 'regulation_db', self._initialize_regulation_database())

    def _initialize_regulation_database(self) -> Dict:
        """
        Initialize a comprehensive mock regulation database.
        In production, this would connect to a real database with current regulations.
        """
        
        # Mock regulation database organized by state -> waste_type -> regulations
        regulation_db = {
            # New York State regulations
            "NY": {
                "e-waste": {
                    "jurisdiction": "New York State",
                    "rules": "Electronic waste is banned from landfills. Must be recycled at certified facilities. Retailers selling electronics must accept old devices for recycling.",
                    "preparation_steps": [
                        "Remove all personal data from devices",
                        "Remove batteries if possible",
                        "Keep original packaging if available",
                        "Do not attempt to disassemble devices"
                    ],
                    "restrictions": [
                        "Cannot be placed in regular trash",
                        "Cannot be placed in recycling bins",
                        "Businesses must use certified haulers"
                    ],
                    "penalties": "Fines up to $350 for improper disposal",
                    "disposal_methods": ["Certified e-waste recyclers", "Retail take-back programs", "Municipal collection events"],
                    "source_url": "https://www.dec.ny.gov/chemical/66872.html",
                    "last_updated": "2024-01-15"
                },
                "medical": {
                    "jurisdiction": "New York State",
                    "rules": "Medical waste requires special handling. Sharps must be in puncture-proof containers. Medications can be returned to pharmacies or police stations.",
                    "preparation_steps": [
                        "Place sharps in FDA-approved containers",
                        "Do not mix different types of medical waste",
                        "Remove personal information from prescription labels",
                        "Never flush medications down drains"
                    ],
                    "restrictions": [
                        "Sharps cannot go in regular trash",
                        "Controlled substances have special requirements",
                        "Home healthcare generators have different rules than facilities"
                    ],
                    "penalties": "Violations can result in fines up to $37,500",
                    "disposal_methods": ["Hospital disposal programs", "Pharmacy take-back", "Police take-back events", "Mail-back programs"],
                    "source_url": "https://www.health.ny.gov/environmental/waste/medical/",
                    "last_updated": "2024-02-01"
                },
                "hazardous": {
                    "jurisdiction": "New York State", 
                    "rules": "Hazardous household waste requires special collection. Paint, chemicals, and batteries must go to designated facilities. Never pour down drains or put in regular trash.",
                    "preparation_steps": [
                        "Keep materials in original containers",
                        "Don't mix different chemicals",
                        "Ensure containers are sealed and labeled",
                        "Transport safely - no loose materials"
                    ],
                    "restrictions": [
                        "Cannot be placed in regular trash",
                        "Cannot be poured down drains or sewers",
                        "Cannot be burned or buried",
                        "Quantity limits may apply at collection sites"
                    ],
                    "penalties": "Improper disposal can result in cleanup costs and fines",
                    "disposal_methods": ["Household hazardous waste facilities", "Special collection events", "Paint recycling programs"],
                    "source_url": "https://www.dec.ny.gov/chemical/8485.html", 
                    "last_updated": "2024-01-20"
                },
                "recyclable": {
                    "jurisdiction": "New York State",
                    "rules": "Recyclables must be clean and separated. NYC has different rules than rest of state. Check local guidelines for accepted materials.",
                    "preparation_steps": [
                        "Clean containers of food residue", 
                        "Remove caps and lids if required",
                        "Separate materials by type",
                        "Check local accepted materials list"
                    ],
                    "restrictions": [
                        "No contaminated materials",
                        "No plastic bags in curbside recycling",
                        "Some materials require special programs"
                    ],
                    "penalties": "Contamination can result in collection refusal",
                    "disposal_methods": ["Curbside recycling", "Drop-off centers", "Bottle deposits"],
                    "source_url": "https://www.dec.ny.gov/chemical/8792.html",
                    "last_updated": "2024-01-10"
                },
                "organic": {
                    "jurisdiction": "New York State",
                    "rules": "Food scraps and yard waste can be composted. NYC requires food scrap separation for large buildings. Check if your area has collection programs.",
                    "preparation_steps": [
                        "Separate food scraps from other waste",
                        "No meat, dairy, or oils in some programs", 
                        "Use compostable bags if required",
                        "Keep yard waste separate from food waste"
                    ],
                    "restrictions": [
                        "No pet waste in compost",
                        "No diseased plants",
                        "Some programs exclude certain food types"
                    ],
                    "penalties": "Large generators may face fines for non-compliance",
                    "disposal_methods": ["Curbside organics collection", "Drop-off composting", "Home composting"],
                    "source_url": "https://www.dec.ny.gov/chemical/8792.html",
                    "last_updated": "2024-01-05"
                }
            },
            
            # California regulations (different rules!)
            "CA": {
                "e-waste": {
                    "jurisdiction": "California State",
                    "rules": "E-waste recycling fee paid at purchase. Free recycling at certified centers. Covered Electronic Waste program covers TVs, monitors, computers, printers.",
                    "preparation_steps": [
                        "No preparation required for most items",
                        "Remove personal data",
                        "Bring proof of California residency for free recycling"
                    ],
                    "restrictions": [
                        "Banned from landfills since 2004",
                        "CRT devices require special handling"
                    ],
                    "penalties": "Illegal dumping fines up to $6,000",
                    "disposal_methods": ["Certified collection sites", "Retail programs", "Manufacturer take-back"],
                    "source_url": "https://www.calrecycle.ca.gov/Electronics",
                    "last_updated": "2024-01-12"
                },
                "hazardous": {
                    "jurisdiction": "California State",
                    "rules": "Universal Waste Rule covers batteries, fluorescent lamps, electronics. Household hazardous waste programs available statewide.",
                    "preparation_steps": [
                        "Separate different waste types",
                        "Keep in original containers when possible",
                        "No mixing of chemicals"
                    ],
                    "restrictions": [
                        "Strict landfill bans",
                        "Enhanced penalties for violations"
                    ],
                    "penalties": "Fines can exceed $25,000 for improper disposal",
                    "disposal_methods": ["HHW facilities", "Curbside programs", "Special events"],
                    "source_url": "https://www.calrecycle.ca.gov/reducewaste/household",
                    "last_updated": "2024-01-18"
                }
            },
            
            # Texas regulations
            "TX": {
                "e-waste": {
                    "jurisdiction": "Texas State",
                    "rules": "Computer Take-Back Program requires manufacturers to provide recycling. No state e-waste disposal fee. Check local programs.",
                    "preparation_steps": [
                        "Remove personal data",
                        "Check manufacturer take-back programs first"
                    ],
                    "restrictions": [
                        "Some local landfill bans apply",
                        "CRT monitors have special requirements"
                    ],
                    "penalties": "Varies by local jurisdiction",
                    "disposal_methods": ["Manufacturer programs", "Local collection events", "Private recyclers"],
                    "source_url": "https://www.tceq.texas.gov/waste/recycle_reuse/electronics",
                    "last_updated": "2024-01-08"
                }
            },
            
            # General federal/default regulations
            "DEFAULT": {
                "e-waste": {
                    "jurisdiction": "Federal/General Guidelines",
                    "rules": "Electronic waste should be recycled through certified programs. Remove personal data before disposal. Check EPA guidelines and local regulations.",
                    "preparation_steps": [
                        "Back up and delete personal data",
                        "Remove batteries if possible",
                        "Find certified recyclers in your area"
                    ],
                    "restrictions": [
                        "Avoid landfill disposal when possible",
                        "Don't disassemble devices yourself"
                    ],
                    "penalties": "Varies by local jurisdiction",
                    "disposal_methods": ["EPA certified recyclers", "Retail programs", "Manufacturer take-back"],
                    "source_url": "https://www.epa.gov/recycle/electronics-donation-and-recycling",
                    "last_updated": "2024-01-01"
                },
                "medical": {
                    "jurisdiction": "Federal/General Guidelines", 
                    "rules": "Follow DEA and FDA guidelines. Use approved sharps containers. Dispose of medications through take-back programs.",
                    "preparation_steps": [
                        "Use FDA-approved sharps containers",
                        "Remove personal info from prescriptions",
                        "Don't flush most medications"
                    ],
                    "restrictions": [
                        "Sharps require special containers",
                        "Controlled substances need DEA-authorized disposal"
                    ],
                    "penalties": "Federal violations can result in significant fines",
                    "disposal_methods": ["DEA take-back events", "Pharmacy programs", "Mail-back programs"],
                    "source_url": "https://www.fda.gov/drugs/disposal-unused-medicines-what-you-should-know",
                    "last_updated": "2024-01-01"
                },
                "hazardous": {
                    "jurisdiction": "Federal/General Guidelines",
                    "rules": "Follow EPA guidelines for household hazardous waste. Never pour down drains or put in regular trash. Use local collection programs.",
                    "preparation_steps": [
                        "Keep in original containers",
                        "Don't mix chemicals",
                        "Transport safely to collection sites"
                    ],
                    "restrictions": [
                        "Cannot go in regular trash in most areas",
                        "Cannot be poured down drains",
                        "Cannot be burned"
                    ],
                    "penalties": "EPA violations can result in substantial fines",
                    "disposal_methods": ["Local HHW facilities", "Collection events", "Retail programs"],
                    "source_url": "https://www.epa.gov/hw/household-hazardous-waste-hhw",
                    "last_updated": "2024-01-01"
                },
                "recyclable": {
                    "jurisdiction": "Federal/General Guidelines",
                    "rules": "Follow local recycling guidelines. Clean containers before recycling. Check what materials are accepted locally.",
                    "preparation_steps": [
                        "Clean food containers",
                        "Check local accepted materials", 
                        "Separate materials as required"
                    ],
                    "restrictions": [
                        "No contaminated materials",
                        "Follow local sorting requirements"
                    ],
                    "penalties": "Varies by local program",
                    "disposal_methods": ["Curbside recycling", "Drop-off centers", "Deposit programs"],
                    "source_url": "https://www.epa.gov/recycle",
                    "last_updated": "2024-01-01"
                },
                "organic": {
                    "jurisdiction": "Federal/General Guidelines",
                    "rules": "Composting reduces methane emissions. Separate organic waste when programs available. Consider home composting.",
                    "preparation_steps": [
                        "Separate food scraps from other waste",
                        "Check local program requirements",
                        "Consider home composting options"
                    ],
                    "restrictions": [
                        "No pet waste in most programs",
                        "Some programs exclude meat/dairy"
                    ],
                    "penalties": "Generally none for households",
                    "disposal_methods": ["Local composting programs", "Home composting", "Drop-off sites"],
                    "source_url": "https://www.epa.gov/recycle/composting-home",
                    "last_updated": "2024-01-01"
                },
                "household": {
                    "jurisdiction": "Federal/General Guidelines",
                    "rules": "Regular household waste goes to landfills or waste-to-energy facilities. Minimize waste through reduction and recycling.",
                    "preparation_steps": [
                        "Bag waste securely",
                        "Follow local collection schedule",
                        "Separate recyclables and organics first"
                    ],
                    "restrictions": [
                        "No hazardous materials",
                        "No large items without special pickup"
                    ],
                    "penalties": "Varies by local waste management rules",
                    "disposal_methods": ["Curbside collection", "Transfer stations", "Drop-off sites"],
                    "source_url": "https://www.epa.gov/recycle/reducing-and-reusing-basics",
                    "last_updated": "2024-01-01"
                }
            }
        }
        
        print(f"📚 Regulation database initialized with {len(regulation_db)} jurisdictions")
        return regulation_db

    def _find_best_regulation(self, location_data: Dict, waste_type: str) -> Optional[Dict]:
        """
        Find the most specific regulation available for the location and waste type.
        Priority: City > County > State > Default
        """
        
        state = location_data.get('state', '').upper()
        city = location_data.get('city', '').lower()
        waste_type_key = waste_type.lower()
        
        print(f"🔍 Looking for regulations: {waste_type} in {city}, {state}")
        
        # Try to find state-specific regulation first
        if state and state in self.regulation_db:
            state_regulations = self.regulation_db[state]
            
            # Look for exact waste type match
            if waste_type_key in state_regulations:
                regulation = state_regulations[waste_type_key].copy()
                print(f"✅ Found state regulation: {state} - {waste_type}")
                return regulation
            
            # Try alternate waste type names
            waste_type_alternates = {
                'e_waste': ['e-waste', 'electronic', 'electronics'],
                'recyclable': ['recycling', 'recycle'],
                'hazardous': ['household_hazardous', 'hhw'],
                'medical': ['pharmaceutical', 'sharps']
            }
            
            for alt_type in waste_type_alternates.get(waste_type_key, []):
                if alt_type in state_regulations:
                    regulation = state_regulations[alt_type].copy()
                    print(f"✅ Found state regulation (alternate): {state} - {alt_type}")
                    return regulation
        
        # Fall back to default federal regulations
        if 'DEFAULT' in self.regulation_db:
            default_regulations = self.regulation_db['DEFAULT']
            if waste_type_key in default_regulations:
                regulation = default_regulations[waste_type_key].copy()
                regulation['jurisdiction'] = f"Federal Guidelines (State: {state})"
                print(f"✅ Using default regulation for {waste_type}")
                return regulation
        
        print(f"⚠️  No specific regulation found for {waste_type} in {state}")
        return None

    def _create_fallback_regulation(self, waste_type: str, location_data: Dict) -> Dict:
        """
        Create a basic fallback regulation when no specific rules are found.
        """
        
        state = location_data.get('state', 'your area')
        
        # Basic guidance based on waste type
        basic_guidance = {
            'e-waste': {
                'rules': 'Electronic waste should be recycled at certified facilities. Do not put in regular trash.',
                'preparation_steps': ['Remove personal data', 'Find local e-waste recycler'],
                'disposal_methods': ['Electronics retailers', 'Recycling centers', 'Manufacturer programs']
            },
            'medical': {
                'rules': 'Medical waste requires special handling. Use approved disposal methods.',
                'preparation_steps': ['Use sharps containers for needles', 'Take medications to pharmacy'],
                'disposal_methods': ['Pharmacy take-back', 'Hospital programs', 'Mail-back services']
            },
            'hazardous': {
                'rules': 'Hazardous materials cannot go in regular trash. Take to special collection facilities.',
                'preparation_steps': ['Keep in original containers', 'Do not mix chemicals'],
                'disposal_methods': ['Hazardous waste facilities', 'Special collection events']
            },
            'recyclable': {
                'rules': 'Clean recyclables and follow local sorting guidelines.',
                'preparation_steps': ['Clean containers', 'Check local accepted materials'],
                'disposal_methods': ['Curbside recycling', 'Recycling centers']
            },
            'organic': {
                'rules': 'Food scraps can be composted where programs exist.',
                'preparation_steps': ['Separate food waste', 'Check for local composting programs'],
                'disposal_methods': ['Composting programs', 'Home composting']
            }
        }
        
        guidance = basic_guidance.get(waste_type, {
            'rules': 'Follow local waste disposal guidelines and environmental regulations.',
            'preparation_steps': ['Check local disposal requirements'],
            'disposal_methods': ['Local waste management services']
        })
        
        return {
            'jurisdiction': f'General Guidelines ({state})',
            'rules': guidance['rules'],
            'preparation_steps': guidance['preparation_steps'],
            'restrictions': ['Follow local environmental regulations'],
            'penalties': 'Varies by local jurisdiction',
            'disposal_methods': guidance['disposal_methods'],
            'source_url': 'https://www.epa.gov/recycle',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'note': 'General guidance - check with local authorities for specific regulations'
        }

    def _format_regulation_response(self, regulation_data: Dict, waste_type: str, location_data: Dict) -> str:
        """
        Format regulation data into a structured JSON response.
        """
        
        # Create RegulationInfo object for validation
        try:
            regulation_info = RegulationInfo(
                jurisdiction=regulation_data['jurisdiction'],
                waste_type=WasteType(waste_type.lower()),
                rules=regulation_data['rules'],
                preparation_steps=regulation_data.get('preparation_steps', []),
                restrictions=regulation_data.get('restrictions', []),
                penalties=regulation_data.get('penalties'),
                last_updated=datetime.strptime(regulation_data['last_updated'], '%Y-%m-%d'),
                source_url=regulation_data.get('source_url')
            )
            
            # Convert to dict and add extra fields
            result = regulation_info.model_dump()
            result['disposal_methods'] = regulation_data.get('disposal_methods', [])
            result['note'] = regulation_data.get('note')
            
            # Add location context
            result['applicable_location'] = {
                'city': location_data.get('city'),
                'state': location_data.get('state'),
                'jurisdiction_level': 'state' if regulation_data['jurisdiction'] != 'Federal/General Guidelines' else 'federal'
            }
            
            return json.dumps(result, default=str)  # default=str handles datetime serialization
            
        except Exception as e:
            print(f"⚠️  Error formatting regulation: {e}")
            # Return basic dict if RegulationInfo validation fails
            return json.dumps(regulation_data, default=str)

    def _run(self, query: str) -> str:
        """
        Main execution method for regulation lookup.
        Expected input: JSON string with 'location' and 'waste_type' keys
        Returns: JSON string with regulation information
        """
        
        try:
            # Parse the query input
            if isinstance(query, str):
                try:
                    query_data = json.loads(query)
                except json.JSONDecodeError:
                    # Handle simple string input like "e-waste in NY"
                    parts = query.split(' in ')
                    if len(parts) == 2:
                        waste_type, location_str = parts[0].strip(), parts[1].strip()
                        query_data = {
                            'waste_type': waste_type,
                            'location': {'state': location_str.upper(), 'city': 'Unknown'}
                        }
                    else:
                        raise ValueError("Invalid query format. Expected JSON or 'waste_type in location' format")
            else:
                query_data = query
            
            location_data = query_data.get('location', {})
            waste_type = query_data.get('waste_type', 'household')
            
            print(f"⚖️  Looking up regulations for {waste_type} in {location_data.get('city', 'Unknown')}, {location_data.get('state', 'Unknown')}")
            
            # Find the best available regulation
            regulation = self._find_best_regulation(location_data, waste_type)
            
            if not regulation:
                print(f"📝 No specific regulation found, creating fallback guidance")
                regulation = self._create_fallback_regulation(waste_type, location_data)
            
            # Format and return the response
            response = self._format_regulation_response(regulation, waste_type, location_data)
            
            print(f"✅ Regulation lookup complete for {regulation['jurisdiction']}")
            return response
            
        except Exception as e:
            print(f"❌ Regulation lookup error: {e}")
            
            # Emergency fallback
            fallback = {
                'jurisdiction': 'General Guidelines',
                'rules': 'Please check with local waste management authorities for proper disposal methods.',
                'preparation_steps': ['Contact local waste management services'],
                'disposal_methods': ['Local waste management facilities'],
                'error': f'Lookup failed: {str(e)}'
            }
            
            return json.dumps(fallback)

    async def _arun(self, query: str) -> str:
        """Async version of the run method"""
        return self._run(query)

# Convenience function to create the tool
def create_regulation_lookup_tool() -> RegulationLookupTool:
    """Factory function to create a regulation lookup tool"""
    return RegulationLookupTool()

if __name__ == "__main__":
    # Quick test of the regulation lookup tool
    print("🧪 Testing Regulation Lookup Tool...")
    
    tool = create_regulation_lookup_tool()
    
    test_queries = [
        {
            'location': {'city': 'New York', 'state': 'NY'},
            'waste_type': 'e-waste'
        },
        {
            'location': {'city': 'Los Angeles', 'state': 'CA'}, 
            'waste_type': 'hazardous'
        },
        {
            'location': {'city': 'Austin', 'state': 'TX'},
            'waste_type': 'medical'
        },
        {
            'location': {'city': 'Miami', 'state': 'FL'},
            'waste_type': 'recyclable'  # FL not in DB, should use fallback
        }
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query['waste_type']} in {query['location']['city']}, {query['location']['state']}")
        result_json = tool._run(json.dumps(query))
        result = json.loads(result_json)
        print(f"   Jurisdiction: {result.get('jurisdiction')}")
        print(f"   Rules: {result.get('rules', '')[:100]}...")
        print(f"   Preparation steps: {len(result.get('preparation_steps', []))} steps")