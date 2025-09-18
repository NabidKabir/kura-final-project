# kura-final-project
Project submission for final enterprise project as per Google's and Kura Labs' Agentic AI Learning Course

Challenge Statement and Architecture

**Challenge Statement: 
  -Our focus is on the helping businesses properly recycle their waste and follow the regulations as defined by their state or local city. Many cities within the United States have different recycling laws, which makes it difficult for sources to offer a comprehensive list and information to businesses. The United States produces a massive amount of waste each year. Waste produced also contributes to environmental degradation and threatens the safety and health of many people both in the U.S. and abroad. 

  **Architecture
    - Hierarchial Agent using a Supervisor and Worker agent workflow. 
      -The user provides input to the Supervisor agent and then the Supervisor assigns tasks to the Worker agent, delegating what is needed. Examples of this include deciding the user's location, whether they are an individual or business, and what they are asking. The worker will then gather the requested info and give it to the Supervisor agent who then will provide a readable summary and instructions to the user in a format that makes sense to them. 

  -Tools used 
    - Google Places API 
    - OpenAI 
    - MCP 
    - LangChain
    -
