# app.py
# Web app Streamlit per gestione eventi (Event Manager)
# Include: autenticazione leggera, calendario mese, filtri, scheda evento editabile,
# gestione anagrafiche: Artisti, Format, Promoter, Risorse (DJ, Vocalist, Ballerine, Service, Tour Manager, Mascotte)
#
# Avvio:
# 1) pip install -r requirements.txt
# 2) python seed_data.py
# 3) streamlit run app.py

import streamlit as st
from datetime import date, datetime, timedelta
import calendar

# DB / models / utils / auth
from db import Base, engine, SessionLocal
from seed_data import seed
from models import Event, Artist, Format, Resource, Promoter
import auth as auth_module
import utils as utils

# Inizializza DB e dati di esempio (idempotente)
Base.metadata.create_all(bind=engine)
seed()

st.set_page_config(page_title="Event Manager", layout="wide", initial_sidebar_state="expanded")

# -------------------------
# Autenticazione (semplice)
# -------------------------
auth_module.login_widget()
if not st.session_state.get("user"):
    st.stop()
user = st.session_state.user

# -------------------------
# Top bar
# -------------------------
st.markdown(
    """
    <div style="display:flex;align-items:center;justify-content:space-between">
      <div>
        <h1 style="margin:0;padding:0">Event Manager</h1>
        <div style="color:gray">Gestione eventi • calendario giornaliero • team</div>
      </div>
      <div style="text-align:right">
        <div style="font-weight:600">Utente: {username}</div>
        <div style="color:gray">Ruolo: {role}</div>
      </div>
    </div>
    """.format(username=user["username"], role=user["role"]),
    unsafe_allow_html=True,
)

st.markdown("---")

# -------------------------
# Sidebar: filtri e admin
# -------------------------
with st.sidebar:
    st.header("Filtri calendario")
    artists = utils.list_artists()
    formats = utils.list_formats()
    artist_names = [a.name for a in artists]
    format_names = [f.name for f in formats]

    selected_artists = st.multiselect("Artisti", options=artist_names)
    selected_formats = st.multiselect("Format", options=format_names)
    status_filter = st.multiselect("Stato", options=["proposta", "confermato", "cancellato"], default=["proposta", "confermato"])
    st.markdown("---")
    if st.button("Nuovo Evento"):
        st.session_state.show_new_event = True

    st.markdown("---")
    st.header("Admin: Anagrafiche")
    admin_section = st.selectbox("Seleziona", ["Nessuno", "Artisti", "Format", "Promoter", "Risorse (DJ/Vocalist/Ballerine)"])

# -------------------------
# Month navigation state
# -------------------------
today = date.today()
if "view_year" not in st.session_state:
    st.session_state.view_year = today.year
if "view_month" not in st.session_state:
    st.session_state.view_month = today.month

col1, col2, col3 = st.columns([1,6,1])
with col1:
    if st.button("◀"):
        m = st.session_state.view_month - 1
        y = st.session_state.view_year
        if m < 1:
            m = 12
            y -= 1
        st.session_state.view_month = m
        st.session_state.view_year = y
        st.experimental_rerun()
with col2:
    st.markdown(f"### {calendar.month_name[st.session_state.view_month]} {st.session_state.view_year}")
with col3:
    if st.button("▶"):
        m = st.session_state.view_month + 1
        y = st.session_state.view_year
        if m > 12:
            m = 1
            y += 1
        st.session_state.view_month = m
        st.session_state.view_year = y
        st.experimental_rerun()

# -------------------------
# Fetch events for month and apply filters
# -------------------------
events = utils.list_events_by_month(st.session_state.view_year, st.session_state.view_month)

def event_matches_filters(ev):
    if selected_artists:
        names = [a.name for a in ev.artists]
        if not any(name in selected_artists for name in names):
            return False
    if selected_formats:
        if ev.format and ev.format.name not in selected_formats:
            return False
    if status_filter:
        if ev.status not in status_filter:
            return False
    return True

events = [e for e in events if event_matches_filters(e)]

# -------------------------
# Render month grid (semplice)
# -------------------------
cal = calendar.Calendar(firstweekday=0)
month_days = cal.monthdayscalendar(st.session_state.view_year, st.session_state.view_month)

def render_day_cell(day):
    if day == 0:
        st.write("")
        return
    d = date(st.session_state.view_year, st.session_state.view_month, day)
    st.markdown(f"**{day}**")
    day_events = [e for e in events if e.date == d]
    for ev in day_events:
        artists_str = ", ".join([a.name for a in ev.artists])
        # badge-like display
        st.markdown(f"- **{ev.title}**  •  {artists_str}  •  _{ev.status}_")
        if st.button(f"Apri {ev.id}", key=f"open_{ev.id}"):
            st.session_state.open_event_id = ev.id
            st.experimental_rerun()

