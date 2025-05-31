# 📊 Juan Soto Budget Team — Streamlit Demo

A quick-and-dirty **Streamlit** app that answers one question:

> *“How good of an MLB team could you build for less than Juan Soto’s 2025 salary?”*

The app scrapes live salary data from **Spotrac**, pulls **FanGraphs/Statcast** stats via **pybaseball**, and assembles a value roster (starters, relievers, bench & backup catcher) that *still* costs less than Soto’s \$51 M contract.

---

## 🚀 Features

| Feature                | What it does                                                |
| ---------------------- | ----------------------------------------------------------- |
| **Live OPS threshold** | Uses Juan Soto’s current OPS + 0.001 as the hitting cutoff. |
| **Dynamic salary cap** | Total roster cost must be < \$51 M (Soto 2025).             |
| **8 position players** | 1B / 2B / 3B / SS / LF / CF / RF + primary C.               |
| **Pitching staff**     | 5 Starters + 5 Relievers (lowest ERA under budget).         |
| **Bench depth**        | 5 best-OPS bats not already picked.                         |
| **Backup C**           | Cheapest remaining catcher to round out the roster.         |
| **Streamlit UI**       | Interactive table + total payroll display.                  |

---

## 🏗️ Tech Stack

| Layer              | Library / Service                                   |
| ------------------ | --------------------------------------------------- |
| **Web UI**         | [Streamlit](https://streamlit.io/)                  |
| **MLB Stats**      | [pybaseball](https://github.com/jldbc/pybaseball)   |
| **Salary Data**    | Spotrac (scraped with `requests` + `BeautifulSoup`) |
| **Fuzzy matching** | `thefuzz` (a maintained fork of fuzzywuzzy)         |
| **Data wrangling** | `pandas`                                            |

---

## 📦 Installation

```bash
# 1. Clone and enter repo
$ git clone https://github.com/<your‑org>/juan‑soto‑budget‑team.git
$ cd juan‑soto‑budget‑team

# 2. Create a virtual env (optional but recommended)
$ python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. Launch the app
$ streamlit run app.py
```

> **Note**: First launch may take \~30 s while pybaseball pulls fresh data & caching kicks in.

---

## ⚙️ How It Works (High Level)

1. **`setup.py` → `compute_team()`**

   * Fetches Soto’s OPS via MLB StatsAPI.
   * Pulls batting + fielding stats, merges primary positions.
   * Scrapes salary tables from Spotrac per position.
   * Selects cheapest high‑OPS hitters for each field spot.
   * Adds pitchers & bench under configurable per‑player caps.
   * Returns a tidy DataFrame + total payroll.
2. **`app.py` (Streamlit)**

   * Caches `compute_team()` with `@st.cache_data` (runs once).
   * Displays roster table + total cost.

---

## 🗂️ Project Structure

```
juan-soto-budget-team/
├─ app.py               # Streamlit front‑end
├─ setup.py             # Core roster‑building logic
├─ sportrac.py          # Spotrac scraper helpers
├─ fuzzy.py             # Fuzzy‑match utils
├─ requirements.txt
└─ README.md            # You are here 😎
```

---

## 🔧 Config Tweaks

| Env Var / Const  | Default      | Description                    |
| ---------------- | ------------ | ------------------------------ |
| `TOTAL_BUDGET`   | 51\_000\_000 | Overall payroll ceiling        |
| `PER_HITTER_CAP` | 5\_666\_667  | Max salary per position player |
| `PER_SP_CAP`     | 2\_000\_000  | Max salary per starter         |
| `PER_RP_CAP`     | 2\_000\_000  | Max salary per reliever        |

Edit these in **`setup.py`** to experiment with different constraints.

---

## 📝 License

MIT — do whatever you want, just give credit.

---

## 🙏 Acknowledgements

* PyBaseball devs for the free stats API wrapper.
* Spotrac for publicly listing MLB contract data.
* FanGraphs for advanced stats.
* Juan Soto for being really, **really** expensive.

---

Ready to see how far \$51 M can go? `streamlit run app.py` and enjoy! ✌️
