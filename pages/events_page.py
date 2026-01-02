# pages/events_page.py
import streamlit as st
import utils
import auth as auth_module

def render(ctx):
    st.header("Eventi")
    if st.session_state.get("show_new_event"):
        st.info("Mostra form di creazione evento (quick create). Vai su 'Eventi' per creare.")
    events = utils.list_all_events()
    for e in events:
        cols = st.columns([4,2,2,1])
        cols[0].write(f"**{e.title}**")
        cols[1].write(", ".join([a.name for a in e.artists]))
        cols[2].write(str(e.date))
        if cols[3].button("Apri", key=f"open_ev_{e.id}"):
            st.session_state.open_event_id = e.id
            auth_module.safe_rerun()
    if st.session_state.get("open_event_id"):
        ev = utils.get_event(st.session_state.open_event_id)
        st.markdown("---")
        st.subheader(f"Scheda: {ev.title}")
        st.write(f"Data: {ev.date}")
        st.write(f"Artisti: {', '.join([a.name for a in ev.artists])}")
        if st.button("Chiudi scheda"):
            st.session_state.open_event_id = None
            auth_module.safe_rerun()