# Grid rendering: una riga per settimana
for week in month_days:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            render_day_cell(day)

st.markdown("---")

# -------------------------
# Right column: new event form / event detail
# -------------------------
right_col = st.container()

with right_col:
    # Nuovo evento
    if st.session_state.get("show_new_event"):
        st.subheader("Crea nuovo evento")
        with st.form("new_event_form"):
            title = st.text_input("Titolo")
            event_date = st.date_input("Data", value=date.today())
            format_choice = st.selectbox("Format", options=[f.name for f in formats])
            artists_choice = st.multiselect("Artisti", options=[a.name for a in artists])
            promoter_choice = st.selectbox("Promoter", options=[p.name for p in utils.list_promoters()] + ["-"], index=0)
            location = st.text_input("Location")
            notes = st.text_area("Note")
            # risorse multi-select (tutte)
            all_resources = utils.list_resources()
            res_options = [f"{r.type}: {r.name}" for r in all_resources]
            resources_choice = st.multiselect("Risorse (assegna)", options=res_options)
            status = st.selectbox("Stato", options=["proposta", "confermato", "cancellato"], index=0)
            submitted = st.form_submit_button("Crea")
            if submitted:
                db = SessionLocal()
                try:
                    fmt = db.query(Format).filter(Format.name == format_choice).first()
                    promoter = None
                    if promoter_choice and promoter_choice != "-":
                        promoter = db.query(Promoter).filter(Promoter.name == promoter_choice).first()
                    ev = Event(date=event_date, title=title, format=fmt, promoter=promoter, location=location, notes=notes, status=status)
                    for aname in artists_choice:
                        art = db.query(Artist).filter(Artist.name == aname).first()
                        if art:
                            ev.artists.append(art)
                    for rsel in resources_choice:
                        # rsel format: "Type: Name"
                        try:
                            rtype, rname = rsel.split(": ", 1)
                            res = db.query(Resource).filter(Resource.type == rtype, Resource.name == rname).first()
                            if res:
                                ev.resources.append(res)
                        except Exception:
                            pass
                    db.add(ev)
                    db.commit()
                    st.success("Evento creato")
                    st.session_state.show_new_event = False
                    st.experimental_rerun()
                finally:
                    db.close()

    # Scheda evento aperta
    if st.session_state.get("open_event_id"):
        ev_id = st.session_state.open_event_id
        db = SessionLocal()
        ev = db.query(Event).get(ev_id)
        if ev:
            st.subheader(f"Scheda evento: {ev.title}")
            with st.form(f"edit_event_{ev.id}"):
                title = st.text_input("Titolo", value=ev.title)
                event_date = st.date_input("Data", value=ev.date)
                format_choice = st.selectbox("Format", options=[f.name for f in formats], index=0)
                artists_choice = st.multiselect("Artisti", options=[a.name for a in artists], default=[a.name for a in ev.artists])
                promoter_choice = st.selectbox("Promoter", options=[p.name for p in utils.list_promoters()] + ["-"], index=0 if not ev.promoter else [p.name for p in utils.list_promoters()].index(ev.promoter.name) if ev.promoter and ev.promoter.name in [p.name for p in utils.list_promoters()] else 0)
                location = st.text_input("Location", value=ev.location or "")
                notes = st.text_area("Note", value=ev.notes or "")
                # resources
                all_resources = utils.list_resources()
                res_options = [f"{r.type}: {r.name}" for r in all_resources]
                default_res = [f"{r.type}: {r.name}" for r in ev.resources]
                resources_choice = st.multiselect("Risorse (assegna)", options=res_options, default=default_res)
                status = st.selectbox("Stato", options=["proposta", "confermato", "cancellato"], index=["proposta","confermato","cancellato"].index(ev.status))
                save = st.form_submit_button("Salva")
                delete = st.form_submit_button("Elimina evento")
                if save:
                    try:
                        fmt = db.query(Format).filter(Format.name == format_choice).first()
                        promoter = None
                        if promoter_choice and promoter_choice != "-":
                            promoter = db.query(Promoter).filter(Promoter.name == promoter_choice).first()
                        ev.title = title
                        ev.date = event_date
                        ev.format = fmt
                        ev.promoter = promoter
                        ev.location = location
                        ev.notes = notes
                        ev.status = status
                        # update artists
                        ev.artists = []
                        for aname in artists_choice:
                            art = db.query(Artist).filter(Artist.name == aname).first()
                            if art:
                                ev.artists.append(art)
                        # update resources
                        ev.resources = []
                        for rsel in resources_choice:
                            try:
                                rtype, rname = rsel.split(": ", 1)
                                res = db.query(Resource).filter(Resource.type == rtype, Resource.name == rname).first()
                                if res:
                                    ev.resources.append(res)
                            except Exception:
                                pass
                        db.add(ev)
                        db.commit()
                        st.success("Evento aggiornato")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Errore: {e}")
                if delete:
                    try:
                        db.delete(ev)
                        db.commit()
                        st.success("Evento eliminato")
                        st.session_state.open_event_id = None
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Errore: {e}")
        db.close()

