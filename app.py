import streamlit as st
import feedparser
import requests
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="SG INFO MON 1.1", page_icon="🇸🇬", layout="wide")

# 2. Styling for Professional Alerts & Source Tags
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .stAlert { border: none; border-left: 4px solid #ff4b4b; background-color: #f0f2f6; }
    .source-tag { 
        background-color: #e1e4e8; color: #24292e; padding: 2px 8px; 
        border-radius: 12px; font-size: 0.75rem; font-weight: 600; 
        margin-right: 8px; border: 1px solid #d1d5da;
    }
    .news-item { margin-bottom: 1rem; padding: 10px; border-radius: 8px; transition: 0.3s; }
    .news-item:hover { background-color: #00000005; }
    </style>
    """, unsafe_allow_html=True)

# 3. Enhanced Feed Processor
def fetch_feed(name, url):
    status = {"name": name, "ok": False, "data": [], "msg": ""}
    try:
        # 5-second timeout to prevent app hanging
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            if feed.entries:
                status["ok"] = True
                for entry in feed.entries:
                    status["data"].append({
                        "source": name,
                        "title": entry.title,
                        "link": entry.link,
                        "date": entry.get('published', 'Recent Update')
                    })
            else:
                status["msg"] = "Stall: No active data entries found in feed."
        else:
            status["msg"] = f"Source Error: HTTP {response.status_code} (Service Unavailable)"
    except Exception:
        status["msg"] = "Connection Stall: Remote server timed out."
    return status

# 4. Sources Registry
sources = {
    "The Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Lianhe Zaobao": "https://www.zaobao.com.sg/rss/realtime/singapore",
    "The Business Times": "https://www.businesstimes.com.sg/rss/singapore",
    "Berita Harian": "https://www.beritaharian.sg/rss/singapura",
    "Tamil Murasu": "https://www.tamilmurasu.com.sg/rss/singapore",
    "Shin Min Daily": "https://www.shinmin.sg/rss/news"
}

# 5. Header
st.title("Singapore Info Monitor 1.1")
st.write(f"System Check: **{datetime.now().strftime('%H:%M:%S')} SGT**")

# 6. Main Logic
tab_unified, tab_source = st.tabs(["📊 Unified Top 9 Headlines", "📰 Individual Sources"])

# Fetch all data once to be efficient
all_results = [fetch_feed(name, url) for name, url in sources.items()]

with tab_unified:
    combined_news = []
    # Identify broken feeds for a professional notice
    stalled_sources = [r['name'] for r in all_results if not r['ok']]
    
    if stalled_sources:
        with st.expander("⚠️ System Notice: Source Connectivity Issues"):
            st.warning(f"The following feeds are currently stalling: {', '.join(stalled_sources)}")
            st.info("💡 **Professional Recommendation:** These are remote source errors. Please try a manual refresh below.")
            if st.button("Manual System Refresh"):
                st.rerun()

    for r in all_results:
        if r['ok']: combined_news.extend(r['data'])
    
    # Sort or simply slice the first 9
    for item in combined_news[:9]:
        st.markdown(f"""
        <div class="news-item">
            <span class="source-tag">{item['source']}</span>
            <strong><a href="{item['link']}" target="_blank" style="color:inherit; text-decoration:none;">{item['title']}</a></strong>
            <div style="font-size:0.8rem; color:gray; margin-top:4px;">🕒 {item['date']}</div>
        </div>
        """, unsafe_allow_html=True)

with tab_source:
    choice = st.radio("Select Newspaper", list(sources.keys()), horizontal=True)
    # Find the specific result
    res = next(r for r in all_results if r['name'] == choice)
    
    if res['ok']:
        for item in res['data'][:5]:
            st.subheader(item['title'])
            st.caption(f"Source: {item['source']} | {item['date']}")
            st.markdown(f"[Read Full Story]({item['link']})")
            st.write("---")
    else:
        st.error(f"### {res['msg']}")
        st.write("This issue is originating from the news provider's RSS server.")
        if st.button(f"Retry {choice}"):
            st.rerun()

# 7. Footer
st.divider()
st.caption("2026 Stable Build | SPH & Mediacorp Integrated Feed")
