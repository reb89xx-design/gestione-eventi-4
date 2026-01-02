# components/event_card.py
import streamlit as st

def render(event):
    st.markdown(f"### {event.title}")
    st.write(f"**Data:** {event.date}")
    st.write(f"**Artisti:** {', '.join([a.name for a in event.artists])}")
    st.write(f"**Format:** {event.format.name if event.format else '-'}")
    st.write(f"**Location:** {event.location or '-'}")
    st.write(f"**Stato:** {event.status}")
    st.write("---")
    st.write(event.notes or "")
