# app.py — Streamlit frontend entry point

import streamlit as st

from graph import build_graph

st.set_page_config(page_title="TravelAI", page_icon="✈️", layout="wide")

# ── ① SESSION STATE INIT ──────────────────────────────────────────
# -- purpose is:
# 1.Create variables only once.
#2.Preserve values across Streamlit reruns.
#3.Avoid rebuilding expensive objects (graph).
#4.Keep user data and application state alive during the session.

if "messages" not in st.session_state:
    st.session_state.messages = []          # full chat history
if "trip_config" not in st.session_state:
    st.session_state.trip_config = {}       # sidebar form values. store trip config.
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()  # LangGraph compiled graph
if "processing" not in st.session_state:
    st.session_state.processing = False
if "show_warning" not in st.session_state:
    st.session_state.show_warning = False
# ── ② SIDEBAR — trip settings form ───────────────────────────────
with st.sidebar:
    st.title("✈️ TravelAI Assistant")
    origin = st.text_input("Departure City", placeholder="Delhi or DEL")
    destination = st.text_input("Destination", placeholder="Tokyo or HND")
    col1, col2 = st.columns(2)
    depart  = col1.date_input("From")
    returns = col2.date_input("To")
    budget  = st.selectbox("Budget", ["Budget", "Mid-range", "Luxury"])
    travellers = st.number_input("Travellers", 1, 10, 2)

    # Saving the trip details.
    if st.session_state.show_warning:
        st.warning("⚠️ Please enter a destination!")

    if st.button("🗺️ Plan my trip", use_container_width=True):

        if not destination.strip():
            #st.warning("⚠️ Please enter a destination!")
            st.session_state.show_warning = True
            st.rerun()
            #st.stop()  # ← stops ALL further execution immediately

        else:
            st.session_state.show_warning = False
            st.session_state.trip_config = {
                "origin": origin,
                "destination": destination,
                "depart_date": depart.strftime("%Y-%m-%d"),
                "return_date": returns.strftime("%Y-%m-%d"),
                "budget": budget,
                "travellers": travellers
        }
        # auto-send as first user message
        st.session_state.messages.append({
            "role": "user",
            "content": f"Plan a trip from {origin} to {destination}"
                       f" from {depart} to {returns}, "
                       f"{travellers} people, {budget} ."
        })
        st.session_state.processing = True
        st.rerun()
    #else:
    #    st.warning("Please enter a destination!")
     #--------------- sidebar footer + reset button pattern-----------------
    st.divider()
    st.button("🗺️ ACTIVE AGENTS", use_container_width=True)
    st.caption("🤖 Groq — Llama 3.1 70B")
    st.caption("🔍 Research Agent + 📅 Itinerary Agent")

    #-------Header section of UI----------------------------
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.trip_config = {}
        st.rerun()

st.title("✈️ Voyanta")
st.caption("AI Agents-Powered Travel Research & Itinerary Planning")

#------------DISPLAYING ALL PREVIOUS MESSAGES FROM CHAT HISTORY-----------------
for msg in st.session_state.messages: #---Take each message from the messages list one by one.----
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
#----message gets sent to your AI graph, the agents run, and the response comes back.-----
if st.session_state.processing:
    st.session_state.processing = False   #in order to avoid infinite loop.
    with st.chat_message("assistant"):
        with st.spinner("🔍 Research Agent is searching..."):
            try:
                state = {
                    "messages": st.session_state.messages,
                    "trip_config": st.session_state.trip_config,
                    "research_output": "",
                    "itinerary_output": ""
                }
                result = st.session_state.graph.invoke(state)
                new_msgs = result.get("messages", [])
                for msg in new_msgs:
                    if msg not in st.session_state.messages:
                        st.session_state.messages.append(msg)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

if prompt := st.chat_input("Ask anything about your trip..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.processing = True
    st.rerun()