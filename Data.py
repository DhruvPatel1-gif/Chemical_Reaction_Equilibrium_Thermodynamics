# This file stores all the  data.

heat_capacity_data = {
    "gas": {
        # Table C.1: Cp(ideal gas)/R = A + B*T + C*T**2 + D/T**2
        "methane":       {"formula": "CH4",    "Tmax_K": 1500, "Cp298_over_R": 4.217, "A": 1.702, "B": 9.081e-3,  "C": -2.164e-6,  "D": 0.0},
        "ethane":        {"formula": "C2H6",   "Tmax_K": 1500, "Cp298_over_R": 6.369, "A": 1.131, "B": 19.225e-3, "C": -5.561e-6,  "D": 0.0},
        "propane":       {"formula": "C3H8",   "Tmax_K": 1500, "Cp298_over_R": 9.001, "A": 1.213, "B": 28.785e-3, "C": -8.824e-6,  "D": 0.0},
        "n_butane":      {"formula": "C4H10",  "Tmax_K": 1500, "Cp298_over_R": 11.928,"A": 1.935, "B": 36.915e-3, "C": -11.402e-6, "D": 0.0},
        "isobutane":     {"formula": "C4H10",  "Tmax_K": 1500, "Cp298_over_R": 11.901,"A": 1.677, "B": 37.853e-3, "C": -11.945e-6, "D": 0.0},
        "n_pentane":     {"formula": "C5H12",  "Tmax_K": 1500, "Cp298_over_R": 14.731,"A": 2.464, "B": 45.351e-3, "C": -14.111e-6, "D": 0.0},
        "n_hexane":      {"formula": "C6H14",  "Tmax_K": 1500, "Cp298_over_R": 17.550,"A": 3.025, "B": 53.722e-3, "C": -16.791e-6, "D": 0.0},
        "n_heptane":     {"formula": "C7H16",  "Tmax_K": 1500, "Cp298_over_R": 20.361,"A": 3.570, "B": 62.127e-3, "C": -19.486e-6, "D": 0.0},
        "n_octane":      {"formula": "C8H18",  "Tmax_K": 1500, "Cp298_over_R": 23.174,"A": 4.108, "B": 70.567e-3, "C": -22.208e-6, "D": 0.0},

        "ethylene":      {"formula": "C2H4",   "Tmax_K": 1500, "Cp298_over_R": 5.325, "A": 1.424, "B": 14.394e-3, "C": -4.392e-6,  "D": 0.0},
        "propylene":     {"formula": "C3H6",   "Tmax_K": 1500, "Cp298_over_R": 7.792, "A": 1.637, "B": 22.706e-3, "C": -6.915e-6,  "D": 0.0},
        "1_butene":      {"formula": "C4H8",   "Tmax_K": 1500, "Cp298_over_R": 10.520,"A": 1.967, "B": 31.630e-3, "C": -9.873e-6,  "D": 0.0},
        "1_pentene":     {"formula": "C5H10",  "Tmax_K": 1500, "Cp298_over_R": 13.437,"A": 2.691, "B": 39.753e-3, "C": -12.447e-6, "D": 0.0},
        "1_hexene":      {"formula": "C6H12",  "Tmax_K": 1500, "Cp298_over_R": 16.240,"A": 3.220, "B": 48.189e-3, "C": -15.157e-6, "D": 0.0},
        "1_heptene":     {"formula": "C7H14",  "Tmax_K": 1500, "Cp298_over_R": 19.053,"A": 3.768, "B": 56.588e-3, "C": -17.847e-6, "D": 0.0},
        "1_octene":      {"formula": "C8H16",  "Tmax_K": 1500, "Cp298_over_R": 21.868,"A": 4.324, "B": 64.960e-3, "C": -20.521e-6, "D": 0.0},

        "acetaldehyde":  {"formula": "C2H4O",  "Tmax_K": 1000, "Cp298_over_R": 6.506, "A": 1.693, "B": 17.978e-3, "C": -6.158e-6,  "D": 0.0},
        "acetylene":     {"formula": "C2H2",   "Tmax_K": 1500, "Cp298_over_R": 5.253, "A": 6.132, "B": 1.952e-3,  "C": 0.0,        "D": -1.299e5},
        "benzene":       {"formula": "C6H6",   "Tmax_K": 1500, "Cp298_over_R": 10.259,"A": -0.206,"B": 39.064e-3, "C": -13.301e-6, "D": 0.0},
        "1_3_butadiene": {"formula": "C4H6",   "Tmax_K": 1500, "Cp298_over_R": 10.720,"A": 2.734, "B": 26.786e-3, "C": -8.882e-6,  "D": 0.0},
        "cyclohexane":   {"formula": "C6H12",  "Tmax_K": 1500, "Cp298_over_R": 13.121,"A": -3.876,"B": 63.249e-3, "C": -20.928e-6, "D": 0.0},
        "ethanol":       {"formula": "C2H6O",  "Tmax_K": 1500, "Cp298_over_R": 8.948, "A": 3.518, "B": 20.001e-3, "C": -6.002e-6,  "D": 0.0},
        "ethylbenzene":  {"formula": "C8H10",  "Tmax_K": 1500, "Cp298_over_R": 15.993,"A": 1.124, "B": 55.380e-3, "C": -18.476e-6, "D": 0.0},
        "ethylene_oxide":{"formula": "C2H4O",  "Tmax_K": 1000, "Cp298_over_R": 5.784, "A": -0.385,"B": 23.463e-3, "C": -9.296e-6,  "D": 0.0},
        "formaldehyde":  {"formula": "CH2O",   "Tmax_K": 1500, "Cp298_over_R": 4.191, "A": 2.264, "B": 7.022e-3,  "C": -1.877e-6,  "D": 0.0},
        "methanol":      {"formula": "CH4O",   "Tmax_K": 1500, "Cp298_over_R": 5.547, "A": 2.211, "B": 12.216e-3, "C": -3.450e-6,  "D": 0.0},
        "styrene":       {"formula": "C8H8",   "Tmax_K": 1500, "Cp298_over_R": 15.534,"A": 2.050, "B": 50.192e-3, "C": -16.662e-6, "D": 0.0},
        "toluene":       {"formula": "C7H8",   "Tmax_K": 1500, "Cp298_over_R": 12.922,"A": 0.290, "B": 47.052e-3, "C": -15.716e-6, "D": 0.0},

        "air":           {"formula": None,     "Tmax_K": 2000, "Cp298_over_R": 3.509, "A": 3.355, "B": 0.575e-3,  "C": 0.0,        "D": -0.016e5},
        "ammonia":       {"formula": "NH3",    "Tmax_K": 1800, "Cp298_over_R": 4.269, "A": 3.578, "B": 3.020e-3,  "C": 0.0,        "D": -0.186e5},
        "bromine":       {"formula": "Br2",    "Tmax_K": 3000, "Cp298_over_R": 4.337, "A": 4.493, "B": 0.056e-3,  "C": 0.0,        "D": -0.154e5},
        "carbon_monoxide":{"formula": "CO",    "Tmax_K": 2500, "Cp298_over_R": 3.507, "A": 3.376, "B": 0.557e-3,  "C": 0.0,        "D": -0.031e5},
        "carbon_dioxide":{"formula": "CO2",    "Tmax_K": 2000, "Cp298_over_R": 4.467, "A": 5.457, "B": 1.045e-3,  "C": 0.0,        "D": -1.157e5},
        "carbon_disulfide":{"formula": "CS2",  "Tmax_K": 1800, "Cp298_over_R": 5.532, "A": 6.311, "B": 0.805e-3,  "C": 0.0,        "D": -0.906e5},
        "chlorine":      {"formula": "Cl2",    "Tmax_K": 3000, "Cp298_over_R": 4.082, "A": 4.442, "B": 0.089e-3,  "C": 0.0,        "D": -0.344e5},
        "hydrogen":      {"formula": "H2",     "Tmax_K": 3000, "Cp298_over_R": 3.468, "A": 3.249, "B": 0.422e-3,  "C": 0.0,        "D": 0.083e5},
        "hydrogen_sulfide":{"formula": "H2S",  "Tmax_K": 2300, "Cp298_over_R": 4.114, "A": 3.931, "B": 1.490e-3,  "C": 0.0,        "D": -0.232e5},
        "hydrogen_chloride":{"formula": "HCl", "Tmax_K": 2000, "Cp298_over_R": 3.512, "A": 3.156, "B": 0.623e-3,  "C": 0.0,        "D": 0.151e5},
        "hydrogen_cyanide":{"formula": "HCN",  "Tmax_K": 2500, "Cp298_over_R": 4.326, "A": 4.736, "B": 1.359e-3,  "C": 0.0,        "D": -0.725e5},
        "nitrogen":      {"formula": "N2",     "Tmax_K": 2000, "Cp298_over_R": 3.502, "A": 3.280, "B": 0.593e-3,  "C": 0.0,        "D": 0.040e5},
        "nitrous_oxide": {"formula": "N2O",    "Tmax_K": 2000, "Cp298_over_R": 4.646, "A": 5.328, "B": 1.214e-3,  "C": 0.0,        "D": -0.928e5},
        "nitric_oxide":  {"formula": "NO",     "Tmax_K": 2000, "Cp298_over_R": 3.590, "A": 3.387, "B": 0.629e-3,  "C": 0.0,        "D": 0.014e5},
        "nitrogen_dioxide":{"formula": "NO2", "Tmax_K": 2000, "Cp298_over_R": 4.447, "A": 4.982, "B": 1.195e-3,  "C": 0.0,        "D": -0.792e5},
        "dinitrogen_tetroxide":{"formula": "N2O4","Tmax_K": 2000,"Cp298_over_R": 9.198,"A":11.660,"B":2.257e-3,"C":0.0,"D":-2.787e5},
        "oxygen":        {"formula": "O2",     "Tmax_K": 2000, "Cp298_over_R": 3.535, "A": 3.639, "B": 0.506e-3,  "C": 0.0,        "D": -0.227e5},
        "sulfur_dioxide":{"formula": "SO2",    "Tmax_K": 2000, "Cp298_over_R": 4.796, "A": 5.699, "B": 0.801e-3,  "C": 0.0,        "D": -1.015e5},
        "sulfur_trioxide":{"formula": "SO3",   "Tmax_K": 2000, "Cp298_over_R": 6.094, "A": 8.060, "B": 1.056e-3,  "C": 0.0,        "D": -2.028e5},
        "water_vapor":   {"formula": "H2O",    "Tmax_K": 2000, "Cp298_over_R": 4.038, "A": 3.470, "B": 1.450e-3,  "C": 0.0,        "D": 0.121e5},
    },
    
    "liquid": {
        # Table C.3: Cp/R = A + B*T + C*T**2 (273.15–373.15 K)
        "ammonia":             {"Cp298_over_R": 9.718, "A": 22.626, "B": -100.75e-3, "C": 192.71e-6},
        "aniline":             {"Cp298_over_R": 23.070,"A": 15.819, "B": 29.03e-3,   "C": -15.80e-6},
        "benzene":             {"Cp298_over_R": 16.157,"A": -0.747,"B": 67.96e-3,    "C": -37.78e-6},
        "1_3_butadiene":       {"Cp298_over_R": 14.779,"A": 22.711, "B": -87.96e-3,  "C": 205.79e-6},
        "carbon_tetrachloride":{"Cp298_over_R": 15.751,"A": 21.155, "B": -48.28e-3,  "C": 101.14e-6},
        "chlorobenzene":       {"Cp298_over_R": 18.240,"A": 11.278, "B": 32.86e-3,   "C": -31.90e-6},
        "chloroform":          {"Cp298_over_R": 13.806,"A": 19.215, "B": -42.89e-3,  "C": 83.01e-6},
        "cyclohexane":         {"Cp298_over_R": 18.737,"A": -9.048,"B": 141.38e-3,  "C": -161.62e-6},
        "ethanol":             {"Cp298_over_R": 13.444,"A": 33.866, "B": -172.60e-3, "C": 349.17e-6},
        "ethylene_oxide":      {"Cp298_over_R": 10.590,"A": 21.039, "B": -86.41e-3,  "C": 172.28e-6},
        "methanol":            {"Cp298_over_R": 9.798, "A": 13.431, "B": -51.28e-3,  "C": 131.13e-6},
        "n_propanol":          {"Cp298_over_R": 16.921,"A": 41.653, "B": -210.32e-3, "C": 427.20e-6},
        "sulfur_trioxide":     {"Cp298_over_R": 30.408,"A": -2.930,"B": 137.08e-3,  "C": -84.73e-6},
        "toluene":             {"Cp298_over_R": 18.611,"A": 15.133, "B": 6.79e-3,    "C": 16.35e-6},
        "water":               {"Cp298_over_R": 9.069, "A": 8.712,  "B": 1.25e-3,    "C": -0.18e-6},
    },
    "solid": {
"calcium_oxide": {   "formula": "CaO", "Tmax_K": 2000, "Cp298_over_R": 5.058,   "A": 6.104, "B": 0.443e-3, "D": -1.047e5},
 "calcium_carbonate": {  "formula": "CaCO3", "Tmax_K": 1200, "Cp298_over_R": 9.848,  "A": 12.572, "B": 2.637e-3, "D": -3.120e5},
 "calcium_hydroxide": {"formula": "Ca(OH)2", "Tmax_K": 700, "Cp298_over_R": 11.217, "A": 9.597, "B": 5.435e-3, "D": 0.0},
"calcium_carbide": {"formula": "CaC2", "Tmax_K": 720, "Cp298_over_R": 7.508, "A": 8.254, "B": 1.429e-3, "D": -1.042e5 },
"calcium_chloride": {"formula": "CaCl2", "Tmax_K": 1055, "Cp298_over_R": 8.762,  "A": 8.646, "B": 1.530e-3, "D": -0.302e5},
"carbon_graphite": { "formula": "C", "Tmax_K": 2000, "Cp298_over_R": 1.026,  "A": 1.771, "B": 0.771e-3, "D": -0.867e5 },
"copper": {"formula": "Cu", "Tmax_K": 1357, "Cp298_over_R": 2.959, "A": 2.677, "B": 0.815e-3, "D": 0.035e5},
"copper_oxide": {"formula": "CuO", "Tmax_K": 1400, "Cp298_over_R": 5.087, "A": 5.780, "B": 0.973e-3, "D": -0.874e5},
"iron_alpha": {"formula": "Fe", "Tmax_K": 1043, "Cp298_over_R": 3.005,"A": -0.111, "B": 6.111e-3, "D": 1.150e5},
"iron_oxide_hematite": {"formula": "Fe2O3", "Tmax_K": 960, "Cp298_over_R": 12.480,"A": 11.812, "B": 9.697e-3, "D": -1.976e5},
"iron_oxide_magnetite": {"formula": "Fe3O4", "Tmax_K": 850, "Cp298_over_R": 18.138, "A": 9.594, "B": 27.112e-3, "D": 0.409e5},
"iron_sulfide": {"formula": "FeS", "Tmax_K": 411, "Cp298_over_R": 6.573, "A": 2.612, "B": 13.286e-3, "D": 0.0},
"iodine": {"formula": "I2", "Tmax_K": 386.8, "Cp298_over_R": 6.929, "A": 6.481, "B": 1.502e-3, "D": 0.0},
"lithium_chloride": {"formula": "LiCl", "Tmax_K": 800, "Cp298_over_R": 5.778,  "A": 5.257, "B": 2.476e-3, "D": -0.193e5 },
"ammonium_chloride": {"formula": "NH4Cl", "Tmax_K": 458, "Cp298_over_R": 10.741, "A": 5.939, "B": 16.105e-3, "D": 0.0},
 "sodium": {"formula": "Na", "Tmax_K": 371, "Cp298_over_R": 3.386,  "A": 1.988, "B": 4.688e-3, "D": 0.0},
"sodium_chloride": {"formula": "NaCl", "Tmax_K": 1073, "Cp298_over_R": 6.111,  "A": 5.526, "B": 1.963e-3, "D": 0.0},
"sodium_hydroxide": { "formula": "NaOH", "Tmax_K": 566, "Cp298_over_R": 7.177, "A": 0.121, "B": 16.316e-3, "D": 1.948e5},
"sodium_bicarbonate": {"formula": "NaHCO3", "Tmax_K": 400, "Cp298_over_R": 10.539, "A": 5.128, "B": 18.148e-3, "D": 0.0 },
 "sulfur_rhombic": { "formula": "S", "Tmax_K": 368.3, "Cp298_over_R": 3.748,  "A": 4.114, "B": -1.728e-3, "D": -0.783e5},
 "silicon_dioxide_quartz": {"formula": "SiO2", "Tmax_K": 847, "Cp298_over_R": 5.345, "A": 4.871, "B": 5.365e-3, "D": -1.001e5}

}
}

