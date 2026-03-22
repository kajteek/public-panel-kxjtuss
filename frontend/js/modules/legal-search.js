/**
 * Legal Search AI Module
 */
window.LegalSearch = {
    init: function () {
        console.log("[LEA+ LEGAL SEARCH]: Initializing AI Research Hub...");

        const input = document.getElementById('ai-search-input');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.performSearch();
            });
        }
    },

    setQuery: function (text) {
        const input = document.getElementById('ai-search-input');
        if (input) {
            input.value = text;
            this.performSearch();
        }
    },

    performSearch: async function () {
        const query = document.getElementById('ai-search-input').value.trim();
        if (!query) return;

        const resultsArea = document.getElementById('ai-results');
        const loadingArea = document.getElementById('ai-loading');
        const progressFill = document.getElementById('search-progress');

        // Reset UI
        resultsArea.style.display = 'none';
        loadingArea.style.display = 'block';
        progressFill.style.width = '10%';

        try {
            // Fake progress
            const interval = setInterval(() => {
                const curr = parseInt(progressFill.style.width);
                if (curr < 85) progressFill.style.width = (curr + 5) + '%';
            }, 300);

            const response = await fetch(`${App.API_URL}/legal-search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });

            clearInterval(interval);
            progressFill.style.width = '100%';

            if (!response.ok) throw new Error('AI Hub Connection Error');

            const data = await response.json();

            // Wait a bit for the progress bar to finish "feeling"
            setTimeout(() => {
                loadingArea.style.display = 'none';
                this.renderResults(data);
            }, 300);

        } catch (error) {
            console.error('[LEA+ AI ERROR]:', error);
            loadingArea.style.display = 'none';
            alert('Failed to connect to LEA+ AI: ' + error.message);
        }
    },

    renderResults: function (data) {
        const resultsArea = document.getElementById('ai-results');
        resultsArea.style.display = 'block';

        // 1. Explanation - Wrap PC citations in badges using the [PC: ...] tag or the fallback regex
        let explanation = data.explanation || 'No explanation provided.';

        // Match the explicit tag [PC: ...]
        const pcTagRegex = /\[PC:\s*(.*?)\]/g;
        explanation = explanation.replace(pcTagRegex, '<span class="pc-badge">$1</span>');

        // Fallback for any missed plain "punkt P.C" mentions (though the prompt should prevent this)
        const fallbackRegex = /(?<!<span class="pc-badge">)(punkt P\.C \d+(?:\s+(?!(?:punkt|lub|oraz|i)\b)[^.]+)+)/g;
        explanation = explanation.replace(fallbackRegex, '<span class="pc-badge">$1</span>');

        document.getElementById('ai-explanation-text').innerHTML = explanation;

        // 2. Penal Code
        const penalCont = document.getElementById('ai-penal-results');
        if (data.penal_code_results && data.penal_code_results.length > 0) {
            penalCont.innerHTML = data.penal_code_results.map(item => `
                <div class="hud-card" style="padding: 1rem; border-color: hsla(var(--status-${item.type === 'F' ? 'felony' : (item.type === 'M' ? 'misdemeanor' : 'infraction')}), 0.2)">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem;">
                        <span class="hud-tag tag-${item.type.toLowerCase()}">${item.type === 'F' ? 'Felony' : (item.type === 'M' ? 'Misdemeanor' : 'Infraction')}</span>
                        <span style="font-family:'JetBrains Mono'; font-size: 0.7rem; opacity: 0.5">#${item.id}</span>
                    </div>
                    <h4 style="font-size: 0.95rem; margin-bottom: 0.5rem;">${item.name}</h4>
                    <p style="font-size: 0.8rem; color: rgba(255,255,255,0.4); line-height: 1.4;">${item.definition}</p>
                </div>
            `).join('');
        } else {
            penalCont.innerHTML = '<p style="font-size: 0.8rem; opacity: 0.5;">No specific penal code charges identified.</p>';
        }

        // 3. Caselaw
        const caselawCont = document.getElementById('ai-caselaw-results');
        if (data.caselaw_result) {
            const c = data.caselaw_result;
            caselawCont.innerHTML = `
                <div class="hud-card" style="padding: 1.25rem; border-color: rgba(255,255,255,0.1)">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem;">
                        <span style="font-size: 0.7rem; color: hsl(var(--primary)); text-transform: uppercase; font-weight: 700; letter-spacing: 1px;">Precedent Case</span>
                        <span style="font-family:'JetBrains Mono'; font-size: 0.7rem; opacity: 0.5">${c.year}</span>
                    </div>
                    <h4 style="font-size: 1rem; margin-bottom: 0.75rem;">${c.case}</h4>
                    <p style="font-size: 0.85rem; margin-bottom: 1rem;">${c.summary}</p>
                    <div style="padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05); font-size: 0.8rem;">
                        <strong style="color: hsl(var(--primary));">IMPLICATION:</strong> ${c.implication}
                    </div>
                </div>
            `;
        } else {
            caselawCont.innerHTML = '<p style="font-size: 0.8rem; opacity: 0.5;">No relevant local caselaw found.</p>';
        }

        // 4. Oyez Cases
        const oyezCont = document.getElementById('ai-oyez-results');
        if (data.oyez_cases && data.oyez_cases.length > 0) {
            oyezCont.innerHTML = data.oyez_cases.map((item, index) => `
                <div class="hud-card oyez-accordion" style="margin-bottom: 0.5rem; border-color: rgba(255,255,255,0.05); overflow: hidden; display: flex; flex-direction: column; cursor: pointer;">
                    <div class="oyez-header" onclick="this.parentElement.classList.toggle('expanded')" style="display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1rem; background: rgba(255,255,255,0.02); transition: background 0.2s;">
                        <span style="font-size: 0.85rem; color: #fff; font-weight: 600;">${item.name}</span>
                        <i class="fas fa-chevron-down oyez-icon" style="font-size: 0.7rem; opacity: 0.5; transition: transform 0.3s;"></i>
                    </div>
                    <div class="oyez-content" style="max-height: 0; transition: max-height 0.3s ease-out, padding 0.3s ease-out; opacity: 1; font-size: 0.8rem; line-height: 1.5; overflow: hidden; display: flex; flex-direction: column;">
                        <p style="margin: 0 1rem; padding-top: 1rem; opacity: 0.8;">${item.summary || 'Brak dodatkowego opisu dla tego precedensu.'}</p>
                        <div style="padding: 1rem;">
                            <a href="${item.href}" target="_blank" class="hud-card" style="display: flex; align-items: center; justify-content: center; width: 100%; padding: 0.5rem; font-size: 0.75rem; text-decoration: none; border-color: rgba(255,255,255,0.1); background: rgba(0, 162, 255, 0.1); color: #fff; transition: background 0.2s, background-color 0.2s;">
                                <span style="font-weight: 600;">PRZEJDŹ DO SPRAWY (OYEZ)</span>
                                <i class="fas fa-external-link-alt" style="margin-left: 8px; opacity: 0.7;"></i>
                            </a>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            oyezCont.innerHTML = '<p style="font-size: 0.8rem; opacity: 0.5;">No external precedents suggested.</p>';
        }

        // Scroll into view
        resultsArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
};
