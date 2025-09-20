# src/agents/waste_management_workflow.py - Complete multi-agent waste management system

import json
import asyncio
from typing import Dict, List, Optional, Literal
from datetime import datetime

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# Import our tools and models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.types import WasteManagementState, WasteClassificationResult, LocationModel, RegulationInfo, DisposalLocation
from tools.waste_classifier import create_waste_classifier
from tools.geolocation import create_geolocation_tool
from tools.regulation_lookup import create_regulation_lookup_tool
from tools.location_finder import create_location_finder_tool
from config.settings import settings

class SupervisorAgent:
    """
    The Supervisor Agent orchestrates the entire workflow.
    
    How it works:
    1. Analyzes the current state and user query
    2. Determines what information is missing
    3. Decides which tool should be called next
    4. Routes the workflow to the appropriate agent/tool
    5. Generates final response when all information is collected
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.1,  # Low temperature for consistent routing decisions
            openai_api_key=settings.openai_api_key
        )
        print("🧠 Supervisor Agent initialized")
    
    def plan_next_action(self, state: WasteManagementState) -> str:
        """
        Analyze current state and determine the next action needed.
        Returns the name of the next node to execute.
        """
        
        print(f"🎯 Supervisor analyzing state...")
        print(f"   User query: {state.get('user_query', 'None')[:50]}...")
        print(f"   Has waste type: {'Yes' if state.get('waste_type') else 'No'}")
        print(f"   Has location: {'Yes' if state.get('user_location') else 'No'}")
        print(f"   Has regulations: {'Yes' if state.get('local_regulations') else 'No'}")
        print(f"   Has facilities: {'Yes' if state.get('disposal_locations') else 'No'}")
        
        # Decision tree for workflow routing
        if not state.get('waste_type'):
            print("   → Need waste classification")
            return "classify_waste"
        
        elif not state.get('user_location'):
            print("   → Need user location")
            return "get_location"
        
        elif not state.get('local_regulations'):
            print("   → Need local regulations")
            return "lookup_regulations"
        
        elif not state.get('disposal_locations'):
            print("   → Need disposal locations")
            return "find_locations"
        
        else:
            print("   → All data collected, generating response")
            return "generate_response"
    
    def generate_final_response(self, state: WasteManagementState) -> str:
        """
        Generate a comprehensive final response using all collected information.
        Uses LLM to create a natural, helpful response.
        """
        
        print("📝 Generating final response...")
        
        # Prepare context for LLM
        waste_type = state.get('waste_type', 'unknown')
        location_data = state.get('user_location', {})
        regulations = state.get('local_regulations', {})
        locations = state.get('disposal_locations', [])
        
        city = location_data.get('city', 'your area')
        state_name = location_data.get('state', 'your state')
        
        # Create context summary
        context = f"""
User Query: {state.get('user_query', 'Waste disposal question')}

ANALYSIS RESULTS:
- Waste Type: {waste_type}
- Location: {city}, {state_name}
- Regulations Available: {'Yes' if regulations else 'No'}
- Facilities Found: {len(locations)} locations

REGULATION SUMMARY:
{regulations.get('rules', 'No specific regulations found') if regulations else 'No regulations available'}

DISPOSAL FACILITIES:
"""
        
        if locations:
            for i, location in enumerate(locations[:3], 1):  # Top 3 facilities
                context += f"{i}. {location.get('name', 'Unknown')} - {location.get('address', 'No address')} ({location.get('distance_km', 'Unknown')}km)\n"
        else:
            context += "No specific facilities found in database.\n"
        
        # LLM prompt for response generation
        system_message = SystemMessage(content="""
You are a helpful waste management assistant. Based on the analysis provided, create a comprehensive, actionable response for the user.

Your response should:
1. Start with a clear answer about their waste type
2. Provide specific local disposal requirements
3. List nearby disposal options with practical details
4. Include any important preparation steps
5. End with helpful next steps

Be conversational but informative. Focus on actionable guidance.
Keep the response well-organized with clear sections.
""")
        
        human_message = HumanMessage(content=f"""
Please create a comprehensive waste disposal response based on this analysis:

{context}