# Smith, Van Ness & Abbott — Appendix C, Table C.4
# Standard enthalpies and Gibbs energies of formation at 298.15 K
# Units: J/mol. None indicates a blank entry in the printed table.
# Separate dictionaries: gas (g), liquid (l), solid (s), aqueous (aq).

formation_properties_298 = {'gas': {
       'methane': {'formula': 'CH4', 'delta_Hf_J_mol': -74520, 'delta_Gf_J_mol': -50460},
       'nitrogen': {'formula': 'N2', 'delta_Hf_J_mol': 0,  'delta_Gf_J_mol': 0},
       'ethane': {'formula': 'C2H6', 'delta_Hf_J_mol': -83820, 'delta_Gf_J_mol': -31855},
       'propane': {'formula': 'C3H8', 'delta_Hf_J_mol': -104680, 'delta_Gf_J_mol': -24290},
       'n_butane': {'formula': 'C4H10', 'delta_Hf_J_mol': -125790, 'delta_Gf_J_mol': -16570},
       'n_pentane': {'formula': 'C5H12', 'delta_Hf_J_mol': -146760, 'delta_Gf_J_mol': -8650},
       'n_hexane': {'formula': 'C6H14', 'delta_Hf_J_mol': -166920, 'delta_Gf_J_mol': 150},
       'n_heptane': {'formula': 'C7H16', 'delta_Hf_J_mol': -187780, 'delta_Gf_J_mol': 8260},
       'n_octane': {'formula': 'C8H18', 'delta_Hf_J_mol': -208750, 'delta_Gf_J_mol': 16260},
       'ethylene': {'formula': 'C2H4', 'delta_Hf_J_mol': 52510, 'delta_Gf_J_mol': 68460},
       'propylene': {'formula': 'C3H6', 'delta_Hf_J_mol': 19710, 'delta_Gf_J_mol': 62205},
       '1_butene': {'formula': 'C4H8', 'delta_Hf_J_mol': -540, 'delta_Gf_J_mol': 70340},
       '1_pentene': {'formula': 'C5H10', 'delta_Hf_J_mol': -21280, 'delta_Gf_J_mol': 78410},
       '1_hexene': {'formula': 'C6H12', 'delta_Hf_J_mol': -41950, 'delta_Gf_J_mol': 86830},
       '1_heptene': {'formula': 'C7H14', 'delta_Hf_J_mol': -62760, 'delta_Gf_J_mol': None},
       'acetaldehyde': {'formula': 'C2H4O', 'delta_Hf_J_mol': -166190, 'delta_Gf_J_mol': -128860},
       'acetylene': {'formula': 'C2H2', 'delta_Hf_J_mol': 227480, 'delta_Gf_J_mol': 209970},
       'benzene': {'formula': 'C6H6', 'delta_Hf_J_mol': 82930, 'delta_Gf_J_mol': 129665},
       '1_3_butadiene': {'formula': 'C4H6', 'delta_Hf_J_mol': 109240, 'delta_Gf_J_mol': 149795},
       'cyclohexane': {'formula': 'C6H12', 'delta_Hf_J_mol': -123140, 'delta_Gf_J_mol': 31920},
       'ethanol': {'formula': 'C2H6O', 'delta_Hf_J_mol': -235100, 'delta_Gf_J_mol': -168490},
       'ethylbenzene': {'formula': 'C8H10', 'delta_Hf_J_mol': 29920, 'delta_Gf_J_mol': 130890},
       'ethylene_oxide': {'formula': 'C2H4O', 'delta_Hf_J_mol': -52630, 'delta_Gf_J_mol': -13010},
       'formaldehyde': {'formula': 'CH2O', 'delta_Hf_J_mol': -108570, 'delta_Gf_J_mol': -102530},
       'methanol': {'formula': 'CH4O', 'delta_Hf_J_mol': -200660, 'delta_Gf_J_mol': -161960},
       'methylcyclohexane': {'formula': 'C7H14', 'delta_Hf_J_mol': -154770, 'delta_Gf_J_mol': 27480},
       'styrene': {'formula': 'C8H8', 'delta_Hf_J_mol': 147360, 'delta_Gf_J_mol': 213900},
       'toluene': {'formula': 'C7H8', 'delta_Hf_J_mol': 50170, 'delta_Gf_J_mol': 122050},
       'ammonia': {'formula': 'NH3', 'delta_Hf_J_mol': -46110, 'delta_Gf_J_mol': -16450},
       'carbon_dioxide': {'formula': 'CO2', 'delta_Hf_J_mol': -393509, 'delta_Gf_J_mol': -394359},
       'carbon_monoxide': {'formula': 'CO', 'delta_Hf_J_mol': -110525, 'delta_Gf_J_mol': -137169},
       'hydrogen_chloride': {'formula': 'HCl', 'delta_Hf_J_mol': -92307, 'delta_Gf_J_mol': -95299},
       'hydrogen_cyanide': {'formula': 'HCN', 'delta_Hf_J_mol': 135100, 'delta_Gf_J_mol': 124700},
       'hydrogen_sulfide': {'formula': 'H2S', 'delta_Hf_J_mol': -20630, 'delta_Gf_J_mol': -33560},
       'hydrogen': {'formula': 'H2', 'delta_Hf_J_mol': 0, 'delta_Gf_J_mol': 0},
       'nitric_oxide': {'formula': 'NO', 'delta_Hf_J_mol': 90250, 'delta_Gf_J_mol': 86550},
       'nitrogen_dioxide': {'formula': 'NO2', 'delta_Hf_J_mol': 33180, 'delta_Gf_J_mol': 51310},
       'nitrous_oxide': {'formula': 'N2O', 'delta_Hf_J_mol': 82050, 'delta_Gf_J_mol': 104200},
       'dinitrogen_tetroxide': {'formula': 'N2O4', 'delta_Hf_J_mol': 9160, 'delta_Gf_J_mol': 97540},
       'sulfur_dioxide': {'formula': 'SO2', 'delta_Hf_J_mol': -296830, 'delta_Gf_J_mol': -300194},
       'water': {'formula': 'H2O', 'delta_Hf_J_mol': -241818, 'delta_Gf_J_mol': -228572}
       },

 'liquid': {
     'acetic_acid': {'formula': 'C2H4O2', 'delta_Hf_J_mol': -484500, 'delta_Gf_J_mol': -389900},
       'benzene': {'formula': 'C6H6', 'delta_Hf_J_mol': 49080, 'delta_Gf_J_mol': 124520},
       'cyclohexane': {'formula': 'C6H12', 'delta_Hf_J_mol': -156230, 'delta_Gf_J_mol': 26850},
       '1_2_ethanediol': {'formula': 'C2H6O2','delta_Hf_J_mol': -454800,'delta_Gf_J_mol': -323080},
       'ethanol': {'formula': 'C2H6O', 'delta_Hf_J_mol': -277690, 'delta_Gf_J_mol': -174780},
       'methanol': {'formula': 'CH4O', 'delta_Hf_J_mol': -238660, 'delta_Gf_J_mol': -166270},
       'methylcyclohexane': {'formula': 'C7H14','delta_Hf_J_mol': -190160,'delta_Gf_J_mol': 20560},
       'toluene': {'formula': 'C7H8', 'delta_Hf_J_mol': 12180, 'delta_Gf_J_mol': 113630},
       'nitric_acid': {'formula': 'HNO3', 'delta_Hf_J_mol': -174100, 'delta_Gf_J_mol': -80710},
       'sulfur_dioxide': {'formula': 'SO2', 'delta_Hf_J_mol': -395720, 'delta_Gf_J_mol': -371060},
       'sulfur_trioxide': {'formula': 'SO3', 'delta_Hf_J_mol': -441040, 'delta_Gf_J_mol': None},
       'sulfuric_acid': {'formula': 'H2SO4', 'delta_Hf_J_mol': -813989, 'delta_Gf_J_mol': -690003},
       'water': {'formula': 'H2O', 'delta_Hf_J_mol': -285830, 'delta_Gf_J_mol': -237129}
       },

 'solid': {'calcium_carbide': {'formula': 'CaC2', 'delta_Hf_J_mol': -59800, 'delta_Gf_J_mol': -64900},
       'calcium_carbonate': {'formula': 'CaCO3', 'delta_Hf_J_mol': -1206920, 'delta_Gf_J_mol': -1128790},
       'calcium_chloride': {'formula': 'CaCl2','delta_Hf_J_mol': -795800,'delta_Gf_J_mol': -748100},
       'calcium_chloride_hexahydrate': {'formula': 'CaCl2.6H2O', 'delta_Hf_J_mol': -2607900, 'delta_Gf_J_mol': None},
       'calcium_hydroxide': {'formula': 'Ca(OH)2', 'delta_Hf_J_mol': -986090, 'delta_Gf_J_mol': -898490},
       'calcium_oxide': {'formula': 'CaO', 'delta_Hf_J_mol': -635090, 'delta_Gf_J_mol': -604030},
       'iron_oxide_feo': {'formula': 'FeO', 'delta_Hf_J_mol': -272000, 'delta_Gf_J_mol': None},
       'iron_oxide_hematite': {'formula': 'Fe2O3', 'delta_Hf_J_mol': -824200, 'delta_Gf_J_mol': -742200},
       'iron_oxide_magnetite': {'formula': 'Fe3O4','delta_Hf_J_mol': -1118400,'delta_Gf_J_mol': -1015400},
       'iron_sulfide_pyrite': {'formula': 'FeS2','delta_Hf_J_mol': -178200,'delta_Gf_J_mol': -166900},
       'lithium_chloride': {'formula': 'LiCl', 'delta_Hf_J_mol': -408610, 'delta_Gf_J_mol': None},
       'lithium_chloride_monohydrate': {'formula': 'LiCl.H2O','delta_Hf_J_mol': -712580,'delta_Gf_J_mol': None},
       'lithium_chloride_dihydrate': {'formula': 'LiCl.2H2O','delta_Hf_J_mol': -1012650,'delta_Gf_J_mol': None},
       'lithium_chloride_trihydrate': {'formula': 'LiCl.3H2O', 'delta_Hf_J_mol': -1311300,'delta_Gf_J_mol': None},
       'sodium_carbonate': {'formula': 'Na2CO3','delta_Hf_J_mol': -1130680,'delta_Gf_J_mol': -1044440},
       'sodium_carbonate_decahydrate': {'formula': 'Na2CO3.10H2O','delta_Hf_J_mol': -4081320,'delta_Gf_J_mol': None},
       'sodium_chloride': {'formula': 'NaCl', 'delta_Hf_J_mol': -411153, 'delta_Gf_J_mol': -384138},
       'sodium_hydroxide': {'formula': 'NaOH', 'delta_Hf_J_mol': -425609, 'delta_Gf_J_mol': -379494}},

 'aq': {
     'ammonia': {'formula': 'NH3', 'delta_Hf_J_mol': None, 'delta_Gf_J_mol': -26500},
        'calcium_chloride': {'formula': 'CaCl2', 'delta_Hf_J_mol': None, 'delta_Gf_J_mol': -810190},
        'calcium_hydroxide': {'formula': 'Ca(OH)2','delta_Hf_J_mol': None,'delta_Gf_J_mol': -868070},
        'nitric_acid': {'formula': 'HNO3', 'delta_Hf_J_mol': None, 'delta_Gf_J_mol': -111250},
        'sodium_chloride': {'formula': 'NaCl', 'delta_Hf_J_mol': None, 'delta_Gf_J_mol': -393133},
        'sodium_hydroxide': {'formula': 'NaOH', 'delta_Hf_J_mol': None, 'delta_Gf_J_mol': -419150},
        'sulfuric_acid': {'formula': 'H2SO4', 'delta_Hf_J_mol': None, 'delta_Gf_J_mol': -744530}
        }
        }


