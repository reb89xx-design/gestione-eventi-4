# pages/calendar_page.py
import streamlit as st
import utils
from datetime import date

def render(ctx):
    st.header("Calendario")
    year = st.number_input("Anno", min_value=2000, max_value=2100, value=st.session_state.get("view_year", date.today().year))
    month = st.number_input("Mese", min_value=1, max_value=12, value=st.session_state.get("view_month", date.today().month))
    st.session_state.view_year = year
    st.session_state.view_month = month
    events = utils.list_events_by_month(year, month)
    for e in events:
        st.write(f"{e.date} — {e.title} • {', '.join([a.name for a in e.artists])}")
