# FloodSafe - Synthetic Kerala-inspired shelter placement data

# Number of candidate shelter locations
NUM_SITES = 12

# Number of shelters we want to select
K = 4

# Synthetic candidate locations
SITES = [
    "Aluva",
    "Perumbavoor",
    "Angamaly",
    "Kalamassery",
    "North Paravur",
    "Muvattupuzha",
    "Kothamangalam",
    "Thrippunithura",
    "Ernakulam",
    "Cherthala",
    "Changanassery",
    "Kuttanad",
]

# Estimated population coverage score for each candidate site.
# These are SYNTHETIC values created for the hackathon.
POPULATION = [
    92,
    78,
    85,
    88,
    70,
    65,
    58,
    82,
    95,
    73,
    68,
    90,
]

# Flood-risk score for each location.
# Higher value = higher risk.
# These are SYNTHETIC values, not actual flood statistics.
FLOOD_RISK = [
    72,
    65,
    58,
    48,
    76,
    52,
    38,
    45,
    42,
    68,
    61,
    85,
]

# Coverage-overlap penalty between pairs of shelters.
#
# Example:
# OVERLAP[(0, 1)] = 0.8 means sites 0 and 1
# provide highly redundant coverage.
#
# Only meaningful overlapping pairs are listed.
OVERLAP = {
    (0, 1): 0.80,
    (0, 2): 0.55,
    (0, 3): 0.70,
    (1, 2): 0.65,
    (1, 5): 0.35,
    (2, 3): 0.60,
    (2, 6): 0.30,
    (3, 7): 0.75,
    (3, 8): 0.65,
    (4, 8): 0.35,
    (4, 9): 0.70,
    (5, 6): 0.65,
    (5, 8): 0.40,
    (6, 8): 0.30,
    (7, 8): 0.80,
    (8, 9): 0.45,
    (9, 10): 0.65,
    (9, 11): 0.55,
    (10, 11): 0.50,
}

# Coordinates are synthetic and used only for visualization.
# They roughly resemble a Kerala-inspired geographic layout.
COORDINATES = {
    "Aluva": (76.35, 10.11),
    "Perumbavoor": (76.47, 10.11),
    "Angamaly": (76.39, 10.20),
    "Kalamassery": (76.33, 10.05),
    "North Paravur": (76.22, 10.14),
    "Muvattupuzha": (76.58, 9.98),
    "Kothamangalam": (76.63, 10.06),
    "Thrippunithura": (76.34, 9.95),
    "Ernakulam": (76.29, 9.98),
    "Cherthala": (76.33, 9.68),
    "Changanassery": (76.55, 9.44),
    "Kuttanad": (76.47, 9.40),
}


def get_problem_data():
    """
    Return all FloodSafe optimization data.
    """

    return {
        "num_sites": NUM_SITES,
        "k": K,
        "sites": SITES,
        "population": POPULATION,
        "flood_risk": FLOOD_RISK,
        "overlap": OVERLAP,
        "coordinates": COORDINATES,
    }


if __name__ == "__main__":
    data = get_problem_data()

    print("FloodSafe problem data")
    print("----------------------")
    print("Number of candidate sites:", data["num_sites"])
    print("Number of shelters to select:", data["k"])
    print()

    for i, site in enumerate(data["sites"]):
        print(
            f"{i}: {site:18s} "
            f"Population={data['population'][i]:3d} "
            f"Risk={data['flood_risk'][i]:3d}"
        )

    print()
    print("Number of overlap relationships:", len(data["overlap"]))