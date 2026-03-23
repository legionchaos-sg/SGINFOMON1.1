@st.cache_data(ttl=600)
def fetch_news_data(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # 1. Get the raw data
        response = requests.get(url, timeout=5, headers=headers)
        feed = feedparser.parse(response.content)
        
        # 2. Extract ONLY the text/links into a simple list
        # This is the "Pickle-friendly" data
        clean_entries = []
        for e in feed.entries[:10]: # Limit to top 10 for safety
            clean_entries.append({
                'title': e.title,
                'link': e.link
            })
        return clean_entries
    except Exception as e:
        return []

# Update your UI loop to use the new list format
with tab_sources:
    sel_name = st.selectbox("Choose News Outlet", list(news_sources.keys()))
    entries = fetch_news_data(news_sources[sel_name]) # Now returns a list, not a feed object
    if entries:
        for e in entries:
            st.markdown(f"• **[{e['title']}]({e['link']})**")
            if trans_on: 
                st.markdown(f"<span class='translation-text'>🇨🇳 {translate_cached(e['title'])}</span>", unsafe_allow_html=True)
