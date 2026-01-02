# pages/artists_page.py
import streamlit as st
import utils
import auth as auth_module

def render(ctx):
    st.header("Artisti")
    if st.session_state.get("show_new_artist"):
        with st.form("new_artist_form"):
            name = st.text_input("Nome artista")
            color = st.color_picker("Colore calendario", "#2b8cbe")
            submitted = st.form_submit_button("Crea artista")
            if submitted:
                utils.create_artist(name=name, calendar_color=color)
                st.success("Artista creato")
                st.session_state.show_new_artist = False
                auth_module.safe_rerun()
    artists = utils.list_artists()
    for a in artists:
        st.write(f"**{a.name}** • {a.calendar_color}")
        if st.button("Apri calendario", key=f"cal_{a.id}"):
            st.session_state.nav_target = "calendar"
            st.session_state.filter_artist = a.name
            auth_module.safe_rerun()
