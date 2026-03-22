import re
import os

base_dir = r"c:\Users\kaketan\.gemini\antigravity\scratch\lspd_web_app\client"

# 1. HTML Update
html_file = os.path.join(base_dir, 'views', 'caseboard.html')
with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

new_fields = """
            <div id="cb-modal-normal-fields">
                <div class="hud-form-row two-cols dfield" data-fields="dob-phone">
                    <div class="hud-form-group">
                        <label class="hud-form-label">DOB</label>
                        <input type="text" class="hud-input" id="pin-field-dob" placeholder="DD/MM/YYYY">
                    </div>
                    <div class="hud-form-group">
                        <label class="hud-form-label">PHONE</label>
                        <input type="text" class="hud-input" id="pin-field-phone" placeholder="Enter phone...">
                    </div>
                </div>
                
                <div class="hud-form-row dfield" data-fields="address">
                    <div class="hud-form-group">
                        <label class="hud-form-label">ADDRESS</label>
                        <input type="text" class="hud-input" id="pin-field-address" placeholder="Enter address...">
                    </div>
                </div>
                
                <div class="hud-form-row dfield" data-fields="reason">
                    <div class="hud-form-group">
                        <label class="hud-form-label">REASON</label>
                        <input type="text" class="hud-input" id="pin-field-reason" placeholder="Enter reason...">
                    </div>
                </div>
                
                <div class="hud-form-row two-cols dfield" data-fields="officer-info">
                    <div class="hud-form-group">
                        <label class="hud-form-label">BADGE #</label>
                        <input type="text" class="hud-input" id="pin-field-badge" placeholder="e.g. 5431">
                    </div>
                    <div class="hud-form-group">
                        <label class="hud-form-label">CALLSIGN</label>
                        <input type="text" class="hud-input" id="pin-field-callsign" placeholder="e.g. 1-ADAM-12">
                    </div>
                </div>
                <div class="hud-form-row dfield" data-fields="officer-div">
                    <div class="hud-form-group">
                        <label class="hud-form-label">DIVISION</label>
                        <input type="text" class="hud-input" id="pin-field-division" placeholder="e.g. K-9, SWAT">
                    </div>
                </div>

                <div class="hud-form-row two-cols dfield" data-fields="statement-info">
                    <div class="hud-form-group">
                        <label class="hud-form-label">STATEMENT BY</label>
                        <input type="text" class="hud-input" id="pin-field-statement-by" placeholder="Name...">
                    </div>
                    <div class="hud-form-group">
                        <label class="hud-form-label">TAKEN BY</label>
                        <input type="text" class="hud-input" id="pin-field-taken-by" placeholder="Officer name...">
                    </div>
                </div>
                
                <div class="hud-form-row two-cols dfield" data-fields="datetime-loc">
                    <div class="hud-form-group">
                        <label class="hud-form-label">DATE / TIME</label>
                        <input type="text" class="hud-input" id="pin-field-datetime" placeholder="DD/MM/YYYY HH:MM">
                    </div>
                    <div class="hud-form-group">
                        <label class="hud-form-label">LOCATION</label>
                        <input type="text" class="hud-input" id="pin-field-location" placeholder="Address/Area...">
                    </div>
                </div>

                <div class="hud-form-row two-cols dfield" data-fields="evidence-info">
                    <div class="hud-form-group">
                        <label class="hud-form-label">TAG #</label>
                        <input type="text" class="hud-input" id="pin-field-tag" placeholder="e.g. EV-1002">
                    </div>
                    <div class="hud-form-group">
                        <label class="hud-form-label">FOUND AT</label>
                        <input type="text" class="hud-input" id="pin-field-found-at" placeholder="Where was it found?">
                    </div>
                </div>
                <div class="hud-form-row dfield" data-fields="evidence-col">
                    <div class="hud-form-group">
                        <label class="hud-form-label">COLLECTED BY</label>
                        <input type="text" class="hud-input" id="pin-field-collected-by" placeholder="Officer name...">
                    </div>
                </div>

                <div class="hud-form-row two-cols dfield" data-fields="vehicle-info1">
                    <div class="hud-form-group">
                        <label class="hud-form-label">LICENSE PLATE</label>
                        <input type="text" class="hud-input" id="pin-field-plate" placeholder="e.g. 2XYZ345">
                    </div>
                    <div class="hud-form-group">
                        <label class="hud-form-label">STATE</label>
                        <input type="text" class="hud-input" id="pin-field-state" placeholder="e.g. San Andreas">
                    </div>
                </div>
                <div class="hud-form-row two-cols dfield" data-fields="vehicle-info2">
                    <div class="hud-form-group">
                        <label class="hud-form-label">MAKE / MODEL</label>
                        <input type="text" class="hud-input" id="pin-field-model" placeholder="e.g. Karin Sultan">
                    </div>
                    <div class="hud-form-group">
                        <label class="hud-form-label">COLOR</label>
                        <input type="text" class="hud-input" id="pin-field-color" placeholder="e.g. Matte Black">
                    </div>
                </div>

                <div class="hud-form-row two-cols dfield" data-fields="weapon-info">
                    <div class="hud-form-group">
                        <label class="hud-form-label">TYPE</label>
                        <input type="text" class="hud-input" id="pin-field-wtype" placeholder="e.g. Pistol, Rifle">
                    </div>
                    <div class="hud-form-group">
                        <label class="hud-form-label">CALIBER</label>
                        <input type="text" class="hud-input" id="pin-field-caliber" placeholder="e.g. 9mm">
                    </div>
                </div>
                <div class="hud-form-row dfield" data-fields="weapon-serial">
                    <div class="hud-form-group">
                        <label class="hud-form-label">SERIAL #</label>
                        <input type="text" class="hud-input" id="pin-field-serial" placeholder="Serial number...">
                    </div>
                </div>
                
                <div class="hud-form-row two-cols dfield" data-fields="org-info">
                    <div class="hud-form-group">
                        <label class="hud-form-label">MEMBERS</label>
                        <input type="text" class="hud-input" id="pin-field-members" placeholder="e.g. 10-20">
                    </div>
                    <div class="hud-form-group">
                        <label class="hud-form-label">TERRITORY</label>
                        <input type="text" class="hud-input" id="pin-field-territory" placeholder="e.g. Davis">
                    </div>
                </div>

                <div class="hud-form-row two-cols dfield" data-fields="doc-info">
                    <div class="hud-form-group">
                        <label class="hud-form-label">DOC TYPE</label>
                        <input type="text" class="hud-input" id="pin-field-doctype" placeholder="e.g. Warrant, Subpoena">
                    </div>
                    <div class="hud-form-group">
                        <label class="hud-form-label">REFERENCE</label>
                        <input type="text" class="hud-input" id="pin-field-reference" placeholder="e.g. Case #...">
                    </div>
                </div>

                <div class="hud-form-row dfield" data-fields="owner">
                    <div class="hud-form-group">
                        <label class="hud-form-label">OWNER</label>
                        <input type="text" class="hud-input" id="pin-field-owner" placeholder="Owner name...">
                    </div>
                </div>

                <div class="hud-form-row dfield" data-fields="generic-type">
                    <div class="hud-form-group">
                        <label class="hud-form-label">TYPE</label>
                        <input type="text" class="hud-input" id="pin-field-generic-type" placeholder="Type info...">
                    </div>
                </div>

                <div class="hud-form-row dfield" data-fields="district">
                    <div class="hud-form-group">
                        <label class="hud-form-label">DISTRICT</label>
                        <input type="text" class="hud-input" id="pin-field-district" placeholder="District name...">
                    </div>
                </div>
                
                <div class="hud-form-row two-cols dfield" data-fields="date-time">
                    <div class="hud-form-group">
                        <label class="hud-form-label">DATE</label>
                        <input type="text" class="hud-input" id="pin-field-date" placeholder="DD/MM/YYYY">
                    </div>
                    <div class="hud-form-group">
                        <label class="hud-form-label">TIME</label>
                        <input type="text" class="hud-input" id="pin-field-time" placeholder="HH:MM">
                    </div>
                </div>

                <div class="hud-form-row dfield" data-fields="details">
                    <div class="hud-form-group">
                        <label class="hud-form-label">DETAILS / DESCRIPTION</label>
                        <textarea class="hud-input" id="pin-field-details" placeholder="Enter details..."
                            style="height: 60px;"></textarea>
                    </div>
                </div>
            </div>
"""

