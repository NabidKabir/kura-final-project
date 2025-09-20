# src/tools/location_finder.py - Find nearby waste disposal facilities using Google Maps

import json
import math
from typing import Dict, List, Optional, Tuple
from langchain.tools import BaseTool
from pydantic import Field

# Import our configuration and models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.types import DisposalLocation, WasteType, LocationModel
from config.settings import settings

class LocationFinderTool(BaseTool):
    """
    This tool finds nearby waste disposal facilities using Google Maps Places API.
    
    How it works:
    1. Takes user location and waste type as input
    2. Determines appropriate search queries for that waste type
    3. Uses Google Places API to find relevant facilities
    4. Calculates distances and gets facility details
    5. Returns sorted list of nearby disposal locations
    6. Falls back to mock data when API unavailable
    """
    
    name: str = "location_finder"
    description: str = (
        "Finds nearby waste disposal facilities based on location and waste type. "
        "Input should be location data (dict) and waste type (string). "
        "Returns list of facilities with addresses, hours, and contact info."
    )
    gmaps_client: Optional[object] = Field(default=None)
    search_queries: Dict = Field(default_factory=dict)
    mock_facilities: Dict = Field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"🗺️  Location Finder Tool initialized")

        # Initialize Google Maps client if API key is available
        object.__setattr__(self, 'gmaps_client', self._initialize_google_maps())

        # Search query mappings for different waste types
        object.__setattr__(self, 'search_queries', self._initialize_search_queries())

        # Mock facility database for fallback
        object.__setattr__(self, 'mock_facilities', self._initialize_mock_facilities())

    def _initialize_google_maps(self):
        """Initialize Google Maps client if API key is configured"""
        
        if not settings.google_maps_api_key or settings.google_maps_api_key == "your-google-maps-api-key-here":
            print("⚠️  Google Maps API key not configured - using mock facility data")
            return None
        
        try:
            import googlemaps
            client = googlemaps.Client(key=settings.google_maps_api_key)
            print("✅ Google Maps client initialized")
            return client
        except ImportError:
            print("⚠️  googlemaps package not available - install with: pip install googlemaps")
            return None
        except Exception as e:
            print(f"⚠️  Google Maps initialization failed: {e}")
            return None

    def _initialize_search_queries(self) -> Dict[str, List[str]]:
        """
        Initialize search queries for different waste types.
        These are the terms we'll use to search Google Places API.
        """
        
        return {
            'e-waste': [
                'electronics recycling center',
                'e-waste disposal facility', 
                'computer recycling',
                'battery recycling center',
                'Best Buy recycling',
                'Staples electronics recycling',
                'electronic waste drop off'
            ],
            'medical': [
                'pharmacy drug disposal',
                'hospital waste disposal',
                'medical waste facility',
                'sharps disposal program',
                'CVS drug take back',
                'Walgreens medication disposal',
                'police drug take back'
            ],
            'hazardous': [
                'hazardous waste facility',
                'household hazardous waste',
                'paint disposal center',
                'chemical waste facility',
                'HHW collection site',
                'toxic waste disposal',
                'automotive fluid recycling'
            ],
            'recyclable': [
                'recycling center',
                'bottle return center',
                'aluminum can recycling',
                'cardboard recycling',
                'glass recycling facility',
                'plastic recycling center',
                'paper recycling drop off'
            ],
            'organic': [
                'composting facility',
                'yard waste drop off',
                'food scrap collection',
                'municipal composting',
                'organic waste facility',
                'green waste recycling',
                'compost drop off site'
            ],
            'household': [
                'transfer station',
                'waste management facility',
                'dump',
                'landfill',
                'garbage disposal facility',
                'solid waste facility',
                'municipal waste center'
            ]
        }

    def _initialize_mock_facilities(self) -> Dict[str, List[Dict]]:
        """
        Initialize mock facility database for fallback when Google Maps isn't available.
        Organized by major cities for realistic testing.
        """
        
        return {
            'new york': [
                {
                    'name': 'Best Buy Electronics Recycling',
                    'address': '622 Broadway, New York, NY 10012',
                    'phone': '(212) 614-1000',
                    'website': 'https://www.bestbuy.com/site/services/recycling/pcmcat149900050025.c',
                    'accepted_waste_types': ['e-waste'],
                    'hours': ['Mon-Sat: 10AM-9PM', 'Sun: 11AM-8PM'],
                    'special_instructions': 'Free recycling for most electronics. Limit 3 items per day.',
                    'latitude': 40.7259,
                    'longitude': -73.9986,
                    'distance_km': 2.1,
                    'rating': 4.2
                },
                {
                    'name': 'NYC Department of Sanitation Special Waste Drop-Off',
                    'address': '1550 2nd Ave, New York, NY 10075', 
                    'phone': '(311) 692-9647',
                    'website': 'https://www1.nyc.gov/site/dsny/resources/recycling-and-garbage-laws.page',
                    'accepted_waste_types': ['hazardous', 'e-waste'],
                    'hours': ['Sat-Sun: 10AM-5PM'],
                    'special_instructions': 'NYC residents only. Bring ID. No business waste.',
                    'latitude': 40.7736,
                    'longitude': -73.9566,
                    'distance_km': 1.8,
                    'rating': 3.8
                },
                {
                    'name': 'CVS Pharmacy - Drug Take Back',
                    'address': '1619 Broadway, New York, NY 10019',
                    'phone': '(212) 247-8384',
                    'website': 'https://www.cvs.com/content/prescription-drug-abuse/disposal',
                    'accepted_waste_types': ['medical'],
                    'hours': ['Mon-Fri: 8AM-10PM', 'Sat-Sun: 9AM-9PM'],
                    'special_instructions': 'Medication disposal kiosk available 24/7. No controlled substances.',
                    'latitude': 40.7614,
                    'longitude': -73.9776,
                    'distance_km': 1.2,
                    'rating': 4.0
                },
                {
                    'name': 'Big Apple Recycling',
                    'address': '2132 Atlantic Ave, Brooklyn, NY 11233',
                    'phone': '(718) 922-8026',
                    'website': None,
                    'accepted_waste_types': ['recyclable'],
                    'hours': ['Mon-Fri: 7AM-5PM', 'Sat: 8AM-4PM'],
                    'special_instructions': 'Cash paid for aluminum cans and glass bottles.',
                    'latitude': 40.6782,
                    'longitude': -73.9442,
                    'distance_km': 8.7,
                    'rating': 4.1
                }
            ],
            'los angeles': [
                {
                    'name': 'UCLA Hazardous Waste Facility',
                    'address': '595 Charles E. Young Dr E, Los Angeles, CA 90095',
                    'phone': '(310) 825-5662',
                    'website': 'https://www.ehs.ucla.edu/hazwaste-management',
                    'accepted_waste_types': ['hazardous', 'e-waste'],
                    'hours': ['Mon-Fri: 7AM-3:30PM'],
                    'special_instructions': 'UCLA community members only. Call ahead.',
                    'latitude': 34.0689,
                    'longitude': -118.4452,
                    'distance_km': 3.2,
                    'rating': 4.3
                },
                {
                    'name': 'Staples Electronics Recycling',
                    'address': '11041 Santa Monica Blvd, Los Angeles, CA 90025',
                    'phone': '(310) 231-9979',
                    'website': 'https://www.staples.com/sbd/cre/marketing/sustainability-center/recycling-services/',
                    'accepted_waste_types': ['e-waste'],
                    'hours': ['Mon-Fri: 8AM-9PM', 'Sat: 9AM-9PM', 'Sun: 10AM-7PM'],
                    'special_instructions': 'Free recycling for small electronics. Fees for monitors.',
                    'latitude': 34.0399,
                    'longitude': -118.4617,
                    'distance_km': 4.1,
                    'rating': 3.9
                },
                {
                    'name': 'City of LA SAFE Centers',
                    'address': '8840 National Blvd, Culver City, CA 90232',
                    'phone': '(800) 988-6942',
                    'website': 'https://www.lacitysan.org/cs/groups/sg_sla/documents/document/y250/mdi0/~edisp/cnt026550.pdf',
                    'accepted_waste_types': ['hazardous', 'e-waste', 'medical'],
                    'hours': ['Fri-Sat: 9AM-3PM', 'Sun: 9AM-3PM'],
                    'special_instructions': 'LA residents only. Free disposal. Proof of residency required.',
                    'latitude': 34.0261,
                    'longitude': -118.3957,
                    'distance_km': 2.8,
                    'rating': 4.5
                }
            ],
            'chicago': [
                {
                    'name': 'Best Buy Recycling Center',
                    'address': '1000 W North Ave, Chicago, IL 60642',
                    'phone': '(312) 846-5200',
                    'website': 'https://www.bestbuy.com/site/services/recycling/pcmcat149900050025.c',
                    'accepted_waste_types': ['e-waste'],
                    'hours': ['Mon-Sat: 10AM-10PM', 'Sun: 11AM-8PM'],
                    'special_instructions': 'Free recycling. $30 fee for tube TVs and monitors.',
                    'latitude': 41.9102,
                    'longitude': -87.6503,
                    'distance_km': 2.9,
                    'rating': 4.0
                },
                {
                    'name': 'Chicago Household Chemical and Computer Recycling',
                    'address': '1150 N North Branch St, Chicago, IL 60642',
                    'phone': '(312) 744-7685',
                    'website': 'https://www.chicago.gov/city/en/depts/streets/supp_info/recycling1/household_chemicalandcomputerrecyclingfacility.html',
                    'accepted_waste_types': ['hazardous', 'e-waste'],
                    'hours': ['Tue-Sat: 8AM-4PM'],
                    'special_instructions': 'Chicago residents only. Free disposal. Call ahead for large items.',
                    'latitude': 41.9023,
                    'longitude': -87.6431,
                    'distance_km': 1.7,
                    'rating': 4.2
                }
            ]
        }

    def _get_search_location_key(self, location_data: Dict) -> str:
        """Get the appropriate key for mock facility lookup"""
        
        city = location_data.get('city', '').lower()
        state = location_data.get('state', '').upper()
        
        # Map cities to our mock data keys
        city_mappings = {
            'new york': 'new york',
            'manhattan': 'new york',
            'brooklyn': 'new york',
            'queens': 'new york',
            'bronx': 'new york',
            'los angeles': 'los angeles',
            'la': 'los angeles',
            'hollywood': 'los angeles',
            'santa monica': 'los angeles',
            'chicago': 'chicago',
            'windy city': 'chicago'
        }
        
        return city_mappings.get(city, 'new york')  # Default to NYC

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        Returns distance in kilometers.
        """
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r

    def _search_google_places(self, location_data: Dict, waste_type: str, radius_km: int = 25) -> List[Dict]:
        """
        Search Google Places API for disposal facilities.
        """
        
        if not self.gmaps_client:
            print("⚠️  Google Maps not available, using mock data")
            return []
        
        user_lat = float(location_data.get('latitude', 40.7128))
        user_lng = float(location_data.get('longitude', -74.0060))
        
        search_queries = self.search_queries.get(waste_type, ['waste disposal facility'])
        all_facilities = []
        
        try:
            for query in search_queries[:3]:  # Limit to first 3 queries to avoid API limits
                print(f"🔍 Searching: '{query}' near {location_data.get('city', 'location')}")
                
                # Search for places
                places_result = self.gmaps_client.places_nearby(
                    location=(user_lat, user_lng),
                    radius=radius_km * 1000,  # Convert to meters
                    keyword=query,
                    type='establishment'
                )
                
                for place in places_result.get('results', [])[:5]:  # Limit to 5 per query
                    try:
                        # Get detailed place information
                        place_details = self.gmaps_client.place(
                            place_id=place['place_id'],
                            fields=['name', 'formatted_address', 'formatted_phone_number', 
                                   'opening_hours', 'website', 'rating', 'geometry', 'types']
                        )['result']
                        
                        # Calculate distance
                        place_lat = place_details['geometry']['location']['lat']
                        place_lng = place_details['geometry']['location']['lng']
                        distance = self._calculate_distance(user_lat, user_lng, place_lat, place_lng)
                        
                        # Create facility info
                        facility = {
                            'name': place_details.get('name', 'Unknown Facility'),
                            'address': place_details.get('formatted_address', 'Address not available'),
                            'phone': place_details.get('formatted_phone_number'),
                            'website': place_details.get('website'),
                            'accepted_waste_types': [waste_type],  # Would need verification in real system
                            'hours': place_details.get('opening_hours', {}).get('weekday_text', []),
                            'special_instructions': f'Call ahead to confirm {waste_type} acceptance',
                            'latitude': place_lat,
                            'longitude': place_lng,
                            'distance_km': round(distance, 1),
                            'rating': place_details.get('rating'),
                            'place_id': place['place_id'],
                            'types': place_details.get('types', [])
                        }
                        
                        all_facilities.append(facility)
                        
                    except Exception as e:
                        print(f"⚠️  Error processing place: {e}")
                        continue
            
            print(f"✅ Found {len(all_facilities)} facilities via Google Maps")
            return all_facilities
            
        except Exception as e:
            print(f"⚠️  Google Places search failed: {e}")
            return []

    def _get_mock_facilities(self, location_data: Dict, waste_type: str, radius_km: int = 25) -> List[Dict]:
        """
        Get mock facilities for testing when Google Maps isn't available.
        """
        
        location_key = self._get_search_location_key(location_data)
        all_facilities = self.mock_facilities.get(location_key, [])
        
        print(f"📍 Using mock facilities for {location_key} ({len(all_facilities)} available)")
        
        # Filter by waste type
        matching_facilities = []
        for facility in all_facilities:
            if waste_type in facility.get('accepted_waste_types', []):
                matching_facilities.append(facility.copy())
        
        # If no exact matches, be more flexible
        if not matching_facilities and waste_type != 'household':
            print(f"⚠️  No exact matches for {waste_type}, looking for general facilities")
            for facility in all_facilities:
                # Add facilities that might accept the waste type
                facility_copy = facility.copy()
                facility_copy['special_instructions'] = f'Call ahead to confirm {waste_type} acceptance. ' + facility_copy.get('special_instructions', '')
                matching_facilities.append(facility_copy)
        
        # Update distances based on user location if coordinates provided
        if location_data.get('latitude') and location_data.get('longitude'):
            user_lat = float(location_data['latitude'])
            user_lng = float(location_data['longitude'])
            
            for facility in matching_facilities:
                if facility.get('latitude') and facility.get('longitude'):
                    distance = self._calculate_distance(
                        user_lat, user_lng,
                        facility['latitude'], facility['longitude']
                    )
                    facility['distance_km'] = round(distance, 1)
        
        print(f"✅ Found {len(matching_facilities)} matching mock facilities")
        return matching_facilities

    def _format_facility_response(self, facilities: List[Dict], location_data: Dict, waste_type: str) -> str:
        """
        Format the facility list into a structured JSON response.
        """
        
        # Remove duplicates based on name and address
        unique_facilities = {}
        for facility in facilities:
            key = (facility.get('name', ''), facility.get('address', ''))
            if key not in unique_facilities or facility.get('distance_km', 999) < unique_facilities[key].get('distance_km', 999):
                unique_facilities[key] = facility
        
        # Sort by distance
        sorted_facilities = sorted(
            unique_facilities.values(),
            key=lambda x: x.get('distance_km', 999)
        )
        
        # Create DisposalLocation objects for validation
        disposal_locations = []
        for facility_data in sorted_facilities[:10]:  # Limit to top 10
            try:
                # Map waste type string to WasteType enum
                waste_types = []
                for wt in facility_data.get('accepted_waste_types', []):
                    try:
                        waste_types.append(WasteType(wt.replace('-', '_')))
                    except ValueError:
                        # Skip invalid waste types
                        continue
                
                location = DisposalLocation(
                    name=facility_data.get('name', 'Unknown Facility'),
                    address=facility_data.get('address', 'Address not available'),
                    phone=facility_data.get('phone'),
                    website=facility_data.get('website'),
                    distance_km=facility_data.get('distance_km'),
                    accepted_waste_types=waste_types,
                    hours=facility_data.get('hours', []),
                    special_instructions=facility_data.get('special_instructions'),
                    rating=facility_data.get('rating')
                )
                
                disposal_locations.append(location)
                
            except Exception as e:
                print(f"⚠️  Error creating DisposalLocation: {e}")
                continue
        
        # Create response
        response = {
            'query_location': {
                'city': location_data.get('city'),
                'state': location_data.get('state'),
                'coordinates': f"{location_data.get('latitude', 'N/A')}, {location_data.get('longitude', 'N/A')}"
            },
            'waste_type': waste_type,
            'search_radius_km': 25,
            'facilities_found': len(disposal_locations),
            'facilities': [loc.dict() for loc in disposal_locations],
            'search_method': 'google_maps' if self.gmaps_client else 'mock_database'
        }
        
        return json.dumps(response, default=str)

    def _run(self, query: str) -> str:
        """
        Main execution method for location finding.
        Expected input: JSON string with 'location' and 'waste_type' keys
        Returns: JSON string with nearby facilities
        """
        
        try:
            # Parse the query input
            if isinstance(query, str):
                try:
                    query_data = json.loads(query)
                except json.JSONDecodeError:
                    # Handle simple string input like "e-waste near NYC"
                    if ' near ' in query:
                        parts = query.split(' near ')
                        waste_type, location_str = parts[0].strip(), parts[1].strip()
                        query_data = {
                            'waste_type': waste_type,
                            'location': {'city': location_str, 'state': 'NY'}  # Default state
                        }
                    else:
                        raise ValueError("Invalid query format. Expected JSON or 'waste_type near location' format")
            else:
                query_data = query
            
            location_data = query_data.get('location', {})
            waste_type = query_data.get('waste_type', 'household')
            radius_km = query_data.get('radius_km', 25)
            
            print(f"🗺️  Finding facilities for {waste_type} near {location_data.get('city', 'Unknown')}, {location_data.get('state', 'Unknown')}")
            
            # Try Google Maps first, fall back to mock data
            facilities = []
            
            if self.gmaps_client and location_data.get('latitude') and location_data.get('longitude'):
                facilities = self._search_google_places(location_data, waste_type, radius_km)
            
            if not facilities:
                facilities = self._get_mock_facilities(location_data, waste_type, radius_km)
            
            # Format and return the response
            response = self._format_facility_response(facilities, location_data, waste_type)
            
            print(f"✅ Location search complete: {len(facilities)} facilities found")
            return response
            
        except Exception as e:
            print(f"❌ Location finder error: {e}")
            
            # Emergency fallback
            fallback_response = {
                'query_location': {'city': 'Unknown', 'state': 'Unknown'},
                'waste_type': 'unknown',
                'facilities_found': 0,
                'facilities': [],
                'error': f'Search failed: {str(e)}',
                'suggestion': 'Please contact local waste management services for disposal options'
            }
            
            return json.dumps(fallback_response)

    async def _arun(self, query: str) -> str:
        """Async version of the run method"""
        return self._run(query)

# Convenience function to create the tool
def create_location_finder_tool() -> LocationFinderTool:
    """Factory function to create a location finder tool"""
    return LocationFinderTool()

if __name__ == "__main__":
    # Quick test of the location finder tool
    print("🧪 Testing Location Finder Tool...")
    
    tool = create_location_finder_tool()
    
    test_queries = [
        {
            'location': {'city': 'New York', 'state': 'NY', 'latitude': 40.7128, 'longitude': -74.0060},
            'waste_type': 'e-waste'
        },
        {
            'location': {'city': 'Los Angeles', 'state': 'CA', 'latitude': 34.0522, 'longitude': -118.2437},
            'waste_type': 'hazardous'
        },
        {
            'location': {'city': 'Chicago', 'state': 'IL'},  # No coordinates - will use mock
            'waste_type': 'medical'
        }
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query['waste_type']} near {query['location']['city']}, {query['location']['state']}")
        result_json = tool._run(json.dumps(query))
        result = json.loads(result_json)
        print(f"   Facilities found: {result.get('facilities_found', 0)}")
        print(f"   Search method: {result.get('search_method', 'unknown')}")
        
        for j, facility in enumerate(result.get('facilities', [])[:2], 1):  # Show first 2
            print(f"   {j}. {facility.get('name')} - {facility.get('distance_km')}km")