/**
 * LEA+ | Core Application Controller
 * Handles routing, module initialization, and global system states.
 */

window.App = {
    currentRoute: null,
    isNavigating: false,

    // Dynamic API Base URL depending on environment
    get API_URL() {
        return window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://localhost:5000/api'
            : 'https://TWOJ-BACKEND-NA-RENDER.onrender.com/api'; // Replace with actual Render URL
    },

    get API_BASE_URL() {
        return this.API_URL + '/generate';
    },

    /**
     * System Initialization
     */
    init: function () {
        console.log("%c[LEA+ SYSTEM]: Initializing ARCHITECT HUD...", "color: #3b82f6; font-weight: bold;");

        // Global Error Handling for Debugging
        window.addEventListener('error', function (event) {
            console.error('[LEA+ GLOBAL ERROR]:', event.error || event.message);
            // Optionally show on UI if in a critical state
            const mount = document.getElementById('app-mount');
            if (mount && mount.innerHTML.includes('hud-loader')) {
                mount.innerHTML = `<div style="color:red; padding:20px;">CRITICAL ERROR: ${event.message}</div>`;
            }
        });

        // Start Global Clock
        this.startClock();

        // Initial Route
        this.route('dashboard');

        // Global Event Listeners
        this.bindGlobalEvents();

        // Check experimental features
        const checkExperimental = () => {
            if (window.Settings) {
                window.Settings.updateNavVisibility(localStorage.getItem('lea_ai_legal_search') === 'true');
            } else {
                setTimeout(checkExperimental, 50);
            }
        };
        checkExperimental();
    },

    /**
     * Handles Routing between different app modules
     * @param {string} moduleId 
     */
    route: function (moduleId) {
        if (this.currentRoute === moduleId) return;

        console.log(`[LEA+ ROUTER]: Navigating to ${moduleId}`);

        // Update Sidebar UI
        document.querySelectorAll('.hud-nav-item').forEach(el => el.classList.remove('active'));
        const activeNav = document.getElementById('nav-' + moduleId);
        if (activeNav) activeNav.classList.add('active');

        // Load content into viewport
        this.loadViewport(moduleId);

        this.currentRoute = moduleId;
    },

    /**
     * Loads the HTML view and initializes the corresponding JS module
     * @param {string} moduleId 
     */
    loadViewport: async function (moduleId) {
        if (this.isNavigating) return;
        this.isNavigating = true;

        const mount = document.getElementById('app-mount');
        if (!mount) return;

        // Show HUD specific loader
        mount.innerHTML = '<div class="hud-loader" style="margin:auto; display:block; margin-top:20%"></div>';

        try {
            const response = await fetch(`views/${moduleId}.html?v=${Date.now()}`);
            if (!response.ok) throw new Error(`Failed to load view: ${moduleId}`);

            const html = await response.text();
            mount.innerHTML = html;

            // Ensure the view is visible (matches layout.css .app-view.active)
            const viewEl = mount.firstElementChild;
            if (viewEl && viewEl.classList.contains('app-view')) {
                viewEl.classList.add('active');
            }

            // Initialize Module Script
            this.initSelectedModule(moduleId);

            this.isNavigating = false;
        } catch (error) {
            this.isNavigating = false;
            console.error("[LEA+ ERROR]:", error);
            mount.innerHTML = `
                <div style="padding: 2rem; color: #ef4444; text-align: center;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                    <h3>VOIDSYSTEM ERROR</h3>
                    <p>${error.message}</p>
                </div>
            `;
        }
    },

    /**
     * Map moduleId to the specific Window object and call .init()
     */
    initSelectedModule: function (moduleId) {
        const moduleMap = {
            'dashboard': 'Dashboard',
            'paperwork': 'Paperwork',
            'penal-code': 'PenalCode',
            'calculator': 'Calculator',
            'map': 'LEAMap',
            'parser': 'Parser',
            'caseboard': 'CaseBoard',
            'caselaws': 'Caselaws',
            'settings': 'Settings',
            'legal-search': 'LegalSearch'
        };

        const globalObjectName = moduleMap[moduleId];
        if (globalObjectName && window[globalObjectName] && typeof window[globalObjectName].init === 'function') {
            console.log(`[LEA+ MODULE]: Starting ${globalObjectName}...`);
            window[globalObjectName].init();
        }
    },

    /**
     * Real-time HUD Clock
     */
    startClock: function () {
        const clockEl = document.getElementById('hud-clock');
        const update = () => {
            const now = new Date();
            const timeStr = now.getUTCHours().toString().padStart(2, '0') + ":" +
                now.getUTCMinutes().toString().padStart(2, '0') + ":" +
                now.getUTCSeconds().toString().padStart(2, '0');
            if (clockEl) clockEl.textContent = timeStr;
        };
        update();
        setInterval(update, 1000);
    },

    /**
     * Global Search Implementation (Placeholder)
     */
    globalSearch: function (query) {
        console.log("[LEA+ SEARCH]:", query);
        // Implement global filtering or search logic here
    },

    /**
     * Logout / Reset Session
     */
    logout: function () {
        if (confirm("Reset current HUD session?")) {
            window.location.reload();
        }
    },

    bindGlobalEvents: function () {
        // Handle Escape to close modals etc.
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (window.UI && window.UI.closeModal) {
                    // This is a bit generic but works for now
                    document.querySelectorAll('.cb-modal.active, .hud-modal.active').forEach(m => {
                        m.classList.remove('active');
                    });
                }
            }
        });
    }
};

// Auto-boot on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
