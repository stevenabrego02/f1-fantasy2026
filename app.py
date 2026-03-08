import streamlit as st
import pandas as pd
import fastf1
import plotly.express as px

# --- UI Configuration ---
st.set_page_config(page_title="2026 F1 Fantasy Battle", layout="wide")
st.title("🏎️ 2026 F1 Fantasy: Live Tracker")

# --- Custom CSS for HTML Tables ---
st.markdown("""
<style>
    .f1-table-container { overflow-x: auto; margin-bottom: 2rem; }
    .f1-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 14px; }
    .f1-table td { border: 1px solid #444; padding: 8px; text-align: center; white-space: nowrap; }
    
    /* Vertical Column Headers */
    .f1-table th { 
        border: 1px solid #444; 
        padding: 10px 8px; 
        text-align: center; 
        white-space: nowrap;
    }
    .f1-table th:not(:first-child) {
        writing-mode: vertical-rl;
        transform: rotate(180deg);
        height: 160px; /* Gives enough room for long sprint/race names */
        vertical-align: bottom;
    }

    /* Sticky First Column */
    .f1-table td:first-child, .f1-table th:first-child { 
        text-align: left; 
        position: sticky; 
        left: 0; 
        background-color: #0e1117; 
        z-index: 1; 
        min-width: 160px; 
    }
    
    /* Bold Bottom Row */
    .f1-table tr:last-child { font-weight: bold; background-color: #1e2530; }
</style>
""", unsafe_allow_html=True)

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

# --- Automated Data Fetching ---
@st.cache_data(ttl=3600)
def fetch_season_data():
    schedule = fastf1.get_event_schedule(2026)
    events = schedule[~schedule['EventFormat'].str.contains('testing', case=False, na=False)]
    
    points_dict = {}
    all_sessions = []
    now = pd.Timestamp.now().tz_localize(None)
    
    for _, event in events.iterrows():
        event_name = event['EventName']
        is_sprint = str(event['EventFormat']).lower() in ['sprint', 'sprint_qualifying', 'sprint_shootout']
        
        # 1. Fetch Sprint (if applicable)
        if is_sprint:
            sprint_name = f"{event_name} (Sprint)"
            all_sessions.append(sprint_name)
            if event['EventDate'] <= now:
                try:
                    session = fastf1.get_session(2026, event_name, 'S')
                    session.load(telemetry=False, weather=False, messages=False)
                    res = session.results[['Abbreviation', 'Points']]
                    points_dict[sprint_name] = dict(zip(res['Abbreviation'], res['Points']))
                except: pass
        
        # 2. Fetch Race
        race_name = f"{event_name} (Race)"
        all_sessions.append(race_name)
        if event['EventDate'] <= now:
            try:
                session = fastf1.get_session(2026, event_name, 'R')
                session.load(telemetry=False, weather=False, messages=False)
                res = session.results[['Abbreviation', 'Points']]
                points_dict[race_name] = dict(zip(res['Abbreviation'], res['Points']))
            except: pass
            
    all_sessions.append("Total")
    return all_sessions, points_dict

def generate_html_spreadsheet(lineup, points_dict, all_sessions):
    rows = []
    for code in lineup:
        d = driver_info.get(code, {"name": code, "img": ""})
        # Combine image and name in HTML
        driver_cell = f"<div style='display:flex; align-items:center;'><img src='{d['img']}' width='35' style='margin-right:10px; border-radius:50%;'> <span>{d['name']}</span></div>"
        
        row = {"Driver": driver_cell}
        total_points = 0
        
        for session_name in all_sessions[:-1]: # Loop through everything except the "Total" column
            if session_name in points_dict:
                pts = points_dict[session_name].get(code, 0)
                row[session_name] = pts
                total_points += pts
            else:
                row[session_name] = "" # Leave blank if race hasn't happened
                
        row["Total"] = total_points
        rows.append(row)
        
    df = pd.DataFrame(rows)
    
    # Calculate bottom row (Grand Prix sums and final Running Sum)
    total_row = {"Driver": "<b>Total</b>"}
    for col in df.columns[1:]:
        if df[col].replace("", pd.NA).isna().all():
            total_row[col] = "" # Leave blank if no data yet
        else:
            total_row[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
            
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    
    # Convert to HTML with our custom CSS classes
    html = df.to_html(escape=False, index=False, classes="f1-table")
    return f"<div class='f1-table-container'>{html}</div>"


# --- Load Data ---
all_sessions, points_dict = fetch_season_data()

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Live Standings", "👤 Team Lineups", "📑 Spreadsheet View"])

with tab1:
    history_data = []
    for session_name in all_sessions:
        if session_name == "Total" or session_name not in points_dict:
            continue
        s_pts = sum(points_dict[session_name].get(code, 0) for code in steven_lineup)
        v_pts = sum(points_dict[session_name].get(code, 0) for code in vanessa_lineup)
        history_data.append({'Race': session_name, 'Steven': s_pts, 'Vanessa': v_pts})
        
    df_chart = pd.DataFrame(history_data)
    
    if not df_chart.empty:
        # FIXED: Changed single quotes to double quotes to prevent syntax errors
        df_chart["Steven's Season Points"] = df_chart['Steven'].cumsum()
        df_chart["Vanessa's Season Points"] = df_chart['Vanessa'].cumsum()
        
        fig = px.line(df_chart, x='Race', y=["Steven's Season Points", "Vanessa's Season Points"], markers=True, title="Cumulative Season Points",
                      color_discrete_map={"Steven's Season Points": "red", "Vanessa's Season Points": "blue"})
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig, use_container_width=True)
    else: 
        st.warning("No race data available yet.")

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
    st.subheader("Steven's Breakdown")
    steven_html = generate_html_spreadsheet(steven_lineup, points_dict, all_sessions)
    st.markdown(steven_html, unsafe_allow_html=True)
    
    st.subheader("Vanessa's Breakdown")
    vanessa_html = generate_html_spreadsheet(vanessa_lineup, points_dict, all_sessions)
    st.markdown(vanessa_html, unsafe_allow_html=True)
