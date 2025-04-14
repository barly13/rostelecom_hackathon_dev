import dash
from dash import dcc, html, dash_table, Output, Input
import plotly.graph_objects as go
import numpy as np
import json
import pandas as pd
from datetime import datetime

secs = [0.0,  1.0,  2.0, 4.0, 854.0, 62913.0, 263666.0, 601013.0, 874461.0, 1250767.0, 1726669.0, 2208353.0, 2846709.0, 3540412.0, 4215159.0, 4981450.0, 5928244.0, 7000816.0, 8521546.0, 9990747.0, 11526042.0, 13391879.0, 15495376.0, 17551140.0, 20507899.0, 24266941.0, 29184041.0, 40506639.0]
probs = [0.0,  0.09615384615384616, 0.19230769230769232, 0.22435897435897437, 0.2564102564102564, 0.28846153846153844, 0.32051282051282054, 0.3525641025641026, 0.38461538461538464, 0.4166666666666667, 0.44871794871794873, 0.4807692307692308, 0.5128205128205128, 0.5448717948717948, 0.5769230769230769, 0.6089743589743589, 0.6410256410256411, 0.6730769230769231, 0.7051282051282052, 0.7371794871794872, 0.7692307692307693, 0.8012820512820513, 0.8333333333333334, 0.8653846153846154, 0.8974358974358975, 0.9294871794871795, 0.9615384615384616, 0.9935897435897436]

def get_probability(time_sec):
    i = 0
    for i in range(len(secs)):
        if secs[i] > time_sec:
            break
    if i == len(secs):
        return 1
    else:
        return min(1, (time_sec - secs[i-1]) / (secs[i] - secs[i-1]) * (probs[i] - probs[i-1]) + probs[i])

today = datetime(2018, 8, 29, 15, 0, 37)

rfm_analysis = pd.read_csv("rfm_data/rfm_analysis.csv")
rfm_analysis["time"] = rfm_analysis.last_purchase_date.apply(lambda x: (today - datetime.strptime(x, '%Y-%m-%d %H:%M:%S')).total_seconds())
rfm_analysis["fire_prob"] = rfm_analysis.time.apply(get_probability)
rfm_analysis = rfm_analysis[["rfm_cell", "fire_prob"]]
rfm_analysis = rfm_analysis.groupby("rfm_cell").mean()

rfm_analysis = rfm_analysis.reset_index()
rfm_analysis["latency"] = rfm_analysis.rfm_cell.apply(lambda x: int(str(x)[0]))
rfm_analysis["freq"] = rfm_analysis.rfm_cell.apply(lambda x: int(str(x)[1]))
rfm_analysis["money"] = rfm_analysis.rfm_cell.apply(lambda x: int(str(x)[2]))

app = dash.Dash(__name__)



# Функция для создания 3D куба с ячейками тензора
def create_tensor_cube(rfm):
    fig = go.Figure()
    # Добавляем точки для каждой ячейки тензора
    x, y, z = [], [], []
    values = []
    for i in range(3):
        for j in range(3):
            for k in range(3):
                data = rfm[(rfm.latency == i+1) & (rfm.freq == j+1) & (rfm.money == k+1)]
                if len(data) == 0:
                    continue
                x.append(i)
                y.append(j)
                z.append(k)
                values.append(float(rfm[(rfm.latency == i+1) & (rfm.freq == j+1) & (rfm.money == k+1)][["fire_prob"]].iloc[0]))

    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(
            size=8,
            color=values,
            cmin=0,
            cmax=1,
            colorscale='Viridis',
            opacity=0.8,
            showscale=True
        ),
        text=[f'Вероятность ухода пользователя: {val:.2f}' for val in values],
        hoverinfo='text'
    ))

    # Настройки внешнего вида
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Давность (0 - недавние, 2 - давние)', nticks=4, range=[-0.5, 2.5]),
            yaxis=dict(title='Частота (0 - частые, 2 - нечастые)', nticks=4, range=[-0.5, 2.5]),
            zaxis=dict(title='Средний чек (0 - высокий чек, 2 - низкий чек)', nticks=4, range=[-0.5, 2.5]),
            aspectmode='cube'
        ),
        # title='3D Тензор 3×3×3 (вращайте мышью)',
        margin=dict(r=20, l=10, b=10, t=50),
        template='plotly_white',
        # Настройки камеры по умолчанию
        scene_camera=dict(
            eye=dict(x=1.5, y=1.5, z=0.5)
        )
    )
    return fig

