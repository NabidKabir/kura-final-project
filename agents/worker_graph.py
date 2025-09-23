import os 
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState
from .worker_tools import get_knowledge_base_chunks, geolocate_ip, get_places
from dotenv import load_dotenv

load_dotenv()

def build_worker_agent():
    """Builds the LangGraph that functions as the ReAct Worker Agent."""
    
    # 1. The toolkit for the agent
    tools = [get_knowledge_base_chunks, geolocate_ip, get_places]
    
    # 2. The agent's "brain" (LLM)
    # Note: "gpt-4o-mini" is the current standard name for this model class.
    # Using the name from your file for consistency.
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    
    # Bind the tools to the LLM, making it "tool-aware"
    llm_with_tools = llm.bind_tools(tools)
    
    # 3. The agent's "instructions" (Prompt)
    prompt = ChatPromptTemplate.from_messages([
       ("system", """
        You are a specialized research agent. Your job is to receive a task and use your tools to find the required information.
        After using your tools, you must compile all the results into a single, structured JSON object.
        Do not respond in conversational language; your output must be only the final JSON report.
        """),
       ("human", "{input}"), 
       ("placeholder", "{agent_scratchpad}"),
    ])
    
    # The runnable chain for the agent's brain
    chain = prompt | llm_with_tools

    # 4. Define the Graph Nodes for the ReAct loop
    # The "Reasoning" step
    def supervisor_node(state): 
        return {"messages": [chain.invoke(state)]}

    # The "Action" step
    worker_node = ToolNode(tools)
    
    # 5. Build the Graph
    workflow = StateGraph(AgentState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("worker", worker_node)

    workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges(
        "supervisor", 
        # This check implements the loop: if a tool is called, go to the worker, otherwise end.
        lambda state: "worker" if state["messages"][-1].tool_calls else END
    )
    # After acting, the worker always loops back to the supervisor to reason again.
    workflow.add_edge("worker", "supervisor")

    # The compiled graph is the runnable "agent" object your teammate can import
    return workflow.compile()

#Aurelio's integration
    #import my build_worker_agent
    
    #call my function so you can reach my worker agent
    legit_desiree_worker_agent = build_worker_agent()
    
    #correct me if I am wrong: 
    
    supervisor - create_supervisor(
        agents=[research_agent, locater_agent, legit_desiree_worker_agent]
    )