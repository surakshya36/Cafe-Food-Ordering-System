function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

document.addEventListener("DOMContentLoaded", function() {
    // Initialize toasts
    const toastEl = document.getElementById('cartToast');
    const toast = toastEl ? new bootstrap.Toast(toastEl) : null;

    // Add to cart functionality (unchanged)
    document.querySelectorAll(".btn-order").forEach(btn => {
        btn.addEventListener("click", function(e) {
            e.preventDefault();
            const item_id = this.value;
            
            fetch("../add-to-cart/", {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json", 
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({id: item_id})
            })
            .then(res => res.json())
            .then(data => {
                console.log(data);
                if(data.success) {
                    const cartCount = document.querySelector('.cart-count');
                    if(cartCount) cartCount.textContent = data.cart_total;
                    
                    if(toast) {
                        const toastMessage = document.getElementById('toastMessage');
                        if(toastMessage) {
                            toastMessage.textContent = data.message || "Item added to cart!";
                            toast.show();
                        }
                    }
                }
            })
            .catch(error => console.error(error));
        });
    });

    document.querySelectorAll("[data-action='increase_quantity'], [data-action='decrease_quantity'], [data-action='remove_item']").forEach(btn => {
    btn.addEventListener("click", function(e) {
        e.preventDefault();
        const itemId = this.dataset.itemId;
        const action = this.dataset.action;
        
        const url = `items/${action}/${itemId}/`;

        fetch(url, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json", 
                'X-CSRFToken': csrftoken 
            }
        })
        .then(res => {
            if (!res.ok) throw new Error('Network response was not ok');
            return res.json();
        })
        .then(data => {
            if (data.success) {
                // Simply reload the page to reflect all cart changes
                location.reload();
            }
        })
        .catch(error => {
            console.error('Cart update failed:', error);
        });
    });
});

});