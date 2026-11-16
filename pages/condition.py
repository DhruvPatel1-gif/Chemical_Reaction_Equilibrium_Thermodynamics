import datetime
import math

import numpy as np
import pandas as pd
import streamlit as st

import equilibrium_engine as eq
import theme
from Data import comp, formation_properties_298, heat_capacity_data

try:
    import report as report_tools
except Exception:  # the page still works without the report module
    report_tools = None

# ============================================================
# PAGE SETUP
# ============================================================

theme.hero(
    "Equilibrium Calculation",
    "Choose the unknown, set the equilibrium constant and models, then define the conditions and feed.",
    eyebrow="Chemical Engineering Thermodynamics",
)

if "reaction_data" not in st.session_state or not st.session_state.reaction_data:
    st.error("Please define and save a reaction before opening this page.")
    st.stop()

base_reaction = [
    dict(component=item["component"],
         phase=item["phase"].lower(),
         coefficient=float(item["coefficient"]))
    for item in st.session_state.reaction_data
]

CALC_LABELS = {
    "composition": "Equilibrium composition",
    "conversion": "Equilibrium conversion",
    "temperature": "Equilibrium temperature",
    "pressure": "Equilibrium pressure",
    "feed": "Required feed composition",
}
CALC_HELP = {
    "composition": "Given T, P and the feed: equilibrium moles and mole fractions.",
    "conversion": "Given T, P and the feed: equilibrium conversion of each reactant.",
    "temperature": "Given P, the feed and one equilibrium condition: the temperature that meets it.",
    "pressure": "Given T, the feed and one equilibrium condition: the pressure that meets it.",
    "feed": "Given T, P, one equilibrium condition and the rest of the feed: the unknown feed amount.",
}
calc_keys = list(CALC_LABELS)
saved_calc = st.session_state.get("calculation_type", "composition")
if saved_calc not in calc_keys:
    saved_calc = "composition"

# ============================================================
# ROW 1  -  GOAL  |  1. REACTION + INERT SPECIES
# ============================================================

col_goal, col_rxn = st.columns([1, 1.6], gap="large")

with col_goal:
    with st.container(key="card_goal"):
        theme.card_title("", "What do you want to calculate?", "This decides which inputs are needed below.")
        calc = st.selectbox(
            "Calculation",
            calc_keys,
            index=calc_keys.index(saved_calc),
            format_func=CALC_LABELS.get,
            key="condition_calc_selector",
            label_visibility="collapsed",
        )
        st.caption(CALC_HELP[calc])
st.session_state.calculation_type = calc

in_reaction = {(r["component"], r["phase"]) for r in base_reaction}
inert_options = [
    f"{name} ({phase})"
    for phase in ("Gas", "Liquid")
    for name in comp[phase]
    if (name, phase.lower()) not in in_reaction
]

with col_rxn:
    with st.container(key="card_reaction"):
        theme.card_title(1, "Reaction", "From the Setup pages. Add inert or diluent species if they are in the feed.")
        theme.equation_box(eq.reaction_equation(base_reaction))
        inert_labels = st.multiselect(
            "Inert / diluent species present in the feed (optional)",
            inert_options,
            help="Species that do not take part in the reaction, e.g. steam, N₂ or a solvent.",
        )
        custom_inert = st.text_input(
            "Other inert species not in the database (comma-separated, gas phase)",
            placeholder="e.g. argon, helium",
        )

reaction = list(base_reaction)
for label in inert_labels:
    name, phase = label.rsplit(" (", 1)
    reaction.append(dict(component=name, phase=phase.rstrip(")").lower(), coefficient=0.0))
for name in [x.strip() for x in custom_inert.split(",") if x.strip()]:
    if (name, "gas") not in in_reaction:
        reaction.append(dict(component=name, phase="gas", coefficient=0.0))

N = len(reaction)
names = [r["component"] for r in reaction]
phases = [r["phase"] for r in reaction]
nu = np.array([r["coefficient"] for r in reaction])
gas_idx = [i for i in range(N) if phases[i] == "gas"]
liq_idx = [i for i in range(N) if phases[i] == "liquid"]


def label_of(i):
    return f"{names[i]} ({phases[i]})"


if any(p not in ("gas", "liquid", "solid") for p in phases):
    st.error("Aqueous species are not supported yet. Use gas, liquid and pure-solid species.")
    st.stop()
if not np.any(nu < 0) or not np.any(nu > 0):
    st.error("The reaction needs at least one reactant (negative coefficient) and one product.")
    st.stop()

# ============================================================
# ROW 2  -  2. EQUILIBRIUM CONSTANT  |  3. THERMODYNAMIC MODELS
# ============================================================

col_k, col_m = st.columns([1, 1.3], gap="large")

k_modes = ["Database (ΔH°f, ΔG°f, Cp)", "Manual ΔG°298 / ΔH°298", "Direct K value"]
k_mode = k_modes[0]
k_detail = ""
ignore_cp = False
std, db_error = None, None

