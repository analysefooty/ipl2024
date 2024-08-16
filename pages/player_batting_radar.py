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
batsman_selected = st.selectbox("Select a batsman: ", batsman_df)
submitted = st.button("Submit")

if submitted:
    batsman_percentile_query = f"select batsman_name, match_phase, sr_percentile from AGG_RUNS_BY_MATCH_PHASE where batsman_name = '{batsman_selected}'"
    cursor.execute(batsman_percentile_query)  # .to_pandas()
    percentile_data_df = cursor.fetch_pandas_all()
    categories = percentile_data_df["MATCH_PHASE"].tolist()
    # st.selectbox("categories", categories)

    values = (percentile_data_df["SR_PERCENTILE"].values * 100).tolist()

    num_vars = len(values)  # Set num_vars to the length of your data

    # Generate angles based on the number of variables
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Close the plot by appending the start value to the end
    values += values[:1]
    # st.selectbox("values", values)

    angles += angles[:1]

    # Create the plot
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection="polar"))
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.25)
    labels_with_percentiles = [
        f"{category} ({int(percentile)}%)"
        for category, percentile in zip(categories, values)
    ]
    # Set the labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels_with_percentiles, color="blue", size=10)
    ax.set_yticks([25, 50, 75, 100])
    # ax.set_yticklabels(values, color="grey", size=7)

    # Display the chart in Streamlit
    st.pyplot(fig)
