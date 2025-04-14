import dash
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px

# Загрузка данных
geolocation = pd.read_csv('../cohort_analysis/clear_data/geolocation.csv')


def calc_means_in_group(group):
    group_unique = group.drop_duplicates(subset=['geolocation_lat', 'geolocation_lng'])
    mean_unique_lat = np.mean(group_unique['geolocation_lat'])
    mean_unique_lng = np.mean(group_unique['geolocation_lng'])
    res_group = pd.Series({
        'lat_d_mean': mean_unique_lat,
        'lng_d_mean': mean_unique_lng,
        'city': group['geolocation_city'].value_counts().index[0],
        'state': group['geolocation_state'].value_counts().index[0]
    })
    return res_group


mean_points = (geolocation.groupby('geolocation_zip_code_prefix')[[
    'geolocation_lat',
    'geolocation_lng',
    'geolocation_city',
    'geolocation_state']]
               .apply(calc_means_in_group)
               .reset_index())

real_points = geolocation.assign(
    points_count=geolocation.groupby('geolocation_zip_code_prefix')['geolocation_zip_code_prefix'].transform('count')
)


# Группировка данных по почтовому индексу (можно взять средние координаты)
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Анализ геолокации по почтовым индексам", style={'textAlign': 'center'}),

    html.Div([
        dcc.Dropdown(
            id='state-selector',
            options=[{'label': state, 'value': state}
                     for state in sorted(mean_points['state'].unique())],
            multi=True,
            placeholder="Выберите штат(ы)",
            style={'width': '50%', 'margin': '3px'}
        ),
        dcc.Dropdown(
            id='code-selector',
            options=[{'label': code, 'value': code}
                     for code in sorted(mean_points['geolocation_zip_code_prefix'].unique())],
            multi=True,
            placeholder="Выберите zip код(ы)",
            style={'width': '50%', 'margin': '3px'}
        ),
        dcc.RadioItems(
            id='coord-type',
            options=[
                {'label': 'Все точки', 'value': 'all'},
                {'label': 'Средние по уникальным координатам', 'value': 'unique_mean'}
            ],
            value='unique_mean',
            style={'margin': '5px'}
        )
    ], style={'display': 'flex', 'flexDirection': 'column'}),

    dcc.Graph(
        id='map-plot',
        style={'height': '74vh'},
        config={'scrollZoom': True}  # Включаем zoom колёсиком здесь
    ),

    html.Div([
        html.H3("Координаты выбранной точки:"),
        html.Div(id='click-data', style={
            'border': '1px solid #ddd',
            'padding': '10px',
            'margin': '10px',
            'backgroundColor': '#f9f9f9'
        }),
        html.Button("Копировать координаты", id="copy-btn"),
        html.Div(id='copy-status')
    ], style={'margin': '20px'})
])

filtered_df = real_points


@app.callback(
    Output('map-plot', 'figure'),
    [Input('state-selector', 'value'),
     Input('code-selector', 'value'),
     Input('coord-type', 'value')]
)
def update_map(selected_states, selected_codes, coord_type):
    if coord_type == 'all':
        filtered_df = real_points.copy()
        if selected_codes or selected_states:
            if selected_codes:
                filtered_df = filtered_df[filtered_df['geolocation_zip_code_prefix'].isin(selected_codes)]
            if selected_states:
                filtered_df = filtered_df[filtered_df['geolocation_state'].isin(selected_states)]
        else:
            filtered_df = filtered_df[filtered_df['geolocation_state'].isin('/////')]
        fig = px.scatter_mapbox(
            filtered_df,
            lat='geolocation_lat',
            lon='geolocation_lng',
            hover_name="geolocation_city",
            hover_data={
                "geolocation_lat": True,
                "geolocation_lng": True,
                "geolocation_state": True,
                "geolocation_zip_code_prefix": True,
                "points_count": True,
            },
            height=800,
            color_discrete_sequence=["red"]
        )

        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            hovermode='closest'
        )

        fig.update_traces(
            hovertemplate=(
                    "<b>%{hovertext}(%{customdata[4]})</b><br><br>" +
                    "Почтовый индекс: %{customdata[3]}<br>" +
                    "Штат: %{customdata[2]}<br>" +
                    "Координаты: (%{customdata[0]:.4f}, %{customdata[1]:.4f})"
            )
        )
    else:
        filtered_df = mean_points.copy()
        if selected_codes:
            filtered_df = filtered_df[filtered_df['geolocation_zip_code_prefix'].isin(selected_codes)]
        if selected_states:
            filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]


        fig = px.scatter_mapbox(
            filtered_df,
            lat='lat_d_mean',
            lon='lng_d_mean',
            hover_name="city",
            hover_data={
                "lat_d_mean": True,
                "lng_d_mean": True,
                "state": True,
                "geolocation_zip_code_prefix": True
            },
            height=800,
            color_discrete_sequence=["blue"]
        )

        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            mapbox=dict(
                center=dict(
                    lat=filtered_df['lat_d_mean'].mean(),
                    lon=filtered_df['lng_d_mean'].mean()
                )
            ),
            # Включение интерактивности
            clickmode='event+select',
            dragmode='pan'
        )

        # Улучшаем отображение подсказки
        fig.update_traces(
            hovertemplate=(
                    "<b>%{hovertext}</b><br><br>" +
                    "Почтовый индекс: %{customdata[2]}<br>" +
                    "Штат: %{customdata[3]}<br>" +
                    "Средние координаты: (%{customdata[0]:.4f}, %{customdata[1]:.4f})"
            )
        )

    return fig


@app.callback(
    Output('click-data', 'children'),
    [Input('map-plot', 'clickData')]
)
def display_click_data(clickData):
    if clickData is None:
        return "Кликните на точку на карте, чтобы увидеть её координаты"

    point = clickData['points'][0]
    lat = point['lat']
    lon = point['lon']

    return html.Div([
        html.P(f"Широта: {lat:.6f}"),
        html.P(f"Долгота: {lon:.6f}"),
        html.P(f"Город: {point.get('hovertext', 'N/A')}"),
        html.P(
            f"Почтовый индекс: {point['customdata'][3] if 'customdata' in point and len(point['customdata']) > 3 else 'N/A'}")
    ])


@app.callback(
    Output('copy-status', 'children'),
    [Input('copy-btn', 'n_clicks')],
    [State('click-data', 'children')]
)
def copy_coordinates(n_clicks, click_data):
    if n_clicks is None or click_data is None:
        return ""

    # Извлекаем координаты из текста
    try:
        lat_line = \
        [c['props']['children'] for c in click_data['props']['children'] if 'Широта' in str(c['props']['children'])][0]
        lon_line = \
        [c['props']['children'] for c in click_data['props']['children'] if 'Долгота' in str(c['props']['children'])][0]

        lat = lat_line.split(": ")[1]
        lon = lon_line.split(": ")[1]

        # Формируем текст для копирования
        text_to_copy = f"{lat}, {lon}"

        # В реальном приложении здесь должен быть JavaScript для копирования в буфер
        return f"Координаты {text_to_copy} скопированы в буфер (в реальном приложении)"
    except:
        return "Ошибка при копировании"


if __name__ == '__main__':
    app.run(debug=True)