Make it helpful, specific, and actionable for the user.
""")
        
        try:
            response = self.llm([system_message, human_message])
            final_response = response.content
            
            print(f"✅ Final response generated ({len(final_response)} characters)")
            return final_response
            
        except Exception as e:
            print(f"⚠️  LLM response generation failed: {e}")
            
            # Fallback response generation
            return self._generate_fallback_response(state)
    
    def _generate_fallback_response(self, state: WasteManagementState) -> str:
        """Generate a structured fallback response without LLM"""
        
        waste_type = state.get('waste_type', 'unknown')
        location_data = state.get('user_location', {})
        regulations = state.get('local_regulations', {})
        locations = state.get('disposal_locations', [])
        
        city = location_data.get('city', 'your area')
        state_name = location_data.get('state', 'your state')
        
        response_parts = []
        
        # Header
        response_parts.append(f"## {waste_type.title()} Disposal Guidance for {city}, {state_name}")
        
        # Waste type classification
        response_parts.append(f"\n**Waste Classification:** Your waste has been classified as {waste_type}.")
        
        # Local regulations
        if regulations:
            response_parts.append(f"\n**Local Regulations:**")
            response_parts.append(f"• {regulations.get('rules', 'No specific rules found')}")
            
            prep_steps = regulations.get('preparation_steps', [])
            if prep_steps:
                response_parts.append(f"\n**Preparation Steps:**")
                for step in prep_steps[:3]:  # Top 3 steps
                    response_parts.append(f"• {step}")
        
        # Disposal locations
        if locations:
            response_parts.append(f"\n**Disposal Locations Near You:**")
            for i, location in enumerate(locations[:3], 1):
                name = location.get('name', 'Unknown Facility')
                address = location.get('address', 'Address not available')
                distance = location.get('distance_km', 'Unknown')
                response_parts.append(f"{i}. **{name}** - {address} ({distance}km)")
                
                if location.get('phone'):
                    response_parts.append(f"   Phone: {location['phone']}")
                
                if location.get('special_instructions'):
                    response_parts.append(f"   Note: {location['special_instructions']}")
        else:
            response_parts.append(f"\n**Disposal Options:**")
            response_parts.append("• Contact your local waste management service")
            response_parts.append("• Check with municipal recycling programs")
            response_parts.append("• Search online for local disposal facilities")
        
        # Next steps
        response_parts.append(f"\n**Next Steps:**")
        response_parts.append("1. Follow any preparation requirements listed above")
        response_parts.append("2. Contact the facility to confirm they accept your waste type")
        response_parts.append("3. Check facility hours and any fees")
        response_parts.append("4. Transport your waste safely to the disposal location")
        
        return "\n".join(response_parts)

class WorkerAgent:
    """
    The Worker Agent executes specific tasks using our tools.
    
    How it works:
    1. Receives task assignments from Supervisor
    2. Uses the appropriate tool for each task
    3. Updates the workflow state with results
    4. Handles errors and provides fallbacks
    """
    
    def __init__(self):
        # Initialize all our tools
        self.tools = {
            'waste_classifier': create_waste_classifier(),
            'geolocation': create_geolocation_tool(),
            'regulation_lookup': create_regulation_lookup_tool(),
            'location_finder': create_location_finder_tool()
        }
        
        print(f"🔧 Worker Agent initialized with {len(self.tools)} tools")
    
    def classify_waste(self, state: WasteManagementState) -> WasteManagementState:
        """Use waste classification tool"""
        
        print("🔍 Worker: Classifying waste...")
        
        try:
            user_query = state.get('user_query', '')
            result_json = self.tools['waste_classifier']._run(user_query)
            result_dict = json.loads(result_json)
            
            state['waste_type'] = result_dict['primary_type']
            state['waste_classification'] = result_dict
            state['confidence_score'] = result_dict.get('confidence', 0.0)
            
            print(f"✅ Waste classified as: {result_dict['primary_type']} (confidence: {result_dict.get('confidence', 0):.2f})")
            
        except Exception as e:
            print(f"❌ Waste classification failed: {e}")
            state['waste_type'] = 'household'
            state['error_message'] = f"Classification error: {str(e)}"
        
        return state
    
    def get_location(self, state: WasteManagementState) -> WasteManagementState:
        """Use geolocation tool"""
        
        print("📍 Worker: Getting user location...")
        
        try:
            # Check if location was provided in the query
            location_input = ""  # Will auto-detect if empty
            
            # TODO: Could extract location from user query using NLP
            # For now, auto-detect or use default
            
            result_json = self.tools['geolocation']._run(location_input)
            result_dict = json.loads(result_json)
            
            state['user_location'] = result_dict
            
            print(f"✅ Location determined: {result_dict.get('city')}, {result_dict.get('state')}")
            
        except Exception as e:
            print(f"❌ Location detection failed: {e}")
            # Fallback to default location
            state['user_location'] = {
                'city': 'New York',
                'state': 'NY',
                'country': 'US'
            }
            state['error_message'] = f"Location error: {str(e)}"
        
        return state
    
    def lookup_regulations(self, state: WasteManagementState) -> WasteManagementState:
        """Use regulation lookup tool"""
        
        print("⚖️  Worker: Looking up local regulations...")
        
        try:
            query_data = {
                'location': state.get('user_location', {}),
                'waste_type': state.get('waste_type', 'household')
            }
            
            result_json = self.tools['regulation_lookup']._run(json.dumps(query_data))
            result_dict = json.loads(result_json)
            
            state['local_regulations'] = result_dict
            
            jurisdiction = result_dict.get('jurisdiction', 'Unknown')
            print(f"✅ Regulations found: {jurisdiction}")
            
        except Exception as e:
            print(f"❌ Regulation lookup failed: {e}")
            state['local_regulations'] = {
                'jurisdiction': 'General Guidelines',
                'rules': 'Please check with local waste management authorities.'
            }
            state['error_message'] = f"Regulation error: {str(e)}"
        
        return state
    
    def find_locations(self, state: WasteManagementState) -> WasteManagementState:
        """Use location finder tool"""
        
        print("🗺️  Worker: Finding disposal locations...")
        
        try:
            query_data = {
                'location': state.get('user_location', {}),
                'waste_type': state.get('waste_type', 'household')
            }
            
            result_json = self.tools['location_finder']._run(json.dumps(query_data))
            result_dict = json.loads(result_json)
            
            facilities = result_dict.get('facilities', [])
            state['disposal_locations'] = facilities
            
            print(f"✅ Found {len(facilities)} disposal locations")
            
        except Exception as e:
            print(f"❌ Location finding failed: {e}")
            state['disposal_locations'] = []
            state['error_message'] = f"Location finder error: {str(e)}"
        
        return state

class WasteManagementWorkflow:
    """
    Main workflow orchestrator that combines Supervisor and Worker agents
    using LangGraph for state management and routing.
    """
    
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.worker = WorkerAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow_graph()
        
        print("🚀 Waste Management Workflow initialized")
    
    def _build_workflow_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow with all nodes and routing logic.
        """
        
        # Create the state graph
        workflow = StateGraph(WasteManagementState)
        
        # Add workflow nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("classify_waste", self._classify_waste_node)
        workflow.add_node("get_location", self._get_location_node)
        workflow.add_node("lookup_regulations", self._lookup_regulations_node)
        workflow.add_node("find_locations", self._find_locations_node)
        workflow.add_node("generate_response", self._generate_response_node)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional routing from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_next_action,
            {
                "classify_waste": "classify_waste",
                "get_location": "get_location", 
                "lookup_regulations": "lookup_regulations",
                "find_locations": "find_locations",
                "generate_response": "generate_response",
                "end": END
            }
        )
        
        # All worker nodes route back to supervisor
        workflow.add_edge("classify_waste", "supervisor")
        workflow.add_edge("get_location", "supervisor")
        workflow.add_edge("lookup_regulations", "supervisor")
        workflow.add_edge("find_locations", "supervisor")
        
        # Response generation ends the workflow
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def _supervisor_node(self, state: WasteManagementState) -> WasteManagementState:
        """Supervisor node that plans the next action"""
        
        next_action = self.supervisor.plan_next_action(state)
        state['processing_step'] = next_action
        
        return state
    
    def _classify_waste_node(self, state: WasteManagementState) -> WasteManagementState:
        """Worker node for waste classification"""
        return self.worker.classify_waste(state)
    
    def _get_location_node(self, state: WasteManagementState) -> WasteManagementState:
        """Worker node for location detection"""
        return self.worker.get_location(state)
    
    def _lookup_regulations_node(self, state: WasteManagementState) -> WasteManagementState:
        """Worker node for regulation lookup"""
        return self.worker.lookup_regulations(state)
    
    def _find_locations_node(self, state: WasteManagementState) -> WasteManagementState:
        """Worker node for location finding"""
        return self.worker.find_locations(state)
    
    def _generate_response_node(self, state: WasteManagementState) -> WasteManagementState:
        """Node for final response generation"""
        
        final_response = self.supervisor.generate_final_response(state)
        state['final_response'] = final_response
        
        return state
    
    def _route_next_action(self, state: WasteManagementState) -> str:
        """Routing function that determines next node based on supervisor decision"""
        
        next_action = state.get('processing_step', 'end')
        
        print(f"🔀 Routing to: {next_action}")
        
        return next_action
    
    async def process_query(self, user_query: str, user_location: Optional[Dict] = None) -> Dict:
        """
        Main entry point - process a user query through the complete workflow.
        
        Args:
            user_query: User's waste disposal question
            user_location: Optional location data (will auto-detect if not provided)
            
        Returns:
            Complete response with guidance, regulations, and locations
        """
        
        print(f"\n🚀 Processing query: '{user_query[:50]}...'")
        start_time = datetime.now()
        
        # Initialize workflow state
        initial_state = WasteManagementState(
            user_query=user_query,
            user_location=user_location,
            waste_type=None,
            waste_classification=None,
            local_regulations=None,
            disposal_locations=None,
            final_response=None,
            guidance_steps=None,
            error_message=None,
            processing_step=None,
            confidence_score=None
        )
        
        try:
            # Run the workflow
            print("🔄 Starting workflow execution...")
            final_state = await self.workflow.ainvoke(initial_state)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Prepare response
            response = {
                'success': True,
                'user_query': user_query,
                'waste_type': final_state.get('waste_type'),
                'user_location': final_state.get('user_location'),
                'final_response': final_state.get('final_response'),
                'waste_classification': final_state.get('waste_classification'),
                'local_regulations': final_state.get('local_regulations'),
                'disposal_locations': final_state.get('disposal_locations'),
                'confidence_score': final_state.get('confidence_score'),
                'processing_time_ms': int(processing_time),
                'error_message': final_state.get('error_message')
            }
            
            print(f"✅ Workflow completed in {processing_time:.0f}ms")
            
            return response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            print(f"❌ Workflow failed: {e}")
            
            return {
                'success': False,
                'user_query': user_query,
                'error_message': str(e),
                'processing_time_ms': int(processing_time),
                'final_response': 'Sorry, I encountered an error processing your request. Please try again or contact local waste management services.'
            }

