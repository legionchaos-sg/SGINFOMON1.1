import streamlit as st
from datetime import datetime

# 1. Page Config
st.set_page_config(
    page_title="SG INFO MON 1.1",
    page_icon="🇸🇬",
    layout="wide"
)

# 2. Adaptive CSS 
st.markdown("""
    <style>
    /* Remove extra space at top */
    .block-container { padding-top: 1rem; max-width: 1200px; }
    
    /* Small styling for the toggle area */
    div[data-testid="stColumn"] {
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Header & Top Right Toggle
# We create two columns: one for the Title, one for the Mode
col_title, col_mode = st.columns([3, 1])

with col_title:
    st.title("Singapore Info Monitor 1.1")

with col_mode:
    # This creates a small dropdown in the top right
    theme = st.selectbox(
        "Display Mode",
        ["Default", "Light", "Dark"],
        label_visibility="collapsed" # Hides the label for a cleaner look
    )

st.write(f"**System Status:** Online | {datetime.now().strftime('%H:%M:%S')} SGT")
st.divider()

# 4. Logic for the Toggle (Informational)
if theme == "Dark":
    st.warning("🌙 **Dark Mode Tip:** Streamlit's engine follows your Browser/System. To force Dark Mode, go to Settings > Theme > Dark.")
elif theme == "Light":
    st.info("☀️ **Light Mode Tip:** Go to Settings > Theme > Light to keep this look permanently.")
else:
    st.success("🏗️ **Adaptive Mode:** Your app is currently following your system's look.")

# 5. Footer
st.caption("Version 1.1 | Top-Right UI Layout")
