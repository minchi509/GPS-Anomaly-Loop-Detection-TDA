import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# =========================
# CONFIG
# =========================

DATA_DIR = "generate_data_TV2"
OUTPUT_DIR = "results"
FIGURE_DIR = "figures"

H1_FILE = os.path.join(OUTPUT_DIR, "h1_persistence_results.csv")
CENTROID_FILE = os.path.join(OUTPUT_DIR, "centroid_estimations.csv")

SCENARIOS = ["KC1", "KC2", "KC3"]
THRESHOLD = 0.15


# =========================
# BASIC SETUP
# =========================

def ensure_folders():
    os.makedirs(FIGURE_DIR, exist_ok=True)


def load_h1_results():
    if not os.path.exists(H1_FILE):
        raise FileNotFoundError(f"Không tìm thấy file H1: {H1_FILE}")

    rows = []

    with open(H1_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "scenario",
            "pair_id",
            "birth",
            "death",
            "persistence",
            "is_significant",
            "threshold",
        }

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(f"File CSV thiếu các cột: {missing_columns}")

        for row in reader:
            rows.append({
                "scenario": row["scenario"],
                "pair_id": int(row["pair_id"]),
                "birth": float(row["birth"]),
                "death": float(row["death"]),
                "persistence": float(row["persistence"]),
                "is_significant": str(row["is_significant"]).lower() in ["true", "1", "yes"],
                "threshold": float(row["threshold"]),
            })

    return rows


def load_points(scenario):
    path = os.path.join(DATA_DIR, f"{scenario}.npy")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy file GPS: {path}")

    points = np.load(path)

    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError(f"{path} phải có shape (N, 2)")

    return points


def load_centroid_estimations():
    if not os.path.exists(CENTROID_FILE):
        print("Không tìm thấy centroid_estimations.csv. GPS map sẽ không vẽ vòng đỏ.")
        return []

    rows = []

    with open(CENTROID_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "scenario",
            "loop_id",
            "centroid_x",
            "centroid_y",
            "radius",
            "persistence",
        }

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(f"File centroid_estimations.csv thiếu các cột: {missing_columns}")

        for row in reader:
            rows.append({
                "scenario": row["scenario"],
                "loop_id": int(row["loop_id"]),
                "centroid_x": float(row["centroid_x"]),
                "centroid_y": float(row["centroid_y"]),
                "radius": float(row["radius"]),
                "persistence": float(row["persistence"]),
            })

    return rows


def filter_by_scenario(rows, scenario):
    return [row for row in rows if row["scenario"] == scenario]


def plot_trajectories(trajectories):
    """
    Vẽ scatter plot cho các trajectory GPS ban đầu.

    Input:
        trajectories: dict[str, np.ndarray]
        Ví dụ:
        {
            "KC1": kc1_points,
            "KC2": kc2_points,
            "KC3": kc3_points,
        }

    Mỗi array phải có shape (N, 2).
    """

    ensure_folders()

    for scenario, points in trajectories.items():
        if points.ndim != 2 or points.shape[1] != 2:
            raise ValueError(f"{scenario} phải có shape (N, 2)")

        x = points[:, 0]
        y = points[:, 1]

        plt.figure(figsize=(7, 6))

        plt.scatter(
            x,
            y,
            color="#6666F6",
            edgecolors="#2A2AF5",
            s=25,
            alpha=0.85,
            label="GPS points",
        )

        plt.title(f"{scenario} - GPS Points Scatter Plot")
        plt.xlabel("x (Simulated longitude)")
        plt.ylabel("y (Simulated latitude)")
        plt.axis("equal")
        plt.grid(True, alpha=0.3)
        plt.legend(loc="lower right")

        output_path = os.path.join(FIGURE_DIR, f"{scenario}_scatter_plot.png")
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        print(f"Saved: {output_path}")


# =========================
# PLOT BARCODE
# =========================

def plot_barcode(h1_df, scenario):
    """
    Vẽ H1 barcode cho một kịch bản.

    Mỗi dòng ngang là một H1 pair.
    Trục x là filtration value.
    Đoạn từ birth đến death biểu diễn thời gian tồn tại của vòng.

    Màu đỏ: significant loop, persistence > 0.15
    Màu xám: noise loop, persistence <= 0.15
    """

    scenario_df = filter_by_scenario(h1_df, scenario)


    plt.figure(figsize=(9, 5))

    for index, row in enumerate(scenario_df):
        birth = row["birth"]
        death = row["death"]
        is_significant = row["is_significant"]

        color = "red" if is_significant else "gray"

        plt.hlines(
            y=index,
            xmin=birth,
            xmax=death,
            color=color,
            linewidth=3,
        )

    plt.title(f"{scenario} - H1 Barcode")
    plt.xlabel("Filtration value")
    plt.ylabel("H1 pair index")
    plt.yticks(range(len(scenario_df)))
    plt.grid(True, alpha=0.3)
    

    legend_elements = [
        Line2D([0], [0], color='red', lw=3, label='Significant loop (pers > 0.15)'),
        Line2D([0], [0], color='gray', lw=3, label='Noise loop')
    ]
    plt.legend(handles=legend_elements, loc="upper right")

    

    output_path = os.path.join(FIGURE_DIR, f"{scenario}_barcode.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")


# =========================
# PLOT PERSISTENCE DIAGRAM
# =========================

