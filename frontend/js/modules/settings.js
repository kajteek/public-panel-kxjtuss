/**
 * Settings Module
 */
window.Settings = {
    init: function () {
        const isEnabled = localStorage.getItem('lea_ai_legal_search') === 'true';
        const checkbox = document.getElementById('setting-ai-legal-search');
        if (checkbox) {
            checkbox.checked = isEnabled;
        }
        this.updateNavVisibility(isEnabled);
    },

    toggleAiLegalSearch: function (enabled) {
        localStorage.setItem('lea_ai_legal_search', enabled);
        this.updateNavVisibility(enabled);
        
        console.log(`[LEA+ SETTINGS]: AI Legal Search ${enabled ? 'ENABLED' : 'DISABLED'}`);
    },

    updateNavVisibility: function (enabled) {
        const navItem = document.getElementById('nav-legal-search');
        const experimentalLabel = document.getElementById('nav-label-experimental');
        
        if (navItem) {
            navItem.style.display = enabled ? 'flex' : 'none';
        }
        if (experimentalLabel) {
            experimentalLabel.style.display = enabled ? 'block' : 'none';
        }

        // Phase 1: Disable "assistants" placeholder logic
        const penalAssistant = document.getElementById('penal-assistant-widget');
        const caselawAssistant = document.getElementById('caselaw-assistant-widget');
        if (penalAssistant) penalAssistant.style.display = enabled ? 'none' : 'block';
        if (caselawAssistant) caselawAssistant.style.display = enabled ? 'none' : 'block';
    }
};
