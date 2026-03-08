import streamlit as st
import pandas as pd
import fastf1
import plotly.express as px

# --- UI Configuration ---
st.set_page_config(page_title="2026 F1 Fantasy Battle", layout="wide")

st.title("🏎️ 2026 F1 Fantasy: Live Tracker")

# --- Setup Driver Data ---
# Add your preferred image URLs here. 
# Using a dictionary allows you to map abbreviations to their names and photos.
driver_info = {
    "HAM": {"name": "Lewis Hamilton", "img": "https://upload.wikimedia.org/wikipedia/commons/1/18/Lewis_Hamilton_2016_Malaysia_2.jpg"},
    "LEC": {"name": "Charles Leclerc", "img": "https://upload.wikimedia.org/wikipedia/commons/0/05/Charles_Leclerc_2019_Bahrain.jpg"},
    "RUS": {"name": "George Russell", "img": "https://upload.wikimedia.org/wikipedia/commons/1/18/George_Russell_2022.jpg"},
    "NOR": {"name": "Lando Norris", "img": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Lando_Norris_2022.jpg"},
    # Add all other drivers in your 8-driver pools here!
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
            d = driver_info.get(code, {"name": code, "img": "https://via.placeholder.com/150"})
            row_col1, row_col2 = st.columns([1, 3])
            row_col1.image(d["img"], width=80)
            row_col2.write(f"**{d['name']}** ({code})")
    with col2:
        st.subheader("Vanessa's Drivers")
        for code in vanessa_lineup:
            d = driver_info.get(code, {"name": code, "img": "https://via.placeholder.com/150"})
            row_col1, row_col2 = st.columns([1, 3])
            row_col1.image(d["img"], width=80)
            row_col2.write(f"**{d['name']}** ({code})")
