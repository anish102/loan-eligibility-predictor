import pickle

import pandas as pd

with open(
    "/home/user/Desktop/7semProject/Loan_Eligibility_Prediction/app/model.pkl", "rb"
) as file:
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
