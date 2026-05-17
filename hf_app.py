import os
import tempfile

import gradio as gr
import pandas as pd

from NetworkSecurity.utils.main_utils.utils import load_object
from NetworkSecurity.utils.ml_utils.model.estimator import NetworkModel


MODEL_PATH = "final_model/model.pkl"
PREPROCESSOR_PATH = "final_model/preprocessor.pkl"
OUTPUT_PATH = "prediction_output/output.csv"


def load_network_model() -> NetworkModel:
    preprocessor = load_object(PREPROCESSOR_PATH)
    model = load_object(MODEL_PATH)
    return NetworkModel(preprocessor=preprocessor, model=model)


network_model = load_network_model()


def predict_csv(file):
    if file is None:
        raise gr.Error("Please upload a CSV file.")

    df = pd.read_csv(file.name)
    input_df = df.drop(columns=["Result", "predicted_column"], errors="ignore")
    predictions = network_model.predict(input_df)

    result_df = df.copy()
    result_df["predicted_column"] = predictions
    result_df["prediction_label"] = result_df["predicted_column"].map(
        {-1: "Legitimate", 0: "Legitimate", 1: "Phishing"}
    )

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    result_df.to_csv(OUTPUT_PATH, index=False)

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".csv", delete=False, prefix="network_security_predictions_"
    )
    result_df.to_csv(temp_file.name, index=False)

    return result_df, temp_file.name


demo = gr.Interface(
    fn=predict_csv,
    inputs=gr.File(label="Upload CSV", file_types=[".csv"]),
    outputs=[
        gr.Dataframe(label="Predictions", interactive=False),
        gr.File(label="Download predictions"),
    ],
    title="Network Security Phishing Detection",
    description=(
        "Upload a CSV with the same feature columns used during training. "
        "The app adds model predictions and a readable prediction label."
    ),
    allow_flagging="never",
)


if __name__ == "__main__":
    demo.launch()
