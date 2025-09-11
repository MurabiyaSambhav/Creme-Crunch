// --------- AJAX for Register ---------

document.addEventListener("DOMContentLoaded", function () {

    const registerForm = document.getElementById("registerFormInner");
    if (registerForm) {
        registerForm.addEventListener("submit", function (e) {
            e.preventDefault(); // Prevent default form submission

            const formData = new FormData(registerForm);

            fetch("/register/", {
                method: "POST",
                body: formData,
                headers: {
                    'X-CSRFToken': csrftoken
                }
            })
                .then(res => {
                    if (!res.ok) {
                        throw new Error(`Server returned ${res.status}`);
                    }
                    return res.json();
                })
                .then(data => {
                    alert(data.message);
                    if (data.success) {
                        registerForm.reset();
                        // Optional: switch to login form if you have a SPA setup
                        if (typeof switchForm === "function") {
                            switchForm('login');
                        }
                    }
                })
                .catch(err => console.error("Register Error:", err));
        });
    }
});