# Convenience function to create the workflow
def create_waste_management_workflow() -> WasteManagementWorkflow:
    """Factory function to create the waste management workflow"""
    return WasteManagementWorkflow()

# Main execution function
async def main():
    """Test the complete workflow with sample queries"""
    
    print("🧪 Testing Complete Waste Management Workflow...")
    
    workflow = create_waste_management_workflow()
    
    # Test queries
    test_queries = [
        "How do I dispose of old laptop batteries?",
        "I have expired prescription medications to get rid of",
        "What should I do with leftover house paint?",
        "Where can I recycle plastic bottles in my area?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"🧪 Test {i}/{len(test_queries)}")
        
        result = await workflow.process_query(query)
        
        print(f"\n📋 Results:")
        print(f"   Success: {result.get('success')}")
        print(f"   Waste Type: {result.get('waste_type')}")
        
        location = result.get('user_location', {})
        print(f"   Location: {location.get('city', 'Unknown')}, {location.get('state', 'Unknown')}")
        
        print(f"   Processing Time: {result.get('processing_time_ms')}ms")
        print(f"   Disposal Locations: {len(result.get('disposal_locations', []))} found")
        
        if result.get('final_response'):
            print(f"\n📝 Response Preview:")
            print(f"   {result['final_response'][:150]}...")

if __name__ == "__main__":
    asyncio.run(main())