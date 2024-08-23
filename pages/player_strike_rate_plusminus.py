import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import sys

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
cursor = conn.cursor()

teams_list = f"select distinct BATTING_TEAM_NAME from ipl order by BATTING_TEAM_NAME"
cursor.execute(teams_list)  # .to_pandas()
teams_list_df = cursor.fetch_pandas_all()

st.title("IPL 2024 Data - Player Strike Rate Plus Minus")
st.text("Weighted average of player strike rate normalized at match level")
st.text("0 = Player SR = Team SR, + = Player SR > Team SR, - = Player SR < Team SR")
st.text("Balls faces in braces. Minimum 10 balls faced")

team_selected = st.selectbox("Select a team: ", teams_list_df)

sr_plusminus_query = f"""SELECT 
    BATSMAN_NAME,
    SUM(BATSMAN_BALLS_FACED) AS TOTAL_BALLS_FACED,
    TEAM_NAME,
    SUM(BATSMAN_SR_ABOVE_TEAM * BATSMAN_BALLS_FACED) / SUM(BATSMAN_BALLS_FACED) AS SR_ABOVE_TEAM,
    SUM(BATSMAN_SR_PLUSMINUS * BATSMAN_BALLS_FACED) / SUM(BATSMAN_BALLS_FACED) AS SR_ABOVE_PLUSMINUS
FROM
    AGGREGATE_RUNS
WHERE
       TEAM_NAME = '{team_selected}'
GROUP BY
    BATSMAN_NAME, TEAM_NAME

HAVING TOTAL_BALLS_FACED > 10
ORDER BY
    SR_ABOVE_PLUSMINUS
"""
cursor.execute(sr_plusminus_query)  # .to_pandas()
sr_plusminus_df = cursor.fetch_pandas_all()

fig, ax = plt.subplots(figsize=(10, 8))  # Adjusted figure size for better visibility

# define colors and bar width
colors = ["#FF9999"]
bar_height = 0.8  # Changed from bar_width to bar_height
bar_width = 0.8
categories = sr_plusminus_df["BATSMAN_NAME"]
y = np.arange(len(categories))  # Changed from x to y

for i, group in enumerate(["SR_ABOVE_PLUSMINUS"]):
    bars = ax.barh(  # Changed from bar to barh
        y,  # + i * bar_height,
        sr_plusminus_df[group],
        height=bar_height,  # Changed from width to height
        color=colors[i],
        label=group,
    )
    for j, bar in enumerate(bars):
        width = bar.get_width()  # Changed from height to width
        label = sr_plusminus_df[group].iloc[j]
        balls_faced = sr_plusminus_df["TOTAL_BALLS_FACED"].iloc[j]
        ax.text(
            width,  # x and y coordinates are swapped
            bar.get_y() + bar.get_height() / 2,
            f"{label:.1f}({balls_faced})",
            ha="left",  # Changed from "center" to "left"
            va="center",  # Changed from "bottom" to "center"
            # xytext=(5, 0),  # Added some padding
            # textcoords="offset points",
        )

    # Customize the plot
ax.set_title("Runs Per Over", fontsize=16)
ax.set_xlabel("Strike Above/Below Team Innings Average", fontsize=12)
# ax.set_ylabel("Players", fontsize=12)
ax.set_yticks(y)  # * (len(sr_plusminus_df.columns) - 1) / 2)
ax.set_yticklabels(categories)
ax.legend()

# Add grid lines
# ax.grid(axis="y", linestyle="--", alpha=0.7)

# Adjust layout
plt.tight_layout()
cursor.close()
conn.close()
# Display the plot in Streamlit
st.pyplot(fig)
