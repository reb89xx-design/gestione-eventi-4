# auth.py
# Autenticazione leggera per Event Manager (Streamlit)
# Usa pbkdf2_sha256 per evitare dipendenze native e include fallback per il rerun

import streamlit as st
from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from db import SessionLocal

# -------------------------
# Compat: safe rerun
# -------------------------
def safe_rerun():
    """
    Tentativo di forzare un rerun in modo compatibile con più versioni di Streamlit.
    - Prova st.experimental_rerun()
    - Se non disponibile, modifica i query params con un timestamp
    - Se anche quello fallisce, toggle di session_state come ultima risorsa
    """
    try:
        st.experimental_rerun()
    except Exception:
        try:
            st.experimental_set_query_params(_rerun=str(datetime.utcnow().timestamp()))
        except Exception:
            st.session_state["_force_rerun"] = not st.session_state.get("_force_rerun", False)

# -------------------------
# Hashing password
# -------------------------
# Uso pbkdf2_sha256 per compatibilità e sicurezza senza dipendenze C
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# -------------------------
# DB helpers & autenticazione
# -------------------------
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate(username: str, password: str):
    db = SessionLocal()
    try:
        user = get_user_by_username(db, username)
        if not user:
            return None
        if verify_password(password, user.hashed_password):
            return {"id": user.id, "username": user.username, "role": user.role}
        return None
    finally:
        db.close()

# -------------------------
# Widget Streamlit per login
# -------------------------
def login_widget():
    if "user" not in st.session_state:
        st.session_state.user = None

    with st.sidebar.form("login_form", clear_on_submit=False):
        st.markdown("### Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Accedi")
        if submitted:
            user = authenticate(username, password)
            if user:
                st.session_state.user = user
                safe_rerun()
            else:
                st.error("Credenziali non valide")

    if st.session_state.user:
        st.sidebar.markdown(f"**Connesso come:** {st.session_state.user['username']}")
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            safe_rerun()
