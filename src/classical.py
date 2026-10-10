# FloodSafe - Classical optimization baseline

from itertools import combinations

from data import get_problem_data


# ---------------------------------------------------------
# Objective weights
# ---------------------------------------------------------

# Higher population coverage is better.
POPULATION_WEIGHT = 1.0

# Flood-risk penalty.
RISK_WEIGHT = 0.35

# Overlapping coverage penalty.
OVERLAP_WEIGHT = 12.0


# ---------------------------------------------------------
# Objective function
# ---------------------------------------------------------

def calculate_objective(selected_sites, data):
    """
    Calculate the FloodSafe objective for a selected set of sites.

    Lower objective value is better.

    Objective =
        - population reward
        + flood-risk penalty
        + overlap penalty
    """

    population = data["population"]
    flood_risk = data["flood_risk"]
    overlap = data["overlap"]

    # Population reward
    population_reward = sum(
        population[i] for i in selected_sites
    )

    # Flood-risk penalty
    risk_penalty = sum(
        flood_risk[i] for i in selected_sites
    )

    # Overlap penalty
    overlap_penalty = 0.0

    selected_sites = list(selected_sites)

    for a in range(len(selected_sites)):
        for b in range(a + 1, len(selected_sites)):
            i = selected_sites[a]
            j = selected_sites[b]

            pair = tuple(sorted((i, j)))

            if pair in overlap:
                overlap_penalty += overlap[pair]

    # Final objective
    objective = (
        -POPULATION_WEIGHT * population_reward
        + RISK_WEIGHT * risk_penalty
        + OVERLAP_WEIGHT * overlap_penalty
    )

    return objective


# ---------------------------------------------------------
# Brute-force solver
# ---------------------------------------------------------

def brute_force_solver(data):
    """
    Evaluate every possible combination of K shelters.

    For 12 sites and K=4:

        C(12,4) = 495 combinations

    This gives us the exact classical optimum.
    """

    num_sites = data["num_sites"]
    k = data["k"]
    sites = data["sites"]

    best_objective = float("inf")
    best_selection = None

    all_results = []

    # Generate every possible K-site combination
    for combination in combinations(range(num_sites), k):

        objective = calculate_objective(
            combination,
            data
        )

        all_results.append(
            (combination, objective)
        )

        if objective < best_objective:
            best_objective = objective
            best_selection = combination

    return best_selection, best_objective, all_results


# ---------------------------------------------------------
# Main test
# ---------------------------------------------------------

if __name__ == "__main__":

    data = get_problem_data()

    best_selection, best_objective, all_results = (
        brute_force_solver(data)
    )

    print()
    print("=" * 55)
    print("FloodSafe - Classical Brute-Force Baseline")
    print("=" * 55)

    print()
    print("Candidate sites:", data["num_sites"])
    print("Shelters required:", data["k"])

    print()
    print(
        "Combinations evaluated:",
        len(all_results)
    )

    print()
    print("Optimal shelter locations:")

    for index in best_selection:
        print(
            f"  {index}: {data['sites'][index]}"
        )

    print()
    print(
        "Classical objective:",
        round(best_objective, 3)
    )

    print()
    print("Selected-site population:")

    population_total = sum(
        data["population"][i]
        for i in best_selection
    )

    print(
        "  Population score:",
        population_total
    )

    print()
    print("Selected-site flood risk:")

    risk_total = sum(
        data["flood_risk"][i]
        for i in best_selection
    )

    print(
        "  Risk score:",
        risk_total
    )

    print()
    print("FloodSafe classical baseline completed!")