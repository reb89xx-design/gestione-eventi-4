# pages/resources_page.py
import streamlit as st
import utils

def render(ctx):
    st.header("Risorse")
    types = ["DJ", "Vocalist", "Ballerina", "Service", "Tour Manager", "Mascotte"]
    sel = st.selectbox("Filtra tipo", ["Tutti"] + types)
    res = utils.list_resources(None if sel == "Tutti" else sel)
    for r in res:
        st.write(f"**{r.name}** • {r.type} • {r.contact or '-'}")
