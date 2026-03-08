import streamlit as st
import pandas as pd
import fastf1
import plotly.express as px

# --- UI Configuration ---
st.set_page_config(page_title="2026 F1 Fantasy Battle", layout="wide")
st.title("🏎️ 2026 F1 Fantasy: Live Tracker")

# --- Driver Data (Updated with all 16 unique drivers) ---
driver_info = {
    "HAM": {"name": "Lewis Hamilton", "img": "https://www.formula1.com/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png"},
    "LEC": {"name": "Charles Leclerc", "img": "https://www.formula1.com/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png"},
    "RUS": {"name": "George Russell", "img": "https://www.formula1.com/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png"},
    "NOR": {"name": "Lando Norris", "img": "https://www.formula1.com/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png"},
    "PIA": {"name": "Oscar Piastri", "img": "https://www.formula1.com/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png"},
    "VER": {"name": "Max Verstappen", "img": "https://www.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png"},
    "LIN": {"name": "Arvid Lindblad", "img": "https://www.formula1.com/content/dam/fom-website/drivers/A/ARVLIN01_Arvid_Lindblad/arvlin01.png"},
    "BOR": {"name": "Gabriel Bortoleto", "img": "https://www.formula1.com/content/dam/fom-website/drivers/G/GABBOR01_Gabriel_Bortoleto/gabbor01.png"},
    "HAD": {"name": "Isack Hadjar", "img": "https://www.formula1.com/content/dam/fom-website/drivers/I/ISAHAD01_Isack_Hadjar/isahad01.png"},
    "SAI": {"name": "Carlos Sainz", "img": "https://www.formula1.com/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png"},
    "GAS": {"name": "Pierre Gasly", "img": "https://www.formula1.com/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png"},
    "BEA": {"name": "Oliver Bearman", "img": "https://www.formula1.com/content/dam/fom-website/drivers/O/OLIBEA01_Oliver_Bearman/olibea01.png"},
    "ANT": {"name": "Kimi Antonelli", "img": "https://www.formula1.com/content/dam/fom-website/drivers/A/KINANT01_Kimi_Antonelli/kinant01.png"},
    "ALB": {"name": "Alex Albon", "img": "https://www.formula1.com/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png"},
    "LAW": {"name": "Liam Lawson", "img": "https://www.formula1.com/content/dam/fom-website/drivers/L/LIALAW01_Liam_Lawson/lialaw01.png"},
}

# --- Define Your Lineups ---
steven_lineup = ["HAM", "LEC", "RUS", "LIN", "BOR", "HAD", "SAI", "GAS"]
vanessa_lineup = ["NOR", "PIA", "VER", "BEA", "ANT", "ALB", "LAW", "NOR"]

# --- Function to Get All Points ---
@st.cache_data(ttl=3600)
def get_season_points():
    schedule = fastf1.get_event_schedule(2026)
    now = pd.Timestamp.now().tz_localize(None)
    past_events = schedule[(schedule['EventDate'] <= now) & (~schedule['EventFormat'].str.contains('testing', case=False, na=False))]
    
    history_data = []
    for _, event in past_events.iterrows():
        try:
            session = fastf1.get_session(2026, event['EventName'], 'R')
            session.load(telemetry=False, weather=False, messages=False)
            results = session.results[['Abbreviation', 'Points']]
            points_map = dict(zip(results['Abbreviation'], results['Points']))
            
            history_data.append({
                'Race': event['EventName'],
                'Steven': sum(points_map.get(d, 0) for d in steven_lineup),
                'Vanessa': sum(points_map.get(d, 0) for d in vanessa_lineup)
            })
        except Exception:
            continue
    return pd.DataFrame(history_data)

# --- Tabs for Layout ---
tab1, tab2 = st.tabs(["📊 Live Standings", "👤 Team Lineups"])

with tab1:
    df = get_season_points()
    if not df.empty:
        df['Steven Total'] = df['Steven'].cumsum()
        df['Vanessa Total'] = df['Vanessa'].cumsum()
        st.table(df[['Race', 'Steven Total', 'Vanessa Total']])
        fig = px.line(df, x='Race', y=['Steven Total', 'Vanessa Total'], markers=True, title="Cumulative Season Points")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No race data available yet.")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Steven's Drivers")
        for code in steven_lineup:
            d = driver_info.get(code, {"name": code, "img": "https://via.placeholder.com/50"})
            row_col1, row_col2 = st.columns([0.5, 4])
            row_col1.image(d["img"], width=50)
            row_col2.write(f"**{d['name']}**")
    with col2:
        st.subheader("Vanessa's Drivers")
        for code in vanessa_lineup:
            d = driver_info.get(code, {"name": code, "img": "https://via.placeholder.com/50"})
            row_col1, row_col2 = st.columns([0.5, 4])
            row_col1.image(d["img"], width=50)
            row_col2.write(f"**{d['name']}**")
