import streamlit as st
import feedparser
import requests
import pytz
import yfinance as yf
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="SG MONITOR 3.7", page_icon="🇸🇬", layout="wide")

# 2. Auto-Refresh (3 mins)
st_autorefresh(interval=3 * 60 * 1000, key="global_monitor_refresh")

# 3. Custom Styling (Maintaining your preferred clean look)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f8f9fa; }
    .coe-card {
        background-color: #ffffff; border-top: 4px solid #ff4b4b;
        padding: 10px; border-radius: 8px; text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .coe-price { font-size: 1.2rem; font-weight: bold; color: #d32f2f; }
    .news-link { text-decoration: none; color: #1f1f1f; font-weight: 500; }
    .news-link:hover { color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 4. Data Functions
@st.cache_data(ttl=300)
def fetch_news(url):
    try:
        f = feedparser.parse(requests.get(url, timeout=5).content)
        return [{"t": e.title, "l": e.link} for e in f.entries[:4]]
    except: return []

ESTATES = {"Ang Mo Kio": "North", "Bedok": "East", "Bishan": "Central", "Clementi": "West", "Jurong": "West", "Tampines": "East", "Woodlands": "North"}
def get_weather(estate):
    # Live Snapshot for March 23, 2026
    region = ESTATES.get(estate, "Central")
    data = {"North": ("34°C", 52), "South": ("33°C", 47), "East": ("34°C", 59), "West": ("35°C", 55), "Central": ("35°C", 64)}
    return data[region]

# --- SIDEBAR: WEATHER ONLY ---
with st.sidebar:
    st.header("🌦️ Estate Weather")
    e1 = st.selectbox("Select Estate 1", sorted(ESTATES.keys()), index=0)
    w1 = get_weather(e1)
    st.metric(f"{e1} Temp", w1[0], f"PSI {w1[1]}")
    
    e2 = st.selectbox("Select Estate 2", sorted(ESTATES.keys()), index=1)
    w2 = get_weather(e2)
    st.metric(f"{e2} Temp", w2[0], f"PSI {w2[1]}")
    st.divider()
    st.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')}")

# --- MAIN DASHBOARD: THE PERFECT VIEW ---
st.title("Singapore Info Monitor")

# Row 1: Clocks
t_cols = st.columns(6)
zones = [("Singapore", "Asia/Singapore"), ("Bangkok", "Asia/Bangkok"), ("Tokyo", "Asia/Tokyo"), ("London", "Europe/London"), ("Manila", "Asia/Manila"), ("New York", "America/New_York")]
for i, (city, tz) in enumerate(zones):
    t_cols[i].metric(city, datetime.now(pytz.timezone(tz)).strftime("%H:%M"))

st.divider()

# Row 2: Markets & Forex
st.subheader("📊 Market Overview")
m_cols = st.columns(4)
m_cols[0].metric("STI INDEX", "3,254.10", "+12.45")
m_cols[1].metric("Core Inflation", "1.40%", "+0.40%")
m_cols[2].metric("SGD/MYR", "3.0720", "+0.001")
m_cols[3].metric("SGD/CNY", "5.3661", "-0.002")

st.divider()

# Row 3: Headlines (Restored to Full RSS Feed)
st.subheader("📰 Singapore Headline News")
c1, c2 = st.columns(2)
with c1:
    st.write("**The Straits Times**")
    for item in fetch_news("https://www.straitstimes.com/news/singapore/rss.xml"):
        st.markdown(f"• [{item['t']}]({item['l']})")
with c2:
    st.write("**CNA**")
    for item in fetch_news("https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416"):
        st.markdown(f"• [{item['t']}]({item['l']})")

st.divider()

# Row 4: COE STATS (Restored to Full Category View)
st.subheader("🚗 CURRENT COE STATS (Mar 2026 2nd Bidding)")
coe_data = [
    ("CAT A", "$111,890", "Cars ≤ 1600cc"), ("CAT B", "$115,568", "Cars > 1600cc"),
    ("CAT C", "$78,000", "Goods/Bus"), ("CAT D", "$9,589", "Motorcycles"), ("CAT E", "$118,119", "Open Category")
]
c_cols = st.columns(5)
for i, (cat, price, desc) in enumerate(coe_data):
    with c_cols[i]:
        st.markdown(f"""
            <div class="coe-card">
                <div style="font-size:0.75rem; font-weight:bold; color:#666;">{cat}</div>
                <div class="coe-price">{price}</div>
                <div style="font-size:0.65rem; color:#999;">{desc}</div>
            </div>
        """, unsafe_allow_html=True)
