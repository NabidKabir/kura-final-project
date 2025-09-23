from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv


load_dotenv()

#assumes that the localhost is running on 8000 and sets up the MCP server
mcp_client = MultiServerMCPClient(
    ["http://127.0.0.1:8000"]
)

#List the tools here and use @tool before each tool; the tool names are found in mcp_server branch for the functions used here
@tool
def get_knowledge_base_chunks() -> list[str]:
    """
    This will call the entire regulations knowledge base
    """
    print("~~ Worker agent's tool is calling 'Get_Knowledge_Base' on/from the MCP server ~~")
    # .invoke is used to get the tool on the remote server by using it's title
    return mcp_client.invoke("Get_Knowledge_Base") #this is the exposure name from mcp_server branch

@tool
def geolocate_ip(ip: str = None) -> dict: 
    """
    Finds the user's location by their IP address by calling the MCP server.
    """
    print("~~ Worker Tool: Calling 'Geolocator' on MCP Server ~~")
    # This invokes the tool on the remote server using its title/exposure name from mcp_server branch
    return mcp_client.invoke("Geolocator", ip=ip)

@tool
def get_places(query: str, latitude: float, longitude: float) -> dict:
    """
    Finds nearby places (like recycling centers) by calling the MCP server.
    """
    print(f"~~ Worker Tool: Calling 'Google Places Locater' for '{query}' on MCP Server ~~")
    # This invokes the tool on the remote server using its title/exposure name from mcp_server branch
    return mcp_client.invoke(
        "Google Places Locater",
        query=query,
        latitude=latitude,
        longitude=longitude
        )
    
    #this tool is the web search fallback so that my agent can stop saying it knows nothing about what the user is talking about.
@tool
def google_search(query: str) -> str:
    """
    A secondary web search tool to find general information.
    Use this if the 'get_knowledge_base_chunks' tool returns an empty list or an error. Having no answer for the user is unacceptable. That's what gets you fired. 
  
    """
    print(f"--- RAG Fallback: Searching the web for '{query}' ---")
    # This calls your web search tool
    search_results = google_search.search(queries=[query])
    # We'll return a formatted string of the top 3 results
    return "\n".join([f"- {res.snippet}" for res in search_results[0].results[:3]])