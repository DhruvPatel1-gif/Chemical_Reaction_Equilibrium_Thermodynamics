"""
equilibrium_engine.py
=====================
Pure-Python (NumPy/SciPy) engine for single-reaction chemical equilibrium.
No Streamlit code lives here, so it can be tested on its own.

Equilibrium condition (Smith, Van Ness & Abbott, Ch. 13):

    prod_i (a_i)^nu_i = K(T)            with  P0 = 1 bar

    gas     : a_i = phi_i * y_i * P / P0          (phi = fugacity coefficient)
    liquid  : a_i = gamma_i * x_i                 (gamma = activity coefficient)
    solid   : a_i = 1                             (pure solid)

K(T) comes from  ln K = -dG(T)/(R T)  with dG(T) built from the 298.15 K
formation data and the heat-capacity polynomial Cp/R = A + B T + C T^2 + D/T^2.

Material balance (one independent reaction):   n_i = n_i0 + nu_i * eps
"""

from __future__ import annotations

import ast
import math
import re
from functools import lru_cache

import numpy as np
from scipy.optimize import brentq

R = 8.314          # J / (mol K)
T_REF = 298.15     # K
P_REF = 1.0        # bar  (standard-state pressure)


class DataMissing(Exception):
    """Thermodynamic data needed for the calculation is not in Data.py."""


class NoSolution(Exception):
    """No equilibrium state satisfies the requested conditions."""


# ======================================================================
# 1. DATABASE LOOKUP  (works with the structure of Data.py)
# ======================================================================

# Elements in their reference state: dHf = dGf = 0 (used only when the
# species is absent from the formation table).
ELEMENT_REFERENCE = {
    ("gas", "oxygen"), ("gas", "nitrogen"), ("gas", "hydrogen"),
    ("gas", "chlorine"),
    ("solid", "sulfur_rhombic"), ("solid", "carbon_graphite"),
    ("solid", "copper"), ("solid", "iron_alpha"),
    ("solid", "iodine"), ("solid", "sodium"),
}

_ALIASES = {
    "water": ["water_vapor"],
    "water_vapor": ["water"],
    "1_3_butadiene": ["1,3-butadiene"],
    "1,3-butadiene": ["1_3_butadiene"],
}


def find_key(database: dict, phase: str, name: str):
    """Return the key under which `name` is stored, or None."""
    table = database.get(phase, {})
    candidates = [name, name.replace("_", "-"), name.replace("-", "_")]
    candidates += _ALIASES.get(name, [])
    for c in candidates:
        if c in table:
            return c
    return None


def _formation_phase_key(phase: str) -> str:
    return "aq" if phase == "aqueous" else phase


def standard_reaction_properties(reaction, formation_db, cp_db,
                                 ignore_missing_cp=False):
    """
    Sum the standard properties over the reaction (nu_i weighted).

    Returns a dict with dH298, dG298 (J/mol), dA..dD (heat-capacity
    coefficients of Cp/R), `tmax` {species: Tmax_K} and `notes`.
    Raises DataMissing with a readable list of what is absent.
    """
    out = dict(dH298=0.0, dG298=0.0, dA=0.0, dB=0.0, dC=0.0, dD=0.0,
               tmax={}, notes=[])
    missing = []
    for sp in reaction:
        nu = float(sp["coefficient"])
        if nu == 0:
            continue                       # inert: drops out of every delta
        phase = sp["phase"].lower()
        name = sp["component"]

        # --- formation properties ------------------------------------
        key = find_key(formation_db, _formation_phase_key(phase), name)
        hf = gf = None
        if key is not None:
            entry = formation_db[_formation_phase_key(phase)][key]
            hf, gf = entry.get("delta_Hf_J_mol"), entry.get("delta_Gf_J_mol")
        if (hf is None or gf is None) and (phase, name) in ELEMENT_REFERENCE:
            hf, gf = 0.0, 0.0
            out["notes"].append(f"{name} ({phase}) is an element in its "
                                f"reference state: dHf = dGf = 0.")
        if hf is None or gf is None:
            missing.append(f"formation H/G of {name} ({phase})")
            continue
        out["dH298"] += nu * hf
        out["dG298"] += nu * gf

        # --- heat capacity -------------------------------------------
        ckey = find_key(cp_db, phase, name)
        if ckey is None:
            if not ignore_missing_cp:
                missing.append(f"heat-capacity data of {name} ({phase})")
            else:
                out["notes"].append(f"No Cp data for {name}: its Cp was "
                                    f"taken as zero.")
            continue
        cp = cp_db[phase][ckey]
        out["dA"] += nu * cp.get("A", 0.0)
        out["dB"] += nu * cp.get("B", 0.0)
        out["dC"] += nu * cp.get("C", 0.0)
        out["dD"] += nu * cp.get("D", 0.0)
        if cp.get("Tmax_K"):
            out["tmax"][f"{name} ({phase})"] = cp["Tmax_K"]
    if missing:
        raise DataMissing("; ".join(missing))
    return out


