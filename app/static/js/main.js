// Aura by Honeyy - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Aura by Honeyy loaded!');
    
    // Add to cart confirmation
    document.querySelectorAll('form[action*="/cart/add/"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const qty = this.querySelector('input[name="quantity"]').value;
            // Optional: Show confirmation message
        });
    });
    
    // Remove from cart confirmation
    document.querySelectorAll('form[action*="/cart/remove/"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Remove item from cart?')) {
                e.preventDefault();
            }
        });
    });
});

// Format currency
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toFixed(2);
}