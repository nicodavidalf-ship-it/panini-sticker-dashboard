import streamlit as st
import pandas as pd

# --- CONFIG ---
teams = ["ARG","BRA","EGY","ENG","FRA","KOR","NOR","RSA","URU"]
parallels = ["Blue","Red","Purple","Green","Black"]

# --- GENERATE STICKERS ---
def generate_stickers():
    data = []
    for team in teams:
        for i in range(1, 21):  # 20 stickers per team (adjust later if needed)
            data.append({
                "sticker": f"{team}{i}",
                "team": team,
                "collected": False,
                "parallel": None,
                "duplicates": 0
            })
    return pd.DataFrame(data)

# --- SESSION STATE ---
if "df" not in st.session_state:
    st.session_state.df = generate_stickers()

df = st.session_state.df

# --- TITLE ---
st.title("⚽ Panini World Cup 2026 Sticker Dashboard")

# --- BULK INPUT ---
st.subheader("Add Stickers")

bulk_input = st.text_area("Enter stickers (comma separated)", "URU2, RSA8")
parallel_input = st.selectbox("Parallel Type", ["None"] + parallels)
duplicates = st.number_input("Number of copies", min_value=1, value=1)

if st.button("Add Stickers"):
    stickers = [s.strip().upper() for s in bulk_input.split(",")]

    for s in stickers:
        if s in df["sticker"].values:
            idx = df[df["sticker"] == s].index[0]
            df.at[idx, "collected"] = True
            df.at[idx, "parallel"] = None if parallel_input == "None" else parallel_input
            df.at[idx, "duplicates"] += duplicates - 1

    st.success("Stickers added!")

# --- FILTER ---
st.subheader("Filter by Team")
team_filter = st.selectbox("Select Team", ["All"] + teams)

view_df = df if team_filter == "All" else df[df["team"] == team_filter]

# --- OVERALL PROGRESS ---
collected = df["collected"].sum()
total = len(df)

st.subheader("Overall Progress")
st.progress(collected / total)
st.write(f"{collected}/{total} collected ({collected/total:.1%})")

# --- TEAM PROGRESS ---
st.subheader("Progress by Team")

team_progress = df.groupby("team")["collected"].agg(["sum","count"]).reset_index()
team_progress["completion %"] = team_progress["sum"] / team_progress["count"]

st.dataframe(team_progress)

# --- CLOSEST TO COMPLETION ---
st.subheader("Closest to Completion")

closest = team_progress.sort_values("completion %", ascending=False)
st.dataframe(closest.head(3))

# --- RARE PARALLELS ---
st.subheader("Rare Stickers")

rare_df = df[df["parallel"].notnull()]
st.dataframe(rare_df)

# --- FULL TABLE ---
st.subheader("Sticker Collection")
st.dataframe(view_df)

# --- MISSING STICKERS ---
st.subheader("Missing Stickers")

missing_df = df[df["collected"] == False]

missing_list = ", ".join(missing_df["sticker"].tolist())
st.write(missing_list)

# --- DOWNLOAD BUTTON ---
csv = missing_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Missing Stickers CSV",
    data=csv,
    file_name="missing_stickers.csv",
    mime="text/csv"
)