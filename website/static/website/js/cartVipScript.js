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

    // Add to VIP cart functionality
    document.querySelectorAll(".btn-order").forEach(btn => {
        btn.addEventListener("click", function(e) {
            e.preventDefault();
            const item_id = this.value;
            
            fetch("../vip-add-to-cart/", {  // VIP cart add URL
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
                            toastMessage.textContent = data.message || "Item added to VIP cart!";
                            toast.show();
                        }
                    }
                }
            })
            .catch(error => console.error(error));
        });
    });

    // VIP cart item quantity increase, decrease, remove buttons
    document.querySelectorAll("[data-action='vip_increase_quantity'], [data-action='vip_decrease_quantity'], [data-action='vip_remove_item']").forEach(btn => {
        btn.addEventListener("click", function(e) {
            e.preventDefault();
            const itemId = this.dataset.itemId;
            const action = this.dataset.action;
            
            // Use VIP cart URL path prefix here
            const url = `/website/vip-cart/items/${action}/${itemId}/`;

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
                    // Reload to reflect cart changes
                    location.reload();
                }
            })
            .catch(error => {
                console.error('VIP Cart update failed:', error);
            });
        });
    });
});
