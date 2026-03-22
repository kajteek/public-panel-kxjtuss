/**
 * LEA+ Global UI Interactions
 * Prevents redundant listeners across modules for things like generic dropdowns.
 */
window.UI = {
    toggleDropdown: function (menuId) {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            if (menu.id !== menuId) menu.classList.remove('active');
        });
        const target = document.getElementById(menuId);
        if (target) target.classList.toggle('active');
    },

    openModal: function (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('active');
    },

    closeModal: function (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('active');
    }
};

// Global click listener to close dropdowns if clicked outside
window.addEventListener('click', (e) => {
    // Specifically ignore caseboard dropdowns gracefully or handle everything here
    if (!e.target.closest('.hud-dropdown')) {
        document.querySelectorAll('.dropdown-menu').forEach(menu => menu.classList.remove('active'));
    }
});
