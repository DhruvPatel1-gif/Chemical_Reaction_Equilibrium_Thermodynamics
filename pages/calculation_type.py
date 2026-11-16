import streamlit as st

st.title("Define Calculation")

st.write(
    "Select the quantity you want to calculate. "
    "The Equilibrium Calculation page then asks only for the information that this "
    "type of problem needs."
)

st.divider()

# ==========================================================
# WHAT DOES THE USER WANT TO CALCULATE?
# ==========================================================

calculation_options = {
    "Equilibrium Composition": "composition",
    "Equilibrium Conversion": "conversion",
    "Equilibrium Temperature": "temperature",
    "Equilibrium Pressure": "pressure",
    "Required Feed Composition": "feed",
}

# What each calculation type needs (used for the help panel and for
# st.session_state.given_information, which older pages still read).
requirements = {
    "composition": {
        "given": ["temperature", "pressure", "feed"],
        "text": "Given T, P and the feed → equilibrium moles and mole fractions "
                "(conversion is reported as well).",
    },
    "conversion": {
        "given": ["temperature", "pressure", "feed"],
        "text": "Given T, P and the feed → equilibrium conversion of each reactant.",
    },
    "temperature": {
        "given": ["pressure", "feed", "equilibrium_composition"],
        "text": "Given P, the feed and one equilibrium condition (a mole fraction or a "
                "conversion) → the temperature at which it is reached.",
    },
    "pressure": {
        "given": ["temperature", "feed", "equilibrium_composition"],
        "text": "Given T, the feed and one equilibrium condition (a mole fraction or a "
                "conversion) → the pressure at which it is reached.",
    },
    "feed": {
        "given": ["temperature", "pressure", "equilibrium_composition"],
        "text": "Given T, P, one equilibrium condition and the rest of the feed (your basis) → "
                "the unknown feed amount, e.g. how much steam or excess reactant is needed.",
    },
}

current_key = st.session_state.get("calculation_type", "composition")
labels = list(calculation_options)
current_label = next((k for k, v in calculation_options.items() if v == current_key), labels[0])

calculation = st.selectbox(
    "Select the required calculation",
    labels,
    index=labels.index(current_label),
)

selected = calculation_options[calculation]
st.info(requirements[selected]["text"])

st.markdown(
    "**Also available on the calculation page**\n"
    "- inert / diluent species (steam, N₂ …) in the feed\n"
    "- gas models: ideal, Peng–Robinson, SRK, virial, and *ideal solution of real gases*\n"
    "- liquid models: ideal, Margules, Van Laar, Wilson, NRTL or your own Gᴱ/RT expression\n"
    "- K(T) from the database, from a manual ΔG°/ΔH°, or entered directly\n"
    "- solids with unit activity, unit conversion (°C, atm …), and an ideal-vs-real comparison"
)

if st.button("Continue", type="primary"):
    st.session_state.calculation_type = selected
    st.session_state.given_information = requirements[selected]["given"]
    st.success("Calculation type saved. Open 'Equilibrium Calculation' to continue.")
