// --------- AJAX for Register ---------

document.addEventListener("DOMContentLoaded", function () {

    // Register Form
    const registerForm = document.getElementById("registerFormInner");
    if (registerForm) {
        registerForm.addEventListener("submit", function (e) {
            e.preventDefault();
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
                        switchForm('login');
                    }
                })
                .catch(err => console.error("Register Error:", err));
        });
    }
});