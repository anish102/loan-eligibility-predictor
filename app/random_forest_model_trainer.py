import pickle
import warnings
from collections import Counter
from random import sample

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")


class LoanApprovalModel:
    def __init__(self):
        self.model = None
        self.feature_names = None

    def load_and_preprocess_data(self, filepath):
        """Load and preprocess the loan dataset."""
        loan_data = pd.read_csv(filepath)
        mapping = {
            " self_employed": {" No": 0, " Yes": 1},
            " education": {" Not Graduate": 0, " Graduate": 1},
            " loan_status": {" Rejected": 0, " Approved": 1},
        }
        for column, map_dict in mapping.items():
            loan_data[column] = loan_data[column].map(map_dict)
        self.feature_names = [
            " self_employed",
            " income_annum",
            " loan_amount",
            " cibil_score",
            " education",
            " loan_term",
            " residential_assets_value",
            " commercial_assets_value",
            " luxury_assets_value",
            " bank_asset_value",
        ]

        X = loan_data[self.feature_names]
        y = loan_data[" loan_status"]

        return X, y

    def plot_distributions(self, loan_data):
        """Plot output distribution and correlation matrix."""
        plt.figure(figsize=(10, 5))
        sns.countplot(data=loan_data, x=" loan_status")
        plt.title("Loan Status Distribution")
        plt.show()
        plt.figure(figsize=(12, 10))
        correlation_matrix = loan_data[self.feature_names + [" loan_status"]].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Feature Correlation Matrix")
        plt.tight_layout()
        plt.show()

    def evaluate_model(self, y_true, y_pred):
        """Evaluate model performance with multiple metrics."""
        print("\nModel Evaluation:")
        print("-" * 50)
        print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
        print("\nClassification Report:")
        print(classification_report(y_true, y_pred))
        plt.figure(figsize=(8, 6))
        cm = confusion_matrix(y_true, y_pred)
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
        plt.title("Confusion Matrix")
        plt.ylabel("True Label")
        plt.xlabel("Predicted Label")
        plt.show()


class DecisionTree:
    def __init__(self, max_depth=None):
        self.max_depth = max_depth
        self.tree = None

    def fit(self, X, y):
        self.tree = self._grow_tree(X, y, depth=0)

    def _grow_tree(self, X, y, depth):
        if len(set(y)) == 1 or (self.max_depth and depth >= self.max_depth):
            return Counter(y).most_common(1)[0][0]
        best_feature, best_threshold, best_gain, best_split = None, None, -1, None
        for feature_index in range(len(X[0])):
            thresholds = set([row[feature_index] for row in X])
            for threshold in thresholds:
                left_indices, right_indices = split_data(X, y, feature_index, threshold)
                if left_indices and right_indices:
                    gain = information_gain(y, left_indices, right_indices)
                    if gain > best_gain:
                        best_feature, best_threshold, best_gain, best_split = (
                            feature_index,
                            threshold,
                            gain,
                            (left_indices, right_indices),
                        )
        if best_gain == -1:
            return Counter(y).most_common(1)[0][0]

        left_indices, right_indices = best_split
        left_subtree = self._grow_tree(
            [X[i] for i in left_indices], [y[i] for i in left_indices], depth + 1
        )
        right_subtree = self._grow_tree(
            [X[i] for i in right_indices], [y[i] for i in right_indices], depth + 1
        )
        return (best_feature, best_threshold, left_subtree, right_subtree)

    def predict(self, X):
        return [self.predict_one(row, self.tree) for row in X]

    def predict_one(self, row, node):
        if not isinstance(node, tuple):
            return node
        feature, threshold, left_subtree, right_subtree = node
        if row[feature] <= threshold:
            return self.predict_one(row, left_subtree)
        return self.predict_one(row, right_subtree)


class RandomForest:
    def __init__(self, n_estimators=10, max_depth=None, max_features=None):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.max_features = max_features
        self.trees = []

    def fit(self, X, y):
        self.trees = []
        n_samples = len(X)
        for _ in range(self.n_estimators):
            indices = sample(range(n_samples), n_samples)
            X_bootstrap = [X[i] for i in indices]
            y_bootstrap = [y[i] for i in indices]
            tree = DecisionTree(max_depth=self.max_depth)
            tree.fit(X_bootstrap, y_bootstrap)
            self.trees.append(tree)

    def predict(self, X):
        tree_predictions = [tree.predict(X) for tree in self.trees]
        aggregated_predictions = []
        for i in range(len(X)):
            predictions = [
                tree_predictions[tree_idx][i] for tree_idx in range(self.n_estimators)
            ]
            aggregated_predictions.append(Counter(predictions).most_common(1)[0][0])
        return aggregated_predictions


def split_data(X, y, feature_index, threshold):
    """Split data based on feature threshold."""
    left_indices = [i for i in range(len(X)) if X[i][feature_index] <= threshold]
    right_indices = [i for i in range(len(X)) if X[i][feature_index] > threshold]
    return left_indices, right_indices


def gini_impurity(y):
    """Calculate Gini impurity."""
    class_counts = Counter(y)
    n_samples = len(y)
    impurity = 1 - sum((count / n_samples) ** 2 for count in class_counts.values())
    return impurity


def information_gain(y, left_indices, right_indices):
    """Calculate information gain."""
    n_samples = len(y)
    left_impurity = gini_impurity([y[i] for i in left_indices])
    right_impurity = gini_impurity([y[i] for i in right_indices])
    weighted_impurity = (len(left_indices) / n_samples) * left_impurity + (
        len(right_indices) / n_samples
    ) * right_impurity
    return gini_impurity(y) - weighted_impurity


def main():
    loan_model = LoanApprovalModel()
    X, y = loan_model.load_and_preprocess_data("app/loan_approval_dataset.csv")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = RandomForest(n_estimators=100, max_depth=10)
    model.fit(X_train.values.tolist(), y_train.values.tolist())
    y_pred = model.predict(X_test.values.tolist())
    loan_model.evaluate_model(y_test, y_pred)
    with open("model.pkl", "wb") as file:
        pickle.dump(model, file)
    print("\nModel saved successfully!")


if __name__ == "__main__":
    main()
