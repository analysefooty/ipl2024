# Import python packages
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from snowflake.snowpark.functions import col
#from snowflake.snowpark.functions import when_matched
#from snowflake.snowpark.session import Session
from snowflake.connector import connect
import requests


# Get the current credentials
cnx = st.connection("snowflake")
session = cnx.session()
#session = get_active_session()
conn = connect(
    account=st.secrets["snowflake"]["account"],
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"]
)
#teams query
cursor = conn.cursor()

team_query = f"SELECT distinct TEAM_NAME from CRICKETDB.C50.runs_by_over"
team_df = cursor.sql(team_query).to_pandas()

# Write directly to the app
st.title("IPL 2024 Data")
team_selected = st.selectbox("Select a team: ", team_df )

ipl_rpo_avg_query = f"SELECT (over_number+1) as over, TRUNCATE(AVG(total_runs),1) as RPO, 'overall' as team from CRICKETDB.C50.runs_by_over group by over_number"
rpo_df = cursor.sql(ipl_rpo_avg_query).to_pandas()
submitted = st.button('Submit')
#st.success('someone clicked the button')
if submitted:
    
    #try:
        runs_query = f"SELECT (over_number+1) as over, TRUNCATE(AVG(total_runs),1) as RPO,'{team_selected}' as team  from CRICKETDB.C50.runs_by_over  where team_name ='{team_selected}' group by over_number"
        runs_df = cursor.sql(runs_query)
        runs_pandas_df = runs_df.to_pandas()
        #editable_df = st.data_editor(runs_df) 
        overall_df = pd.concat([rpo_df,runs_pandas_df],ignore_index=True)
        overall_df_pivot = overall_df.pivot(index='OVER', columns='TEAM',values='RPO').fillna(0)
        fig, ax = plt.subplots(figsize=(10, 6))

        #define colors and bar width
        colors = ['#FF9999', '#66B2FF']
        bar_width = 0.25

        categories = overall_df_pivot.index
        x = np.arange(len(categories))

        for i, group in enumerate(overall_df_pivot.columns):
            ax.bar(x+i*bar_width, overall_df_pivot[group],width=bar_width,label=group,color=colors[i])

        # this is for stacked bars
        #bottom = pd.Series([0] * overall_df_pivot.shape[0], index=overall_df_pivot.index)

        #for i, group in enumerate(overall_df_pivot.columns):
        #    ax.bar(overall_df_pivot.index, overall_df_pivot[group], label=group, bottom=bottom, color=colors[i])
        #    bottom += overall_df_pivot[group]
        #bars = ax.bar(overall_df['OVER'], overall_df['RPO'], color=overall_df['TEAM'])
      
        # Customize the plot
        ax.set_title('Runs Per Over', fontsize=16)
        ax.set_xlabel('Over #', fontsize=12)
        ax.set_ylabel('Avg Runs Scored', fontsize=12)
        ax.set_xticks(x + bar_width * (len(overall_df_pivot.columns) - 1) / 2)
        ax.set_xticklabels(categories)
        ax.legend()

        # Add grid lines
        ax.grid(axis='y', linestyle='--', alpha=0.7)

# Adjust layout
        plt.tight_layout()

# Display the plot in Streamlit
        st.pyplot(fig)
