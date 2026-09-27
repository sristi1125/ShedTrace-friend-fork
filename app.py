import base64
from pathlib import Path

import pandas as pd
import streamlit as st
from pipeline import (
    load_data,
    get_building_report,
    get_building_report_by_bin,
    get_map_context,
    SHED_LAT_COL,
    SHED_LON_COL,
)
from ai_chat import ask_ai
import map_view

LOGO_PATH = Path(__file__).parent / "assets" / "shedtrace_logo.png"
LOGO_B64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()

st.set_page_config(page_title="ShedTrace", page_icon=str(LOGO_PATH))


# ============================================================
# CUSTOM CSS — APPLE-INSPIRED THEME
# ============================================================

st.html("""
<style>

/* ============================================================
   TOKENS
   ============================================================ */

:root {
    --bg: #FFFFFF;
    --bg-subtle: #F5F5F7;
    --text: #1D1D1F;
    --text-secondary: #86868B;
    --accent: #0071E3;
    --accent-hover: #0077ED;
    --accent-active: #006EDB;
    --hairline: #D2D2D7;
}


/* ============================================================
   GLOBAL
   ============================================================ */

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
                 "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
}

.stApp {
    background-color: var(--bg);
    color: var(--text);
}

[data-testid="stMainBlockContainer"] {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
}

footer {
    visibility: hidden;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    padding: 3rem 0 2.5rem 0;
    text-align: center;
    animation: rise 0.7s ease-out;
}

.hero-title {
    font-size: 3.4rem;
    font-weight: 600;
    letter-spacing: -0.03em;
    line-height: 1.02;
    color: var(--text);
}

.hero-title .accent {
    color: var(--accent);
}

.hero-logo {
    height: 96px !important;
    width: auto !important;
    max-width: none !important;
    display: block;
    margin: 0 auto;
}

.hero-subtitle {
    margin: 0.9rem auto 0;
    color: var(--text-secondary);
    font-size: 1.1rem;
    font-weight: 400;
    line-height: 1.5;
}

@keyframes rise {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
    .hero { animation: none; }
}


/* ============================================================
   SEARCH
   ============================================================ */

.search-label {
    color: var(--text-secondary);
    font-size: 0.95rem;
    font-weight: 400;
    margin-bottom: 0.5rem;
}


/* ============================================================
   CASE HEADER
   ============================================================ */

.case-header {
    background: var(--bg-subtle);
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    margin: 2rem 0 1.25rem;
}

.case-kicker {
    color: var(--text-secondary);
    font-size: 0.85rem;
    font-weight: 400;
}

.case-address {
    color: var(--text);
    font-size: 1.4rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-top: 0.2rem;
}


/* ============================================================
   MAP
   ============================================================ */

.map-note {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 0.9rem;
}


/* ============================================================
   METRICS
   ============================================================ */

[data-testid="stMetric"] {
    background: var(--bg-subtle);
    border-radius: 18px;
    padding: 1.3rem 1.4rem;
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary);
    font-size: 0.85rem;
    font-weight: 400;
}

[data-testid="stMetricValue"] {
    color: var(--text);
    font-weight: 600;
}


/* ============================================================
   SECTION HEADERS
   ============================================================ */

.section-header {
    margin-top: 0.5rem;
    margin-bottom: 1rem;
    color: var(--text);
    font-size: 1.3rem;
    font-weight: 600;
    letter-spacing: -0.015em;
}


/* ============================================================
   TABS (segmented control)
   ============================================================ */

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 2px;
    background: var(--bg-subtle);
    border-radius: 12px;
    padding: 4px;
}

[data-testid="stTabs"] button[data-baseweb="tab"] {
    height: 40px;
    color: var(--text-secondary);
    font-weight: 500;
    border-radius: 9px;
    background: transparent;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--text);
    background: var(--bg);
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background: transparent;
}

[data-testid="stTabs"] [data-baseweb="tab-border"] {
    background: transparent;
}


/* ============================================================
   INPUTS
   ============================================================ */

div[data-testid="stTextInput"] input {
    background-color: var(--bg-subtle);
    color: var(--text);
    border: none;
    border-radius: 12px;
    min-height: 48px;
    font-size: 1.05rem;
}

div[data-testid="stTextInput"] input:focus {
    box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.35);
}

div[data-testid="stTextInput"] input::placeholder {
    color: var(--text-secondary);
}


/* ============================================================
   BUTTON
   ============================================================ */

.stButton > button {
    background-color: var(--accent);
    color: #FFFFFF;
    border: none;
    border-radius: 980px;
    min-height: 48px;
    font-weight: 500;
    transition: background-color 0.15s ease;
}

.stButton > button:hover {
    background-color: var(--accent-hover);
    color: #FFFFFF;
    border: none;
}

.stButton > button:active {
    background-color: var(--accent-active);
}

.stButton > button:focus-visible {
    color: #FFFFFF;
    border: none;
    box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.35);
}


/* ============================================================
   EXPANDER
   ============================================================ */

[data-testid="stExpander"] {
    background-color: var(--bg-subtle);
    border: none;
    border-radius: 14px;
}

[data-testid="stExpander"] summary {
    color: var(--text);
}


/* ============================================================
   ALERTS & CAPTIONS
   ============================================================ */

[data-testid="stAlert"] {
    border-radius: 14px;
}

[data-testid="stCaptionContainer"] {
    color: var(--text-secondary);
}


/* ============================================================
   DIVIDERS
   ============================================================ */

hr {
    border-color: var(--hairline);
}


/* ============================================================
   DEPLOY / TOOLBAR
   ============================================================ */

[data-testid="stToolbar"] button[aria-label*="Deploy"] {
    color: var(--accent) !important;
}

[data-testid="stToolbar"] button[aria-label*="Deploy"] svg {
    color: var(--accent) !important;
    fill: var(--accent) !important;
    stroke: var(--accent) !important;
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 768px) {
    .hero-title {
        font-size: 2.4rem;
    }
    .hero-logo {
        height: 68px;
    }
}

</style>
""")


