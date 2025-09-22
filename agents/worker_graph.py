import os 
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState
from .worker_tools import get_knowledge_base_chunks, geolocate_ip, get_places
from dotenv import load_dotenv

load_dotenv

def build_worker_agent():
    """ Builds the LangGraph for the Worker Agent."""
    
    # List the all of the tools that the worker agent can use; based on function names
    tools = [get_knowledge_base_chunks, geolocate_ip, get_places]
    
    #llm brain and model
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)
    
    #Prompt for the Worker Agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
         
            You are a worker agent aka a research agent. You will receive tasks from the Supervisor Agent after the user asks it a question and it delegates tasks to you. Your need to complete the tasks that you have been givem, using the tools in the mcp server that are available for you. 
            
            If a tool returns that it does not have any information that can answer the users query, then you may use your general knowledge to provide a helpful answer. Always let the user know that you could not find their local regulation, first. """),
        ("user", "{input}"), 
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    #Graph nodes; these are the steps the agent will take; will have to be adjusted bc I do not have code for the supervisor agent yet
    
    def supervisor_node(state): 
        chain = prompt | llm_with_tools
        return {"messages": [llm_with_tools.invoke(state["messages"])]} #other possibility: [cain.invoke(state)]}
    
    #this node completes the tasks
    worker_node = ToolNode(tools)
    
    #Building the graph
    workflow = StateGraph(AgentState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("worker", worker_node)
    
    workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges(
        "supervisor", 
        lambda state: "worker" if state["messages"][-1].tool_calls else "END"
    )
    workflow.add_edge("worker", "supervisor")
    
    return workflow.compile()
    
    