# auth.py
import streamlit as st
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from db import SessionLocal

# Usa pbkdf2_sha256 per evitare dipendenze native (compatibile e sicuro)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Utility: hash & verify
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Simple user loader (for prototype)
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

# Streamlit helper
def login_widget():
    if "user" not in st.session_state:
        st.session_state.user = None

    with st.sidebar.form("login_form", clear_on_submit=False):
        st.write("**Login**")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Accedi")
        if submitted:
            user = authenticate(username, password)
            if user:
                st.session_state.user = user
                st.experimental_rerun()
            else:
                st.error("Credenziali non valide")
    if st.session_state.user:
        st.sidebar.write(f"Connesso come **{st.session_state.user['username']}**")
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.experimental_rerun()