with col_k:
    with st.container(key="card_k"):
        theme.card_title(2, "Equilibrium constant", "Where K(T) comes from.")

        try:
            std = eq.standard_reaction_properties(reaction, formation_properties_298, heat_capacity_data)
        except eq.DataMissing as error:
            db_error = str(error)
            if "heat-capacity" in db_error and "formation" not in db_error:
                ignore_cp = st.checkbox("Treat species without Cp data as ΔCp = 0 and continue", value=False)
                if ignore_cp:
                    std = eq.standard_reaction_properties(
                        reaction, formation_properties_298, heat_capacity_data, ignore_missing_cp=True)
                    db_error = None

        k_mode = st.radio("Source of K(T)", k_modes, index=0 if std else 1)

        if k_mode == k_modes[0]:
            if std is None:
                st.error(f"Database values are missing: {db_error}. Choose 'Manual' to enter them yourself.")
                st.stop()
            lnK_fn = eq.make_lnK(std["dH298"], std["dG298"], std["dA"], std["dB"], std["dC"], std["dD"])
            K298 = math.exp(max(min(-std["dG298"] / (eq.R * eq.T_REF), 700), -700))
            theme.stat_tiles([
                ("ΔH°298", f"{std['dH298'] / 1000:,.2f} kJ/mol"),
                ("ΔG°298", f"{std['dG298'] / 1000:,.2f} kJ/mol"),
                ("K at 298.15 K", f"{K298:.5g}"),
            ])
            for note in std["notes"]:
                st.caption("ℹ️ " + note)
            k_detail = (f"Database values: ΔH°298 = {std['dH298']:,.0f} J/mol, "
                        f"ΔG°298 = {std['dG298']:,.0f} J/mol (K at 298.15 K = {K298:.5g})")
        elif k_mode == k_modes[1]:
            c1, c2 = st.columns(2)
            dG_in = c1.number_input("ΔG°298 (J/mol)", value=float(std["dG298"]) if std else 0.0,
                                    step=100.0, format="%.6g")
            dH_in = c2.number_input("ΔH°298 (J/mol)", value=float(std["dH298"]) if std else 0.0,
                                    step=100.0, format="%.6g",
                                    help="With ΔH° = 0 (and no ΔCp) K is constant with temperature.")
            with st.expander("Heat-capacity change ΔCp/R = ΔA + ΔB·T + ΔC·T² + ΔD/T²  (optional)"):
                d1, d2, d3, d4 = st.columns(4)
                dA_in = d1.number_input("ΔA", value=float(std["dA"]) if std else 0.0, format="%.6g")
                dB_in = d2.number_input("ΔB", value=float(std["dB"]) if std else 0.0, format="%.6g")
                dC_in = d3.number_input("ΔC", value=float(std["dC"]) if std else 0.0, format="%.6g")
                dD_in = d4.number_input("ΔD", value=float(std["dD"]) if std else 0.0, format="%.6g")
            lnK_fn = eq.make_lnK(dH_in, dG_in, dA_in, dB_in, dC_in, dD_in)
            k_detail = f"Manual values: ΔG°298 = {dG_in:,.6g} J/mol, ΔH°298 = {dH_in:,.6g} J/mol"
            if any((dA_in, dB_in, dC_in, dD_in)):
                k_detail += f", ΔCp/R = {dA_in:g} + {dB_in:g}T + {dC_in:g}T² + {dD_in:g}/T²"
        else:
            K_in = st.number_input("Equilibrium constant K (dimensionless, P° = 1 bar)", value=1.0,
                                   min_value=1e-300, format="%.6g")
            lnK_fn = eq.make_constant_lnK(K_in)
            st.caption("K is treated as independent of temperature.")
            k_detail = f"Direct value: K = {K_in:.6g}, independent of temperature"

gas_txt = "No gas-phase species"
liq_txt = "No liquid-phase species"
gas_model = eq.GasModel("ideal")
liquid_model = eq.LiquidModel("ideal")

