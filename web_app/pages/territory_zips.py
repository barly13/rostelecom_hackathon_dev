import dash
from territory_analysis.territory_analysis import get_app_layout

dash.register_page(__name__, path='/territory_zips', name="Территориальный по индексам")
layout = get_app_layout()