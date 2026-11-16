import streamlit as st
import pandas as pd
from Data import comp


if "selected_components" not in st.session_state:
    st.session_state.selected_components = []


if st.session_state.selected_components and isinstance(st.session_state.selected_components[0], str):
    previous_phase = st.session_state.get("phase", "Gas")
    st.session_state.selected_components = [
        {"component": name, "phase": previous_phase}
        for name in st.session_state.selected_components
    ]

st.title("Component Selection")
st.write("Select the chemical components required for your reaction.")
st.divider()

st.session_state.phase = st.selectbox(
    "Select Phase of Components",
    ["Gas", "Liquid", "Solid", "Aqueous"],
    width=200,
)

comp_col, add_col = st.columns([3, 1])
with comp_col:
    component = st.selectbox(
        "Select Component",
        comp[st.session_state.phase],
        width=500,
    )

with add_col:
    st.write("")
    st.write("")
    if st.button("Add Component"):
        already_added = any(
            item["component"] == component and item["phase"] == st.session_state.phase
            for item in st.session_state.selected_components
        )
        if not already_added:
            st.session_state.selected_components.append(
                {"component": component, "phase": st.session_state.phase}
            )
            st.rerun()
        else:
            st.warning("This component is already added in this phase.")

with st.expander("Species not in the database? Add a custom component"):
    st.caption(
        "Use this for problems that give you the equilibrium data directly (for example "
        "'A → B with ΔG° = -1000 J/mol'). The phase is the one chosen above. For custom "
        "species choose 'Manual ΔG°298 / ΔH°298' or 'Direct K' on the calculation page."
    )
    custom_col, custom_add_col = st.columns([3, 1])
    with custom_col:
        custom_name = st.text_input("Custom species name", key="custom_species_name", placeholder="e.g. A")
    with custom_add_col:
        st.write("")
        st.write("")
        if st.button("Add custom component"):
            custom_name = custom_name.strip()
            if not custom_name:
                st.warning("Enter a name for the custom species.")
            elif any(
                item["component"] == custom_name and item["phase"] == st.session_state.phase
                for item in st.session_state.selected_components
            ):
                st.warning("This component is already added in this phase.")
            else:
                st.session_state.selected_components.append(
                    {"component": custom_name, "phase": st.session_state.phase}
                )
                st.rerun()

st.subheader("Selected Components")

if not st.session_state.selected_components:
    st.info("No components selected yet.")
else:
    for index, item in enumerate(st.session_state.selected_components):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(item["component"])
        with col2:
            st.write(item["phase"])
        with col3:
            if st.button("Remove", key=f"remove_component_{index}"):
                removed_label = f'{item["component"]} ({item["phase"]})'


                st.session_state.reaction_data = [
                    reaction_item
                    for reaction_item in st.session_state.get("reaction_data", [])
                    if not (
                        reaction_item.get("component") == item["component"]
                        and reaction_item.get("phase") == item["phase"]
                    )
                ]

                # Clear reaction dropdown selections that refer to the removed component.
                for key in list(st.session_state.keys()):
                    if (key.startswith("reactant_") or key.startswith("product_")) and st.session_state.get(key) == removed_label:
                        del st.session_state[key]

                st.session_state.selected_components.pop(index)
                st.rerun()

# A compact view of the selected component-phase pairs.
df = pd.DataFrame(st.session_state.selected_components)
if not df.empty:
    st.dataframe(df.rename(columns={"component": "Component", "phase": "Phase"}), hide_index=True, width="stretch")
