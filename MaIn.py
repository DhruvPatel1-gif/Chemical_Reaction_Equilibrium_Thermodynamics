import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path regardless of execution environment
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import theme

st.set_page_config(
    page_title="Chemical Reaction Equilibrium",
    page_icon="⚗️",
    layout="wide",
)

# Colours follow the system light/dark setting; see theme.py (also contains the icon-font fix).
theme.apply_theme()

home = st.Page(
    "pages/home.py",
    title="Home",
    icon=":material/home:",
    default=True,
)

components = st.Page(
    "pages/components.py",
    title="Add Components",
    icon=":material/science:",
)

reaction = st.Page(
    "pages/reaction.py",
    title="Define Reaction",
    icon=":material/sync_alt:",
)

calculation_type = st.Page(
    "pages/calculation_type.py",
    title="Calculation Type",
    icon=":material/tune:",
)

condition = st.Page(
    "pages/condition.py",
    title="Equilibrium Calculation",
    icon=":material/calculate:",
)

pages = {
    "General": [home],
    "Setup": [components, reaction, calculation_type],
    "Calculations": [condition],
}

pg = st.navigation(pages)
pg.run()