def plot_persistence_diagram(h1_df, scenario):
    """
    Vẽ persistence diagram cho một kịch bản.

    Mỗi điểm là một H1 pair: (birth, death).
    Điểm càng xa đường chéo death = birth thì persistence càng lớn.

    Màu đỏ: significant loop, persistence > 0.15
    Màu xám: noise loop, persistence <= 0.15
    """

    scenario_df = filter_by_scenario(h1_df, scenario)

    plt.figure(figsize=(6, 6))

    for row in scenario_df:
        birth = row["birth"]
        death = row["death"]
        is_significant = row["is_significant"]

        color = "red" if is_significant else "gray"

        plt.scatter(
            birth,
            death,
            color=color,
            s=70,
            alpha=0.8,
        )

    birth_values = [row["birth"] for row in scenario_df]
    death_values = [row["death"] for row in scenario_df]

    min_value = min(min(birth_values), min(death_values))
    max_value = max(max(birth_values), max(death_values))

    padding = (max_value - min_value) * 0.1
    if padding == 0:
        padding = 0.05

    min_axis = min_value - padding
    max_axis = max_value + padding

    plt.plot(
        [min_axis, max_axis],
        [min_axis, max_axis],
        color="black",
        linestyle="--",
        linewidth=1,
        alpha=0.6,
    )

    plt.title(f"{scenario} - H1 Persistence Diagram")
    plt.xlabel("Birth")
    plt.ylabel("Death")
    plt.xlim(min_axis, max_axis)
    plt.ylim(min_axis, max_axis)
    plt.grid(True, alpha=0.3)


    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="red",
            markersize=8,
            label="Significant loop (pers > 0.15)",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="gray",
            markersize=8,
            label="Noise loop",
        ),
    ]

    plt.legend(handles=legend_elements, loc="lower right")


    output_path = os.path.join(FIGURE_DIR, f"{scenario}_persistence_diagram.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")


# =========================
# PLOT GPS MAP
# =========================

def plot_gps_map(h1_df, centroid_df, scenario):
    """
    Vẽ bản đồ GPS cho từng kịch bản.

    Màu xanh: toàn bộ GPS trajectory và GPS points.
    Vùng tròn đỏ trong suốt: vòng significant ước lượng từ centroid/radius của TV6.
    Dấu chấm đỏ: tâm vòng ước lượng.

    """

    points = load_points(scenario)

    scenario_h1 = filter_by_scenario(h1_df, scenario)
    significant_count = sum(1 for row in scenario_h1 if row["is_significant"])

    plt.figure(figsize=(7, 6))

    x = points[:, 0]
    y = points[:, 1]

    gps_fill_color = "#6666F6"
    gps_edge_color = "#2A2AF5"

    plt.plot(
        x,
        y,
        color=gps_fill_color,
        linewidth=1.2,
        alpha=0.85,
        marker="o",
        markersize=3.5,
        markerfacecolor=gps_fill_color,
        markeredgecolor=gps_edge_color,
        markeredgewidth=1.0,
    )

    scenario_loops = [
        row for row in centroid_df
        if row["scenario"] == scenario and row["persistence"] > THRESHOLD
    ]

    for row in scenario_loops:
        centroid_x = row["centroid_x"]
        centroid_y = row["centroid_y"]
        radius = row["radius"]

        circle = plt.Circle(
            (centroid_x, centroid_y),
            radius,
            facecolor="red",
            edgecolor="none",
            fill=True,
            alpha=0.25,
        )

        plt.gca().add_patch(circle)

        plt.scatter(
            centroid_x,
            centroid_y,
            color="darkred",
            marker="o",
            s=35,
            linewidths=0.8,
        )

    loop_word = "loop" if significant_count == 1 else "loops"

    plt.title(f"{scenario} - GPS Map ({significant_count} significant {loop_word})")
    plt.xlabel("x (Simulated longitude)")
    plt.ylabel("y (Simulated latitude)")
    plt.axis("equal")
    plt.grid(True, alpha=0.3)

    legend_elements = [
        Line2D(
            [0],
            [0],
            color=gps_fill_color,
            linewidth=1.2,
            marker="o",
            markersize=5,
            markerfacecolor=gps_fill_color,
            markeredgecolor=gps_edge_color,
            markeredgewidth=1.0,
            label="GPS trajectory",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            markersize=12,
            markerfacecolor="red",
            markeredgecolor="none",
            alpha=0.25,
            label="Estimated loop\n(pers > 0.15)",
        ),
        Line2D(
            [0],
            [0],
            color="darkred",
            marker="o",
            linestyle="None",
            markersize=6,
            markeredgewidth=0.8,
            label="Estimated centroid",
        ),
    ]

    plt.legend(handles=legend_elements, loc="lower right")

    output_path = os.path.join(FIGURE_DIR, f"{scenario}_gps_map.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")

# =========================
# SUMMARY
# =========================

def print_summary(h1_df):
    print("\n===== H1 Persistence Summary =====")

    for scenario in SCENARIOS:
        scenario_df = filter_by_scenario(h1_df, scenario)

        total_pairs = len(scenario_df)
        significant_pairs = sum(1 for row in scenario_df if row["is_significant"])
        max_persistence = max(row["persistence"] for row in scenario_df)

        print(
            f"{scenario}: "
            f"total H1 pairs = {total_pairs}, "
            f"significant loops = {significant_pairs}, "
            f"max persistence = {max_persistence:.6f}"
        )


# =========================
# MAIN
# =========================

def main():
    ensure_folders()

    h1_df = load_h1_results()
    centroid_df = load_centroid_estimations()

    trajectories = {
        scenario: load_points(scenario)
        for scenario in SCENARIOS
    }

    plot_trajectories(trajectories)
    
    print_summary(h1_df)

    for scenario in SCENARIOS:
        plot_barcode(h1_df, scenario)
        plot_persistence_diagram(h1_df, scenario)
        plot_gps_map(h1_df, centroid_df, scenario)

    print("\nDone. All figures are saved in the figures/ folder.")


if __name__ == "__main__":
    main()