# ============================================================
# HERO
# ============================================================

st.html(f"""
<div class="hero">
    <img class="hero-logo" style="height:96px !important; width:auto !important; max-width:none !important; display:block; margin:0 auto;" src="data:image/png;base64,{LOGO_B64}" alt="ShedTrace" />
    <div class="hero-subtitle">
        The paper trail behind every shed.
    </div>
</div>
""")


# ============================================================
# DATA
# ============================================================

@st.cache_data
def get_data():
    return load_data()

sheds, violations, complaints, elevator, fire = get_data()


# ============================================================
# SEARCH
# ============================================================

st.html("""
<div class="search-label">
    Search an address
</div>
""")

address = st.text_input("Address", placeholder="e.g. 350 5th Avenue, Manhattan", label_visibility="collapsed")

if st.button("Investigate Building") and address:
    report = get_building_report(address, sheds, violations, complaints, elevator, fire)
    st.session_state["report"] = report
    st.session_state["address"] = address

report = st.session_state.get("report")
saved_address = st.session_state.get("address")

if report is None and address:
    st.warning("No sidewalk shed currently found at that address.")

if report is not None:
    shed = report["shed"]

    st.html(f"""
    <div class="case-header">
        <div class="case-kicker">Active investigation</div>
        <div class="case-address">📍 {report['address']}</div>
    </div>
    """)

    col1, col2, col3 = st.columns(3)
    col1.metric("Shed active for", f"{shed['duration_years']} yrs")
    col2.metric("Open violations", report["open_violation_count"])
    col3.metric("Complaints filed", report["complaint_count"])

    st.caption(f"Permit renewals: {shed['renewal_count']}")

    if SHED_LAT_COL in sheds.columns and SHED_LON_COL in sheds.columns:
        st.html('<div class="section-header">Shed Landscape</div>')
        map_df = get_map_context(report["bin"], sheds, violations, complaints)

        if map_df is None or map_df.empty:
            st.info("Couldn't place this building on the map (missing or invalid coordinates).")
        else:
            st.html("""
            <div class="map-note">
                🥇 Gold = selected building &nbsp;·&nbsp;
                Height = shed duration &nbsp;·&nbsp;
                Color = severity &nbsp;·&nbsp;
                Click a building to investigate it
            </div>
            """)

            deck = map_view.build_deck(map_df)

            with st.container(border=True):
                event = st.pydeck_chart(
                    deck,
                    on_select="rerun",
                    selection_mode="single-object",
                    key="shed_map",
                    height=550,
                )

            clicked_bin = map_view.get_clicked_bin(event)

            if clicked_bin and clicked_bin != report["bin"]:
                new_report = get_building_report_by_bin(
                    clicked_bin, sheds, violations, complaints, elevator, fire
                )
                if new_report is not None:
                    st.session_state["report"] = new_report
                    st.session_state["address"] = new_report["address"]
                    st.rerun()
    else:
        st.info(
            f"Map hidden: couldn't find {SHED_LAT_COL!r}/{SHED_LON_COL!r} in your "
            "sidewalk shed CSV. Update SHED_LAT_COL/SHED_LON_COL in pipeline.py "
            "to match your real column names. Columns found: "
            + ", ".join(sheds.columns)
        )

    tab_shed, tab_elevator, tab_fire, tab_ai = st.tabs(
        ["🏗️ Shed Timeline", "🛗 Elevator Safety", "🔥 Fire Safety", "🤖 Ask AI"]
    )

    with tab_shed:
        st.html('<div class="section-header">Evidence Timeline</div>')

        timeline = report["timeline"]
        MAX_SHOWN = 15

        if len(timeline) > MAX_SHOWN:
            st.caption(
                f"Showing the {MAX_SHOWN} most recent of {len(timeline)} total events."
            )
            shown = timeline[-MAX_SHOWN:]
        else:
            shown = timeline

        for date, label in shown:
            st.write(f"**{date.date()}** — {label}")

        if len(timeline) > MAX_SHOWN:
            with st.expander(f"Show all {len(timeline)} events"):
                for date, label in timeline:
                    st.write(f"**{date.date()}** — {label}")

    with tab_elevator:
        elevator_records = report["elevator_records"]
        if not elevator_records:
            st.info("No elevator safety records found for this building.")
        else:
            st.write(f"**{len(elevator_records)} elevator device(s) on file**")
            for e in elevator_records:
                inspected = (
                    e["last_inspection"].date()
                    if pd.notnull(e["last_inspection"])
                    else "Unknown"
                )
                cat1_filed = (
                    e["last_cat1_filed"].date()
                    if pd.notnull(e["last_cat1_filed"])
                    else "Unknown"
                )
                st.write(
                    f"- **{e['device_type']}** (Device #{e['device_number']}) — "
                    f"Status: {e['status']} — Last inspected: {inspected}"
                )

                with st.expander(f"View elevator history — Device #{e['device_number']}"):
                    st.write(f"**Current status:** {e['status']}")
                    st.write(f"**Last periodic inspection:** {inspected}")
                    st.write(f"**Last CAT1 report filed:** {cat1_filed}")

                    elev_violations = report["elevator_related_violations"]
                    elev_complaints = report["elevator_related_complaints"]

                    st.write(f"**Elevator-related violations:** {len(elev_violations)}")
                    for v in elev_violations:
                        date = v["date"].date() if pd.notnull(v["date"]) else "Unknown"
                        st.write(f"  - {date}: {v['description']}")

                    st.write(f"**Elevator-related complaints:** {len(elev_complaints)}")
                    for c in elev_complaints:
                        date = c["date"].date() if pd.notnull(c["date"]) else "Unknown"
                        st.write(f"  - {date}: {c['type_label']}")

    with tab_fire:
        fire_records = report["fire_records"]
        if not fire_records:
            st.info("No fire safety inspection records found for this building.")
        else:
            st.write(f"**{len(fire_records)} fire inspection record(s) on file**")
            for f in fire_records:
                visited = (
                    f["last_visit"].date()
                    if pd.notnull(f["last_visit"])
                    else "Unknown"
                )
                st.write(
                    f"- Status: **{f['status']}** — Last visit: {visited}"
                )

            with st.expander("View fire safety history"):
                fire_violations = report["fire_related_violations"]
                fire_complaints = report["fire_related_complaints"]

                st.write(f"**Fire-related violations:** {len(fire_violations)}")
                for v in fire_violations:
                    date = v["date"].date() if pd.notnull(v["date"]) else "Unknown"
                    st.write(f"  - {date}: {v['description']}")

                st.write(f"**Fire-related complaints:** {len(fire_complaints)}")
                for c in fire_complaints:
                    date = c["date"].date() if pd.notnull(c["date"]) else "Unknown"
                    st.write(f"  - {date}: {c['type_label']}")

    with tab_ai:
        st.html(f'<div class="section-header">Ask about {report["address"]}</div>')
        st.caption("This assistant only knows the real data shown in the other tabs for this building.")

        question = st.text_input("Ask a question:", key="ai_question")
        if st.button("Ask", key="ai_ask_button") and question:
            with st.spinner("Thinking..."):
                try:
                    answer = ask_ai(saved_address, report, question)
                    st.write(answer)
                except Exception as e:
                    st.error(f"Something went wrong talking to Gemini: {e}")