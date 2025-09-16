document.addEventListener('DOMContentLoaded', () => {
    const authModal = document.getElementById('authModal');
    const loginFormContainer = document.getElementById('loginForm');
    const registerFormContainer = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginFormInner');
    const loginButtons = ['btn-login-header', 'btn-login-mobile', 'btn-login-cart']
        .map(id => document.getElementById(id))
        .filter(Boolean);

    // Attach login buttons
    loginButtons.forEach(btn => btn.addEventListener('click', e => {
        e.preventDefault();
        openModal("login"); // use global openModal from base.js
    }));

    // Close modal when clicking outside
    authModal.addEventListener('click', e => {
        if (e.target === authModal) closeModal(); // use global closeModal
    });

    // Make switchForm global (if not already)
    window.switchForm = switchForm;

    // AJAX login
    if (loginForm) {
        loginForm.addEventListener('submit', async e => {
            e.preventDefault();
            const data = new FormData(loginForm);
            try {
                const res = await fetch(loginForm.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrftoken   // use global csrftoken from base.js
                    },
                    body: data
                });

                const text = await res.text();
                let json;

                try {
                    json = JSON.parse(text);
                } catch (parseErr) {
                    console.error("Server returned non-JSON response:", text.slice(0, 300));
                    document.getElementById('login-error').innerText =
                        "Server error (non-JSON response)";
                    return;
                }

                if (json.success) {
                    closeModal();
                    window.location.href = json.redirect_url;
                } else {
                    document.getElementById('login-error').innerText = json.message;
                }
            } catch (err) {
                document.getElementById('login-error').innerText = 'Server error';
                console.error("Login error:", err);
            }
        });
    }

    // Initialize Lucide icons safely
    if (typeof lucide !== 'undefined' && typeof lucide.replace === 'function') {
        lucide.replace();
    }
});
