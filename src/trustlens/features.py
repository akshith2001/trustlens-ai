"""Feature roles and preprocessing for the credit-risk case study."""

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


NUMERIC_FEATURES = [
    "duration_months",
    "credit_amount",
    "age_years",
]

CATEGORICAL_FEATURES = [
    "checking_account_status",
    "credit_history",
    "purpose",
    "savings",
    "employment_duration",
    "installment_rate",
    "personal_status_sex",
    "other_debtors",
    "present_residence",
    "property",
    "other_installment_plans",
    "housing",
    "number_credits",
    "job",
    "people_liable",
    "telephone",
    "foreign_worker",
]

GOVERNED_EXCLUDED_FEATURES = frozenset(
    {"personal_status_sex", "foreign_worker"}
)


def build_preprocessor(
    excluded_features: frozenset[str] = frozenset(),
) -> ColumnTransformer:
    """Create preprocessing without learning from validation rows in advance."""

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                StandardScaler(),
                [name for name in NUMERIC_FEATURES if name not in excluded_features],
            ),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                [
                    name
                    for name in CATEGORICAL_FEATURES
                    if name not in excluded_features
                ],
            ),
        ]
    )
