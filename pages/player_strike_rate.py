# Import python packages
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess
import sys

# USED THIS TO FIX INCOMPABITILITY OF PYTHON VERSION - ONE TIME IS ENOUGH
# def install(package):
#    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
# install("snowflake-connector-python")

import snowflake.connector

# from snowflake.snowpark.functions import col
# from snowflake.snowpark.functions import when_matched
# from snowflake.snowpark.session import Session
from snowflake.connector import connect
import requests
import os

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

# get all the batsman who have faced more than 60 balls

batsman_list_query = (
    f"select batsman_name from ipl group by batsman_name having count(distinct id) > 60"
)
cursor.execute(batsman_list_query)  # .to_pandas()
batsman_df = cursor.fetch_pandas_all()

# Write directly to the app
st.title("IPL 2024 Data")
batsman_selected = st.selectbox("Select a batsman: ", batsman_df)

batsman_strike_rate_query = f"select truncate(sum(batsman_runs)/count(distinct id),1)*100 as strike_rate from ipl where batsman_name = '{batsman_selected}'"
submitted = st.button("Submit")


cursor.execute(batsman_strike_rate_query)
batsman_avg_SR = cursor.fetch_pandas_all()

# get the average strike rate of the batsman
avg_SR = batsman_avg_SR["STRIKE_RATE"][0]

# st.success('someone clicked the button')
if submitted:

    # try:
    batsman_SR_by_line_length_query = f"select truncate(sum(batsman_runs)/count(distinct id),1)*100 as strike_rate,bowling_length_name as length,bowling_line_name as line from ipl where batsman_name = '{batsman_selected}' group by line, length;"
    cursor.execute(batsman_SR_by_line_length_query)
    batsman_avg_SR_line_length_df = cursor.fetch_pandas_all()

    # print(batsman_avg_SR_line_length_df.columns)  #
    # print(batsman_avg_SR_line_length_df.index)
    batsman_avg_SR_line_length_df["strike_rate"] = pd.to_numeric(
        batsman_avg_SR_line_length_df["STRIKE_RATE"], errors="coerce"
    )
    strike_rates_grid = batsman_avg_SR_line_length_df.pivot(
        index="LENGTH", columns="LINE", values="STRIKE_RATE"
    )
    # Convert all values in the grid to numeric, replacing any non-convertible values with NaN
    strike_rates_grid = strike_rates_grid.apply(pd.to_numeric, errors="coerce")

    # Fill NaN values with 0 or another appropriate value
    strike_rates_grid = strike_rates_grid.fillna(0)

    player_data = strike_rates_grid.values

    # Get row and column labels
    lengths = strike_rates_grid.index.to_list()
    lines = strike_rates_grid.columns.to_list()

    avg_SR = pd.to_numeric(avg_SR)
    mask = player_data > avg_SR
    zero_mask = player_data == 0
    mask = mask | zero_mask

    fig, ax = plt.subplots(figsize=(12, 9))
    sns.heatmap(
        player_data,
        annot=True,
        fmt=".1f",
        cmap="Reds",
        center=avg_SR,
        linewidths=0.5,
        mask=~mask,
        ax=ax,
    )
    sns.heatmap(
        player_data,
        annot=True,
        fmt=".1f",
        cmap="Reds_r",
        center=avg_SR,
        linewidths=0.5,
        cbar=False,
        mask=mask,
        ax=ax,
    )

    # Customize the colors
    cbar = ax.collections[0].colorbar
    cbar.set_label("Strike Rate")

    # Add labels and title
    ax.set_xlabel("Ball Line")
    ax.set_ylabel("Ball Length")

    # Set x-axis ticks and labels
    ax.set_xticks(np.arange(len(lines)) + 0.5)
    ax.set_xticklabels(lines, rotation=45, ha="right")

    # Set y-axis ticks and labels
    ax.set_yticks(np.arange(len(lengths)) + 0.5)
    ax.set_yticklabels(lengths, rotation=0)

    plt.title("Player SR by Line & Length vs Player Average SR")

    # Add a text annotation for the league average
    plt.text(
        1.05,
        0.5,
        f"Batsman Average SR: {avg_SR:.1f}",
        rotation=90,
        verticalalignment="center",
        transform=ax.transAxes,
    )

    plt.tight_layout()
    plt.show()
    cursor.close()
    conn.close()
    # Display the plot in Streamlit
    st.pyplot(fig)