pattern = r'<div id="cb-modal-normal-fields">.*?(?=<div class="hud-form-row two-cols" style="margin-top:0\.5rem">)'
html = re.sub(pattern, new_fields, html, flags=re.DOTALL)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html)

# 2. CSS Update
css_file = os.path.join(base_dir, 'css', 'caseboard.css')
with open(css_file, 'r', encoding='utf-8') as f:
    css = f.read()

new_pin_css = """/* Pins on Canvas */
.cb-pin {
    position: absolute;
    width: 280px;
    background: #11151c;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 4px;
    cursor: grab;
    user-select: none;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.5);
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
    overflow: hidden;
    display: flex;
}

.cb-pin.selected {
    border-color: #3b82f6;
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
    transform: scale(1.02);
}

.cb-pin-sidebar {
    width: 4px;
    flex-shrink: 0;
}

.cb-pin[data-type="suspect"] .cb-pin-sidebar { background: #ef4444; }
.cb-pin[data-type="poi"] .cb-pin-sidebar { background: #f97316; }
.cb-pin[data-type="victim"] .cb-pin-sidebar { background: #ec4899; }
.cb-pin[data-type="witness"] .cb-pin-sidebar { background: #eab308; }
.cb-pin[data-type="officer"] .cb-pin-sidebar { background: #3b82f6; }
.cb-pin[data-type="evidence"] .cb-pin-sidebar { background: #22c55e; }
.cb-pin[data-type="weapon"] .cb-pin-sidebar { background: #ef4444; }
.cb-pin[data-type="vehicle"] .cb-pin-sidebar { background: #a855f7; }
.cb-pin[data-type="location"] .cb-pin-sidebar { background: #3b82f6; }
.cb-pin[data-type="organization"] .cb-pin-sidebar { background: #eab308; }
.cb-pin[data-type="stickynote"] .cb-pin-sidebar { background: #eab308; }
.cb-pin[data-type="note"] .cb-pin-sidebar { background: #64748b; }

.cb-pin-content {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.cb-pin-action-bar {
    position: absolute;
    top: 8px;
    right: 8px;
    display: flex;
    gap: 4px;
    opacity: 0.2;
    transition: opacity 0.2s;
}
.cb-pin:hover .cb-pin-action-bar {
    opacity: 1;
}

.cb-pin-action {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.6);
    width: 24px;
    height: 24px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.8rem;
}

.cb-pin-action:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
}

.cb-pin-action.delete:hover {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

.cb-pin-header {
    padding: 12px 14px 10px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

.cb-pin-title {
    font-size: 1rem;
    font-weight: 800;
    color: #fff;
    margin-bottom: 4px;
}

.cb-pin-type-name {
    font-size: 0.7rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.cb-pin-body {
    padding: 12px 14px;
}

.cb-pin-image {
    width: 100%;
    height: 120px;
    object-fit: cover;
    border-radius: 4px;
    margin-bottom: 10px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.cb-pin-details-text {
    font-size: 0.8rem;
    line-height: 1.4;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 12px;
}

.cb-pin-meta {
    display: flex;
    flex-direction: column;
    gap: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 12px;
    margin-bottom: 12px;
}

.cb-pin-meta .meta-row {
    display: flex;
    font-size: 0.75rem;
}

.cb-pin-meta .meta-row .label {
    color: rgba(255, 255, 255, 0.4);
    width: 70px;
    flex-shrink: 0;
}

.cb-pin-meta .meta-row .val {
    color: #fff;
    font-weight: 600;
    flex: 1;
}

.cb-pin-footer {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.5);
    font-weight: 600;
}

.cb-pin-tag {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.5);
    margin-top: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}
"""

css_pattern = r'/\* Pins on Canvas \*/\s*\.cb-pin \{.*?(?=/\* Premium Modal Design for Case Board \*/)'
css = re.sub(css_pattern, new_pin_css + "\n\n", css, flags=re.DOTALL)

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(css)

print("HTML and CSS updated.")
