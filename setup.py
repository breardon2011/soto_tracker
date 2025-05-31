import requests
from pybaseball import batting_stats, fielding_stats
import pandas as pd
from fuzzy import * 
from sportrac import *
from pybaseball import pitching_stats


SOTO_URL = "https://statsapi.mlb.com/api/v1/people/665742/stats?stats=season&season=2025"
POSITIONS = ['1B','2B','3B','SS','LF','CF','RF']
CATCHER = 'C'
TOTAL_BUDGET = 51_000_000


def compute_team2():
    used_names = set()
    team = {}
    budget_used = 0
    resp = requests.get(SOTO_URL)
    json = resp.json()
    soto_ops = json["stats"][0]["splits"][0]["stat"]["ops"]
    target_ops = float(soto_ops) + .001


    batting = batting_stats(2025)
    fielding = fielding_stats(2025)
    position_df = fielding.groupby('Name')['Pos'].agg(lambda x: x.value_counts().idxmax()).reset_index()
    position_df.columns = ['Name', 'Primary_Pos']
    batting_with_pos = pd.merge(batting, position_df, on='Name', how='left')


    for pos in POSITIONS:
        filtered = batting_with_pos[
            (batting_with_pos['OPS'] > target_ops) &
            (batting_with_pos['Primary_Pos'] == pos)
        ]
        first_20 = filtered.sort_values(by='OPS', ascending=False).head(20)

        player_salaries = scrape_spotrac_position_salaries(position_code=pos.lower())
        first_20['Matched_Salary'] = first_20['Name'].apply(
            lambda name: fuzzy_match_salary(name, player_salaries)
        )

        cheap_players = first_20[first_20['Matched_Salary'] <  5_666_667]
        sorted_cheap_players = cheap_players.sort_values(by='OPS', ascending=False)

        if not sorted_cheap_players.empty:
            player = sorted_cheap_players.iloc[0]
            team[pos] = player
            budget_used += player['Matched_Salary']


    catcher_pool = batting_with_pos[
        batting_with_pos['OPS'] > target_ops  
    ]
    catcher_top = catcher_pool.sort_values(by='OPS', ascending=False).head(20)

    catcher_salaries = scrape_spotrac_position_salaries(position_code='c')
    catcher_top['Matched_Salary'] = catcher_top['Name'].apply(
        lambda name: fuzzy_match_salary(name, catcher_salaries)
    )

    catcher_cheap = catcher_top[catcher_top['Matched_Salary'] < (TOTAL_BUDGET - budget_used)]
    catcher_sorted = catcher_cheap.sort_values(by='OPS', ascending=False)

    if not catcher_sorted.empty:
        player = catcher_sorted.iloc[0]
        team['C'] = player
        budget_used += player['Matched_Salary']

    team['Starters'] = select_pitchers('SP', 5, budget_left=TOTAL_BUDGET - budget_used, exclude=used_names)
    budget_used += sum(p['Matched_Salary'] for p in team['Starters'])
    used_names.update(p['Name'] for p in team['Starters'])

    team['Relievers'] = select_pitchers('RP', 5, budget_left=TOTAL_BUDGET - budget_used, exclude=used_names)
    budget_used += sum(p['Matched_Salary'] for p in team['Relievers'])
    used_names.update(p['Name'] for p in team['Relievers'])

    team['Bench'] = select_bench_hitters(5, batting_with_pos, budget_left=TOTAL_BUDGET - budget_used, exclude=used_names)
    budget_used += sum(p['Matched_Salary'] for p in team['Bench'])
    used_names.update(p['Name'] for p in team['Bench'])

    backup_catcher = select_backup_catcher(batting_with_pos, budget_left=TOTAL_BUDGET - budget_used, exclude=used_names)
    if backup_catcher is not None:
        team['Backup_C'] = backup_catcher
        budget_used += backup_catcher['Matched_Salary']
        used_names.add(backup_catcher['Name'])

    return team, budget_used
    # print(f"Total salary used: ${budget_used:,.0f}")
    # for pos, player in team.items():
    #     print(f"{pos}: {player['Name']} - OPS {player['OPS']} - ${player['Matched_Salary']:,.0f}")



