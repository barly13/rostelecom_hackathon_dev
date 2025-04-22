import dash
from ml.dash.dash_ml import get_app_layout

dash.register_page(__name__, path='/visual_prediction', name="Предсказания модели")
layout = get_app_layout()
