import numpy as np

from trustlens.calibration import expected_calibration_error


def test_perfectly_grouped_probabilities_have_zero_calibration_error() -> None:
    actual = np.array([0, 0, 1, 1])
    probabilities = np.array([0.0, 0.0, 1.0, 1.0])

    assert expected_calibration_error(actual, probabilities) == 0.0
