// ------------------ CSRF Helper ------------------
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


// ------------------ Modal Functions ------------------
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

    if (form === "login") document.getElementById("loginForm").classList.remove("hidden");
    else document.getElementById("registerForm").classList.remove("hidden");
}


// ------------------ Cart Sidebar Functions ------------------
const cartButtons = document.querySelectorAll('.btn-cart');
const cartSidebar = document.getElementById('cart-sidebar');
const cartOverlay = document.getElementById('cart-overlay');
const closeCartBtn = document.getElementById('close-cart');
const cartItemsContainer = document.getElementById('cart-items');

// Header Cart Elements
const cartCountEl = document.getElementById('cart-count');   // number of items
const cartTotalEl = document.getElementById('cart-total');   // total amount

// Open Cart
cartButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        cartSidebar.style.right = '0';
        cartOverlay.classList.remove('hidden');

        // Fetch cart items via AJAX
        fetchCartItems();
    });
});

// Close Cart
closeCartBtn.addEventListener('click', closeCart);
cartOverlay.addEventListener('click', closeCart);

function closeCart() {
    cartSidebar.style.right = '-400px';
    cartOverlay.classList.add('hidden');
}

// Fetch Cart Items (AJAX) and update header
function fetchCartItems() {
    fetch('/cart/items/')  // Replace with your Django URL returning JSON cart items
        .then(res => res.json())
        .then(data => {
            // ---------------- Update Sidebar ----------------
            cartItemsContainer.innerHTML = '';
            if (data.items.length === 0) {
                cartItemsContainer.innerHTML = '<p class="text-gray-500">Your cart is empty.</p>';
            } else {
                data.items.forEach(item => {
                    cartItemsContainer.innerHTML += `
                        <div class="flex justify-between items-center mb-3">
                            <span>${item.name} x ${item.quantity}</span>
                            <span>₹${item.total_price.toFixed(2)}</span>
                        </div>
                    `;
                });
            }

            // ---------------- Update Header Cart ----------------
            let totalCount = data.items.reduce((sum, item) => sum + item.quantity, 0);
            let totalAmount = data.items.reduce((sum, item) => sum + item.total_price, 0);

            if (cartCountEl) cartCountEl.innerText = totalCount;
            if (cartTotalEl) cartTotalEl.innerText = `₹${totalAmount.toFixed(2)}`;
        })
        .catch(err => {
            cartItemsContainer.innerHTML = '<p class="text-red-500">Failed to load cart.</p>';
            console.error(err);
        });
}

// ------------------ Initialize Header Cart on Page Load ----------------
document.addEventListener('DOMContentLoaded', fetchCartItems);
