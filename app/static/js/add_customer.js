const API_URL = "http://localhost:8000"; // Update with your FastAPI backend URL

// Function to check if the user is authenticated (i.e., token exists in localStorage)
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

// Handle form submission for adding a customer
document
  .getElementById("add-customer-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    // Check if the user is authenticated
    if (!isAuthenticated()) {
      window.location.href = "/static/login.html"; // Redirect to login page if no valid token
      return;
    }

    // Collect the customer data from the form
    const customerData = {
      name: document.getElementById("name").value,
      is_employed: document.getElementById("is_employed").checked,
      income: parseFloat(document.getElementById("income").value),
      is_graduated: document.getElementById("is_graduated").checked,
      loan_amount: parseFloat(document.getElementById("loan_amount").value),
      credit_score: parseInt(document.getElementById("credit_score").value),
      residential_assets:
        parseFloat(document.getElementById("residential_assets").value) || 0,
      commercial_assets:
        parseFloat(document.getElementById("commercial_assets").value) || 0,
      luxury_assets:
        parseFloat(document.getElementById("luxury_assets").value) || 0,
      bank_assets:
        parseFloat(document.getElementById("bank_assets").value) || 0,
      loan_term: parseInt(document.getElementById("loan_term").value),
      approval_status: document.getElementById("approval_status").checked,
    };

    try {
      const response = await fetch(`${API_URL}/customer`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`, // Send token in the Authorization header
          "Content-Type": "application/json", // Set content type to JSON
        },
        body: JSON.stringify(customerData), // Send customer data as JSON
      });

      if (response.ok) {
        const data = await response.json();
        alert("Customer added successfully!");
        window.location.href = "/static/customers.html"; // Redirect to customer list after successful addition
      } else {
        const errorData = await response.json();
        document.getElementById("error-message").textContent =
          errorData.detail || "Error adding customer"; // Show error if response is not ok
      }
    } catch (error) {
      console.error("Error:", error);
      document.getElementById("error-message").textContent =
        "An error occurred. Please try again."; // Handle any errors during the request
    }
  });