def make_lnK(dH298, dG298, dA=0.0, dB=0.0, dC=0.0, dD=0.0):
    """ln K(T) from dH298, dG298 and the dCp/R polynomial (SVNA Eq. 13.18)."""
    dS298 = (dH298 - dG298) / T_REF

    def lnK(T):
        if T <= 0:
            raise ValueError("Temperature must be positive.")
        heat = R * (dA * (T - T_REF)
                    + dB / 2.0 * (T**2 - T_REF**2)
                    + dC / 3.0 * (T**3 - T_REF**3)
                    - dD * (1.0 / T - 1.0 / T_REF))
        ent = R * (dA * math.log(T / T_REF)
                   + dB * (T - T_REF)
                   + dC / 2.0 * (T**2 - T_REF**2)
                   - dD / 2.0 * (1.0 / T**2 - 1.0 / T_REF**2))
        dG = (dH298 + heat) - T * (dS298 + ent)
        return -dG / (R * T)

    lnK.parts = lambda T: _k_parts(dH298, dG298, dA, dB, dC, dD, T)
    return lnK


def _k_parts(dH298, dG298, dA, dB, dC, dD, T):
    dS298 = (dH298 - dG298) / T_REF
    heat = R * (dA * (T - T_REF) + dB / 2.0 * (T**2 - T_REF**2)
                + dC / 3.0 * (T**3 - T_REF**3)
                - dD * (1.0 / T - 1.0 / T_REF))
    ent = R * (dA * math.log(T / T_REF) + dB * (T - T_REF)
               + dC / 2.0 * (T**2 - T_REF**2)
               - dD / 2.0 * (1.0 / T**2 - 1.0 / T_REF**2))
    dH = dH298 + heat
    dS = dS298 + ent
    return dict(dH_T=dH, dS_T=dS, dG_T=dH - T * dS)


def make_constant_lnK(K):
    if K <= 0:
        raise ValueError("K must be positive.")
    value = math.log(K)
    f = lambda T: value
    f.parts = lambda T: dict(dH_T=float("nan"), dS_T=float("nan"),
                             dG_T=-R * T * value)
    return f


# ======================================================================
# 2. CRITICAL PROPERTIES (for real-gas models)
# ======================================================================

def _name_candidates(name: str):
    c = [name.replace("_", " ")]
    dashed = re.sub(r"(?<=\d)_(?=\d)", ",", name)
    dashed = dashed.replace("_", "-")
    c += [dashed, name]
    if name.startswith(("n_", "iso")):
        c.append(name.replace("_", "-"))
    return list(dict.fromkeys(c))


_CRIT_CACHE = {}          # only successful look-ups are cached, so a failure is retried on the next run


def _critical_via_chemical(ident):
    from thermo import Chemical
    ch = Chemical(ident)
    return {"Tc": ch.Tc, "Pc": ch.Pc, "omega": ch.omega, "Zc": ch.Zc, "Vc": ch.Vc}


def _critical_via_chemicals(ident):
    """Same data set, read directly by CAS number (lighter than building a full Chemical object)."""
    from chemicals.identifiers import CAS_from_any
    from chemicals.critical import Tc, Pc, Vc, Zc
    from chemicals.acentric import omega
    cas = CAS_from_any(ident)
    return {"Tc": Tc(cas), "Pc": Pc(cas), "omega": omega(cas), "Zc": Zc(cas), "Vc": Vc(cas)}


def critical_diagnostics(name: str, formula: str | None = None):
    """Try every identifier and route and report what happened (used by the 'why?' panel in the app)."""
    info = {"thermo_version": None, "import_error": None, "attempts": []}
    try:
        import thermo
        info["thermo_version"] = getattr(thermo, "__version__", "unknown")
        from thermo import Chemical  # noqa: F401
    except Exception as error:
        info["import_error"] = f"{type(error).__name__}: {error}"
        return info
    identifiers = _name_candidates(name)
    if formula:
        identifiers.append(formula)
    for ident in dict.fromkeys(identifiers):
        for route, fn in (("thermo.Chemical", _critical_via_chemical),
                          ("chemicals (by CAS)", _critical_via_chemicals)):
            try:
                v = fn(ident)
                got = {k: x for k, x in v.items() if x is not None}
                info["attempts"].append((ident, route, "found " + ", ".join(got) if got else "no values"))
            except Exception as error:
                info["attempts"].append((ident, route, f"{type(error).__name__}: {str(error)[:120]}"))
    return info


