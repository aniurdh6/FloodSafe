# FloodSafe - QUBO and Ising Hamiltonian construction

from data import get_problem_data

from qiskit.quantum_info import SparsePauliOp


# ---------------------------------------------------------
# QUBO weights
# ---------------------------------------------------------

POPULATION_WEIGHT = 1.0
RISK_WEIGHT = 0.35
OVERLAP_WEIGHT = 12.0

# Penalty for violating the exactly-K constraint
CONSTRAINT_PENALTY = 50.0


# ---------------------------------------------------------
# Build QUBO
# ---------------------------------------------------------

def build_qubo(data):
    """
    Build the FloodSafe QUBO.

    The optimization problem is:

        minimize:
            - population reward
            + flood-risk penalty
            + overlap penalty
            + exactly-K penalty

    Constraint:

        sum(x_i) = K

    where x_i is binary.
    """

    n = data["num_sites"]
    k = data["k"]

    population = data["population"]
    flood_risk = data["flood_risk"]
    overlap = data["overlap"]

    # Linear coefficients
    linear = [0.0] * n

    # Quadratic coefficients
    quadratic = {}

    # Constant term
    constant = CONSTRAINT_PENALTY * (k ** 2)

    # -----------------------------------------------------
    # Population + risk
    # -----------------------------------------------------

    for i in range(n):

        linear[i] += (
            -POPULATION_WEIGHT * population[i]
            + RISK_WEIGHT * flood_risk[i]
        )

    # -----------------------------------------------------
    # Overlap penalty
    # -----------------------------------------------------

    for (i, j), value in overlap.items():

        quadratic[(i, j)] = (
            OVERLAP_WEIGHT * value
        )

    # -----------------------------------------------------
    # Exactly-K constraint
    #
    # A(sum(x_i) - K)^2
    #
    # = A sum(x_i)
    #   + 2A sum(x_i x_j)
    #   - 2AK sum(x_i)
    #   + AK^2
    #
    # Since x_i^2 = x_i:
    #
    # Linear contribution:
    #       A - 2AK
    #
    # Quadratic contribution:
    #       2A
    # -----------------------------------------------------

    for i in range(n):

        linear[i] += (
            CONSTRAINT_PENALTY
            - 2 * CONSTRAINT_PENALTY * k
        )

    for i in range(n):
        for j in range(i + 1, n):

            if (i, j) in quadratic:
                quadratic[(i, j)] += (
                    2 * CONSTRAINT_PENALTY
                )
            else:
                quadratic[(i, j)] = (
                    2 * CONSTRAINT_PENALTY
                )

    return constant, linear, quadratic


# ---------------------------------------------------------
# Convert QUBO to Ising Hamiltonian
# ---------------------------------------------------------

def qubo_to_ising(constant, linear, quadratic):
    """
    Convert:

        C(x) = c + sum(a_i x_i)
                  + sum(b_ij x_i x_j)

    into an Ising Hamiltonian using:

        x_i = (1 - Z_i) / 2
    """

    n = len(linear)

    # Identity contribution
    identity = constant

    # Z coefficients
    z_coefficients = [0.0] * n

    # -----------------------------------------------------
    # Linear terms
    # -----------------------------------------------------

    for i in range(n):

        a = linear[i]

        identity += a / 2.0
        z_coefficients[i] -= a / 2.0

    # -----------------------------------------------------
    # Quadratic terms
    # -----------------------------------------------------

    zz_terms = []

    for (i, j), b in quadratic.items():

        identity += b / 4.0

        z_coefficients[i] -= b / 4.0
        z_coefficients[j] -= b / 4.0

        zz_terms.append((i, j, b / 4.0))

    # -----------------------------------------------------
    # Build SparsePauliOp
    # -----------------------------------------------------

    terms = []

    # Identity term
    if abs(identity) > 1e-12:
        terms.append(("I" * n, identity))

    # Z terms
    for i, coefficient in enumerate(z_coefficients):

        if abs(coefficient) > 1e-12:

            pauli = ["I"] * n
            pauli[i] = "Z"

            # Qiskit uses little-endian Pauli strings
            pauli_string = "".join(reversed(pauli))

            terms.append(
                (pauli_string, coefficient)
            )

    # ZZ terms
    for i, j, coefficient in zz_terms:

        pauli = ["I"] * n

        pauli[i] = "Z"
        pauli[j] = "Z"

        pauli_string = "".join(reversed(pauli))

        terms.append(
            (pauli_string, coefficient)
        )

    return SparsePauliOp.from_list(terms)


# ---------------------------------------------------------
# Complete Hamiltonian builder
# ---------------------------------------------------------

def build_cost_hamiltonian(data):

    constant, linear, quadratic = build_qubo(data)

    hamiltonian = qubo_to_ising(
        constant,
        linear,
        quadratic
    )

    return (
        hamiltonian,
        constant,
        linear,
        quadratic
    )


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    data = get_problem_data()

    hamiltonian, constant, linear, quadratic = (
        build_cost_hamiltonian(data)
    )

    print()
    print("=" * 60)
    print("FloodSafe - QUBO Construction")
    print("=" * 60)

    print()
    print("Number of variables:", data["num_sites"])
    print("Required shelters:", data["k"])

    print()
    print("Constraint penalty:", CONSTRAINT_PENALTY)

    print()
    print("QUBO constant:")
    print(constant)

    print()
    print("Number of linear terms:")
    print(len(linear))

    print()
    print("Number of quadratic terms:")
    print(len(quadratic))

    print()
    print("Ising Hamiltonian:")
    print(hamiltonian)

    print()
    print("Number of qubits:")
    print(hamiltonian.num_qubits)

    print()
    print("FloodSafe QUBO construction completed!")