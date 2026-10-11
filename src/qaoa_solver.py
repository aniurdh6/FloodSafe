# FloodSafe - QAOA Solver
#
# Direct statevector implementation of QAOA using Qiskit.
# Supports p = 1, 2, 3, ... QAOA layers.

import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from scipy.optimize import minimize

from src.data import get_problem_data
from src.qubo import build_cost_hamiltonian
from src.classical import calculate_objective, brute_force_solver


# ============================================================
# BITSTRING / SELECTION UTILITIES
# ============================================================

def bitstring_to_selection(bitstring, num_sites):
    """
    Convert a Qiskit computational-basis bitstring
    into selected site indices.

    Qiskit bitstrings are ordered:
        q_(n-1) ... q_1 q_0
    """

    bitstring = bitstring.replace(" ", "")

    if len(bitstring) != num_sites:
        raise ValueError(
            f"Expected {num_sites}-bit string, got {len(bitstring)}."
        )

    selected = []

    for q in range(num_sites):
        # q0 corresponds to the rightmost bit
        if bitstring[num_sites - 1 - q] == "1":
            selected.append(q)

    return selected


def selection_to_names(selection, data):
    """Convert selected site indices into site names."""

    return [data["sites"][i] for i in selection]


# ============================================================
# QAOA CIRCUIT
# ============================================================

def build_qaoa_circuit(
    hamiltonian,
    num_qubits,
    gammas,
    betas,
):
    """
    Build a p-layer QAOA circuit.

    Hamiltonian:
        H = sum_j c_j P_j

    Cost unitary:
        U_C(gamma) = exp(-i gamma H)

    Mixer:
        U_B(beta) = exp(-i beta sum_i X_i)

    gammas and betas each contain p parameters.
    """

    p = len(gammas)

    if len(betas) != p:
        raise ValueError(
            "gammas and betas must have the same length."
        )

    qc = QuantumCircuit(num_qubits)

    # --------------------------------------------------------
    # Uniform initial state |+>
    # --------------------------------------------------------

    for q in range(num_qubits):
        qc.h(q)

    # --------------------------------------------------------
    # Convert Hamiltonian to Pauli terms
    # --------------------------------------------------------

    pauli_terms = hamiltonian.to_list()

    # --------------------------------------------------------
    # QAOA layers
    # --------------------------------------------------------

    for layer in range(p):

        gamma = gammas[layer]
        beta = betas[layer]

        # ====================================================
        # COST LAYER
        # ====================================================

        for label, coefficient in pauli_terms:

            coeff = float(np.real(coefficient))

            # Identity term contributes only a global phase.
            if label.count("I") == num_qubits:
                continue

            z_qubits = []

            # Qiskit Pauli labels are q_(n-1)...q_0
            for q in range(num_qubits):

                if label[num_qubits - 1 - q] == "Z":
                    z_qubits.append(q)

            # ------------------------------------------------
            # Single Z term
            # ------------------------------------------------

            if len(z_qubits) == 1:

                q = z_qubits[0]

                # RZ(theta) = exp(-i theta Z / 2)
                #
                # Need:
                # exp(-i gamma * coeff * Z)
                #
                # Therefore:
                # theta = 2 * gamma * coeff

                qc.rz(
                    2.0 * gamma * coeff,
                    q,
                )

            # ------------------------------------------------
            # ZZ term
            # ------------------------------------------------

            elif len(z_qubits) == 2:

                q1, q2 = z_qubits

                # RZZ(theta) = exp(-i theta ZZ / 2)
                #
                # Therefore:
                # theta = 2 * gamma * coeff

                qc.rzz(
                    2.0 * gamma * coeff,
                    q1,
                    q2,
                )

            else:

                raise ValueError(
                    f"Unsupported Pauli term in Hamiltonian: {label}"
                )

        # ====================================================
        # MIXER LAYER
        # ====================================================

        for q in range(num_qubits):

            # RX(theta) = exp(-i theta X / 2)
            #
            # Need:
            # exp(-i beta X)
            #
            # Therefore:
            # theta = 2 * beta

            qc.rx(
                2.0 * beta,
                q,
            )

    return qc


# ============================================================
# EXPECTATION VALUE
# ============================================================

