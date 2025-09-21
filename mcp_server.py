from fastmcp import FastMCP, Resource
import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

recycle_mcp = FastMCP("Recycling_Server")

@recycle_mcp.resource()
def regulation_knowledge_base() -> Resource:
    """Recycling and waste management regulation knowledge base"""

    with open("knowledge_base/knowledge_base.txt", "r", encoding="utf-8") as f:
        text = f.read()

    return Resource(
        uri="kb://regulation-knowledge-base",
        name="Waste Regulation Knowledge Base",
        mimeType="text/plain",
        description="Guidelines and facts about regulations regarding recycling and waste classification.",
        contents=text,
    )


@recycle_mcp.tool(title="Geolocator")
def geolocate_ip(ip: str = None) -> dict:
    """Function that locates the users location by latitude and longitude by their IP address.

        Args:
            ip (optional): IP address to check. If none, uses caller's IP.

        Returns:
            Dictionary with latitude and longitude of IP address OR error message
    """

    url = f"http://ip-api.com/json/{ip or ''}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        geo_data = response.json()

        if geo_data.get("status") != "success":
            raise ValueError(f"Geolocation Lookup Failed {geo_data}")
        else:
            return {"latitude": geo_data["lat"], "longitude": geo_data["lon"]}
    except Exception as e:
        return {"error": str(e)}

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

@recycle_mcp.tool(title="Places Locater")
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
        locations.append({
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

if __name__ == "__main__":
    recycle_mcp.start(host="localhost", port=8000)