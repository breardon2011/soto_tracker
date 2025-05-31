import streamlit as st
from setup import compute_team

st.set_page_config(page_title="OPS-Optimized Roster", layout="wide")

st.title("💰 OPS-Optimized 2025 Roster (< $51 M)")

@st.cache_data
def load():
    return compute_team()

team_df, total = load()

st.dataframe(team_df, use_container_width=True)

st.markdown(f"### Total salary used: **${total:,.0f}**")
