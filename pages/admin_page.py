# pages/admin_page.py
import streamlit as st
from seed_data import seed
import auth as auth_module

def render(ctx):
    st.header("Admin / Impostazioni")
    st.write("Utenti, backup DB, seed, preferenze.")
    if st.button("Esegui seed (ricrea dati mancanti)"):
        seed()
        st.success("Seed eseguito")
        auth_module.safe_rerun()
