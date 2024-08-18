import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import sys


# USED THIS TO FIX INCOMPABITILITY OF PYTHON VERSION - ONE TIME IS ENOUGH
# def install(package):
#    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
# install("snowflake-connector-python")

from snowflake.connector import connect

conn = connect(
    account="vpb33500.us-west-2",  # os.environ.get("SNOWFLAKE_ACCOUNT"),
    user="ravirami2",  # os.environ.get("SNOWFLAKE_USER"),
    password="Campnou77$",  # os.environ.get("SNOWFLAKE_PASSWORD"),
    warehouse="COMPUTE_WH",  # os.environ.get("SNOWFLAKE_WAREHOUSE"),
    database="CRICKETDB",  # os.environ.get("SNOWFLAKE_DATABASE"),
    schema="C50",  # os.environ.get("SNOWFLAKE_SCHEMA")
    role="ACCOUNTADMIN",
)
# conn = connect(
#       account=st.secrets["account"],
#    user=st.secrets["user"],
#    password=st.secrets["password"],
#    warehouse=st.secrets["warehouse"],
#    database=st.secrets["database"],
#    schema=st.secrets["schema"]
# )
# teams query
cursor = conn.cursor()

batsman_list_query = (
    f"select batsman_name from ipl group by batsman_name having count(distinct id) > 60"
)
cursor.execute(batsman_list_query)  # .to_pandas()
batsman_df = cursor.fetch_pandas_all()

# Write directly to the app
st.title("IPL 2024 Data - Batting Radar")
st.text(
    "Percentile Rank of Batsman Strike Rate in Powerplay, Middle Overs and Death Overs"
)
batsmen_selected = st.multiselect("Select a batsman: ", batsman_df, max_selections=2)
submitted = st.button("Submit")
if len(batsmen_selected) != 2:
    st.error("Please select exactly 2 batsmen")
    st.stop()


if submitted:
    batsmen_list = "','".join(batsmen_selected)

    batsman_percentile_query = f"SELECT batsman_name, match_phase, sr_percentile FROM AGG_RUNS_BY_MATCH_PHASE WHERE batsman_name IN ('{batsmen_list}')"
    cursor.execute(batsman_percentile_query)  # .to_pandas()
    percentile_data_df = cursor.fetch_pandas_all()
    # st.text(percentile_data_df.values.tolist())
    percentile_data_df_unique = percentile_data_df.drop_duplicates(
        subset=["MATCH_PHASE"]
    )
    categories = percentile_data_df_unique["MATCH_PHASE"].values.tolist()
    values = percentile_data_df["SR_PERCENTILE"].values.tolist()

    def get_player_data(player_name, df):
        player_data = []
        for category in categories:
            value = df[
                (df["BATSMAN_NAME"] == player_name) & (df["MATCH_PHASE"] == category)
            ]["SR_PERCENTILE"].values
            player_data.append(value[0] if len(value) > 0 else 0)
        return player_data

    player1_data = get_player_data(batsmen_selected[0], percentile_data_df)
    player2_data = get_player_data(batsmen_selected[1], percentile_data_df)

    # Add the first value to the end to close the plot
    player1_data.append(player1_data[0])
    player2_data.append(player2_data[0])

    # N = len(categories)

    num_vars = len(values)  # Set num_vars to the length of your data
    num_categories = len(categories)
    # Generate angles based on the number of variables
    angles = np.linspace(0, 2 * np.pi, num_categories, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    # Create the plot
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection="polar"))
    ax.plot(
        angles,
        player1_data,
        "o-",
        linewidth=2,
        label=batsmen_selected[0],
    )
    ax.fill(angles, player1_data, alpha=0.25)
    ax.plot(
        angles,
        player2_data,
        "o-",
        linewidth=2,
        label=batsmen_selected[1],
    )
    ax.fill(angles, player2_data, alpha=0.25)
    labels_with_percentiles = [
        f"{category} ({int(percentile)}%)"
        for category, percentile in zip(categories, values)
    ]
    # Set the labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color="blue", size=10)
    ax.set_yticks([0.25, 0.50, 0.75, 1.0])
    # ax.set_yticklabels(values, color="grey", size=7)
    ax.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))

    plt.title("Player Comparison")
    plt.tight_layout()
    # Display the chart in Streamlit
    st.pyplot(fig)

cursor.close()
