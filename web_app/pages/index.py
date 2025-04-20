import dash
from dash import html, dcc

dash.register_page(__name__, path='/', name="Главная")  # Регистрируем страницу

layout = html.Div([
    html.H1("Добро пожаловать на главную страницу! "),
    html.H1("Навигация по дашбордам доступна в верхней части страницы"),
],
    style={
        'width': 'fit-content',  # или конкретная ширина ('800px')
        'margin': 'auto',        # автоматические отступы по бокам
        'display': 'block'       # обязательно для margin:auto
    })