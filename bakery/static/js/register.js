// --------- AJAX for Register ---------
document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("registerFormInner");
    const loginMessage = document.getElementById("loginMessage");
    const registerMessage = document.getElementById("registerMessage");

    function showMessage(target, message, type = "success") {
        if (target) {
            target.innerHTML = `
                <div class="p-2 rounded ${type === "success" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}">
                    ${message}
                </div>
            `;
        } else {
            alert(message); // fallback
        }
    }

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
});
