from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from agents import create_research_agent, create_itinerary_agent
import operator

class TravelState(TypedDict):
    messages:         Annotated[List[dict], operator.add]
    trip_config:      dict
    research_output:  str
    itinerary_output: str

def research_node(state: TravelState) -> dict:
    agent    = create_research_agent()
    trip     = state.get("trip_config", {})
    #print("TRIP CONFIG:", trip)
    last_msg = state["messages"][-1]["content"]


    query = (
        f"Research this travel request: {last_msg}\n"
        f"Origin: {trip.get('origin', '')}\n"
        f"Destination: {trip.get('destination', '')}\n"
        f"Dates: {trip.get('depart_date', '')} to {trip.get('return_date', '')}\n"
        f"Budget: {trip.get('budget', 'mid-range')}\n"
        f"Travellers: {trip.get('travellers', 2)}"

    )
    #print("===== RESEARCH QUERY =====")
    #print(query)
    #print("==========================")
    #print("DEPART:", trip.get("depart"))

    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    output = result["messages"][-1].content

    return dict(messages=[{"role": "assistant",
                           "content": f"🔍 **Research Agent:**\n\n{output}"}], research_output=output)

def itinerary_node(state: TravelState) -> dict:
    agent    = create_itinerary_agent()
    trip     = state.get("trip_config", {})
    research = state.get("research_output", "")
    last_msg = state["messages"][-1]["content"]
    flight_keywords = [
        "flight",
        "airfare",
        "ticket",
        "airline"
    ]

    if any(
            word in last_msg
            for word in flight_keywords
    ):
        return {
            "messages": [],
            "itinerary_output": state.get(
                "itinerary_output",
                ""
            )
        }
    query = (
        f"Using this research:\n{research}\n\n"
        f"Create a full itinerary for: {last_msg}\n"
        f"Origin: {trip.get('origin', '')}\n"
        f"Destination: {trip.get('destination', '')}\n"
        f"Dates: {trip.get('depart_date', '')} to {trip.get('return_date', '')}\n"
        f"Budget: {trip.get('budget', 'mid-range')}\n"
        f"Travellers: {trip.get('travellers', 2)}"
    )

    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    output = result["messages"][-1].content

    return {
        "messages":  [{"role": "assistant",
                              "content": f"📅 **Itinerary Agent:**\n\n{output}"}],
        "itinerary_output": output
    }

def build_graph():
    workflow = StateGraph(TravelState)
    workflow.add_node("research",  research_node)
    workflow.add_node("itinerary", itinerary_node)
    workflow.set_entry_point("research")
    workflow.add_edge("research",  "itinerary")
    workflow.add_edge("itinerary", END)
    return workflow.compile()