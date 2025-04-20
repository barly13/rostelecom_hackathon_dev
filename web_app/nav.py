import dash
from dash import dcc, html, Output, Input
from dash.exceptions import PreventUpdate

from cohort_analysis.cohort_analysis import register_callbacks_ca
from rfm_analysis.rfm_analysis_visual import register_callbacks_rfm
from territory_analysis.territory_analysis import register_callbacks_ta

app = dash.Dash(__name__, use_pages=True)

# Структура приложения с навигацией
app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div([
        dcc.Link(f"{page['name']}",
                 href=page["relative_path"],
                 id=f"nav-{page['name']}",
                 style={'padding': '20px', 'background': '#f8f9fa'}
                 )
        for page in dash.page_registry.values()
    ], style={'padding': '20px', 'background': '#f8f9fa'}),

    dash.page_container
])

register_callbacks_ta(app)
register_callbacks_rfm(app)
register_callbacks_ca(app)

@app.callback(
    [Output(f"nav-{page['name']}", "style") for page in dash.page_registry.values()],
    Input("url", "pathname")
)
def update_active_links(pathname):
    if not pathname:
        raise PreventUpdate

    styles = []
    for page in dash.page_registry.values():
        if pathname == page["relative_path"]:
            # Стиль для активной страницы
            styles.append({
                "margin": "0 10px",
                "fontWeight": "bold",
                "color": "black",
                "borderBottom": "2px solid white",
                "transform": "scale(1.05)"
            })
        else:
            # Стиль для неактивных страниц
            styles.append({
                "margin": "0 10px",
                "color": "grey"
            })
    return styles


if __name__ == '__main__':
    app.run(debug=True)