import os
from mcp_server import *
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from fastmcp import Client
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

app = FastAPI()

class Item(BaseModel):
    query: str

@app.post("/agent")
async def agent_chat(item: Item):
    llm = ChatOpenAI(model="gpt-4.1-mini")

    test_client = Client(test_mcp)

    async with test_client:
        tools = await load_mcp_tools(test_client.session)
        agent = create_react_agent(model=llm, tools=tools)
        user_input = item.query
        message_template = {"messages": [HumanMessage(content=user_input)]}
        async for message in agent.astream(message_template):
            if "agent" in message and message['agent']["messages"][0].content:
                response = message['agent']["messages"][0].content
    return {
        "query": item.query,
        "response": response
    }