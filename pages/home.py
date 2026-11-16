import streamlit as st

st.markdown(
    """
    <div style="padding:2.1rem 2.3rem;border-radius:18px;
                background:linear-gradient(120deg,#17324d 0%,#315f7e 100%);
                color:#fff;margin-bottom:1.4rem;
                box-shadow:0 8px 24px rgba(23,50,77,.16);">
        <div style="font-size:.82rem;letter-spacing:.16em;text-transform:uppercase;
                    opacity:.82;margin-bottom:.7rem;">
            Chemical Engineering • Thermodynamics
        </div>
        <div style="font-size:2.25rem;font-weight:600;line-height:1.2;
                    font-family:Georgia,'Times New Roman',serif;">
            Chemical Reaction Equilibrium Simulator
        </div>
        <div style="font-size:1.05rem;opacity:.9;margin-top:.8rem;max-width:850px;">
            A thermodynamic workbench for calculating equilibrium states across
            gas, liquid and pure-solid phases.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("A structured workflow")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 01 · Components")
    st.write("Choose chemical species and assign their physical phases.")
with c2:
    st.markdown("### 02 · Reaction")
    st.write("Build the balanced reaction using stoichiometric coefficients.")
with c3:
    st.markdown("### 03 · Calculation")
    st.write("Specify operating conditions and select suitable thermodynamic models.")

st.divider()
st.subheader("Thermodynamic capabilities")
left, right = st.columns(2)
with left:
    st.markdown(
        """
        **Gas-phase models**
        - Ideal gas
        - Peng–Robinson EOS
        - Soave–Redlich–Kwong EOS
        - Second-virial model
        """
    )
with right:
    st.markdown(
        """
        **Liquid and solid phases**
        - Ideal liquid solution
        - Margules, Van Laar, Wilson and NRTL
        - Custom excess Gibbs-energy expression
        - Pure solids with unit activity
        """
    )

st.info("Begin with **Add Components** in the sidebar, then define your reaction.")
