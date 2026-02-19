window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 800) {
        navbar.classList.add('scrolled');
        navbar.classList.remove('bg-transparent');
    } else {
        navbar.classList.remove('scrolled');
        navbar.classList.add('bg-transparent');
    }
});
