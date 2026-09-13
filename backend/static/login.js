document.addEventListener("DOMContentLoaded", () => {

    const loginForm =
        document.getElementById("loginForm");

    const errorMessage =
        document.getElementById("loginError");

    if (!loginForm) {
        return;
    }

    loginForm.addEventListener("submit", async event => {

        event.preventDefault();

        const email =
            document.getElementById("email").value.trim();

        const password =
            document.getElementById("password").value;

        errorMessage.style.display = "none";
        errorMessage.textContent = "";

        try {

            const response = await fetch("/api/login", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    password: password
                })

            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Invalid email or password."
                );
            }

            window.location.href = "/";

        } catch (error) {

            errorMessage.textContent =
                error.message ||
                "Login failed.";

            errorMessage.style.display = "block";
        }

    });

});