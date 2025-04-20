import os.path
from http.cookiejar import debug

import pandas as pd
import numpy as np


# Создаем DataFrames (таблицы)

current_dir = os.path.dirname(__file__)
file_path_1 = f'{current_dir}/../clear_data_app/clear_data/products.csv'  # путь к products
file_path_2 = f'{current_dir}/../clear_data_app/clear_data/orders_items.csv'  # путь к orders_items
file_path_3 = f'{current_dir}/../clear_data_app/clear_data/product_category_name_translation.csv'  # путь к product_category_name_translation

products = pd.read_csv(file_path_1)
order_items = pd.read_csv(file_path_2)
product_category_name_translation = pd.read_csv(file_path_3)

# Выполняем FULL JOIN products с product_category_name_translation по столбцу 'product_category_name'
cols = ['product_id', 'product_category_name_english', 'product_category_name']
full_join_products_id_name = pd.merge(products, product_category_name_translation, on='product_category_name', how='outer')[cols]
full_join_products_id_name = full_join_products_id_name.sort_values(by = 'product_category_name_english').fillna(0)

mask_of_NaN_english_name = full_join_products_id_name.product_category_name_english == 0
full_join_products_id_name.loc[mask_of_NaN_english_name, "product_category_name_english"] = full_join_products_id_name.product_category_name[mask_of_NaN_english_name]

# Выполняем FULL JOIN full_join_products_id_name с order_items по столбцу 'product_category_name'
full_join_products_order_items = pd.merge(full_join_products_id_name, order_items, on='product_id', how='outer')
cols = ['product_id', 'product_category_name_english', 'count', 'price']
# Добавляем колонку "count" с количеством заказанных продуктов, где по умолчанию значение = 1
full_join_products_order_items = full_join_products_order_items.assign(count =  np.ones(len(full_join_products_order_items)))
full_join_products_order_items = full_join_products_order_items.sort_values(by = 'price', ascending = False).fillna(0)
df_abc = full_join_products_order_items[cols]

# ABC-анализ
# Группируем по "product_category_name_english"(названиям товаров), при этом находится кол-во заказов и их суммарная стоимость для каждого продукта
cols = ['product_category_name_english', 'price', 'count']
df_abc = df_abc[cols].groupby('product_category_name_english').sum().sort_values(by = 'price', ascending = False).reset_index()
# Находим общую сумму стоимостей всех заказанных продуктов
sum_of_all_price = float(sum(df_abc.price))
# Добавляем колонку "percent" с процентной долей каждого продукта
df_abc = df_abc.assign(percent = df_abc.price / sum_of_all_price * 100).sort_values(by = 'percent', ascending = False)
# Добавляем кумулятивную сумму процентов
df_abc = df_abc.assign(cumsum_percent = np.cumsum(df_abc.percent))
# Создадим колонку "ABC"
df_abc = df_abc.assign(ABC = '')
# Проведём классификацию продуктов по ABC-анализу
df_abc.loc[df_abc.cumsum_percent <= 80, "ABC"] = 'A'
df_abc.loc[df_abc.cumsum_percent > 80, "ABC"] = 'B'
df_abc.loc[df_abc.cumsum_percent >= 95, "ABC"] = 'C'

# XYZ-анализ
cols = ['order_id', 'product_category_name_english', 'count', 'shipping_limit_date']
df_xyz = full_join_products_order_items[cols][full_join_products_order_items.shipping_limit_date != 0]

# Даты первого и последнего заказов
last_date = max(df_xyz.shipping_limit_date)
early_date = min(df_xyz.shipping_limit_date)

# Диапазон анализируемых дат
start_date_input = '2016-09-19 00:15:34' # early_date
end_date_input = '2018-09-19 00:15:34' # last_date

# Преобразуем введенные даты в datetime
start_date = pd.to_datetime(start_date_input)
end_date = pd.to_datetime(end_date_input)
print(f'Сроки отгрузки товаров: \nот {early_date}\nдо {last_date}')
delta_month = (end_date.to_period('M') - start_date.to_period('M')).n
print(f'Длительность анализируемого периода в месяцах = {delta_month}')



# Фильтруем DataFrame по выбранному диапазону
df_filtered_xyz = df_xyz[(pd.to_datetime(df_xyz["shipping_limit_date"]) >= start_date) & (pd.to_datetime(df_xyz["shipping_limit_date"]) <= end_date)]

