# components/calendar_widget.py
# Placeholder: componente calendario semplice. Puoi sostituire con FullCalendar via componente custom.
import streamlit as st
import calendar
from datetime import date

def render_month(year, month, events, open_callback_key_prefix="open"):
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")
                else:
                    st.markdown(f"**{day}**")
                    d = date(year, month, day)
                    day_events = [e for e in events if e.date == d]
                    for ev in day_events:
                        st.markdown(f"- **{ev.title}**  •  _{ev.status}_")
                        if st.button("Apri", key=f"{open_callback_key_prefix}_{ev.id}"):
                            st.session_state.open_event_id = ev.id
                            try:
                                st.experimental_rerun()
                            except Exception:
                                st.experimental_set_query_params(_rerun=str(date.today().isoformat()))
