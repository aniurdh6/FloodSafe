# Qiskit Fall Fest 2026 — Project Submission Template
**IIIT Kottayam Quantum Hackathon (24-Hour Sprint)**

# Project Title

# FloodSafe — Quantum Optimization for Flood Relief Shelter Placement

## Project Metadata

* **Project Title:** `FloodSafe — Quantum Optimization for Flood Relief Shelter Placement`
* **Team Name:** `ASTRA`
* **Chosen Track:** `Track 2: Open-Domain Optimization & Real-World Solvers`
* **Video Presentation Link:** `[Insert Video Link Here]`
* **Live Demo Timestamp in Video:** `[MM:SS]`

### Team Members (Max 4 members)

| Name | Email | GitHub Username |
| :--- | :--- | :--- |
| `Anirudh` | `anirudhkarthinksane@gmail.com` | `aniurdh6` |

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
  * **Key Gates Used:** `H, RZ, RZZ, RX, CX`
  * **Primitives / Quantum Tools Used:** `Qiskit QuantumCircuit, Statevector, SparsePauliOp`
  * **Classical Optimizer:** `SciPy COBYLA`
  * **Other Technologies Used:** `Python, NumPy, SciPy, Pandas, Matplotlib, Streamlit`

### QAOA Circuit Construction

