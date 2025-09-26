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
from langchain_tavily import TavilySearch
import httpx
import asyncio

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

@recycle_mcp.tool(title="Knowledge Base Retrieval")
async def regulation_retrieval(query: str) -> dict:
    """Function that retrieves relevant information from the knowledge base. 

        Args:
            query: string that contains the user query to run a similarity search against knowledge base

        Returns:
            dictionary with the query as well as any results in a list
    """
    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(
        None, lambda: vector_store.similarity_search(query, k=3)
    )
    return {"query": query, "results": [doc.page_content for doc in results]}


tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)

@recycle_mcp.tool(title="Tavily Search Retreival")
async def web_search(query: str) -> dict:
    """Function that retrieves relevant information from the web ONLY if not found in knowledge base

        Args:
            query: string that contains the user query to run a web search

        Returns
            results: results of the web search in the form of a dict
    """

    search_result = await tavily_search.invoke(query)

    return search_result


@recycle_mcp.tool(title="Geolocator")
async def geolocate_ip() -> dict:
    """Function that locates the users location by latitude and longitude by their IP address.
        Returns:
            Dictionary with latitude and longitude of IP address OR error message
    """

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
    recycle_mcp.run(transport="http", host="localhost", port=8000)