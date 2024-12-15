import os
import pickle

import pandas as pd

MODEL_PATH = os.getenv("MODEL_PATH")

with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)


def predict_approval_status(customer):
    input_data = {
        " self_employed": [customer["is_employed"]],
        " income_annum": [customer["income"]],
        " loan_amount": [customer["loan_amount"]],
        " cibil_score": [customer["credit_score"]],
        " education": [customer["is_graduated"]],
        " loan_term": [customer["loan_term"]],
        " residential_assets_value": [customer["residential_assets"]],
        " commercial_assets_value": [customer["commercial_assets"]],
        " luxury_assets_value": [customer["luxury_assets"]],
        " bank_asset_value": [customer["bank_assets"]],
    }
    X_new = pd.DataFrame(input_data)
    predictions = model.predict(X_new)
    return bool(predictions[0])