```python
from qiskit import QuantumCircuit


def build_qaoa_circuit(cost_hamiltonian, gamma, beta, depth=1):
    n = cost_hamiltonian.num_qubits
    qc = QuantumCircuit(n)

    # Initial equal superposition
    for q in range(n):
        qc.h(q)

    # QAOA layers
    for layer in range(depth):
        g = gamma[layer]
        b = beta[layer]

        # Cost Hamiltonian evolution
        for pauli, coeff in zip(
            cost_hamiltonian.paulis,
            cost_hamiltonian.coeffs
        ):
            label = pauli.to_label()

            if abs(coeff.real) < 1e-12:
                continue

            z_qubits = [
                q for q, p in enumerate(label)
                if p == "Z"
            ]

            # Single-qubit Z term
            if len(z_qubits) == 1:
                q = z_qubits[0]
                qc.rz(2 * g * coeff.real, q)

            # Two-qubit ZZ term
            elif len(z_qubits) == 2:
                q1, q2 = z_qubits

                qc.cx(q1, q2)
                qc.rzz(2 * g * coeff.real, q1, q2)
                qc.cx(q1, q2)

        # X mixer
        for q in range(n):
            qc.rx(2 * b, q)

    return qc

    3. Mathematical Formulation
Decision Variables
For each candidate shelter site \(i\):
\[
x_i \in \{0,1\}
\]
where:
- \(x_i = 1\): shelter is selected
- \(x_i = 0\): shelter is not selected
There are 12 candidate sites and exactly 4 shelters must be selected.
Objective Function
FloodSafe minimizes the following objective:
\[
C(x) =
-P(x)
+\lambda_R R(x)
+\lambda_O O(x)
+A\left(\sum_i x_i-K\right)^2
\]
where:
- \(P(x)\) = population reward
- \(R(x)\) = flood-risk penalty
- \(O(x)\) = redundant-coverage / overlap penalty
- \(K=4\) = required number of shelters
- \(A\) = constraint penalty
The implementation uses:
- Population weight = 1.0
- Flood-risk weight = 0.35
- Overlap weight = 12.0
- Constraint penalty = 50.0
The exact-K constraint expands into linear and quadratic QUBO terms.
QUBO Representation
The resulting QUBO contains:
- 12 binary variables
- 12 linear terms
- 66 quadratic terms
- Exact-selection constraint
- Constant offset
The QUBO is converted into an Ising Hamiltonian using:
\[
x_i = \frac{1-Z_i}{2}
\]
The resulting Hamiltonian is represented using Qiskit's SparsePauliOp.
Problem Data
The prototype contains 12 candidate locations:
1. Aluva
2. Perumbavoor
3. Angamaly
4. Kalamassery
5. North Paravur
6. Muvattupuzha
7. Kothamangalam
8. Thrippunithura
9. Ernakulam
10. Cherthala
11. Changanassery
12. Kuttanad
The data includes:
- Synthetic population scores
- Synthetic flood-risk scores
- Pairwise overlap relationships
- Kerala-inspired geographic coordinates
4. Classical Baseline
To evaluate the quantum approach, FloodSafe uses an exact classical brute-force solver.
Because the problem requires selecting exactly 4 sites from 12 candidates, the number of feasible combinations is:
\[
\binom{12}{4}=495
\]
The classical solver evaluates all 495 feasible combinations and identifies the global optimum.
Classical Optimal Solution
The exact classical solution selects:
- Aluva
- Angamaly
- Ernakulam
- Kuttanad
Classical objective:
-265.45

This exact classical result provides the reference point for evaluating the QAOA solutions.
5. Experimental Results
FloodSafe was evaluated using QAOA with different circuit depths.
QAOA Depth	Selected Shelters	Objective	Objective Gap	Feasible	Feasibility Rate
p = 1	Aluva, Angamaly, Ernakulam, Changanassery	-251.85	13.60	Yes	10.94%
p = 2	Aluva, Angamaly, Ernakulam, Changanassery	-251.85	13.60	Yes	10.94%
p = 3	Angamaly, Thrippunithura, Ernakulam, Kuttanad	-261.90	3.55	Yes	18.02%


The best observed QAOA result was obtained at depth \(p=3\), achieving an objective gap of approximately 3.55 from the exact classical optimum.
Interpretation
Increasing the QAOA depth improved the observed solution quality for this instance.
The p=3 solution is close to the classical optimum while remaining a feasible four-shelter configuration. However, QAOA is probabilistic, so repeated executions can produce different sampled solutions.
The feasibility rate represents the fraction of sampled bitstrings satisfying the exact four-shelter requirement.
6. Results Comparison
The classical solver guarantees the optimal solution for this small 12-site instance because it exhaustively evaluates all 495 feasible combinations.
QAOA does not provide the same optimality guarantee. Instead, it generates a probability distribution over candidate configurations and uses a classical optimizer to tune the circuit parameters.
This makes the comparison useful for demonstrating how a quantum optimization workflow behaves on a realistic combinatorial formulation rather than claiming quantum advantage.
Key Result
The best observed QAOA result achieved:
QAOA objective       = -261.90
Classical optimum    = -265.45
Objective gap        = 3.55
Feasible solution    = True
Feasibility rate     = 18.02%

Solution Comparison
Method	Selected Sites	Objective
Classical Exact	Aluva, Angamaly, Ernakulam, Kuttanad	-265.45
QAOA p=3	Angamaly, Thrippunithura, Ernakulam, Kuttanad	-261.90


The QAOA solution is different from the classical optimum but remains a feasible four-shelter configuration with a relatively small objective gap.
7. Application / Live Demo
FloodSafe includes a Streamlit dashboard for interactive exploration.
The dashboard allows the user to:
1. View the candidate shelter locations.
2. Inspect population and flood-risk values.
3. Configure optimization parameters.
4. Run the QAOA solver.
5. Compare QAOA against the classical optimum.
6. Inspect the selected shelter locations.
7. Observe objective gap and feasibility metrics.
Run the Application
streamlit run app.py

The dashboard is designed as a decision-support prototype rather than an operational disaster-management system.
8. Project Structure
FloodSafe/
│
├── app.py
├── README.md
├── requirements.txt
│
├── src/
│   ├── data.py
│   ├── classical.py
│   ├── qubo.py
│   ├── qaoa_solver.py
│   └── evaluation.py
│
├── notebooks/
│   └── FloodSafe_QAOA.ipynb
│
└── references/
    └── track-2-optimization/
        ├── README.md
        └── track2_optimization_QAOA.ipynb

9. Technologies Used
Software
- Python
- Qiskit
- NumPy
- SciPy
- Pandas
- Matplotlib
- NetworkX
- Streamlit
- Jupyter Notebook
Quantum Components
- QuantumCircuit
- Statevector
- SparsePauliOp
- QAOA
- QUBO formulation
- Ising Hamiltonian
- COBYLA classical optimization
Classical Components
- Exact brute-force enumeration
- Combinatorial optimization
- Objective evaluation
- Feasibility analysis
- QAOA result benchmarking
10. Limitations
This project is a research and educational prototype.
Data Limitation
The population, flood-risk, overlap, and geographic coordinates are synthetic and Kerala-inspired. They are not official government or historical disaster datasets.
Classical Simulation Limitation
The current implementation uses statevector simulation on a classical computer. Therefore, the experiment does not demonstrate a real quantum hardware advantage.
Problem Size
The demonstration uses only 12 candidate sites so that exact classical enumeration is computationally practical.
QAOA Limitation
QAOA is probabilistic and its performance depends on:
- Circuit depth
- Parameter optimization
- Mixer design
- Penalty scaling
- Number of measurements
- Random sampling
Therefore, a single QAOA run should not be interpreted as a guaranteed global optimum.
11. Future Work
Future versions of FloodSafe could include:
- Larger real-world disaster-planning instances
- Real population and flood-risk datasets
- Execution on IBM Quantum hardware
- Warm-start QAOA
- Constraint-preserving XY mixers
- Dicke-state initialization for fixed-cardinality optimization
- Comparison with greedy and integer-programming solvers
- Multi-period emergency shelter planning
- Dynamic shelter relocation based on changing flood conditions
- Integration of road-network accessibility and travel time
- Larger-scale benchmark experiments
- Hardware noise and error-mitigation studies
12. Conclusion
FloodSafe demonstrates how a real-world emergency resource-allocation problem can be transformed into a QUBO and explored using a QAOA-based quantum optimization workflow.
The project connects problem formulation, QUBO construction, Ising Hamiltonian encoding, quantum circuit execution, classical parameter optimization, and classical benchmarking in a single end-to-end pipeline.
For the 12-site synthetic instance, the exact classical solver found an objective of -265.45, while the best observed QAOA configuration achieved -261.90 with a feasible four-shelter selection.
The objective gap between the best observed QAOA solution and the exact classical optimum was 3.55.
The goal of the project is not to claim quantum advantage, but to demonstrate a rigorous and reproducible workflow for exploring quantum optimization on a practical decision-making problem.

13. How to Run
1. Clone the repository
git clone https://github.com/aniurdh6/FloodSafe.git
cd FloodSafe

2. Create and activate the virtual environment
Windows:
python -m venv .venv
.venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Run the Streamlit application
streamlit run app.py

5. Run the Jupyter notebook
jupyter notebook

Then open:
notebooks/FloodSafe_QAOA.ipynb

14. Reproducibility
All experiments use the source code and synthetic dataset contained in this repository.
The notebook records the classical baseline and QAOA experiments, including:
- Selected shelters
- Objective values
- Feasibility
- Feasibility rate
- Objective gap
- QAOA circuit depth
Because QAOA sampling is probabilistic, repeated executions can produce different sampled solutions.
15. Hackathon Submission
GitHub Repository:
https://github.com/aniurdh6/FloodSafe
Video Presentation:
[Insert Video Link Here]
Live Demo Timestamp:
[MM:SS]
16. Attribution
This project was developed for the Qiskit Fall Fest 2026 — IIIT Kottayam Quantum Hackathon.
Qiskit is used as the core quantum-computing framework for the optimization workflow.
The project team understands and takes responsibility for the implementation, mathematical formulation, experimental methodology, and reported results.

### After pasting

Do **only these two things** now:

1. Press **`Ctrl + A`** inside `README.md`.
2. Paste the complete content above.
3. Press **`Ctrl + S`**.

Then **send me a screenshot of the README**. I'll check whether the Markdown rendered correctly before we make the next change.