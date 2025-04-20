import dash
from cohort_analysis.cohort_analysis import get_app_layout

dash.register_page(__name__, path='/cohorts', name="Когортный")
layout = get_app_layout()