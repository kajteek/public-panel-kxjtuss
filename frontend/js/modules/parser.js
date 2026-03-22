/**
 * Parser Module
 */
window.Parser = {
    init: function () {
        // Ready
    },

    parseLogs: function () {
        const input = document.getElementById('log-input').value;
        const lines = input.split('\n');
        const signals = lines.filter(l => l.includes('says') || l.includes('*') || l.includes('[Radio]'));

        const results = document.getElementById('parser-results');
        if (!results) return;

        results.innerHTML = `
            <div class="hud-card" style="border-color:hsl(var(--primary) / 0.3)">
                <span class="hud-label">Signals Extracted: ${signals.length}</span>
                <pre style="font-family:'JetBrains Mono'; font-size:0.75rem; color:hsl(var(--h) 10% 70%); background:rgba(0,0,0,0.3); padding:1rem; border-radius:8px; margin-top:1rem; max-height:300px; overflow:auto">
${signals.join('\n')}
                </pre>
            </div>
        `;
    }
};
