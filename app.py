# app.py
# Event Manager - Streamlit single-entry router (pagine separate)
# Usa: sqlite + SQLAlchemy + Streamlit
#
# Avvio:
# 1) pip install -r requirements.txt
# 2) python seed_data.py
# 3) streamlit run app.py

import streamlit as st
from datetime import date, datetime
import calendar
from types import SimpleNamespace

from db import Base, engine
from seed_data import seed
import auth as auth_module
import utils

# --- Inizializza DB e seed (idempotente) ---
Base.metadata.create_all(bind=engine)
seed()

st.set_page_config(page_title="Event Manager", layout="wide")

# --- Autenticazione ---
auth_module.login_widget()
if not st.session_state.get("user"):
    st.stop()
user = st.session_state.user

# --- Helper UI condivisi ---
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
    # mappa label -> key
    key = dict(pages)[choice]
    return key

# --- Pagine (skeleton, estendibili) ---
def page_dashboard(ctx):
    st.header("Dashboard")
    st.subheader("Prossimi eventi")
    events = utils.list_upcoming_events(limit=10)
    if not events:
        st.info("Nessun evento futuro trovato.")
    for e in events:
        st.write(f"**{e.date}** — {e.title} • {', '.join([a.name for a in e.artists])} • _{e.status}_")
    st.markdown("---")
    st.subheader("Azioni rapide")
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
    st.write("Vista mese. Filtra da sinistra e clicca un evento per aprire la scheda.")
    # valori di default dal session_state o oggi
    year = st.number_input("Anno", min_value=2000, max_value=2100, value=st.session_state.get("view_year", date.today().year))
    month = st.number_input("Mese", min_value=1, max_value=12, value=st.session_state.get("view_month", date.today().month))
    st.session_state.view_year = year
    st.session_state.view_month = month

    events = utils.list_events_by_month(year, month)
    if not events:
        st.info("Nessun evento per il mese selezionato.")
    # semplice rendering elenco; sostituibile con calendar_widget o FullCalendar
    for e in events:
        cols = st.columns([4,2,2,1])
        cols[0].write(f"**{e.title}**")
        cols[1].write(", ".join([a.name for a in e.artists]) or "-")
        cols[2].write(str(e.date))
        if cols[3].button("Apri", key=f"cal_open_{e.id}"):
            st.session_state.open_event_id = e.id
            auth_module.safe_rerun()

def page_events(ctx):
    st.header("Eventi")
    # Quick create se richiesto
    if st.session_state.get("show_new_event"):
        st.info("Creazione rapida: compila i campi principali e salva.")
        with st.form("quick_create_event"):
            title = st.text_input("Titolo")
            event_date = st.date_input("Data", value=date.today())
            formats = utils.list_formats()
            format_choice = st.selectbox("Format", options=[f.name for f in formats] if formats else ["-"])
            artists = utils.list_artists()
            artists_choice = st.multiselect("Artisti", options=[a.name for a in artists])
            status = st.selectbox("Stato", options=["proposta", "confermato", "cancellato"], index=0)
            submitted = st.form_submit_button("Crea")
            if submitted:
                db_fmt = None
                if format_choice and format_choice != "-":
                    db_fmt = next((f for f in formats if f.name == format_choice), None)
                db = utils.SessionLocal() if hasattr(utils, "SessionLocal") else None
                try:
                    # usa utils.create_event per consistenza
                    artist_objs = []
                    for aname in artists_choice:
                        a = next((x for x in artists if x.name == aname), None)
                        if a:
                            artist_objs.append(a)
                    utils.create_event(title=title, date_=event_date, format_obj=db_fmt, status=status, artist_objs=artist_objs)
                    st.success("Evento creato")
                    st.session_state.show_new_event = False
                    auth_module.safe_rerun()
                except Exception as e:
                    st.error(f"Errore creazione evento: {e}")

    # Lista eventi con ricerca e azioni
    st.subheader("Elenco eventi")
    events = utils.list_all_events()
    search = st.text_input("Cerca per titolo o artista")
    filtered = []
    for e in events:
        if not search:
            filtered.append(e)
        else:
            if search.lower() in e.title.lower() or any(search.lower() in a.name.lower() for a in e.artists):
                filtered.append(e)
    if not filtered:
        st.info("Nessun evento trovato.")
    for e in filtered:
        cols = st.columns([4,2,2,1])
        cols[0].write(f"**{e.title}**")
        cols[1].write(", ".join([a.name for a in e.artists]) or "-")
        cols[2].write(str(e.date))
        if cols[3].button("Apri", key=f"events_open_{e.id}"):
            st.session_state.open_event_id = e.id
            auth_module.safe_rerun()

    # Scheda evento aperta
    if st.session_state.get("open_event_id"):
        ev = utils.get_event(st.session_state.open_event_id)
        if ev:
            st.markdown("---")
            st.subheader(f"Scheda evento: {ev.title}")
            with st.form(f"edit_event_{ev.id}"):
                title = st.text_input("Titolo", value=ev.title)
                event_date = st.date_input("Data", value=ev.date)
                formats = utils.list_formats()
                format_names = [f.name for f in formats]
                format_choice = st.selectbox("Format", options=format_names if format_names else ["-"], index=format_names.index(ev.format.name) if ev.format and ev.format.name in format_names else 0)
                artists = utils.list_artists()
                artist_names = [a.name for a in artists]
                artists_choice = st.multiselect("Artisti", options=artist_names, default=[a.name for a in ev.artists])
                promoters = utils.list_promoters()
                promoter_names = [p.name for p in promoters]
                promoter_choice = st.selectbox("Promoter", options=["-"] + promoter_names, index=(1 + promoter_names.index(ev.promoter.name)) if ev.promoter and ev.promoter.name in promoter_names else 0)
                location = st.text_input("Location", value=ev.location or "")
                notes = st.text_area("Note", value=ev.notes or "")
                # risorse
                all_resources = utils.list_resources()
                res_options = [f"{r.type}: {r.name}" for r in all_resources]
                default_res = [f"{r.type}: {r.name}" for r in ev.resources]
                resources_choice = st.multiselect("Risorse (assegna)", options=res_options, default=default_res)
                status = st.selectbox("Stato", options=["proposta", "confermato", "cancellato"], index=["proposta","confermato","cancellato"].index(ev.status))
                save = st.form_submit_button("Salva")
                delete = st.form_submit_button("Elimina")
                if save:
                    try:
                        fmt_obj = next((f for f in formats if f.name == format_choice), None)
                        promoter_obj = None
                        if promoter_choice and promoter_choice != "-":
                            promoter_obj = next((p for p in promoters if p.name == promoter_choice), None)
                        # aggiorna campi
                        ev.title = title
                        ev.date = event_date
                        ev.format = fmt_obj
                        ev.promoter = promoter_obj
                        ev.location = location
                        ev.notes = notes
                        ev.status = status
                        # artists
                        ev.artists = []
                        for aname in artists_choice:
                            aobj = next((a for a in artists if a.name == aname), None)
                            if aobj:
                                ev.artists.append(aobj)
                        # resources
                        ev.resources = []
                        for rsel in resources_choice:
                            try:
                                rtype, rname = rsel.split(": ", 1)
                                res = next((r for r in all_resources if r.type == rtype and r.name == rname), None)
                                if res:
                                    ev.resources.append(res)
                            except Exception:
                                pass
                        utils.update_event(ev.id, title=ev.title, date=ev.date, format=ev.format, promoter=ev.promoter, location=ev.location, notes=ev.notes, status=ev.status)
                        st.success("Evento aggiornato")
                        st.session_state.open_event_id = None
                        auth_module.safe_rerun()
                    except Exception as e:
                        st.error(f"Errore salvataggio: {e}")
                if delete:
                    try:
                        utils.delete_event(ev.id)
                        st.success("Evento eliminato")
                        st.session_state.open_event_id = None
                        auth_module.safe_rerun()
                    except Exception as e:
                        st.error(f"Errore eliminazione: {e}")