with col_m:
    with st.container(key="card_models"):
        theme.card_title(3, "Thermodynamic models", "Non-ideality of the gas and liquid phases.")

        # ---------------- gas ----------------
        if gas_idx:
            st.markdown("**Gas phase**")
            gas_choices = {
                "Ideal gas (φ = 1)": "ideal",
                "Peng–Robinson EOS": "pr",
                "Soave–Redlich–Kwong EOS": "srk",
                "Virial, 2nd coefficient (Pitzer B⁰/B¹)": "virial",
            }
            gas_label = st.selectbox("Gas-phase model", list(gas_choices))
            eos = gas_choices[gas_label]
            ideal_solution = st.checkbox(
                "Ideal solution of real gases (Lewis/Randall rule: φ̂ᵢ = φᵢ of the pure gas at T, P)",
                value=False, disabled=(eos == "ideal"))
            gas_txt = gas_label + (", ideal solution of real gases (Lewis/Randall rule)"
                                   if (ideal_solution and eos != "ideal") else "")
            if eos != "ideal":
                rows = []
                property_records = []
                database_missing = []
                formula_by_name = {}

                for i in gas_idx:
                    name = names[i]

                    # First obtain the formula from the selected component's database
                    # entry. Some species use a different key in the formation table.
                    cp_key = eq.find_key(heat_capacity_data, "gas", name)
                    formula = None
                    if cp_key:
                        formula = heat_capacity_data["gas"][cp_key].get("formula")

                    if formula is None:
                        form_key = eq.find_key(formation_properties_298, "gas", name)
                        if form_key:
                            formula = formation_properties_298["gas"][form_key].get("formula")

                    formula_by_name[name] = formula
                    # Try the database name first, then its formula through thermo.Chemical.
                    critical = eq.critical_properties(name, formula)
                    is_database_species = name in comp.get("Gas", [])

                    required = ["Tc", "Pc", "omega"]
                    if eos == "virial":
                        required += ["Zc", "Vc"]

                    if critical is None:
                        critical = {key: None for key in ("Tc", "Pc", "omega", "Zc", "Vc")}

                    missing = [key for key in required if critical.get(key) is None]
                    if missing and is_database_species:
                        database_missing.append(f"{name}: {', '.join(missing)}")
                    property_records.append((i, name, is_database_species, critical, missing))

                    rows.append({
                        "Species": name,
                        "Source": "thermo library" if not missing else (
                            "Database species — lookup incomplete" if is_database_species
                            else "User-defined — manual values needed"
                        ),
                        "Tc (K)": critical.get("Tc"),
                        "Pc (bar)": critical.get("Pc") / 1e5 if critical.get("Pc") is not None else None,
                        "Acentric factor (ω)": critical.get("omega"),
                        "Critical compressibility (Zc)": critical.get("Zc"),
                        "Critical volume (cm³/mol)": critical.get("Vc") * 1e6 if critical.get("Vc") is not None else None,
                    })

                st.markdown("**Critical properties retrieved from the `thermo` library**")
                st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

                if database_missing:
                    st.error(
                        "The thermo library could not provide all required critical properties "
                        "for these database components: " + "; ".join(database_missing) +
                        ". No estimated values have been substituted. Try another EOS or update "
                        "the thermo package if the component should be supported."
                    )
                    with st.expander("Why was the lookup incomplete? (diagnostics)"):
                        for entry in database_missing:
                            sp = entry.split(":")[0]
                            diag = eq.critical_diagnostics(sp, formula_by_name.get(sp))
                            st.markdown(f"**{sp}**")
                            if diag["import_error"]:
                                st.error("`thermo` could not be imported in the Python environment running "
                                         f"Streamlit: {diag['import_error']}. Install it there with "
                                         "`pip install thermo` and restart the app.")
                            else:
                                st.caption(f"thermo version {diag['thermo_version']}")
                                st.dataframe(pd.DataFrame(diag["attempts"],
                                                          columns=["Identifier tried", "Route", "Outcome"]),
                                             hide_index=True, width="stretch")
                    st.stop()

                # Only custom/user-defined species may be completed manually.
                custom_missing = [(i, name, critical, missing)
                                  for i, name, is_db, critical, missing in property_records
                                  if missing and not is_db]
                if custom_missing:
                    st.warning(
                        "The following user-defined species were not fully recognised by "
                        "thermo.Chemical. Enter the missing values manually."
                    )
                    for i, name, critical, missing in custom_missing:
                        st.markdown(f"**{name} (user-defined)**")
                        cols = st.columns(len(missing))
                        for col, prop_name in zip(cols, missing):
                            labels = {
                                "Tc": "Tc (K)",
                                "Pc": "Pc (bar)",
                                "omega": "Acentric factor (ω)",
                                "Zc": "Critical compressibility (Zc)",
                                "Vc": "Critical volume (cm³/mol)",
                            }
                            value = col.number_input(
                                labels[prop_name],
                                value=0.0,
                                min_value=0.0 if prop_name != "omega" else -5.0,
                                key=f"custom_crit_{i}_{prop_name}",
                                format="%.8g",
                            )
                            critical[prop_name] = (
                                value * 1e5 if prop_name == "Pc" else
                                value * 1e-6 if prop_name == "Vc" else value
                            )

                # Arrange the property arrays in exactly the same order as gas_idx.
                final_records = {i: critical for i, _, _, critical, _ in property_records}
                for i, name, is_db, critical, missing in property_records:
                    if missing and not is_db:
                        critical = final_records[i]
                required_values = ["Tc", "Pc", "omega"] + (["Zc", "Vc"] if eos == "virial" else [])
                for i, name, is_db, critical, missing in property_records:
                    if any(critical.get(key) is None or critical.get(key) == 0
                           for key in required_values if key != "omega"):
                        st.error(f"Required critical properties are incomplete for {name}.")
                        st.stop()
                    if critical.get("omega") is None:
                        st.error(f"Acentric factor is missing for {name}.")
                        st.stop()

                props = {
                    "Tc": [final_records[i]["Tc"] for i in gas_idx],
                    "Pc": [final_records[i]["Pc"] for i in gas_idx],
                    "omega": [final_records[i]["omega"] for i in gas_idx],
                    "Zc": [final_records[i]["Zc"] for i in gas_idx],
                    "Vc": [final_records[i]["Vc"] for i in gas_idx],
                }
                kij = None
                if len(gas_idx) > 1 and not ideal_solution:
                    with st.expander("Binary interaction parameters kᵢⱼ (default 0)"):
                        kdf = st.data_editor(
                            pd.DataFrame(np.zeros((len(gas_idx),) * 2),
                                         index=[names[i] for i in gas_idx],
                                         columns=[names[i] for i in gas_idx]),
                            key="kij_editor_" + "_".join(names[i] for i in gas_idx))
                        kij = kdf.values
                gas_model = eq.GasModel(eos, ideal_solution, props, kij)

        # ---------------- liquid ----------------
        if len(liq_idx) >= 2:
            if gas_idx:
                st.divider()
            st.markdown("**Liquid phase**")
            m = len(liq_idx)
            ln_ = [names[i] for i in liq_idx]
            liq_choices = {
                "Ideal solution (γ = 1)": "ideal",
                "Margules  (Gᴱ/RT = Σ Aᵢⱼ xᵢ xⱼ)": "margules",
                "Van Laar (binary)": "van_laar",
                "Wilson": "wilson",
                "NRTL": "nrtl",
                "Custom Gᴱ/RT expression": "custom",
            }
            liq_label = st.selectbox("Liquid-phase activity model", list(liq_choices))
            kind = liq_choices[liq_label]
            liq_txt = liq_label
            tag = "_".join(ln_)

            def grid_inputs(items, ncols=3):
                values = []
                for start in range(0, len(items), ncols):
                    cols = st.columns(ncols)
                    for col, (label, key, default, step) in zip(cols, items[start:start + ncols]):
                        values.append(col.number_input(label, value=default, step=step, key=key, format="%.6g"))
                return values

            ordered = [(a, b) for a in range(m) for b in range(m) if a != b]
            unordered = [(a, b) for a in range(m) for b in range(a + 1, m)]
            try:
                if kind == "margules":
                    vals = grid_inputs([(f"A({ln_[a]}, {ln_[b]})", f"mar_{tag}_{a}{b}", 0.0, 0.05) for a, b in unordered])
                    A = np.zeros((m, m))
                    for (a, b), v in zip(unordered, vals):
                        A[a, b] = A[b, a] = v
                    liquid_model = eq.LiquidModel("margules", {"A": A})
                    st.caption("For a binary this is Gᴱ/RT = A·x₁x₂, i.e. ln γ₁ = A·x₂², ln γ₂ = A·x₁².")
                    liq_txt += ": " + ", ".join(f"A({ln_[a]}, {ln_[b]}) = {v:g}" for (a, b), v in zip(unordered, vals))
                elif kind == "van_laar":
                    if m != 2:
                        st.error("Van Laar is available for binary liquid mixtures only.")
                        st.stop()
                    a12, a21 = grid_inputs([(f"A₁₂ = ln γ({ln_[0]}) at infinite dilution", f"vl12_{tag}", 0.0, 0.05),
                                            (f"A₂₁ = ln γ({ln_[1]}) at infinite dilution", f"vl21_{tag}", 0.0, 0.05)], 2)
                    liquid_model = eq.LiquidModel("van_laar", {"A12": a12, "A21": a21})
                    liq_txt += f": A12 = {a12:g}, A21 = {a21:g}"
                elif kind == "wilson":
                    st.caption("Wilson parameters are retrieved from Thermo's ChemSep Wilson database using component CAS numbers.")
                    formulas = []
                    for name in ln_:
                        fkey = eq.find_key(formation_properties_298, "liquid", name)
                        formula = formation_properties_298.get("liquid", {}).get(fkey, {}).get("formula") if fkey else None
                        formulas.append(formula)
                    matrices, report = eq.liquid_interaction_parameters("wilson", ln_, formulas)
                    st.caption("Source: " + report["table"])
                    st.dataframe(pd.DataFrame({"Component": ln_, "CAS": report["cas"]}), hide_index=True, width="stretch")
                    st.markdown("**Wilson coefficients** — ln(Λᵢⱼ) = aᵢⱼ + bᵢⱼ/T")
                    a_df = st.data_editor(pd.DataFrame(matrices["aij"], index=ln_, columns=ln_),
                                          key=f"wilson_a_{tag}", num_rows="fixed")
                    b_df = st.data_editor(pd.DataFrame(matrices["bij"], index=ln_, columns=ln_),
                                          key=f"wilson_b_{tag}", num_rows="fixed")
                    if a_df.isna().any().any() or b_df.isna().any().any():
                        st.warning("Some Wilson binary parameters are unavailable. Enter the missing values manually before calculating.")
                        st.stop()
                    liquid_model = eq.LiquidModel("wilson", {"mode": "thermo", "a": a_df.values, "b": b_df.values})
                    liq_txt += f", parameters from {report['table']}"
                    with st.expander("Parameter retrieval status"):
                        for pair, status in report["pairs"].items():
                            st.write(f"**{pair}:** {status}")
                elif kind == "nrtl":
                    st.caption("NRTL parameters are retrieved from Thermo's ChemSep NRTL database using component CAS numbers.")
                    formulas = []
                    for name in ln_:
                        fkey = eq.find_key(formation_properties_298, "liquid", name)
                        formula = formation_properties_298.get("liquid", {}).get(fkey, {}).get("formula") if fkey else None
                        formulas.append(formula)
                    matrices, report = eq.liquid_interaction_parameters("nrtl", ln_, formulas)
                    st.caption("Source: " + report["table"] + " | τᵢⱼ = aᵢⱼ + bᵢⱼ/T")
                    st.dataframe(pd.DataFrame({"Component": ln_, "CAS": report["cas"]}), hide_index=True, width="stretch")
                    st.markdown("**NRTL coefficients**")
                    a_df = st.data_editor(pd.DataFrame(matrices["aij"], index=ln_, columns=ln_),
                                          key=f"nrtl_a_{tag}", num_rows="fixed")
                    b_df = st.data_editor(pd.DataFrame(matrices["bij"], index=ln_, columns=ln_),
                                          key=f"nrtl_b_{tag}", num_rows="fixed")
                    alpha_df = st.data_editor(pd.DataFrame(matrices["alphaij"], index=ln_, columns=ln_),
                                              key=f"nrtl_alpha_{tag}", num_rows="fixed")
                    if a_df.isna().any().any() or b_df.isna().any().any() or alpha_df.isna().any().any():
                        st.warning("Some NRTL binary parameters are unavailable. Enter the missing values manually before calculating.")
                        st.stop()
                    liquid_model = eq.LiquidModel("nrtl", {"a": a_df.values, "b": b_df.values, "alpha": alpha_df.values})
                    liq_txt += f", parameters from {report['table']}"
                    with st.expander("Parameter retrieval status"):
                        for pair, status in report["pairs"].items():
                            st.write(f"**{pair}:** {status}")
                elif kind == "custom":
                    vars_ = {}
                    for k, n in enumerate(ln_):
                        vars_[f"x{k + 1}"] = k
                        safe = "".join(ch if ch.isalnum() else "_" for ch in n)
                        if safe and not safe[0].isdigit():
                            vars_[f"x_{safe}"] = k
                    expr = st.text_input("Gᴱ/RT as a function of the liquid mole fractions",
                                         value="0.1*x1*x2", key=f"ge_expr_{tag}")
                    st.caption("Variables: " + ", ".join(f"x{k + 1} = {n}" for k, n in enumerate(ln_)) +
                               ", T (K).  Functions: exp, log, sqrt.  Use ** or ^ for powers.")
                    liquid_model = eq.LiquidModel("custom", {"expr": expr, "vars": vars_})
                    liq_txt += f": Gᴱ/RT = {expr}"
            except Exception as error:
                st.error(f"Liquid model error: {error}")
                st.stop()

            if kind != "ideal":
                st.caption("Liquid activities: aᵢ = γᵢ xᵢ with the pure liquid at T as the standard state.")
        elif len(liq_idx) == 1:
            liq_txt = "Single liquid species, pure liquid (activity = 1)"
            if gas_idx:
                st.divider()
            st.markdown("**Liquid phase**")
            st.caption("Single liquid species: activity = 1 (pure liquid).")

        if not gas_idx and not liq_idx:
            st.caption("Only pure solids take part in this reaction, so there is no gas or liquid model to choose.")

