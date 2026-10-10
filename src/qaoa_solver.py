# FloodSafe - Fast QAOA quantum solver

import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from scipy.optimize import minimize

from data import get_problem_data
from qubo import build_cost_hamiltonian
from classical import calculate_objective, brute_force_solver


# ---------------------------------------------------------
# QAOA settings
# ---------------------------------------------------------

QAOA_DEPTH = 3
MAX_ITERATIONS = 30
SHOTS = 2048


# ---------------------------------------------------------
# Build QAOA circuit
# ---------------------------------------------------------

def build_qaoa_circuit(cost_hamiltonian, gamma, beta, depth=1):
    """
    Build a QAOA circuit using cost and mixer layers.
    """

    n = cost_hamiltonian.num_qubits

    qc = QuantumCircuit(n)

    # Initial |+> state
    for q in range(n):
        qc.h(q)

    # QAOA layers
    for layer in range(depth):

        g = gamma[layer]
        b = beta[layer]

        # -------------------------------------------------
        # Cost layer
        #
        # For each Pauli term:
        #
        # Z_i      -> RZ
        # Z_i Z_j  -> RZZ
        # -------------------------------------------------

        for pauli, coefficient in zip(
            cost_hamiltonian.paulis,
            cost_hamiltonian.coeffs
        ):

            coefficient = float(np.real(coefficient))

            # Ignore identity
            if pauli.to_label().count("Z") == 0:
                continue

            z_positions = [
                i
                for i, p in enumerate(pauli.to_label()[::-1])
                if p == "Z"
            ]

            if len(z_positions) == 1:

                qc.rz(
                    2 * g * coefficient,
                    z_positions[0]
                )

            elif len(z_positions) == 2:

                i, j = z_positions

                qc.rzz(
                    2 * g * coefficient,
                    i,
                    j
                )

        # -------------------------------------------------
        # Mixer layer
        # -------------------------------------------------

        for q in range(n):

            qc.rx(
                2 * b,
                q
            )

    return qc


# ---------------------------------------------------------
# Energy calculation
# ---------------------------------------------------------

def calculate_energy(statevector, hamiltonian):
    """
    Calculate <psi|H|psi>.
    """

    energy = statevector.expectation_value(
        hamiltonian
    )

    return float(np.real(energy))


# ---------------------------------------------------------
# QAOA optimization
# ---------------------------------------------------------

