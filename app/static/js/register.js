const API_URL = "http://localhost:8000";

document
  .getElementById("register-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const id = document.getElementById("id").value;
    const name = document.getElementById("name").value;
    const password = document.getElementById("password").value;
    const registrationDocument = document.getElementById(
      "registration-document"
    ).files[0];

    if (!registrationDocument) {
      document.getElementById("error-message").textContent =
        "Please upload a registration document.";
      return;
    }

    const formData = new FormData();
    formData.append("id", id);
    formData.append("name", name);
    formData.append("password", password);
    formData.append("file", registrationDocument);

    try {
      const response = await fetch(`${API_URL}/register`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        alert("Your account has been registered!\nPlease wait till the account gets activated!")
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
