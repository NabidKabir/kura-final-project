from typing import TypedDict, Annotated, Optional, Any
from langchain_core.messages import BaseMessage 
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """This is the state for the worker agent. This 'messages' will hold the messages during that specific instance of the conversation. When the user exits the Slack integration where they provide input, then the state will be reset. When the worker agent gets the tasks from the Supervisor agent, it will choose what tools to use and then provide a structured output to the supervisor agent."""
    
    #What does this do? The add_messages function tells LangGraph how to update the list. New messages will be appended to the list. Got this from one of the labs :) 
    
    messages: Annotated[list[BaseMessage], add_messages]
    