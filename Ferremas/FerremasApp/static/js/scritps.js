document.addEventListener("DOMContentLoaded", function() {

    document.querySelectorAll('.dropdown-submenu .dropdown-toggle').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            var submenu = this.nextElementSibling;
            submenu.classList.toggle('show');
        });
    });


    document.addEventListener('click', function(e) {
        document.querySelectorAll('.dropdown-submenu .dropdown-menu').forEach(function(submenu) {
            submenu.classList.remove('show');
        });
    });
});