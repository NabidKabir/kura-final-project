# src/tools/geolocation.py - Geolocation tool for finding user location

import json
import re
import requests
from typing import Dict, Optional, Tuple
from langchain.tools import BaseTool
from pydantic import Field

# Import our configuration and models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.types import LocationModel
from config.settings import settings

class GeolocationTool(BaseTool):
    """
    This tool handles user location detection and geocoding.
    
    How it works:
    1. Takes various location inputs (address, coordinates, or auto-detect)
    2. Uses Google Maps Geocoding API when available
    3. Falls back to IP-based location or manual input
    4. Returns standardized LocationModel data
    5. Handles edge cases and provides reasonable defaults
    """
    
    name: str = "geolocation"
    description: str = (
        "Determines user location from various inputs. "
        "Input can be an address, city/state, zip code, or coordinates. "
        "Returns standardized location data with city, state, coordinates."
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"📍 Geolocation Tool initialized")

    def _geocode_with_google(self, address: str) -> Optional[Dict]:
        """
        Use Google Maps Geocoding API to get location details from address.
        This gives us the most accurate and complete location data.
        """
        
        if not settings.google_maps_api_key or settings.google_maps_api_key == "your-google-maps-api-key-here":
            print("⚠️  Google Maps API key not configured, using fallback")
            return None
        
        try:
            import googlemaps
            
            # Initialize Google Maps client
            gmaps = googlemaps.Client(key=settings.google_maps_api_key)
            
            # Geocode the address
            geocode_result = gmaps.geocode(address)
            
            if not geocode_result:
                print(f"⚠️  No results found for address: {address}")
                return None
            
            # Extract the first (best) result
            result = geocode_result[0]
            
            # Parse the components
            components = {comp['types'][0]: comp['long_name'] 
                         for comp in result['address_components']}
            
            location_data = {
                "address": result.get('formatted_address', address),
                "latitude": float(result['geometry']['location']['lat']),
                "longitude": float(result['geometry']['location']['lng']),
                "city": components.get('locality') or components.get('sublocality'),
                "state": components.get('administrative_area_level_1'),
                "zipcode": components.get('postal_code'),
                "country": components.get('country', 'US')
            }
            
            # Clean up state (convert full name to abbreviation if needed)
            if location_data.get('state'):
                location_data['state'] = self._normalize_state(location_data['state'])
            
            print(f"✅ Geocoded: {location_data.get('city')}, {location_data.get('state')}")
            return location_data
            
        except ImportError:
            print("⚠️  googlemaps package not available, install with: pip install googlemaps")
            return None
        except Exception as e:
            print(f"⚠️  Google Maps geocoding failed: {e}")
            return None

    def _normalize_state(self, state: str) -> str:
        """Convert full state names to abbreviations"""
        
        state_mapping = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
            'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
            'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
            'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
            'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
            'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
            'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
            'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
            'wisconsin': 'WI', 'wyoming': 'WY'
        }
        
        state_lower = state.lower()
        return state_mapping.get(state_lower, state.upper()[:2])

    def _parse_address_input(self, location_input: str) -> Dict:
        """
        Parse various address formats and extract components.
        Handles formats like: "New York, NY", "90210", "San Francisco", etc.
        """
        
        location_input = location_input.strip()
        
        # Check if it's just a zip code
        if re.match(r'^\d{5}(-\d{4})?$', location_input):
            return {
                "zipcode": location_input,
                "address": location_input,
                "type": "zipcode"
            }
        
        # Check if it contains coordinates (lat, lng)
        coord_match = re.search(r'(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)', location_input)
        if coord_match:
            lat, lng = float(coord_match.group(1)), float(coord_match.group(2))
            # Validate coordinates are reasonable
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return {
                    "latitude": lat,
                    "longitude": lng,
                    "address": location_input,
                    "type": "coordinates"
                }
        
        # Parse city, state format
        if ',' in location_input:
            parts = [part.strip() for part in location_input.split(',')]
            if len(parts) == 2:
                city, state = parts
                return {
                    "city": city,
                    "state": self._normalize_state(state),
                    "address": location_input,
                    "type": "city_state"
                }
        
        # Assume it's a general address or city name
        return {
            "address": location_input,
            "type": "general"
        }

    def _get_ip_location(self) -> Dict:
        """
        Get approximate location based on IP address.
        This is a fallback when no address is provided.
        """
        
        try:
            # Using a free IP geolocation service
            response = requests.get('http://ipapi.co/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                location_data = {
                    "city": data.get('city'),
                    "state": self._normalize_state(data.get('region', '')),
                    "zipcode": data.get('postal'),
                    "latitude": float(data.get('latitude', 0)) if data.get('latitude') else None,
                    "longitude": float(data.get('longitude', 0)) if data.get('longitude') else None,
                    "country": data.get('country_code', 'US'),
                    "address": f"{data.get('city', '')}, {data.get('region', '')}".strip(', ')
                }
                
                print(f"✅ IP-based location: {location_data.get('city')}, {location_data.get('state')}")
                return location_data
                
        except Exception as e:
            print(f"⚠️  IP geolocation failed: {e}")
        
        # Ultimate fallback - assume NYC (could be configured per deployment)
        return {
            "city": "New York",
            "state": "NY", 
            "zipcode": "10001",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "country": "US",
            "address": "New York, NY"
        }

    def _validate_and_complete_location(self, location_data: Dict) -> Dict:
        """
        Validate location data and fill in missing fields when possible.
        """
        
        # Ensure we have at least city and state for waste regulations
        if not location_data.get('city') or not location_data.get('state'):
            
            # If we have coordinates, try reverse geocoding
            if location_data.get('latitude') and location_data.get('longitude'):
                lat, lng = location_data['latitude'], location_data['longitude']
                
                # Try Google Maps reverse geocoding
                reverse_geocode = self._reverse_geocode(lat, lng)
                if reverse_geocode:
                    location_data.update(reverse_geocode)
            
            # If we have zipcode, try to infer state
            elif location_data.get('zipcode'):
                state = self._zipcode_to_state(location_data['zipcode'])
                if state:
                    location_data['state'] = state
        
        # Ensure required fields have values
        if not location_data.get('city'):
            location_data['city'] = "Unknown City"
        if not location_data.get('state'):
            location_data['state'] = "NY"  # Default fallback
        if not location_data.get('country'):
            location_data['country'] = "US"
        
        return location_data

    def _reverse_geocode(self, lat: float, lng: float) -> Optional[Dict]:
        """Reverse geocode coordinates to get address components"""
        
        if not settings.google_maps_api_key or settings.google_maps_api_key == "your-google-maps-api-key-here":
            return None
        
        try:
            import googlemaps
            gmaps = googlemaps.Client(key=settings.google_maps_api_key)
            
            results = gmaps.reverse_geocode((lat, lng))
            if results:
                result = results[0]
                components = {comp['types'][0]: comp['long_name'] 
                             for comp in result['address_components']}
                
                return {
                    "city": components.get('locality') or components.get('sublocality'),
                    "state": self._normalize_state(components.get('administrative_area_level_1', '')),
                    "zipcode": components.get('postal_code'),
                    "address": result.get('formatted_address')
                }
        except Exception as e:
            print(f"⚠️  Reverse geocoding failed: {e}")
        
        return None

    def _zipcode_to_state(self, zipcode: str) -> Optional[str]:
        """
        Map ZIP codes to states using first 3 digits.
        This is a simplified mapping for common ZIP code ranges.
        """
        
        if not zipcode or len(zipcode) < 5:
            return None
        
        zip_prefix = int(zipcode[:3])
        
        # Simplified ZIP code to state mapping
        zip_to_state = {
            (100, 199): 'MA', (200, 299): 'DC', (300, 399): 'GA',
            (400, 499): 'KY', (500, 599): 'IA', (600, 699): 'IL',
            (700, 799): 'LA', (800, 999): 'CO', (100, 149): 'NY',
            (150, 196): 'PA', (970, 999): 'TX', (900, 969): 'CA',
            (980, 999): 'WA', (590, 599): 'MT', (10, 59): 'MA',
            (60, 99): 'CT', (70, 89): 'NJ', (100, 149): 'NY',
            (150, 196): 'PA', (197, 199): 'DE'
        }
        
        for (start, end), state in zip_to_state.items():
            if start <= zip_prefix <= end:
                return state
        
        return None

    def _run(self, location_input: str = "") -> str:
        """
        Main execution method for location detection.
        Returns JSON string with location data.
        """
        
        print(f"📍 Processing location: '{location_input}'")
        
        try:
            # Handle empty input (auto-detect location)
            if not location_input.strip():
                print("🌐 No location provided, attempting IP-based detection...")
                location_data = self._get_ip_location()
            else:
                # Parse the input to understand what type of location data we have
                parsed_input = self._parse_address_input(location_input)
                
                # If it's coordinates, we already have what we need
                if parsed_input.get('type') == 'coordinates':
                    location_data = parsed_input.copy()
                
                # If it's an address, try to geocode it
                elif parsed_input.get('address'):
                    google_result = self._geocode_with_google(parsed_input['address'])
                    
                    if google_result:
                        location_data = google_result
                    else:
                        # Use parsed input as fallback
                        location_data = parsed_input.copy()
                        
                        # Try to enhance with IP location if missing data
                        if not location_data.get('city') or not location_data.get('state'):
                            ip_data = self._get_ip_location()
                            for key in ['city', 'state', 'latitude', 'longitude']:
                                if not location_data.get(key) and ip_data.get(key):
                                    location_data[key] = ip_data[key]
                
                else:
                    # Fallback to IP location
                    location_data = self._get_ip_location()
            
            # Validate and complete the location data
            location_data = self._validate_and_complete_location(location_data)
            
            # Create a LocationModel for validation
            location_model = LocationModel(
                address=location_data.get('address'),
                city=location_data.get('city'),
                state=location_data.get('state'),
                zipcode=location_data.get('zipcode'),
                latitude=location_data.get('latitude'),
                longitude=location_data.get('longitude'),
                country=location_data.get('country', 'US')
            )
            
            print(f"✅ Location resolved: {location_model.city}, {location_model.state}")
            
            # Return as JSON string for LangChain compatibility
            return json.dumps(location_model.dict())
            
        except Exception as e:
            print(f"❌ Geolocation error: {e}")
            
            # Ultimate fallback
            fallback_location = LocationModel(
                address="New York, NY",
                city="New York",
                state="NY",
                zipcode="10001",
                latitude=40.7128,
                longitude=-74.0060,
                country="US"
            )
            
            return json.dumps(fallback_location.dict())

    async def _arun(self, location_input: str = "") -> str:
        """Async version of the run method"""
        return self._run(location_input)

# Convenience function to create the tool
def create_geolocation_tool() -> GeolocationTool:
    """Factory function to create a geolocation tool"""
    return GeolocationTool()

if __name__ == "__main__":
    # Quick test of the geolocation tool
    print("🧪 Testing Geolocation Tool...")
    
    tool = create_geolocation_tool()
    
    test_inputs = [
        "",  # Auto-detect
        "New York, NY",
        "90210", 
        "San Francisco",
        "40.7128, -74.0060",
        "123 Main Street, Boston, MA"
    ]
    
    for location_input in test_inputs:
        print(f"\n📝 Testing: '{location_input}' (empty means auto-detect)")
        result_json = tool._run(location_input)
        result = json.loads(result_json)
        print(f"   Result: {result['city']}, {result['state']} ({result.get('zipcode', 'no zip')})")
        if result.get('latitude'):
            print(f"   Coordinates: {result['latitude']:.4f}, {result['longitude']:.4f}")