from langchain_core.tools import tool       
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv

load_dotenv()

#Conect to MCP server

mcp_client = MultiServerMCPClient(
    servers=["http://127.0.0.1:8000"])
   
#client tools
@tool
def geolocate_ip(ip: str = None) -> dict: 
    """Find user's location based on their IP address by calling on the MCP server."""
    print("Worker Tool: Caling the geolocate_ip on the MCP server")
    #will invoke the tool on the server
    return mcp_client.invoke_tool("geolocate_ip", ip=ip)

@tool
def get_places (query: str, lat: float, lng: float) -> dict:
    """Find nearby places such as recycling centers by calling on the MCP server."""
    print(f"Worker Tool: Calling on get_places for '{query}' on MCP server")
    #will invoke the tool on the server
    return mcp_client.invoke(
        "Locate Places Locator",
        query=query,
        lat=lat,
        lng=lng
    )
    
    #knowledge base is local to the worker
    from tools.knowledge_base import search_knowledge_base
    @tool 
    
    def lookup_city_regulations(city: str, topic: str) -> str:
        """Looks up specific regulations that can be found in the worker agents internal knowledge base.
        print(f" Worker Tool: Looking up regulations about '{topic}' in '{city}'")"""
        return search_knowledge_base(city=city, topic=topic)