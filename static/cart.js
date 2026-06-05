document.addEventListener("DOMContentLoaded", function () {
  const cartCount = document.querySelector("#cart-badge") || document.querySelector(".cart-count");
  const addToCartButtons = document.querySelectorAll(".add-to-cart-btn");
  const cartIcon = cartCount ? cartCount.parentElement : null;

  // Load cart from localStorage
  let cart = JSON.parse(localStorage.getItem("cart")) || [];
  // Older items might not have `quantity` or `rating` — default to sensible values
  cart = cart.map((it) => ({ ...it, quantity: it.quantity || 1, rating: it.rating || 0 }));
  updateCartCount();

  addToCartButtons.forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      const type = btn.getAttribute("data-type") || "shoe";
      const rawId = btn.getAttribute("data-product-id") || btn.dataset.productId || btn.getAttribute("data-shoe-id") || btn.getAttribute("data-watch-id");
      const productId = String(rawId);

      const selectedQty = parseInt(btn.getAttribute("data-quantity") || btn.getAttribute("data-shoe-quantity") || "1", 10) || 1;
      const existing = cart.find((item) => String(item.id) === productId && item.type === type);

      const selectedRating = parseInt(btn.getAttribute('data-rating') || btn.dataset.rating || '0', 10) || 0;

      if (existing) {
        existing.quantity = Math.min(5, (parseInt(existing.quantity, 10) || 1) + selectedQty);
        if (selectedRating > 0) existing.rating = selectedRating;
      } else {
        const image = btn.getAttribute("data-product-image") || btn.getAttribute("data-shoe-image") || "";
        const name = btn.getAttribute("data-product-name") || btn.getAttribute("data-shoe-name") || "";
        const brand = btn.getAttribute("data-product-brand") || btn.getAttribute("data-shoe-brand") || "";
        const price = btn.getAttribute("data-product-price") || btn.getAttribute("data-shoe-price") || "0";

        cart.push({
          id: productId,
          type: type,
          image,
          name,
          brand,
          price,
          quantity: Math.min(5, selectedQty),
          rating: selectedRating
        });
      }

      localStorage.setItem("cart", JSON.stringify(cart));
      updateCartCount();
      btn.textContent = `Added`;

      if (e && typeof e.preventDefault === 'function') e.preventDefault();
    });
  });

  // Wire plus/minus buttons that live inside each `.product-card` element.
  const productEls = document.querySelectorAll('.product-card');
  productEls.forEach(function (productEl) {
    const addBtn = productEl.querySelector('.add-to-cart-btn');
    if (!addBtn) return;

    // Wire up star rating clicks inside this product element.
    const ratingEl = productEl.querySelector('.rating');
    if (ratingEl) {
      const stars = Array.from(ratingEl.querySelectorAll('.star'));
      // initialize from data attribute if present
      const initial = parseInt(addBtn.getAttribute('data-shoe-rating') || addBtn.dataset.shoeRating || '0', 10) || 0;
      if (initial > 0) stars.forEach((st, i) => st.classList.toggle('filled', i < initial));

      stars.forEach(function (star, idx) {
        star.style.cursor = 'pointer';
        star.addEventListener('click', function (e) {
          e.preventDefault();
          const rating = idx + 1;
          stars.forEach((s, i) => s.classList.toggle('filled', i < rating));
          // store selected rating on the add-to-cart button so other handlers can read it
          addBtn.dataset.shoeRating = String(rating);
          addBtn.setAttribute('data-shoe-rating', String(rating));

          // AJAX SUBMISSION TO BACKEND
          const prodType = ratingEl.getAttribute('data-type');
          const prodId = ratingEl.getAttribute('data-id');
          const csrfTokenEl = document.querySelector('[name=csrfmiddlewaretoken]');
          const csrfToken = csrfTokenEl ? csrfTokenEl.value : '';

          if (prodType && prodId && csrfToken) {
              fetch("/web/review/add/", {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json',
                      'X-CSRFToken': csrfToken,
                      'X-Requested-With': 'XMLHttpRequest'
                  },
                  body: JSON.stringify({ type: prodType, id: prodId, rating: rating })
              })
              .then(response => {
                  if (response.status === 403 || response.redirected) {
                      alert("Please log in to save your rating.");
                      return;
                  }
                  return response.json();
              })
              .then(data => {
                  if (data && data.status === 'success') {
                      console.log('Rating saved successfully');
                      // Optional: show a small toast or subtle feedback instead of alert if preferred
                  } else if (data && data.message) {
                      alert("Error: " + data.message);
                  }
              })
              .catch(err => {
                  console.error('Rating submission failed:', err);
                  alert("Could not connect to server to save rating.");
              });
          } else if (!csrfToken) {
              console.warn('CSRF token missing, rating not sent to server');
              alert("Security token missing. Please refresh the page.");
          }

          // If this product is already in the cart, update its rating immediately
          try {
            const rawId = addBtn.getAttribute('data-shoe-id') || addBtn.dataset.shoeId;
            const shoeId = String(rawId);
            const cartItem = cart.find((i) => String(i.shoeId) === shoeId);
            if (cartItem) {
              cartItem.rating = rating;
              localStorage.setItem('cart', JSON.stringify(cart));
              // update counters / button states
              updateCartCount();
              // if cart modal is open, re-render it to show updated rating
              const existingModal = document.getElementById('cart-modal');
              if (existingModal && typeof showCartModal === 'function') {
                showCartModal();
              }
            }
          } catch (err) {
            console.error('Error updating rating in cart:', err);
          }
        });
      });
    }

    // attempt to find plus/minus buttons inside the quantity-controls div
    const btnContainer = productEl.querySelector('.quantity-controls');
    if (!btnContainer) return;
    const btns = Array.from(btnContainer.querySelectorAll('button'));
    if (btns.length === 0) return;

    let plusBtn = null;
    let minusBtn = null;
    btns.forEach(function (b) {
      const t = (b.textContent || '').trim();
      if (t === '+' || t === '\u002B') plusBtn = b;
      if (t === '-' || t === '\u2212') minusBtn = b;
    });

    // Helper to persist & refresh
    function persistAndRefresh() {
      localStorage.setItem('cart', JSON.stringify(cart));
      updateCartCount();
    }

    if (plusBtn) {
      plusBtn.addEventListener('click', function (e) {
        e.preventDefault();
        const display = productEl.querySelector('.qty-display');
        if (display) {
          let qty = parseInt(display.textContent || '0', 10);
          if (qty < 5) {
            qty++;
            display.textContent = qty;
            addBtn.setAttribute('data-quantity', qty);
            
            // Link with 'Added' button and cart if already present
            const rawId = addBtn.getAttribute("data-product-id") || addBtn.dataset.productId || addBtn.getAttribute("data-shoe-id") || addBtn.getAttribute("data-watch-id");
            const shoeId = String(rawId);
            let item = cart.find((i) => String(i.shoeId) === shoeId || String(i.watchId) === shoeId);
            if (item) {
              item.quantity = qty;
              localStorage.setItem('cart', JSON.stringify(cart));
              updateCartCount();
              addBtn.textContent = `Added (${qty})`;
              addBtn.disabled = qty >= 5;
            }
          }
        }
      });
    }

    if (minusBtn) {
      minusBtn.addEventListener('click', function (e) {
        e.preventDefault();
        const display = productEl.querySelector('.qty-display');
        if (display) {
          let qty = parseInt(display.textContent || '0', 10);
          if (qty > 0) {
            qty--;
            display.textContent = qty;
            addBtn.setAttribute('data-quantity', qty);

            // Link with 'Added' button and cart if already present
            const rawId = addBtn.getAttribute("data-product-id") || addBtn.dataset.productId || addBtn.getAttribute("data-shoe-id") || addBtn.getAttribute("data-watch-id");
            const shoeId = String(rawId);
            let itemIdx = cart.findIndex((i) => String(i.shoeId) === shoeId || String(i.watchId) === shoeId);
            if (itemIdx !== -1) {
              if (qty === 0) {
                cart.splice(itemIdx, 1);
                addBtn.textContent = "Add to Cart";
                addBtn.disabled = false;
              } else {
                cart[itemIdx].quantity = qty;
                addBtn.textContent = `Added (${qty})`;
                addBtn.disabled = false;
              }
              localStorage.setItem('cart', JSON.stringify(cart));
              updateCartCount();
            }
          }
        }
      });
    }
  });

  // Ensure buttons reflect current cart quantities on load
  function refreshButtons() {
    addToCartButtons.forEach(function (btn) {
      const rawId = btn.getAttribute("data-product-id") || btn.dataset.productId || btn.getAttribute("data-shoe-id") || btn.getAttribute("data-watch-id");
      const pid = String(rawId);
      const item = cart.find((i) => String(i.shoeId) === pid || String(i.watchId) === pid);
      if (item) {
        btn.disabled = item.quantity >= 5;
        btn.textContent = `Added (${item.quantity})`;
      } else {
        btn.disabled = false;
        btn.textContent = "Add to Cart";
      }
    });
  }

  if (cartIcon) {
    cartIcon.addEventListener("click", function (e) {
      e.preventDefault();
      showCartModal();
    });
  }

  function updateCartCount() {
    // Count total items (sum of quantities)
    const total = cart.reduce((sum, it) => sum + (it.quantity || 0), 0);
    if (cartCount) cartCount.textContent = total;
    refreshButtons();
  }

  function showCartModal() {
    // Remove existing modal if present
    let oldModal = document.getElementById("cart-modal");
    if (oldModal) oldModal.remove();

    // Create modal
    const modal = document.createElement("div");
    modal.id = "cart-modal";
    modal.style.position = "fixed";
    modal.style.top = "12%";
    modal.style.right = "5%";
    modal.zIndex = "4";
    modal.style.transform = "translateX(50px)";
    modal.style.background = "#fff";
    modal.style.padding = "2rem";
    modal.style.boxShadow = "0 2px 16px rgba(0,0,0,0.2)";
    modal.style.zIndex = "9999";
    modal.style.borderRadius = "10px";
    modal.style.Width = "70%";
    modal.style.maxWidth= "350px";
    modal.style.marginTop = "20px";
    modal.style.maxHeight = "65%";
    modal.style.overflowY = "auto";
    modal.style.border = "1px solid brown";  
    modal.style.fontFamily = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    modal.scrollIntoView({ behavior: 'smooth', block: 'center' });  
    
    

    let html = `<h2 style="color:var(--jumia-dark, #313133);border-bottom:1px solid #eee;padding-bottom:10px;">Cart Items</h2>`;
  let totalPrice = 0;
  let totalPriceUSD = 0;
    if (cart.length === 0) {
      html += `<p style="color:#75757a;text-align:center;padding:20px 0;">Your cart is empty.</p>`;
    } else {
      cart.forEach(function (item) {
        const qty = item.quantity || 1;
        let priceNGN = parseFloat(item.price || item.shoePrice || item.watchPrice || 0);
        let subtotalNGN = priceNGN * qty;
        totalPrice += subtotalNGN;

        let starHtml = '';
        const ratingVal = parseInt(item.rating || 0, 10) || 0;
        if (ratingVal > 0) {
          for (let i = 1; i <= 5; i++) {
            starHtml += `<span style="color:${i<=ratingVal?'gold':'#ddd'};font-size:14px;margin-right:2px">★</span>`;
          }
        }

        html += `<div style="display:flex;background:#f9f9f9;border-radius:10px;padding:1rem;margin-bottom:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.07);text-align:center;align-items:center;">
          <img src="${item.image || item.shoeImage || item.watchImage}" alt="${item.name || item.shoeName}" style="width:60px;height:70px;object-fit:cover;border-radius:8px;margin-bottom:10px;border:1px solid #eee;display:flex;margin-left:auto;margin-right:auto;">
          <div style="margin-bottom:6px;margin-left:12px;flex:1;text-align:left;">
            <span style="font-weight:bold;font-size:1.1rem;">${item.name || item.shoeName || item.watchName}</span><br>
            <span style="color:#555;">${item.brand || item.shoeBrand || item.watchBrand}</span><br>
            ${starHtml}
          </div>
          <div style="margin-bottom:4px;text-align:right;">
            <div style="font-weight:bold;color:#222;">₦${priceNGN.toLocaleString()} × ${qty}</div>
            <div style="color:#4a148c;font-weight:bold;">₦${subtotalNGN.toLocaleString()}</div>
          </div>
        </div>`;
      });
      html += `<h3 style="margin-top:1rem;">Total: ₦${totalPrice.toLocaleString()} <br>`;
    }
    html += `<button id="clear-cart-modal" style="margin-top:1rem;margin-right:1rem;background-color:#ff4d4f;color:white;border:1px solid #ff4d4f;padding:10px 20px;border-radius:5px;cursor:pointer;font-weight:600;">Clear Cart</button>`;
    html += `<button id="close-cart-modal" style="margin-top:1rem;background-color:#75757a;color:white;border:1px solid #75757a;padding:10px 20px;border-radius:5px;cursor:pointer;font-weight:600;">Close</button>`;
    modal.innerHTML = html;
    document.body.appendChild(modal);

    document.getElementById("close-cart-modal").onclick = function () {
      modal.remove();
    };
    document.getElementById("clear-cart-modal").onclick = function () {
      cart = [];
      localStorage.setItem("cart", JSON.stringify(cart));
      updateCartCount();
      modal.remove();
      // Re-enable all add-to-cart buttons and reset displays
      addToCartButtons.forEach(function (btn) {
        btn.disabled = false;
        btn.textContent = "Add to Cart";
        btn.setAttribute('data-quantity', '0');
        btn.setAttribute('data-shoe-quantity', '0');
      });
      document.querySelectorAll('.qty-display').forEach(display => {
        display.textContent = '0';
      });
    };
  }
});


  
