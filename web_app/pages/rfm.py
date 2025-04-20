import dash
from rfm_analysis.rfm_analysis_visual import get_app_layout

dash.register_page(__name__, path='/rfm', name="RFM-анализ")
layout = get_app_layout()