# Если данных нет, выводим сообщение
if df_filtered_xyz.empty:
    print("Нет данных за выбранный период.")
else:
    # Преобразуем дату в формат datetime и извлекаем год-месяц
    df_filtered_xyz["shipping_limit_date"] = pd.to_datetime(df_filtered_xyz["shipping_limit_date"])
    df_filtered_xyz["year_month"] = df_filtered_xyz["shipping_limit_date"].dt.strftime("%Y-%m")



    # Группируем по продукту и месяцу, суммируем количество
    monthly_sales = df_filtered_xyz.groupby(["product_category_name_english", "year_month"])["count"].sum().reset_index()

    # Вычисляем среднее количество заказов в месяц для каждого продукта
    mean_orders_per_month = monthly_sales.groupby("product_category_name_english")["count"].mean().reset_index()
    mean_orders_per_month.columns = ["product_category_name_english", "mean_quantity_per_month"]

    # Вычисляем стандартное отклонение (среднеквадратичное отклонение) для каждого продукта
    std_dev_per_product = monthly_sales.groupby("product_category_name_english")["count"].std().reset_index()
    std_dev_per_product.columns = ["product_category_name_english", "std_deviation"]

    # Объединяем результаты
    df_filtered_xyz = pd.merge(mean_orders_per_month, std_dev_per_product, on="product_category_name_english")
    df_filtered_xyz = df_filtered_xyz.assign(variation = df_filtered_xyz.std_deviation / df_filtered_xyz.mean_quantity_per_month * 100)
print("Среднее количество заказов в месяц и стандартное отклонение по продуктам:")
# Сортируем продукты по величине их вариации
df_filtered_xyz = df_filtered_xyz.sort_values(by = 'variation', ascending = True)
# Проведём классификацию продуктов по XYZ-анализу
df_filtered_xyz = df_filtered_xyz.assign(XYZ = np.zeros(len(df_filtered_xyz)))
df_filtered_xyz.XYZ[df_filtered_xyz.variation < 10] = 'X'
df_filtered_xyz.XYZ[df_filtered_xyz.variation >= 10] = 'Y'
df_filtered_xyz.XYZ[df_filtered_xyz.variation >= 25] = 'Z'

# Сохранение результатов

# df_abc.to_csv('ABC.csv')
# df_filtered_xyz.to_csv('XYZ.csv')
df_general = pd.merge(df_abc, df_filtered_xyz, on='product_category_name_english', how='outer')
# df_general.to_csv('abc_xyz_analysis.csv')
import plotly.graph_objects as go
from collections import Counter

# Визуализация
df = df_general

# Цвета групп
colors = {'A': '#4CAF50', 'B': '#FFC107', 'C': '#F44336'}

# Штриховка для XYZ
xyz_patterns = {
    'X': {'shape': '', 'solidity': 0},  # Нет штриховки
    'Y': {'shape': '/', 'solidity': 0.4},  # Одиночная штриховка
    'Z': {'shape': 'x', 'solidity': 0.4}  # Перекрестная штриховка
}


def get_most_common_xyz(group_df):
    if 'XYZ' not in group_df.columns:
        return 'X'
    xyz_counts = Counter(group_df['XYZ'])
    return xyz_counts.most_common(1)[0][0]


# Создаем списки для диаграммы
labels, values, text = [], [], []
marker_colors, marker_patterns = [], []

# Обработка групп
for abc_group in ['A', 'B', 'C']:
    group_df = df[df['ABC'] == abc_group]

    if abc_group == 'A':
        # Для группы A - отдельные товары
        for _, row in group_df.iterrows():
            labels.append(row['product_category_name_english'])
            values.append(row['price'])
            # Улучшенный текст с черным цветом и лучшей читаемостью
            text.append(
                f"<b style='color:black'>{row['product_category_name_english']}</b><br><span style='color:black'>{row['percent']:.1f}%</span>")
            marker_colors.append(colors[abc_group])

            xyz = row['XYZ'] if 'XYZ' in row else 'X'
            pattern = xyz_patterns[xyz].copy()
            pattern['fgcolor'] = colors[abc_group]
            marker_patterns.append(pattern)
    else:
        # Для групп B и C - объединенные секторы
        if not group_df.empty:
            group_name = f'Группа {abc_group}'
            labels.append(group_name)
            values.append(group_df['price'].sum())
            # Улучшенный текст с черным цветом
            text.append(
                f"<b style='color:black'>{group_name}</b><br><span style='color:black'>{group_df['percent'].sum():.1f}%</span>")
            marker_colors.append(colors[abc_group])

            xyz = get_most_common_xyz(group_df)
            pattern = xyz_patterns[xyz].copy()
            pattern['fgcolor'] = colors[abc_group]
            marker_patterns.append(pattern)


