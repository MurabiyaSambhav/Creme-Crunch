// product.js

// Function to change quantity
function changeQuantity(val) {
    let qtyInput = document.getElementById('quantity');
    let qty = parseInt(qtyInput.value);

    qty += val;
    if (qty < 1) qty = 1;

    qtyInput.value = qty;
    updatePrice();
}

// Function to update price dynamically
function updatePrice() {
    let qty = parseInt(document.getElementById('quantity').value);
    let weightPrice = parseInt(document.getElementById('weight').value);

    let total = qty * weightPrice;
    document.getElementById('price').innerText = `₹${total}.00`;
}

// Run updatePrice on page load (default)
document.addEventListener("DOMContentLoaded", () => {
    updatePrice();
});
