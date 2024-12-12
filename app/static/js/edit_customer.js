const API_URL = "http://localhost:8000"; // Update with your FastAPI backend URL

const urlParams = new URLSearchParams(window.location.search);
const customerId = urlParams.get("id");

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

// Fetch the customer data and prefill the form
document.addEventListener("DOMContentLoaded", async () => {
  if (!isAuthenticated()) {
    window.location.href = "/static/login.html"; // Redirect to login page if no valid token
    return;
  }

  try {
    const response = await fetch(`${API_URL}/customer/${customerId}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      const customer = data.customer;
      document.getElementById("name").value = customer.name;
      document.getElementById("income").value = customer.income;
      document.getElementById("loan_amount").value = customer.loan_amount;
      document.getElementById("credit_score").value = customer.credit_score;
      document.getElementById("is_employed").checked = customer.is_employed;
      document.getElementById("is_graduated").checked = customer.is_graduated;
      document.getElementById("residential_assets").value =
        customer.residential_assets;
      document.getElementById("commercial_assets").value =
        customer.commercial_assets;
      document.getElementById("luxury_assets").value = customer.luxury_assets;
      document.getElementById("bank_assets").value = customer.bank_assets;
      document.getElementById("loan_term").value = customer.loan_term;
      document.getElementById("approval_status").checked =
        customer.approval_status;
    } else {
      const errorData = await response.json();
      alert(errorData.detail || "Error fetching customer data");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred. Please try again.");
  }
});

// Update customer
document
  .getElementById("edit-customer-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();
    if (!isAuthenticated()) {
      window.location.href = "/static/login.html"; // Redirect to login page if no valid token
      return;
    }

    const updatedData = {
      name: document.getElementById("name").value,
      income: parseFloat(document.getElementById("income").value),
      loan_amount: parseFloat(document.getElementById("loan_amount").value),
      credit_score: parseInt(document.getElementById("credit_score").value),
      is_employed: document.getElementById("is_employed").checked,
      is_graduated: document.getElementById("is_graduated").checked,
      residential_assets: document.getElementById("residential_assets").value,
      commercial_assets: document.getElementById("commercial_assets").value,
      luxury_assets: document.getElementById("luxury_assets").value,
      bank_assets: document.getElementById("bank_assets").value,
      loan_term: document.getElementById("loan_term").value,
      approval_status: document.getElementById("approval_status").checked,
    };

    try {
      const response = await fetch(`${API_URL}/customer/${customerId}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedData),
      });

      if (response.ok) {
        alert("Customer updated successfully!");
        window.location.href = "/static/customers.html"; // Redirect back to customers list page
      } else {
        const errorData = await response.json();
        document.getElementById("error-message").textContent =
          errorData.detail || "Error updating customer";
      }
    } catch (error) {
      console.error("Error:", error);
      document.getElementById("error-message").textContent =
        "An error occurred. Please try again.";
    }
  });

// Check approval status button logic
document
  .getElementById("check-status-button")
  .addEventListener("click", async function (event) {
    event.preventDefault(); // Prevent form submission

    const customerData = {
      name: document.getElementById("name").value,
      is_employed: document.getElementById("is_employed").checked,
      income: parseFloat(document.getElementById("income").value),
      is_graduated: document.getElementById("is_graduated").checked,
      residential_assets:
        parseFloat(document.getElementById("residential_assets").value) || 0,
      commercial_assets:
        parseFloat(document.getElementById("commercial_assets").value) || 0,
      luxury_assets:
        parseFloat(document.getElementById("luxury_assets").value) || 0,
      bank_assets:
        parseFloat(document.getElementById("bank_assets").value) || 0,
      credit_score:
        parseFloat(document.getElementById("credit_score").value) || 0,
      loan_amount:
        parseFloat(document.getElementById("loan_amount").value) || 0,
      loan_term: parseFloat(document.getElementById("loan_term").value) || 0,
    };

    try {
      const response = await fetch(
        `${API_URL}/check_approval_status/${customerId}`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(customerData),
        }
      );

      if (!response.ok) {
        throw new Error("Error checking approval status");
      }

      const data = await response.json();
      const approvalStatus = data.approval_status;
      const message = data.message;

      // Display approval status in the UI
      const approvalStatusCheckbox = document.getElementById("approval_status");
      approvalStatusCheckbox.checked = approvalStatus;

      // Optionally, display the message somewhere in the UI
      if (message) {
        showAlert(message);
      }
    } catch (error) {
      console.error("Error:", error);
      document.getElementById("error-message").textContent =
        "Failed to check approval status";
    }
  });

function showAlert(message) {
  const modal = document.getElementById("alert-modal");
  const modalMessage = document.getElementById("modal-message");
  const okBtn = document.getElementById("modal-ok-btn");

  modalMessage.textContent = message;
  modal.style.display = "block";

  // Close the modal when the "OK" button or the close icon is clicked
  okBtn.onclick = () => {
    modal.style.display = "none";
  };

  // Close the modal if the user clicks outside of the modal
  window.onclick = (event) => {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };
}
