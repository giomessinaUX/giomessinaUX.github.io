document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const contactsToggle = document.getElementById('contacts-toggle');
    const contactLinks = document.getElementById('contact-links');

    // Theme toggle
    themeToggle.addEventListener('click', function(e) {
        e.preventDefault();
        body.classList.toggle('dark-theme');
    });

    // Mobile contacts toggle
    contactsToggle.addEventListener('click', function() {
        if (window.innerWidth <= 900) {
            contactLinks.style.display = contactLinks.style.display === 'block' ? 'none' : 'block';
        }
    });

    // Reset contact links display on window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 900) {
            contactLinks.style.display = 'block';
        } else {
            contactLinks.style.display = 'none';
        }
    });
});