# ============================================================
# ROW 3  -  4. OPERATING CONDITIONS  |  5. FEED
# ============================================================

col_op, col_feed = st.columns([1, 1.3], gap="large")

T_search = P_search = None
with col_op:
    with st.container(key="card_op"):
        theme.card_title(4, "Operating conditions", "Temperature and pressure of the reactor.")
        if calc == "temperature":
            st.markdown("**Temperature search range**")
            ta, tb = st.columns(2)
            Tmin_in = ta.number_input("From (K)", value=300.0, min_value=1.0, step=50.0)
            Tmax_in = tb.number_input("To (K)", value=1500.0, min_value=2.0, step=50.0)
            T_search = (Tmin_in, Tmax_in)
            T = None
        else:
            t_unit = st.radio("Temperature unit", ["K", "°C"], horizontal=True)
            t_val = st.number_input(f"Temperature ({t_unit})", value=500.0 if t_unit == "K" else 227.0,
                                    step=1.0, format="%.6g")
            T = t_val if t_unit == "K" else t_val + 273.15
            if t_unit == "°C":
                st.caption(f"= {T:.2f} K")
        st.divider()
        if calc == "pressure":
            st.markdown("**Pressure search range**")
            pa, pb = st.columns(2)
            Pmin_in = pa.number_input("From (bar)", value=0.01, min_value=1e-6, format="%.6g")
            Pmax_in = pb.number_input("To (bar)", value=1000.0, min_value=1e-5, format="%.6g")
            P_search = (Pmin_in, Pmax_in)
            P = None
        else:
            p_unit = st.radio("Pressure unit", list(eq.PRESSURE_TO_BAR), horizontal=True)
            p_val = st.number_input(f"Pressure ({p_unit})", value=1.0, min_value=1e-9, step=0.1, format="%.6g")
            P = p_val * eq.PRESSURE_TO_BAR[p_unit]
            if p_unit != "bar":
                st.caption(f"= {P:.5g} bar")

