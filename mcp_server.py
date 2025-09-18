import os
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

test_mcp = FastMCP("Google Places")


GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

@test_mcp.tool(title="Places Locater")
def get_places(query: str, latitude: float, longitude: float) -> dict:
    """Function that leverages the Google Places API to find locations near the latidute and longitude given.

    Args:
        query: The type of location you are searching for (in example "Recycling center")
        latitude: The current latitude of the user
        longitude: The current longitude of the user

    Returns:
        Dictionary with location details, results and metadata
    """
    #the google api url
    url = 'https://places.googleapis.com/v1/places:searchText'
    #headers used for the request
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': GOOGLE_API_KEY,
        'X-Goog-FieldMask': '*'
    }
    #the request body used for the api request
    request_body = {
        "textQuery": query,
        "locationBias": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": 100.0
            }
        }
    }
    #get the response
    response = requests.post(url, headers=headers, json=request_body)
    #get the json object
    output = response.json()
    #save the locations in a dictionary
    locations = []
    #loop through the output
    for row in output['places']:
        locations.append({
            "name": row["displayName"]["text"],
            "address": row["formattedAddress"]
        })
    return {
        "query": query,
        "latitude_used": latitude,
        "longitude_used": longitude,
        "results": locations
    }