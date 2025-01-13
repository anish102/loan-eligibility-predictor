def loan_package_recommender(loan_packages, customer_data):
    best_packages = []
    assets_value = sum(
        [
            customer_data["residential_assets"],
            customer_data["commercial_assets"],
            customer_data["luxury_assets"],
            customer_data["bank_assets"],
        ]
    )
    eligible_packages = []
    for package in loan_packages:
        if (
            customer_data["income"] >= package.min_income
            and assets_value >= package.min_assets
            and customer_data["credit_score"] >= package.min_credit_score
        ):
            loan_amount_distance = abs(
                customer_data["loan_amount"] - package.loan_amount
            )
            loan_term_distance = abs(customer_data["loan_term"] - package.loan_term)
            score = loan_amount_distance + loan_term_distance
            eligible_packages.append((package, score))
    eligible_packages.sort(key=lambda x: x[1])
    best_packages = [package for package, score in eligible_packages]
    return best_packages
