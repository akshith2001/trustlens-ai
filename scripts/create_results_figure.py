"""Create a publication-style summary from the locked JSON result."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


RESULT_PATH = Path("results/final_test_metrics.json")
FIGURE_PATH = Path("figures/final_test_summary.png")


def main() -> None:
    if not RESULT_PATH.exists():
        raise SystemExit("Locked final result does not exist")
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    figure, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    metrics = ["Balanced\naccuracy", "Precision", "Recall", "F1"]
    values = [
        result["balanced_accuracy"],
        result["precision"],
        result["recall"],
        result["f1"],
    ]
    bars = axes[0].bar(metrics, values, color=["#315C8C", "#D9822B", "#2D7D46", "#7253A3"])
    axes[0].set_ylim(0, 1)
    axes[0].set_ylabel("Score")
    axes[0].set_title("Locked final-test performance")
    axes[0].bar_label(bars, labels=[f"{value:.3f}" for value in values], padding=3)

    matrix = np.array(
        [
            [result["true_negatives"], result["false_positives"]],
            [result["false_negatives"], result["true_positives"]],
        ]
    )
    axes[1].imshow(matrix, cmap="Blues")
    axes[1].set_xticks([0, 1], labels=["Predicted lower", "Predicted higher"])
    axes[1].set_yticks([0, 1], labels=["Actual lower", "Actual higher"])
    axes[1].set_title("Confusion matrix")
    for row in range(2):
        for column in range(2):
            axes[1].text(
                column,
                row,
                str(matrix[row, column]),
                ha="center",
                va="center",
                fontsize=14,
                color="white" if matrix[row, column] > matrix.max() / 2 else "black",
            )

    figure.suptitle("TrustLens AI — governed credit-risk research prototype", fontsize=14)
    figure.text(
        0.5,
        0.01,
        "Historical research data only; not for real lending decisions.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=[0, 0.04, 1, 0.94])
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURE_PATH, dpi=180, bbox_inches="tight")
    plt.close(figure)
    print(f"Figure written to {FIGURE_PATH}")


if __name__ == "__main__":
    main()
