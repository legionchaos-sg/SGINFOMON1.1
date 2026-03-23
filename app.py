# 8. News Section
st.header("🇸🇬 Singapore Headline News")
st.info("News feeds are active in the tabs below. Sources update every 3 mins.")

# Expanded news sources dictionary
sources = {
    "The Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CNA": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416",
    "Business Times": "https://www.businesstimes.com.sg/rss-feeds/singapore",
    "Mothership": "https://mothership.sg/feed/",
    "Shin Min (新明)": "https://www.zaobao.com.sg/rss/realtime/singapore"
}

# Function to fetch and parse feeds with headers to prevent blocking
def fetch_news(url):
    try:
        # User-Agent header is critical for SPH (ST/BT) and Mothership servers
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, timeout=5, headers=headers)
        return feedparser.parse(response.content)
    except Exception as e:
        return None

t1, t2 = st.tabs(["📊 Unified Feed", "📰 Individual Sources"])

with t1:
    # Shows the top 2 latest headlines from every source
    for name, url in sources.items():
        feed = fetch_news(url)
        if feed and feed.entries:
            st.markdown(f"**{name}**")
            for e in feed.entries[:2]:
                st.markdown(f"• [{e.title}]({e.link})")
        else:
            st.warning(f"⚠️ {name} feed currently unavailable.")

with t2:
    # Detailed view for a single selected source
    sel = st.selectbox("Select News Outlet", list(sources.keys()))
    feed = fetch_news(sources[sel])
    if feed and feed.entries:
        for e in feed.entries[:8]:  # Show more items in the individual view
            # Try to show a summary/snippet if available
            summary = e.summary[:100] + "..." if 'summary' in e else ""
            st.markdown(f"**[{e.title}]({e.link})**")
            if summary:
                st.caption(summary)
    else:
        st.error(f"Could not retrieve news from {sel}. Please check your connection.")

st.divider()
