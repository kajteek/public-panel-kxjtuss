import re

js_file = r"c:\Users\kaketan\.gemini\antigravity\scratch\lspd_web_app\client\js\modules\caseboard.js"
css_file = r"c:\Users\kaketan\.gemini\antigravity\scratch\lspd_web_app\client\css\caseboard.css"

# =======================
# Fix caseboard.js HTML
# =======================
with open(js_file, "r", encoding="utf-8") as f:
    js_code = f.read()

# The renderPin HTML replacement
new_html_template = """            el.innerHTML = `
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
                            <i class="fas fa-calendar-alt"></i> <span>${creationDate}</span>
                            <i class="fas fa-link" style="margin-left: 8px;"></i> <span>${linkCount}</span>
                        </div>
                        <div class="cb-pin-tag">
                            <i class="fas fa-pen" style="color:#f59e0b"></i> <span>#CD-${pin.id.slice(-4)}</span>
                            ${priorityIcon}
                        </div>
                    </div>
                </div>
            `;"""
            
js_code = re.sub(r'el\.innerHTML = `[\s\S]*?<div class="cb-pin-tag">[\s\S]*?</div>\s*</div>\s*</div>\s*`;', new_html_template, js_code)

with open(js_file, "w", encoding="utf-8") as f:
    f.write(js_code)

# =======================
# Fix caseboard.css
# =======================
with open(css_file, "r", encoding="utf-8") as f:
    css_code = f.read()

new_css = """/* Pins on Canvas */
.cb-pin {
    position: absolute;
    width: 250px;
    background: #11151c;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    cursor: grab;
    user-select: none;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
    display: flex;
    flex-direction: column;
}

.cb-pin.selected {
    border-color: #3b82f6;
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
    transform: scale(1.02);
}

.cb-pin-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    position: relative;
}

.cb-pin-action-bar {
    position: absolute;
    top: -30px;
    right: 0;
    display: flex;
    gap: 4px;
    opacity: 0;
    transition: opacity 0.2s, top 0.2s;
}
.cb-pin:hover .cb-pin-action-bar {
    opacity: 1;
    top: -35px;
}

.cb-pin-action {
    background: #151b23;
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.6);
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.8rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5);
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
    padding: 12px 14px 10px 24px;
    position: relative;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

.cb-pin-sidebar {
    position: absolute;
    left: 8px;
    top: 12px;
    bottom: 10px;
    width: 3px;
    border-radius: 3px;
}

.cb-pin-title {
    font-size: 1rem;
    font-weight: 800;
    color: #fff;
    margin-bottom: 4px;
    line-height: 1.1;
    word-break: break-word;
}

.cb-pin-type-name {
    font-size: 0.7rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    gap: 6px;
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
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 12px;
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
    align-items: flex-start;
}

.cb-pin-meta .meta-row .label {
    color: rgba(255, 255, 255, 0.4);
    width: 80px;
    flex-shrink: 0;
}

.cb-pin-meta .meta-row .val {
    color: #fff;
    font-weight: 600;
    flex: 1;
    word-break: break-word;
}

.cb-pin-footer {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.4);
    font-weight: 600;
    margin-bottom: 8px;
}
.cb-pin-footer span {
    color: rgba(255,255,255,0.7);
}

.cb-pin-tag {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.6);
    display: flex;
    align-items: center;
    gap: 6px;
}
"""

css_code = re.sub(r'/\* Pins on Canvas \*/\n\.cb-pin \{[\s\S]*?(?=/\* Premium Modal Design for Case Board \*/)', new_css + "\n\n", css_code)

with open(css_file, "w", encoding="utf-8") as f:
    f.write(css_code)

print("Pin UI update completed.")