def critical_properties(name: str, formula: str | None = None):
    """Tc [K], Pc [Pa], omega, Zc, Vc [m3/mol] from the `thermo` library (and its `chemicals` data package).

    Only library values are returned; missing properties are never estimated.
    """
    key = (name, formula)
    if key in _CRIT_CACHE:
        return _CRIT_CACHE[key]
    identifiers = _name_candidates(name)
    if formula:
        identifiers.append(formula)

    for ident in dict.fromkeys(identifiers):
        for fn in (_critical_via_chemical, _critical_via_chemicals):
            try:
                values = fn(ident)
            except Exception:
                continue
            if values["Tc"] is not None and values["Pc"] is not None:
                result = {k: (float(v) if v is not None else None) for k, v in values.items()}
                _CRIT_CACHE[key] = result
                return result
    return None


def chemical_cas(name: str, formula: str | None = None):
    """Return a CAS number using thermo.Chemical; None if not recognized."""
    try:
        from thermo import Chemical
    except Exception:
        return None
    identifiers = _name_candidates(name)
    if formula:
        identifiers.append(formula)
    for ident in dict.fromkeys(identifiers):
        try:
            cas = Chemical(ident).CAS
            if cas:
                return str(cas)
        except Exception:
            continue
    return None


def liquid_interaction_parameters(kind: str, components, formulas=None):
    """Retrieve ChemSep Wilson/NRTL parameters from thermo.IPDB.

    Returns (matrices, report). Missing pairs are NaN (never silently zero).
    Wilson matrices contain aij and bij for ln(Lambda_ij)=aij+bij/T.
    NRTL matrices contain aij, bij and alphaij for tau=aij+bij/T.
    """
    if kind not in ("wilson", "nrtl"):
        raise ValueError("Only Wilson and NRTL parameters are available here.")
    from thermo.interaction_parameters import IPDB

    formulas = formulas or [None] * len(components)
    cas_numbers = [chemical_cas(name, formula) for name, formula in zip(components, formulas)]
    m = len(components)
    keys = ("aij", "bij") if kind == "wilson" else ("aij", "bij", "alphaij")
    matrices = {key: np.full((m, m), np.nan, dtype=float) for key in keys}
    for key in keys:
        np.fill_diagonal(matrices[key], 0.0)

    table_name = "ChemSep Wilson" if kind == "wilson" else "ChemSep NRTL"
    metadata = IPDB.metadata.get(table_name, {})
    available = {key.lower() for key in metadata.get("necessary keys", [])}
    if not available:
        # Fall back to the keys actually stored in the loaded ChemSep table.
        for entry in IPDB.tables.get(table_name, {}).values():
            available.update(str(key).lower() for key in entry.keys())
    candidate_keys = [key for key in keys if key in available]
    # ChemSep's NRTL table commonly stores the energy term as bij/T, with no
    # constant aij term. In that representation aij is exactly zero.
    if kind == "nrtl" and "aij" not in available:
        matrices["aij"][:] = 0.0
    pair_status = {}
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            pair = f"{components[i]} → {components[j]}"
            if not cas_numbers[i] or not cas_numbers[j]:
                pair_status[pair] = "CAS number unavailable from thermo.Chemical"
                continue
            found = []
            for key in candidate_keys:
                try:
                    if IPDB.has_ip_specific(table_name, [cas_numbers[i], cas_numbers[j]], key):
                        value = IPDB.get_ip_specific(table_name, [cas_numbers[i], cas_numbers[j]], key)
                        if value is not None and np.isfinite(float(value)):
                            matrices[key][i, j] = float(value)
                            found.append(key)
                except Exception:
                    continue
            pair_status[pair] = "Retrieved: " + ", ".join(found) if found else "Not present in Thermo ChemSep database"
    return matrices, {"table": table_name, "cas": cas_numbers, "pairs": pair_status, "keys": keys}


# ======================================================================
# 3. GAS-PHASE FUGACITY COEFFICIENTS
# ======================================================================

GAS_EOS = ("ideal", "pr", "srk", "virial")


