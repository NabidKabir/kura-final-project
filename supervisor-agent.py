from langchain_openai import ChatOpenAI
import os
import asyncio
from dotenv import load_dotenv
from fastmcp import Client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import convert_to_messages
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler

load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]

supervisor = None

if not OPENAI_API_KEY or not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
    raise ValueError(
        "Missing required environment variables: OPENAI_API_KEY or SLACK_BOT_TOKEN or SLACK_APP_TOKEN"
    )

app = AsyncApp(token=SLACK_BOT_TOKEN)

def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)

def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")

async def build_locator_agent(recycle_mcp):
    async with recycle_mcp:
        tools = await load_mcp_tools(recycle_mcp.session)
        locator_agent = create_react_agent(
            model="openai:gpt-4.1-mini",
            tools=tools,
            prompt=(
                "You are a locater agent.\n\n"
                "INSTRUCTIONS:\n"
                "- Assist ONLY with locating-related tasks, DO NOT do any math\n"
                "- After you're done with your tasks, respond to the supervisor directly\n"
                "- Respond ONLY with the results of your work, do NOT include ANY other text."
            ),
            name="locater_agent"
        )
        return locator_agent
    
async def build_research_agent(recycle_mcp):
    async with recycle_mcp:
        tools = await load_mcp_tools(recycle_mcp.session)
        research_agent = create_react_agent(
            model="openai:gpt-4.1-mini",
            tools=tools,
            prompt=(
                "You are a research agent.\n\n"
                "INSTRUCTIONS:\n"
                "You are a research agent.\n\n"
                "INSTRUCTIONS:\n"
                "- Assist ONLY with research-related tasks, DO NOT do any math\n"
                "- You will ONLY use the MCP function regulation_retrieval(query: str)"
                "- Do NOT use any other tool."
                "- First consult the waste disposal knowledge base when possible.\n"
                "- If needed, you may use web search for additional context.\n"
                "- After you're done with your tasks, respond to the supervisor directly\n"
                "- Respond ONLY with the results of your work, do NOT include ANY other text."
            ),
            name="research_agent",
        )
        return research_agent
    
@app.event("app_mention")
async def handle_query(body, say):
    global supervisor
    event = body["event"]
    message = event["text"]
    thread_ts = event.get("thread_ts", event["ts"])

    if supervisor is None:
        await say(text="Bot is still starting, please try again.", thread_ts=thread_ts)
        return

    response = await supervisor.ainvoke({"messages": [{"role": "user", "content": message}]})
    print("invoke")
    
    text = response["messages"][-1].content

    await say(text=text, thread_ts=thread_ts)

async def main():
    global supervisor
    async with Client("http://localhost:8000/mcp") as recycle_mcp:
        locator_agent = await build_locator_agent(recycle_mcp)
        research_agent = await build_research_agent(recycle_mcp)

        supervisor = create_supervisor(
            model=init_chat_model("openai:gpt-4.1-mini"),
            agents=[research_agent, locator_agent],
            prompt=(
                "You are a supervisor managing two agents:\n"
                "- a research agent. Assign research-related tasks to this agent, such as more information on city guidelines.\n"
                "- a locater agent. Assign locating-related tasks to this agent, such as finding places near a specific area.\n"
                "Assign work to one agent at a time, do not call agents in parallel.\n"
                "You should use the research agent to inform yourself on the appropriate guidelines and then use the locater agent to give five locations for the user.\n"
                "You must also inform the user of any fines they could incur if they do not follow the guidelines.\n"
                "Do not do any work yourself."
            ),
            add_handoff_back_messages=True,
            output_mode="full_history"
        ).compile()
        handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
        await handler.start_async()
      

if __name__ == "__main__":
    asyncio.run(main())

