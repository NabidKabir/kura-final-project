
#Libraries import goes here; Pydantic is for data structures, googlemaps connects to the API, connects to my knowledge base via tools.knowledge_base
import os 
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import googlemaps
from tools.knowledge_base import search_knowledge_base

#looks for .env file
load_dotenv()
#gmaps = Google Maps as the variable name
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
app = FastAPI(title="MCP Tool Server")

#requesting info from the APIs

#Pydantic models; these are the data structures that define the input and output of the endpoints
class RegulationRequest(BaseModel):
    city: str
    topic: str  
    
class PlacesRequest(BaseModel):
   location: str
   radius: int = 5000 #meters were suggested
   keyword: str = "recycling center"
   
#Endpoints ; app.post is the decorator; accepts POST requests   
@app.post("/tools/lookup_regulations") #this is a URL endpoint; used to help answer questions. @ is the decorator. This right here is what helps the endpoint provide access to our static knowledge base
def lookup_regulations_endpoint(request: RegulationRequest):
    # Before I was writing city:, topic:, result:; but I think maybe passing it into the function directly might be a better strategy.
    #this validates incoming JSON data against the RegulationRequest model. 
    print(f"MCP Server has received a request for regulation about '{request.topic}' in '{request.city}'")
    #execites search funciton using the city and topic 
    result = search_knowledge_base(city=request.city, topic= request.topic)
    return {"result": result}

@app.post("/tools/find_nearby_places")
def find_nearby_places_endpoint(request: PlacesRequest):
    #this is going to be where we we use the Google Places API
    print(f"MCP Server has received a request to find the nearby recycling centers. Received request to find '{request.keyword}' within {request.radius} meters of '{request.location}'")
    
    #error handling here
    try: 
        #we need the coordinates for the location 
        geocode_result = gmaps.geocode(request.location)
        if not geocode_result:
            return {"error": "The location could not be found."}
        #lat for latutude, lng for longitude
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        
        #find nearby places
        places_result = gmaps.places_nearby(
            location=(lat, lng), 
            radius=request.radius, 
            keyword=request.keyword
        )
        #This is *supposed* to format the request 
        if not places_result.get('results'):
            return {"result": f"No {request.keyword} found near this {request.location}."}
        
        formatted_results = []
        for place in places_result['results'][:5]: #we want the top 5 results I guess
            formatted_results.append(
                f" Name: {place['name']}, Address: {place['vicinity']}"
            )
        return {"result": "\n".join(formatted_results)}
    
    except Exception as e:
        return {"result": f"An unexpected error has occurred within the Google Places API: {e}"}
    
    
               