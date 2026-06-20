import os
import requests
from langchain.tools import tool
#from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

# ------------Tool 1 — Tavily web search---------------------
load_dotenv()

def get_tavily_tool():
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment variables")

    return TavilySearch(
        max_results=5,
        tavily_api_key=api_key
    )
    """return TavilySearchResults(
        max_results=5,
        tavily_api_key=api_key
    )"""
#-----------------Tool 2 — Open-Meteo weather (no API key needed)---------------

@tool
def get_weather(city: str) -> str:
    """Get weather forecast for a city. Input should be a city name."""
    try:
        geo_url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
        geo_res = requests.get(geo_url, headers={"User-Agent": "TravelPlannerApp/1.0"})
        geo_data = geo_res.json()

        if not geo_data:
            return f"Could not find location: {city}"

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            f"&timezone=auto&forecast_days=7"
        )
        w_res = requests.get(weather_url)
        w_data = w_res.json()
        daily = w_data.get("daily", {})

        result = f"Weather forecast for {city}:\n"
        for i in range(min(5, len(daily.get("time", [])))):
            result += (
                f"- {daily['time'][i]}: "
                f"Max {daily['temperature_2m_max'][i]}°C, "
                f"Min {daily['temperature_2m_min'][i]}°C, "
                f"Rain: {daily['precipitation_sum'][i]}mm\n"
            )
        return result
    except Exception as e:
        return f"Weather fetch failed: {str(e)}"

#Tool 3 — SERPAPI (Google) flight search

@tool
def search_flights(origin: str, destination: str, departure_date: str, adults: int = 1) -> str:
    """Search for available flights between two cities.
    Args:
        origin: departure city or airport code e.g. Delhi or DEL
        destination: arrival city or airport code e.g. Tokyo or TYO
        departure_date: date in YYYY-MM-DD format
        adults: number of adult passengers
    """
    if not departure_date:
        return "Departure date is required."

    if not origin:
        return "Origin is required."

    if not destination:
        return "Destination is required."

    print("==== FLIGHT TOOL CALLED ====")
    print("Origin:", origin)
    print("Destination:", destination)
    print("Departure:", departure_date)
    print("Adults:", adults)

    try:
        from serpapi import GoogleSearch
        api_key = os.getenv("SERPAPI_KEY")
        if not api_key:
            return "SERPAPI_KEY is missing from environment variables."

        params = {
            "engine":            "google_flights",
            "departure_id":      origin,
            "arrival_id":        destination,
            "outbound_date":     departure_date,
            "type":2,            #one way flights
            "adults":            adults,
            "currency":          "INR",
            "hl":                "en",
            "api_key":           os.getenv("SERPAPI_KEY")
        }

        search  = GoogleSearch(params)
        """ Creates the search object"""
        results = search.get_dict()
        """sends the requests"""
        if "error" in results:
            return f"SerpAPI Error: {results['error']}"

        best_flights = results.get("best_flights", [])
        """Get the best recommendations"""
        other_flights = results.get("other_flights", [])
        """Get the other flights or additional options"""
        all_flights = best_flights + other_flights
        """Combine both the results in one"""

        if not all_flights:
            return f"No flights found from {origin} to {destination} on {departure_date}"


        response = f"Flights from {origin} to {destination} on {departure_date}:\n\n"
        # ---- Showing top 3 flights------------------
        for i, flight in enumerate(all_flights[:3], 1):
            price    = flight.get("price", "N/A")
            duration = flight.get("total_duration", 0)
            hours    = duration // 60
            minutes  = duration % 60
            legs     = flight.get("flights", [{}])
            airline  = legs[0].get("airline", "N/A") if legs else "N/A"
            stops    = len(legs) - 1
            stop_txt = "Direct" if stops == 0 else f"{stops} stop"
            response += f"{i}. {airline} | {hours}h {minutes}m | {stop_txt} | INR {price}\n"
            """IndiGo | 2h 45m | Direct | INR 6500"""

        return response

    except Exception as e:
        return f"Flight search failed: {str(e)}"

#if __name__ == "__main__":
 #   result = search_flights.invoke({
  #      "origin": "DEL",
   #     "destination": "GOI",
    #    "departure_date": "2026-07-15",
     #   "adults": 1
    #})

    #print(result)