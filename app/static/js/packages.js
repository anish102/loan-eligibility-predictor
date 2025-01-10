const API_URL = "http://localhost:8000"; // Update with your FastAPI backend URL

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

// Load customer data when the page loads
document.addEventListener("DOMContentLoaded", async () => {
  if (!isAuthenticated()) {
    window.location.href = "/static/login.html"; // Redirect to login if no token
    return;
  }

  try {
    const response = await fetch(`${API_URL}/loan_packages`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      const packagesList = data.packages;
      const packageTable = document.getElementById("packages-list");

      packagesList.forEach((package) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${package.loan_name}</td>
          <td>${package.loan_amount}</td>
          <td>${package.loan_term}</td>
          <td>${package.loan_amount}</td>
        `;
        row.addEventListener("click", () => {
          window.location.href = `/static/edit_loan_package.html?id=${package.id}`;
        });

        packageTable.appendChild(row);
      });
    } else {
      const errorData = await response.json();
      document.getElementById("error-message").textContent =
        errorData.detail || "Error fetching packages";
    }
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("error-message").textContent =
      "An error occurred. Please try again.";
  }
});
