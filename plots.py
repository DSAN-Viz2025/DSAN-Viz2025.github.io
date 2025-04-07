import plotly.express as px
import plotly.io as pio
import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv("data/clean_data/cleaned_security_incidents.csv", parse_dates=["date"])


df["year"] = df["date"].dt.year
# Group and count incidents by year and attack type
df_yearly = df.groupby(["year", "means_of_attack"]).size().reset_index(name="count")

# Plotly line chart
fig = px.line(
    df_yearly,
    x="year",
    y="count",
    color="means_of_attack",
    title="Trends in Means of Attack Over Time",
    labels={"count": "Number of Incidents", "year": "Year"},
)

fig.update_layout(
    legend_title_text="Means of Attack",
    title_x=0.5,
    title={"font": {"weight": "bold"}},
    height=600,
)

pio.write_html(
    fig,
    file="outputs/trends_over_time.html",
    include_plotlyjs="cdn",
    full_html=False,
    config={"responsive": True},
)


# break

# Drop rows missing essential info
df = df.dropna(subset=["latitude", "longitude", "means_of_attack"])

# Group and aggregate by location and attack type
bubble_df = (
    df.groupby(["latitude", "longitude", "country", "means_of_attack"])
    .agg({"total_killed": "sum", "total_wounded": "sum", "total_kidnapped": "sum"})
    .reset_index()
)

# Rename column for cleaner display
bubble_df.rename(columns={"means_of_attack": "Means of Attack"}, inplace=True)
bubble_df.rename(columns={"total_killed": "Total Killed"}, inplace=True)
bubble_df.rename(columns={"total_wounded": "Total Wounded"}, inplace=True)
bubble_df.rename(columns={"total_kidnapped": "Total Kidnapped"}, inplace=True)


# Create the map
fig = px.scatter_geo(
    bubble_df,
    lat="latitude",
    lon="longitude",
    color="Means of Attack",
    size="Total Killed",  #
    hover_name="country",
    hover_data={
        "Total Killed": True,
        "Total Wounded": True,
        "Total Kidnapped": True,
        "latitude": False,
        "longitude": False,
    },
    projection="natural earth",
    title="Fatal Incidents by Location and Means of Attack",
    size_max=30,
)

fig.update_geos(showocean=True, oceancolor="LightBlue")
# Tidy layout
fig.update_layout(
    title_x=0.5,
    title={"font": {"weight": "bold"}},  # Make the title bold
    legend_title_text="Means of Attack",
    geo=dict(
        showland=True,
        landcolor="rgb(229, 229, 229)",
        showcountries=True,
        showcoastlines=True,
        projection_type="natural earth",
    ),
)


pio.write_html(
    fig,
    file="outputs/attack_type_world.html",
    include_plotlyjs="cdn",
    full_html=False,
    config={"responsive": True},
)
