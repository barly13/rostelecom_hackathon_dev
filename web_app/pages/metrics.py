import dash
from customer_metrics.customer_metrics_visual import get_app_layout

dash.register_page(__name__, path='/metrics', name="Метрики покупателей")
layout = get_app_layout()