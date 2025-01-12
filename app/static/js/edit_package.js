const API_URL = "http://localhost:8000";

const urlParams = new URLSearchParams(window.location.search);
const packageId = urlParams.get("id");

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

document.addEventListener("DOMContentLoaded", async () => {
  if (!isAuthenticated()) {
    window.location.href = "/static/login.html";
    return;
  }

  try {
    const response = await fetch(`${API_URL}/loan_package/${packageId}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      const package = data.package;
      document.getElementById("loan_name").value = package.loan_name;
      document.getElementById("loan_amount").value = package.loan_amount;
      document.getElementById("min_income").value = package.min_income;
      document.getElementById("min_assets").value = package.min_assets;
      document.getElementById("min_credit_score").value =
        package.min_credit_score;
      document.getElementById("loan_term").value = package.loan_term;
      document.getElementById("interest_rate").value = package.interest_rate;
    } else {
      const errorData = await response.json();
      alert(errorData.detail || "Error fetching package data");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred. Please try again.");
  }
});

document
  .getElementById("edit-package-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();
    if (!isAuthenticated()) {
      window.location.href = "/static/login.html";
      return;
    }

    const updatedData = {
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
      const response = await fetch(`${API_URL}/loan_package/${packageId}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedData),
      });

      if (response.ok) {
        alert("Package updated successfully!");
        window.location.href = "/static/loan_packages.html";
      } else {
        const errorData = await response.json();
        document.getElementById("error-message").textContent =
          errorData.detail || "Error updating package";
      }
    } catch (error) {
      console.error("Error:", error);
      document.getElementById("error-message").textContent =
        "An error occurred. Please try again.";
    }
  });

async function deletePackage() {
  if (!isAuthenticated()) {
    window.location.href = "/static/login.html";
    return;
  }

  const confirmDelete = confirm(
    "Are you sure you want to delete this package? This action cannot be undone."
  );
  if (!confirmDelete) {
    return;
  }

  try {
    const response = await fetch(`${API_URL}/loan_package/${packageId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      alert("Package deleted successfully!");
      window.location.href = "/static/loan_packages.html";
    } else {
      const errorData = await response.json();
      alert(errorData.detail || "Error deleting package");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred. Please try again.");
  }
}

function showAlert(message) {
  const modal = document.getElementById("alert-modal");
  const modalMessage = document.getElementById("modal-message");
  const okBtn = document.getElementById("modal-ok-btn");

  modalMessage.textContent = message;
  modal.style.display = "block";

  okBtn.onclick = () => {
    modal.style.display = "none";
  };

  window.onclick = (event) => {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };
}
