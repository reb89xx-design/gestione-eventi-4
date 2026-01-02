# pages/dashboard.py
# (opzionale: se vuoi spostare le funzioni pagina in file separati)
import streamlit as st
import utils
import auth as auth_module

def render(ctx):
    st.header("Dashboard")
    st.subheader("Prossimi eventi")
    events = utils.list_upcoming_events(limit=10)
    for e in events:
        st.write(f"**{e.date}** — {e.title} • {', '.join([a.name for a in e.artists])} • _{e.status}_")
    st.markdown("---")
    st.subheader("Quick actions")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Nuovo Evento"):
            st.session_state.nav_target = "events"
            st.session_state.show_new_event = True
            auth_module.safe_rerun()
    with c2:
        if st.button("Crea Artista"):
            st.session_state.nav_target = "artists"
            st.session_state.show_new_artist = True
            auth_module.safe_rerun()
    with c3:
        if st.button("Apri Calendario"):
            st.session_state.nav_target = "calendar"
            auth_module.safe_rerun()
