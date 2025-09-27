from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
from typing import Dict, Any
import httpx
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
# Simplified approach without complex MCP client connections

load_dotenv()

# Create FastAPI app for web interface
web_app = FastAPI(title="DAINE Recycling Assistant", description="Web interface for recycling guidance")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")

# MCP Server URL (internal Docker network)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Removed complex agent builders - using simplified approach with direct tool calls

class RecyclingAssistant:
    """Web interface for the recycling assistant with multi-agent architecture"""

    def __init__(self):
        self.conversation_history = []
        self.supervisor = None
        self.is_initialized = False

    async def query_mcp_server(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Query the MCP server tools"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{MCP_SERVER_URL}/{endpoint}", json=data)
                return response.json()
        except Exception as e:
            return {"error": f"Failed to connect to MCP server: {str(e)}"}

    async def search_knowledge_base(self, query: str) -> Dict[str, Any]:
        """Search the recycling knowledge base"""
        return await self.query_mcp_server("knowledge-search", {"query": query})

    async def find_locations(self, query: str, latitude: float = None, longitude: float = None) -> Dict[str, Any]:
        """Find recycling locations"""
        if latitude is None or longitude is None:
            # Get user location first
            location_data = await self.query_mcp_server("geolocate", {})
            if "error" not in location_data:
                latitude = location_data.get("latitude")
                longitude = location_data.get("longitude")

        return await self.query_mcp_server("places-search", {
            "query": query,
            "latitude": latitude,
            "longitude": longitude
        })

    async def web_search(self, query: str) -> Dict[str, Any]:
        """Search the web for recycling information"""
        return await self.query_mcp_server("web-search", {"query": query})

    async def initialize_supervisor(self):
        """Initialize the supervisor agent with research and locator agents"""
        if self.is_initialized:
            return

        print("Initializing supervisor agent...")
        try:
            # Create a simplified supervisor that orchestrates responses using our existing tools
            self.supervisor = openai_client
            self.is_initialized = True
            print("✅ Supervisor agent initialized successfully!")
        except Exception as e:
            print(f"❌ Failed to initialize supervisor: {str(e)}")
            self.supervisor = None

    async def get_comprehensive_response(self, user_query: str) -> str:
        """Get a comprehensive response using multi-agent architecture"""

        print(f"Starting agent-based response for: {user_query}")

        # Initialize supervisor if not already done
        if not self.is_initialized:
            await self.initialize_supervisor()

        # If supervisor initialization failed, fall back to old method
        if self.supervisor is None:
            print("Supervisor not available, falling back to direct tool approach")
            return await self.fallback_response(user_query)

        try:
            # Use supervisor to orchestrate the response by analyzing the query
            print("Invoking supervisor agent...")

            # Get relevant information using our working tools
            kb_results = await self.search_knowledge_base(user_query)
            location_results = await self.find_locations(f"recycling {user_query}")
            web_results = await self.web_search(user_query)

            # Create a comprehensive prompt for the supervisor
            supervisor_prompt = f"""
            You are a recycling assistant supervisor. The user asked: "{user_query}"

            Available information:

            Knowledge Base Results:
            {kb_results}

            Location Results:
            {location_results}

            Web Search Results:
            {web_results}

            Instructions:
            - Provide a comprehensive, well-structured response
            - Include relevant regulations, guidelines, and disposal methods
            - Provide specific location information when applicable
            - Mention potential fines for improper disposal
            - Make the response actionable and helpful
            - Format the response clearly with headers and bullet points
            - Do NOT use asterisks, bold formatting, or markdown emphasis
            - Use plain text formatting only
            """

            response = await self.supervisor.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": supervisor_prompt}],
                temperature=0.7,
                max_tokens=1500
            )

            agent_response = response.choices[0].message.content
            print(f"Agent response length: {len(agent_response) if agent_response else 0}")
            return agent_response

        except Exception as e:
            print(f"Error with supervisor agent: {str(e)}")
            return await self.fallback_response(user_query)

    async def fallback_response(self, user_query: str) -> str:
        """Fallback response method using direct tool calls"""
        print("Using fallback response method")

        # Simple fallback - just use knowledge base
        try:
            kb_response = await self.search_knowledge_base(user_query)
            if kb_response.get("results"):
                response_text = f"Based on recycling guidelines:\n\n"
                for i, result in enumerate(kb_response["results"][:3], 1):
                    response_text += f"{i}. {result}\n\n"
                return response_text
            else:
                return "I apologize, but I'm having trouble accessing detailed information right now. Please try asking a more specific question about recycling."
        except Exception as e:
            return "I apologize, but I'm having trouble accessing detailed information right now. Please try asking a more specific question about recycling."


