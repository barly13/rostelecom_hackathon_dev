import dash
from dash import dcc, html, dash_table, Input, Output, State
import pandas as pd
import io
import base64
from ml.one_order_model import OneOrderModel


# app = dash.Dash(__name__)


def get_app_layout():
    return html.Div([
        html.H1("Предсказание вероятности следующей покупки"),

        # Поле для загрузки файла
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Перетащите или ',
                html.A('выберите CSV файл')
            ]),
            style={
                'width': '50%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        html.Div([
                html.Button('Спрогнозировать',
                            id='predict-button',
                            n_clicks=0,
                            style={
                                'height': '60px',
                                'width': '150px',
                                'margin': '10px 10px 10px 10px',
                                'fontSize': '16px'
                            })
            ], style={'width': '4%', 'display': 'inline-block', 'vertical-align': 'top', 'textAlign': 'center'}),

        html.Div([
            # Исходные данные (левая колонка)
            html.Div([
                html.H3("Исходные данные (первые 20 строк)"),
                html.Div(id='original-data-info'),
                dash_table.DataTable(
                    id='original-data-table',
                    page_size=20,
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'height': 'auto',
                        'minWidth': '100px', 'width': '100px',
                        'whiteSpace': 'nowrap'
                    }
                ),
                html.Div([
                    html.Button('Предыдущая страница', id='original-prev-page', n_clicks=0),
                    html.Button('Следующая страница', id='original-next-page', n_clicks=0),
                ], style={'margin-top': '10px'})
            ], style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top'}),

            html.Div([
                html.Div(id='result-data-info')
            ], style={'width': '2%', 'display': 'inline-block', 'vertical-align': 'top'}),

            # Результирующие данные (правая колонка)
            html.Div([
                html.H3("Вероятность следующей покупки"),
                html.Div(id='result-data-info'),
                dash_table.DataTable(
                    id='result-data-table',
                    page_size=20,
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'height': 'auto',
                        'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                        'whiteSpace': 'normal'
                    }
                ),
                html.Div([
                    html.Button('Предыдущая страница', id='result-prev-page', n_clicks=0),
                    html.Button('Следующая страница', id='result-next-page', n_clicks=0),
                ], style={'margin-top': '10px'})
            ], style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top'})
        ])
    ])

current_original_page = 0
current_result_page = 0
stored_df = None
processed_df = pd.DataFrame()


def process_data(df):
    # return df
    processed_df = df.copy()
    oom = OneOrderModel('../models/rfc.pkl', '../cluster_table.csv')
    return oom.predict(processed_df)


def register_callbacks_ml(app):
    @app.callback(
        [Output('original-data-table', 'data'),
         Output('original-data-table', 'columns'),
         Output('original-data-info', 'children'),
         Output('result-data-table', 'data'),
         Output('result-data-table', 'columns'),
         Output('result-data-info', 'children')],
        [Input('upload-data', 'contents'),
         Input('predict-button', 'n_clicks'),
         Input('original-prev-page', 'n_clicks'),
         Input('original-next-page', 'n_clicks'),
         Input('result-prev-page', 'n_clicks'),
         Input('result-next-page', 'n_clicks')],
        [State('upload-data', 'filename'),
         State('original-data-table', 'data')]
    )
    def update_output(contents, predict_clicks, orig_prev, orig_next, res_prev, res_next, filename, original_data):
        global current_original_page, current_result_page, stored_df, processed_df

        ctx = dash.callback_context
        if not ctx.triggered:
            return [None] * 6

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Обработка загруженного файла
        if button_id == 'upload-data' and contents is not None:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            try:
                if 'csv' in filename:
                    # Читаем CSV файл
                    stored_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                    try:
                        stored_df.drop(columns=['Unnamed: 0'], inplace=True)
                    except Exception:
                        pass
                    current_original_page = 0
                    current_result_page = 0
                else:
                    return [None, None, "Пожалуйста, загрузите CSV файл", None, None, ""]
            except Exception as e:
                return [None, None, f"Ошибка при чтении файла: {e}", None, None, ""]

        # Обработка кнопок пагинации
        elif button_id in ['original-prev-page', 'original-next-page']:
            if button_id == 'original-prev-page' and current_original_page > 0:
                current_original_page -= 1
            elif button_id == 'original-next-page' and stored_df is not None and (current_original_page + 1) * 20 < len(
                    stored_df):
                current_original_page += 1

        elif button_id in ['result-prev-page', 'result-next-page']:
            if button_id == 'result-prev-page' and current_result_page > 0:
                current_result_page -= 1
            elif button_id == 'result-next-page' and processed_df is not None and (current_result_page + 1) * 20 < len(
                    stored_df):
                current_result_page += 1

        # Если данных нет, возвращаем пустые результаты
        if stored_df is None:
            return [None] * 6

        # Преобразуем исходные данные для отображения
        original_columns = [{"name": str(i), "id": str(i)} for i in stored_df.columns]
        original_data = stored_df.iloc[current_original_page * 20:(current_original_page + 1) * 20].to_dict('records')
        original_info = f"Файл: {filename}, Строк: {len(stored_df)}, Столбцов: {len(stored_df.columns)}"

        # Обрабатываем данные только при нажатии кнопки "Спрогнозировать"
        if button_id == 'predict-button':
            processed_df = process_data(stored_df)
            current_result_page = 0
        else:
            # Если обработка еще не выполнялась, показываем пустую таблицу
            if 'processed_df' not in globals():
                return original_data, original_columns, original_info, None, None, "Нажмите 'Спрогнозировать' для обработки данных"
            processed_df = globals().get('processed_df', pd.DataFrame())

        # Преобразуем результирующие данные для отображения
        result_columns = [{"name": str(i), "id": str(i)} for i in processed_df.columns]
        result_data = processed_df.iloc[current_result_page * 20:(current_result_page + 1) * 20].to_dict('records')
        result_info = f"Строк: {len(processed_df)}, Столбцов: {len(processed_df.columns)}"

        return original_data, original_columns, original_info, result_data, result_columns, result_info


# if __name__ == '__main__':
#     app.run(debug=True)