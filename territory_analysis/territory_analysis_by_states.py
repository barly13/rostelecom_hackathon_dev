from dash import Dash, html, dcc
import plotly.graph_objects as go
import json
import pandas as pd
import tqdm
from datetime import datetime, timedelta


products = pd.read_csv("../cohort_analysis/clear_data/products.csv")
orders = pd.read_csv("../cohort_analysis/clear_data/orders.csv")
customers = pd.read_csv("../cohort_analysis/clear_data/customers.csv")
geolocation = pd.read_csv("../cohort_analysis/clear_data/geolocation.csv")
order_payments = pd.read_csv("../cohort_analysis/clear_data/order_payments.csv")
order_reviews = pd.read_csv("../cohort_analysis/clear_data/order_reviews.csv")
orders_items = pd.read_csv("../cohort_analysis/clear_data/orders_items.csv")
sellers = pd.read_csv("../cohort_analysis/clear_data/sellers.csv")
product_category_name_translation = pd.read_csv("../cohort_analysis/clear_data/product_category_name_translation.csv")

rfm_analysis = pd.read_csv("../rfm_analysis/rfm_data/rfm_analysis.csv")
data = rfm_analysis[["customer_unique_id", "recency_days"]].merge(customers, on="customer_unique_id")[["customer_unique_id", "recency_days", "customer_state"]].drop_duplicates()

states_names = ['RJ', 'SP', 'MG', 'PE', 'PR', 'SC', 'GO', 'RR', 'MT', 'RS', 'PI',
       'BA', 'ES', 'AL', 'DF', 'SE', 'AM', 'MA', 'CE', 'PA', 'TO', 'MS',
       'RO', 'PB', 'RN', 'AC', 'AP']

states_values = {}
for name in states_names:
    states_values[name] = dict(overall=len(data[data.customer_state == name]), fired=len(data[(data.customer_state == name) & (data.recency_days > 231)]))

min_pers = min([el[1]["fired"]/el[1]["overall"] for el in states_values.items()])
max_pers = max([el[1]["fired"]/el[1]["overall"] for el in states_values.items()])
delta = max_pers - min_pers

with open('territory_data/brazil_geo.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

app = Dash(__name__)
fig = go.Figure()

for feature in data["features"]:
    type = feature["geometry"]["type"]
    if type == "Polygon":
        coords = feature["geometry"]["coordinates"][0][::10]
        name = feature["id"]
        state_meta = states_values[name]
        percentage =  (state_meta["fired"] / state_meta["overall"])
        fig.add_trace(go.Scattermap(
            mode="lines",
            lon=[coord[0] for coord in coords],
            lat=[coord[1] for coord in coords],
            line=dict(width=2, color='blue'),
            fill='toself',
            fillcolor=f'rgba(0, 0, 255, {percentage})',
            hoverinfo='none',
            name=name
        ))
        center_lat = (max(coord[1] for coord in coords[:-1]) + min(coord[1] for coord in coords[:-1])) / 2
        center_lon = (max(coord[0] for coord in coords[:-1]) + min(coord[0] for coord in coords[:-1])) / 2
        fig.add_trace(go.Scattermap(
            mode="markers",
            lon=[center_lon],
            lat=[center_lat],
            marker=dict(
                size=10,
                color='red',
                opacity=0.8
            ),
            text=[f"{name}: {state_meta['fired']}/{state_meta['overall']} ({percentage*100:.1f}%)"],
            hoverinfo='text',
            name="Точка",
            showlegend=False
        ))
    elif type == "MultiPolygon":
        coords = sorted(feature["geometry"]["coordinates"], key=lambda x: -len(x[0]))
        name = feature["id"]
        for coord in coords[:1]:
            coord = coord[0][::10]
            state_meta = states_values[name]
            percentage = (state_meta["fired"] / state_meta["overall"])# - min_pers) / delta

            fig.add_trace(go.Scattermap(
                mode="lines",
                lon=[coord[0] for coord in coord],
                lat=[coord[1] for coord in coord],
                line=dict(width=2, color='blue'),
                fill='toself',
                fillcolor=f'rgba(0, 0, 255, {percentage})',
                hoverinfo='none',
                name=name
            ))
            center_lat = (max(coord[1] for coord in coord) + min(coord[1] for coord in coord)) / 2
            center_lon = (max(coord[0] for coord in coord) + min(coord[0] for coord in coord)) / 2
            fig.add_trace(go.Scattermap(
                mode="markers",
                lon=[center_lon],
                lat=[center_lat],
                marker=dict(
                    size=10,
                    color='red',
                    opacity=0.8
                ),
                text=[f"{name}: {state_meta['fired']}/{state_meta['overall']} ({percentage*100:.1f}%)"],
                hoverinfo='text',
                name="Точка",
                showlegend=False
            ))



# Настройки карты
fig.update_layout(
    mapbox=dict(
        style="open-street-map",
        zoom=9
        # center=dict(lat=center_lat, lon=center_lon)
    ),
    margin={"r":0,"t":0,"l":0,"b":0},
    height=600
)

app.layout = html.Div([
    html.H1("Полигон с интерактивной точкой", style={'textAlign': 'center'}),
    dcc.Graph(
        id='map',
        figure=fig,
        config={'scrollZoom': True}
    )
])

if __name__ == '__main__':
    app.run(debug=True)