import pandas as pd

from NetworkSecurity.utils.main_utils.utils import load_object
from NetworkSecurity.utils.ml_utils.model.estimator import NetworkModel


def test_saved_model_predicts_sample_rows():
    df = pd.read_csv("Valid_data/test.csv")
    input_df = df.drop(columns=["Result", "predicted_column"], errors="ignore")

    model = NetworkModel(
        preprocessor=load_object("final_model/preprocessor.pkl"),
        model=load_object("final_model/model.pkl"),
    )

    predictions = model.predict(input_df.head(3))

    assert len(predictions) == 3
    assert set(predictions).issubset({-1, 0, 1, -1.0, 0.0, 1.0})
