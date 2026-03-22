/**
 * Penal Code Module
 */
window.PenalCode = {
    data: {},
    activeCategory: 'ALL',

    init: async function () {
        try {
            const res = await fetch('data/devg-data/devg_penal_code.json');
            if (!res.ok) throw new Error("Fetch failed");
            this.data = await res.json();

            // Share data with Calculator if needed to prevent double fetch
            if (window.Calculator) window.Calculator.penalCodeData = this.data;

            const searchInput = document.getElementById('penal-search');
            if (searchInput) {
                searchInput.addEventListener('input', () => this.applyFilters());
            }

            this.renderList(Object.values(this.data).filter(i => i.id !== "000"));
        } catch (e) {
            console.error("Penal Code load fail", e);
        }
    },

    selectFilter: function (value, label) {
        this.activeCategory = value;
        document.getElementById('penal-filter-selected').textContent = label;

        // Update active class
        document.querySelectorAll('#penal-filter-menu .dropdown-item').forEach(item => {
            if (item.getAttribute('onclick').includes(`'${value}'`)) item.classList.add('active');
            else item.classList.remove('active');
        });

        UI.toggleDropdown('penal-filter-menu');
        this.applyFilters();
    },

    applyFilters: function () {
        const term = document.getElementById('penal-search').value.toLowerCase();
        const category = this.activeCategory;

        const items = Object.values(this.data).filter(i => {
            if (i.id === "000") return false;
            const matchesSearch = i.charge.toLowerCase().includes(term) || (i.definition && i.definition.toLowerCase().includes(term)) || i.id.includes(term);
            const matchesCategory = category === 'ALL' || i.type === category;
            return matchesSearch && matchesCategory;
        });
        this.renderList(items);
    },

    renderList: function (items) {
        const list = document.getElementById('penal-list');
        if (!list) return;

        list.innerHTML = items.map(item => {
            const tag = item.type.toLowerCase();
            return `
                <div class="hud-card">
                    <div class="card-header">
                        <span class="hud-tag tag-${tag}">${item.type === 'F' ? 'Felony' : (item.type === 'M' ? 'Misdemeanor' : 'Infraction')}</span>
                        <span style="font-family:'JetBrains Mono'; font-size:0.75rem; opacity:0.5">#${item.id}</span>
                    </div>
                    <h3 style="font-size:1.1rem; margin-bottom:0.75rem">${item.charge}</h3>
                    <p style="font-size:0.8rem; color:hsl(var(--h) 10% 60%); line-height:1.5; margin-bottom:1.5rem">
                        ${item.definition || 'No definition available.'}
                    </p>
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; border-top:1px solid hsl(var(--border-light)); margin-top:1rem; padding-top:1rem">
                        <span>Grzywna: <strong style="color:hsl(var(--primary))">$${item.fine['1']} - $${item.fine['3']}</strong></span>
                        <span>Czas: <strong style="color:hsl(var(--primary))">${item.time.days}d ${item.time.hours}h</strong></span>
                    </div>
                </div>
            `;
        }).join('');
    }
};
