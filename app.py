import sys
import os

import streamlit as st
import pandas as pd


# ---------------------------------------------------------
# Add src folder to Python path
# ---------------------------------------------------------

SRC_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "src"
)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# ---------------------------------------------------------
# Import FloodSafe modules
# ---------------------------------------------------------

from data import get_problem_data
from classical import brute_force_solver, calculate_objective
from qaoa_solver import run_qaoa


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="FloodSafe | Quantum Shelter Optimization",
    page_icon="🌊",
    layout="wide",
)


# ---------------------------------------------------------
# Load problem data
# ---------------------------------------------------------

data = get_problem_data()

sites = data["sites"]
population = data["population"]
risk = data["flood_risk"]
coordinates = data["coordinates"]
k = data["k"]


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def calculate_metrics(selected_sites):
    """Calculate real-world metrics for selected shelters."""

    population_score = sum(
        population[i] for i in selected_sites
    )

    risk_score = sum(
        risk[i] for i in selected_sites
    )

    overlap_score = 0.0

    selected_set = set(selected_sites)

    for (i, j), value in data["overlap"].items():
        if i in selected_set and j in selected_set:
            overlap_score += value

    objective = calculate_objective(
        selected_sites,
        data
    )

    return (
        population_score,
        risk_score,
        overlap_score,
        objective,
    )