# Initialize assistant
assistant = RecyclingAssistant()

@web_app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@web_app.get("/sw.js")
async def service_worker():
    """Serve the service worker file"""
    from fastapi.responses import FileResponse
    return FileResponse("templates/sw.js", media_type="application/javascript")

@web_app.get("/favicon.ico")
async def favicon():
    """Serve a simple favicon"""
    from fastapi.responses import Response
    # Simple 1x1 transparent PNG
    favicon_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    return Response(content=favicon_data, media_type="image/png")

@web_app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, message: str = Form(...)):
    """Handle chat messages"""

    # Add user message to history
    assistant.conversation_history.append({"role": "user", "content": message})

    # Get comprehensive response using AI consolidation
    try:
        print(f"Processing query: {message}")
        comprehensive_response = await assistant.get_comprehensive_response(message)
        print(f"Generated response length: {len(comprehensive_response) if comprehensive_response else 0}")

        if comprehensive_response and len(comprehensive_response.strip()) > 0:
            response_data = {
                "type": "comprehensive",
                "message": comprehensive_response
            }
        else:
            print("Empty response from AI, falling back to original processing")
            response_data = await process_user_query(message)

    except Exception as e:
        print(f"Error in AI consolidation: {str(e)}")
        # Fallback to original processing if AI consolidation fails
        response_data = await process_user_query(message)

    # Add assistant response to history
    assistant.conversation_history.append({"role": "assistant", "content": response_data})

    return templates.TemplateResponse("index.html", {
        "request": request,
        "conversation": assistant.conversation_history,
        "latest_response": response_data
    })

@web_app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Search page for specific queries"""
    return templates.TemplateResponse("search.html", {"request": request})

@web_app.post("/api/knowledge-search")
async def api_knowledge_search(query: str = Form(...)):
    """API endpoint for knowledge base search"""
    result = await assistant.search_knowledge_base(query)
    return result

@web_app.post("/api/location-search")
async def api_location_search(query: str = Form(...)):
    """API endpoint for location search"""
    result = await assistant.find_locations(query)
    return result

@web_app.post("/api/web-search")
async def api_web_search(query: str = Form(...)):
    """API endpoint for web search"""
    result = await assistant.web_search(query)
    return result

async def process_user_query(message: str) -> Dict[str, Any]:
    """Process user query and determine appropriate response"""

    message_lower = message.lower()

    # Check if user is asking for locations
    if any(word in message_lower for word in ["where", "find", "location", "near me", "center"]):
        result = await assistant.find_locations(f"recycling {message}")
        return {
            "type": "location",
            "message": "Here are recycling locations I found:",
            "data": result
        }

    # Check if user is asking about regulations/rules
    elif any(word in message_lower for word in ["rule", "regulation", "law", "fine", "legal"]):
        result = await assistant.search_knowledge_base(message)
        if not result.get("results") or len(result.get("results", [])) == 0:
            # Fallback to web search
            result = await assistant.web_search(message)
            return {
                "type": "web_search",
                "message": "Here's what I found from recent sources:",
                "data": result
            }
        return {
            "type": "knowledge",
            "message": "Based on recycling regulations:",
            "data": result
        }

    # Default: search knowledge base first, fallback to web
    else:
        result = await assistant.search_knowledge_base(message)
        if result.get("results") and len(result.get("results", [])) > 0:
            return {
                "type": "knowledge",
                "message": "Here's what I found in the knowledge base:",
                "data": result
            }
        else:
            # Fallback to web search
            result = await assistant.web_search(message)
            return {
                "type": "web_search",
                "message": "Here's what I found from recent sources:",
                "data": result
            }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(web_app, host="0.0.0.0", port=3000)