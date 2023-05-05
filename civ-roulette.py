import streamlit as st
import pandas as pd
import numpy as np
import random
import os

DATASET_LOCATION = './datasets'

@st.cache_data
def load_datasets(directory: str) -> dict:
    """
    This function loads all the datasets in the given directory into a dictionary.
    The key is the file name. The value is the file loaded into a DataFrame.
    """
    datasets = {}
    for dirpath, dirnames, files in os.walk(directory):
        for file_name in files:
            data = pd.read_csv(dirpath + '/' + file_name)
            datasets[file_name] = data
    return datasets

def make_selections(civs, players, num_choices):
    for _ in range(num_choices):
        for player_choices in players.values():
            if len(civs) > 0:
                rng = random.Random(st.session_state["seed"])
                selected_civ = rng.choice(civs)
                player_choices.append(selected_civ)
                civs.remove(selected_civ)   
    return

def display_selections(selections):
    for player,selections in selections.items():
        st.subheader(f"Selections for {player}:")
        civ_df = pd.DataFrame(selections)
        st.table(civ_df.style.hide(axis="index"))
        st.divider()
    return

def display_easy_copy(selections):
    data = ""
    for player,selections in selections.items():
        data += f"# Selections for {player}\n"
        for civ in selections:
            data += f" -> {civ['Civilization']} - {civ['Leader']}\n"
    st.code(data, language="markdown")
    return

def randomize_seed():
    st.session_state["seed"] = random.randint(1,10000)
    return

def select_dlc(dataset):
    dlc_enabled = ["Base Game"]
    dlc_cols = st.columns(3)
    for i,dlc in enumerate(dataset["DLC"].dropna().unique()):
        if dlc:
            with dlc_cols[i % 3]:
                if st.checkbox(dlc, value=True):
                    dlc_enabled.append(dlc)
    return dlc_enabled


if "seed" not in st.session_state:
    randomize_seed()

# Load datasets from file
datasets = load_datasets(DATASET_LOCATION)

# Dataset Selection
dataset_selection = st.selectbox("Select dataset", datasets.keys())
selected_dataset = datasets[dataset_selection]

# DLC Filter
enabled_dlc = select_dlc(selected_dataset)
selected_dataset.drop(selected_dataset[selected_dataset["DLC"].str.contains("|".join(enabled_dlc)) == False].index, inplace=True)
selected_dataset.reset_index(inplace=True)

# Civ List
civs = selected_dataset.to_dict(orient="records")

# Player Selection
num_players = st.slider("Select number of players", 1, 12, 3)

player_names = []
name_cols = st.columns(3)
for i in range(num_players):
    with name_cols[i % 3]:
        player_names.append(st.text_input(f"Player {i+1}'s Name", value=f"Player {i+1}"))

# Civ Selection Options
num_choices = st.slider("Select number of choices", 1, 10, 3)
if (num_players * num_choices > len(civs)):
    st.warning(f"Warning: there are not enough unique Civilizations to give {num_players} players {num_choices} options. Please reduce the number of options.")

# Prep for selection
player_selections = {}
for player in player_names:
    player_selections[player] = []

st.divider()

# Make selection
make_selections(civs, player_selections, num_choices)

# Button to re-roll selections
st.header("Random Selections")
# st.detailed_view = st.checkbox("Detailed View")
st.button("Re-roll", on_click=randomize_seed)
# Display results
# if st.detailed_view == True:
#     display_selections(player_selections)
# else:
display_easy_copy(player_selections)