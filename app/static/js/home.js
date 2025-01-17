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

async function fetchCustomerOverview() {
  try {
    const response = await fetch(`${API_URL}/customers/overview`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });
    if (response.ok) {
      const data = await response.json();
      document.getElementById("total-customers").textContent =
        data.total_customers;
      document.getElementById("approved-customers").textContent =
        data.loan_approved_customers;
      document.getElementById("latest-customer").textContent =
        data.latest_customer;
    }
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("error-message").textContent =
      "An error occurred. Please reload page.";
  }
}

async function fetchPackageOverview() {
  try {
    const response = await fetch(`${API_URL}/packages/overview`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });
    if (response.ok) {
      const data = await response.json();
      document.getElementById("total-packages").textContent =
        data.total_packages;
      document.getElementById("max-loan").textContent = data.max_loan;
      document.getElementById("min-loan").textContent = data.min_loan;
    }
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("error-message").textContent =
      "An error occurred. Please reload page.";
  }
}

window.onload = function () {
  if (!isAuthenticated()) {
    window.location.href = "/static/login.html";
    return;
  }
  fetchCustomerOverview();
  fetchPackageOverview();
};
