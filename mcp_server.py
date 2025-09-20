from fastmcp import FastMCP
import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

recycle_mcp = FastMCP("Recycling_Server")

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

@mcp.tool(title="Places Locater")
def get_places(query: str, latitude: float, longitude: float) -> dict:
    """Function that leverages the Google Places API to find locations near the latitude and longitude given."

        Args:
            query: The type of location you are searching for (example: "Recycling Center")
            latitude: The current location of the user in terms of a nort-south position point on Earth
            longitude: The current location of the user in terms of a east-west position point on Earth

        Returns:
            Dictionary with 3 location details, results, and metadata
    """ 
    #Google API Url
    url = 'https://places.googleapis.com/v1/places:searchText'

    #headers for request
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': GOOGLE_API_KEY,
        'X-Goog-FieldMask': '*'
    }

    #request body

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

    #get response
    response = requests.post(url, headers=headers, json=request_body)
    #get JSON object
    output = response.json()
    #save the locations in a dictionary
    locations = []

    for row in output['places']:
        loactions.append({
            "name": row["displayName"]["text"],
            "address": row["formattedAddress"],
            "phone_number": row["nationalPhoneNumber"]
        })

    return {
        "query": query,
        "latitude_used": latitude,
        "longitude_used": longitude,
        "results": locations
    }
