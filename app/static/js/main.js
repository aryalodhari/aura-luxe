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

// for close the messagePanel from the jinja
const btn = document.getElementById("btn");

// Fix: Check if the button actually exists on the page before adding the listener
if (btn) {
    btn.addEventListener("click", function(e){
        const messagePanel = document.getElementById("messagepanel");
        // Extra safety check for the panel itself
        if (messagePanel) {
            messagePanel.style.display = "none";
        }
    });
}