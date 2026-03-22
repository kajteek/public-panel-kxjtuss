/**
 * LSPD Case Board System
 * Handles interactable pinning, zooming, and panning for investigation boards.
 */

window.CaseBoard = {
    state: {
        zoom: 0.5,
        pos: {
            x: (window.innerWidth ? (window.innerWidth - 280) / 2 : 960) - 1250,
            y: (window.innerHeight ? window.innerHeight / 2 : 540) - 1250
        },
        isPanning: false,
        lastMousePos: { x: 0, y: 0 },
        pins: [],
        links: [],
        connectMode: false,
        freeLineMode: false,
        isDrawingFreeLine: false,
        currentFreeLine: null,
        selectedPinForLink: null,
        maxZIndex: 100,
        activeCase: "New Investigation",
        caseID: "#2024-6615",
        contextPinId: null,
        contextLinkId: null,
        lastClickTime: 0,
        vehicleData: []
    },

    init() {
        try {
            console.log("[CaseBoard]: ATTEMPTING INIT V3...");
            this.cacheDOM();
            this.bindLocalEvents();

            // Ensure data is loaded
            if (!this.state.vehicleData || this.state.vehicleData.length === 0) {
                this.fetchVehicleData();
            }

            if (this.state.isInitialized) {
                this.renderStats();
                this.updateTransform();

                // Clear SVGs safely
                if (this.svg) this.svg.innerHTML = '';

                // Re-render cached pins on new DOM
                document.querySelectorAll('.cb-pin').forEach(el => el.remove());
                this.state.pins.forEach(pin => {
                    this.renderPin(pin);
                });
                this.renderLinks();
                this.initVehicleAutocomplete();
                return; // Prevent rebinding window listeners
            }

            this.bindGlobalEvents();

            this.renderStats();
            this.resetView(); // Ensure zoom strictly sets the zoom text layout accurately

            // Pin context menu actions - Defensive binding for Brave/Adblockers
            const bindClick = (id, handler) => {
                const el = document.getElementById(id);
                if (el) el.onclick = handler;
                else console.warn(`[CaseBoard]: Missing element #${id} for binding.`);
            };

            bindClick('cb-ctx-pin-delete', () => this.deletePin(this.state.contextPinId));
            bindClick('cb-ctx-pin-duplicate', () => this.duplicatePin(this.state.contextPinId));
            bindClick('cb-ctx-pin-edit', () => this.openEditPinModal(this.state.contextPinId));
            bindClick('cb-ctx-pin-reset', () => {
                const el = document.getElementById(this.state.contextPinId);
                if (el) el.style.transform = 'rotate(0deg)';
            });
            bindClick('cb-ctx-pin-link-from', () => {
                const el = document.getElementById(this.state.contextPinId);
                this.toggleConnectMode(true);
                this.onPinClick(el);
                this.closeContextMenus();
            });

            const linkToEl = document.getElementById('cb-ctx-pin-link-to');
            if (linkToEl) {
                linkToEl.onclick = () => {
                    const el = document.getElementById(this.state.contextPinId);
                    if (this.state.connectMode && this.state.selectedPinForLink) {
                        this.onPinClick(el);
                    }
                    this.closeContextMenus();
                };
            }

            this.state.isInitialized = true;
            this.fetchVehicleData();
            this.initVehicleAutocomplete();
        } catch (error) {
            console.error("[CaseBoard]: CRITICAL INIT FAILURE", error);
        }
    },

    async fetchVehicleData() {
        try {
            const res = await fetch(`data/devg-data/devg_vehicles.json?v=${Date.now()}`);
            console.log(`[CaseBoard]: Fetch response status: ${res.status}`);
            if (res.ok) {
                const data = await res.json();
                this.state.vehicleData = Object.values(data);
                console.log(`[CaseBoard]: Data parsed. Count: ${this.state.vehicleData.length}`);
            } else {
                console.error(`[CaseBoard]: Fetch failed with status ${res.status}`);
            }
        } catch (e) {
            console.error("[CaseBoard]: Failed to load vehicle data", e);
        }
    },

    initVehicleAutocomplete() {
        const input = document.getElementById('pin-field-model');
        const suggestionsCont = document.getElementById('cb-vehicle-suggestions');

        console.log("[CaseBoard]: Autocomplete init attempt", {
            input: !!input,
            suggestionsCont: !!suggestionsCont,
            dataType: typeof this.state.vehicleData,
            dataLength: this.state.vehicleData ? this.state.vehicleData.length : 0
        });

        if (!input || !suggestionsCont) return;

        // Clear previous listeners by replacing the element or using a flag
        // For simplicity and since elements are replaced on load, we just add new ones.
        // But let's be safe and use a flag if it's already there (though with App.loadViewport it shouldn't be).

        let selectedIndex = -1;
        let filteredVehicles = [];

        const renderSuggestions = (list, query) => {
            if (list.length === 0) {
                suggestionsCont.classList.remove('active');
                return;
            }

            const regex = new RegExp(`(${query})`, 'gi');
            suggestionsCont.innerHTML = list.slice(0, 15).map((v, idx) => `
                <div class="cb-suggestion-item ${idx === selectedIndex ? 'selected' : ''}" data-index="${idx}">
                    <div class="cb-suggestion-name">${v.name.replace(regex, '<mark class="cb-highlight">$1</mark>')}</div>
                    <div class="cb-suggestion-model">${v.model.replace(regex, '<mark class="cb-highlight">$1</mark>')}</div>
                </div>
            `).join('');
            suggestionsCont.classList.add('active');

            // Add click events to items
            suggestionsCont.querySelectorAll('.cb-suggestion-item').forEach(item => {
                item.onclick = () => {
                    const idx = parseInt(item.dataset.index);
                    selectSuggestion(list[idx]);
                };
            });
        };

        const selectSuggestion = (v) => {
            input.value = v.name; // User wanted "name" as suggestion, but many use model as search. We'll put name in input.
            // Actually, usually users want "Brand Model" or just "Model". The JSON has both.
            // "Albany Alpha" (name) vs "Alpha" (model).
            suggestionsCont.classList.remove('active');
            input.focus();
        };

        // Remove existing listeners if they were previously attached to avoid multiple bindings
        if (this._autocompleteHandlers && input) {
            input.removeEventListener('input', this._autocompleteHandlers.onInput);
            input.removeEventListener('keydown', this._autocompleteHandlers.onKeydown);
        }

        this._autocompleteHandlers = {
            onInput: () => {
                console.log("[CaseBoard]: input heard", input.value);
                const query = input.value.trim().toLowerCase();
                if (query.length < 2) {
                    suggestionsCont.classList.remove('active');
                    return;
                }

                if (!this.state.vehicleData || this.state.vehicleData.length === 0) {
                    console.warn("[CaseBoard]: No vehicle data available for autocomplete. Trying to reload...");
                    this.fetchVehicleData();
                    return;
                }

                filteredVehicles = this.state.vehicleData.filter(v =>
                    v.name.toLowerCase().includes(query) ||
                    v.model.toLowerCase().includes(query)
                ).sort((a, b) => a.name.length - b.name.length);

                selectedIndex = -1;
                renderSuggestions(filteredVehicles, query);
            },
            onKeydown: (e) => {
                if (!suggestionsCont.classList.contains('active')) return;

                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    selectedIndex = Math.min(selectedIndex + 1, Math.min(filteredVehicles.length, 15) - 1);
                    renderSuggestions(filteredVehicles, input.value.trim());
                    scrollToSelected();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    selectedIndex = Math.max(selectedIndex - 1, 0);
                    renderSuggestions(filteredVehicles, input.value.trim());
                    scrollToSelected();
                } else if (e.key === 'Enter') {
                    if (selectedIndex >= 0) {
                        e.preventDefault();
                        selectSuggestion(filteredVehicles[selectedIndex]);
                    }
                } else if (e.key === 'Escape') {
                    suggestionsCont.classList.remove('active');
                }
            }
        };

        input.addEventListener('input', this._autocompleteHandlers.onInput);
        input.addEventListener('keydown', this._autocompleteHandlers.onKeydown);
        console.log("[CaseBoard]: Autocomplete listeners attached.");

        const scrollToSelected = () => {
            const selected = suggestionsCont.querySelector('.cb-suggestion-item.selected');
            if (selected) {
                selected.scrollIntoView({ block: 'nearest' });
            }
        };

        // Close when clicking outside
        window.addEventListener('click', (e) => {
            if (!e.target.closest('.cb-autocomplete-container')) {
                suggestionsCont.classList.remove('active');
            }
        });
    },

    showContextMenu(menuId, x, y) {
        this.closeContextMenus();
        const menu = document.getElementById(menuId);
        if (menu) {
            menu.style.display = 'block';
            menu.style.left = x + 'px';
            menu.style.top = y + 'px';
        }
    },

    closeContextMenus() {
        document.querySelectorAll('.cb-context-menu').forEach(m => m.style.display = 'none');
    },

    cacheDOM() {
        this.view = document.getElementById('view-caseboard');
        this.workspace = document.querySelector('.cb-workspace');
        this.canvas = document.querySelector('.cb-canvas');
        this.svg = document.getElementById('cb-connections-svg');
        this.zoomDisplay = document.getElementById('cb-zoom-level');
    },

    bindLocalEvents() {
        if (!this.workspace) return;

        // Navigation & Right Click
        this.workspace.addEventListener('mousedown', (e) => {
            if (e.button === 0) {
                if (this.state.freeLineMode) {
                    this.state.isDrawingFreeLine = true;
                    // Start Polyline
                    const rect = this.workspace.getBoundingClientRect();
                    const x = (e.clientX - rect.left - this.state.pos.x) / this.state.zoom;
                    const y = (e.clientY - rect.top - this.state.pos.y) / this.state.zoom;

                    this.state.currentFreeLine = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
                    this.state.currentFreeLine.setAttribute("fill", "none");
                    this.state.currentFreeLine.setAttribute("stroke", "#ec4899");
                    this.state.currentFreeLine.setAttribute("stroke-width", "4");
                    this.state.currentFreeLine.setAttribute("stroke-opacity", "0.8");
                    this.state.currentFreeLine.setAttribute("points", `${x},${y}`);
                    this.svg.appendChild(this.state.currentFreeLine);
                    return;
                }
                // Left click for pan
                this.state.isPanning = true;
                this.state.lastMousePos = { x: e.clientX, y: e.clientY };
            }
        });

        this.workspace.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -0.1 : 0.1;

            const rect = this.workspace.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            const oldZoom = this.state.zoom;
            const newZoom = Math.min(Math.max(0.2, oldZoom + delta), 3);

            if (newZoom !== oldZoom) {
                const zoomRatio = newZoom / oldZoom;
                this.state.pos.x = mouseX - (mouseX - this.state.pos.x) * zoomRatio;
                this.state.pos.y = mouseY - (mouseY - this.state.pos.y) * zoomRatio;
                this.setZoom(newZoom);
            }
        }, { passive: false });

        this.workspace.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.showContextMenu('cb-ctx-canvas', e.clientX, e.clientY);
        });
    },

    bindGlobalEvents() {
        window.addEventListener('mousemove', (e) => {
            if (this.state.isDrawingFreeLine && this.state.currentFreeLine) {
                const rect = this.workspace.getBoundingClientRect();
                const x = (e.clientX - rect.left - this.state.pos.x) / this.state.zoom;
                const y = (e.clientY - rect.top - this.state.pos.y) / this.state.zoom;
                const pts = this.state.currentFreeLine.getAttribute("points");
                this.state.currentFreeLine.setAttribute("points", pts + ` ${x},${y}`);
                return;
            }
            if (this.state.isPanning) {
                const dx = e.clientX - this.state.lastMousePos.x;
                const dy = e.clientY - this.state.lastMousePos.y;
                this.state.pos.x += dx;
                this.state.pos.y += dy;
                this.state.lastMousePos = { x: e.clientX, y: e.clientY };
                this.updateTransform();
            }
        });

        window.addEventListener('mouseup', () => {
            this.state.isPanning = false;
            this.state.isDrawingFreeLine = false;
            this.state.currentFreeLine = null;
        });

        window.addEventListener('resize', () => {
            if (document.getElementById('view-caseboard')) this.updateTransform();
        });

        window.addEventListener('click', (e) => {
            if (!e.target.closest('.cb-context-menu')) {
                this.closeContextMenus();
            }
            if (!e.target.closest('.hud-dropdown')) {
                document.querySelectorAll('.cb-modal .dropdown-menu').forEach(m => m.classList.remove('active'));
            }
        });
    },

    toggleFreeLineMode() {
        this.closeContextMenus();

        // Drop two nodes connected by a line instead of drawing SVG directly
        const cx = -this.state.pos.x / this.state.zoom + window.innerWidth / 3;
        const cy = -this.state.pos.y / this.state.zoom + window.innerHeight / 3;

        const id1 = 'pin-' + Date.now() + 'A';
        const id2 = 'pin-' + Date.now() + 'B';

        const node1 = { id: id1, type: 'node', x: cx, y: cy, data: { name: 'Node A', leftDot: true, glow: true } };
        const node2 = { id: id2, type: 'node', x: cx + 250, y: cy + 100, data: { name: 'Node B', leftDot: true, glow: false } };

        this.state.pins.push(node1, node2);
        this.renderPin(node1);
        this.renderPin(node2);

        this.state.links.push({
            id: 'link-' + Date.now(),
            from: id1,
            to: id2,
            color: '#ef4444',
            style: 'solid',
            label: ''
        });

        this.renderLinks();
        this.renderStats();
    },

    toggleConnectMode() {
        // Placeholder for future connection mode logic
    },

    setZoom(value) {
        this.state.zoom = Math.min(Math.max(0.2, value), 3);
        if (this.zoomDisplay) {
            this.zoomDisplay.textContent = Math.round(this.state.zoom * 100) + "%";
        }
        this.updateTransform();
    },

    updateTransform() {
        if (this.canvas) {
            this.canvas.style.transform = `translate(${this.state.pos.x}px, ${this.state.pos.y}px) scale(${this.state.zoom})`;
            this.renderLinks(); // Re-render links on transform change
        }
    },

    // Modal Logic
    toggleMenu(e, menuId) {
        e.stopPropagation();
        document.querySelectorAll('.dropdown-menu').forEach(m => {
            if (m.id !== menuId) m.classList.remove('active');
        });
        const menu = document.getElementById(menuId);
        if (menu) menu.classList.toggle('active');
    },

    selectPinType(val, text, iconClass, color) {
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
    },

    selectDropdown(type, val, text) {
        document.getElementById(`pin-field-${type}`).value = val;
        document.getElementById(`pin-${type}-selected`).innerText = text;
        document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('active'));
    },

    openAddPinModal() {
        const modal = document.getElementById('cb-modal-add-pin');
        if (modal) {
            modal.classList.add('active');
            // Reset form
            document.querySelectorAll('#cb-modal-add-pin .hud-input').forEach(i => i.value = '');
            this.selectPinType('suspect', 'Suspect', 'fa-user', '#a855f7');
            this.selectDropdown('size', 'medium', 'Medium');
            this.selectDropdown('priority', 'normal', 'Normal');

            this.state.editingPinId = null;

            const titleEl = document.querySelector('#cb-modal-add-pin .cb-modal-title');
            if (titleEl) titleEl.innerText = "ADD NEW PIN";
        }
    },

    openStickyNoteModal() {
        this.openAddPinModal();
        this.selectPinType('stickynote', 'Sticky Note', 'fa-thumbtack', '#eab308');
    },

    toggleLabels() {
        this.closeContextMenus();
        const labels = document.querySelectorAll('.cb-line-label');
        labels.forEach(l => {
            l.style.display = (l.style.display === 'none' ? 'block' : 'none');
        });
    },

    newCase() {
        this.closeContextMenus();
        if (confirm("Are you sure you want to start a new case? All unsaved pins and links will be lost.")) {
            this.state.pins = [];
            this.state.links = [];

            document.querySelectorAll('.cb-pin').forEach(el => el.remove());
            document.querySelectorAll('.cb-line-label').forEach(el => el.remove());

            if (this.svg) this.svg.innerHTML = '';

            const titleEl = document.getElementById('cb-investigation-name');
            const idEl = document.getElementById('cb-case-id');
            if (titleEl) titleEl.innerText = "New Investigation";
            if (idEl) idEl.innerText = "#" + new Date().getFullYear() + "-" + Math.floor(Math.random() * 9000 + 1000);

            this.renderStats();
            this.renderLinks();
        }
    },

    closeAddPinModal() {
        const modal = document.getElementById('cb-modal-add-pin');
        if (modal) modal.classList.remove('active');
    },

    onPinTypeChange(type) {
        // Handled via static fields in index.html for now to match premium design.
        // We can add show/hide logic here if specific types need different fields.
    },

    submitAddPin() {
        try {
            const typeEl = document.getElementById('cb-pin-type-select');
            const typeValue = typeEl ? typeEl.value : 'suspect';

            const nameInput = document.getElementById('pin-field-name');
            const nameValue = nameInput ? nameInput.value.trim() : '';

            if (!nameValue) {
                if (nameInput) {
                    nameInput.style.borderColor = '#ef4444';
                    nameInput.style.boxShadow = '0 0 10px rgba(239, 68, 68, 0.3)';
                    nameInput.focus();
                    
                    // Add a placeholder hint
                    const originalPlaceholder = nameInput.placeholder;
                    nameInput.placeholder = "TITLE IS REQUIRED!";
                    setTimeout(() => {
                        nameInput.style.borderColor = '';
                        nameInput.style.boxShadow = '';
                        nameInput.placeholder = originalPlaceholder;
                    }, 2000);
                }
                return;
            }

            const safeVal = (id) => {
                const el = document.getElementById(id);
                return el ? el.value : '';
            };

            const data = {
                name: nameValue,
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
            this.addPin(typeValue, data);
        } catch (e) {
            alert("CRITICAL ERROR IN submitAddPin: " + e.message);
            console.error(e);
        }
    },

    addPin(type = 'suspect', data = {}) {
        try {
            const defaultData = {
                name: type.charAt(0).toUpperCase() + type.slice(1) + ' Name',
                type: type,
                details: 'Details test',
                dob: '23/12/2000',
                phone: '23-342453',
                address: 'Goma Street, Vespucci',
                date: new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit' }),
                tag: 'sadsa asdxsa #dasd'
            };

            const pinData = { ...defaultData, ...data };

            if (this.state.editingPinId) {
                const pin = this.state.pins.find(p => p.id === this.state.editingPinId);
                if (pin) {
                    pin.type = type;
                    pin.data = { ...pin.data, ...data };
                    this.renderPin(pin);
                }
                this.state.editingPinId = null;
            } else {
                const id = 'pin-' + Date.now();
                const pin = {
                    id: id,
                    type: type,
                    x: -this.state.pos.x / this.state.zoom + 100,
                    y: -this.state.pos.y / this.state.zoom + 100,
                    data: pinData
                };
                this.state.pins.push(pin);
                this.renderPin(pin);
            }

            this.renderStats();
            this.closeAddPinModal();
        } catch (e) {
            alert("CRITICAL ERROR IN addPin: " + e.message);
            console.error(e);
        }
    },

    renderPin(pin) {
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
    },

    duplicatePin(pinId) {
        const pin = this.state.pins.find(p => p.id === pinId);
        if (!pin) return;

        const newData = { ...pin.data, name: pin.data.name + ' (copy)' };
        const newPin = {
            ...pin,
            id: 'pin-' + Date.now(),
            x: pin.x + 30,
            y: pin.y + 30,
            data: newData
        };

        this.state.pins.push(newPin);
        this.renderPin(newPin);
        this.renderStats();
    },

    deletePin(pinId) {
        this.state.pins = this.state.pins.filter(p => p.id !== pinId);
        this.state.links = this.state.links.filter(l => l.from !== pinId && l.to !== pinId);
        const el = document.getElementById(pinId);
        if (el) el.remove();
        this.renderLinks();
        this.renderStats();
    },

    openEditPinModal(pinId) {
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
    },

    initPinDragging(el) {
        let isDragging = false;
        let hasMoved = false;
        let startPos = { x: 0, y: 0 };

        const onMouseMove = (e) => {
            if (!isDragging) return;
            hasMoved = true;

            const dx = (e.clientX - startPos.x) / this.state.zoom;
            const dy = (e.clientY - startPos.y) / this.state.zoom;

            const currentLeft = parseFloat(el.style.left);
            const currentTop = parseFloat(el.style.top);

            el.style.left = (currentLeft + dx) + 'px';
            el.style.top = (currentTop + dy) + 'px';

            startPos = { x: e.clientX, y: e.clientY };

            // Update links while dragging
            this.renderLinks();
        };

        const onMouseUp = (e) => {
            if (isDragging) {
                isDragging = false;

                // Stop listening
                window.removeEventListener('mousemove', onMouseMove);
                window.removeEventListener('mouseup', onMouseUp);

                if (!hasMoved) {
                    const now = Date.now();
                    if (now - this.state.lastClickTime < 300) {
                        this.toggleConnectMode(true);
                        this.onPinClick(el);
                        this.showToast('Click another pin to connect');
                    } else {
                        this.onPinClick(el);
                    }
                    this.state.lastClickTime = now;
                }

                const pinState = this.state.pins.find(p => p.id === el.id);
                if (pinState) {
                    pinState.x = parseFloat(el.style.left);
                    pinState.y = parseFloat(el.style.top);
                }
            }
        };

        el.addEventListener('mousedown', (e) => {
            if (e.button !== 0) return;
            if (e.target.closest('.cb-pin-action')) return;

            e.stopPropagation(); // Prevent workspace pan
            isDragging = true;
            hasMoved = false;
            startPos = { x: e.clientX, y: e.clientY };

            // Bring to front
            el.style.zIndex = ++this.state.maxZIndex;

            // Mark other pins as not selected
            document.querySelectorAll('.cb-pin').forEach(p => p.classList.remove('selected'));
            el.classList.add('selected');

            // Attach transient listeners
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
        });
    },

    toggleConnectMode(force = null) {
        this.state.connectMode = force !== null ? force : !this.state.connectMode;
        const btn = document.getElementById('cb-btn-connect');
        if (btn) {
            if (this.state.connectMode) {
                btn.classList.add('active');
                this.workspace.style.cursor = 'crosshair';
            } else {
                btn.classList.remove('active');
                this.workspace.style.cursor = 'grab';
                this.state.selectedPinForLink = null;
                document.querySelectorAll('.cb-pin').forEach(p => p.classList.remove('linking', 'selected'));
            }
        }
    },

    showToast(msg) {
        const toast = document.createElement('div');
        toast.style = 'position:fixed; bottom:80px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.8); color:#fff; padding:10px 20px; border-radius:20px; z-index:10000; font-size:0.9rem; border:1px solid rgba(255,255,255,0.1); backdrop-filter:blur(5px);';
        toast.textContent = msg;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    },

    onPinClick(el) {
        if (!this.state.connectMode) return;

        if (!this.state.selectedPinForLink) {
            this.state.selectedPinForLink = el.id;
            el.classList.add('linking');
        } else {
            if (this.state.selectedPinForLink !== el.id) {
                this.addLink(this.state.selectedPinForLink, el.id);
            }
            // Reset
            document.querySelectorAll('.cb-pin').forEach(p => p.classList.remove('linking'));
            this.state.selectedPinForLink = null;
            if (!this.state.connectMode) this.toggleConnectMode(false);
        }
    },

    addLink(p1Id, p2Id) {
        const exists = this.state.links.find(l =>
            (l.from === p1Id && l.to === p2Id) || (l.from === p2Id && l.to === p1Id)
        );
        if (exists) return;

        const newLink = {
            id: 'link-' + Date.now(),
            from: p1Id,
            to: p2Id,
            color: '#ef4444',
            style: 'solid',
            label: 'test',
            locked: true
        };
        this.state.links.push(newLink);
        this.renderLinks();
        this.renderStats();

        // Open edit modal automatically on create
        this.openEditConnectionModal(newLink.id);
    },

    openEditConnectionModal(linkId) {
        const link = this.state.links.find(l => l.id === linkId);
        if (!link) return;

        this.state.contextLinkId = linkId;
        const modal = document.getElementById('cb-modal-edit-connection');
        if (modal) {
            document.getElementById('cb-conn-label').value = link.label || '';
            document.getElementById('cb-conn-color').value = link.color || '#2563eb';
            document.getElementById('cb-conn-style').value = link.style || 'solid';
            document.getElementById('cb-conn-locked').checked = link.locked || false;

            modal.classList.add('active');
        }
    },

    closeEditConnectionModal() {
        const modal = document.getElementById('cb-modal-edit-connection');
        if (modal) modal.classList.remove('active');
        this.state.contextLinkId = null;
    },

    saveConnection() {
        const link = this.state.links.find(l => l.id === this.state.contextLinkId);
        if (link) {
            link.label = document.getElementById('cb-conn-label').value;
            link.color = document.getElementById('cb-conn-color').value;
            link.style = document.getElementById('cb-conn-style').value;
            link.locked = document.getElementById('cb-conn-locked').checked;
            this.renderLinks();
        }
        this.closeEditConnectionModal();
    },

    deleteConnection() {
        this.state.links = this.state.links.filter(l => l.id !== this.state.contextLinkId);
        this.renderLinks();
        this.renderStats();
        this.closeEditConnectionModal();
    },

    renderLinks() {
        if (!this.svg) return;
        this.svg.innerHTML = '';

        // Remove old labels
        document.querySelectorAll('.cb-line-label').forEach(l => l.remove());

        this.state.links.forEach(link => {
            const p1 = document.getElementById(link.from);
            const p2 = document.getElementById(link.to);
            if (!p1 || !p2) return;

            const x1 = parseFloat(p1.style.left) + p1.offsetWidth / 2;
            const y1 = parseFloat(p1.style.top) + p1.offsetHeight / 2;
            const x2 = parseFloat(p2.style.left) + p2.offsetWidth / 2;
            const y2 = parseFloat(p2.style.top) + p2.offsetHeight / 2;

            const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            line.setAttribute("x1", x1);
            line.setAttribute("y1", y1);
            line.setAttribute("x2", x2);
            line.setAttribute("y2", y2);
            line.setAttribute("stroke", link.color);
            line.setAttribute("stroke-width", "2");
            if (link.style === 'dashed') line.setAttribute("stroke-dasharray", "8,8");
            if (link.style === 'dotted') line.setAttribute("stroke-dasharray", "2,4");

            this.svg.appendChild(line);

            // Label
            if (link.label) {
                const label = document.createElement('div');
                label.className = 'cb-line-label';
                label.textContent = link.label;
                label.style.left = ((x1 + x2) / 2) + 'px';
                label.style.top = ((y1 + y2) / 2) + 'px';
                label.onclick = (e) => {
                    e.stopPropagation();
                    this.openEditConnectionModal(link.id);
                };
                this.canvas.appendChild(label);
            }
        });
    },

    resetView() {
        this.state.zoom = 0.5;
        this.state.pos = {
            x: (window.innerWidth ? (window.innerWidth - 280) / 2 : 960) - 1250,
            y: (window.innerHeight ? window.innerHeight / 2 : 540) - 1250
        };
        this.updateTransform();
        if (this.zoomDisplay) this.zoomDisplay.textContent = "50%";
    },

    renderStats() {
        const pinCountEl = document.querySelectorAll('.cb-stat-card .value')[0];
        const linkCountEl = document.querySelectorAll('.cb-stat-card .value')[1];

        if (pinCountEl) pinCountEl.textContent = this.state.pins.length;
        if (linkCountEl) linkCountEl.textContent = this.state.links.length;

        // Update sidebar counts
        const counts = {};
        this.state.pins.forEach(p => {
            counts[p.type] = (counts[p.type] || 0) + 1;
        });

        document.querySelectorAll('.cb-pin-type-item').forEach(item => {
            const type = item.getAttribute('data-type');
            const countEl = item.querySelector('.count');
            if (countEl && type) {
                countEl.textContent = counts[type] || 0;
            }
        });
    }
};

// Hook into the main app switchView (assumed global)
// CaseBoard.init() is now called from script.js bootstrap.
