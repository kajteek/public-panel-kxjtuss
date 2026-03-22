import re

js_file = r"c:\Users\kaketan\.gemini\antigravity\scratch\lspd_web_app\client\js\modules\caseboard.js"

with open(js_file, 'r', encoding='utf-8') as f:
    js_content = f.read()

# The CORRECT and FULL `renderPin` replacing the broken one in the file.
full_render_pin = """    renderPin(pin) {
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
            suspect: { t: 'Suspect', i: 'fa-user', c: '#ef4444' }, /* Red icon for Suspect from user mockup */
            poi: { t: 'Person of Interest', i: 'fa-bullseye', c: '#ec4899' },
            victim: { t: 'Victim', i: 'fa-heart-broken', c: '#f43f5e' },
            stickynote: { t: 'Sticky Note', i: 'fa-thumbtack', c: '#eab308' },
            witness: { t: 'Witness', i: 'fa-user-secret', c: '#eab308' }, /* Yellow witness */
            officer: { t: 'Officer', i: 'fa-shield-alt', c: '#3b82f6' },
            evidence: { t: 'Evidence', i: 'fa-search', c: '#f59e0b' },
            weapon: { t: 'Weapon', i: 'fa-crosshairs', c: '#ef4444' }, /* Target */
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

            // Ensure we use the exact design from user's zdjecie2 target reference.
            el.innerHTML = `
                <div class="cb-pin-content">
                    <div class="cb-pin-action-bar">
                        <button class="cb-pin-action edit" title="Edit"><i class="fas fa-pencil-alt"></i></button>
                        <button class="cb-pin-action duplicate" title="Duplicate"><i class="fas fa-copy"></i></button>
                        <button class="cb-pin-action delete" title="Delete"><i class="fas fa-trash"></i></button>
                    </div>
                    <div class="cb-pin-header">
                        <div class="cb-pin-sidebar" style="background: ${m.c};"></div>
                        <div class="cb-pin-title">${d.name}</div>
                        <div class="cb-pin-type-name" style="color: ${m.c};">
                            <i class="fas ${m.i}"></i> ${m.t}
                        </div>
                    </div>
                    <div class="cb-pin-body">
                        ${d.photo ? `<img src="${d.photo}" class="cb-pin-image" onerror="this.style.display='none'">` : ''}
                        ${detailsHtml}
                        ${metaHtml ? `<div class="cb-pin-meta">${metaHtml}</div>` : ''}
                        <div class="cb-pin-footer">
                            <div style="display:flex; align-items:center; gap:4px;"><i class="fas fa-calendar-alt" style="color:#3b82f6;"></i> <span>${creationDate}</span></div>
                            <div style="display:flex; align-items:center; gap:4px; margin-left:8px;"><i class="fas fa-link" style="color:rgba(255,255,255,0.5);"></i> <span>${linkCount}</span></div>
                        </div>
                        <div class="cb-pin-tag">
                            <i class="fas fa-pen" style="color:#f59e0b"></i> <span>${d.tag || ('#CD-' + pin.id.slice(-4))}</span>
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

js_content = re.sub(r'    renderPin\(pin\) \{.*?(?=    duplicatePin\()', full_render_pin + "\n\n", js_content, flags=re.DOTALL)

with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("caseboard.js fully restored with the correct HTML!")

index_file = r"c:\Users\kaketan\.gemini\antigravity\scratch\lspd_web_app\client\index.html"
with open(index_file, 'r', encoding='utf-8') as f:
    idx = f.read()

idx = idx.replace("css/caseboard.css?v=1.8", "css/caseboard.css?v=1.9")
idx = idx.replace("js/modules/caseboard.js?v=1.8", "js/modules/caseboard.js?v=1.9")

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(idx)

print("index.html cache busting updated to v1.9")
