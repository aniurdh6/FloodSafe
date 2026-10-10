# Qiskit Fall Fest 2026 — Project Submission Template
**IIIT Kottayam Quantum Hackathon (24-Hour Sprint)**

# Project Title

# FloodSafe — Quantum Optimization for Flood Relief Shelter Placement

## Project Metadata

* **Project Title:** `FloodSafe — Quantum Optimization for Flood Relief Shelter Placement`
* **Team Name:** `[ASTRA]`
* **Chosen Track:** `Track 2: Open-Domain Optimization & Real-World Solvers`
* **Video Presentation Link:** `[Insert Video Link Here]`
* **Live Demo Timestamp in Video:** `[MM:SS]`

### Team Members (Max 4 members)

| Name | Email | GitHub Username |
| :--- | :--- | :--- |
| `Anirudh` | `[anirudhkarthinksane@gmail.com]` | `aniurdh6` |

---

## 1. Project Overview & Motivation

* **Summary (3–4 sentences):**  
  `FloodSafe is a quantum optimization prototype for selecting emergency flood-relief shelter locations. The system considers 12 synthetic Kerala-inspired candidate locations and selects exactly 4 shelters while balancing population coverage, flood risk, and redundant coverage between nearby locations. The problem is formulated as a Quadratic Unconstrained Binary Optimization (QUBO) model and converted into an Ising cost Hamiltonian for QAOA. The quantum solution is compared against an exact classical brute-force solver over all 495 possible 4-site combinations.`

* **Why this problem / game?**  
  `Flood relief planning is a practical resource-allocation problem where emergency planners must make decisions under limited resources. Selecting poorly distributed or high-risk shelters can reduce the effectiveness of emergency response. FloodSafe demonstrates how a real-world planning dilemma can be formulated as a combinatorial optimization problem and explored using quantum optimization techniques.`

  `The data used in this prototype is synthetic and Kerala-inspired and does not represent official historical flood or population data.`

---

## 2. Quantum Architecture & Mechanics

* **Core Quantum Principles Used:**  
  `FloodSafe uses quantum superposition, phase evolution, interference, and the Quantum Approximate Optimization Algorithm (QAOA). The initial Hadamard layer places the 12-qubit system into a superposition of possible shelter configurations. The cost Hamiltonian encodes population reward, flood-risk penalties, redundant-coverage penalties, and an exact-K constraint. QAOA alternates cost and mixer operations to concentrate probability toward low-cost configurations.`

* **How the Quantum Circuit is Integrated:**  
  `Each candidate shelter corresponds to one binary decision variable and one qubit. A qubit state of |1> represents selecting a shelter, while |0> represents not selecting it.`

  `The optimization objective contains population reward, flood-risk penalties, overlap penalties, and a constraint enforcing the selection of exactly four shelters.`

  `The QUBO is converted to an Ising Hamiltonian using x_i = (1 - Z_i) / 2 and represented using Qiskit's SparsePauliOp. QAOA then applies parameterized cost and mixer layers. The resulting quantum state is sampled and feasible four-shelter configurations are evaluated using the original objective.`

* **Circuit Details:**
  * **Number of Qubits:** `12`
  * **Key Gates Used:** `H, RZ, RZZ, RX`
  * **Primitives / Quantum Tools Used:** `Qiskit QuantumCircuit, Statevector, SparsePauliOp`
  * **Classical Optimizer:** `SciPy COBYLA`
  * **Other Technologies Used:** `Python, NumPy, SciPy, Pandas, Matplotlib, Streamlit`

```python
from qiskit import QuantumCircuit

def build_qaoa_circuit(cost_hamiltonian, gamma, beta, depth=1):
    n = cost_hamiltonian.num_qubits

    qc = QuantumCircuit(n)

    # Initial superposition
    for q in range(n):
        qc.h(q)

    # QAOA layers
    for layer in range(depth):
        g = gamma[layer]
        b = beta[layer]

        # Cost and mixer operations
        # are constructed from the Ising Hamiltonian
        # and applied to the quantum circuit.

        for q in range(n):
            qc.rx(2 * b, q)

    return qc