/**
 * Paperwork Factory Module
 */
window.Paperwork = {
    currentCategory: 'intelligence',
    currentMDCCategory: 'lspd',
    mdcTemplatesData: {},

    // Core structural templates
    templates: [
        {
            id: 'official_statement', name: 'News Release', icon: 'fa-newspaper',
            fields: [
                { id: 'doc_type', label: 'Document Type', type: 'select', options: ['News Release', 'Official Statement', 'Public Notice'] },
                { id: 'doc_number', label: 'Document Number', type: 'text', readOnly: true },
                { id: 'content', label: 'Content (Markdown)', type: 'textarea', placeholder: 'Use # for headers, - for lists...' }
            ]
        },
        {
            id: 'missing_person', name: 'Missing Person', icon: 'fa-search',
            fields: [
                { id: 'name', label: 'Full Name', type: 'text' },
                { id: 'age', label: 'Age', type: 'number' },
                { id: 'doc_number', label: 'Case Number', type: 'text', readOnly: true },
                { id: 'photo_url', label: 'Photo URL', type: 'photo' },
                { id: 'appearance', label: 'Appearance', type: 'textarea' },
                { id: 'missing_details', label: 'Missing Details', type: 'textarea' }
            ]
        },
        {
            id: 'wanted', name: 'Wanted Poster', icon: 'fa-user-secret',
            fields: [
                { id: 'alert_type', label: 'Alert Type (e.g. WANTED)', type: 'text', defaultValue: 'W POSZUKIWANIU' },
                { id: 'name', label: 'Full Name', type: 'text' },
                { id: 'details_line', label: 'Short Description', type: 'text', placeholder: 'e.g. 25 YEARS OLD | BLACK HAIR' },
                { id: 'doc_number', label: 'BOLO ID', type: 'text', readOnly: true },
                { id: 'photo_urls', label: 'Photo URLs (comma separated, max 4)', type: 'text' },
                { id: 'reasons', label: 'Reasons / Description of Crime', type: 'textarea' }
            ]
        },
        {
            id: 'internal_memo', name: 'Internal Memo', icon: 'fa-folder-open',
            fields: [
                { id: 'subject', label: 'Subject', type: 'text' },
                { id: 'doc_number', label: 'Memo ID', type: 'text', readOnly: true },
                { id: 'to', label: 'To', type: 'text' },
                { id: 'from', label: 'From', type: 'text' },
                { id: 'content', label: 'Content', type: 'textarea' }
            ]
        },
        {
            id: 'personnel_change', name: 'Personnel Change', icon: 'fa-user-edit',
            fields: [
                { id: 'full_name', label: 'Officer Full Name', type: 'text' },
                { id: 'doc_number', label: 'PC ID', type: 'text', readOnly: true },
                { id: 'old_rank', label: 'Previous Rank', type: 'text' },
                { id: 'new_rank', label: 'New Rank', type: 'text' },
                { id: 'details', label: 'Reason / Remarks', type: 'textarea' }
            ]
        },
        {
            id: 'disciplinary_action', name: 'Disciplinary Action', icon: 'fa-gavel',
            fields: [
                { id: 'full_name', label: 'Full Name', type: 'text' },
                { id: 'doc_number', label: 'DA ID', type: 'text', readOnly: true },
                { id: 'infraction', label: 'Infraction', type: 'text' },
                { id: 'penalty', label: 'Penalty', type: 'text' },
                { id: 'details', label: 'Event Details', type: 'textarea' }
            ]
        },
        {
            id: 'official_letter', name: 'Official Letter', icon: 'fa-envelope-open-text',
            fields: [
                { id: 'recipient', label: 'Recipient', type: 'text' },
                { id: 'doc_number', label: 'OL ID', type: 'text', readOnly: true },
                { id: 'subject', label: 'Subject', type: 'text' },
                { id: 'content', label: 'Letter Content', type: 'textarea' }
            ]
        },
        {
            id: 'division_letter', name: 'Division Letter', icon: 'fa-building',
            fields: [
                { id: 'division_key', label: 'Division', type: 'select', options: [
                    { value: 'metro', label: 'Metropolitan Division' },
                    { value: 'raed', label: 'Recruitment And Employment Division' },
                    { value: 'fod', label: 'Fiscal Operations Division' },
                    { value: 'fld', label: 'Firearms Licensing Division' },
                    { value: 'pd', label: 'Personnel Division' },
                    { value: 'cd', label: 'Communications Division' },
                    { value: 'bss', label: 'Behavioral Science Services' },
                    { value: 'dtp', label: 'Detective Training Program' },
                    { value: 'stp', label: 'Supervisor Training Program' },
                    { value: 'ftp', label: 'Field Training Program' },
                    { value: 'pcd', label: 'Public Communications Division' },
                    { value: 'iag', label: 'Internal Affairs Group' },
                    { value: 'rmalag', label: 'Risk Management And Legal Affairs Group' },
                    { value: 'fts', label: 'Firearms Training Section' },
                    { value: 'td', label: 'Traffic Division' },
                    { value: 'asd', label: 'Air Support Division' },
                    { value: 'missionrow', label: 'Patrol Division' },
                    { value: 'k9', label: 'K9' },
                    { value: 'bs', label: 'Bomb Squad' },
                    { value: 'fsd', label: 'Forensic Science Division' },
                    { value: 'git', label: 'Gang Impact Team' },
                    { value: 'db', label: 'Detective Bureau' },
                    { value: 'mcd', label: 'Major Crimes Division' },
                    { value: 'gnd', label: 'Gang & Narcotics Division' },
                    { value: 'gd', label: 'Mission Row Gang Detail' },
                    { value: 'slo', label: 'Senior Lead Program' }
                ] },
                { id: 'doc_number', label: 'DL ID', type: 'text', readOnly: true },
                { id: 'recipient', label: 'To', type: 'text' },
                { id: 'sender', label: 'From', type: 'text' },
                { id: 'subject', label: 'Subject', type: 'text' },
                { id: 'content', label: 'Content', type: 'textarea' }
            ]
        },
        {
            id: 'tweet', name: 'LEA Tweet', icon: 'fa-brands fa-twitter',
            fields: [
                { id: 'tw_date', label: 'Post date', type: 'text', defaultValue: 'March 20th' },
                { id: 'content', label: 'Tweet content', type: 'textarea' },
                { id: 'photo_url', label: 'Media URL (Optional)', type: 'photo' }
            ]
        }
    ],

    init: function () {
        this.renderGrid();
    },

    switchCategory: function (cat) {
        this.currentCategory = cat;
        document.querySelectorAll('.hud-tab').forEach(t => t.classList.remove('active'));
        const tabEl = document.getElementById(`tab-${cat === 'intelligence' ? 'intel' : 'mdc'}`);
        if (tabEl) tabEl.classList.add('active');

        const subFilters = document.getElementById('mdc-sub-filters');
        if (cat === 'mdc') {
            subFilters.style.display = 'flex';
            this.renderMDCSubFilters();
        } else {
            subFilters.style.display = 'none';
        }

        this.renderGrid();
    },

    renderMDCSubFilters: function () {
        const container = document.getElementById('mdc-sub-filters');
        const categories = ['standard', 'lspd', 'realistic', 'legacy', 'lssd', 'sadcr', 'sfm', 'special'];

        container.innerHTML = categories.map(cat => `
            <span class="sub-tab ${this.currentMDCCategory === cat ? 'active' : ''}" onclick="Paperwork.switchMDCCategory('${cat}')">${cat}</span>
        `).join('');
    },

    switchMDCCategory: function (cat) {
        this.currentMDCCategory = cat;
        document.querySelectorAll('.sub-tab').forEach(t => {
            if (t.textContent.toLowerCase() === cat) t.classList.add('active');
            else t.classList.remove('active');
        });
        this.renderGrid();
    },

    renderGrid: async function () {
        const grid = document.getElementById('template-selector-grid');
        if (!grid) return;
        grid.innerHTML = '<div class="hud-loader"></div>';

        if (this.currentCategory === 'intelligence') {
            grid.innerHTML = this.templates.map(tpl => `
                <div class="hud-card" style="cursor:pointer; text-align:center" onclick="Paperwork.openEditor('${tpl.id}', 'intelligence')">
                    <i class="fas ${tpl.icon}" style="font-size:2rem; color:hsl(var(--primary)); margin-bottom:1rem; opacity:0.8"></i>
                    <h4 style="font-size:0.85rem">${tpl.name}</h4>
                </div>
            `).join('');
        } else {
            try {
                const listRes = await fetch(`data/paperwork-generators/${this.currentMDCCategory}/manifest.json`);
                if (!listRes.ok) throw new Error("Manifest not found");
                const manifest = await listRes.json();
                const templateFiles = manifest.files || [];

                grid.innerHTML = '';
                for (const file of templateFiles) {
                    const tRes = await fetch(`data/paperwork-generators/${this.currentMDCCategory}/${file}`);
                    const tpl = await tRes.json();
                    this.mdcTemplatesData[tpl.id] = tpl;

                    const card = document.createElement('div');
                    card.className = 'hud-card h-full';
                    card.style.cursor = 'pointer';
                    card.style.transition = 'transform 0.2s, border-color 0.2s';

                    const faIcon = this.mapMDCtoFA(tpl.icon);
                    card.innerHTML = `
                        <div style="display:flex; flex-direction:column; align-items:center; height:100%; justify-content:center; gap:1rem; padding:1.5rem">
                            <div class="icon-circle" style="width:50px; height:50px; background:hsl(var(--primary) / 0.1); border-radius:50%; display:flex; align-items:center; justify-content:center">
                                <i class="fas ${faIcon}" style="font-size:1.4rem; color:hsl(var(--primary))"></i>
                            </div>
                            <div style="text-align:center">
                                <h4 style="font-size:0.85rem; font-weight:700; color:white; margin-bottom:0.5rem">${tpl.title}</h4>
                                <p style="font-size:0.65rem; color:rgba(255,255,255,0.4); line-height:1.4">${tpl.description || 'Standard MDC report'}</p>
                            </div>
                        </div>
                    `;
                    card.onmouseover = () => { card.style.borderColor = 'hsl(var(--primary))'; card.style.transform = 'translateY(-4px)'; };
                    card.onmouseout = () => { card.style.borderColor = ''; card.style.transform = ''; };
                    card.onclick = () => this.openEditor(tpl.id, 'mdc');
                    grid.appendChild(card);
                }
            } catch (e) {
                grid.innerHTML = `<div style="color:hsl(var(--error)); padding: 2rem">Failed to load MDC templates for ${this.currentMDCCategory}.</div>`;
            }
        }
    },

    mapMDCtoFA: function (icon) {
        const map = {
            'Car': 'fa-car', 'FileText': 'fa-file-alt', 'Shield': 'fa-shield-alt',
            'User': 'fa-user', 'Briefcase': 'fa-briefcase', 'AlertTriangle': 'fa-exclamation-triangle',
            'Search': 'fa-search', 'Gavel': 'fa-gavel', 'Lock': 'fa-lock',
            'Trash2': 'fa-trash-alt', 'UserX': 'fa-user-slash', 'Fingerprint': 'fa-fingerprint',
            'Scale': 'fa-balance-scale'
        };
        return map[icon] || 'fa-file-invoice';
    },

    openEditor: function (tid, type = 'intelligence') {
        let tpl = type === 'intelligence' ? this.templates.find(t => t.id === tid) : this.mdcTemplatesData[tid];
        if (!tpl) return;

        // Toggle Views
        document.getElementById('template-browser').style.display = 'none';
        document.getElementById('paperwork-editor-view').style.display = 'flex';

        // Update Metadata
        const typeBadge = document.getElementById('editor-type-badge');
        typeBadge.textContent = type === 'intelligence' ? 'Intelligence' : 'MDC Paperwork';
        typeBadge.className = `hud-tag ${type === 'intelligence' ? 'tag-i' : 'tag-m'}`;

        const titleEl = document.getElementById('editor-title');
        titleEl.textContent = tpl.name || tpl.title;
        titleEl.dataset.type = type;
        titleEl.dataset.id = tid;

        if (type === 'intelligence') {
            this.renderIntelForm(tpl);
            this.updatePreview(tid);
        } else {
            this.renderMDCForm(tpl);
            this.updateMDCPreview(tid);
        }
    },

    closeEditor: function () {
        document.getElementById('template-browser').style.display = 'flex';
        document.getElementById('paperwork-editor-view').style.display = 'none';
        document.getElementById('formatting-help-panel').style.display = 'none';
    },

    toggleFormattingHelp: function () {
        const panel = document.getElementById('formatting-help-panel');
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    },

    insertTag: function (open, close) {
        console.log(`[Paperwork] Inserting Tag: "${open}" / "${close}"`);
        // Find the active or primary textarea
        let textarea = document.activeElement;
        if (!textarea || textarea.tagName !== 'TEXTAREA') {
            textarea = document.querySelector('#doc-form-fields textarea');
        }

        if (!textarea) return;

        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const text = textarea.value;
        const before = text.substring(0, start);
        const after = text.substring(end, text.length);
        const selected = text.substring(start, end);
        const closeTag = close || '';

        textarea.value = before + open + selected + closeTag + after;

        // Reset focus and selection
        textarea.focus();
        const cursorPos = start + open.length + selected.length;
        textarea.setSelectionRange(cursorPos, cursorPos);

        // Trigger live update
        if (textarea.oninput) textarea.oninput();
    },

    debounce: function (func, wait) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func(...args), wait);
        };
    },

    renderIntelForm: function (tpl) {
        const container = document.getElementById('doc-form-fields');
        container.innerHTML = '';
        const debouncedUpdate = this.debounce(() => this.updatePreview(tpl.id), 300);

        tpl.fields.forEach(f => {
            const group = document.createElement('div');
            group.className = 'hud-form-group';
            group.innerHTML = `<label class="hud-label">${f.label}</label>`;

            let input;
            if (f.type === 'textarea') {
                input = document.createElement('textarea');
                input.className = 'hud-input-ctrl';
                input.style.height = '120px';
            } else if (f.type === 'select') {
                input = document.createElement('select');
                input.className = 'hud-input-ctrl';
                f.options.forEach(opt => {
                    const o = document.createElement('option');
                    if (typeof opt === 'object' && opt.value) {
                        o.value = opt.value;
                        o.textContent = opt.label || opt.value;
                    } else {
                        o.value = opt;
                        o.textContent = opt;
                    }
                    input.appendChild(o);
                });
            } else {
                input = document.createElement('input');
                input.type = f.type;
                input.className = 'hud-input-ctrl';
            }

            input.id = f.id;
            if (f.readOnly) {
                input.value = `DOC-${Math.floor(Math.random() * 89999 + 10000)}`;
                input.readOnly = true;
                input.style.opacity = '0.5';
            }
            if (f.defaultValue) input.value = f.defaultValue;
            if (f.placeholder) input.placeholder = f.placeholder;

            input.addEventListener('input', debouncedUpdate);
            group.appendChild(input);
            container.appendChild(group);
        });
    },

    updatePreview: async function (tid) {
        const tpl = this.templates.find(t => t.id === tid);
        if (!tpl) return;

        const data = { template: tid, format: 'png', preview: true };
        tpl.fields.forEach(f => {
            const el = document.getElementById(f.id);
            if (el) data[f.id] = el.value;
        });

        const img = document.getElementById('doc-preview-img');
        const sheet = document.getElementById('paper-sheet-container');
        const loader = document.getElementById('preview-loader');

        if (loader) loader.classList.add('active');
        if (img) {
            img.style.display = 'block';
            img.style.opacity = '0.4';
        }
        if (sheet) sheet.style.display = 'none';

        try {
            const res = await fetch(App.API_BASE_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                img.onload = () => {
                    img.style.opacity = '1';
                    if (loader) loader.classList.remove('active');
                };
                img.src = url;
            } else {
                if (loader) loader.classList.remove('active');
            }
        } catch (e) {
            if (loader) loader.classList.remove('active');
            console.error("Preview fail", e);
        }
    },

    generate: function (format) {
        const title = document.getElementById('editor-title').textContent;
        const type = document.getElementById('editor-title').dataset.type;
        const tid = document.getElementById('editor-title').dataset.id;

        if (type === 'intelligence') {
            this.generateIntelligence(tid, format);
        } else {
            this.generateMDC(tid, format);
        }
    },

    generateIntelligence: async function (tid, format) {
        const tpl = this.templates.find(t => t.id === tid);
        if (!tpl) return;

        const data = { template: tid, format: format };
        tpl.fields.forEach(f => {
            const el = document.getElementById(f.id);
            if (el) data[f.id] = el.value;
        });

        try {
            const res = await fetch(App.API_BASE_URL + '?download=1', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                const blob = await res.blob();
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = `LSPD_${tid}.${format}`;
                a.click();
            }
        } catch (e) { console.error("Gen fail", e); }
    },

    generateMDC: async function (tid, format) {
        const content = document.getElementById('paper-sheet-content');
        if (!content) return;

        const data = {
            type: 'mdc',
            html: content.innerHTML,
            format: format,
            template: tid
        };

        try {
            const res = await fetch(App.API_BASE_URL + '?download=1', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                const blob = await res.blob();
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = `MDC_${tid}.${format}`;
                a.click();
            }
        } catch (e) { console.error("MDC Gen fail", e); }
    },

    renderMDCForm: function (tpl) {
        const container = document.getElementById('doc-form-fields');
        container.innerHTML = '';

        tpl.form.forEach(item => {
            if (item.type === 'section') {
                const h = document.createElement('h3');
                h.style.color = 'hsl(var(--primary))';
                h.style.fontSize = '0.8rem';
                h.style.marginTop = '1.5rem';
                h.style.marginBottom = '0.75rem';
                h.style.textTransform = 'uppercase';
                h.textContent = item.title;
                container.appendChild(h);
                return;
            }

            if (item.type === 'group') {
                const groupDiv = document.createElement('div');
                groupDiv.style.display = 'grid';
                groupDiv.style.gridTemplateColumns = 'repeat(auto-fit, minmax(150px, 1fr))';
                groupDiv.style.gap = '1rem';
                item.fields.forEach(f => this.renderMDCField(f, groupDiv, tpl.id));
                container.appendChild(groupDiv);
                return;
            }

            this.renderMDCField(item, container, tpl.id);
        });
    },

    renderMDCField: function (f, container, tplId) {
        if (f.type === 'hidden') return;
        const debouncedUpdate = this.debounce(() => this.updateMDCPreview(tplId), 300);

        if (['officer', 'general', 'location', 'charge', 'input_group'].includes(f.type)) {
            const section = document.createElement('div');
            section.className = 'hud-form-sub-section';
            section.style.borderLeft = '2px solid hsl(var(--primary) / 0.3)';
            section.style.paddingLeft = '1rem';
            section.style.marginBottom = '1rem';

            const labelText = f.label || f.type.toUpperCase();
            section.innerHTML = `<label class="hud-label" style="color:hsl(var(--primary)); margin-bottom:0.5rem">${labelText}</label>`;

            if (f.type === 'general') {
                const row = document.createElement('div');
                row.style.display = 'flex'; row.style.gap = '1rem';
                ['date', 'time'].forEach(field => {
                    const input = document.createElement('input'); input.className = 'hud-input-ctrl';
                    input.id = `${f.name}.${field}`; input.placeholder = field.toUpperCase();
                    if (field === 'date') input.value = new Date().toLocaleDateString('pl-PL');
                    if (field === 'time') {
                        const now = new Date();
                        input.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
                    }
                    input.addEventListener('input', debouncedUpdate);
                    const sub = document.createElement('div'); sub.style.flex = 1; sub.appendChild(input); row.appendChild(sub);
                });
                section.appendChild(row);
            } else if (f.type === 'location') {
                const row = document.createElement('div'); row.style.display = 'flex'; row.style.gap = '1rem';
                ['district', 'street'].forEach(field => {
                    const input = document.createElement('input'); input.className = 'hud-input-ctrl';
                    input.id = `${f.name}.${field}`; input.placeholder = field.toUpperCase();
                    input.addEventListener('input', debouncedUpdate);
                    const sub = document.createElement('div'); sub.style.flex = 1; sub.appendChild(input); row.appendChild(sub);
                });
                section.appendChild(row);
            } else if (f.type === 'officer') {
                const row = document.createElement('div'); row.style.display = 'flex'; row.style.gap = '0.5rem'; row.style.flexDirection = 'column';
                ['name', 'rank', 'badgeNumber'].forEach(field => {
                    const input = document.createElement('input'); input.className = 'hud-input-ctrl';
                    input.id = `${f.name}.0.${field}`; input.placeholder = field.toUpperCase();
                    input.addEventListener('input', debouncedUpdate);
                    row.appendChild(input);
                });
                section.appendChild(row);
            } else if (f.type === 'charge') {
                const input = document.createElement('input'); input.className = 'hud-input-ctrl';
                input.placeholder = 'Charge ID (e.g. 101)'; input.id = `${f.name}.0.chargeId`;
                input.addEventListener('input', debouncedUpdate); section.appendChild(input);
                const fine = document.createElement('input'); fine.className = 'hud-input-ctrl';
                fine.placeholder = 'Fine Amount'; fine.id = `${f.name}.0.fine`; fine.style.marginTop = '0.5rem';
                fine.addEventListener('input', debouncedUpdate); section.appendChild(fine);
            } else if (f.type === 'input_group') {
                f.fields.forEach(sf => {
                    const input = document.createElement('input'); input.className = 'hud-input-ctrl';
                    input.id = `${f.name}.0.${sf.name}`; input.placeholder = sf.label;
                    input.addEventListener('input', debouncedUpdate); section.appendChild(input);
                });
            }
            container.appendChild(section);
            return;
        }

        const group = document.createElement('div');
        group.className = 'hud-form-group';
        group.innerHTML = `<label class="hud-label">${f.label || f.name}</label>`;

        let input;
        if (f.type === 'textarea') {
            input = document.createElement('textarea'); input.className = 'hud-input-ctrl'; input.style.height = '100px';
        } else if (f.type === 'select' || f.type === 'datalist' || f.type === 'better-switch') {
            input = document.createElement('select'); input.className = 'hud-input-ctrl';
            const options = f.options || (f.dataOn ? [f.dataOn, f.dataOff] : []);
            options.forEach(opt => {
                const o = document.createElement('option'); o.value = opt; o.textContent = opt; input.appendChild(o);
            });
        } else {
            input = document.createElement('input'); input.type = 'text'; input.className = 'hud-input-ctrl';
        }

        input.id = f.name;
        if (f.placeholder) input.placeholder = f.placeholder;
        if (f.defaultValue !== undefined) input.value = f.defaultValue;

        input.addEventListener('input', debouncedUpdate);
        group.appendChild(input);
        container.appendChild(group);
    },

    parseBBCode: function (text) {
        if (!text) return "";
        let html = text.replace(/\[b\]/gi, "<strong>").replace(/\[\/b\]/gi, "</strong>")
            .replace(/\[i\]/gi, "<em>").replace(/\[\/i\]/gi, "</em>")
            .replace(/\[u\]/gi, "<u>").replace(/\[\/u\]/gi, "</u>")
            .replace(/\[del\]/gi, "<del>").replace(/\[\/del\]/gi, "</del>")
            .replace(/\[hr\]\[\/hr\]/gi, "<hr class='bb-hr'>").replace(/\[hr\]/gi, "<hr class='bb-hr'>")
            .replace(/\[list\]([\s\S]*?)\[\/list\]/gi, "<ul>$1</ul>")
            .replace(/\[list=none\]([\s\S]*?)\[\/list\]/gi, "<ul style='list-style:none; padding:0'>$1</ul>")
            .replace(/\[\*\]/gi, "<li>")
            .replace(/\[color=([\w#]+)\]([\s\S]*?)\[\/color\]/gi, '<span style="color:$1">$2</span>')
            .replace(/\[size=(\d+)\]([\s\S]*?)\[\/size\]/gi, '<span style="font-size:$1% !important">$2</span>')
            .replace(/\[img\]([\s\S]*?)\[\/img\]/gi, '<img src="$1" style="max-width:100%">')
            .replace(/\[bwlspdlogo=(\d+)\]\[\/bwlspdlogo\]/gi, '<img src="assets/l-lspd.png" width="$1" style="display:block;margin:0 auto">')
            .replace(/\[cb\]/gi, '<i class="far fa-square" style="margin-right:5px"></i>')
            .replace(/\[cbc\]/gi, '<i class="far fa-check-square" style="margin-right:5px"></i>')
            .replace(/\[color=transparent\]spacer\[\/color\]/gi, '<div style="height:20px"></div>')
            .replace(/\[color=transparent\]tt\[\/color\]/gi, '<span style="opacity:0">.</span>')
            .replace(/\n/g, "<br>");

        html = html.replace(/\[divbox2=([\w#]+)\]([\s\S]*?)\[\/divbox2\]/gi, (m, color, content) => `<div class="bb-divbox2" style="background:${color}">${content}</div>`);
        html = html.replace(/\[aligntable=([\w,.-]+)\]([\s\S]*?)\[\/aligntable\]/gi, (m, params, content) => {
            const p = params.split(','); const align = p[0] || 'left';
            return `<div class="bb-aligntable bb-align-${align}">${content}</div>`;
        });
        html = html.replace(/\[altspoiler2=([\s\S]*?)\]([\s\S]*?)\[\/altspoiler2\]/gi, (m, title, content) => `<div class="bb-spoiler"><div class="bb-spoiler-header">${title}</div><div class="bb-spoiler-content">${content}</div></div>`);

        return html;
    },

    updateMDCPreview: function (tid) {
        const tpl = this.mdcTemplatesData[tid];
        if (!tpl) return;

        if (typeof Handlebars === 'undefined') {
            console.warn("Handlebars not loaded yet");
            return;
        }

        if (!Handlebars.helpers.is_in) {
            Handlebars.registerHelper('is_in', function (arr, val) {
                if (!arr) return false;
                if (Array.isArray(arr)) return arr.includes(val);
                return arr === val;
            });
            Handlebars.registerHelper('lookup_penal', function (id) {
                return (window.PenalCode && window.PenalCode.data[id]) || { charge: 'Unknown' };
            });
            Handlebars.registerHelper('initials', function (name) {
                if (!name) return "";
                return name.split(' ').map(n => n.charAt(0)).join('').toUpperCase();
            });
        }

        const data = {
            penalCode: window.PenalCode ? window.PenalCode.data : {}
        };

        const inputs = document.querySelectorAll('#doc-form-fields input, #doc-form-fields textarea, #doc-form-fields select');
        inputs.forEach(input => {
            const val = input.type === 'checkbox' ? input.checked : input.value;
            if (input.id.includes('.')) {
                const parts = input.id.split('.');
                let curr = data;
                for (let i = 0; i < parts.length - 1; i++) {
                    const part = parts[i];
                    if (!curr[part]) {
                        curr[part] = !isNaN(parts[i + 1]) ? [] : {};
                    }
                    curr = curr[part];
                }
                curr[parts[parts.length - 1]] = val;
            } else {
                data[input.id] = val;
            }
        });

        const sheet = document.getElementById('paper-sheet-container');
        const img = document.getElementById('doc-preview-img');
        const content = document.getElementById('paper-sheet-content');

        if (sheet) sheet.style.display = 'block';
        if (img) img.style.display = 'none';

        try {
            const template = Handlebars.compile(tpl.output);
            const text = template(data);
            const htmlOutput = this.parseBBCode(text);
            if (content) content.innerHTML = htmlOutput;
        } catch (e) {
            console.error("Handlebars Error", e);
            if (content) content.innerHTML = `<div style="color:red">Error rendering template: ${e.message}</div>`;
        }
    }
};
