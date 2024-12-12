const API_URL = "http://localhost:8000"; // Update with your FastAPI backend URL

// Handle register form submission
document
  .getElementById("register-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const id = document.getElementById("id").value;
    const name = document.getElementById("name").value;
    const password = document.getElementById("password").value;

    const registerData = { id, name, password };

    try {
      const response = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(registerData),
      });

      if (response.ok) {
        // Redirect to login page after successful registration
        window.location.href = "login.html";
      } else {
        const errorData = await response.json();
        document.getElementById("error-message").textContent =
          errorData.detail || "Registration failed";
      }
    } catch (error) {
      console.error("Error:", error);
      document.getElementById("error-message").textContent =
        "An error occurred. Please try again.";
    }
  });
