import streamlit as st
import pandas as pd
import fastf1

# --- UI Configuration ---
st.set_page_config(page_title="F1 Fantasy", layout="wide")
st.title("🏎️ Fantasy Battle: 2026 Season")

# --- Define Your Lineups ---
steven_lineup = ["HAM", "LEC", "RUS", "LIN", "BOR", "HAD", "SAI", "GAS"]
vanessa_lineup = ["NOR", "PIA", "VER", "BEA", "ANT", "ALB", "LAW", "NOR"]

# --- Automated Data Fetching ---
@st.cache_data(ttl=3600)
def get_latest_f1_data(year):
    try:
        schedule = fastf1.get_event_schedule(year)
        now = pd.Timestamp.now().tz_localize(None)
        # Filter for races that have already started
        past_races = schedule[schedule['EventDate'] <= now]
        if past_races.empty:
            return None, "Season hasn't started yet!"
        
        latest_event = past_races.iloc[-1]
        session = fastf1.get_session(year, latest_event['EventName'], 'R')
        session.load(telemetry=False, weather=False, messages=False)
        return session.results[['Abbreviation', 'Points']], latest_event['EventName']
    except Exception as e:
        return None, str(e)

# --- Display Logic ---
results_df, current_race = get_latest_f1_data(2026)

if results_df is not None:
    st.subheader(f"Results for: {current_race}")
    points_map = dict(zip(results_df['Abbreviation'], results_df['Points']))
    
    # Calculate scores
    s_score = sum(points_map.get(d, 0) for d in steven_lineup)
    v_score = sum(points_map.get(d, 0) for d in vanessa_lineup)
    
    col1, col2 = st.columns(2)
    col1.metric("Steven's Total", int(s_score))
    col2.metric("Vanessa's Total", int(v_score))
    
    if s_score > v_score: st.success("Steven is winning!")
    elif v_score > s_score: st.success("Vanessa is winning!")
else:
    st.warning("Waiting for race data...")