class GasModel:
    """
    eos            : 'ideal' | 'pr' | 'srk' | 'virial' (Pitzer-Abbott B0,B1)
    ideal_solution : True -> Lewis/Randall rule, phi_hat_i = phi_i(pure, T, P)
    props          : dict of arrays Tc, Pc, omega, Zc, Vc (gas-species order)
    kij            : binary interaction matrix (default 0)
    """

    def __init__(self, eos="ideal", ideal_solution=False, props=None, kij=None):
        if eos not in GAS_EOS:
            raise ValueError(f"Unknown gas model {eos}")
        self.eos = eos
        self.ideal_solution = ideal_solution
        self.props = props
        self.kij = kij

    # -- helpers -------------------------------------------------------
    def _p(self, key, idx):
        return np.asarray(self.props[key], dtype=float)[idx]

    def _kij(self, idx):
        if self.kij is None:
            return np.zeros((len(idx), len(idx)))
        return np.asarray(self.kij, dtype=float)[np.ix_(idx, idx)]

    def _cubic(self, T, P_pa, y, idx):
        Tc, Pc, w = self._p("Tc", idx), self._p("Pc", idx), self._p("omega", idx)
        if self.eos == "pr":
            kappa = 0.37464 + 1.54226 * w - 0.26992 * w**2
            a_c = 0.45724 * R**2 * Tc**2 / Pc
            b = 0.07780 * R * Tc / Pc
        else:
            kappa = 0.480 + 1.574 * w - 0.176 * w**2
            a_c = 0.42748 * R**2 * Tc**2 / Pc
            b = 0.08664 * R * Tc / Pc
        ai = a_c * (1.0 + kappa * (1.0 - np.sqrt(T / Tc)))**2
        aij = np.sqrt(np.outer(ai, ai)) * (1.0 - self._kij(idx))
        a_mix = float(y @ aij @ y)
        b_mix = float(y @ b)
        A = a_mix * P_pa / (R * T)**2
        B = b_mix * P_pa / (R * T)
        if self.eos == "pr":
            coeffs = [1.0, -(1.0 - B), A - 3.0 * B**2 - 2.0 * B,
                      -(A * B - B**2 - B**3)]
        else:
            coeffs = [1.0, -1.0, A - B - B**2, -A * B]
        roots = np.roots(coeffs)
        real = roots[np.abs(roots.imag) < 1e-9].real
        real = real[real > B]
        if real.size == 0:
            raise ValueError("Cubic EOS has no physical vapour root.")
        Z = float(real.max())
        s = aij @ y
        term = 2.0 * s / a_mix - b / b_mix
        if self.eos == "pr":
            r2 = math.sqrt(2.0)
            return ((b / b_mix) * (Z - 1.0) - math.log(Z - B)
                    - A / (2.0 * r2 * B) * term
                    * math.log((Z + (1.0 + r2) * B) / (Z + (1.0 - r2) * B)))
        return ((b / b_mix) * (Z - 1.0) - math.log(Z - B)
                - A / B * term * math.log(1.0 + B / Z))

    def _virial(self, T, P_pa, y, idx):
        Tc, Pc, w = self._p("Tc", idx), self._p("Pc", idx), self._p("omega", idx)
        Zc, Vc = self._p("Zc", idx), self._p("Vc", idx)
        Tcij = np.sqrt(np.outer(Tc, Tc)) * (1.0 - self._kij(idx))
        wij = (w[:, None] + w[None, :]) / 2.0
        Zcij = (Zc[:, None] + Zc[None, :]) / 2.0
        Vc3 = Vc ** (1.0 / 3.0)
        Vcij = ((Vc3[:, None] + Vc3[None, :]) / 2.0) ** 3
        Pcij = Zcij * R * Tcij / Vcij
        Tr = T / Tcij
        B0 = 0.083 - 0.422 / Tr**1.6
        B1 = 0.139 - 0.172 / Tr**4.2
        Bij = R * Tcij / Pcij * (B0 + wij * B1)
        d = 2.0 * Bij - np.diag(Bij)[:, None] - np.diag(Bij)[None, :]
        return P_pa / (R * T) * (np.diag(Bij) + d @ y - 0.5 * float(y @ d @ y))

    def _mixture(self, T, P_pa, y, idx):
        if self.eos == "virial":
            return self._virial(T, P_pa, y, idx)
        return self._cubic(T, P_pa, y, idx)

    # -- public --------------------------------------------------------
    def ln_phi(self, T, P_bar, y):
        y = np.asarray(y, dtype=float)
        n = len(y)
        if self.eos == "ideal":
            return np.zeros(n)
        P_pa = P_bar * 1e5
        idx = np.arange(n)
        if self.ideal_solution:                       # Lewis / Randall rule
            out = np.zeros(n)
            for i in range(n):
                out[i] = self._mixture(T, P_pa, np.array([1.0]), np.array([i]))[0]
            return out
        return np.asarray(self._mixture(T, P_pa, y, idx), dtype=float)


# ======================================================================
# 4. LIQUID-PHASE ACTIVITY COEFFICIENTS
# ======================================================================

LIQUID_MODELS = ("ideal", "margules", "van_laar", "wilson", "nrtl", "custom")

_SAFE_FUNCS = {"exp": np.exp, "log": np.log, "ln": np.log, "sqrt": np.sqrt,
               "log10": np.log10, "abs": abs}


