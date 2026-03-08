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
    .f1-table-container { 
        overflow-x: auto; 
        max-width: 100%; 
        margin-bottom: 2rem; 
    }
    .f1-table { 
        width: 100%; 
        border-collapse: collapse; 
        font-family: sans-serif; 
        font-size: 13px; 
    }
    .f1-table td { 
        border: 1px solid #444; 
        padding: 8px; 
        text-align: center; 
        white-space: nowrap; 
    }
    
    /* Vertical Column Headers */
    .f1-table th { 
        border: 1px solid #444; 
        padding: 5px; 
        text-align: center; 
    }
    .f1-table th:not(:first-child) {
        writing-mode: vertical-rl;
        transform: rotate(180deg);
        height: 200px; /* Increased height to prevent text cut-off */
        white-space: nowrap;
        vertical-align: middle;
        line-height: 1.2;
    }

    /* Sticky First Column */
    .f1-table td:first-child, .f1-table th:first-child { 
        text-align: left; 
        position: sticky; 
        left: 0; 
        background-color: #0e1117; 
        z-index: 2; 
        min-width: 160px; 
    }
    
    /* Bold Bottom Row */
    .f1-table tr:last-child { font-weight: bold; background-color: #1e2530; }

    /* Responsive Mobile Adjustments */
    @media (max-width: 600px) {
        .f1-table th:not(:first-child) { height: 130px; font-size: 10px; }
    }
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

# --- Data Fetching ---
@st.cache_data(ttl=3600)
def fetch_season_data():
    schedule = fastf1.get_event_schedule(2026)
    events = schedule[~schedule['EventFormat'].str.contains('testing', case=False, na=False)]
    points_dict, all_sessions = {}, []
    now = pd.Timestamp.now().tz_localize(None)
    
    for _, event in events.iterrows():
        event_name = event['EventName']
        is_sprint = str(event['EventFormat']).lower() in ['sprint', 'sprint_qualifying', 'sprint_shootout']
        
        if is_sprint:
            sprint_name = f"{event_name} (Sprint)"
            all_sessions.append(sprint_name)
            if event['EventDate'] <= now:
                try:
                    s = fastf1.get_session(2026, event_name, 'S')
                    s.load(telemetry=False, weather=False, messages=False)
                    res = s.results[['Abbreviation', 'Points']]
                    points_dict[sprint_name] = dict(zip(res['Abbreviation'], res['Points']))
                except: pass
        
        race_name = f"{event_name} (Race)"
        all_sessions.append(race_name)
        if event['EventDate'] <= now:
            try:
                s = fastf1.get_session(2026, event_name, 'R')
                s.load(telemetry=False, weather=False, messages=False)
                res = s.results[['Abbreviation', 'Points']]
                points_dict[race_name] = dict(zip(res['Abbreviation'], res['Points']))
            except: pass
            
    all_sessions.append("Total")
    return all_sessions, points_dict

def generate_html_spreadsheet(lineup, points_dict, all_sessions):
    rows = []
    for code in lineup:
        d = driver_info.get(code, {"name": code, "img": ""})
        driver_cell = f"<div style='display:flex; align-items:center;'><img src='{d['img']}' width='35' style='margin-right:10px; border-radius:50%;'> <span>{d['name']}</span></div>"
        row = {"Driver": driver_cell}
        total_pts = 0
        for session in all_sessions[:-1]:
            pts = points_dict.get(session, {}).get(code, 0)
            row[session] = pts
            total_pts += pts
        row["Total"] = total_pts
        rows.append(row)
        
    df = pd.DataFrame(rows)
    total_row = {"Driver": "<b>Total</b>"}
    for col in df.columns[1:]:
        total_row[col] = df[col].sum()
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    return f"<div class='f1-table-container'>{df.to_html(escape=False, index=False, classes='f1-table')}</div>"

# --- Main App ---
all_sessions, points_dict = fetch_season_data()
tab1, tab2, tab3 = st.tabs(["📊 Live Standings", "👤 Team Lineups", "📑 Spreadsheet View"])

with tab1:
    history_data = []
    for s in all_sessions:
        if s == "Total" or s not in points_dict: continue
        history_data.append({'Race': s, 'Steven': sum(points_dict[s].get(c, 0) for c in steven_lineup), 
                             'Vanessa': sum(points_dict[s].get(c, 0) for c in vanessa_lineup)})
    df_chart = pd.DataFrame(history_data)
    if not df_chart.empty:
        df_chart["Steven's Season Points"] = df_chart['Steven'].cumsum()
        df_chart["Vanessa's Season Points"] = df_chart['Vanessa'].cumsum()
        fig = px.line(df_chart, x='Race', y=["Steven's Season Points", "Vanessa's Season Points"], markers=True, title="Cumulative Season Points")
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    for name, lineup, col in [("Steven", steven_lineup, col1), ("Vanessa", vanessa_lineup, col2)]:
        with col:
            st.subheader(f"{name}'s Drivers")
            for code in lineup:
                d = driver_info.get(code, {"name": code, "img": "https://via.placeholder.com/35"})
                c1, c2 = st.columns([0.2, 5])
                c1.image(d["img"], width=30)
                c2.markdown(f"**{d['name']}**")

with tab3:
    st.markdown(generate_html_spreadsheet(steven_lineup, points_dict, all_sessions), unsafe_allow_html=True)
    st.markdown(generate_html_spreadsheet(vanessa_lineup, points_dict, all_sessions), unsafe_allow_html=True)
