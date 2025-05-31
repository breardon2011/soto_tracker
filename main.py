import streamlit as st
from setup import compute_team
import requests


SOTO_STATS_URL = ("https://statsapi.mlb.com/api/v1/people/665742/"
                  "stats?stats=season&season=2025")
SOTO_SALARY    = 51_000_000  # Spotrac 2025 cash total



st.set_page_config(page_title="OPS-Optimized Roster", layout="wide")

st.title("💰 How much team can Juan Soto buy?")


@st.cache_data(ttl=3600)   # cache for 1 hour
def get_soto_stats():
    data = requests.get(SOTO_STATS_URL, timeout=10).json()
    stat = data["stats"][0]["splits"][0]["stat"]
    return {
        "Season" : "2025",
        "Team"   : "New York Mets",
        "AVG"    : stat["avg"],
        "OBP"    : stat["obp"],
        "SLG"    : stat["slg"],
        "OPS"    : stat["ops"],
        "HR"     : stat["homeRuns"],
        "RBI"    : stat["rbi"],
        "Salary" : f"${SOTO_SALARY:,.0f}"
    }


@st.cache_data
def load():
    return compute_team()


# ─────────────────────────────────────────────────────────────
# Juan Soto headline card
# ─────────────────────────────────────────────────────────────
soto = get_soto_stats()

st.markdown("## 💸 Juan Soto 2025 Stats")
cols = st.columns(6)
cols[0].metric("AVG", soto["AVG"])
cols[1].metric("OBP", soto["OBP"])
cols[2].metric("SLG", soto["SLG"])
cols[3].metric("OPS", soto["OPS"])
cols[4].metric("HR",  soto["HR"])
cols[5].metric("RBI", soto["RBI"])

st.markdown(f"**2025 Cash Salary:** `{soto['Salary']}`")


team_df, total = load()

st.dataframe(team_df, use_container_width=True)

st.markdown(f"### Total salary used: **${total:,.0f}**")