def compile_ge_expression(expr: str, var_names):
    """
    Turn a user string such as '0.1*x1*x2' into f(x_array, T) -> G^E/RT.
    Only arithmetic, numbers, the variables and a few math functions are
    permitted (checked on the syntax tree before anything is evaluated).
    `var_names` is a dict {symbol: index into x} (several symbols may point to
    the same species) or a plain list of symbols (index = position).
    """
    if not isinstance(var_names, dict):
        var_names = {name: k for k, name in enumerate(var_names)}
    text = expr.strip().replace("^", "**")
    if not text:
        raise ValueError("Enter an expression for G^E/RT.")
    tree = ast.parse(text, mode="eval")
    allowed = set(var_names) | set(_SAFE_FUNCS) | {"T", "R", "pi"}
    ok_nodes = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Load, ast.Add,
                ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd)
    for node in ast.walk(tree):
        if isinstance(node, ok_nodes):
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            continue
        if isinstance(node, ast.Name):
            if node.id not in allowed:
                raise ValueError(f"Unknown symbol '{node.id}' in expression.")
            continue
        if isinstance(node, ast.Call):
            if (isinstance(node.func, ast.Name) and node.func.id in _SAFE_FUNCS
                    and not node.keywords):
                continue
        raise ValueError("Unsupported syntax in G^E/RT expression.")
    code = compile(tree, "<ge_over_RT>", "eval")

    def f(x, T):
        env = dict(_SAFE_FUNCS)
        env.update({"T": T, "R": R, "pi": math.pi})
        env.update({name: x[k] for name, k in var_names.items()})
        return float(eval(code, {"__builtins__": {}}, env))   # noqa: S307
    return f


class LiquidModel:
    """
    kind   : ideal | margules | van_laar | wilson | nrtl | custom
    params : model dependent (all matrices follow the liquid-species order)
        margules : {"A": m x m symmetric}          GE/RT = sum_{i<j} A_ij x_i x_j
        van_laar : {"A12":..., "A21":...}           (binary)
        wilson   : {"mode":"direct","Lam": m x m}, {"mode":"dlambda",...}, or
                   {"mode":"thermo","a":m x m,"b":m x m} with ln(Lambda)=a+b/T
        nrtl     : {"a": m x m, "b": m x m [K], "alpha": m x m}  tau = a + b/T
        custom   : {"expr": "0.1*x1*x2", "vars": {"x1": 0, "x2": 1}}
    """

    def __init__(self, kind="ideal", params=None):
        if kind not in LIQUID_MODELS:
            raise ValueError(f"Unknown liquid model {kind}")
        self.kind = kind
        self.params = params or {}
        self._ge = None
        if kind == "custom":
            self._ge = compile_ge_expression(self.params["expr"],
                                             self.params["vars"])

    def ln_gamma(self, T, x):
        x = np.asarray(x, dtype=float)
        m = len(x)
        k = self.kind
        if k == "ideal" or m == 1:
            return np.zeros(m)
        p = self.params

        if k == "margules":
            A = np.asarray(p["A"], dtype=float)
            return A @ x - 0.5 * float(x @ A @ x)

        if k == "van_laar":
            if m != 2:
                raise ValueError("Van Laar is implemented for binary mixtures.")
            A12, A21 = p["A12"], p["A21"]
            den = A12 * x[0] + A21 * x[1]
            if den == 0:
                return np.zeros(2)
            return np.array([A12 * (A21 * x[1] / den) ** 2,
                             A21 * (A12 * x[0] / den) ** 2])

        if k == "wilson":
            mode = p.get("mode", "direct")
            if mode == "direct":
                Lam = np.asarray(p["Lam"], dtype=float)
            elif mode == "thermo":
                a = np.asarray(p["a"], dtype=float)
                b = np.asarray(p["b"], dtype=float)
                Lam = np.exp(a + b / T)
            else:
                V = np.asarray(p["V"], dtype=float)
                dlam = np.asarray(p["dlam"], dtype=float)
                Lam = V[None, :] / V[:, None] * np.exp(-dlam / (R * T))
            np.fill_diagonal(Lam, 1.0)
            S = Lam @ x                        # S_i = sum_j x_j Lam_ij
            return 1.0 - np.log(S) - Lam.T @ (x / S)

        if k == "nrtl":
            tau = np.asarray(p["a"], dtype=float) + np.asarray(p["b"], dtype=float) / T
            np.fill_diagonal(tau, 0.0)
            alpha = np.asarray(p["alpha"], dtype=float)
            G = np.exp(-alpha * tau)
            np.fill_diagonal(G, 1.0)
            S = G.T @ x                        # S_j = sum_k x_k G_kj
            C = (tau * G).T @ x                # C_j = sum_m x_m tau_mj G_mj
            term1 = C / S                      # sum_j x_j tau_ji G_ji / S_i
            term2 = (G * (tau - (C / S)[None, :])) @ (x / S)
            return term1 + term2

        if k == "custom":                     # G^E/RT -> ln(gamma_i) numerically
            out = np.zeros(m)
            for i in range(m):
                h = min(1e-6, 0.5 * x[i]) if x[i] > 0 else 1e-9
                xp, xm = x.copy(), x.copy()
                xp[i] += h
                xm[i] -= h
                fp = xp.sum() * self._ge(xp / xp.sum(), T)
                fm = xm.sum() * self._ge(xm / xm.sum(), T)
                out[i] = (fp - fm) / (2.0 * h)
            return out

        raise ValueError(k)


