import streamlit as st
import pandas as pd
from supabase import create_client

# --- SUPABASE CONFIG ---
SUPABASE_URL = "https://qdegcbneedwbqllenvrm.supabase.co"
SUPABASE_KEY = "sb_publishable_AehbQss_pfLe-yAncoOf9A_tOH4X2N1"

supabase = create_client(SUPABASE_URL,SUPABASE_KEY)

# --- LOGIN ---
st.title("⚽ Panini 2026")

user_id = st.text_input("Enter your email")

if not user_id:
    st.stop()

# --- TEAMS ---
teams = ["ARG","BRA","ENG","FRA","GER","ESP","ITA","POR"]

players = [
    "Messi","Di Maria","Alvarez","Enzo","Otamendi",
    "Mbappe","Griezmann","Dembele","Camavinga","Tchouameni",
    "Kane","Bellingham","Saka","Foden","Rice"
]

def generate_stickers():
    data = []
    for team in teams:
        for i, p in enumerate(players[:15], start=1):
            data.append({
                "sticker": f"{team}{i}",
                "team": team,
                "player": p,
                "collected": False,
                "duplicates": 0,
                "parallel": None
            })
    return pd.DataFrame(data)

df = generate_stickers()

# --- LOAD USER DATA ---
def load_data():
    res = supabase.table("collection").select("*").eq("user_id", user_id).execute()

    if res.data:
        return pd.DataFrame(res.data)
    return df

df = load_data()

# --- SAVE ---
def save_row(row):
    supabase.table("collection").upsert({
        "user_id": user_id,
        "sticker": row["sticker"],
        "collected": row["collected"],
        "duplicates": row["duplicates"],
        "parallel": row["parallel"]
    }).execute()

# --- UI ---
st.subheader("Add Sticker")

sticker = st.text_input("Sticker (e.g. ARG1)")

if st.button("Add"):
    if sticker in df["sticker"].values:
        idx = df[df["sticker"] == sticker].index[0]
        df.at[idx, "collected"] = True
        df.at[idx, "duplicates"] += 1
        save_row(df.loc[idx])

# --- PROGRESS ---
st.subheader("Progress")

collected = df["collected"].sum()
total = len(df)

st.progress(collected / total)
st.write(f"{collected}/{total}")

# --- TABLE ---
st.dataframe(df)
