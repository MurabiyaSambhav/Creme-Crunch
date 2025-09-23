// about_us.js

document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("contactForm");
    const message = document.getElementById("message");
    const charCount = document.getElementById("charCount");
    const phoneInput = document.getElementById("phone");
    const msgBox = document.getElementById("success-message");

    // Message character count
    message.addEventListener("input", () => {
        let len = message.value.length;
        if(len > 180) {
            message.value = message.value.substring(0, 180); 
            len = 180;
        }
        charCount.innerText = `${len} / 180`;
    });

    // Phone input only numbers and max 10 digits
    phoneInput.addEventListener("input", () => {
        phoneInput.value = phoneInput.value.replace(/[^0-9]/g, ""); 
        if(phoneInput.value.length > 10) {
            phoneInput.value = phoneInput.value.slice(0, 10); 
        }
    });

    // Form submit via AJAX
    form.addEventListener("submit", function(e) {
        e.preventDefault();

        let formData = new FormData(this);

        fetch(form.action || window.location.href, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            msgBox.innerText = data.message;
            msgBox.style.display = "block";
            msgBox.style.opacity = "1";
            msgBox.style.textAlign = "center";

            if (data.success) {
                form.reset();
                charCount.innerText = "0 / 180";
            }

            setTimeout(() => {
                msgBox.style.transition = "opacity 1s ease";
                msgBox.style.opacity = "0";
                setTimeout(() => {
                    msgBox.style.display = "none";
                    msgBox.style.opacity = "1";
                }, 1000);
            }, 8000);
        })
        .catch(error => console.error("Error:", error));
    });
});
