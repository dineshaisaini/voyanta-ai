"""Defines both AI agents using LangChain's ReAct (Reason + Act) pattern.
Agent 1- Research Agent searches and gathers destination info.
Agent 2- Itinerary Agent builds the day-by-day plan. Both use Groq Llama 3.1 70B as their brain."""

import os
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools import get_tavily_tool, get_weather, search_flights
from dotenv import load_dotenv

load_dotenv()

#---Step 1- LLM setup + Research Agent


def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile", temperature=0, api_key=os.getenv("GROQ_API_KEY"))

def create_research_agent() :
    llm = get_llm()
    tools = [get_tavily_tool(), get_weather, search_flights]

    system_prompt = """You are an expert travel research assistant.
For any destination, research and provide:
1. Best time to visit and current weather forecast
2. Visa requirements based on the traveller's nationality. If nationality is not provided, assume Indian passport holder.
3. If Origin, Destination and Departure Date are available, ALWAYS use the search_flights tool to find flight options.
4. Before calling search_flights, verify that:
   - Origin is not empty
   - Destination is not empty
   - Departure Date is not empty
5. Never call search_flights with empty values.
6. If any required flight information is missing, ask the user for the missing information instead of calling the tool.
7. Include the returned flight information in the final answer.
8. Do not estimate, invent, or guess flight prices. Use only the tool output.
9. Top attractions and must-see places
10. Local cuisine and best food areas
11. Safety tips and travel advisories
12. Local transport options
13. Cultural tips and customs
14. Estimated daily budget in INR

Always return well-structured, detailed information.

Flight Search Rules:
- Use search_flights only when Origin, Destination and Departure Date are known.
- Never pass an empty string to search_flights.
- If the user asks "show me more flight options", reuse the current trip information from the conversation state.
- Do not ask for information that already exists in the trip configuration.
"""
    return create_agent(model=llm, tools=tools, system_prompt=system_prompt)

#---Step 2: Itinerary Agent
def create_itinerary_agent():
    llm = get_llm()
    #tools = [search_flights]

    system_prompt = """
    You are an expert travel itinerary planner.

    Create a detailed day-by-day itinerary based on:
    - Destination
    - Travel dates
    - Budget
    - Number of travellers
    - Research information provided

    Include:
    - Morning activities
    - Afternoon activities
    - Evening activities
    - Food recommendations
    - Transport suggestions
    - Estimated costs

    Use any available tools when needed.

    Always return a clear day-by-day itinerary.
    """


    return create_agent(
        model=llm,
        system_prompt=system_prompt,
       # tools=tools
    )
