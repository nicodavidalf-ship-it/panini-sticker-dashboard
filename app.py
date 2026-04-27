import streamlit as st
import pandas as pd
from supabase import create_client

# --- SUPABASE CONFIG ---
SUPABASE_URL = "https://qdegcbneedwbqllenvrm.supabase.co"
SUPABASE_KEY = "sb_publishable_AehbQss_pfLe-yAncoOf9A_tOH4X2N1"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Panini 2026", layout="wide")

# --- LOGIN ---
st.title("⚽ Panini 2026")
user_id = st.text_input("Enter your email")

if not user_id:
    st.stop()

# --- DATA ---
teams = [
    "ARG","BRA","ENG","FRA","GER","ESP","ITA","POR",
    "NED","BEL","CRO","URU","COL","MEX","USA","CAN"
]

players = [f"Player{i}" for i in range(1, 21)]

def generate_stickers():
    data = []
    for team in teams:
        for i, p in enumerate(players, start=1):
            data.append({
                "user_id": user_id,
                "sticker": f"{team}{i}",
                "team": team,
                "player": p,
                "collected": False,
                "duplicates": 0,
                "parallel": None
            })
    return pd.DataFrame(data)

# --- LOAD ---
def load_data():
    try:
        res = supabase.table("collection").select("*").execute()

        if res.data:
            df_db = pd.DataFrame(res.data)
            df_user = df_db[df_db["user_id"] == user_id]

            if not df_user.empty:
                return df_user

        return pd.DataFrame()

    except Exception as e:
        st.error(f"DB error: {e}")
        return pd.DataFrame()

# --- INIT USER ---
def initialize_user():
    base_df = generate_stickers()

    supabase.table("collection").insert(base_df.to_dict("records")).execute()

# --- SAVE ---
def save_row(row):
    supabase.table("collection").upsert(row.to_dict()).execute()

# --- MAIN FLOW ---
df = load_data()

if df.empty:
    st.warning("Initializing your collection...")
    initialize_user()
    df = load_data()

# --- ADD STICKERS ---
st.subheader("Add Stickers")

bulk_input = st.text_area("Enter stickers", "ARG1, BRA2")
copies = st.number_input("Copies", min_value=1, value=1)

if st.button("Add"):
    stickers = [s.strip().upper() for s in bulk_input.split(",")]

    for s in stickers:
        if s in df["sticker"].values:
            idx = df[df["sticker"] == s].index[0]

            df.at[idx, "collected"] = True
            df.at[idx, "duplicates"] += copies

            save_row(df.loc[idx])

    st.success("Updated!")

# --- PROGRESS ---
collected = df["collected"].sum()
total = len(df)

st.subheader("Progress")
st.progress(collected / total if total else 0)
st.write(f"{collected}/{total} ({(collected/total):.1%})")

# --- FILTER ---
team_filter = st.selectbox("Team", ["All"] + teams)
view_df = df if team_filter == "All" else df[df["team"] == team_filter]

# --- TABLE ---
st.subheader("Collection")
st.dataframe(view_df)

# --- MISSING ---
missing_df = df[df["collected"] == False]

st.subheader("Missing Stickers")
st.write(", ".join(missing_df["sticker"].tolist()))

csv = missing_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Missing List",
    csv,
    "missing.csv",
    "text/csv"
)
