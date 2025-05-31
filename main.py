import streamlit as st
from setup import compute_team

st.title("💰 OPS-Optimized 2025 Roster (< $51 M)")

@st.cache_data
def load():
    return compute_team()

team_df, total = load()

st.dataframe(team_df)
st.markdown(f"### Total salary used: **${total:,.0f}**")
