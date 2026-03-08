import streamlit as st
import pandas as pd
import fastf1
import plotly.express as px

# --- UI Configuration ---
st.set_page_config(page_config="wide")
st.title("🏎️ 2026 F1 Fantasy: Live Tracker")

# --- Define Your Lineups ---
steven_lineup = ["HAM", "LEC", "RUS", "LIN", "BOR", "HAD", "SAI", "GAS"]
vanessa_lineup = ["NOR", "PIA", "VER", "BEA", "ANT", "ALB", "LAW", "NOR"]

# --- Function to Get All Points to Date ---
@st.cache_data(ttl=3600)
def get_season_points():
    schedule = fastf1.get_event_schedule(2026)
    now = pd.Timestamp.now().tz_localize(None)
    
    # Filter for past races, explicitly excluding testing
    past_events = schedule[(schedule['EventDate'] <= now) & (~schedule.is_testing())]
    
    history_data = []
    
    for _, event in past_events.iterrows():
        try:
            # Load the Race session specifically
            session = fastf1.get_session(2026, event['EventName'], 'R')
            session.load(telemetry=False, weather=False, messages=False)
            results = session.results[['Abbreviation', 'Points']]
            points_map = dict(zip(results['Abbreviation'], results['Points']))
            
            history_data.append({
                'Race': event['EventName'],
                'Steven': sum(points_map.get(d, 0) for d in steven_lineup),
                'Vanessa': sum(points_map.get(d, 0) for d in vanessa_lineup)
            })
        except:
            continue
            
    return pd.DataFrame(history_data)

# --- Display Logic ---
df = get_season_points()

if not df.empty:
    # Calculate running totals
    df['Steven Total'] = df['Steven'].cumsum()
    df['Vanessa Total'] = df['Vanessa'].cumsum()
    
    # Display only the requested columns
    st.table(df[['Race', 'Steven Total', 'Vanessa Total']])
    
    # Plotting
    fig = px.line(df, x='Race', y=['Steven Total', 'Vanessa Total'], 
                  markers=True, title="Cumulative Season Points")
    st.plotly_chart(fig)
else:
    st.warning("No race data available yet.")
