from trustlens.final_evaluation import FinalTestResult


def test_final_result_is_json_serialisable() -> None:
    result = FinalTestResult(
        model_name="example",
        test_records=10,
        decision_threshold=0.2,
        accuracy=0.7,
        balanced_accuracy=0.6,
        precision=0.5,
        recall=0.8,
        f1=0.6,
        true_negatives=4,
        false_positives=2,
        false_negatives=1,
        true_positives=3,
        weighted_error_cost=7,
        brier_score=0.2,
        log_loss=0.6,
        expected_calibration_error=0.1,
    )

    assert result.to_dict()["model_name"] == "example"
