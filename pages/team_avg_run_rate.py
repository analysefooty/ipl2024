# Import python packages
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

team_query = f"SELECT distinct TEAM_NAME from CRICKETDB.C50.runs_by_over"
cursor.execute(team_query)  # .to_pandas()
team_df = cursor.fetch_pandas_all()

# Write directly to the app
st.title("IPL 2024 Data")
team_selected = st.selectbox("Select a team: ", team_df)

ipl_rpo_avg_query = f"SELECT (over_number+1) as over, TRUNCATE(AVG(total_runs),1) as RPO, 'overall' as team from CRICKETDB.C50.runs_by_over group by over_number"
cursor.execute(ipl_rpo_avg_query)
rpo_df = cursor.fetch_pandas_all()
submitted = st.button("Submit")
# st.success('someone clicked the button')
if submitted:

    # try:
    runs_query = f"SELECT (over_number+1) as over, TRUNCATE(AVG(total_runs),1) as RPO,'{team_selected}' as team  from CRICKETDB.C50.runs_by_over  where team_name ='{team_selected}' group by over_number"
    cursor.execute(runs_query)
    runs_pandas_df = cursor.fetch_pandas_all()
    # runs_pandas_df = runs_df.to_pandas()
    # editable_df = st.data_editor(runs_df)
    overall_df = pd.concat([rpo_df, runs_pandas_df], ignore_index=True)
    overall_df_pivot = overall_df.pivot(
        index="OVER", columns="TEAM", values="RPO"
    ).fillna(0)
    fig, ax = plt.subplots(figsize=(10, 6))

    # define colors and bar width
    colors = ["#FF9999", "#66B2FF"]
    bar_width = 0.4

    categories = overall_df_pivot.index
    x = np.arange(len(categories))

    for i, group in enumerate(overall_df_pivot.columns):
        bars = ax.bar(
            x + i * bar_width,
            overall_df_pivot[group],
            width=bar_width,
            label=group,
            color=colors[i],
        )
        for j, bar in enumerate(bars):
            height = bar.get_height()
            label = overall_df_pivot[group].iloc[j]
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{label}",
                ha="center",
                va="bottom",  # Optional: rotate label for better fit
            )
    # this is for stacked bars
    # bottom = pd.Series([0] * overall_df_pivot.shape[0], index=overall_df_pivot.index)

    # for i, group in enumerate(overall_df_pivot.columns):
    #    ax.bar(overall_df_pivot.index, overall_df_pivot[group], label=group, bottom=bottom, color=colors[i])
    #    bottom += overall_df_pivot[group]
    # bars = ax.bar(overall_df['OVER'], overall_df['RPO'], color=overall_df['TEAM'])

    # Customize the plot
    ax.set_title("Runs Per Over", fontsize=16)
    ax.set_xlabel("Over #", fontsize=12)
    ax.set_ylabel("Avg Runs Scored", fontsize=12)
    ax.set_xticks(x + bar_width * (len(overall_df_pivot.columns) - 1) / 2)
    ax.set_xticklabels(categories)
    ax.legend()

    # Add grid lines
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Adjust layout
    plt.tight_layout()
    cursor.close()
    conn.close()
    # Display the plot in Streamlit
    st.pyplot(fig)