# ======================================================================
# 5. ROOT-FINDING UTILITY
# ======================================================================

def scan_roots(f, xs, xtol=1e-14, rtol=1e-12):
    """Locate every sign change of f on the grid xs and refine with Brent."""
    vals = []
    for x in xs:
        try:
            v = f(x)
        except Exception:
            v = np.nan
        vals.append(v if np.isfinite(v) else np.nan)
    roots, stable = [], []
    for i in range(len(xs) - 1):
        a, b = vals[i], vals[i + 1]
        if not (np.isfinite(a) and np.isfinite(b)):
            continue
        if a == 0:
            roots.append(float(xs[i])); stable.append(b > 0); continue
        if a * b < 0:
            try:
                r = brentq(f, xs[i], xs[i + 1], xtol=xtol, rtol=rtol, maxiter=300)
            except Exception:
                continue
            roots.append(float(r)); stable.append(a < 0)
    # drop duplicates
    uniq, ustable = [], []
    for r, s in zip(roots, stable):
        if not any(math.isclose(r, u, rel_tol=1e-9, abs_tol=1e-12) for u in uniq):
            uniq.append(r); ustable.append(s)
    return uniq, ustable, np.array(vals)


# ======================================================================
# 6. THE EQUILIBRIUM PROBLEM
# ======================================================================