# Функция для создания тепловой карты
def create_heatmap(rfm, ax):
    tensor = np.full((3, 3), np.nan)
    form_string = "{}, {}, Вероятность ухода: {:.2f}"
    first = []
    second = []
    x_label = ""
    y_label = ""
    if ax == "latency": # по давности объединение
        first = ["Частые", "Средней частоты", "Редкие"]
        second = ["Высокий чек", "Средний чек", "Низкий чек"]
        x_label = "Средний чек"
        y_label = "Частота"
        rfm = rfm.groupby(["freq", "money"])[["fire_prob"]].mean()
        for money in (1, 2, 3):
            for freq in (1, 2, 3):
                if (freq, money) in rfm.index:
                    tensor[freq-1, money-1] = rfm.loc[freq, money]
    elif ax == "frequency": # по частоте объединение
        first = ["Недавние", "Средней давности", "Давние"]
        second = ["Высокий чек", "Средний чек", "Низкий чек"]
        x_label = "Средний чек"
        y_label = "Давность"
        rfm = rfm.groupby(["latency", "money"])[["fire_prob"]].mean()
        for money in (1, 2, 3):
            for latency in (1, 2, 3):
                if (latency, money) in rfm.index:
                    tensor[latency-1, money-1] = rfm.loc[latency, money]
    elif ax == "money": # по чеку объединение
        first = ["Недавние", "Средней давности", "Давние"]
        second = ["Частые", "Средней частоты", "Редкие"]
        x_label = "Частота"
        y_label = "Давность"
        rfm = rfm.groupby(["latency", "freq"])[["fire_prob"]].mean()
        for freq in (1, 2, 3):
            for latency in (1, 2, 3):
                if (latency, freq) in rfm.index:
                    tensor[latency-1, freq-1] = rfm.loc[latency, freq]

    fig = go.Figure(data=go.Heatmap(
        z=tensor,
        zmin=0,
        zmax=1,
        colorscale='Viridis',
        colorbar=dict(title='Значение'),
        hoverongaps=False,
        text=np.array([[form_string.format(first[i], second[j], tensor[i, j])
                        for j in range(3)] for i in range(3)]),
        hoverinfo='text'
    ))

    fig.update_layout(
        xaxis=dict(title=x_label, tickvals=[0, 1, 2]),
        yaxis=dict(title=y_label, tickvals=[0, 1, 2]),
        width=500,
        height=500,
        margin=dict(r=20, l=10, b=10, t=50),
    )
    return fig

def create_line(rfm, ax):
    tensor = np.full((1, 3), np.nan)
    form_string = "{}, Вероятность ухода: {:.2f}"
    labels = []
    ax_label = ""

    if "latency" not in ax: # по давности объединение
        labels = ["Недавние", "Средней давности", "Давние"]
        ax_label = "Давность"
        rfm = rfm.groupby(["latency"])[["fire_prob"]].mean()
        for latency in (1, 2, 3):
            tensor[0, latency-1] = rfm.loc[latency]

    elif "frequency" not in ax: # по давности объединение
        labels = ["Частые", "Средней частоты", "Редкие"]
        ax_label = "Частота"
        rfm = rfm.groupby(["freq"])[["fire_prob"]].mean()
        for frequency in (1, 2, 3):
            tensor[0, frequency-1] = rfm.loc[frequency]

    elif "money" not in ax: # по давности объединение
        labels = ["Высокий чек", "Средний чек", "Низкий чек"]
        ax_label = "Средний чек"
        rfm = rfm.groupby(["money"])[["fire_prob"]].mean()
        for money in (1, 2, 3):
            tensor[0, money-1] = rfm.loc[money]

    fig = go.Figure(data=go.Heatmap(
        z=tensor,
        zmin=0,
        zmax=1,
        colorscale='Viridis',
        colorbar=dict(title='Значение'),
        hoverongaps=False,
        text=np.array([[form_string.format(labels[i], tensor[0, i])
                        for i in range(3)]]),
        hoverinfo='text'
    ))

    fig.update_layout(
        xaxis=dict(title=ax_label, tickvals=[0, 1, 2]),
        yaxis=dict(title="", tickvals=[0, 1, 2]),
        width=500,
        height=250,
        margin=dict(r=20, l=10, b=10, t=50),
    )
    return fig


app.layout = html.Div([
    html.H1("RFM", style={'textAlign': 'center'}),
    html.Div([
        dcc.Checklist(
            id='axis-selector',
            options=[
                {'label': 'Объединить по давности', 'value': 'latency'},
                {'label': 'Объединить по частоте', 'value': 'frequency'},
                {'label': 'Объединить по среднему чеку', 'value': 'money'}
            ],
            value=[],
            labelStyle={'display': 'inline-block', 'margin': '10px'}
        )
    ], style={'textAlign': 'center'}),

    html.Div(
        style={
            'display': 'flex',
            'justifyContent': 'center',
            'width': '100%',
            'padding': '20px'
        },
        id='tables',
        children=[]
    )
])

@app.callback(
    Output('tables', 'children'),
    Input('axis-selector', 'value')
)
def update_tables(selected):
    if len(selected) == 0:
        return dcc.Graph(
            figure=create_tensor_cube(rfm_analysis),
            style={
                'width': '80vw',
                'height': '70vh',
                'display': 'block',
                'margin': '0 auto'
            }
        )

    if len(selected) == 1:
        return dcc.Graph(
            figure=create_heatmap(rfm_analysis, selected[0]),
            style={
                'width': '30vw',
                'height': '100vh',
                'display': 'block',
                'margin': '0 auto'
            }
        )

    if len(selected) == 2:
        return dcc.Graph(
            figure=create_line(rfm_analysis, selected),
            style={
                'width': '30vw',
                'height': '100vh',
                'display': 'block',
                'margin': '0 auto'
            }
        )


if __name__ == '__main__':
    app.run(debug=True)