# -------------------------
# Admin: gestione anagrafiche
# -------------------------
if admin_section == "Artisti":
    st.header("Gestione Artisti")
    cols = st.columns([2,1,1])
    with cols[0]:
        search = st.text_input("Cerca artista")
    with cols[1]:
        if st.button("Nuovo artista"):
            st.session_state.show_new_artist = True
    artists = utils.list_artists()
    if st.session_state.get("show_new_artist"):
        st.subheader("Crea nuovo artista")
        with st.form("new_artist"):
            name = st.text_input("Nome")
            bio = st.text_area("Bio")
            color = st.color_picker("Colore calendario", "#2b8cbe")
            submitted = st.form_submit_button("Crea")
            if submitted:
                utils.create_artist(name=name, bio=bio, calendar_color=color)
                st.success("Artista creato")
                st.session_state.show_new_artist = False
                st.experimental_rerun()
    st.write("### Elenco artisti")
    for a in artists:
        if search and search.lower() not in a.name.lower():
            continue
        st.write(f"**{a.name}**  •  {a.calendar_color}  •  {'Attivo' if a.active else 'Inattivo'}")
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button(f"Modifica_{a.id}", key=f"edit_artist_{a.id}"):
                st.session_state.edit_artist_id = a.id
                st.experimental_rerun()
        with c2:
            if st.button(f"Elimina_{a.id}", key=f"del_artist_{a.id}"):
                utils.delete_artist(a.id)
                st.success("Artista eliminato")
                st.experimental_rerun()
    if st.session_state.get("edit_artist_id"):
        aid = st.session_state.edit_artist_id
        a = utils.get_artist(aid)
        if a:
            st.subheader(f"Modifica artista: {a.name}")
            with st.form(f"form_edit_artist_{a.id}"):
                name = st.text_input("Nome", value=a.name)
                bio = st.text_area("Bio", value=a.bio or "")
                color = st.color_picker("Colore calendario", value=a.calendar_color or "#2b8cbe")
                active = st.checkbox("Attivo", value=a.active)
                save = st.form_submit_button("Salva")
                cancel = st.form_submit_button("Annulla")
                if save:
                    utils.update_artist(a.id, name=name, bio=bio, calendar_color=color, active=active)
                    st.success("Aggiornato")
                    st.session_state.edit_artist_id = None
                    st.experimental_rerun()
                if cancel:
                    st.session_state.edit_artist_id = None
                    st.experimental_rerun()

if admin_section == "Format":
    st.header("Gestione Format")
    if st.button("Nuovo format"):
        st.session_state.show_new_format = True
    if st.session_state.get("show_new_format"):
        with st.form("new_format"):
            name = st.text_input("Nome format")
            desc = st.text_area("Descrizione")
            dur = st.number_input("Durata giorni (default)", min_value=1, value=1)
            submitted = st.form_submit_button("Crea")
            if submitted:
                utils.create_format(name=name, description=desc, default_duration_days=dur)
                st.success("Format creato")
                st.session_state.show_new_format = False
                st.experimental_rerun()
    formats = utils.list_formats()
    for f in formats:
        st.write(f"**{f.name}**  •  {f.default_duration_days} giorno(i)")
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button(f"Modifica_format_{f.id}", key=f"edit_format_{f.id}"):
                st.session_state.edit_format_id = f.id
                st.experimental_rerun()
        with c2:
            if st.button(f"Elimina_format_{f.id}", key=f"del_format_{f.id}"):
                utils.delete_format(f.id)
                st.success("Format eliminato")
                st.experimental_rerun()
    if st.session_state.get("edit_format_id"):
        fid = st.session_state.edit_format_id
        f = utils.get_format(fid)
        if f:
            with st.form(f"form_edit_format_{f.id}"):
                name = st.text_input("Nome", value=f.name)
                desc = st.text_area("Descrizione", value=f.description or "")
                dur = st.number_input("Durata giorni", min_value=1, value=f.default_duration_days or 1)
                save = st.form_submit_button("Salva")
                cancel = st.form_submit_button("Annulla")
                if save:
                    utils.update_format(f.id, name=name, description=desc, default_duration_days=dur)
                    st.success("Aggiornato")
                    st.session_state.edit_format_id = None
                    st.experimental_rerun()
                if cancel:
                    st.session_state.edit_format_id = None
                    st.experimental_rerun()

