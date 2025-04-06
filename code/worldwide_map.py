import folium
import pandas as pd
import geopandas as gpd
from folium.features import GeoJsonTooltip
from branca.colormap import linear

# Load data
df = pd.read_csv(
    "../data/clean_data/cleaned_security_incidents.csv", parse_dates=["date"]
)
df_geo = df.dropna(subset=["latitude", "longitude"])

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(
    df_geo,
    geometry=gpd.points_from_xy(df_geo["longitude"], df_geo["latitude"]),
    crs="EPSG:4326",
)

# Load world shapefile
world = gpd.read_file(
    "../data/maps/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
)
world = world[~world["ADMIN"].isin(["Antarctica"])]

# Aggregate incidents by country
incident_counts = gdf.groupby("country")["incident_id"].count().reset_index()
incident_counts.columns = ["country", "incident_count"]
world = world.merge(incident_counts, left_on="ADMIN", right_on="country", how="left")
world["incident_count"] = world["incident_count"].fillna(0)

# Color scale
colormap = linear.OrRd_09.scale(
    world["incident_count"].min(), world["incident_count"].max()
)
colormap.caption = "Number of Security Incidents"

# Create base map with ocean-colored tiles
m = folium.Map(
    location=[10, 20],
    zoom_start=2.5,
    min_zoom=2.5,
    max_bounds=True,
    tiles="CartoDB Positron",  # pale blue ocean
)


# Choropleth styling
def style_function(feature):
    count = feature["properties"]["incident_count"]
    return {
        "fillColor": colormap(count),
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.7,
    }


# Tooltip
tooltip = GeoJsonTooltip(
    fields=["ADMIN", "incident_count"],
    aliases=["Country:", "Security Incidents:"],
    localize=True,
    sticky=True,
    style=(
        "background-color: white; color: #333; font-family: sans-serif; font-size: 13px; "
        "padding: 5px; border-radius: 5px; box-shadow: 1px 1px 2px rgba(0,0,0,0.25);"
    ),
)

# Add choropleth to map
folium.GeoJson(
    world, name="Choropleth", style_function=style_function, tooltip=tooltip
).add_to(m)

for _, row in gdf.iterrows():
    popup_html = f"""
    <strong>Date:</strong> {row['date'].strftime('%Y-%m-%d')}<br>
    <strong>Country:</strong> {row['country']}<br>
    <strong>Region:</strong> {row['region']}<br>
    <strong>Means of Attack:</strong> {row['means_of_attack']}<br>
    <strong>Killed:</strong> {row['total_killed']}<br>
    <strong>Wounded:</strong> {row['total_wounded']}<br>
    <strong>Kidnapped:</strong> {row['total_kidnapped']}
    """

    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=2,
        color="#5e3c99",  # muted violet border
        fill=True,
        fill_color="#b2abd2",  # soft purple fill
        fill_opacity=0.45,
        popup=folium.Popup(popup_html, max_width=300),
    ).add_to(m)


# Add color legend
colormap.add_to(m)
m = folium.Map(...)
m
m.save("../outputs/security_incidents_interactive_map.html")
