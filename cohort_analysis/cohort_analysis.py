import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

from clear_data_app.clear_data_frames import ClearDataFrames

# Предположим, у нас есть DataFrame df_orders_cohort с нужными колонками
dfs = ClearDataFrames()
dfs.load_clear_data()

df_orders = dfs.orders.merge(dfs.customers, on='customer_id', how='left')
df_orders = df_orders[['order_id','customer_unique_id', 'order_purchase_timestamp']]
df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])

first_last_orders = df_orders.groupby('customer_unique_id')['order_purchase_timestamp'].agg(['min', 'max']).reset_index()
first_last_orders.columns = ['customer_unique_id', 'first_order_date', 'last_order_date']
first_last_orders['first_order_date'] = first_last_orders['first_order_date'].dt.to_period('M')
first_last_orders['last_order_date'] = first_last_orders['last_order_date'].dt.to_period('M')

first_last_orders['months_diff'] = (first_last_orders['last_order_date'] - first_last_orders['first_order_date']).apply(lambda x: x.n)

max_diff_month = first_last_orders['months_diff'].max()
unique_months = pd.concat([first_last_orders['first_order_date'], first_last_orders['last_order_date']]).drop_duplicates().reset_index(drop=True)
lowest_months = unique_months.min()
highest_months = unique_months.max() + max_diff_month
all_months = []
while lowest_months <= highest_months:
    all_months.append(lowest_months)
    lowest_months += 1


cohort_dict = {}
for month in all_months:
    cohort = [0 for i in range(max_diff_month + 1)]
    cohort_dict[month] = cohort.copy()
for row in first_last_orders.itertuples():
    for i in range(row.months_diff + 1):
        for j in range(row.months_diff + 1 - i):
            cohort_dict[row.first_order_date + i][j] += 1

cohort_list = []
for cohort_month, counts in cohort_dict.items():
    for months_diff, customers_count in enumerate(counts):
        cohort_list.append({
            'cohort_month': cohort_month,
            'months_diff': months_diff,
            'customers_count': customers_count
        })
cohort_df = pd.DataFrame(cohort_list)
cohort_df = cohort_df[cohort_df['customers_count'] > 0]
start_values = cohort_df[cohort_df['months_diff'] == 0].pivot_table(
        index='cohort_month',
        values='customers_count',
        aggfunc='sum'
    ).squeeze()[1:]

# Создаем Dash приложение
app = dash.Dash(__name__)

app.layout = html.Div([
    # Заголовок
    html.Div(
        html.H1("Когортный анализ удержания клиентов",
                style={'textAlign': 'center', 'margin-bottom': '20px'}),
        style={'width': '100%'}
    ),

    # Панель управления
    html.Div([
        html.Div([
            html.Label("Выберите тип визуализации:",
                       style={'font-weight': 'bold'}),
            dcc.RadioItems(
                id='heatmap-type',
                options=[
                    {'label': 'Абсолютные значения', 'value': 'absolute'},
                    {'label': 'Процент удержания', 'value': 'retention'}
                ],
                value='absolute',
                inline=True,
                style={'margin-bottom': '20px'}
            ),
        ], style={'padding': '10px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-bottom': '20px'}),

        html.Div([
            html.Label("Выберите временной период:",
                       style={'font-weight': 'bold'}),
            dcc.RangeSlider(
                id='cohort-range',
                min=1,
                max=max_diff_month,
                value=[1, 6],
                marks={i: f'{i} мес.' for i in range(max_diff_month + 1)},
                step=1,
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'padding': '10px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-bottom': '20px'})
    ], style={
        'width': '80%',
        'margin': '0 auto',
        'display': 'flex',
        'flex-direction': 'column',
        'gap': '15px'
    }),

    # График
    html.Div(
        dcc.Graph(id='cohort-heatmap',
                  style={'height': '70vh'}),
        style={
            'width': '90%',
            'margin': '0 auto',
            'flex-grow': '1',
            'min-height': '500px'
        }
    )
], style={
    'display': 'flex',
    'flex-direction': 'column',
    'min-height': '100vh',
    'padding': '20px 0'
})


def create_cohort_analysis(df):
    cohort_counts = df.pivot_table(
        index='cohort_month',
        columns='months_diff',
        values='customers_count',
        aggfunc='sum',
        fill_value=0
    )
    retention = cohort_counts.div(start_values, axis=0) * 100
    retention = retention.replace(0, np.nan)
    return retention.round(1)


@app.callback(
    Output('cohort-heatmap', 'figure'),
    [Input('heatmap-type', 'value'),
     Input('cohort-range', 'value')]
)
def update_heatmap(heatmap_type, month_range):
    # Фильтруем данные по выбранному диапазону месяцев
    filtered_data = cohort_df[
        (cohort_df['months_diff'] >= month_range[0]) &
        (cohort_df['months_diff'] <= month_range[1])
        ]
    filtered_data = filtered_data[filtered_data['months_diff'] > 0]
    if heatmap_type == 'retention':
        data = create_cohort_analysis(filtered_data)
        title = "Процент удержания клиентов по когортам (%)"
        hover_template = 'Когорта: %{y}<br>Месяц: %{x}<br>Удержание: %{z}%'
        color_scale = 'Blues'
    else:
        data = filtered_data.pivot_table(index='cohort_month',
                                       columns='months_diff',
                                       values='customers_count')
        title = "Количество клиентов по когортам"

        hover_template = 'Когорта: %{y}<br>Месяц: %{x}<br>Клиенты: %{z} из %{customdata[0]}'
        color_scale = 'Blues'

    fig = px.imshow(
        data,
        labels=dict(x="Месяц относительно первой покупки",
                    y="Когорта, месяц первой покупки)",
                    color=title),
        x=[f"Месяц {i}" for i in data.columns],
        y=data.index.astype(str),
        color_continuous_scale=color_scale,
        title=title
    )

    if heatmap_type == 'retention':
        fig.update_traces(
            hovertemplate=hover_template,
            texttemplate="%{z}",
            textfont={"size": 10}
        )
    else:
        customdata = np.zeros((len(data.index), len(data.columns), 1))
        for i, cohort in enumerate(data.index):
            for j, month_diff in enumerate(data.columns):
                customdata[i, j, 0] = start_values.get(cohort, 0)
        fig.update_traces(
            customdata=customdata,
            hovertemplate=hover_template,
            texttemplate="%{z}",
            textfont={"size": 10}
        )

    fig.update_layout(
        xaxis_title="Временной период",
        yaxis_title="Месяц",
        height=600,
        margin=dict(l=50, r=50, b=100, t=100)
    )

    return fig


if __name__ == '__main__':
    app.run(debug=True)