

document.addEventListener('DOMContentLoaded', function() {
  const accountBtn = document.getElementById('btn');
  const dropdownContent = document.getElementById('content');

  if (accountBtn && dropdownContent) {
    accountBtn.addEventListener('click', function() {
      dropdownContent.classList.toggle('hidden');
    });

    // Optional: hide dropdown if clicking outside
    window.addEventListener('click', function(e) {
      if (!e.target.matches('#btn')) {
        dropdownContent.classList.add('hidden');
      }
    });
    } else {
    console.log("❌ Elements not found!");
  }
});