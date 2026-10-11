import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PATH SETUP
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# IMPORT PROJECT MODULES
# ============================================================

from data import get_problem_data
from classical import brute_force_solver
from qaoa_solver import solve_qaoa


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FloodSafe",
    page_icon="🌊",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #777;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 26px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD PROBLEM
# ============================================================

@st.cache_data
def load_problem():
    return get_problem_data()


data = load_problem()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🌊 FloodSafe</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Quantum Optimization for Flood Relief Shelter Placement'
    '</div>',
    unsafe_allow_html=True,
)

st.info(
    "FloodSafe uses QAOA to optimize emergency relief shelter "
    "placement while balancing population reward, flood risk, "
    "and redundant coverage."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Optimization Settings")

qaoa_depth = st.sidebar.selectbox(
    "QAOA Depth (p)",
    options=[1, 2, 3],
    index=0,
)

maxiter = st.sidebar.slider(
    "Optimizer Iterations",
    min_value=5,
    max_value=50,
    value=15,
    step=5,
)

shots = st.sidebar.slider(
    "Sampling Shots",
    min_value=512,
    max_value=4096,
    value=2048,
    step=512,
)

run_button = st.sidebar.button(
    "🚀 Run Quantum Optimization",
    width="stretch",
)


# ============================================================
# PROBLEM OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">📌 Problem Overview</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Candidate Sites",
        data["num_sites"],
    )

with col2:
    st.metric(
        "Shelters Selected",
        data["k"],
    )

with col3:
    st.metric(
        "QAOA Depth",
        qaoa_depth,
    )

with col4:
    st.metric(
        "Sampling Shots",
        shots,
    )


# ============================================================
# SITE DATA
# ============================================================

st.markdown(
    '<div class="section-title">📍 Candidate Relief Sites</div>',
    unsafe_allow_html=True,
)

site_rows = []

for i, site in enumerate(data["sites"]):

    site_rows.append(
        {
            "ID": i,
            "Site": site,
            "Population Score": data["population"][i],
            "Flood Risk": data["flood_risk"][i],
        }
    )

site_df = pd.DataFrame(site_rows)

st.dataframe(
    site_df,
    width="stretch",
    hide_index=True,
)


# ============================================================
# CLASSICAL BASELINE
# ============================================================

st.markdown(
    '<div class="section-title">🖥️ Classical Baseline</div>',
    unsafe_allow_html=True,
)

classical_result = brute_force_solver(data)

classical_objective = classical_result["objective"]


# ------------------------------------------------------------
# Get classical selected indices robustly
# ------------------------------------------------------------

classical_indices = (
    classical_result.get("selected_indices")
    or classical_result.get("selected")
    or classical_result.get("sites")
    or []
)


# ------------------------------------------------------------
# Convert indices to names
# ------------------------------------------------------------

classical_sites = []

for item in classical_indices:

    if isinstance(item, int):

        if 0 <= item < len(data["sites"]):
            classical_sites.append(
                data["sites"][item]
            )

    elif isinstance(item, str):

        classical_sites.append(item)


st.success(
    f"Classical optimum objective: "
    f"**{classical_objective:.2f}**"
)

if classical_sites:

    st.write(
        "**Classical optimal shelters:** "
        + ", ".join(classical_sites)
    )

else:

    st.write(
        "**Classical optimal shelters:** "
        "See optimization result."
    )


# ============================================================
# QUANTUM OPTIMIZATION
# ============================================================

