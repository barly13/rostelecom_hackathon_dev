import dash
from territory_analysis.territory_analysis_by_states import get_app_layout

dash.register_page(__name__, path='/territory_states', name="Территориальный по штатам")
layout = get_app_layout()