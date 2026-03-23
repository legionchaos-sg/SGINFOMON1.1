with tab2:
    # Updated 2026 Zaobao Realtime Feed
    zb_news = get_news("https://www.zaobao.com.sg/rss/realtime/singapore")
    
    if zb_news:
        for entry in zb_news:
            st.markdown(f"**[{entry.title}]({entry.link})**")
            st.caption(f"🕒 {entry.published if 'published' in entry else 'Just updated'}")
            st.write("---")
    else:
        # Improved error message for troubleshooting
        st.warning("⚠️ Zaobao feed is currently restricted or refreshing. Please check back in 5 minutes.")
        if st.button("Manual Refresh"):
            st.rerun()
