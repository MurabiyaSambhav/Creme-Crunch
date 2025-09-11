// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


//   Modal Functions
   
        function openModal(form) {
            document.getElementById("authModal").classList.remove("hidden");
        switchForm(form);
    }
        function closeModal() {
            document.getElementById("authModal").classList.add("hidden");
    }
        function switchForm(form) {
            document.getElementById("loginForm").classList.add("hidden");
        document.getElementById("registerForm").classList.add("hidden");
        if(form === "login") document.getElementById("loginForm").classList.remove("hidden");
        else document.getElementById("registerForm").classList.remove("hidden");
    }
 

