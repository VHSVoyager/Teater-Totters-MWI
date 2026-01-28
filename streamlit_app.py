import altair as alt
import pandas as pd
import streamlit as st
from datetime import timedelta

# Show the page title and description.
st.set_page_config(page_title="Teater Totters", page_icon="🐮")
st.title("🐮 Teater Totters")
st.write(
    """
    Guild Data Visualizer!
    """
)

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/tt_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df


df = load_data()

# Show a multiselect widget with the Names using `st.multiselect`.
members = st.multiselect(
    "Members",
    df.Name.unique(),
    [],
)

# Show a slider widget with the Dates using `st.slider`.
dates = st.slider("Date", 
                  df['Date'].min().to_pydatetime(), 
                  df['Date'].max().to_pydatetime(), 
                 (df['Date'].min().to_pydatetime(), df['Date'].max().to_pydatetime()),
                 step=timedelta(days=7))

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[(df["Name"].isin(members)) & (df["Date"].between(dates[0], dates[1]))]
df_reshaped = df_filtered.pivot_table(
    index="Date", columns="Name", values="Experience", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="Date", ascending=True)


# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_reshaped,
    width='content',
    column_config={"Date": st.column_config.DatetimeColumn("Date", format='MMM D, YYYY', width='auto')},
)

# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="Date", var_name="Name", value_name="gross"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("gross:Q", title="Total Experience", scale=alt.Scale(domain=[df_chart['gross'].min()-50000,df_chart['gross'].max()+50000])),
        color="Name:N",
    )
    .properties(height=320)
)
if(members):
    st.altair_chart(chart, use_container_width=True)
