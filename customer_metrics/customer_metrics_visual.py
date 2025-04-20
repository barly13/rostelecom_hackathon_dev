import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import datetime


# Генерация данных
def generate_data():
    dates = pd.date_range(start='2023-01-01', periods=30)
    values = [10 + i * 0.5 + (i % 3) * 2 for i in range(30)]
    return pd.DataFrame({'Дата': dates, 'Значение': values})

def get_dau_data():
    import os
    current_dir = os.path.dirname(__file__)
    return pd.read_csv(f"{current_dir}/customer_metrics_data/dau.csv")

def get_mau_data():
    import os
    current_dir = os.path.dirname(__file__)
    return pd.read_csv(f"{current_dir}/customer_metrics_data/mau.csv")

def get_retention_1():
    import os
    current_dir = os.path.dirname(__file__)
    return pd.read_csv(f"{current_dir}/customer_metrics_data/retention_1_month.csv")

def get_retention_3():
    import os
    current_dir = os.path.dirname(__file__)
    return pd.read_csv(f"{current_dir}/customer_metrics_data/retention_analysis.csv")

dau_data = get_dau_data()
mau_data = get_mau_data()
retention_1 = get_retention_1()
retention_3 = get_retention_3()

# app = dash.Dash(__name__)

def get_app_layout():
   return html.Div([
        html.H3("DAU", style={'textAlign': 'center'}),
        dcc.Graph(
            id='dau-plot',
            figure={
                'data': [go.Scatter(
                    x=dau_data['date_day'],
                    y=dau_data['count'],
                    mode='lines+markers',
                    line=dict(color='blue', width=2),
                    marker=dict(color='black', size=8),
                    hovertemplate=(
                        "<b>Дата</b>: %{x|%d %b %Y}<br>"  # Формат месяца и года
                        "<b>DAU</b>: %{y:,}<br>"  # Разделители тысяч для чисел
                        "<extra></extra>"  # Убираем лишнюю инфо
                    ),
                )
                ],
                'layout': {
                    'dragmode': 'pan',  # Только перемещение по ЛКМ
                    'xaxis': {
                        'fixedrange': False,  # Разрешаем масштабирование по X
                    },
                    'yaxis': {
                        'fixedrange': True  # Фиксируем масштаб по Y
                    }
                }
            },
            config={
                'scrollZoom': True,  # Включаем масштабирование (boolean, не строка)
                'modeBarButtonsToRemove': ['zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d']  # Убираем ненужные кнопки
            },
            style={'height': '70vh'}
        ),
        html.Div("ЛКМ: перемещение | Колесико: масштаб по X",
                 style={'textAlign': 'center', 'color': 'gray'}),

        html.H3("MAU", style={'textAlign': 'center'}),
        dcc.Graph(
            id='mau-plot',
            figure={
                'data': [go.Scatter(
                    x=mau_data['month_year'],
                    y=mau_data['count'],
                    mode='lines+markers',
                    line=dict(color='blue', width=2),
                    marker=dict(color='black', size=8),
                    hovertemplate=(
                        "<b>Дата</b>: %{x|%d %b %Y}<br>"  # Формат месяца и года
                        "<b>MAU</b>: %{y:,}<br>"  # Разделители тысяч для чисел
                        "<extra></extra>"  # Убираем лишнюю инфо
                    ),
                )
                ],
                'layout': {
                    'dragmode': 'pan',  # Только перемещение по ЛКМ
                    'xaxis': {
                        'fixedrange': False,  # Разрешаем масштабирование по X
                    },
                    'yaxis': {
                        'fixedrange': True  # Фиксируем масштаб по Y
                    }
                }
            },
            config={
                'scrollZoom': True,  # Включаем масштабирование (boolean, не строка)
                'modeBarButtonsToRemove': ['zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d']  # Убираем ненужные кнопки
            },
            style={'height': '70vh'}
        ),
        html.Div("ЛКМ: перемещение | Колесико: масштаб по X",
                 style={'textAlign': 'center', 'color': 'gray'}),

        html.H3("Retention 1 month", style={'textAlign': 'center'}),
        dcc.Graph(
            id='retention-1-plot',
            figure={
                'data': [go.Scatter(
                    x=retention_1['period'],
                    y=retention_1['starting_customers'],
                    customdata=retention_1['retention_rate'],
                    mode='lines+markers',
                    line=dict(color='blue', width=2),
                    marker=dict(color='black', size=8),
                    name="На начало периода",
                    hovertemplate=(
                        "<b>Покупателей на начало периода</b>: %{y:,}<br>"      
                        "<b>Retention Rate</b>: %{customdata}%<br>"
                        "<extra></extra>"
                    ),
                ),
                    go.Scatter(
                    x=retention_1['period'],
                    y=retention_1['new_customers'],
                    customdata=retention_1['retention_rate'],
                    mode='lines+markers',
                    line=dict(color='green', width=2),
                    marker=dict(color='black', size=8),
                    name = "Новые покупатели",
                    hovertemplate=(
                        "<b>Покупателей новых</b>: %{y:,}<br>"      
                        "<b>Retention Rate</b>: %{customdata}%<br>"
                        "<extra></extra>"
                    ),
                ),
                    go.Scatter(
                    x=retention_1['period'],
                    y=retention_1['departed_customers'],
                    customdata=retention_1['retention_rate'],
                    mode='lines+markers',
                    line=dict(color='red', width=2),
                    marker=dict(color='black', size=8),
                    name = "Ушедшие покупатели",
                    hovertemplate=(
                        "<b>Покупателей ушедших</b>: %{y:,}<br>"      
                        "<b>Retention Rate</b>: %{customdata}%<br>"
                        "<extra></extra>"
                    ),
                ),
                    go.Scatter(
                    x=retention_1['period'],
                    y=retention_1['ending_customers'],
                    customdata=retention_1['retention_rate'],
                    mode='lines+markers',
                    line=dict(color='#0000aa', width=2),
                    marker=dict(color='black', size=8),
                    name = "Покупателей на конец периода",
                    hovertemplate=(
                        "<b>Покупателей на конец периода</b>: %{y:,}<br>"      
                        "<b>Retention Rate</b>: %{customdata}%<br>"
                        "<extra></extra>"
                    ),
                )
                ],
                'layout': {
                    'dragmode': 'pan',  # Только перемещение по ЛКМ
                    'xaxis': {
                        'fixedrange': False,  # Разрешаем масштабирование по X
                    },
                    'yaxis': {
                        'fixedrange': True  # Фиксируем масштаб по Y
                    }
                }
            },
            config={
                'scrollZoom': True,  # Включаем масштабирование (boolean, не строка)
                'modeBarButtonsToRemove': ['zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d']  # Убираем ненужные кнопки
            },
            style={'height': '70vh'}
        ),
        html.Div("ЛКМ: перемещение | Колесико: масштаб по X",
                 style={'textAlign': 'center', 'color': 'gray'}),

        html.H3("Retention 3 months", style={'textAlign': 'center'}),
        dcc.Graph(
            id='retention-3-plot',
            figure={
                'data': [go.Scatter(
                    x=retention_3['period'],
                    y=retention_3['starting_customers'],
                    customdata=retention_3['retention_rate'],
                    mode='lines+markers',
                    line=dict(color='blue', width=2),
                    marker=dict(color='black', size=8),
                    name="На начало периода",
                    hovertemplate=(
                        "<b>Покупателей на начало периода</b>: %{y:,}<br>"      
                        "<b>Retention Rate</b>: %{customdata}%<br>"
                        "<extra></extra>"
                    ),
                ),
                    go.Scatter(
                        x=retention_3['period'],
                        y=retention_3['new_customers'],
                        customdata=retention_3['retention_rate'],
                        mode='lines+markers',
                        line=dict(color='green', width=2),
                        marker=dict(color='black', size=8),
                        name="Новые покупатели",
                        hovertemplate=(
                            "<b>Покупателей новых</b>: %{y:,}<br>"      
                            "<b>Retention Rate</b>: %{customdata}%<br>"
                            "<extra></extra>"
                        ),
                    ),
                    go.Scatter(
                        x=retention_3['period'],
                        y=retention_3['departed_customers'],
                        customdata=retention_3['retention_rate'],
                        mode='lines+markers',
                        line=dict(color='red', width=2),
                        marker=dict(color='black', size=8),
                        name="Ушедшие покупатели",
                        hovertemplate=(
                            "<b>Покупателей ушедших</b>: %{y:,}<br>"      
                            "<b>Retention Rate</b>: %{customdata}%<br>"
                            "<extra></extra>"
                        ),
                    ),
                    go.Scatter(
                        x=retention_3['period'],
                        y=retention_3['ending_customers'],
                        customdata=retention_3['retention_rate'],
                        mode='lines+markers',
                        line=dict(color='#0000aa', width=2),
                        marker=dict(color='black', size=8),
                        name="Покупателей на конец периода",
                        hovertemplate=(
                            "<b>Покупателей на конец периода</b>: %{y:,}<br>"      
                            "<b>Retention Rate</b>: %{customdata}%<br>"
                            "<extra></extra>"
                        ),
                    )
                ],
                'layout': {
                    'dragmode': 'pan',  # Только перемещение по ЛКМ
                    'xaxis': {
                        'fixedrange': False,  # Разрешаем масштабирование по X
                    },
                    'yaxis': {
                        'fixedrange': True  # Фиксируем масштаб по Y
                    }
                }
            },
            config={
                'scrollZoom': True,  # Включаем масштабирование (boolean, не строка)
                'modeBarButtonsToRemove': ['zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d']  # Убираем ненужные кнопки
            },
            style={'height': '70vh'}
        ),
        html.Div("ЛКМ: перемещение | Колесико: масштаб по X",
                 style={'textAlign': 'center', 'color': 'gray'})
    ])

# if __name__ == '__main__':
#     app.run(debug=True)