unknown_j = None
n0 = np.zeros(N)
first_reactant = int(np.where(nu < 0)[0][0])

with col_feed:
    with st.container(key="card_feed"):
        theme.card_title(5, "Feed", "Moles of each species entering the reactor.")
        if calc == "feed":
            unknown_j = st.selectbox(
                "Which feed amount is unknown?", range(N), format_func=label_of,
                help="Enter the other species per your basis; the unknown amount is solved so that the "
                     "equilibrium specification below is met.")
            feed_mode = "Enter moles of each species"
        else:
            feed_mode = st.radio("Feed specification", ["Enter moles of each species",
                                                         "Stoichiometric proportions of reactants"], horizontal=True)

        if feed_mode.startswith("Stoichiometric"):
            basis = st.number_input("Basis: total moles of reactants fed", value=1.0, min_value=1e-9, format="%.6g")
            react_total = float(-nu[nu < 0].sum())
            for i in range(N):
                if nu[i] < 0:
                    n0[i] = basis * (-nu[i]) / react_total
            inert_idx = [i for i in range(N) if nu[i] == 0]
            if inert_idx:
                cols = st.columns(min(2, len(inert_idx)))
                for k, i in enumerate(inert_idx):
                    n0[i] = cols[k % len(cols)].number_input(
                        f"Moles of {label_of(i)}", min_value=0.0, value=0.0, step=0.1,
                        key=f"eq_n0_{i}_{names[i]}_{phases[i]}", format="%.6g")
            st.caption("Feed: " + ", ".join(f"{names[i]} = {n0[i]:.4g}" for i in range(N) if n0[i] > 0))
        else:
            cols = st.columns(min(2, N))
            for i in range(N):
                if i == unknown_j:
                    cols[i % len(cols)].markdown(f"**{label_of(i)}**  \n*solved by the calculator*")
                    continue
                n0[i] = cols[i % len(cols)].number_input(
                    f"Moles of {label_of(i)}", min_value=0.0, value=1.0 if i == first_reactant else 0.0, step=0.1,
                    key=f"eq_n0_{i}_{names[i]}_{phases[i]}", format="%.6g")

# ============================================================
# ROW 4  -  6. SPECIFICATION (only when T, P or feed is the unknown)
# ============================================================

spec = None
spec_text = ""
if calc in ("temperature", "pressure", "feed"):
    with st.container(key="card_spec"):
        theme.card_title(6, "Equilibrium specification", "The condition at equilibrium that fixes the unknown.")
        spec_kind = st.radio("The condition at equilibrium is given as",
                             ["Mole fraction of a species (in its own phase)", "Conversion of a reactant"],
                             horizontal=True)
        sa, sb = st.columns(2)
        if spec_kind.startswith("Mole"):
            options = [i for i in range(N) if phases[i] in ("gas", "liquid")]
            s_idx = sa.selectbox("Species", options, format_func=label_of)
            s_val = sb.number_input("Equilibrium mole fraction (0 – 1; e.g. 10 mol-% = 0.10)",
                                    min_value=1e-9, max_value=1.0 - 1e-9, value=0.5, step=0.01, format="%.6g")
            spec = dict(type="mole_fraction", index=int(s_idx), value=float(s_val))
            spec_text = f"Equilibrium mole fraction of {label_of(int(s_idx))} = {s_val:g}"
        else:
            options = [i for i in range(N) if nu[i] < 0]
            s_idx = sa.selectbox("Reactant", options, format_func=label_of)
            s_val = sb.number_input("Equilibrium conversion (%)", min_value=1e-6, max_value=100.0 - 1e-6,
                                    value=50.0, step=1.0, format="%.6g")
            spec = dict(type="conversion", index=int(s_idx), value=float(s_val) / 100.0)
            spec_text = f"Equilibrium conversion of {label_of(int(s_idx))} = {s_val:g} %"

# ============================================================
# BUILD THE PROBLEM
# ============================================================

try:
    problem = eq.EquilibriumProblem(reaction, lnK_fn, gas_model, liquid_model)
except Exception as error:
    st.error(f"Could not set up the equilibrium problem: {error}")
    st.stop()

has_nonideal = (gas_model.eos != "ideal") or (liquid_model.kind != "ideal")

compare = False
with st.container(key="card_run"):
    theme.card_title("", "Solve", "Run the calculation with the inputs above.")
    if has_nonideal:
        compare = st.checkbox("Also solve with the ideal model (gas φ = 1, liquid γ = 1) and show the error",
                              value=False)
    run = st.button("Calculate", type="primary")


