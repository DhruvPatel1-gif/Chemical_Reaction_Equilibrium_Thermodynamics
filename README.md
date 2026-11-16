# ⚗️ Chemical Reaction Equilibrium Simulator

A comprehensive thermodynamic workbench built with **Streamlit**, **NumPy**, **SciPy**, and **ReportLab** for calculating equilibrium states of single chemical reactions across gas, liquid, and pure-solid phases.

---

## 🚀 Quick Start (Local Run)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the Streamlit app:**
   ```bash
   streamlit run app.py
   ```
   *(or `streamlit run MaIn.py`)*

3. Open your browser at `http://localhost:8501`.

---

## 🌐 Deploying to Streamlit Community Cloud

Deploying this app to [Streamlit Community Cloud](https://share.streamlit.io/) is free and takes less than 2 minutes:

### Step 1: Initialize Git and Push to GitHub

From the project root directory (`Chemical Reaction Equilibrium Thermodynaics`):

```bash
# 1. Initialize git (if not already done)
git init

# 2. Stage all files (requirements.txt, .streamlit, app.py, pages, etc.)
git add .

# 3. Commit files
git commit -m "Initial commit for Streamlit deployment"

# 4. Set the main branch
git branch -M main

# 5. Link to your GitHub repository (replace with your repo URL)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git

# 6. Push to GitHub
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Log in to [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
2. Click **"New app"**.
3. Select your repository: `<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>`.
4. Set **Branch**: `main`.
5. Set **Main file path**: `app.py`.
6. Click **"Deploy!"**.

Streamlit Cloud will automatically:
- Read `requirements.txt` and install all Python dependencies (`thermo`, `chemicals`, `scipy`, `reportlab`, `pandas`, `streamlit`, `numpy`).
- Read `packages.txt` and install system fonts (`fonts-liberation`) for PDF report generation.
- Read `.streamlit/config.toml` to style the application.

---

## 📁 Repository Structure

```
.
├── app.py                      # Main entrypoint for Streamlit Cloud deployment
├── MaIn.py                     # Alternative entrypoint (identical navigation)
├── requirements.txt            # Python dependencies for pip
├── packages.txt                # Linux OS apt-get packages (fonts for ReportLab)
├── .gitignore                  # Git ignore rules for clean repository
├── README.md                   # Project overview & deployment guide
├── .streamlit/
│   └── config.toml             # Streamlit server & theme configuration
├── Data.py                     # Thermodynamic database (Cp coefficients, ΔHf°, ΔGf°)
├── equilibrium_engine.py       # Core equilibrium calculation engine (NumPy / SciPy)
├── report.py                   # Formal PDF report generator (ReportLab)
├── theme.py                    # Styling, typography & theme manager
└── pages/                      # Multi-page application structure
    ├── home.py                 # Landing page & overview
    ├── components.py           # Species & phase selection
    ├── reaction.py             # Stoichiometry & reaction definition
    ├── calculation_type.py     # Choice of unknown (T, P, conversion, composition, feed)
    └── condition.py            # Equilibrium calculation & PDF report export
```

---

## 🔬 Thermodynamic Capabilities

- **Gas-Phase Fugacity Models**:
  - Ideal Gas
  - Peng–Robinson Equation of State (EOS)
  - Soave–Redlich–Kwong (SRK) EOS
  - Second-Virial coefficient model
- **Liquid-Phase Activity Models**:
  - Ideal Solution
  - Margules, Van Laar, Wilson, and NRTL equations
  - Custom excess Gibbs energy functions ($G^E / RT$)
- **Solid Phases**:
  - Pure solids with unit activity ($a_i = 1$)
- **Formal Reporting**:
  - High-precision PDF reports formatted with Times-compatible serif typography, summary tables, step-by-step working, and convergence details.
