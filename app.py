# app.py
import streamlit as st
from db import Base, engine
from seed_data import seed
import auth as auth_module
import utils
from types import SimpleNamespace

# Initialize DB and seed
Base.metadata.create_all(bind=engine)
seed()

st.set_page_config(page_title="Event Manager", layout="wide")

# Authentication
auth_module.login_widget()
if not st.session_state.get("user"):
    st.stop()
user = st.session_state.user

# Shared UI helpers
def topbar():
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;justify-content:space-between">
          <div>
            <h1 style="margin:0;padding:0">Event Manager</h1>
            <div style="color:gray">Gestione eventi • calendario • team</div>
          </div>
          <div style="text-align:right">
            <div style="font-weight:600">Utente: {user['username']}</div>
            <div style="color:gray">Ruolo: {user['role']}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

def left_nav(selected):
    pages = [
        ("Dashboard", "dashboard"),
        ("Calendario", "calendar"),
        ("Eventi", "events"),
        ("Artisti", "artists"),
        ("Format", "formats"),
        ("Risorse", "resources"),
        ("Promoter", "promoters"),
        ("Admin", "admin"),
    ]
    st.sidebar.title("Navigazione")
    labels = [p[0] for p in pages]
    index = 0
    for i, p in enumerate(pages):
        if p[1] == selected:
            index = i
            break
    choice = st.sidebar.radio("", labels, index=index)
    # map label back to key
    key = dict(pages)[choice]
    return key

# Page skeletons (delegano a pages/* quando vuoi modularizzare)
def page_dashboard(ctx):
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

def page_calendar(ctx):
    st.header("Calendario")
    st.write("Vista mese con filtri. Clic su evento per aprire scheda.")
    year = st.number_input("Anno", min_value=2000, max_value=2100, value=st.session_state.get("view_year",  date.today().year))
    month = st.number_input("Mese", min_value=1, max_value=12, value=st.session_state.get("view_month", date.today().month))
    st.session_state.view_year = year
    st.session_state.view_month = month
    events = utils.list_events_by_month(year, month)
    for e in events:
        st.write(f"{e.date} — {e.title} • {', '.join([a.name for a in e.artists])}")

def page_events(ctx):
    st.header("Eventi")
    if st.session_state.get("show_new_event"):
        st.info("Mostra form di creazione evento (quick create). Vai su 'Eventi' per creare.")
    st.write("Elenco eventi (tabella) con ricerca e filtri.")
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

def page_artists(ctx):
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

def page_formats(ctx):
    st.header("Format")
    st.write("Gestione format e duplicazione rapida di eventi da format.")
    formats = utils.list_formats()
    for f in formats:
        st.write(f"**{f.name}** — {f.default_duration_days} giorno(i)")
        if st.button("Duplica evento da questo format", key=f"dup_{f.id}"):
            st.success("Funzione duplicazione (placeholder)")

def page_resources(ctx):
    st.header("Risorse")
    st.write("DJ, Vocalist, Ballerine, Service, Tour Manager, Mascotte")
    types = ["DJ", "Vocalist", "Ballerina", "Service", "Tour Manager", "Mascotte"]
    sel = st.selectbox("Filtra tipo", ["Tutti"] + types)
    res = utils.list_resources(None if sel == "Tutti" else sel)
    for r in res:
        st.write(f"**{r.name}** • {r.type} • {r.contact or '-'}")

def page_promoters(ctx):
    st.header("Promoter")
    promoters = utils.list_promoters()
    for p in promoters:
        st.write(f"**{p.name}** • {p.contact or '-'}")

def page_admin(ctx):
    st.header("Admin / Impostazioni")
    st.write("Utenti, backup DB, seed, preferenze.")
    if st.button("Esegui seed (ricrea dati mancanti)"):
        seed()
        st.success("Seed eseguito")
        auth_module.safe_rerun()

# Router
def main():
    topbar()
    nav_target = st.session_state.get("nav_target", None)
    selected = nav_target or st.session_state.get("page", "dashboard")
    page_key = left_nav(selected)
    st.session_state.page = page_key
    ctx = SimpleNamespace(user=user)

    if page_key == "dashboard":
        page_dashboard(ctx)
    elif page_key == "calendar":
        page_calendar(ctx)
    elif page_key == "events":
        page_events(ctx)
    elif page_key == "artists":
        page_artists(ctx)
    elif page_key == "formats":
        page_formats(ctx)
    elif page_key == "resources":
        page_resources(ctx)
    elif page_key == "promoters":
        page_promoters(ctx)
    elif page_key == "admin":
        page_admin(ctx)
    else:
        st.write("Pagina non trovata")

if __name__ == "__main__":
    main()
