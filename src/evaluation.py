# FloodSafe - Quantum vs Classical Evaluation
# Compares classical optimum with QAOA at different depths.

from data import get_problem_data
from classical import brute_force_solver, calculate_objective
from qaoa_solver import run_qaoa


def evaluate():
    data = get_problem_data()

    print("=" * 70)
    print("FloodSafe - Quantum vs Classical Evaluation")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Classical baseline
    # ---------------------------------------------------------
    print("\nRunning classical brute-force solver...")

    classical_selection, classical_objective, all_results = (
        brute_force_solver(data)
    )

    print("\nCLASSICAL BASELINE")
    print("-" * 40)

    print("Selected sites:")
    for i in classical_selection:
        print(f"  {i}: {data['sites'][i]}")

    print(f"Objective: {classical_objective:.2f}")
    print(f"Combinations checked: {len(all_results)}")

    # ---------------------------------------------------------
    # 2. QAOA experiments
    # ---------------------------------------------------------
    results = []

    for depth in [1, 2, 3]:

        print("\n" + "=" * 70)
        print(f"Running QAOA with depth p={depth}")
        print("=" * 70)

        result = run_qaoa(data, depth=depth)

        # Get selected sites returned by QAOA
        selected_sites = result["selected_sites"]

        # Calculate the real FloodSafe objective
        qaoa_objective = calculate_objective(
            selected_sites,
            data
        )

        # Compare with classical optimum
        objective_gap = (
            qaoa_objective - classical_objective
        )

        results.append({
            "depth": depth,
            "objective": qaoa_objective,
            "gap": objective_gap,
            "feasibility_rate": result["feasibility_rate"],
            "selected_sites": selected_sites,
            "selected_names": [
                data["sites"][i]
                for i in selected_sites
            ],
        })

    # ---------------------------------------------------------
    # 3. Final comparison
    # ---------------------------------------------------------
    print("\n")
    print("=" * 70)
    print("FINAL COMPARISON")
    print("=" * 70)

    print(
        f"{'Method':<15}"
        f"{'Objective':<15}"
        f"{'Gap':<12}"
        f"{'Feasible':<12}"
    )

    print("-" * 70)

    print(
        f"{'Classical':<15}"
        f"{classical_objective:<15.2f}"
        f"{0.00:<12.2f}"
        f"{'Yes':<12}"
    )

    for result in results:
        print(
            f"{'QAOA p=' + str(result['depth']):<15}"
            f"{result['objective']:<15.2f}"
            f"{result['gap']:<12.2f}"
            f"{'Yes':<12}"
        )

    # ---------------------------------------------------------
    # 4. Selected sites comparison
    # ---------------------------------------------------------
    print("\n")
    print("=" * 70)
    print("SELECTED SHELTER LOCATIONS")
    print("=" * 70)

    print("\nClassical optimum:")
    print(", ".join(
        data["sites"][i]
        for i in classical_selection
    ))

    for result in results:
        print(f"\nQAOA p={result['depth']}:")
        print(", ".join(result["selected_names"]))

    # ---------------------------------------------------------
    # 5. Best QAOA result
    # ---------------------------------------------------------
    best_qaoa = min(
        results,
        key=lambda x: x["objective"]
    )

    print("\n")
    print("=" * 70)
    print("BEST QAOA RESULT")
    print("=" * 70)

    print(f"Best depth: p={best_qaoa['depth']}")
    print(f"Objective: {best_qaoa['objective']:.2f}")
    print(f"Classical objective: {classical_objective:.2f}")
    print(f"Objective gap: {best_qaoa['gap']:.2f}")

    print("\nSelected shelters:")
    for site in best_qaoa["selected_names"]:
        print(f"  - {site}")

    print("\nEvaluation completed successfully!")
    print("=" * 70)

    return {
        "classical_objective": classical_objective,
        "classical_selection": classical_selection,
        "qaoa_results": results,
    }


if __name__ == "__main__":
    evaluate()