# Создаем диаграмму
fig = go.Figure()

fig.add_trace(go.Pie(
    labels=labels,
    values=values,
    text=text,
    marker=dict(
        colors=marker_colors,
        line=dict(color='#fff', width=1),
        pattern=dict(
            shape=[p['shape'] for p in marker_patterns],
            solidity=[p['solidity'] for p in marker_patterns],
            fgcolor=[p['fgcolor'] for p in marker_patterns],
            bgcolor='rgba(255,255,255,0)'
        )
    ),
    textinfo='text',
    textposition='inside',
    hole=0.4,
    hoverinfo='label+value+percent',
    name='',
    textfont=dict(
        family="Arial Black",  # Более жирный шрифт
        size=14,  # Увеличенный размер
        color='black'  # Черный цвет текста
    ),
    insidetextorientation='auto'  # Автоматическое выравнивание текста
))

# Настройки отображения
fig.update_layout(
    title=dict(
        text='<b>ABC-XYZ Анализ продуктов</b>',
        font=dict(size=20, family='Arial Black', color='black'),
        x=0.5,
        y=0.95
    ),
    annotations=[
        dict(
            text=f"<b style='color:black'>A: 0-80%</b><br><b style='color:black'>B: 80-95%</b><br><b style='color:black'>C: 95-100%</b>",
            x=0.5, y=0.5,
            font=dict(size=16, family='Arial', color='black'),
            showarrow=False,
            bgcolor='white',
            bordercolor='lightgray',
            borderwidth=1
        ),
        dict(
            text=f"<b style='color:black'>Продуктов:</b><br><span style='color:black'>A: {len(df[df['ABC'] == 'A'])}</span><br><span style='color:black'>B: {len(df[df['ABC'] == 'B'])}</span><br><span style='color:black'>C: {len(df[df['ABC'] == 'C'])}</span>",
            x=0.9, y=0.15,
            font=dict(size=14, family='Arial'),
            showarrow=False,
            bordercolor="#c7c7c7",
            borderwidth=1,
            borderpad=4,
            bgcolor="#ffffff",
            opacity=0.8
        ),
        dict(
            text="<b style='color:black'>Цвета групп:</b><br><span style='color:#4CAF50'>■</span> <span style='color:black'>A</span><br>"
                 "<span style='color:#FFC107'>■</span> <span style='color:black'>B</span><br>"
                 "<span style='color:#F44336'>■</span> <span style='color:black'>C</span><br><br>"
                 "<b style='color:black'>Штриховка XYZ:</b><br>"
                 "<span style='color:black'>нет штриха - X</span><br>"
                 "<span style='color:black'>'/' - Y</span><br>"
                 "<span style='color:black'>'x' - Z</span>",
            x=0.05, y=0.05,
            font=dict(size=14, family='Arial'),
            showarrow=False,
            bordercolor="#c7c7c7",
            borderwidth=1,
            borderpad=4,
            bgcolor="#ffffff",
            opacity=0.8
        )
    ],
    showlegend=False,
    height=750,  # Увеличена высота
    uniformtext_minsize=14,  # Минимальный размер текста
    uniformtext_mode='hide',
    margin=dict(l=50, r=50, b=100, t=100, pad=4),
    paper_bgcolor='white'  # Белый фон для лучшей читаемости
)

# Дополнительные настройки для улучшения читаемости
fig.update_traces(
    hovertemplate='<b>%{label}</b><br>Доля: %{percent:.1%}<br>Сумма: %{value:.0f}',
    texttemplate='<b>%{label}</b><br>%{percent:.1%}'
)

import dash
from dash import html, dcc

def get_app_layout():
    return html.Div([
            html.H1("ABC-XYZ анализ", style={'textAlign': 'center'}),
            dcc.Graph(
                id='abc',
                figure=fig,
            )
        ])

# app.run(debug=True)