def expectation_value(
    hamiltonian,
    statevector,
):
    """
    Calculate:

        <psi|H|psi>

    using matrix-vector multiplication.
    """

    # Apply H to |psi>
    evolved = hamiltonian @ statevector

    # Calculate <psi|H|psi>
    value = np.vdot(
        statevector,
        evolved,
    )

    return float(np.real(value))


# ============================================================
# QAOA OPTIMIZATION
# ============================================================

def optimize_qaoa(
    hamiltonian,
    num_qubits,
    p=1,
    maxiter=30,
):
    """
    Optimize QAOA parameters using a classical optimizer.

    Parameters
    ----------
    hamiltonian :
        Ising Hamiltonian.

    num_qubits :
        Number of qubits.

    p : int
        Number of QAOA layers.

    maxiter : int
        Maximum number of classical optimization iterations.
    """

    if p < 1:
        raise ValueError(
            "QAOA depth p must be at least 1."
        )

    # --------------------------------------------------------
    # Reproducible initial parameters
    # --------------------------------------------------------

    rng = np.random.default_rng(42)

    initial_gammas = rng.uniform(
        0.1,
        0.8,
        size=p,
    )

    initial_betas = rng.uniform(
        0.1,
        0.8,
        size=p,
    )

    initial_params = np.concatenate(
        [
            initial_gammas,
            initial_betas,
        ]
    )

    # --------------------------------------------------------
    # Objective function for classical optimizer
    # --------------------------------------------------------

    def objective(params):

        gammas = params[:p]
        betas = params[p:]

        circuit = build_qaoa_circuit(
            hamiltonian,
            num_qubits,
            gammas,
            betas,
        )

        state = Statevector.from_instruction(
            circuit
        )

        return expectation_value(
            hamiltonian,
            state,
        )

    # --------------------------------------------------------
    # Classical optimization
    # --------------------------------------------------------

    result = minimize(
        objective,
        initial_params,
        method="COBYLA",
        options={
            "maxiter": maxiter,
            "rhobeg": 0.5,
        },
    )

    # --------------------------------------------------------
    # Optimized parameters
    # --------------------------------------------------------

    optimized_params = result.x

    gammas = optimized_params[:p]
    betas = optimized_params[p:]

    # --------------------------------------------------------
    # Build final optimized circuit
    # --------------------------------------------------------

    final_circuit = build_qaoa_circuit(
        hamiltonian,
        num_qubits,
        gammas,
        betas,
    )

    # --------------------------------------------------------
    # Final statevector
    # --------------------------------------------------------

    final_state = Statevector.from_instruction(
        final_circuit
    )

    # --------------------------------------------------------
    # Final expectation value
    # --------------------------------------------------------

    final_energy = expectation_value(
        hamiltonian,
        final_state,
    )

    return {
        "gammas": gammas,
        "betas": betas,
        "energy": final_energy,
        "statevector": final_state,
        "circuit": final_circuit,
        "optimizer_result": result,
    }


# ============================================================
# SAMPLING
# ============================================================

def sample_statevector(
    statevector,
    shots=2048,
    seed=42,
):
    """
    Sample computational-basis states from a Statevector.
    """

    probabilities = statevector.probabilities()

    rng = np.random.default_rng(seed)

    states = np.arange(
        len(probabilities)
    )

    samples = rng.choice(
        states,
        size=shots,
        p=probabilities,
    )

    counts = {}

    num_qubits = statevector.num_qubits

    for state in samples:

        bitstring = format(
            int(state),
            f"0{num_qubits}b",
        )

        counts[bitstring] = (
            counts.get(
                bitstring,
                0,
            )
            + 1
        )

    return counts


# ============================================================
# MAIN QAOA SOLVER
# ============================================================