if run_button:

    st.markdown(
        '<div class="section-title">⚛️ QAOA Optimization</div>',
        unsafe_allow_html=True,
    )

    with st.spinner(
        f"Running QAOA with p={qaoa_depth}. "
        "Please wait..."
    ):

        try:

            result = solve_qaoa(
                data=data,
                p=qaoa_depth,
                maxiter=maxiter,
                shots=shots,
            )

        except Exception as e:

            st.error(
                "QAOA execution failed."
            )

            st.exception(e)

            st.stop()


    # ========================================================
    # SUCCESS
    # ========================================================

    st.success(
        "Quantum optimization completed successfully! 🎉"
    )


    # ========================================================
    # RESULTS
    # ========================================================

    st.markdown(
        '<div class="section-title">🏆 Optimization Results</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "QAOA Objective",
            f'{result["objective"]:.2f}',
        )

    with col2:

        st.metric(
            "Classical Objective",
            f'{result["classical_objective"]:.2f}',
        )

    with col3:

        st.metric(
            "Objective Gap",
            f'{result["objective_gap"]:.2f}',
        )

    with col4:

        st.metric(
            "Feasibility Rate",
            f'{result["feasibility_rate"] * 100:.2f}%',
        )


    # ========================================================
    # SELECTED SHELTERS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🚨 Selected Relief Shelters'
        '</div>',
        unsafe_allow_html=True,
    )

    selected_sites = result["selected_sites"]

    if selected_sites:

        st.success(
            "**QAOA Selected Shelters:** "
            + ", ".join(selected_sites)
        )

    else:

        st.warning(
            "No feasible shelter configuration was found."
        )


    # ========================================================
    # QUANTUM VS CLASSICAL
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '⚖️ Classical vs Quantum'
        '</div>',
        unsafe_allow_html=True,
    )

    comparison_df = pd.DataFrame(
        {
            "Metric": [
                "Objective",
                "Objective Gap",
                "Feasible",
                "Feasibility Rate",
            ],
            "Classical": [
                classical_objective,
                0.0,
                "Yes",
                "100%",
            ],
            "QAOA": [
                result["objective"],
                result["objective_gap"],
                "Yes"
                if result["feasible"]
                else "No",
                f'{result["feasibility_rate"] * 100:.2f}%',
            ],
        }
    )

    st.dataframe(
        comparison_df,
        width="stretch",
        hide_index=True,
    )


    # ========================================================
    # OBJECTIVE COMPARISON
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📊 Objective Comparison'
        '</div>',
        unsafe_allow_html=True,
    )

    fig, ax = plt.subplots()

    ax.bar(
        ["Classical", "QAOA"],
        [
            classical_objective,
            result["objective"],
        ],
    )

    ax.set_ylabel(
        "Objective Value"
    )

    ax.set_title(
        "Classical vs QAOA Objective"
    )

    st.pyplot(
        fig,
        clear_figure=True,
    )

    plt.close(fig)


    # ========================================================
    # QAOA PARAMETERS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🧮 Optimized QAOA Parameters'
        '</div>',
        unsafe_allow_html=True,
    )

    parameter_df = pd.DataFrame(
        {
            "Layer": list(
                range(
                    1,
                    len(result["gammas"]) + 1,
                )
            ),
            "Gamma": result["gammas"],
            "Beta": result["betas"],
        }
    )

    st.dataframe(
        parameter_df,
        width="stretch",
        hide_index=True,
    )


    # ========================================================
    # BEST BITSTRING
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🔢 Best Quantum Bitstring'
        '</div>',
        unsafe_allow_html=True,
    )

    st.code(
        result["best_bitstring"],
        language="text",
    )

    st.write(
        f'Best sample count: '
        f'**{result["best_sample_count"]}**'
    )


    # ========================================================
    # FEASIBILITY
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '✅ Constraint Feasibility'
        '</div>',
        unsafe_allow_html=True,
    )

    if result["feasible"]:

        st.success(
            f'Exactly {data["k"]} shelters were selected. '
            'The solution satisfies the cardinality constraint.'
        )

    else:

        st.warning(
            f'The sampled solution does not satisfy '
            f'the exactly-{data["k"]} shelter constraint.'
        )


    # ========================================================
    # QAOA CIRCUIT
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🔬 QAOA Circuit'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.expander(
        "Show Quantum Circuit"
    ):

        st.text(
            result["circuit"].draw(
                output="text"
            )
        )


    # ========================================================
    # QUANTUM COUNTS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📈 Sampled Quantum States'
        '</div>',
        unsafe_allow_html=True,
    )

    counts = result["counts"]

    sorted_counts = sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:15]

    counts_df = pd.DataFrame(
        sorted_counts,
        columns=[
            "Bitstring",
            "Count",
        ],
    )

    st.dataframe(
        counts_df,
        width="stretch",
        hide_index=True,
    )


    # ========================================================
    # LIMITATIONS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '⚠️ Interpretation & Limitations'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write(
        """
        **No quantum advantage is claimed.**

        The classical brute-force solver provides the exact
        optimum for this small 12-site problem.

        QAOA is evaluated according to how closely its sampled
        feasible solution approaches the classical optimum.

        The population term is modeled as a reward, while flood
        risk and redundant coverage are modeled as penalties.

        The exactly-K shelter requirement is encoded through a
        quadratic penalty in the QUBO formulation.

        The current experiment uses a classical statevector
        simulator, so these results do not demonstrate
        fault-tolerant quantum hardware performance.
        """
    )


else:

    # ========================================================
    # READY SCREEN
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🚀 Ready to Optimize'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write(
        """
        Configure the QAOA parameters in the sidebar and click
        **Run Quantum Optimization**.

        FloodSafe will:

        1. Build the optimization Hamiltonian.
        2. Construct the QAOA circuit.
        3. Optimize the QAOA parameters.
        4. Sample the final quantum state.
        5. Find the best feasible shelter configuration.
        6. Compare it against the exact classical solution.
        """
    )

    st.info(
        "💡 For the fastest demonstration, start with "
        "p = 1, 15 iterations, and 2048 shots."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "FloodSafe • Qiskit Fall Fest 2026 • "
    "Track 2: Open-Domain Optimization & Real-World Solvers"
)