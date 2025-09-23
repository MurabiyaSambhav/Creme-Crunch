document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("registerFormInner");
    const loginMessage = document.getElementById("loginMessage");
    const registerMessage = document.getElementById("registerMessage");

   function showMessage(target, message, type = "success") {
    if (target) {
        target.innerHTML = `
            <div class="p-2 rounded" 
                 style="color: white; 
                        background-color: ${type === "success" ? '#63b665ff' : '#e38c86ff'}; 
                        text-align: center;">
                ${message}
            </div>
        `;
    } else {
        alert(message); // fallback
    }
}


    // AJAX form submit
    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            try {
                const res = await fetch("/register/", {
                    method: "POST",
                    body: new FormData(registerForm),
                    headers: {
                        "X-CSRFToken": csrftoken,
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                if (!res.ok) throw new Error(`Server returned ${res.status}`);

                const data = await res.json();

                if (data.success) {
                    registerForm.reset();
                    showMessage(loginMessage, data.message, "success");

                    if (typeof switchForm === "function") switchForm("login");
                } else {
                    showMessage(registerMessage, data.message, "error");
                }
            } catch (err) {
                console.error("Register Error:", err);
                showMessage(registerMessage, "Something went wrong. Please try again.", "error");
            }
        });
    }

    // Phone input validation
    const phoneInput = document.querySelector("input[name='phone']");
    if (phoneInput) {
        phoneInput.addEventListener("input", () => {
            phoneInput.value = phoneInput.value.replace(/[^0-9]/g, "");
            if (phoneInput.value.length > 10) phoneInput.value = phoneInput.value.slice(0, 10);
        });
    }

window.closeModal = function () {
    const authModal = document.getElementById("authModal");
    if (authModal) authModal.classList.add("hidden");

    // Reset forms
    const registerForm = document.getElementById("registerFormInner");
    if (registerForm) registerForm.reset();

    const loginForm = document.getElementById("loginFormInner");
    if (loginForm) loginForm.reset();

    // Clear messages
    const registerMessage = document.getElementById("registerMessage");
    if (registerMessage) registerMessage.innerHTML = '';

    const loginError = document.getElementById("login-error"); // correct div
    if (loginError) loginError.innerHTML = '';
};
});
