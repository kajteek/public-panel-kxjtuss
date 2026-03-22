import re
import os

js_file = r"c:\Users\kaketan\.gemini\antigravity\scratch\lspd_web_app\client\js\modules\caseboard.js"
with open(js_file, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. selectPinType
repl_selectPinType = """    selectPinType(val, text, iconClass, color) {
        document.getElementById('cb-pin-type-select').value = val;
        document.getElementById('pin-type-selected').innerHTML = `<i class="fas ${iconClass}" style="color:${color}; margin-right:8px;"></i> ${text}`;

        const stickies = document.getElementById('cb-modal-sticky-fields');
        if (val === 'stickynote') {
            if (stickies) stickies.style.display = 'block';
        } else {
            if (stickies) stickies.style.display = 'none';
        }
        
        const fieldMap = {
            'suspect': ['dob-phone', 'address', 'details'],
            'poi': ['dob-phone', 'address', 'reason', 'details'],
            'victim': ['dob-phone', 'address', 'details'],
            'witness': ['dob-phone', 'address', 'details'],
            'officer': ['officer-info', 'officer-div', 'details'],
            'statement': ['statement-info', 'datetime-loc', 'details'],
            'evidence': ['evidence-info', 'evidence-col', 'details'],
            'vehicle': ['vehicle-info1', 'vehicle-info2', 'owner', 'details'],
            'weapon': ['weapon-info', 'weapon-serial', 'details'],
            'location': ['address', 'generic-type', 'district', 'details'],
            'timeline': ['date-time', 'details'],
            'phone': ['dob-phone', 'owner', 'details'],
            'document': ['doc-info', 'details'],
            'organization': ['generic-type', 'org-info', 'details'],
            'note': ['details'],
            'stickynote': []
        };
        
        const activeFields = fieldMap[val] || [];
        document.querySelectorAll('.dfield').forEach(el => {
            const fieldKey = el.getAttribute('data-fields');
            if (activeFields.includes(fieldKey)) {
                el.style.display = '';
            } else {
                el.style.display = 'none';
            }
        });

        document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('active'));
    },"""
js = re.sub(r'    selectPinType\(val, text, iconClass, color\) \{.*?(?=    selectDropdown\()', repl_selectPinType + "\n\n", js, flags=re.DOTALL)

# 2. submitAddPin
repl_submitAddPin = """    submitAddPin() {
        try {
            const typeEl = document.getElementById('cb-pin-type-select');
            const type = typeEl ? typeEl.value : 'suspect';

            const safeVal = (id) => {
                const el = document.getElementById(id);
                return el ? el.value : '';
            };

            const data = {
                name: safeVal('pin-field-name') || 'Unknown',
                photo: safeVal('pin-field-photo'),
                size: safeVal('pin-field-size'),
                priority: safeVal('pin-field-priority'),
                todos: safeVal('pin-field-todos'),
                
                dob: safeVal('pin-field-dob'),
                phone: safeVal('pin-field-phone'),
                address: safeVal('pin-field-address'),
                reason: safeVal('pin-field-reason'),
                badge: safeVal('pin-field-badge'),
                callsign: safeVal('pin-field-callsign'),
                division: safeVal('pin-field-division'),
                statementBy: safeVal('pin-field-statement-by'),
                takenBy: safeVal('pin-field-taken-by'),
                datetime: safeVal('pin-field-datetime'),
                location: safeVal('pin-field-location'),
                tag: safeVal('pin-field-tag'),
                foundAt: safeVal('pin-field-found-at'),
                collectedBy: safeVal('pin-field-collected-by'),
                plate: safeVal('pin-field-plate'),
                state: safeVal('pin-field-state'),
                model: safeVal('pin-field-model'),
                color: safeVal('pin-field-color'),
                wtype: safeVal('pin-field-wtype'),
                caliber: safeVal('pin-field-caliber'),
                serial: safeVal('pin-field-serial'),
                members: safeVal('pin-field-members'),
                territory: safeVal('pin-field-territory'),
                doctype: safeVal('pin-field-doctype'),
                reference: safeVal('pin-field-reference'),
                owner: safeVal('pin-field-owner'),
                gtype: safeVal('pin-field-generic-type'),
                district: safeVal('pin-field-district'),
                date: safeVal('pin-field-date'),
                time: safeVal('pin-field-time'),
                details: safeVal('pin-field-details'),
                creationDate: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
            };
            this.addPin(type, data);
        } catch (e) {
            alert("CRITICAL ERROR IN submitAddPin: " + e.message);
            console.error(e);
        }
    },"""
js = re.sub(r'    submitAddPin\(\) \{.*?(?=    addPin\()', repl_submitAddPin + "\n\n", js, flags=re.DOTALL)

# 3. renderPin
repl_renderPin = """    renderPin(pin) {
        let el = document.getElementById(pin.id);
        const isNew = !el;

        if (isNew) {
            el = document.createElement('div');
            el.className = 'cb-pin';
            el.id = pin.id;
            el.style.zIndex = ++this.state.maxZIndex;
        }

        el.dataset.type = pin.type;
        el.style.left = pin.x + 'px';
        el.style.top = pin.y + 'px';

        const typeMap = {
            suspect: { t: 'Suspect', i: 'fa-user', c: '#a855f7' },
            poi: { t: 'Person of Interest', i: 'fa-bullseye', c: '#ec4899' },
            victim: { t: 'Victim', i: 'fa-heart-broken', c: '#f43f5e' },
            stickynote: { t: 'Sticky Note', i: 'fa-thumbtack', c: '#eab308' },
            witness: { t: 'Witness', i: 'fa-eye', c: '#22c55e' },
            officer: { t: 'Officer', i: 'fa-shield-alt', c: '#3b82f6' },
            evidence: { t: 'Evidence', i: 'fa-search', c: '#f59e0b' },
            weapon: { t: 'Weapon', i: 'fa-gun', c: '#ef4444' },
            vehicle: { t: 'Vehicle', i: 'fa-car', c: '#06b6d4' },
            location: { t: 'Location', i: 'fa-map-marker-alt', c: '#10b981' },
            organization: { t: 'Organization', i: 'fa-building', c: '#eab308' },
            note: { t: 'Note', i: 'fa-edit', c: '#64748b' },
            statement: { t: 'Statement', i: 'fa-file-alt', c: '#3b82f6' },
            timeline: { t: 'Timeline', i: 'fa-clock', c: '#8b5cf6' },
            phone: { t: 'Phone', i: 'fa-mobile-alt', c: '#ec4899' },
            document: { t: 'Document', i: 'fa-file-invoice', c: '#64748b' }
        };
        const m = typeMap[pin.type] || typeMap['suspect'];

        if (pin.type === 'node') {
            const glowClass = pin.data.glow ? 'box-shadow: 0 0 15px rgba(59,130,246,0.6); border: 1px solid rgba(59,130,246,0.8);' : 'border: 1px solid rgba(255,255,255,0.05);';
            const dotSide = pin.data.leftDot ? 'left:4px;' : 'right:4px;';
            const offsetX = pin.data.leftDot ? 12 : 128; 
            el.innerHTML = `
                <div style="width:140px; height:24px; background:#0a0e14; border-radius:12px; ${glowClass} position:relative; cursor:move; display:flex; align-items:center;">
                    <div class="cb-node-connect-point" style="width:16px; height:16px; background:#fff; border-radius:50%; position:absolute; ${dotSide} display:flex; align-items:center; justify-content:center; pointer-events:none;">
                        <div style="width:8px; height:8px; background:#ef4444; border-radius:50%;"></div>
                    </div>
                </div>
            `;
            pin.offsetX = offsetX;
            pin.offsetY = 12;

            if (!pin.data.centered) {
                pin.x -= 70;
                pin.y -= 12;
                pin.data.centered = true;
                el.style.left = pin.x + 'px';
                el.style.top = pin.y + 'px';
            }
        } else if (pin.type === 'stickynote') {
            let todosHtml = '';
            if (pin.data.todos) {
                const lines = pin.data.todos.split('\\n').filter(l => l.trim() !== '');
                todosHtml = lines.map(l => `
                    <div style="display:flex; align-items:flex-start; margin-top:5px; gap:8px;">
                        <input type="checkbox" style="width:16px; height:16px; cursor:pointer;" onclick="event.stopPropagation()">
                        <span style="font-size:0.95rem; color:#1a1a1a; text-shadow:none">${l}</span>
                    </div>`).join('');
            }

            el.innerHTML = `
                <div style="background:#eab308; color:#111; padding:15px; width:250px; border-radius:4px; box-shadow:3px 3px 15px rgba(0,0,0,0.5); border-top:12px solid #ca8a04;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div style="font-weight:800; font-size:1.1rem; margin-bottom:2px; color:#000;">${pin.data.name}</div>
                        <button class="cb-pin-action delete" style="background:none; border:none; color:rgba(0,0,0,0.3); font-size:1.1rem; cursor:pointer;" title="Delete"><i class="fas fa-times"></i></button>
                    </div>
                    <div style="font-size:0.7rem; text-transform:uppercase; color:rgba(0,0,0,0.5); margin-bottom:12px; font-weight:800; letter-spacing:1px;">
                        <i class="fas fa-thumbtack" style="color:#ef4444; margin-right:4px; font-size:0.8rem"></i> STICKY NOTE
                    </div>
                    ${todosHtml}
                </div>
            `;
            const delBtn = el.querySelector('.cb-pin-action.delete');
            if (delBtn) delBtn.onclick = (e) => { e.stopPropagation(); this.deletePin(pin.id); };
        } else {
            const d = pin.data;
            let metaHtml = '';
            const fields = [
                { l: 'DOB:', v: d.dob },
                { l: 'Phone:', v: d.phone },
                { l: 'Address:', v: d.address },
                { l: 'Reason:', v: d.reason },
                { l: 'Badge:', v: d.badge },
                { l: 'Callsign:', v: d.callsign },
                { l: 'Division:', v: d.division },
                { l: 'By:', v: d.statementBy },
                { l: 'Taken By:', v: d.takenBy },
                { l: 'Time:', v: d.datetime || d.time },
                { l: 'Loc:', v: d.location },
                { l: 'Tag:', v: d.tag },
                { l: 'Found:', v: d.foundAt },
                { l: 'Collector:', v: d.collectedBy },
                { l: 'Plate:', v: d.plate },
                { l: 'State:', v: d.state },
                { l: 'Model:', v: d.model },
                { l: 'Color:', v: d.color },
                { l: 'Type:', v: (d.wtype || d.gtype) },
                { l: 'Caliber:', v: d.caliber },
                { l: 'Serial:', v: d.serial },
                { l: 'Members:', v: d.members },
                { l: 'Territory:', v: d.territory },
                { l: 'Doc Type:', v: d.doctype },
                { l: 'Ref:', v: d.reference },
                { l: 'Owner:', v: d.owner },
                { l: 'District:', v: d.district },
                { l: 'Date:', v: d.date }
            ];

            fields.forEach(f => {
                if (f.v && f.v.trim() !== '') {
                    metaHtml += `<div class="meta-row"><span class="label">${f.l}</span><span class="val">${f.v}</span></div>`;
                }
            });

            let detailsHtml = d.details ? `<div class="cb-pin-details-text">${d.details}</div>` : '';
            let priorityIcon = d.priority === 'urgent' ? '<i class="fas fa-exclamation-triangle" style="color:#ef4444; margin-left:auto"></i>' : (d.priority === 'high' ? '<i class="fas fa-exclamation-circle" style="color:#f59e0b; margin-left:auto"></i>' : '');
            
            const linkCount = this.state.links.filter(l => l.from === pin.id || l.to === pin.id).length;
            const creationDate = pin.data.creationDate || new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

            el.innerHTML = `
                <div class="cb-pin-sidebar"></div>
                <div class="cb-pin-content">
                    <div class="cb-pin-action-bar">
                        <button class="cb-pin-action edit" title="Edit"><i class="fas fa-pencil-alt"></i></button>
                        <button class="cb-pin-action duplicate" title="Duplicate"><i class="fas fa-copy"></i></button>
                        <button class="cb-pin-action delete" title="Delete"><i class="fas fa-trash"></i></button>
                    </div>
                    <div class="cb-pin-header">
                        <div class="cb-pin-title">${d.name}</div>
                        <div class="cb-pin-type-name" style="color: ${m.c}; margin-bottom: 0px; display: flex; align-items: center; gap: 6px;">
                            <i class="fas ${m.i}"></i> ${m.t}
                        </div>
                    </div>
                    <div class="cb-pin-body">
                        ${d.photo ? `<img src="${d.photo}" class="cb-pin-image" onerror="this.style.display='none'">` : ''}
                        ${detailsHtml}
                        ${metaHtml ? `<div class="cb-pin-meta">${metaHtml}</div>` : ''}
                        <div class="cb-pin-footer">
                            <div style="display:flex; align-items:center; gap:4px;"><i class="fas fa-calendar-alt"></i> <span>${creationDate}</span></div>
                            <div style="display:flex; align-items:center; gap:4px; margin-left:8px;"><i class="fas fa-link"></i> <span>${linkCount}</span></div>
                        </div>
                        <div class="cb-pin-tag">
                            <i class="fas fa-pen" style="color:#f59e0b"></i> <span>#CD-${pin.id.slice(-4)}</span>
                            ${priorityIcon}
                        </div>
                    </div>
                </div>
            `;
            const editBtn = el.querySelector('.cb-pin-action.edit');
            const dupBtn = el.querySelector('.cb-pin-action.duplicate');
            const delBtn = el.querySelector('.cb-pin-action.delete');
            if (editBtn) editBtn.onclick = (e) => { e.stopPropagation(); this.openEditPinModal(pin.id); };
            if (dupBtn) dupBtn.onclick = (e) => { e.stopPropagation(); this.duplicatePin(pin.id); };
            if (delBtn) delBtn.onclick = (e) => { e.stopPropagation(); this.deletePin(pin.id); };
        }

        if (isNew) {
            el.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.state.contextPinId = pin.id;
                
                // Show 'Connect to here' ONLY if connectMode is active
                const toBtn = document.getElementById('cb-ctx-pin-link-to');
                if (toBtn) {
                    if (this.state.connectMode && this.state.selectedPinForLink && this.state.selectedPinForLink !== pin.id) {
                        toBtn.style.display = 'flex';
                    } else {
                        toBtn.style.display = 'none';
                    }
                }
                
                this.showContextMenu('cb-ctx-pin', e.clientX, e.clientY);
            });

            this.canvas.appendChild(el);
            this.initPinDragging(el);
        }
    },"""
js = re.sub(r'    renderPin\(pin\) \{.*?(?=    duplicatePin\()', repl_renderPin + "\n\n", js, flags=re.DOTALL)

# 4. openEditPinModal
repl_openEditPinModal = """    openEditPinModal(pinId) {
        const pin = this.state.pins.find(p => p.id === pinId);
        if (!pin) return;

        const modal = document.getElementById('cb-modal-add-pin');
        if (modal) {
            modal.classList.add('active');
            document.querySelectorAll('#cb-modal-add-pin .hud-input').forEach(i => i.value = '');
        }

        this.state.editingPinId = pinId;

        const safeSet = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.value = val || '';
        };

        const d = pin.data;
        safeSet('pin-field-name', d.name);
        safeSet('pin-field-photo', d.photo);
        safeSet('pin-field-todos', d.todos);
        
        safeSet('pin-field-dob', d.dob);
        safeSet('pin-field-phone', d.phone);
        safeSet('pin-field-address', d.address);
        safeSet('pin-field-reason', d.reason);
        safeSet('pin-field-badge', d.badge);
        safeSet('pin-field-callsign', d.callsign);
        safeSet('pin-field-division', d.division);
        safeSet('pin-field-statement-by', d.statementBy);
        safeSet('pin-field-taken-by', d.takenBy);
        safeSet('pin-field-datetime', d.datetime);
        safeSet('pin-field-location', d.location);
        safeSet('pin-field-tag', d.tag);
        safeSet('pin-field-found-at', d.foundAt);
        safeSet('pin-field-collected-by', d.collectedBy);
        safeSet('pin-field-plate', d.plate);
        safeSet('pin-field-state', d.state);
        safeSet('pin-field-model', d.model);
        safeSet('pin-field-color', d.color);
        safeSet('pin-field-wtype', d.wtype);
        safeSet('pin-field-caliber', d.caliber);
        safeSet('pin-field-serial', d.serial);
        safeSet('pin-field-members', d.members);
        safeSet('pin-field-territory', d.territory);
        safeSet('pin-field-doctype', d.doctype);
        safeSet('pin-field-reference', d.reference);
        safeSet('pin-field-owner', d.owner);
        safeSet('pin-field-generic-type', d.gtype);
        safeSet('pin-field-district', d.district);
        safeSet('pin-field-date', d.date);
        safeSet('pin-field-time', d.time);
        safeSet('pin-field-details', d.details);

        this.selectDropdown('size', d.size || 'medium', (d.size || 'medium').toUpperCase());
        this.selectDropdown('priority', d.priority || 'normal', (d.priority || 'normal').toUpperCase());

        const typeMap = {
            suspect: { t: 'Suspect', i: 'fa-user', c: '#a855f7' },
            poi: { t: 'Person of Interest', i: 'fa-bullseye', c: '#ec4899' },
            victim: { t: 'Victim', i: 'fa-heart-broken', c: '#f43f5e' },
            stickynote: { t: 'Sticky Note', i: 'fa-thumbtack', c: '#eab308' },
            witness: { t: 'Witness', i: 'fa-eye', c: '#22c55e' },
            officer: { t: 'Officer', i: 'fa-shield-alt', c: '#3b82f6' },
            evidence: { t: 'Evidence', i: 'fa-search', c: '#f59e0b' },
            weapon: { t: 'Weapon', i: 'fa-gun', c: '#ef4444' },
            vehicle: { t: 'Vehicle', i: 'fa-car', c: '#06b6d4' },
            location: { t: 'Location', i: 'fa-map-marker-alt', c: '#10b981' },
            organization: { t: 'Organization', i: 'fa-building', c: '#eab308' },
            note: { t: 'Note', i: 'fa-edit', c: '#64748b' },
            statement: { t: 'Statement', i: 'fa-file-alt', c: '#3b82f6' },
            timeline: { t: 'Timeline', i: 'fa-clock', c: '#8b5cf6' },
            phone: { t: 'Phone', i: 'fa-mobile-alt', c: '#ec4899' },
            document: { t: 'Document', i: 'fa-file-invoice', c: '#64748b' }
        };
        const meta = typeMap[pin.type] || typeMap['suspect'];
        this.selectPinType(pin.type, meta.t, meta.i, meta.c);

        const titleEl = document.querySelector('#cb-modal-add-pin .cb-modal-title');
        if (titleEl) titleEl.innerText = "EDIT PIN";
    },"""
js = re.sub(r'    openEditPinModal\(pinId\) \{.*?(?=    initPinDragging\()', repl_openEditPinModal + "\n\n", js, flags=re.DOTALL)

with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js)

print("JS updated successfully.")
