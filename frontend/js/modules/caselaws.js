/**
 * LEA+ | Caselaws & Precedents Module
 * Handles loading and searching legal precedents.
 */

window.Caselaws = {
    data: [],
    container: null,
    searchInput: null,

    init: function () {
        console.log("[LEA+ CASELAWS]: Initializing...");
        this.container = document.getElementById('cl-grid');
        this.searchInput = document.getElementById('cl-search-input');

        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
            this.searchInput.placeholder = "Szukaj wg nazwy, opisu lub konsekwencji...";
        }

        this.loadData();
    },

    loadData: async function () {
        try {
            const response = await fetch(`data/caselaws.json?t=${new Date().getTime()}`);
            if (!response.ok) throw new Error("Failed to load caselaws data");

            const json = await response.ok ? await response.json() : { caselaws: [] };
            this.data = json.caselaws;
            this.render(this.data);
        } catch (error) {
            console.error("[LEA+ CASELAWS ERROR]:", error);
            if (this.container) {
                this.container.innerHTML = `<div class="cl-no-results"><i class="fas fa-exclamation-circle"></i><p>ERROR LOADING DATA: ${error.message}</p></div>`;
            }
        }
    },

    render: function (items) {
        if (!this.container) return;

        if (items.length === 0) {
            this.container.innerHTML = `
                <div class="cl-no-results">
                    <i class="fas fa-folder-open"></i>
                    <p>Nie odnaleziono precedensów spełniających Twoje kryteria.</p>
                </div>
            `;
            return;
        }

        this.container.innerHTML = items.map(item => `
            <div class="cl-card juris-${item.jurisdiction.split('-')[0]}" data-id="${item.id}">
                <div class="cl-card-header">
                    <div class="cl-title-box">
                        <h3 class="cl-title">${item.case}</h3>
                        <div class="cl-meta">
                            <span class="cl-badge"><i class="fas fa-gavel"></i> ${item.jurisdiction.replace('-', ' ')}</span>
                            <span class="cl-year"><i class="far fa-calendar-alt"></i> ${item.year}</span>
                        </div>
                    </div>
                </div>

                <div class="cl-content-section">
                    <span class="cl-label"><i class="fas fa-info-circle"></i> Podsumowanie</span>
                    <p class="cl-summary">${item.summary}</p>
                </div>

                <div class="cl-content-section">
                    <span class="cl-label"><i class="fas fa-scale-balanced"></i> Konsekwencje Prawne</span>
                    <div class="cl-implication">
                        ${item.implication}
                    </div>
                </div>

                <div class="cl-footer">
                    <a href="${item.source}" target="_blank" class="cl-link">
                        <i class="fas fa-external-link-alt"></i> ZOBACZ CASELAW
                    </a>
                </div>
            </div>
        `).join('');
    },

    handleSearch: function (query) {
        const q = query.toLowerCase().trim();
        if (!q) {
            this.render(this.data);
            return;
        }

        const filtered = this.data.filter(item => {
            return item.case.toLowerCase().includes(q) ||
                item.summary.toLowerCase().includes(q) ||
                item.implication.toLowerCase().includes(q) ||
                item.jurisdiction.toLowerCase().includes(q);
        });

        this.render(filtered);
    }
};
