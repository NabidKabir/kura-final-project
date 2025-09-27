from fastmcp import FastMCP
import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
# from langchain_tavily import TavilySearchAPIWrapper
import httpx
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

if not TAVILY_API_KEY or not GOOGLE_API_KEY:
    raise ValueError(
        "Missing required environment variables: TAVILY_API_KEY or GOOGLE_API KEY"
    )

recycle_mcp = FastMCP("Recycling_Server")

document = TextLoader(file_path="./knowledge_base/knowledge_base.txt").load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=50
)
chunks = text_splitter.split_documents(document)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = Chroma(
    collection_name="knowledge-base",
    embedding_function=embeddings
)

vector_store.add_documents(documents=chunks)

# Core functions that can be called directly
async def knowledge_search_function(query: str) -> dict:
    """Function that retrieves relevant information from the knowledge base."""
    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(
        None, lambda: vector_store.similarity_search(query, k=3)
    )
    return {"query": query, "results": [doc.page_content for doc in results]}

@recycle_mcp.tool(title="Knowledge Base Retrieval")
async def regulation_retrieval(query: str) -> dict:
    """Function that retrieves relevant information from the knowledge base.

        Args:
            query: string that contains the user query to run a similarity search against knowledge base

        Returns:
            dictionary with the query as well as any results in a list
    """
    return await knowledge_search_function(query)


# Temporarily disable Tavily integration - focus on Chroma first
# web_search = TavilySearchAPIWrapper(tavily_api_key=TAVILY_API_KEY, max_results=3)

async def web_search_function(query: str) -> dict:
    """Function that retrieves relevant information from the web ONLY if not found in knowledge base"""
    # Temporarily return simple response while we fix Tavily integration
    return {"query": query, "results": ["Web search temporarily disabled - use knowledge base retrieval instead"]}

@recycle_mcp.tool(title="Tavily Search Retreival")
async def web_search_tool(query: str) -> dict:
    """Function that retrieves relevant information from the web ONLY if not found in knowledge base

        Args:
            query: string that contains the user query to run a web search

        Returns
            results: results of the web search in the form of a dict
    """
    return await web_search_function(query)


async def geolocate_function() -> dict:
    """Function that locates the users location by latitude and longitude by their IP address."""
    url = f"http://ip-api.com/json/"

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(url)
            response.raise_for_status()
            geo_data = response.json()

        if geo_data.get("status") != "success":
            raise ValueError(f"Geolocation Lookup Failed {geo_data}")
        return {"latitude": geo_data["lat"],
                "longitude": geo_data["lon"]}

    except Exception as e:
        return {"error": str(e)}

@recycle_mcp.tool(title="Geolocator")
async def geolocate_ip() -> dict:
    """Function that locates the users location by latitude and longitude by their IP address.
        Returns:
            Dictionary with latitude and longitude of IP address OR error message
    """
    return await geolocate_function()

async def places_search_function(query: str, latitude: float, longitude: float) -> dict:
    """Function that leverages the Google Places API to find locations near the latitude and longitude given."""
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

    try:
        #get response
        response = requests.post(url, headers=headers, json=request_body)
        #get JSON object
        output = response.json()

        if 'places' not in output:
            return {"query": query, "results": [], "error": "No places found"}

        #save the locations in a dictionary
        locations = []

        for row in output['places']:
            locations.append({
                "name": row["displayName"]["text"],
                "address": row["formattedAddress"],
                "phone_number": row.get("nationalPhoneNumber", "Not available")
            })

        return {
            "query": query,
            "latitude_used": latitude,
            "longitude_used": longitude,
            "results": locations
        }
    except Exception as e:
        return {"query": query, "error": str(e)}

@recycle_mcp.tool(title="Google Places Locater")
async def get_places(query: str, latitude: float, longitude: float) -> dict:
    """Function that leverages the Google Places API to find locations near the latitude and longitude given."

        Args:
            query: The type of location you are searching for (example: "Recycling Center")
            latitude: The current location of the user in terms of a nort-south position point on Earth
            longitude: The current location of the user in terms of a east-west position point on Earth

        Returns:
            Dictionary with 3 location details, results, and metadata
    """
    return await places_search_function(query, latitude, longitude)
# Create FastAPI app for HTTP endpoints
app = FastAPI(title="KURA MCP Server", description="HTTP endpoints for recycling tools")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class QueryRequest(BaseModel):
    query: str

class LocationRequest(BaseModel):
    query: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# HTTP endpoints that call the core functions
@app.post("/knowledge-search")
async def knowledge_search_endpoint(request: QueryRequest):
    """HTTP endpoint for knowledge base search"""
    return await knowledge_search_function(request.query)

@app.post("/web-search")
async def web_search_endpoint(request: QueryRequest):
    """HTTP endpoint for web search"""
    return await web_search_function(request.query)

@app.post("/geolocate")
async def geolocate_endpoint():
    """HTTP endpoint for geolocation"""
    return await geolocate_function()

@app.post("/places-search")
async def places_search_endpoint(request: LocationRequest):
    """HTTP endpoint for places search"""
    if request.latitude is None or request.longitude is None:
        # Get location first
        location_data = await geolocate_function()
        if "error" in location_data:
            return location_data
        request.latitude = location_data["latitude"]
        request.longitude = location_data["longitude"]

    return await places_search_function(request.query, request.latitude, request.longitude)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "KURA MCP Server", "status": "running"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# Add WebSocket endpoint for MCP
from fastapi import WebSocket
import json

@app.websocket("/mcp")
async def mcp_websocket(websocket: WebSocket):
    """WebSocket endpoint for MCP connections"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Handle MCP protocol messages here
            # For now, echo back a simple response
            response = {"jsonrpc": "2.0", "id": 1, "result": {"status": "ok"}}
            await websocket.send_text(json.dumps(response))
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)