def run_case(prob):
    """Return a list of (solved value or None, state)."""
    if calc in ("composition", "conversion"):
        if n0.sum() <= 0:
            raise ValueError("Enter a positive initial amount of at least one species.")
        return [(None, prob.state(n0, T, P))]
    if calc == "temperature":
        return prob.solve_temperature(n0, P, spec, *T_search)
    if calc == "pressure":
        return prob.solve_pressure(n0, T, spec, *P_search)
    return prob.solve_feed(n0, unknown_j, T, P, spec)


def settings_snapshot():
    """Plain-text record of the inputs, stored with the results so the report matches what was solved."""
    inert = [label_of(i) for i in range(N) if nu[i] == 0]
    if calc == "temperature":
        t_txt = f"Solved (search range {T_search[0]:g} to {T_search[1]:g} K)"
    else:
        t_txt = f"{T:.2f} K ({T - 273.15:.2f} °C)"
    if calc == "pressure":
        p_txt = f"Solved (search range {P_search[0]:g} to {P_search[1]:g} bar)"
    else:
        p_txt = f"{P:.6g} bar ({P / 1.01325:.6g} atm)"
    feed_parts = []
    for i in range(N):
        if calc == "feed" and i == unknown_j:
            feed_parts.append(f"{label_of(i)} = to be solved")
        elif n0[i] > 0 or nu[i] != 0:
            feed_parts.append(f"{label_of(i)} = {n0[i]:.6g} mol")
    rows = [
        ("Quantity calculated", CALC_LABELS[calc]),
        ("Inert / diluent species", ", ".join(inert) if inert else "None"),
        ("Source of K(T)", k_mode),
        ("K(T) data", k_detail),
        ("Gas-phase model", gas_txt),
        ("Liquid-phase model", liq_txt),
        ("Temperature", t_txt),
        ("Pressure", p_txt),
        ("Feed", "; ".join(feed_parts)),
    ]
    if spec_text:
        rows.append(("Equilibrium specification", spec_text))
    return rows


if run:
    try:
        if calc != "feed" and n0.sum() <= 0:
            raise ValueError("Enter a positive initial amount of at least one species.")
        if calc == "feed" and np.delete(n0, unknown_j).sum() <= 0:
            raise ValueError("Give a positive amount for at least one other feed species (your basis).")
        out = dict(calc=calc, problem=problem, results=run_case(problem), ideal=None, ideal_error=None,
                   spec=spec, unknown_j=unknown_j,
                   tmax=(std or {}).get("tmax", {}) if k_mode == k_modes[0] else {},
                   nonideal=has_nonideal,
                   settings=settings_snapshot(),
                   reaction_text=eq.reaction_equation(reaction))
        if compare:
            ideal_problem = eq.EquilibriumProblem(reaction, lnK_fn, eq.GasModel("ideal"), eq.LiquidModel("ideal"))
            try:
                out["ideal"] = run_case(ideal_problem)
            except Exception as error:
                out["ideal_error"] = str(error)
        st.session_state["eq_output"] = out
    except Exception as error:
        st.session_state.pop("eq_output", None)
        st.error(f"Calculation could not be completed: {error}")

# ============================================================
# RESULT HELPERS
# ============================================================


def fmt_tbl(df):
    return df.style.format("{:.6g}", na_rep="—", subset=[c for c in df.columns if df[c].dtype.kind == "f"])


def result_tables(prob, s):
    n0_tot = s["n0"].sum()
    rows = []
    for i in range(len(prob.names)):
        coef = np.exp(s["lnphi"][i]) if prob.phases[i] == "gas" else (
            np.exp(s["lngam"][i]) if prob.phases[i] == "liquid" else np.nan)
        rows.append({
            "Component": prob.names[i],
            "Phase": prob.phases[i].capitalize(),
            "ν": prob.nu[i],
            "Initial moles": s["n0"][i],
            "Feed mole fraction": s["n0"][i] / n0_tot if n0_tot > 0 else np.nan,
            "Equilibrium moles": s["n"][i],
            "Mole fraction (own phase)": s["frac"][i],
            "φ̂ (gas) / γ (liquid)": coef,
            "Activity a": np.exp(s["lna"][i]) if prob.nu[i] != 0 else np.nan,
        })
    comp_df = pd.DataFrame(rows)
    conv_rows = [{"Reactant": f"{prob.names[i]} ({prob.phases[i]})", "Conversion (%)": 100 * s["conversion"][i]}
                 for i in range(len(prob.names)) if prob.nu[i] < 0]
    return comp_df, pd.DataFrame(conv_rows)


def k_expression(prob):
    def tex(name):
        return name.replace("_", r"\_")
    terms = []
    for i, name in enumerate(prob.names):
        if prob.nu[i] == 0:
            continue
        if prob.phases[i] == "gas":
            a = rf"\left(\hat{{\phi}}_{{\text{{{tex(name)}}}}}\,y_{{\text{{{tex(name)}}}}}\,\frac{{P}}{{P^\circ}}\right)"
        elif prob.phases[i] == "liquid":
            a = rf"\left(\gamma_{{\text{{{tex(name)}}}}}\,x_{{\text{{{tex(name)}}}}}\right)"
        else:
            continue
        terms.append(a + rf"^{{{prob.nu[i]:g}}}")
    return "K = " + (r"\;".join(terms) if terms else "1")


def headline_for(o, value, s):
    """One-line answer for temperature / pressure / feed problems (None otherwise)."""
    prob = o["problem"]
    if o["calc"] == "temperature":
        return f"Equilibrium temperature = {value:.4f} K  ({value - 273.15:.2f} °C)"
    if o["calc"] == "pressure":
        return f"Equilibrium pressure = {value:.6g} bar  ({value / 1.01325:.6g} atm)"
    if o["calc"] == "feed":
        return (f"Required feed of {prob.names[o['unknown_j']]} ({prob.phases[o['unknown_j']]}) = "
                f"{value:.6g} mol  (basis: the other feed amounts entered)")
    return None


