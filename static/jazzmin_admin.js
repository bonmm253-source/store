document.addEventListener('DOMContentLoaded', function() {
    // Target the password input on the login page
    const passwordField = document.querySelector('input[name="password"]');

    if (passwordField && document.body.classList.contains('login-page')) {
        // Create wrapper to hold input and icon
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';

        // Insert wrapper before password field and move field into it
        passwordField.parentNode.insertBefore(wrapper, passwordField);
        wrapper.appendChild(passwordField);

        // Add padding to input so text doesn't go under icon
        passwordField.style.paddingRight = '40px';

        // Create the toggle icon
        const icon = document.createElement('i');
        icon.className = 'fas fa-eye';
        icon.style.cssText = 'position: absolute; right: 12px; top: 50%; transform: translateY(-50%); cursor: pointer; color: #888; z-index: 10;';

        wrapper.appendChild(icon);

        icon.addEventListener('click', function() {
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);

            // Toggle eye icon
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }
});