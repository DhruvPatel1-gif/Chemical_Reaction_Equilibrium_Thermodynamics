import streamlit as st
from Data import heat_capacity_data, formation_properties_298

phase_key = {"Gas": "gas", "Liquid": "liquid", "Solid": "solid", "Aqueous": "aq"}

if "selected_reactant" not in st.session_state:
    st.session_state.selected_reactant = []
if "selected_product" not in st.session_state:
    st.session_state.selected_product = []
if "reaction_data" not in st.session_state:
    st.session_state.reaction_data = []

# Build readable, unique dropdown labels. A component can be present in
# more than one phase, so its phase is included in the label.
selected_components = st.session_state.get("selected_components", [])
component_options = {
    f'{item["component"]} ({item["phase"]})': item
    for item in selected_components
    if isinstance(item, dict) and "component" in item and "phase" in item
}
option_labels = list(component_options.keys())

st.title("Reaction Definition")
st.write("Define the reactants, products and their stoichiometric coefficients.")
st.divider()

if not option_labels:
    st.warning("Please add components on the Component Selection page first.")
else:
    Reactants, Products = st.columns(2, gap="large")

    with Reactants:
        if st.button("Add Reactant"):
            st.session_state.selected_reactant.append(None)
            st.rerun()

        for i, item in enumerate(st.session_state.selected_reactant):
            reactant, coefficient_r, remove_r = st.columns(3)
            with reactant:
                st.selectbox(
                    "Select Reactant",
                    option_labels,
                    key=f"reactant_{i}",
                )
            with coefficient_r:
                st.number_input("Coefficient", min_value=1, max_value=100, value=1, key=f"reactant_coefficient_{i}")
            with remove_r:
                if st.button("Remove", key=f"remove_button_{i}"):
                    st.session_state.selected_reactant.pop(i)
                    st.rerun()

    with Products:
        if st.button("Add Product"):
            st.session_state.selected_product.append(None)
            st.rerun()

        for i, item in enumerate(st.session_state.selected_product):
            product, coefficient_p, remove_p = st.columns(3)
            with product:
                st.selectbox(
                    "Select Product",
                    option_labels,
                    key=f"product_{i}",
                )
            with coefficient_p:
                st.number_input("Coefficient", min_value=1, max_value=100, value=1, key=f"product_coeff_{i}")
            with remove_p:
                if st.button("Remove", key=f"remove_p_{i}"):
                    st.session_state.selected_product.pop(i)
                    st.rerun()

    if st.button("Save Reaction"):
        reaction_data = []

        for i, item in enumerate(st.session_state.selected_reactant):
            selected_label = st.session_state.get(f"reactant_{i}")
            if selected_label in component_options:
                selected = component_options[selected_label]
                coefficient = st.session_state[f"reactant_coefficient_{i}"]
                reaction_data.append({
                    "component": selected["component"],
                    "phase": selected["phase"],
                    "coefficient": -coefficient,
                })

        for i, item in enumerate(st.session_state.selected_product):
            selected_label = st.session_state.get(f"product_{i}")
            if selected_label in component_options:
                selected = component_options[selected_label]
                coefficient = st.session_state[f"product_coeff_{i}"]
                reaction_data.append({
                    "component": selected["component"],
                    "phase": selected["phase"],
                    "coefficient": coefficient,
                })

        st.session_state.reaction_data = reaction_data

reaction_data = st.session_state.get("reaction_data", [])
if reaction_data:
    st.write(reaction_data)

    reactant_terms = []
    product_terms = []
    missing_formulas = []

    for item in reaction_data:
        component = item["component"]
        phase = item["phase"]
        coefficient = item["coefficient"]
        phase_database_key = phase_key[phase]

        # Formula data is phase-specific. If the formation-property table
        # does not contain this species, use its component identifier and
        # show a notice rather than stopping the whole page with KeyError.
        species_data = formation_properties_298.get(phase_database_key, {}).get(component, {})
        formula = species_data.get("formula", component)
        if "formula" not in species_data:
            missing_formulas.append(f"{component} ({phase})")

        # Omit coefficient 1 from the displayed chemical equation.
        coefficient_text = "" if abs(coefficient) == 1 else str(abs(coefficient))
        term = f"{coefficient_text} {formula}".strip()

        if coefficient < 0:
            reactant_terms.append(term)
        elif coefficient > 0:
            product_terms.append(term)

    reactant_string = " + ".join(reactant_terms) or ""
    product_string = " + ".join(product_terms) or ""
    reaction_equation = f"\\mathrm{{{reactant_string} \\rightleftharpoons {product_string}}}"
    st.latex(r"\huge " + reaction_equation)

    if missing_formulas:
        st.warning(
            "A formula was not found in formation_properties_298 for: "
            + ", ".join(missing_formulas)
            + ". These are displayed using their component identifiers for now."
        )
