# FloodSafe - Classical optimization baseline

from itertools import combinations

try:
    # When imported as src.classical
    from .data import get_problem_data
except ImportError:
    # When run directly as python src/classical.py
    from data import get_problem_data


# Objective weights
POPULATION_WEIGHT = 1.0
RISK_WEIGHT = 0.35
OVERLAP_WEIGHT = 12.0


def calculate_objective(selected_sites, data):
    """
    Calculate the FloodSafe objective.

    Lower objective is better.

    Objective =
        - population reward
        + flood risk penalty
        + overlap/redundancy penalty
    """

    population_reward = sum(
        data["population"][i] for i in selected_sites
    )

    risk_penalty = sum(
        data["flood_risk"][i] for i in selected_sites
    )

    overlap_penalty = 0.0

    selected_set = set(selected_sites)

    for (i, j), overlap_value in data["overlap"].items():
        if i in selected_set and j in selected_set:
            overlap_penalty += overlap_value

    objective = (
        -POPULATION_WEIGHT * population_reward
        + RISK_WEIGHT * risk_penalty
        + OVERLAP_WEIGHT * overlap_penalty
    )

    return objective


def brute_force_solver(data):
    """
    Exhaustively evaluate all combinations of K shelters.

    For 12 candidate sites and K=4:

        C(12,4) = 495 combinations
    """

    num_sites = data["num_sites"]
    k = data["k"]

    all_results = []

    best_objective = float("inf")
    best_selection = None

    for selected_sites in combinations(range(num_sites), k):

        objective = calculate_objective(
            selected_sites,
            data
        )

        all_results.append({
            "selected_sites": selected_sites,
            "objective": objective
        })

        if objective < best_objective:
            best_objective = objective
            best_selection = selected_sites

    return {
        "selected_sites": best_selection,
        "objective": best_objective,
        "all_results": all_results
    }


if __name__ == "__main__":

    data = get_problem_data()

    result = brute_force_solver(data)

    print("FloodSafe Classical Optimization")
    print("=" * 40)

    print("Number of candidate sites:", data["num_sites"])
    print("Number of shelters:", data["k"])

    print("\nOptimal shelter locations:")
    for i in result["selected_sites"]:
        print("-", data["sites"][i])

    print("\nOptimal objective:", result["objective"])

    print(
        "Combinations evaluated:",
        len(result["all_results"])
    )