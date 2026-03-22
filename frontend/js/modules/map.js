/**
 * Map Module
 */
window.LEAMap = {
    leaMap: null,
    drawnItems: null,
    drawHistory: [],
    redoStack: [],
    currentColor: '#3b82f6',
    activeDrawHandler: null,
    mapColors: ['#3b82f6', '#ef4444', '#22c55e', '#f97316', '#a855f7', '#ec4899'],

    init: async function () {
        if (!document.getElementById('lea-map')) return;

        if (typeof L === 'undefined') {
            setTimeout(() => this.init(), 100);
            return;
        }

        // Initialize Map
        this.leaMap = L.map('lea-map', {
            center: [-45, -20],
            zoom: 4,
            maxZoom: 5,
            minZoom: 2,
            zoomControl: false,
            attributionControl: true,
            preferCanvas: true
        });

        window.leaMap = this.leaMap; // expose for global resizing if needed

        const transparentPixel = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';

        L.tileLayer('assets/map/tiles/{z}/{x}/{y}.jpg', {
            attribution: 'San Andreas Street Guide - LEA+',
            noWrap: true,
            errorTileUrl: transparentPixel
        }).addTo(this.leaMap);

        this.drawnItems = new L.FeatureGroup();
        this.leaMap.addLayer(this.drawnItems);

        try {
            const res = await fetch('data/map/streets.json');
            const streets = await res.json();

            const markersLayer = new L.LayerGroup();
            this.leaMap.addLayer(markersLayer);

            streets.forEach(s => {
                const marker = L.marker(s.loc, { title: s.title, opacity: 0 });
                markersLayer.addLayer(marker);
            });

            const searchControl = new L.Control.Search({
                layer: markersLayer,
                propertyName: 'title',
                marker: false,
                moveToLocation: (latlng, title, map) => {
                    map.setView(latlng, 5);
                },
                initial: false,
                collapsed: false,
                textPlaceholder: 'Wyszukaj ulicę...',
                textCancel: ''
            });

            this.leaMap.addControl(searchControl);
            this.initCustomMapControls();

            const searchBtn = document.querySelector('.leaflet-control-search .search-button');
            if (searchBtn) searchBtn.remove();
        } catch (e) {
            console.error("Map data failed to load", e);
        }

        this.initMapDrawControls();
    },

    initCustomMapControls: function () {
        const self = this;
        const ZoomControl = L.Control.extend({
            options: { position: 'topleft' },
            onAdd: function () {
                const container = L.DomUtil.create('div', 'lea-custom-map-controls');
                L.DomEvent.disableClickPropagation(container);

                const zoomIn = L.DomUtil.create('button', 'lea-zoom-btn', container);
                zoomIn.innerHTML = '<i class="fas fa-plus"></i>';
                zoomIn.title = "Zoom In";
                zoomIn.onclick = () => self.leaMap.zoomIn();

                const zoomOut = L.DomUtil.create('button', 'lea-zoom-btn', container);
                zoomOut.innerHTML = '<i class="fas fa-minus"></i>';
                zoomOut.title = "Zoom Out";
                zoomOut.onclick = () => self.leaMap.zoomOut();

                return container;
            }
        });

        this.leaMap.addControl(new ZoomControl());
    },

    initMapDrawControls: function () {
        const self = this;
        const CustomControl = L.Control.extend({
            options: { position: 'topright' },
            onAdd: function () {
                const container = L.DomUtil.create('div', 'leaflet-custom-draw-controls');
                L.DomEvent.disableClickPropagation(container);

                const drawRow = L.DomUtil.create('div', 'leaflet-draw-custom-container', container);
                const tools = [
                    { id: 'marker', icon: 'fa-map-pin', title: 'Marker' },
                    { id: 'polyline', icon: 'fa-route', title: 'Polyline' },
                    { id: 'polygon', icon: 'fa-draw-polygon', title: 'Polygon' },
                    { id: 'text', icon: 'fa-font', title: 'Text Label' }
                ];

                tools.forEach(t => {
                    const btn = L.DomUtil.create('button', 'leaflet-custom-draw-button', drawRow);
                    btn.innerHTML = `<i class="fas ${t.icon}"></i>`;
                    btn.title = t.title;
                    btn.onclick = () => self.activateTool(t.id, btn);
                });

                const actionRow = L.DomUtil.create('div', 'leaflet-draw-action-container', container);
                const actions = [
                    { id: 'undo', icon: 'fa-undo', title: 'Undo', action: () => self.undoDraw() },
                    { id: 'redo', icon: 'fa-redo', title: 'Redo', action: () => self.redoDraw() },
                    { id: 'clear', icon: 'fa-trash-alt', title: 'Clear', action: () => self.clearMap() },
                    { id: 'snapshot', icon: 'fa-camera', title: 'Snapshot', action: () => self.takeMapSnapshot() }
                ];

                actions.forEach(a => {
                    const btn = L.DomUtil.create('button', 'leaflet-custom-draw-button', actionRow);
                    btn.id = `map-btn-${a.id}`;
                    btn.innerHTML = `<i class="fas ${a.icon}"></i>`;
                    btn.title = a.title;
                    btn.onclick = a.action;
                });

                const colorPicker = L.DomUtil.create('div', 'leaflet-custom-color-picker', container);
                self.mapColors.forEach(c => {
                    const dot = L.DomUtil.create('button', 'leaflet-color-button', colorPicker);
                    dot.style.backgroundColor = c;
                    dot.style.color = c;
                    if (c === self.currentColor) dot.classList.add('selected');
                    dot.onclick = () => {
                        self.currentColor = c;
                        document.querySelectorAll('.leaflet-color-button').forEach(d => d.classList.remove('selected'));
                        dot.classList.add('selected');

                        if (self.activeDrawHandler) {
                            const currentType = self.activeDrawHandler._type;
                            const activeBtn = document.querySelector('.leaflet-custom-draw-button.active');
                            self.activeDrawHandler.disable();
                            self.activeDrawHandler = null;
                            if (activeBtn) self.activateTool(currentType, activeBtn);
                        }
                    };
                });

                return container;
            }
        });

        this.leaMap.addControl(new CustomControl());

        this.leaMap.on(L.Draw.Event.CREATED, (e) => {
            const layer = e.layer;
            if (layer instanceof L.Path) {
                layer.setStyle({ color: this.currentColor });
            } else if (layer instanceof L.Marker) {
                layer.options.draggable = true;
                if (layer.dragging) layer.dragging.enable();
                layer.setIcon(L.divIcon({
                    className: '',
                    html: `<div style="background:${this.currentColor};width:14px;height:14px;border:2px solid white;border-radius:50%;box-shadow:0 0 5px rgba(0,0,0,0.5)"></div>`,
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                }));
            }
            this.drawnItems.addLayer(layer);
            this.drawHistory.push(layer);
            this.redoStack = [];
            this.updateMapBtnState();

            this.promptShapeLabel(layer);

            if (this.activeDrawHandler) {
                this.activeDrawHandler.disable();
                this.activeDrawHandler = null;
                document.querySelectorAll('.leaflet-custom-draw-button').forEach(b => b.classList.remove('active'));
            }
        });
    },

    activateTool: function (type, btn) {
        if (this.activeDrawHandler && this.activeDrawHandler._type === type) {
            this.activeDrawHandler.disable();
            this.activeDrawHandler = null;
            btn.classList.remove('active');
            return;
        }

        if (this.activeDrawHandler) {
            this.activeDrawHandler.disable();
        }
        document.querySelectorAll('.leaflet-custom-draw-button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const options = {
            shapeOptions: { color: this.currentColor, opacity: 1, weight: 4 },
            polyline: {
                shapeOptions: { color: this.currentColor, opacity: 1, weight: 4 },
                showLength: false
            },
            polygon: {
                shapeOptions: { color: this.currentColor, opacity: 0.5, fill: true, fillColor: this.currentColor },
                showArea: false,
                showLength: false
            },
            metric: false
        };

        if (type === 'marker') {
            this.activeDrawHandler = new L.Draw.Marker(this.leaMap, {
                icon: L.divIcon({
                    className: 'lea-map-marker',
                    html: `<div style="background:${this.currentColor};width:14px;height:14px;border:2px solid white;border-radius:50%;box-shadow:0 0 10px rgba(0,0,0,0.5)"></div>`,
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                })
            });
        } else if (type === 'polyline') {
            this.activeDrawHandler = new L.Draw.Polyline(this.leaMap, options.polyline);
        } else if (type === 'polygon') {
            this.activeDrawHandler = new L.Draw.Polygon(this.leaMap, options.polygon);
        } else if (type === 'text') {
            const self = this;
            if (!this._boundTextHandler) {
                this._boundTextHandler = this.onMapTextClick.bind(this);
            }
            this.activeDrawHandler = {
                _type: 'text',
                enable: function () {
                    self.leaMap.on('click', self._boundTextHandler);
                    self.leaMap.getContainer().style.cursor = 'crosshair';
                },
                disable: function () {
                    self.leaMap.off('click', self._boundTextHandler);
                    self.leaMap.getContainer().style.cursor = '';
                }
            };
        }

        if (this.activeDrawHandler) {
            this.activeDrawHandler._type = type;
            this.activeDrawHandler.enable();
        }
    },

    // To prevent listener duplication on bind
    _boundTextHandler: null,

    onMapTextClick: function (e) {
        const container = this.leaMap.getContainer();
        const existing = container.querySelector('.lea-map-hud-input-wrapper');
        if (existing) existing.remove();

        const wrapper = document.createElement('div');
        wrapper.className = 'lea-map-hud-input-wrapper';

        const point = this.leaMap.latLngToContainerPoint(e.latlng);
        wrapper.style.left = (point.x + 10) + 'px';
        wrapper.style.top = (point.y - 15) + 'px';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'hud-input-ctrl';
        input.placeholder = 'ENTER TACTICAL LABEL...';
        input.style.width = '200px';
        input.style.height = '32px';
        input.style.fontSize = '0.7rem';
        input.style.padding = '0 10px';

        wrapper.appendChild(input);
        container.appendChild(wrapper);
        L.DomEvent.disableClickPropagation(wrapper);

        input.focus();

        const saveLabel = () => {
            const text = input.value.trim();
            if (text !== "") {
                const label = L.marker(e.latlng, {
                    draggable: true,
                    icon: L.divIcon({
                        className: 'lea-map-text-wrapper',
                        html: `<div class="lea-hud-tooltip">${text.toUpperCase()}</div>`,
                        iconSize: null
                    })
                });
                this.drawnItems.addLayer(label);
                this.drawHistory.push(label);
                this.updateMapBtnState();
            }
            wrapper.remove();

            if (this.activeDrawHandler && this.activeDrawHandler._type === 'text') {
                this.activeDrawHandler.disable();
                this.activeDrawHandler = null;
                document.querySelectorAll('.leaflet-custom-draw-button').forEach(b => b.classList.remove('active'));
            }
        };

        input.onkeydown = (ev) => {
            if (ev.key === 'Enter') {
                ev.preventDefault();
                saveLabel();
            }
            if (ev.key === 'Escape') wrapper.remove();
        };
    },

    promptShapeLabel: function (layer) {
        let latlng;
        if (layer instanceof L.Marker) {
            latlng = layer.getLatLng();
        } else if (layer instanceof L.Polygon) {
            latlng = layer.getBounds().getCenter();
        } else if (layer instanceof L.Polyline) {
            latlng = layer.getBounds().getCenter();
        } else {
            return;
        }

        const container = this.leaMap.getContainer();
        const existing = container.querySelector('.lea-shape-label-prompt');
        if (existing) existing.remove();

        const wrapper = document.createElement('div');
        wrapper.className = 'lea-shape-label-prompt';
        const point = this.leaMap.latLngToContainerPoint(latlng);
        wrapper.style.position = 'absolute';
        wrapper.style.left = (point.x + 15) + 'px';
        wrapper.style.top = (point.y - 15) + 'px';
        wrapper.style.zIndex = '1000';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'hud-input-ctrl';
        input.placeholder = 'Nazwij / opisz (opcjonalnie)';
        input.style.width = '180px';
        input.style.height = '28px';
        input.style.fontSize = '0.75rem';
        input.style.padding = '0 8px';
        input.style.background = 'hsl(var(--card-bg))';
        input.style.border = '1px solid hsl(var(--primary))';
        input.style.color = '#fff';
        input.style.borderRadius = 'var(--radius-sm)';
        input.style.boxShadow = '0 4px 15px rgba(0,0,0,0.8)';
        input.style.outline = 'none';

        wrapper.appendChild(input);
        container.appendChild(wrapper);
        L.DomEvent.disableClickPropagation(wrapper);

        setTimeout(() => input.focus(), 50);

        const finish = () => {
            if (!wrapper.isConnected) return;
            const text = input.value.trim();
            if (text !== "") {
                const isMarker = layer instanceof L.Marker;
                layer.bindTooltip(text.toUpperCase(), {
                    permanent: true,
                    direction: isMarker ? 'right' : 'center',
                    offset: isMarker ? [10, 0] : [0, 0],
                    className: 'lea-compact-label'
                }).openTooltip();
                this.updateLegend();
            }
            wrapper.remove();
        };

        input.onkeydown = (ev) => {
            if (ev.key === 'Enter') finish();
            if (ev.key === 'Escape') wrapper.remove();
        };

        const onMapDown = () => {
            finish();
            this.leaMap.off('mousedown', onMapDown);
        };
        setTimeout(() => this.leaMap.on('mousedown', onMapDown), 100);
    },

    undoDraw: function () {
        if (this.drawHistory.length > 0) {
            const last = this.drawHistory.pop();
            this.drawnItems.removeLayer(last);
            this.redoStack.push(last);
            this.updateMapBtnState();
        }
    },

    redoDraw: function () {
        if (this.redoStack.length > 0) {
            const next = this.redoStack.pop();
            this.drawnItems.addLayer(next);
            this.drawHistory.push(next);
            this.updateMapBtnState();
        }
    },

    clearMap: function () {
        this.drawnItems.clearLayers();
        this.drawHistory = [];
        this.redoStack = [];
        this.updateMapBtnState();
    },

    updateMapBtnState: function () {
        const undoBtn = document.getElementById('map-btn-undo');
        const redoBtn = document.getElementById('map-btn-redo');
        const clearBtn = document.getElementById('map-btn-clear');
        if (undoBtn) undoBtn.disabled = this.drawHistory.length === 0;
        if (redoBtn) redoBtn.disabled = this.redoStack.length === 0;
        if (clearBtn) clearBtn.disabled = this.drawHistory.length === 0;

        this.updateLegend();
    },

    updateLegend: function () {
        if (!this.legendControl) {
            const Legend = L.Control.extend({
                options: { position: 'bottomleft' },
                onAdd: function () {
                    return L.DomUtil.create('div', 'lea-map-legend');
                }
            });
            this.legendControl = new Legend();
            this.leaMap.addControl(this.legendControl);
        }

        const container = this.legendControl.getContainer();
        container.innerHTML = '<div class="legend-title">Taktyczna Legenda</div>';

        let hasItems = false;
        this.drawnItems.eachLayer(layer => {
            let text = "";
            let color = "";
            let iconClass = "fa-map-pin";

            if (layer.getTooltip && layer.getTooltip()) {
                text = layer.getTooltip().getContent();
                if (layer instanceof L.Marker) {
                    iconClass = "fa-map-pin";
                    if (layer.options.icon && layer.options.icon.options.html) {
                        const html = layer.options.icon.options.html;
                        const match = html.match(/background:(#[0-9a-f]{6}|rgba?[^;]+)/i);
                        color = match ? match[1] : '#fff';
                    } else color = '#fff';
                } else if (layer instanceof L.Path) {
                    if (layer instanceof L.Polygon) iconClass = "fa-draw-polygon";
                    else if (layer instanceof L.Polyline) iconClass = "fa-route";
                    color = layer.options.color || '#fff';
                }
            } else if (layer.options.icon && layer.options.icon.options.className === 'lea-map-text-wrapper') {
                const doc = new DOMParser().parseFromString(layer.options.icon.options.html, 'text/html');
                text = doc.body.textContent;
                color = '#fff';
                iconClass = "fa-font";
            }

            if (text) {
                hasItems = true;
                const item = L.DomUtil.create('div', 'legend-item', container);
                const icon = L.DomUtil.create('i', `fas ${iconClass} legend-shape-icon`, item);
                icon.style.color = color;
                icon.style.width = '16px';
                icon.style.textAlign = 'center';
                const lbl = L.DomUtil.create('div', 'legend-lbl', item);
                lbl.textContent = text;
            }
        });

        container.style.display = hasItems ? 'block' : 'none';
    },

    takeMapSnapshot: function () {
        const container = this.leaMap.getContainer();
        const controls = container.querySelectorAll('.leaflet-control');
        controls.forEach(c => {
            if (!c.classList.contains('lea-map-legend') && !c.querySelector('.lea-map-legend')) {
                c.style.display = 'none';
            }
        });

        html2canvas(container, {
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#0a0e14'
        }).then(canvas => {
            const link = document.createElement('a');
            link.download = `lea_tactical_map_${Date.now()}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
            controls.forEach(c => c.style.display = '');
        }).catch(err => {
            console.error("Snapshot failed", err);
            controls.forEach(c => c.style.display = '');
        });
    }
};
