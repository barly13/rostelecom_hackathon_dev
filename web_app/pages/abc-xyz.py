import dash
from abc_xyz_analysis.abc_xyz_visual import get_app_layout

dash.register_page(__name__, path='/abc-xyz', name="ABC & XYZ")
layout = get_app_layout()