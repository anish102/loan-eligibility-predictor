const API_URL = "http://localhost:8000";

function isAuthenticated() {
  const token = localStorage.getItem("token");
  if (!token) {
    return false;
  }
  const payload = JSON.parse(atob(token.split(".")[1]));
  const exp = payload.exp;
  if (exp * 1000 < Date.now()) {
    localStorage.removeItem("token");
    return false;
  }
  return true;
}

document
  .getElementById("add-package-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    if (!isAuthenticated()) {
      window.location.href = "/static/login.html";
      return;
    }

    const packageData = {
      loan_name: document.getElementById("loan_name").value,
      loan_amount: parseFloat(document.getElementById("loan_amount").value),
      min_income: parseFloat(document.getElementById("min_income").value),
      min_assets: parseInt(document.getElementById("min_assets").value),
      loan_term: parseInt(document.getElementById("loan_term").value),
      min_credit_score: parseInt(
        document.getElementById("min_credit_score").value
      ),
      interest_rate: parseFloat(document.getElementById("interest_rate").value),
    };

    try {
      const response = await fetch(`${API_URL}/loan_package`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(packageData),
      });

      if (response.ok) {
        const data = await response.json();
        alert("Package added successfully!");
        window.location.href = "/static/loan_packages.html";
      } else {
        const errorData = await response.json();
        document.getElementById("error-message").textContent =
          errorData.detail || "Error adding package";
      }
    } catch (error) {
      console.error("Error:", error);
      document.getElementById("error-message").textContent =
        "An error occurred. Please try again.";
    }
  });