def ideal_comparison(o, k, value, s):
    """DataFrame comparing the selected model with the ideal model for solution k (or None)."""
    prob = o["problem"]
    if o["ideal"] is None or k >= len(o["ideal"]):
        return None
    v_id, s_id = o["ideal"][k]
    if o["calc"] in ("temperature", "pressure", "feed"):
        what = {"temperature": "Temperature (K)", "pressure": "Pressure (bar)",
                "feed": f"Feed of {prob.names[o['unknown_j']] if o['unknown_j'] is not None else ''} (mol)"}[o["calc"]]
        cmp = pd.DataFrame({"Quantity": [what], "Selected model": [value], "Ideal model": [v_id]})
    else:
        cmp = pd.DataFrame({"Component": prob.names, "Selected model": s["frac"], "Ideal model": s_id["frac"]})
    cmp["Error of ideal model (%)"] = 100 * (cmp["Ideal model"] - cmp["Selected model"]) / cmp["Selected model"]
    if o["calc"] not in ("temperature", "pressure", "feed"):
        cmp = cmp[cmp["Selected model"].notna()]
    return cmp


def working_lines(prob, s):
    """Plain-text derivation shown in the app and in the report."""
    lines = ["K = Π aᵢ^νᵢ with aᵢ = φ̂ᵢ yᵢ P/P° (gas), γᵢ xᵢ (liquid), 1 (pure solid), P° = 1 bar."]
    parts = prob.lnK_fn.parts(s["T"])
    lines.append(f"ΔG°(T) = {parts['dG_T']:,.1f} J/mol → ln K = −ΔG°/RT = {s['lnK']:.6g} → K = {s['K']:.6g}")
    if not math.isnan(parts["dH_T"]):
        lines.append(f"ΔH°(T) = {parts['dH_T']:,.1f} J/mol,  ΔS°(T) = {parts['dS_T']:,.3f} J/(mol·K)")
    lnQ = float(prob.nu @ s["lna"])
    lines.append(f"At the solution: ln Π aᵢ^νᵢ = {lnQ:.8g}  vs  ln K = {s['lnK']:.8g}  (difference {lnQ - s['lnK']:.2e})")
    lines.append("Material balance: nᵢ = nᵢ,₀ + νᵢ ε;  R = 8.314 J/(mol·K).")
    return lines


def show_state(prob, s, header):
    st.markdown(f"##### {header}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Temperature", f"{s['T']:.4f} K", f"{s['T'] - 273.15:.2f} °C", delta_color="off")
    m2.metric("Pressure", f"{s['P']:.6g} bar")
    m3.metric("K", f"{s['K']:.6g}")
    m4.metric("Extent ε (mol)", f"{s['eps']:.6g}")
    comp_df, conv_df = result_tables(prob, s)
    st.dataframe(fmt_tbl(comp_df), width="stretch", hide_index=True)
    st.caption("Mole fractions are taken within each phase (gas within gas, liquid within liquid). "
               "Pure solids have unit activity and no mole fraction.")
    if not conv_df.empty:
        st.markdown("**Equilibrium conversion**")
        st.dataframe(fmt_tbl(conv_df), width="stretch", hide_index=True)
    return comp_df


# ---------------- report ----------------

def _cell(v):
    if isinstance(v, (float, np.floating)):
        return "—" if math.isnan(v) or math.isinf(v) else f"{v:.6g}"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    return str(v)


def _table(title, df, note=None, rename=None):
    if rename:
        df = df.rename(columns=rename)
    return dict(title=title, header=[str(c) for c in df.columns],
                rows=[[_cell(v) for v in row] for row in df.itertuples(index=False, name=None)], note=note)


def make_report_payload(o, title, author, include_working, include_ideal):
    prob = o["problem"]
    results = o["results"]
    solutions = []
    for k, (value, s) in enumerate(results):
        tag = f"Solution {k + 1}" if len(results) > 1 else "Equilibrium state"
        comp_df, conv_df = result_tables(prob, s)
        tables = [_table(
            "Equilibrium composition", comp_df,
            note="Mole fractions are taken within each phase. φ is the fugacity coefficient of a gas "
                 "component in the mixture, γ the activity coefficient of a liquid component; pure solids "
                 "have unit activity.",
            rename={"Equilibrium moles": "Equil. moles", "Mole fraction (own phase)": "Mole fraction",
                    "φ̂ (gas) / γ (liquid)": "φ / γ"})]
        if not conv_df.empty:
            tables.append(_table("Equilibrium conversion", conv_df))
        if include_ideal:
            cmp = ideal_comparison(o, k, value, s)
            if cmp is not None:
                tables.append(_table("Comparison with the ideal model", cmp))
        warnings = []
        over = [f"{n} (valid to {t:g} K)" for n, t in o["tmax"].items() if s["T"] > t]
        if over:
            warnings.append("Heat-capacity correlation extrapolated beyond its stated range for: " + ", ".join(over))
        solutions.append(dict(
            tag=tag,
            headline=headline_for(o, value, s),
            summary=[("Temperature", f"{s['T']:.4f} K ({s['T'] - 273.15:.2f} °C)"),
                     ("Pressure", f"{s['P']:.6g} bar"), ("K", f"{s['K']:.6g}"),
                     ("Extent ε (mol)", f"{s['eps']:.6g}")],
            tables=tables, warnings=warnings,
            working=working_lines(prob, s) if include_working else []))
    notes = ["Standard states: ideal gas at P° = 1 bar, pure liquid at the system temperature, pure solid."]
    if len(results) > 1:
        notes.append(f"{len(results)} mathematical solutions were found; check which one is physically meaningful.")
    if include_ideal and o["ideal_error"]:
        notes.append(f"The ideal-model comparison could not be completed: {o['ideal_error']}")
    return dict(title=title, author=author, date=datetime.date.today().strftime("%d %B %Y"),
                calc_label=CALC_LABELS[o["calc"]], reaction=o["reaction_text"],
                settings=o["settings"], solutions=solutions, notes=notes)