class EquilibriumProblem:
    """One reaction, any mix of gas / liquid / pure-solid species and inerts."""

    def __init__(self, reaction, lnK_fn, gas_model=None, liquid_model=None):
        self.reaction = reaction
        self.names = [r["component"] for r in reaction]
        self.phases = [r["phase"].lower() for r in reaction]
        self.nu = np.array([float(r["coefficient"]) for r in reaction])
        if any(p not in ("gas", "liquid", "solid") for p in self.phases):
            raise NotImplementedError(
                "Aqueous species are not supported yet (gas, liquid and pure "
                "solid phases only).")
        self.gas_idx = np.array([i for i, p in enumerate(self.phases) if p == "gas"], dtype=int)
        self.liq_idx = np.array([i for i, p in enumerate(self.phases) if p == "liquid"], dtype=int)
        self.sol_idx = np.array([i for i, p in enumerate(self.phases) if p == "solid"], dtype=int)
        self.lnK_fn = lnK_fn
        self.gas_model = gas_model or GasModel("ideal")
        self.liq_model = liquid_model or LiquidModel("ideal")
        if not np.any(self.nu < 0) or not np.any(self.nu > 0):
            raise ValueError("The reaction needs at least one reactant and one product.")

    # -- activities ----------------------------------------------------
    def activities(self, n, T, P):
        """Return (ln a, ln phi, ln gamma, phase mole fraction) or None."""
        N = len(n)
        lna = np.zeros(N)
        lnphi = np.full(N, np.nan)
        lngam = np.full(N, np.nan)
        frac = np.full(N, np.nan)
        active = self.nu != 0
        if self.gas_idx.size:
            ng = n[self.gas_idx]
            tot = ng.sum()
            if tot <= 0:
                return None
            y = ng / tot
            if np.any((y <= 0) & active[self.gas_idx]):
                return None
            lp = self.gas_model.ln_phi(T, P, y)
            lna[self.gas_idx] = np.log(np.where(y > 0, y, 1.0)) + lp + math.log(P / P_REF)
            lnphi[self.gas_idx] = lp
            frac[self.gas_idx] = y
        if self.liq_idx.size:
            nl = n[self.liq_idx]
            tot = nl.sum()
            if tot <= 0:
                return None
            x = nl / tot
            if np.any((x <= 0) & active[self.liq_idx]):
                return None
            lg = self.liq_model.ln_gamma(T, x)
            lna[self.liq_idx] = np.log(np.where(x > 0, x, 1.0)) + lg
            lngam[self.liq_idx] = lg
            frac[self.liq_idx] = x
        lna[~active] = 0.0
        return lna, lnphi, lngam, frac

    def ln_Q(self, n, T, P):
        act = self.activities(n, T, P)
        if act is None:
            return np.nan
        return float(self.nu @ act[0])

    # -- extent of reaction -------------------------------------------
    def extent_bounds(self, n0):
        lo, hi = -np.inf, np.inf
        for i, nu in enumerate(self.nu):
            if nu > 0:
                lo = max(lo, -n0[i] / nu)
            elif nu < 0:
                hi = min(hi, -n0[i] / nu)
        return lo, hi

    def _residual(self, eps, n0, T, P, lnK):
        n = n0 + self.nu * eps
        if np.any(n < -1e-12):
            return np.nan
        return self.ln_Q(np.maximum(n, 0.0), T, P) - lnK

    def solve_extent(self, n0, T, P):
        """Return (eps, all_roots, lnK) for fixed T, P and feed."""
        n0 = np.asarray(n0, dtype=float)
        lnK = self.lnK_fn(T)
        lo, hi = self.extent_bounds(n0)
        if not (np.isfinite(lo) and np.isfinite(hi)) or lo >= hi:
            raise NoSolution("The feed gives no finite, non-empty range for the "
                             "extent of reaction. Check that every reactant "
                             "present can be consumed and products can be formed.")
        t = np.concatenate([np.linspace(0, 1, 301),
                            10 ** np.linspace(-13, -2, 45),
                            1 - 10 ** np.linspace(-13, -2, 45)])
        t = np.unique(t[(t > 0) & (t < 1)])
        xs = lo + (hi - lo) * t
        roots, stable, vals = scan_roots(lambda e: self._residual(e, n0, T, P, lnK), xs)
        if not roots:
            finite = vals[np.isfinite(vals)]
            if finite.size == 0:
                raise NoSolution("The equilibrium expression could not be evaluated "
                                 "(check the feed and the property models).")
            if np.all(finite < 0):
                raise NoSolution("Q < K over the whole feasible range: the forward "
                                 "reaction runs until a reactant is used up "
                                 "(essentially complete conversion).")
            if np.all(finite > 0):
                raise NoSolution("Q > K over the whole feasible range: the reaction "
                                 "essentially does not proceed forward (the reverse "
                                 "reaction dominates).")
            raise NoSolution("No equilibrium root found in the feasible range.")
        pool = [r for r, s in zip(roots, stable) if s] or roots
        return pool[0], roots, lnK

    # -- full state ----------------------------------------------------
    def state(self, n0, T, P, eps=None):
        n0 = np.asarray(n0, dtype=float)
        roots = None
        if eps is None:
            eps, roots, lnK = self.solve_extent(n0, T, P)
        else:
            lnK = self.lnK_fn(T)
            roots = [eps]
        n = np.maximum(n0 + self.nu * eps, 0.0)
        act = self.activities(n, T, P)
        if act is None:
            raise NoSolution("The equilibrium state could not be evaluated.")
        lna, lnphi, lngam, frac = act
        conv = np.full(len(n), np.nan)
        for i in range(len(n)):
            if self.nu[i] < 0 and n0[i] > 0:
                conv[i] = -self.nu[i] * eps / n0[i]
        return dict(T=T, P=P, eps=eps, roots=roots, lnK=lnK, K=math.exp(max(min(lnK, 700), -700)),
                    n0=n0, n=n, lna=lna, lnphi=lnphi, lngam=lngam, frac=frac,
                    conversion=conv)

    # -- specification  ->  extent (closed form) ------------------------
    def eps_from_spec(self, n0, spec):
        """
        spec = {"type": "mole_fraction", "index": i, "value": y}   (phase mole fraction)
             | {"type": "conversion",    "index": i, "value": X}   (fraction 0-1)
        With the feed known, both give eps directly (linear equation).
        """
        i, v = spec["index"], float(spec["value"])
        if spec["type"] == "conversion":
            if self.nu[i] >= 0:
                raise ValueError("Conversion can only be specified for a reactant.")
            if n0[i] <= 0:
                raise ValueError("The chosen reactant is absent from the feed.")
            return v * n0[i] / (-self.nu[i])
        if self.phases[i] == "gas":
            idx = self.gas_idx
        elif self.phases[i] == "liquid":
            idx = self.liq_idx
        else:
            raise ValueError("Mole fraction is undefined for a pure solid.")
        S0 = n0[idx].sum()
        dnu = self.nu[idx].sum()
        den = self.nu[i] - v * dnu
        if abs(den) < 1e-14:
            raise NoSolution("The specified mole fraction cannot be reached by "
                             "this reaction (denominator is zero).")
        return (v * S0 - n0[i]) / den

    def _feasible(self, n0, eps):
        lo, hi = self.extent_bounds(n0)
        tol = 1e-9 * max(1.0, abs(eps))
        return lo - tol <= eps <= hi + tol

    # -- solve for T ---------------------------------------------------
    def solve_temperature(self, n0, P, spec, Tmin, Tmax, npts=240):
        n0 = np.asarray(n0, dtype=float)
        eps = self.eps_from_spec(n0, spec)
        if not self._feasible(n0, eps):
            raise NoSolution("With this feed the specification is impossible: it would "
                             "need a negative amount of some species (for example "
                             "more of another reactant than you fed).")
        n = np.maximum(n0 + self.nu * eps, 0.0)
        f = lambda T: self.ln_Q(n, T, P) - self.lnK_fn(T)
        roots, _, _ = scan_roots(f, np.linspace(Tmin, Tmax, npts), xtol=1e-9)
        if not roots:
            raise NoSolution(f"No temperature between {Tmin:g} K and {Tmax:g} K "
                             f"satisfies the specification. Widen the range or "
                             f"check the target.")
        return [(T, self.state(n0, T, P, eps=eps)) for T in roots]

    # -- solve for P ---------------------------------------------------
    def solve_pressure(self, n0, T, spec, Pmin, Pmax, npts=300):
        n0 = np.asarray(n0, dtype=float)
        eps = self.eps_from_spec(n0, spec)
        if not self._feasible(n0, eps):
            raise NoSolution("With this feed the specification is impossible: it would "
                             "need a negative amount of some species (for example "
                             "more of another reactant than you fed).")
        n = np.maximum(n0 + self.nu * eps, 0.0)
        lnK = self.lnK_fn(T)
        f = lambda P: self.ln_Q(n, T, P) - lnK
        grid = np.logspace(math.log10(Pmin), math.log10(Pmax), npts)
        roots, _, _ = scan_roots(f, grid, xtol=1e-12)
        if not roots:
            if self.nu[self.gas_idx].sum() == 0 if self.gas_idx.size else True:
                raise NoSolution("Pressure does not influence this equilibrium "
                                 "(no change in moles of gas and ideal behaviour).")
            raise NoSolution(f"No pressure between {Pmin:g} and {Pmax:g} bar "
                             f"satisfies the specification.")
        return [(P, self.state(n0, T, P, eps=eps)) for P in roots]

    # -- solve for an unknown feed amount ------------------------------
    def solve_feed(self, n0_base, j, T, P, spec, xmax=None, npts=400):
        """
        The amount of species j in the feed is unknown (other amounts fixed
        in n0_base).  Returns a list of (x_j, state).
        """
        n0_base = np.asarray(n0_base, dtype=float).copy()
        n0_base[j] = 0.0
        scale = max(n0_base.sum(), 1.0)
        top = xmax if xmax else 1e4 * scale

        def n0_of(x):
            n0 = n0_base.copy()
            n0[j] = x
            return n0

        def f(x):
            n0 = n0_of(x)
            eps = self.eps_from_spec(n0, spec)
            if not self._feasible(n0, eps):
                return np.nan
            n = np.maximum(n0 + self.nu * eps, 0.0)
            return self.ln_Q(n, T, P) - self.lnK_fn(T)

        grid = np.unique(np.concatenate([[0.0], np.logspace(-8, math.log10(top), npts) * (1 if xmax else scale)]))
        roots, _, _ = scan_roots(f, grid, xtol=1e-13)
        if not roots:
            raise NoSolution("No feed amount of the selected species satisfies the "
                             "specification at this T and P. The target may be "
                             "unreachable (e.g. above the equilibrium limit).")
        out = []
        for x in roots:
            n0 = n0_of(x)
            eps = self.eps_from_spec(n0, spec)
            out.append((x, self.state(n0, T, P, eps=eps)))
        return out

    # -- parametric sweeps -------------------------------------------
    def sweep(self, n0, variable, values, T=None, P=None):
        rows = []
        for v in values:
            Ti, Pi = (v, P) if variable == "T" else (T, v)
            try:
                s = self.state(n0, Ti, Pi)
                rows.append((v, s))
            except Exception:
                rows.append((v, None))
        return rows


# ======================================================================
# 7. SMALL HELPERS
# ======================================================================

PRESSURE_TO_BAR = {"bar": 1.0, "atm": 1.01325, "kPa": 0.01, "MPa": 10.0,
                   "Pa": 1e-5, "psia": 0.0689476, "mmHg": 0.00133322}


def reaction_equation(reaction, show_phase=True):
    def fmt(sp):
        c = abs(float(sp["coefficient"]))
        c_txt = "" if math.isclose(c, 1.0) else f"{c:g} "
        tag = {"gas": "g", "liquid": "l", "solid": "s", "aqueous": "aq"}[sp["phase"].lower()]
        return f"{c_txt}{sp['component']}" + (f"({tag})" if show_phase else "")
    left = " + ".join(fmt(s) for s in reaction if float(s["coefficient"]) < 0)
    right = " + ".join(fmt(s) for s in reaction if float(s["coefficient"]) > 0)
    return f"{left}  →  {right}"