def run_qaoa(data, depth=QAOA_DEPTH):

    hamiltonian, _, _, _ = build_cost_hamiltonian(data)

    n = hamiltonian.num_qubits

    print()
    print("=" * 60)
    print("FloodSafe - QAOA Solver")
    print("=" * 60)

    print()
    print("Qubits:", n)
    print("QAOA depth:", depth)
    print("Maximum iterations:", MAX_ITERATIONS)
    print("Shots:", SHOTS)

    # -----------------------------------------------------
    # Objective history
    # -----------------------------------------------------

    objective_history = []

    # -----------------------------------------------------
    # QAOA objective function
    # -----------------------------------------------------

    def objective(parameters):

        gamma = parameters[:depth]
        beta = parameters[depth:]

        circuit = build_qaoa_circuit(
            hamiltonian,
            gamma,
            beta,
            depth
        )

        statevector = Statevector.from_instruction(
            circuit
        )

        energy = calculate_energy(
            statevector,
            hamiltonian
        )

        objective_history.append(energy)

        return energy

    # -----------------------------------------------------
    # Initial parameters
    # -----------------------------------------------------

    np.random.seed(42)

    initial_parameters = np.random.uniform(
        0,
        np.pi,
        2 * depth
    )

    print()
    print("Number of QAOA parameters:",
          len(initial_parameters))

    print()
    print("Starting QAOA optimization...")

    # -----------------------------------------------------
    # Classical optimizer
    # -----------------------------------------------------

    result = minimize(
        objective,
        initial_parameters,
        method="COBYLA",
        options={
            "maxiter": MAX_ITERATIONS
        }
    )

    print()
    print("Optimization finished.")

    print("Iterations:",
          result.nfev)

    print("Minimum expected energy:",
          round(float(result.fun), 6))

    print()
    print("Optimal parameters:")

    print(
        np.round(result.x, 5)
    )

    # -----------------------------------------------------
    # Build optimized circuit
    # -----------------------------------------------------

    gamma = result.x[:depth]
    beta = result.x[depth:]

    optimized_circuit = build_qaoa_circuit(
        hamiltonian,
        gamma,
        beta,
        depth
    )

    optimized_statevector = Statevector.from_instruction(
        optimized_circuit
    )

    # -----------------------------------------------------
    # Get computational-basis probabilities
    # -----------------------------------------------------

    probabilities = optimized_statevector.probabilities()

    # -----------------------------------------------------
    # Sample bitstrings
    # -----------------------------------------------------

    rng = np.random.default_rng(42)

    states = np.arange(
        2 ** n
    )

    sampled_states = rng.choice(
        states,
        size=SHOTS,
        p=probabilities
    )

    # Count samples
    counts = {}

    for state in sampled_states:

        bitstring = format(
            state,
            f"0{n}b"
        )

        counts[bitstring] = (
            counts.get(bitstring, 0) + 1
        )

    # -----------------------------------------------------
    # Evaluate sampled solutions
    # -----------------------------------------------------

    scored = []

    for key, count in counts.items():

        # Qiskit little-endian convention
        bits = key[::-1]

        assignment = [
            int(bits[i])
            for i in range(n)
        ]

        selected_sites = [
            i
            for i, bit in enumerate(assignment)
            if bit == 1
        ]

        objective_value = calculate_objective(
            selected_sites,
            data
        )

        feasible = (
            len(selected_sites) == data["k"]
        )

        scored.append(
            (
                assignment,
                count,
                objective_value,
                feasible
            )
        )

    # -----------------------------------------------------
    # Only consider feasible solutions
    # -----------------------------------------------------

    feasible_results = [
        item
        for item in scored
        if item[3]
    ]

    if feasible_results:

        best = min(
            feasible_results,
            key=lambda x: x[2]
        )

    else:

        best = min(
            scored,
            key=lambda x: abs(
                sum(x[0]) - data["k"]
            )
        )

    best_assignment = best[0]
    best_count = best[1]
    best_objective = best[2]
    best_feasible = best[3]

    selected_sites = [
        i
        for i, bit in enumerate(best_assignment)
        if bit == 1
    ]

    # -----------------------------------------------------
    # Feasibility rate
    # -----------------------------------------------------

    total_shots = sum(
        count
        for _, count, _, _ in scored
    )

    feasible_shots = sum(
        count
        for _, count, _, feasible in scored
        if feasible
    )

    feasibility_rate = (
        feasible_shots / total_shots
    )

    # -----------------------------------------------------
    # Classical optimum
    # -----------------------------------------------------

    classical_selection, classical_objective, _ = (
        brute_force_solver(data)
    )

    # -----------------------------------------------------
    # Objective comparison
    # -----------------------------------------------------

    objective_gap = (
        best_objective -
        classical_objective
    )

    # -----------------------------------------------------
    # Results
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("QAOA RESULTS")
    print("=" * 60)

    print()
    print("Best QAOA assignment:")
    print(best_assignment)

    print()
    print("Selected shelter locations:")

    for index in selected_sites:

        print(
            f"  {index}: {data['sites'][index]}"
        )

    print()
    print("Number of selected shelters:",
          len(selected_sites))

    print()
    print("QAOA objective:",
          round(best_objective, 3))

    print("Classical optimal objective:",
          round(classical_objective, 3))

    print("Objective gap:",
          round(objective_gap, 3))

    print()
    print("Feasible solution:",
          best_feasible)

    print(
        "Feasibility rate:",
        f"{feasibility_rate * 100:.2f}%"
    )

    print()
    print("Best solution sample count:",
          best_count)

    print()
    print("=" * 60)
    print("FloodSafe QAOA completed!")
    print("=" * 60)

    return {
        "assignment": best_assignment,
        "selected_sites": selected_sites,
        "objective": best_objective,
        "classical_selection": classical_selection,
        "classical_objective": classical_objective,
        "objective_gap": objective_gap,
        "feasibility_rate": feasibility_rate,
        "counts": counts,
        "objective_history": objective_history,
        "optimal_parameters": result.x,
        "circuit": optimized_circuit,
    }


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    data = get_problem_data()

    run_qaoa(
        data,
        depth=QAOA_DEPTH
    )