import streamlit as st
import pandas as pd
import fastf1
import plotly.express as px

# --- Define Your Lineups ---
steven_lineup = ["HAM", "LEC", "RUS", "LIN", "BOR", "HAD", "SAI", "GAS"]
vanessa_lineup = ["NOR", "PIA", "VER", "BEA", "ANT", "ALB", "LAW", "NOR"]

# --- Function to Get All Points to Date ---
@st.cache_data(ttl=3600)
def get_season_points():
    schedule = fastf1.get_event_schedule(2026)
    now = pd.Timestamp.now().tz_localize(None)
    past_races = schedule[schedule['EventDate'] <= now]
    
    history_data = []
    
    for _, race in past_races.iterrows():
        try:
            session = fastf1.get_session(2026, race['EventName'], 'R')
            session.load(telemetry=False, weather=False, messages=False)
            results = session.results[['Abbreviation', 'Points']]
            points_map = dict(zip(results['Abbreviation'], results['Points']))
            
            history_data.append({
                'Race': race['EventName'],
                'Steven': sum(points_map.get(d, 0) for d in steven_lineup),
                'Vanessa': sum(points_map.get(d, 0) for d in vanessa_lineup)
            })
        except:
            continue
            
    return pd.DataFrame(history_data)

# --- Display Logic ---
st.title("🏆 2026 F1 Fantasy: Live Tracker")
df = get_season_points()

if not df.empty:
    df['Steven_Total'] = df['Steven'].cumsum()
    df['Vanessa_Total'] = df['Vanessa'].cumsum()
    
    st.table(df)
    
    fig = px.line(df, x='Race', y=['Steven_Total', 'Vanessa_Total'], 
                  markers=True, title="Cumulative Season Points")
    st.plotly_chart(fig)
else:
    st.warning("No race data available yet.")