def compute_team():
    TOTAL_BUDGET = 51_000_000
    POSITIONS    = ['1B','2B','3B','SS','LF','CF','RF']
    used_names   = set()
    players      = []
    budget_used  = 0

    # --- helper -----------------------------------------------------------
    def _add_player(row, role):
        nonlocal budget_used
        players.append({
            "Role"  : role,
            "Name"  : row["Name"],
            "Team"  : row["Team"],
            "OPS"   : row.get("OPS"),
            "ERA"   : row.get("ERA"),
            "Salary": row["Matched_Salary"],
            "Age"   : row.get("Age"),
        })
        used_names.add(row["Name"])
        budget_used += row["Matched_Salary"]
    # ----------------------------------------------------------------------

    # 1️⃣ threshold = Juan Soto OPS + .001
    soto_ops = requests.get(
        "https://statsapi.mlb.com/api/v1/people/665742/stats?stats=season&season=2025"
    ).json()["stats"][0]["splits"][0]["stat"]["ops"]
    target_ops = float(soto_ops) + 0.001

    batting  = batting_stats(2025)
    fielding = fielding_stats(2025)
    position_df = (
        fielding.groupby("Name")["Pos"]
        .agg(lambda x: x.value_counts().idxmax())
        .reset_index()
        .rename(columns={"Pos": "Primary_Pos"})
    )
    batting_with_pos = batting.merge(position_df, on="Name", how="left")

    # 2️⃣ corner & OF positions
    for pos in POSITIONS:
        pool = (
            batting_with_pos[(batting_with_pos["OPS"] > target_ops)
                             & (batting_with_pos["Primary_Pos"] == pos)]
            .sort_values("OPS", ascending=False)
            .head(30)
        )
        salaries = scrape_spotrac_position_salaries(position_code=pos.lower())
        pool["Matched_Salary"] = pool["Name"].apply(
            lambda n: fuzzy_match_salary(n, salaries)
        ).astype(float)
        pool = pool.dropna(subset=["Matched_Salary"])
        pool = pool[pool["Matched_Salary"] < 5_666_667]
        if not pool.empty:
            _add_player(pool.iloc[0], pos)

    # 3️⃣ catcher (first one tries starter slot)
    catch_pool = (
        batting_with_pos[batting_with_pos["OPS"] > target_ops]
        .sort_values("OPS", ascending=False)
        .head(40)
    )
    catch_salaries = scrape_spotrac_position_salaries("c")
    catch_pool["Matched_Salary"] = catch_pool["Name"].apply(
        lambda n: fuzzy_match_salary(n, catch_salaries)
    ).astype(float)
    catch_pool = catch_pool.dropna(subset=["Matched_Salary"])
    catch_pool = catch_pool[catch_pool["Matched_Salary"] <= TOTAL_BUDGET - budget_used]
    if not catch_pool.empty:
        _add_player(catch_pool.iloc[0], "C")

    # 4️⃣ 5 SP + 5 RP
    def _pick_pitchers(role_code, role_label, needed):
        pool = (pitching_stats(2025)
                .sort_values("ERA")
                .head(120))
        pool = pool[~pool["Name"].isin(used_names)]
        sal = scrape_spotrac_position_salaries(role_code)
        pool["Matched_Salary"] = pool["Name"].apply(
            lambda n: fuzzy_match_salary(n, sal)
        ).astype(float)
        pool = pool.dropna(subset=["Matched_Salary"])
        for _, row in pool.iterrows():
            if needed == 0:
                break
            if row["Matched_Salary"] <= 2_000_000:
                _add_player(row, role_label)
                needed -= 1
     #solve nan issue 
    def _pick_relievers(role_code, role_label, needed):
        pool = (pitching_stats(2025, qual=0)
                .sort_values("ERA")
                .head(120))
        pool = pool[~pool["Name"].isin(used_names)]
        sal = scrape_spotrac_position_salaries(role_code)
        pool["Matched_Salary"] = pool["Name"].apply(
            lambda n: fuzzy_match_salary(n, sal)
        ).astype(float)
        pool = pool.dropna(subset=["Matched_Salary"])
        for _, row in pool.iterrows():
            if needed == 0:
                break
            if row["Matched_Salary"] <= 2_000_000:
                _add_player(row, role_label)
                needed -= 1

    _pick_pitchers("sp", "SP", 5)
    _pick_relievers("rp", "RP", 5)

    # 5️⃣ bench (best remaining OPS)
    bench_pool = (
        batting_with_pos[~batting_with_pos["Name"].isin(used_names)]
        .sort_values("OPS", ascending=True)
        .head(100)
    )
    bench_salaries = scrape_spotrac_position_salaries(bench=True)  # fallback
    bench_pool["Matched_Salary"] = bench_pool["Name"].apply(
        lambda n: fuzzy_match_salary(n, bench_salaries)
    ).astype(float)
    bench_pool = bench_pool.dropna(subset=["Matched_Salary"])
    for _, row in bench_pool.iterrows():
        if len([p for p in players if p["Role"] == "Bench"]) == 5:
            break
        if row["Matched_Salary"] <= 1_000_000:
            _add_player(row, "Bench")

    # 6️⃣ cheap backup catcher if not already picked
    if "Backup_C" not in {p["Role"] for p in players}:
        bc = select_backup_catcher(batting_with_pos,
                                   budget_left=5_000_000,
                                   exclude=used_names)
        if bc is not None:
            _add_player(bc, "Backup_C")

    players_df = pd.DataFrame(players)
    return players_df, budget_used
