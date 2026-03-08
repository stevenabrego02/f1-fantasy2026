import streamlit as st
import pandas as pd
import fastf1
import plotly.express as px

# --- UI Configuration ---
st.set_page_config(page_title="2026 F1 Fantasy Battle", layout="wide")
st.title("🏎️ 2026 F1 Fantasy: Live Tracker")

# --- Driver Data ---
driver_info = {
    "HAM": {"name": "Lewis Hamilton", "img": "https://www.formula1.com/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png"},
    "LEC": {"name": "Charles Leclerc", "img": "https://www.formula1.com/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png"},
    "RUS": {"name": "George Russell", "img": "https://media.formula1.com/image/upload/c_fill,w_80,h_80,g_north/q_auto/d_common:f1:2026:fallback:driver:2026fallbackdriverright.webp/v1740000000/common/f1/2026/mercedes/georus01/2026mercedesgeorus01right.webp"},
    "NOR": {"name": "Lando Norris", "img": "https://www.formula1.com/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png"},
    "PIA": {"name": "Oscar Piastri", "img": "https://www.formula1.com/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png"},
    "VER": {"name": "Max Verstappen", "img": "https://www.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png"},
    "LIN": {"name": "Arvid Lindblad", "img": "https://media.formula1.com/image/upload/c_fill,w_80,h_80,g_north/q_auto/d_common:f1:2026:fallback:driver:2026fallbackdriverright.webp/v1740000000/common/f1/2026/racingbulls/arvlin01/2026racingbullsarvlin01right.webp"},
    "BOR": {"name": "Gabriel Bortoleto", "img": "https://www.formula1.com/content/dam/fom-website/drivers/G/GABBOR01_Gabriel_Bortoleto/gabbor01.png"},
    "HAD": {"name": "Isack Hadjar", "img": "https://www.formula1.com/content/dam/fom-website/drivers/I/ISAHAD01_Isack_Hadjar/isahad01.png"},
    "SAI": {"name": "Carlos Sainz", "img": "https://www.formula1.com/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png"},
    "GAS": {"name": "Pierre Gasly", "img": "https://www.formula1.com/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png"},
    "BEA": {"name": "Oliver Bearman", "img": "https://www.formula1.com/content/dam/fom-website/drivers/O/OLIBEA01_Oliver_Bearman/olibea01.png"},
    "ANT": {"name": "Kimi Antonelli", "img": "https://media.formula1.com/image/upload/c_fill,w_80,h_80,g_north/q_auto/d_common:f1:2026:fallback:driver:2026fallbackdriverright.webp/v1740000000/common/f1/2026/mercedes/andant01/2026mercedesandant01right.webp"},
    "ALB": {"name": "Alex Albon", "img": "https://www.formula1.com/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png"},
    "LAW": {"name": "Liam Lawson", "img": "https://www.formula1.com/content/dam/fom-website/drivers/L/LIALAW01_Liam_Lawson/lialaw01.png"},
    "HUL": {"name": "Nico Hulkenberg", "img": "https://media.formula1.com/image/upload/c_fill,w_80,h_80,g_north/q_auto/d_common:f1:2026:fallback:driver:2026fallbackdriverright.webp/v1740000000/common/f1/2026/audi/nichul01/2026audinichul01right.webp"},
}

# --- Lineups ---
steven_lineup = ["HAM", "LEC", "RUS", "LIN", "BOR", "HAD", "SAI", "GAS"]
vanessa_lineup = ["NOR", "PIA", "VER", "BEA", "ANT", "ALB", "LAW", "HUL"]

@st.cache_data(ttl=3600)
def get_season_points():
    schedule = fastf1.get_event_schedule(2026)
    now = pd.Timestamp.now().tz_localize(None)
    past_events = schedule[(schedule['EventDate'] <= now) & (~schedule['EventFormat'].str.contains('testing', case=False, na=False))]
    history_data = []
    for _, event in past_events.iterrows():
        try:
            # We assume 'R' for race; you could expand this to include 'S' for sprint
            session = fastf1.get_session(2026, event['EventName'], 'R')
            session.load(telemetry=False, weather=False, messages=False)
            results = session.results[['Abbreviation', 'Points']]
            points_map = dict(zip(results['Abbreviation'], results['Points']))
            history_data.append({'Race': event['EventName'], 'Steven': sum(points_map.get(d, 0) for d in steven_lineup), 'Vanessa': sum(points_map.get(d, 0) for d in vanessa_lineup)})
        except: continue
    return pd.DataFrame(history_data)

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Live Standings", "👤 Team Lineups", "📑 Spreadsheet View"])

with tab1:
    df = get_season_points()
    if not df.empty:
        df['Steven Total'] = df['Steven'].cumsum()
        df['Vanessa Total'] = df['Vanessa'].cumsum()
        fig = px.line(df, x='Race', y=['Steven Total', 'Vanessa Total'], markers=True, title="Cumulative Season Points",
                      color_discrete_map={"Steven Total": "red", "Vanessa Total": "blue"})
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("No data available.")

with tab2:
    col1, col2 = st.columns(2)
    for name, lineup, col in [("Steven", steven_lineup, col1), ("Vanessa", vanessa_lineup, col2)]:
        with col:
            st.subheader(f"{name}'s Drivers")
            for code in lineup:
                d = driver_info.get(code, {"name": code, "img": "https://via.placeholder.com/35"})
                c1, c2 = st.columns([0.3, 5])
                c1.image(d["img"], width=35)
                c2.markdown(f"<small>{d['name']}</small>", unsafe_allow_html=True)

with tab3:
    st.subheader("Steven's Driver List")
    steven_df = pd.DataFrame([driver_info.get(d, {"name": d, "img": ""}) for d in steven_lineup])
    st.dataframe(steven_df, column_config={"img": st.column_config.ImageColumn("Photo")})
    st.subheader("Vanessa's Driver List")
    vanessa_df = pd.DataFrame([driver_info.get(d, {"name": d, "img": ""}) for d in vanessa_lineup])
    st.dataframe(vanessa_df, column_config={"img": st.column_config.ImageColumn("Photo")})