if admin_section == "Promoter":
    st.header("Gestione Promoter")
    if st.button("Nuovo promoter"):
        st.session_state.show_new_promoter = True
    if st.session_state.get("show_new_promoter"):
        with st.form("new_promoter"):
            name = st.text_input("Nome promoter")
            contact = st.text_input("Contatto")
            submitted = st.form_submit_button("Crea")
            if submitted:
                utils.create_promoter(name=name, contact=contact)
                st.success("Promoter creato")
                st.session_state.show_new_promoter = False
                st.experimental_rerun()
    promoters = utils.list_promoters()
    for p in promoters:
        st.write(f"**{p.name}**  •  {p.contact or '-'}")
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button(f"Modifica_promoter_{p.id}", key=f"edit_promoter_{p.id}"):
                st.session_state.edit_promoter_id = p.id
                st.experimental_rerun()
        with c2:
            if st.button(f"Elimina_promoter_{p.id}", key=f"del_promoter_{p.id}"):
                utils.delete_promoter(p.id)
                st.success("Promoter eliminato")
                st.experimental_rerun()
    if st.session_state.get("edit_promoter_id"):
        pid = st.session_state.edit_promoter_id
        p = utils.get_promoter(pid)
        if p:
            with st.form(f"form_edit_promoter_{p.id}"):
                name = st.text_input("Nome", value=p.name)
                contact = st.text_input("Contatto", value=p.contact or "")
                save = st.form_submit_button("Salva")
                cancel = st.form_submit_button("Annulla")
                if save:
                    utils.update_promoter(p.id, name=name, contact=contact)
                    st.success("Aggiornato")
                    st.session_state.edit_promoter_id = None
                    st.experimental_rerun()
                if cancel:
                    st.session_state.edit_promoter_id = None
                    st.experimental_rerun()

if admin_section == "Risorse (DJ/Vocalist/Ballerine)":
    st.header("Gestione Risorse (DJ, Vocalist, Ballerine, Service, Tour Manager, Mascotte)")
    resource_types = ["DJ", "Vocalist", "Ballerina", "Service", "Tour Manager", "Mascotte"]
    with st.expander("Crea nuova risorsa"):
        with st.form("new_resource"):
            name = st.text_input("Nome")
            rtype = st.selectbox("Tipo", resource_types)
            contact = st.text_input("Contatto")
            availability = st.text_area("Disponibilità (note)")
            submitted = st.form_submit_button("Crea")
            if submitted:
                utils.create_resource(name=name, type=rtype, contact=contact, availability=availability)
                st.success("Risorsa creata")
                st.experimental_rerun()
    sel_type = st.selectbox("Filtra per tipo", ["Tutti"] + resource_types)
    resources = utils.list_resources(None if sel_type == "Tutti" else sel_type)
    for r in resources:
        st.write(f"**{r.name}**  •  {r.type}  •  {r.contact or '-'}")
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button(f"Modifica_res_{r.id}", key=f"edit_res_{r.id}"):
                st.session_state.edit_resource_id = r.id
                st.experimental_rerun()
        with c2:
            if st.button(f"Elimina_res_{r.id}", key=f"del_res_{r.id}"):
                utils.delete_resource(r.id)
                st.success("Risorsa eliminata")
                st.experimental_rerun()
    if st.session_state.get("edit_resource_id"):
        rid = st.session_state.edit_resource_id
        r = utils.get_resource(rid)
        if r:
            with st.form(f"form_edit_resource_{r.id}"):
                name = st.text_input("Nome", value=r.name)
                rtype = st.selectbox("Tipo", resource_types, index=resource_types.index(r.type) if r.type in resource_types else 0)
                contact = st.text_input("Contatto", value=r.contact or "")
                availability = st.text_area("Disponibilità", value=r.availability or "")
                save = st.form_submit_button("Salva")
                cancel = st.form_submit_button("Annulla")
                if save:
                    utils.update_resource(r.id, name=name, type=rtype, contact=contact, availability=availability)
                    st.success("Aggiornato")
                    st.session_state.edit_resource_id = None
                    st.experimental_rerun()
                if cancel:
                    st.session_state.edit_resource_id = None
                    st.experimental_rerun()

# -------------------------
# Footer / tips
# -------------------------
st.markdown("---")
st.markdown(
    """
    **Tip rapidi:**  
    - Usa i filtri nella sidebar per isolare Artisti o Format.  
    - Crea eventi rapidamente con "Nuovo Evento".  
    - Gestisci anagrafiche in Admin per mantenere il calendario pulito.
    """
)
