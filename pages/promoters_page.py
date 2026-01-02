# pages/promoters_page.py
import streamlit as st
import utils

def render(ctx):
    st.header("Promoter")
    promoters = utils.list_promoters()
    for p in promoters:
        st.write(f"**{p.name}** • {p.contact or '-'}")