def page_artists(ctx):
    st.header("Artisti")
    if st.session_state.get("show_new_artist"):
        with st.form("new_artist_form"):
            name = st.text_input("Nome artista")
            color = st.color_picker("Colore calendario", "#2b8cbe")
            submitted = st.form_submit_button("Crea artista")
            if submitted:
                try:
                    utils.create_artist(name=name, calendar_color=color)
                    st.success("Artista creato")
                    st.session_state.show_new_artist = False
                    auth_module.safe_rerun()
                except Exception as e:
                    st.error(f"Errore creazione artista: {e}")
    st.subheader("Elenco artisti")
    artists = utils.list_artists()
    if not artists:
        st.info("Nessun artista presente.")
    for a in artists:
        cols = st.columns([4,1])
        cols[0].write(f"**{a.name}**")
        cols[1].write(a.calendar_color)
        if cols[0].button("Apri calendario artista", key=f"artist_cal_{a.id}"):
            st.session_state.nav_target = "calendar"
            st.session_state.filter_artist = a.name
            auth_module.safe_rerun()

def page_formats(ctx):
    st.header("Format")
    st.subheader("Elenco format")
    formats = utils.list_formats()
    if not formats:
        st.info("Nessun format presente.")
    for f in formats:
        cols = st.columns([4,1])
        cols[0].write(f"**{f.name}**")
        cols[1].write(f"{f.default_duration_days} giorno(i)")
        if cols[0].button("Modifica", key=f"edit_format_{f.id}"):
            st.info("Modifica format: funzione da implementare (placeholder).")

def page_resources(ctx):
    st.header("Risorse")
    types = ["DJ", "Vocalist", "Ballerina", "Service", "Tour Manager", "Mascotte"]
    sel = st.selectbox("Filtra tipo", ["Tutti"] + types)
    res = utils.list_resources(None if sel == "Tutti" else sel)
    if not res:
        st.info("Nessuna risorsa trovata.")
    for r in res:
        cols = st.columns([4,1])
        cols[0].write(f"**{r.name}** • {r.type}")
        cols[1].write(r.contact or "-")

def page_promoters(ctx):
    st.header("Promoter")
    promoters = utils.list_promoters()
    if not promoters:
        st.info("Nessun promoter presente.")
    for p in promoters:
        st.write(f"**{p.name}** • {p.contact or '-'}")

def page_admin(ctx):
    st.header("Admin / Impostazioni")
    st.write("Utenti, backup DB, seed, preferenze.")
    if st.button("Esegui seed (ricrea dati mancanti)"):
        seed()
        st.success("Seed eseguito")
        auth_module.safe_rerun()

# --- Router principale ---
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
