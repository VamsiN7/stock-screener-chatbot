import streamlit as st

st.set_page_config(
    page_title="Peter Lynch Screener",
    page_icon="📈",
    layout="wide"
)

st.sidebar.title("📊 Peter Lynch Screener")
page = st.sidebar.radio("Navigate", [
    "🏠 Home",
    "📈 Stock Analysis",
    "✅ Recommendations",
    "🔍 Screener",
    # "🧠 Market Insights"
])

if page == "🏠 Home":
    st.switch_page("pages/1_Home.py")
elif page == "📈 Stock Analysis":
    st.switch_page("pages/2_Stock_Analysis.py")
elif page == "✅ Recommendations":
    st.switch_page("pages/3_Recommendations.py")
elif page == "🔍 Screener":
    st.switch_page("pages/4_Screener.py")
# elif page == "🧠 Market Insights":
#     st.switch_page("pages/5_Market_Insights.py")