def solve_qaoa(
    data=None,
    p=1,
    maxiter=30,
    shots=2048,
):
    """
    Solve the FloodSafe shelter placement problem using QAOA.

    Supports arbitrary QAOA depth p >= 1.
    """

    # --------------------------------------------------------
    # Load problem data
    # --------------------------------------------------------

    if data is None:
        data = get_problem_data()

    # --------------------------------------------------------
    # Build Ising Hamiltonian
    # --------------------------------------------------------

    hamiltonian, pieces = build_cost_hamiltonian(
        data
    )

    num_qubits = data["num_sites"]

    # --------------------------------------------------------
    # Classical exact baseline
    # --------------------------------------------------------

    classical = brute_force_solver(
        data
    )

    # --------------------------------------------------------
    # Optimize QAOA
    # --------------------------------------------------------

    optimization_result = optimize_qaoa(
        hamiltonian,
        num_qubits,
        p=p,
        maxiter=maxiter,
    )

    statevector = optimization_result[
        "statevector"
    ]

    # --------------------------------------------------------
    # Sample final quantum state
    # --------------------------------------------------------

    counts = sample_statevector(
        statevector,
        shots=shots,
        seed=42,
    )

    # ========================================================
    # FIND BEST FEASIBLE SAMPLED SOLUTION
    # ========================================================

    best_solution = None

    feasible_count = 0

    for bitstring, count in counts.items():

        selected = bitstring_to_selection(
            bitstring,
            num_qubits,
        )

        # ----------------------------------------------------
        # Exact-K feasibility
        # ----------------------------------------------------

        if len(selected) == data["k"]:

            feasible_count += count

            objective = calculate_objective(
                selected,
                data,
            )

            if (
                best_solution is None
                or objective
                < best_solution["objective"]
            ):

                best_solution = {
                    "bitstring": bitstring,
                    "selected": selected,
                    "objective": objective,
                    "count": count,
                }

    # ========================================================
    # HANDLE CASE WHERE NO FEASIBLE SAMPLE APPEARED
    # ========================================================

    if best_solution is None:

        most_frequent = max(
            counts.items(),
            key=lambda x: x[1],
        )

        bitstring = most_frequent[0]

        selected = bitstring_to_selection(
            bitstring,
            num_qubits,
        )

        objective = calculate_objective(
            selected,
            data,
        )

        best_solution = {
            "bitstring": bitstring,
            "selected": selected,
            "objective": objective,
            "count": most_frequent[1],
        }

    # ========================================================
    # METRICS
    # ========================================================

    qaoa_objective = (
        best_solution["objective"]
    )

    classical_objective = (
        classical["objective"]
    )

    objective_gap = (
        qaoa_objective
        - classical_objective
    )

    feasibility_rate = (
        feasible_count / shots
    )

    feasible = (
        len(best_solution["selected"])
        == data["k"]
    )

    selected_names = selection_to_names(
        best_solution["selected"],
        data,
    )

    # ========================================================
    # RETURN COMPLETE RESULT
    # ========================================================

    return {
        "selected_sites": selected_names,

        "selected_indices": (
            best_solution["selected"]
        ),

        "objective": qaoa_objective,

        "classical_objective": (
            classical_objective
        ),

        "objective_gap": objective_gap,

        "feasible": feasible,

        "feasibility_rate": (
            feasibility_rate
        ),

        "best_bitstring": (
            best_solution["bitstring"]
        ),

        "best_sample_count": (
            best_solution["count"]
        ),

        "counts": counts,

        "gammas": (
            optimization_result["gammas"]
        ),

        "betas": (
            optimization_result["betas"]
        ),

        "energy": (
            optimization_result["energy"]
        ),

        "circuit": (
            optimization_result["circuit"]
        ),

        "statevector": (
            optimization_result["statevector"]
        ),

        "p": p,

        "shots": shots,

        "maxiter": maxiter,

        "classical_solution": classical,

        "hamiltonian": hamiltonian,

        "qubo_pieces": pieces,
    }


# ============================================================
# TEST FROM TERMINAL
# ============================================================

if __name__ == "__main__":

    data = get_problem_data()

    print("FloodSafe QAOA Solver")
    print("====================")
    print()

    result = solve_qaoa(
        data,
        p=1,
        maxiter=30,
        shots=2048,
    )

    print(
        "QAOA depth:",
        result["p"],
    )

    print(
        "Selected shelters:",
        result["selected_sites"],
    )

    print(
        "QAOA objective:",
        result["objective"],
    )

    print(
        "Classical optimal objective:",
        result["classical_objective"],
    )

    print(
        "Objective gap:",
        result["objective_gap"],
    )

    print(
        "Feasible:",
        result["feasible"],
    )

    print(
        "Feasibility rate:",
        result["feasibility_rate"],
    )