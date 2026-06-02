document.addEventListener("DOMContentLoaded", function () {
  const cartCount = document.querySelector(".cart-count");
  const addToCartButtons = document.querySelectorAll(".add-to-cart-btn");
  const cartIcon = document.querySelector(".cart-count").parentElement;


  // Load cart from localStorage
  let cart = JSON.parse(localStorage.getItem("cart")) || [];
  // Older items might not have `quantity` or `rating` — default to sensible values
  cart = cart.map((it) => ({ ...it, quantity: it.quantity || 1, rating: it.rating || 0 }));
  updateCartCount();

  addToCartButtons.forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      // normalize watchId to string to avoid type mismatches
      const rawId = btn.getAttribute("data-watch-id") || btn.dataset.watchId;
      const watchId = String(rawId);

      // Get quantity from data-shoe-quantity (set by quantity controls) or default to 1
      const selectedQty = parseInt(btn.getAttribute("data-watch-quantity") || "1", 10) || 1;

      // Find existing item by normalized id
      const existing = cart.find((item) => String(item.watchId) === watchId);
      // Read selected rating (set when user clicks stars)
      const selectedRating = parseInt(btn.getAttribute('data-watch-rating') || btn.dataset.watchRating || '0', 10) || 0;
      if (existing) {
        // Ensure quantity is an integer
        existing.quantity = parseInt(existing.quantity, 10) || 1;
        // update rating to latest selected rating if provided
        if (selectedRating > 0) existing.rating = selectedRating;
        // Add the selected quantity to existing quantity, max 5
        existing.quantity = Math.min(5, existing.quantity + selectedQty);
        localStorage.setItem("cart", JSON.stringify(cart));
        updateCartCount();
        btn.textContent = `Added (${existing.quantity})`;
        btn.disabled = existing.quantity >= 5;
      } else {
        const watchImage = btn.getAttribute("data-watch-image") || btn.dataset.watchImage || "";
        const watchName = btn.getAttribute("data-watch-name") || btn.dataset.watchName || "";
        const watchBrand = btn.getAttribute("data-watch-brand") || btn.dataset.watchBrand || "";
        const watchPrice = btn.getAttribute("data-watch-price") || btn.dataset.shoePrice || "0";
        // Use selected quantity, not just 1
        const addQty = Math.min(5, selectedQty);
        cart.push({ watchId, watchImage, watchName, watchBrand, watchPrice, quantity: addQty, rating: selectedRating });
        localStorage.setItem("cart", JSON.stringify(cart));
        updateCartCount();
        btn.disabled = false;
        btn.textContent = `Added (${addQty})`;
      }
      // prevent accidental form submit if button is inside a form
      if (e && typeof e.preventDefault === 'function') e.preventDefault();
    });
  });

  // Wire plus/minus buttons that live inside each `.shoe` element.
  // These buttons are plain <button>+/-</button> siblings of the add-to-cart button in the template.
  const watchEls = document.querySelectorAll('.watch');
  watchEls.forEach(function (watchEl) {
    const addBtn = watchEl.querySelector('.add-to-cart-btn');
    if (!addBtn) return;

    // Wire up star rating clicks inside this `.shoe` element.
    const ratingEl = watchEl.querySelector('.rating');
    if (ratingEl) {
      const stars = Array.from(ratingEl.querySelectorAll('.star'));
      // initialize from data attribute if present
      const initial = parseInt(addBtn.getAttribute('data-watch-rating') || addBtn.dataset.watchRating || '0', 10) || 0;
      if (initial > 0) stars.forEach((st, i) => st.classList.toggle('filled', i < initial));

      stars.forEach(function (star, idx) {
        star.style.cursor = 'pointer';
        star.addEventListener('click', function (e) {
          e.preventDefault();
          const rating = idx + 1;
          stars.forEach((s, i) => s.classList.toggle('filled', i < rating));
          // store selected rating on the add-to-cart button so other handlers can read it
          addBtn.dataset.watchRating = String(rating);
          addBtn.setAttribute('data-watch-rating', String(rating));
          // If this product is already in the cart, update its rating immediately
          try {
            const rawId = addBtn.getAttribute('data-watch-id') || addBtn.dataset.watchId;
            const watchId = String(rawId);
            const cartItem = cart.find((i) => String(i.watchId) === watchId);
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
            // fail silently — rating persistence is non-critical
            console.error('Error updating rating in cart:', err);
          }
        });
      });
    }

    // attempt to find plus/minus buttons inside the immediate div following the add button
    const btnContainer = addBtn.nextElementSibling || watchEl.querySelector('div');
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
        const rawId = addBtn.getAttribute('data-watch-id') || addBtn.dataset.watchId;
        const watchId = String(rawId);
        let item = cart.find((i) => String(i.watchId) === watchId);
        if (item) {
          item.quantity = parseInt(item.quantity, 10) || 1;
          if (item.quantity < 5) item.quantity = Math.min(5, item.quantity + 1);
        } else {
          const shoeImage = addBtn.getAttribute('data-watch-image') || addBtn.dataset.shoeImage || "";
          const shoeName = addBtn.getAttribute('data-watch-name') || addBtn.dataset.shoeName || "";
          const shoeBrand = addBtn.getAttribute('data-watch-brand') || addBtn.dataset.shoeBrand || "";
          const shoePrice = addBtn.getAttribute('data-watch-price') || addBtn.dataset.shoePrice || "0";
          const shoeRating = parseInt(addBtn.getAttribute('data-watch-rating') || addBtn.dataset.shoeRating || '0', 10) || 0;
          cart.push({ shoeId, shoeImage, shoeName, shoeBrand, shoePrice, quantity: 1, rating: shoeRating });
        }
        persistAndRefresh();
      });
    }

    if (minusBtn) {
      minusBtn.addEventListener('click', function (e) {
        e.preventDefault();
        const rawId = addBtn.getAttribute('data-watch-id') || addBtn.dataset.watchId;
        const watchId = String(rawId);
        let idx = cart.findIndex((i) => String(i.watchId) === watchId);
        if (idx === -1) return; // nothing to decrease
        const item = cart[idx];
        item.quantity = parseInt(item.quantity, 10) || 1;
        item.quantity = item.quantity - 1;
        if (item.quantity <= 0) {
          cart.splice(idx, 1);
        }
        persistAndRefresh();
      });
    }
  });

  // Ensure buttons reflect current cart quantities on load
  function refreshButtons() {
    addToCartButtons.forEach(function (btn) {
      const watchId = btn.getAttribute("data-watch-id");
      const item = cart.find((i) => i.watchId === watchId);
      if (item) {
        btn.disabled = item.quantity >= 5;
        btn.textContent = `Added (${item.quantity})`;
      } else {
        btn.disabled = false;
        btn.textContent = "Add to Cart";
      }
    });
  }

  cartIcon.addEventListener("click", function () {
    showCartModal();
  });

  function updateCartCount() {
    // Count total items (sum of quantities)
    const total = cart.reduce((sum, it) => sum + (it.quantity || 0), 0);
    cartCount.textContent = total;
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
    
    

    let html = `<h2>Cart Items</h2>`;
  let totalPrice = 0;
  let totalPriceUSD = 0;
    if (cart.length === 0) {
      html += `<p>Your cart is empty.</p>`;
    } else {
      cart.forEach(function (item) {
        const qty = item.quantity || 1;
        let priceUSD = parseFloat(item.watchPrice) || 0;
        let subtotalUSD = priceUSD * qty;
        let subtotalNGN = subtotalUSD * 1500;
        totalPriceUSD += subtotalUSD;
        totalPrice += subtotalNGN;
        // build a small star display if rating present
        let starHtml = '';
        const ratingVal = parseInt(item.rating || 0, 10) || 0;
        if (ratingVal > 0) {
          for (let i = 1; i <= 5; i++) {
            starHtml += `<span style="color:${i<=ratingVal?'gold':'#ddd'};font-size:14px;margin-right:2px">★</span>`;
          }
        }
        html += `<div style="display:flex;background:#f9f9f9;border-radius:10px;padding:1rem;margin-bottom:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.07);text-align:center;align-items:center;">
          <img src="${item.watchImage}" alt="${item.watchName}" style="width:60px;height:70px;object-fit:cover;border-radius:8px;margin-bottom:10px;border:1px solid #eee;display:flex;margin-left:auto;margin-right:auto;">
          <div style="margin-bottom:6px;margin-left:12px;flex:1;text-align:left;">
            <span style="font-weight:bold;font-size:1.1rem;">${item.watchName}</span><br>
            <span style="color:#555;">${item.watchBrand}</span><br>
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
    html += `<button id="clear-cart-modal" style="margin-top:1rem;margin-right:1rem;">Clear Cart</button>`;
    html += `<button id="close-cart-modal" style="margin-top:1rem;">Close</button>`;
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
      // Re-enable all add-to-cart buttons
      addToCartButtons.forEach(function (btn) {
        btn.disabled = false;
        btn.textContent = "Add to Cart";
      });
    };
  }
});
