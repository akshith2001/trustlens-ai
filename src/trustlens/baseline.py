"""Majority-class benchmark for the credit-risk case study."""

from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split

from trustlens.data import CreditDataset
from trustlens.evaluation import ClassificationMetrics, evaluate_predictions

TEST_SIZE = 0.20
RANDOM_STATE = 42


def evaluate_majority_baseline(dataset: CreditDataset) -> ClassificationMetrics:
    """Train and evaluate a stratified majority-class baseline."""

    features_train, features_test, target_train, target_test = train_test_split(
        dataset.features,
        dataset.target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=dataset.target,
    )
    model = DummyClassifier(strategy="most_frequent")
    model.fit(features_train, target_train)
    predictions = model.predict(features_test)
    return evaluate_predictions(target_test.to_numpy(), predictions)
