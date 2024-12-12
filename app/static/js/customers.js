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
    const response = await fetch(`${API_URL}/customers`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      const customersList = data.customers;
      const customersTable = document.getElementById("customers-list");

      customersList.forEach((customer) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${customer.name}</td>
          <td>${customer.income}</td>
          <td>${customer.credit_score}</td>
          <td>${customer.loan_amount}</td>
          <td class="action">
            <button onclick="window.location.href='/static/edit_customer.html?id=${customer.id}'">View</button>
            <button onclick="deleteCustomer(${customer.id})">Delete</button>
          </td>
        `;
        customersTable.appendChild(row);
      });
    } else {
      const errorData = await response.json();
      document.getElementById("error-message").textContent =
        errorData.detail || "Error fetching customers";
    }
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("error-message").textContent =
      "An error occurred. Please try again.";
  }
});

// Delete customer
async function deleteCustomer(customerId) {
  if (!isAuthenticated()) {
    window.location.href = "/static/login.html"; // Redirect to login if no token
    return;
  }

  try {
    const response = await fetch(`${API_URL}/customer/${customerId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      window.location.reload(); // Reload the page to reflect the changes
    } else {
      const errorData = await response.json();
      alert(errorData.detail || "Error deleting customer");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred. Please try again.");
  }
}
