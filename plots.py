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


# victim outcomes

from plotly.subplots import make_subplots
import plotly.graph_objects as go

outcome_data = {
    "Victim Type": ["National"] * 3 + ["International"] * 3,
    "Outcome": ["Killed", "Wounded", "Kidnapped"] * 2,
    "Count": [
        df["nationals_killed"].sum(),
        df["nationals_wounded"].sum(),
        df["nationals_kidnapped"].sum(),
        df["internationals_killed"].sum(),
        df["internationals_wounded"].sum(),
        df["internationals_kidnapped"].sum(),
    ],
}

plot_df = pd.DataFrame(outcome_data)

nationals = plot_df[plot_df["Victim Type"] == "National"]
internationals = plot_df[plot_df["Victim Type"] == "International"]

_ = fig = make_subplots(
    rows=1,
    cols=2,
    specs=[[{"type": "domain"}, {"type": "domain"}]],
    subplot_titles=["National Aid Workers", "International Aid Workers"],
)

_ = fig.add_trace(
    go.Pie(
        labels=nationals["Outcome"],
        values=nationals["Count"],
        name="Nationals",
        hole=0.5,
        marker=dict(colors=px.colors.qualitative.Antique),
    ),
    1,
    1,
)

_ = fig.add_trace(
    go.Pie(
        labels=internationals["Outcome"],
        values=internationals["Count"],
        name="Internationals",
        hole=0.5,
        marker=dict(colors=px.colors.qualitative.Antique),
    ),
    1,
    2,
)

fig.update_layout(
    title_text="Victim Outcomes by Aid Worker Type",
    title_x=0.5,
    title={"font": {"weight": "bold"}},
    annotations=[
        dict(text="Nationals", x=0.18, y=0.5, font_size=14, showarrow=False),
        dict(text="Internationals", x=0.82, y=0.5, font_size=14, showarrow=False),
    ],
    height=500,
    margin=dict(t=80),
)

pio.write_html(
    fig,
    file="outputs/national_international.html",
    include_plotlyjs="cdn",
    full_html=False,
    config={"responsive": True},
)
