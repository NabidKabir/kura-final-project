#experimental code

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Import the function that builds your agent's brain
from agents.worker_graph import build_worker_agent

# Import the callback manager that will be our token tracker
from langchain_community.callbacks import get_openai_callback

# Load environment variables from your .env file
load_dotenv()

# --- BUILD THE AGENT ---
# This calls the function in your worker_graph.py file
worker_agent = build_worker_agent()

# --- DEFINE THE TASK ---
# This is the high-level task that would come from the Supervisor Agent
task = "I have a restaurant in NYC, what are the rules for my trash bins?"

# --- RUN THE AGENT AND TRACK USAGE ---
if __name__ == "__main__":
    print(f"--- Running Worker Agent for task: '{task}' ---")

    # This 'with' block is your token usage tracker
    with get_openai_callback() as cb:
        # This is where we invoke the agent to run the task
        response = worker_agent.invoke({"messages": [HumanMessage(content=task)]})

        # After the agent is finished, the 'cb' object contains all the usage data
        print(f"\n--- TOKEN USAGE TRACKER ---")
        print(f"Total Tokens: {cb.total_tokens}")
        print(f"Prompt Tokens: {cb.prompt_tokens}")
        print(f"Completion Tokens: {cb.completion_tokens}")
        print(f"Total Cost (USD): ${cb.total_cost:.4f}")

    # The final answer is the last message in the conversation stream
    final_answer = response["messages"][-1].content

    print("\n--- FINAL AGENT RESPONSE ---")
    print(final_answer)