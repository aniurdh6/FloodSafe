# FloodSafe - QUBO and Ising Hamiltonian construction

from src.data import get_problem_data
from qiskit.quantum_info import SparsePauliOp


# ============================================================
# QUBO WEIGHTS
# ============================================================

POPULATION_WEIGHT = 1.0
RISK_WEIGHT = 0.35
OVERLAP_WEIGHT = 12.0

# Penalty for selecting something other than exactly K shelters
CONSTRAINT_PENALTY = 50.0


# ============================================================
# BUILD QUBO
# ============================================================

def build_qubo(data=None):
    """
    Build the FloodSafe QUBO.

    Objective:
        - maximize population coverage
        + minimize flood risk
        + minimize redundant coverage

    Constraint:
        select exactly K shelters.
    """

    if data is None:
        data = get_problem_data()

    n = data["num_sites"]
    k = data["k"]

    population = data["population"]
    flood_risk = data["flood_risk"]
    overlap = data["overlap"]

    # Linear coefficients
    linear = {}

    for i in range(n):

        linear[i] = (
            -POPULATION_WEIGHT * population[i]
            + RISK_WEIGHT * flood_risk[i]
        )

    # Quadratic coefficients
    quadratic = {}

    # Overlap penalty
    for (i, j), value in overlap.items():

        quadratic[(i, j)] = (
            OVERLAP_WEIGHT * value
        )

    # ========================================================
    # EXACT-K CONSTRAINT
    #
    # A(sum(x_i) - K)^2
    #
    # = A sum(x_i)
    #   + 2A sum(x_i x_j)
    #   - 2AK
    #   + AK^2
    # ========================================================

    A = CONSTRAINT_PENALTY

    # Linear contribution
    for i in range(n):
        linear[i] += A - 2 * A * k

    # Quadratic contribution
    for i in range(n):
        for j in range(i + 1, n):

            if (i, j) in quadratic:
                quadratic[(i, j)] += 2 * A
            else:
                quadratic[(i, j)] = 2 * A

    # Constant contribution
    constant = A * (k ** 2)

    return {
        "linear": linear,
        "quadratic": quadratic,
        "constant": constant,
    }


# ============================================================
# QUBO -> ISING
# ============================================================

def qubo_to_ising(qubo):
    """
    Convert QUBO into an Ising Hamiltonian.

    Uses:

        x_i = (1 - Z_i) / 2
    """

    linear = qubo["linear"]
    quadratic = qubo["quadratic"]
    constant = qubo["constant"]

    num_qubits = len(linear)

    # Identity coefficient
    identity_coefficient = float(constant)

    # Z coefficients
    z_coefficients = {
        i: 0.0
        for i in range(num_qubits)
    }

    # ZZ coefficients
    zz_coefficients = {}

    # --------------------------------------------------------
    # Linear terms
    #
    # a_i x_i
    #
    # = a_i/2 - a_i/2 Z_i
    # --------------------------------------------------------

    for i, coefficient in linear.items():

        coefficient = float(coefficient)

        identity_coefficient += coefficient / 2.0

        z_coefficients[i] += -coefficient / 2.0

    # --------------------------------------------------------
    # Quadratic terms
    #
    # b_ij x_i x_j
    #
    # = b_ij/4
    #   - b_ij/4 Z_i
    #   - b_ij/4 Z_j
    #   + b_ij/4 Z_i Z_j
    # --------------------------------------------------------

    for (i, j), coefficient in quadratic.items():

        coefficient = float(coefficient)

        identity_coefficient += coefficient / 4.0

        z_coefficients[i] += -coefficient / 4.0
        z_coefficients[j] += -coefficient / 4.0

        zz_coefficients[(i, j)] = (
            zz_coefficients.get((i, j), 0.0)
            + coefficient / 4.0
        )

    # --------------------------------------------------------
    # Build SparsePauliOp
    # --------------------------------------------------------

    paulis = []
    coefficients = []

    # Identity
    paulis.append("I" * num_qubits)
    coefficients.append(identity_coefficient)

    # Z terms
    for i in range(num_qubits):

        coefficient = z_coefficients[i]

        if abs(coefficient) > 1e-12:

            label = ["I"] * num_qubits

            # Qiskit Pauli labels are ordered q(n-1)...q0
            label[num_qubits - 1 - i] = "Z"

            paulis.append("".join(label))
            coefficients.append(coefficient)

    # ZZ terms
    for (i, j), coefficient in zz_coefficients.items():

        if abs(coefficient) <= 1e-12:
            continue

        label = ["I"] * num_qubits

        label[num_qubits - 1 - i] = "Z"
        label[num_qubits - 1 - j] = "Z"

        paulis.append("".join(label))
        coefficients.append(coefficient)

    hamiltonian = SparsePauliOp(
        paulis,
        coeffs=coefficients
    )

    return hamiltonian


# ============================================================
# COMPLETE COST HAMILTONIAN
# ============================================================

def build_cost_hamiltonian(data=None):
    """
    Build the FloodSafe QUBO and corresponding
    Ising cost Hamiltonian.
    """

    if data is None:
        data = get_problem_data()

    qubo = build_qubo(data)

    hamiltonian = qubo_to_ising(
        qubo
    )

    return hamiltonian, qubo


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    data = get_problem_data()

    hamiltonian, qubo = build_cost_hamiltonian(
        data
    )

    print()
    print("FloodSafe QUBO")
    print("==============")
    print(
        "Number of variables:",
        data["num_sites"]
    )
    print(
        "Number of shelters (K):",
        data["k"]
    )
    print(
        "Constraint penalty:",
        CONSTRAINT_PENALTY
    )
    print(
        "QUBO constant:",
        qubo["constant"]
    )
    print(
        "Linear terms:",
        len(qubo["linear"])
    )
    print(
        "Quadratic terms:",
        len(qubo["quadratic"])
    )
    print(
        "Number of qubits:",
        hamiltonian.num_qubits
    )