comp = {

    # ==================== GAS PHASE ====================

    'Gas': (

        '1_3_butadiene',
        '1_butene',
        '1_heptene',
        '1_hexene',
        '1_octene',
        '1_pentene',

        'acetaldehyde',
        'acetylene',
        'air',
        'ammonia',
        'benzene',
        'bromine',

        'carbon_dioxide',
        'carbon_disulfide',
        'carbon_monoxide',
        'chlorine',
        'cyclohexane',

        'dinitrogen_tetroxide',

        'ethane',
        'ethanol',
        'ethylbenzene',
        'ethylene',
        'ethylene_oxide',

        'formaldehyde',
        'hydrogen',
        'hydrogen_chloride',
        'hydrogen_cyanide',
        'hydrogen_sulfide',

        'isobutane',

        'methane',
        'methanol',
        'methylcyclohexane',

        'n_butane',
        'n_heptane',
        'n_hexane',
        'n_octane',
        'n_pentane',

        'nitric_oxide',
        'nitrogen',
        'nitrogen_dioxide',
        'nitrous_oxide',

        'oxygen',
        'propane',
        'propylene',

        'styrene',
        'sulfur_dioxide',
        'sulfur_trioxide',

        'toluene',
        'water',
        'water_vapor'
    ),


    # ==================== LIQUID PHASE ====================

    'Liquid': (

        '1_2_ethanediol',
        '1_3_butadiene',

        'acetic_acid',
        'ammonia',
        'aniline',

        'benzene',
        'carbon_tetrachloride',
        'chlorobenzene',
        'chloroform',
        'cyclohexane',

        'ethanol',
        'ethylene_oxide',

        'methanol',
        'methylcyclohexane',

        'n_propanol',
        'nitric_acid',

        'sulfur_dioxide',
        'sulfur_trioxide',
        'sulfuric_acid',

        'toluene',
        'water'
    ),


    # ==================== SOLID PHASE ====================

    'Solid': (

        'ammonium_chloride',

        'calcium_carbide',
        'calcium_carbonate',
        'calcium_chloride',
        'calcium_chloride_hexahydrate',
        'calcium_hydroxide',
        'calcium_oxide',

        'carbon_graphite',
        'copper',
        'copper_oxide',

        'iron_alpha',
        'iron_oxide_feo',
        'iron_oxide_hematite',
        'iron_oxide_magnetite',
        'iron_sulfide',
        'iron_sulfide_pyrite',

        'iodine',

        'lithium_chloride',
        'lithium_chloride_dihydrate',
        'lithium_chloride_monohydrate',
        'lithium_chloride_trihydrate',

        'sodium',
        'sodium_bicarbonate',
        'sodium_carbonate',
        'sodium_carbonate_decahydrate',
        'sodium_chloride',
        'sodium_hydroxide',

        'silicon_dioxide_quartz',
        'sulfur_rhombic'
    ),


    # ==================== AQUEOUS PHASE ====================

    'Aqueous': (

        'ammonia',
        'calcium_chloride',
        'calcium_hydroxide',
        'nitric_acid',
        'sodium_chloride',
        'sodium_hydroxide',
        'sulfuric_acid'
    )

}