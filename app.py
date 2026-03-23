# 6. Market Overview (Grouped in Dropdown)
st.write("")
with st.expander("📊 Market Overview & Commodities", expanded=True):
    # Defining tickers
    m_tickers = {
        "STI INDEX": "^STI", 
        "Gold Price": "GC=F", 
        "Crude Price": "CL=F",
        "Silver Price": "SI=F",
        "S&P 500": "^GSPC"
    }
    
    m_data = get_financial_data(m_tickers)
    
    # Row 1: Your Defaults (Gold and Crude)
    col_def1, col_def2 = st.columns(2)
    with col_def1:
        st.metric("Gold (Default)", f"${m_data['Gold Price']['p']:,.2f}", f"{m_data['Gold Price']['change']:+.2f}")
    with col_def2:
        st.metric("Crude Oil (Default)", f"${m_data['Crude Price']['p']:,.2f}", f"{m_data['Crude Price']['change']:+.2f}")
    
    st.divider()
    
    # Row 2: The rest of the list
    col_rest1, col_rest2, col_rest3 = st.columns(3)
    with col_rest1:
        st.metric("STI INDEX", f"{m_data['STI INDEX']['p']:,.2f}", f"{m_data['STI INDEX']['change']:+.2f}")
    with col_rest2:
        st.metric("Silver Price", f"${m_data['Silver Price']['p']:,.2f}", f"{m_data['Silver Price']['change']:+.2f}")
    with col_rest3:
        st.metric("S&P 500", f"{m_data['S&P 500']['p']:,.2f}", f"{m_data['S&P 500']['change']:+.2f}")

# 7. Forex Exchange Panel (Grouped in Dropdown)
with st.expander("💱 Forex Exchange (Base: 1 SGD)", expanded=False):
    fx_tickers = {
        "CNY (China)": "SGDCNY=X", 
        "MYR (Malaysia)": "SGDMYR=X", 
        "THB (Thailand)": "SGDTHB=X", 
        "JPY (Japan)": "SGDJPY=X", 
        "AUD (Australia)": "SGDAUD=X"
    }
    fx_data = get_financial_data(fx_tickers)
    fx_cols = st.columns(5)

    for i, label in enumerate(fx_tickers.keys()):
        val = fx_data[label]
        color = "#28a745" if val['change'] >= 0 else "#dc3545"
        arrow = "▲" if val['change'] >= 0 else "▼"
        with fx_cols[i]:
            st.markdown(f"""
                <div class="forex-card">
                    <div class="forex-label">{label}</div>
                    <div class="forex-price">{val['p']:.4f}</div>
                    <div style="color:{color}; font-size:0.8rem; font-weight:bold;">
                        {arrow} {abs(val['pc']):.2f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)
