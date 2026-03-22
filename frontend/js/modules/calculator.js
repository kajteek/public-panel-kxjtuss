/**
 * Calculator Module
 */
window.Calculator = {
    penalCodeData: {},
    selectedCharges: [],

    init: async function () {
        if (Object.keys(this.penalCodeData).length === 0) {
            try {
                const res = await fetch('data/devg-data/devg_penal_code.json');
                const data = await res.json();
                this.penalCodeData = data;
            } catch (e) { console.error("Calc init fail", e); }
        }

        const searchInput = document.getElementById('calc-search');
        if (searchInput) {
            searchInput.addEventListener('input', () => this.renderList());
        }

        const clearBtn = document.getElementById('calc-clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.selectedCharges = [];
                this.renderList();
            });
        }

        const copyBtn = document.getElementById('calc-copy-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyCharges());
        }

        this.renderList();
    },

    copyCharges: function () {
        if (this.selectedCharges.length === 0) return;

        const textToCopy = this.selectedCharges.map(sc => {
            const c = this.penalCodeData[sc.id];
            return `${c.id}. ${c.charge} (${c.type})`;
        }).join(', ');

        navigator.clipboard.writeText(textToCopy).then(() => {
            const btn = document.getElementById('calc-copy-btn');
            if (btn) {
                const originalHTML = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check" style="margin-right: 6px;"></i> SKOPIOWANO';
                btn.style.background = 'rgba(16, 185, 129, 0.2)';
                btn.style.borderColor = '#10b981';
                btn.style.color = '#10b981';

                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.style.background = 'rgba(59, 130, 246, 0.15)';
                    btn.style.borderColor = 'hsl(var(--primary))';
                    btn.style.color = '#fff';
                }, 2000);
            }
        });
    },

    renderList: function () {
        const list = document.getElementById('calc-charge-list');
        if (!list) return;

        const term = (document.getElementById('calc-search')?.value || "").toLowerCase();

        let charges = Object.values(this.penalCodeData).filter(c => c.id !== "000");
        if (term) {
            charges = charges.filter(c => c.charge.toLowerCase().includes(term) || c.id.includes(term));
        }

        list.innerHTML = charges.map(c => {
            const isSelected = this.selectedCharges.find(sc => sc.id === c.id);
            const months = c.time.hours;
            const fine = parseInt(c.fine['1'] || 0);

            let catClass = 'tag-m';
            let catName = 'Misdemeanor';
            if (c.type === 'F') { catClass = 'tag-f'; catName = 'Felony'; }
            if (c.type === 'I') { catClass = 'tag-i'; catName = 'Infraction'; }

            return `
            <div class="charge-card ${isSelected ? 'selected' : ''}" onclick="Calculator.toggleCharge('${c.id}')">
                <div class="charge-card-info">
                    <div class="charge-card-header">
                        <span class="calc-tag ${catClass}">${catName}</span>
                        <span class="charge-card-title">${c.charge}</span>
                    </div>
                    <div class="charge-card-stats">
                        <span class="stat">Time: <span class="val">${months} mies.</span></span>
                        <span class="stat">Fine: <span class="val">$${fine.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></span>
                    </div>
                </div>
                <div class="charge-radio"></div>
            </div>
        `}).join('');

        this.updateSummary();
    },

    toggleCharge: function (id) {
        const idx = this.selectedCharges.findIndex(c => c.id === id);
        if (idx > -1) {
            this.selectedCharges.splice(idx, 1);
        } else {
            this.selectedCharges.push({ id, offense: 1 });
        }
        this.renderList();
    },

    updateSummary: function () {
        const totalTimeEl = document.getElementById('calc-total-time');
        const totalFineEl = document.getElementById('calc-total-fine');
        const selectedCountEl = document.getElementById('calc-selected-count');
        const selectedListEl = document.getElementById('calc-selected-list');
        const clearBtn = document.getElementById('calc-clear-btn');
        const copyBtn = document.getElementById('calc-copy-btn');

        if (!totalTimeEl || !totalFineEl) return;

        let m = 0; let f = 0;

        this.selectedCharges.forEach(sc => {
            const c = this.penalCodeData[sc.id];
            if (!c) return;
            m += c.time.hours; // 1 hour = 1 month
            f += parseInt(c.fine['1'] || 0);
        });

        totalTimeEl.textContent = m;
        totalFineEl.textContent = `$${f.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        selectedCountEl.textContent = this.selectedCharges.length;

        if (this.selectedCharges.length === 0) {
            if (clearBtn) clearBtn.style.display = 'none';
            if (copyBtn) copyBtn.style.display = 'none';
            selectedListEl.innerHTML = `
                <div class="empty-state" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100px; color: hsl(var(--h) 10% 30%); gap: 10px;">
                    <i class="fas fa-shield-alt" style="font-size: 1.5rem;"></i>
                    <span style="font-size: 0.8rem;">No charges selected.</span>
                </div>
            `;
        } else {
            if (clearBtn) clearBtn.style.display = 'block';
            if (copyBtn) copyBtn.style.display = 'block';
            selectedListEl.innerHTML = this.selectedCharges.map(sc => {
                const c = this.penalCodeData[sc.id];
                return `<div style="font-size: 0.85rem; color: hsl(var(--h) 10% 70%); padding: 5px 0;">• ${c.charge}</div>`;
            }).join('');
        }
    }
};