# ============================================================
# RESULTS
# ============================================================

out = st.session_state.get("eq_output")
if out is not None:
    prob = out["problem"]
    results = out["results"]
    with st.container(key="card_result"):
        theme.card_title("", "Results", CALC_LABELS[out["calc"]])
        if len(results) > 1:
            st.warning(f"{len(results)} mathematical solutions were found; each is shown below. "
                       "Check which one is physically meaningful.")

        for k, (value, s) in enumerate(results):
            tag = f"Solution {k + 1}" if len(results) > 1 else "Equilibrium state"
            head = headline_for(out, value, s)
            if head:
                st.success(head)
            if out["calc"] == "feed":
                tot = s["n0"].sum()
                st.info(f"Mole fraction of {prob.names[out['unknown_j']]} in the total feed = {value / tot:.6g}")
            show_state(prob, s, tag)

            # ---- ideal comparison ----
            cmp = ideal_comparison(out, k, value, s)
            if cmp is not None:
                st.markdown("**Comparison with the ideal model**")
                st.dataframe(fmt_tbl(cmp), width="stretch", hide_index=True)
            elif out["ideal_error"]:
                st.warning(f"The ideal-model comparison failed: {out['ideal_error']}")

            # ---- warnings & working ----
            over = [f"{n} (valid to {t:g} K)" for n, t in out["tmax"].items() if s["T"] > t]
            if over:
                st.warning("Heat-capacity correlation extrapolated beyond its stated range for: " + ", ".join(over))
            with st.expander(f"Show working ({tag.lower()})"):
                st.latex(k_expression(prob))
                for line in working_lines(prob, s)[1:]:
                    st.write(line)
            if k < len(results) - 1:
                st.divider()

    # ============================================================
    # REPORT
    # ============================================================

    with st.container(key="card_report"):
        theme.card_title("", "Report", "Download a formal PDF write-up of this calculation, set in Times New Roman.")
        if report_tools is None:
            st.info("Report generation needs the `report.py` module in the root directory.")
        else:
            r1, r2 = st.columns(2)
            rep_title = r1.text_input("Report title", value="Chemical Reaction Equilibrium Report", key="rep_title")
            rep_author = r2.text_input("Prepared by (optional)", key="rep_author",
                                       placeholder="Name, roll number or course")
            o1, o2 = st.columns(2)
            inc_work = o1.checkbox("Include working", value=True, key="rep_work")
            has_ideal = out["ideal"] is not None
            inc_ideal = o2.checkbox("Include ideal-model comparison", value=has_ideal, disabled=not has_ideal,
                                    key="rep_ideal",
                                    help=None if has_ideal else "Tick the ideal-model option before calculating.")
            try:
                payload = make_report_payload(out, rep_title.strip() or "Equilibrium Report",
                                              rep_author.strip(), inc_work, inc_ideal and has_ideal)
                data = report_tools.build_pdf(payload)
                st.caption(f"Typeface: {report_tools.pdf_font_label()}.")
                try:
                    st.download_button("Download PDF report", data, file_name="equilibrium_report.pdf",
                                       mime="application/pdf", on_click="ignore")
                except TypeError:  # older Streamlit without on_click="ignore"
                    st.download_button("Download PDF report", data, file_name="equilibrium_report.pdf",
                                       mime="application/pdf")
            except ImportError as error:
                st.error(f"Install the missing package to create the PDF: `pip install reportlab` ({error}).")
            except Exception as error:
                st.error(f"The report could not be created: {error}")

# ============================================================
# PARAMETRIC STUDY
# ============================================================

if calc in ("composition", "conversion") and n0.sum() > 0:
    with st.container(key="card_sweep"):
        theme.card_title("", "Parametric study", "Equilibrium against temperature or pressure.")
        var = st.radio("Vary", ["Temperature", "Pressure"], horizontal=True)
        if var == "Temperature":
            s1, s2 = st.columns(2)
            lo = s1.number_input("From (K)", value=max(300.0, T - 200.0), min_value=1.0, key="sw_t_lo")
            hi = s2.number_input("To (K)", value=T + 300.0, min_value=2.0, key="sw_t_hi")
        else:
            s1, s2 = st.columns(2)
            lo = s1.number_input("From (bar)", value=max(0.1, P / 10), min_value=1e-6, format="%.6g", key="sw_p_lo")
            hi = s2.number_input("To (bar)", value=P * 10, min_value=1e-5, format="%.6g", key="sw_p_hi")
        npts = st.slider("Points", 10, 80, 30)
        if st.button("Run study"):
            if var == "Temperature":
                grid = np.linspace(lo, hi, npts)
                runs = problem.sweep(n0, "T", grid, P=P)
            else:
                grid = np.logspace(math.log10(lo), math.log10(hi), npts)
                runs = problem.sweep(n0, "P", grid, T=T)
            st.session_state["eq_sweep"] = dict(var=var, grid=grid, runs=runs, names=names, phases=phases, nu=nu)
        sw = st.session_state.get("eq_sweep")
        if sw:
            frame = {"x": sw["grid"]}
            for i, nm in enumerate(sw["names"]):
                if sw["nu"][i] < 0:
                    frame[f"conversion of {nm} (%)"] = [100 * s["conversion"][i] if s else np.nan for _, s in sw["runs"]]
            conv_df = pd.DataFrame(frame).set_index("x")
            st.markdown(f"**Conversion vs {sw['var'].lower()}** ({'K' if sw['var'] == 'Temperature' else 'bar'})")
            st.line_chart(conv_df)
            frac = {"x": sw["grid"]}
            for i, nm in enumerate(sw["names"]):
                if sw["phases"][i] != "solid":
                    frac[f"{nm} ({sw['phases'][i]})"] = [s["frac"][i] if s else np.nan for _, s in sw["runs"]]
            st.markdown("**Equilibrium mole fractions**")
            st.line_chart(pd.DataFrame(frac).set_index("x"))