def create_site_dataframe(selected_sites):

    rows = []

    for i, site in enumerate(sites):

        longitude, latitude = coordinates[site]

        rows.append({
            "Site": site,
            "Latitude": latitude,
            "Longitude": longitude,
            "Population": population[i],
            "Flood Risk": risk[i],
            "Selected": (
                "Selected"
                if i in selected_sites
                else "Candidate"
            ),
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("🌊 FloodSafe")

st.subheader(
    "Quantum Optimization for Emergency Relief Shelter Placement"
)

st.markdown(
    """
**FloodSafe** uses **Qiskit QAOA** to determine where emergency
relief shelters should be placed while balancing population coverage,
flood risk, and redundant coverage.
"""
)

st.divider()


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Optimization Settings")

depth = st.sidebar.selectbox(
    "QAOA Depth",
    [1, 2, 3],
    index=0,
)

st.sidebar.metric(
    "Candidate Sites",
    data["num_sites"],
)

st.sidebar.metric(
    "Shelters to Select",
    k,
)

st.sidebar.info(
    "This demonstration uses 12 synthetic "
    "Kerala-inspired candidate locations."
)


# ---------------------------------------------------------
# Classical baseline
# ---------------------------------------------------------

with st.spinner("Calculating classical baseline..."):

    classical_selection, classical_objective, all_results = (
        brute_force_solver(data)
    )

classical_population, classical_risk, classical_overlap, _ = (
    calculate_metrics(classical_selection)
)


# ---------------------------------------------------------
# Top metrics
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Candidate Sites",
        data["num_sites"],
    )

with col2:
    st.metric(
        "Shelters Selected",
        k,
    )

with col3:
    st.metric(
        "Population Coverage",
        classical_population,
    )

with col4:
    st.metric(
        "Classical Objective",
        f"{classical_objective:.2f}",
    )


# ---------------------------------------------------------
# Classical baseline
# ---------------------------------------------------------

st.header("Classical Baseline")

st.write(
    "The classical baseline exhaustively evaluates all "
    f"{len(all_results)} possible 4-site combinations."
)

classical_names = [
    sites[i]
    for i in classical_selection
]

st.success(
    "Classical optimal shelters: "
    + ", ".join(classical_names)
)


# ---------------------------------------------------------
# Candidate locations
# ---------------------------------------------------------

st.header("Candidate Shelter Locations")

map_df = create_site_dataframe(
    classical_selection
)

st.map(
    map_df,
    latitude="Latitude",
    longitude="Longitude",
    size=100,
)

st.dataframe(
    map_df[
        [
            "Site",
            "Population",
            "Flood Risk",
            "Selected",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Quantum optimization
# ---------------------------------------------------------

st.divider()

st.header("Quantum Optimization")

st.write(
    f"Run QAOA with depth **p={depth}** using the "
    "12-qubit FloodSafe optimization model."
)

run_button = st.button(
    "Run QAOA Optimization",
    type="primary",
    use_container_width=True,
)


if run_button:

    with st.spinner(
        f"Running QAOA p={depth}..."
    ):

        qaoa_result = run_qaoa(
            data,
            depth=depth,
        )

    qaoa_selection = qaoa_result["selected_sites"]

    qaoa_population, qaoa_risk, qaoa_overlap, qaoa_objective = (
        calculate_metrics(qaoa_selection)
    )

    objective_gap = (
        qaoa_objective - classical_objective
    )

    # -----------------------------------------------------
    # Quantum result
    # -----------------------------------------------------

    st.success(
        "QAOA optimization completed successfully!"
    )

    st.header("QAOA Recommendation")

    qaoa_names = [
        sites[i]
        for i in qaoa_selection
    ]

    st.info(
        "Recommended shelters: "
        + ", ".join(qaoa_names)
    )

    # -----------------------------------------------------
    # Quantum metrics
    # -----------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Population Coverage",
            qaoa_population,
        )

    with c2:
        st.metric(
            "Flood Risk",
            qaoa_risk,
        )

    with c3:
        st.metric(
            "QAOA Objective",
            f"{qaoa_objective:.2f}",
        )

    with c4:
        st.metric(
            "Objective Gap",
            f"{objective_gap:.2f}",
        )

    # -----------------------------------------------------
    # Quantum vs classical
    # -----------------------------------------------------

    st.header("Quantum vs Classical")

    comparison = pd.DataFrame(
        {
            "Method": [
                "Classical",
                f"QAOA p={depth}",
            ],
            "Objective": [
                classical_objective,
                qaoa_objective,
            ],
            "Population": [
                classical_population,
                qaoa_population,
            ],
            "Flood Risk": [
                classical_risk,
                qaoa_risk,
            ],
        }
    )

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------------------------------
    # Result interpretation
    # -----------------------------------------------------

    if abs(objective_gap) < 1e-9:

        st.success(
            "QAOA found the same optimal shelter "
            "placement as the classical exhaustive search."
        )

    else:

        st.warning(
            f"QAOA produced a feasible solution with an "
            f"objective gap of {objective_gap:.2f} "
            "from the classical optimum."
        )

    # -----------------------------------------------------
    # QAOA solution map
    # -----------------------------------------------------

    st.header("QAOA Shelter Placement")

    qaoa_map_df = create_site_dataframe(
        qaoa_selection
    )

    st.map(
        qaoa_map_df,
        latitude="Latitude",
        longitude="Longitude",
        size=100,
    )

    # -----------------------------------------------------
    # Selected shelters
    # -----------------------------------------------------

    st.header("Selected Relief Shelters")

    selected_table = qaoa_map_df[
        qaoa_map_df["Selected"] == "Selected"
    ][
        [
            "Site",
            "Population",
            "Flood Risk",
        ]
    ]

    st.dataframe(
        selected_table,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Methodology
# ---------------------------------------------------------

st.divider()

with st.expander("How FloodSafe Works"):

    st.markdown(
        """
### 1. Real-world formulation

Each candidate location is represented by a binary
decision variable:

`xᵢ = 1` → select the shelter

`xᵢ = 0` → do not select the shelter

### 2. Optimization objective

FloodSafe balances:

- Population coverage
- Flood-risk penalty
- Redundant coverage penalty
- Exactly 4 selected shelters

### 3. QUBO

The real-world optimization problem is converted
into a **Quadratic Unconstrained Binary Optimization
(QUBO)** formulation.

### 4. Ising Hamiltonian

The QUBO is transformed into an Ising cost Hamiltonian
using:

`xᵢ = (1 - Zᵢ) / 2`

### 5. QAOA

Qiskit is used to construct and optimize the QAOA
circuit.

The resulting quantum state is sampled to obtain
candidate shelter placements.

### 6. Classical comparison

The quantum result is compared against exhaustive
classical search over all 495 possible combinations.
"""
    )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "FloodSafe | Qiskit Fall Fest 2026 | "
    "Open-Domain Optimization & Real-World Solvers"
)